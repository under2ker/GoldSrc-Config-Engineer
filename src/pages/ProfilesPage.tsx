import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { isTauri } from "@tauri-apps/api/core";
import { open } from "@tauri-apps/plugin-dialog";
import { toast } from "sonner";
import {
  Copy,
  ClipboardCopy,
  Download,
  FileJson,
  FolderOutput,
  History,
  Library,
  Loader2,
  Pencil,
  Star,
  Trash2,
  Eye,
} from "lucide-react";
import {
  deployModularFiles,
  exportModularFromJson,
  generateConfigFromJson,
  historyAppend,
  historyClear,
  historyDelete,
  historyList,
  historyLoad,
  profileDelete,
  profileLoad,
  profileSave,
  profileUpdate,
} from "@/lib/api";
import type { HistoryEntry } from "@/types/api";
import { saveCfgToDisk, saveJsonToDisk } from "@/lib/cfgFiles";
import { useConfigStore } from "@/stores/configStore";
import { useProfileStore } from "@/stores/profileStore";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  AlertDialog,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { pageCaptionClass, pageLeadClass, pageShellClass } from "@/lib/layoutTokens";
import { cn } from "@/lib/utils";

export function ProfilesPage() {
  const navigate = useNavigate();
  const profiles = useProfileStore((s) => s.profiles);
  const refreshProfiles = useProfileStore((s) => s.refreshProfiles);
  const setStagedProfile = useConfigStore((s) => s.setStagedProfile);

  const [busyId, setBusyId] = useState<string | null>(null);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [historyBusyId, setHistoryBusyId] = useState<number | null>(null);
  const [renameId, setRenameId] = useState<string | null>(null);
  const [renameName, setRenameName] = useState("");
  const [clearHistoryOpen, setClearHistoryOpen] = useState(false);
  const [clearHistoryBusy, setClearHistoryBusy] = useState(false);
  const [profileFilter, setProfileFilter] = useState("");
  const [duplicateId, setDuplicateId] = useState<string | null>(null);
  const [duplicateName, setDuplicateName] = useState("");
  const [historyFilter, setHistoryFilter] = useState("");

  const filteredProfiles = useMemo(() => {
    const q = profileFilter.trim().toLowerCase();
    if (!q) return profiles;
    return profiles.filter((p) => p.name.toLowerCase().includes(q));
  }, [profiles, profileFilter]);

  const filteredHistory = useMemo(() => {
    const q = historyFilter.trim().toLowerCase();
    if (!q) return history;
    return history.filter((h) => {
      const blob = [String(h.id), h.created_at, String(h.size_bytes), h.profile_id ?? ""].join(" ");
      return blob.toLowerCase().includes(q);
    });
  }, [history, historyFilter]);

  async function copyTextToClipboard(text: string, okMessage: string) {
    try {
      await navigator.clipboard.writeText(text);
      toast.success(okMessage);
    } catch {
      toast.error("Не удалось скопировать в буфер");
    }
  }

  const refreshHistory = useCallback(async () => {
    if (!isTauri()) return;
    try {
      setHistory(await historyList(40));
    } catch {
      setHistory([]);
    }
  }, []);

  useEffect(() => {
    void refreshProfiles();
    void refreshHistory();
  }, [refreshProfiles, refreshHistory]);

  const run = useCallback(
    async (id: string, fn: () => Promise<void>) => {
      setBusyId(id);
      try {
        await fn();
      } catch (e: unknown) {
        toast.error(String(e));
      } finally {
        setBusyId(null);
      }
    },
    [],
  );

  async function onDownloadSingle(id: string) {
    await run(id, async () => {
      const json = await profileLoad(id);
      const r = await generateConfigFromJson(json);
      const path = await saveCfgToDisk(r.content, `${sanitizeFilePart(r.label)}.cfg`);
      if (path) {
        toast.success("Файл сохранён", { description: path });
      }
    });
  }

  async function onExportProfileJson(id: string, displayName: string) {
    await run(id, async () => {
      const json = await profileLoad(id);
      const pretty = prettyJsonString(json);
      const path = await saveJsonToDisk(pretty, `${sanitizeFilePart(displayName)}.json`);
      if (path) {
        toast.success("JSON сохранён", { description: path });
      }
    });
  }

  async function onExportHistoryJson(h: HistoryEntry) {
    setHistoryBusyId(h.id);
    try {
      const json = await historyLoad(h.id);
      const pretty = prettyJsonString(json);
      const path = await saveJsonToDisk(pretty, `snapshot-${h.id}.json`);
      if (path) {
        toast.success("Снимок сохранён как JSON", { description: path });
      }
    } catch (e: unknown) {
      toast.error(String(e));
    } finally {
      setHistoryBusyId(null);
    }
  }

  async function onModularDeploy(id: string) {
    await run(id, async () => {
      const json = await profileLoad(id);
      const files = await exportModularFromJson(json);
      const dir = await open({
        directory: true,
        multiple: false,
        title: "Папка для модульного набора (например cstrike)",
      });
      if (dir === null) return;
      const target = typeof dir === "string" ? dir : dir[0];
      await deployModularFiles(target, files);
      try {
        await historyAppend(json, id);
        await refreshHistory();
      } catch {
        /* история опциональна */
      }
      toast.success("Модульный набор записан", { description: target });
    });
  }

  async function onPreview(id: string) {
    await run(id, async () => {
      const json = await profileLoad(id);
      const r = await generateConfigFromJson(json);
      navigate("/preview", { state: { cfgText: r.content } });
    });
  }

  async function onLoadIntoEditor(id: string, name: string) {
    await run(id, async () => {
      const json = await profileLoad(id);
      setStagedProfile(json, name);
      toast.success("Профиль загружен", { description: "Его можно сохранить снова после правок на импорте." });
    });
  }

  async function onToggleFavorite(id: string, name: string, fav: boolean) {
    await run(id, async () => {
      await profileUpdate(id, { isFavorite: !fav });
      toast.success(fav ? "Убрано из избранного" : "В избранном", { description: name });
      await refreshProfiles();
    });
  }

  async function onSaveDuplicate() {
    if (!duplicateId) return;
    const id = duplicateId;
    const name = duplicateName.trim();
    if (!name) {
      toast.error("Введите имя для копии");
      return;
    }
    setDuplicateId(null);
    await run(id, async () => {
      const json = await profileLoad(id);
      await profileSave(name, json);
      toast.success("Копия профиля сохранена", { description: name });
      await refreshProfiles();
    });
  }

  async function onSaveRename() {
    if (!renameId) return;
    const id = renameId;
    const name = renameName.trim();
    if (!name) {
      toast.error("Введите имя");
      return;
    }
    setRenameId(null);
    await run(id, async () => {
      await profileUpdate(id, { name });
      toast.success("Профиль переименован");
      await refreshProfiles();
    });
  }

  async function onHistoryToDraft(row: HistoryEntry) {
    setHistoryBusyId(row.id);
    try {
      const json = await historyLoad(row.id);
      setStagedProfile(json, `История #${row.id}`);
      toast.success("Снимок загружен в черновик", { description: "Импорт → правки при необходимости" });
    } catch (e: unknown) {
      toast.error(String(e));
    } finally {
      setHistoryBusyId(null);
    }
  }

  async function onHistoryDelete(rowId: number) {
    setHistoryBusyId(rowId);
    try {
      await historyDelete(rowId);
      toast.success("Запись истории удалена");
      await refreshHistory();
    } catch (e: unknown) {
      toast.error(String(e));
    } finally {
      setHistoryBusyId(null);
    }
  }

  async function onClearAllHistory() {
    setClearHistoryBusy(true);
    try {
      const n = await historyClear();
      toast.success("История очищена", {
        description: n > 0 ? `Удалено записей: ${n}` : "Записей не было",
      });
      await refreshHistory();
    } catch (e: unknown) {
      toast.error(String(e));
    } finally {
      setClearHistoryBusy(false);
      setClearHistoryOpen(false);
    }
  }

  async function confirmDelete() {
    if (!deleteId) return;
    const id = deleteId;
    setDeleteId(null);
    await run(id, async () => {
      await profileDelete(id);
      toast.success("Профиль удалён");
      await refreshProfiles();
    });
  }

  if (!isTauri()) {
    return (
      <div className={pageShellClass}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Library className="size-5 opacity-90" />
              Профили
            </CardTitle>
            <CardDescription>
              Локальные профили доступны в программе для Windows / macOS / Linux. В браузере откройте{" "}
              <Link to="/import" className="text-primary underline-offset-4 hover:underline">
                импорт
              </Link>{" "}
              и раздел экспорта.
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    );
  }

  return (
    <div className={pageShellClass}>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className={pageLeadClass}>
            Профили хранятся в локальной базе на этом компьютере. Из профиля можно собрать один `.cfg` или модульный набор,
            как из режима или пресета.
          </p>
          <p className="mt-2 text-sm">
            <Link to="/import" className="text-primary underline-offset-4 hover:underline">
              Импорт .cfg
            </Link>
            {" · "}
            <Link to="/export" className="text-primary underline-offset-4 hover:underline">
              Экспорт
            </Link>
          </p>
        </div>
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() => {
            void refreshProfiles();
            void refreshHistory();
          }}
        >
          Обновить список
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Library className="size-5 opacity-90" />
            Сохранённые профили
          </CardTitle>
          <CardDescription>
            Создаются на странице «Импорт» после разбора файла — «Сохранить как профиль».
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {profiles.length === 0 ? (
            <p className="text-sm text-muted-foreground">Пока нет профилей. Импортируйте `.cfg` и сохраните набор.</p>
          ) : (
            <>
              <div className="space-y-2">
                <Label htmlFor="profiles-filter" className={pageCaptionClass}>
                  Поиск по имени
                </Label>
                <Input
                  id="profiles-filter"
                  placeholder="Начните вводить имя…"
                  value={profileFilter}
                  onChange={(e) => setProfileFilter(e.target.value)}
                />
              </div>
              {filteredProfiles.length === 0 ? (
                <p className="text-sm text-muted-foreground">Ничего не найдено — сбросьте фильтр или измените запрос.</p>
              ) : null}
            <ul className="space-y-2">
              {filteredProfiles.map((p) => (
                <li
                  key={p.id}
                  className="flex flex-col gap-3 rounded-lg border border-border bg-muted/15 p-3 sm:flex-row sm:items-center sm:justify-between"
                >
                  <div className="min-w-0 space-y-1">
                    <div className="flex items-center gap-2">
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        className="size-8 shrink-0"
                        disabled={busyId === p.id}
                        aria-label={p.is_favorite ? "Убрать из избранного" : "В избранное"}
                        onClick={() => void onToggleFavorite(p.id, p.name, p.is_favorite)}
                      >
                        <Star
                          className={`size-4 ${p.is_favorite ? "fill-amber-400 text-amber-500" : "opacity-60"}`}
                        />
                      </Button>
                      <p className="truncate font-medium">{p.name}</p>
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        className="size-8 shrink-0"
                        disabled={busyId === p.id}
                        aria-label="Переименовать"
                        onClick={() => {
                          setRenameId(p.id);
                          setRenameName(p.name);
                        }}
                      >
                        <Pencil className="size-4 opacity-70" />
                      </Button>
                    </div>
                    <div className={cn(pageCaptionClass, "flex flex-wrap items-center gap-2")}>
                      <span>обновлён</span>
                      <Badge variant="outline" className="font-mono text-[10px]">
                        {p.updated_at.slice(0, 19).replace("T", " ")}
                      </Badge>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="h-7 gap-1 px-2 text-[10px] text-muted-foreground"
                        title="Копировать внутренний ID профиля"
                        onClick={() => void copyTextToClipboard(p.id, "ID профиля скопирован")}
                      >
                        <ClipboardCopy className="size-3" />
                        ID
                      </Button>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Button
                      type="button"
                      size="sm"
                      variant="secondary"
                      disabled={busyId === p.id}
                      onClick={() => void onPreview(p.id)}
                    >
                      {busyId === p.id ? (
                        <Loader2 className="size-4 animate-spin" />
                      ) : (
                        <Eye className="size-4" />
                      )}
                      Просмотр
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="default"
                      disabled={busyId === p.id}
                      onClick={() => void onDownloadSingle(p.id)}
                    >
                      <Download className="size-4" />
                      Один .cfg
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      disabled={busyId === p.id}
                      onClick={() => void onExportProfileJson(p.id, p.name)}
                    >
                      <FileJson className="size-4" />
                      JSON…
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      disabled={busyId === p.id}
                      onClick={() => void onModularDeploy(p.id)}
                    >
                      <FolderOutput className="size-4" />
                      Модульно…
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="ghost"
                      disabled={busyId === p.id}
                      onClick={() => void onLoadIntoEditor(p.id, p.name)}
                    >
                      В черновик
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      disabled={busyId === p.id}
                      onClick={() => {
                        setDuplicateId(p.id);
                        setDuplicateName(`${p.name} (копия)`);
                      }}
                    >
                      <Copy className="size-4" />
                      Копия…
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="ghost"
                      className="text-destructive hover:bg-destructive/10 hover:text-destructive"
                      disabled={busyId === p.id}
                      onClick={() => setDeleteId(p.id)}
                    >
                      <Trash2 className="size-4" />
                    </Button>
                  </div>
                </li>
              ))}
            </ul>
            </>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-col gap-4 space-y-0 sm:flex-row sm:items-start sm:justify-between">
          <div className="space-y-1.5">
            <CardTitle className="flex items-center gap-2">
              <History className="size-5 opacity-90" />
              История снимков
            </CardTitle>
            <CardDescription>
              Снимки после генерации на главной или на «Экспорт» (один файл или модульный набор), либо после записи
              профиля в папку. Можно загрузить в черновик для правок. Лимит хранимых записей задаётся в «Настройки».
            </CardDescription>
          </div>
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="shrink-0 border-destructive/40 text-destructive hover:bg-destructive/10"
            disabled={history.length === 0 || clearHistoryBusy}
            onClick={() => setClearHistoryOpen(true)}
          >
            Очистить всё…
          </Button>
        </CardHeader>
        <CardContent className="space-y-3">
          {history.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              Пока нет записей. Сформируйте конфиг на «Экспорт» или запишите модульный набор из профиля.
            </p>
          ) : (
            <>
              <div className="space-y-2">
                <Label htmlFor="history-filter" className={pageCaptionClass}>
                  Фильтр списка (номер, дата, размер)
                </Label>
                <Input
                  id="history-filter"
                  placeholder="Например: 12 или 2026-04 или KiB"
                  value={historyFilter}
                  onChange={(e) => setHistoryFilter(e.target.value)}
                />
              </div>
              {filteredHistory.length === 0 ? (
                <p className="text-sm text-muted-foreground">Нет совпадений — измените фильтр.</p>
              ) : null}
            <ul className="space-y-2">
              {filteredHistory.map((h) => (
                <li
                  key={h.id}
                  className="flex flex-col gap-2 rounded-lg border border-border bg-muted/10 px-3 py-2 sm:flex-row sm:items-center sm:justify-between"
                >
                  <div className="flex min-w-0 flex-wrap items-center gap-x-2 gap-y-1 text-sm">
                    <span className="font-mono text-xs text-muted-foreground">#{h.id}</span>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="h-7 gap-1 px-2 text-[10px] text-muted-foreground"
                      title="Копировать номер записи"
                      onClick={() => void copyTextToClipboard(String(h.id), "Номер записи скопирован")}
                    >
                      <ClipboardCopy className="size-3" />
                      ID
                    </Button>
                    <span className="text-muted-foreground">·</span>
                    <span>{h.created_at.slice(0, 19).replace("T", " ")}</span>
                    <span className="mx-2 text-muted-foreground">·</span>
                    <span>{(h.size_bytes / 1024).toFixed(1)} KiB</span>
                    {h.profile_id ? (
                      <>
                        <span className="mx-2 text-muted-foreground">·</span>
                        <span className="text-xs">профиль</span>
                      </>
                    ) : null}
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Button
                      type="button"
                      size="sm"
                      variant="secondary"
                      disabled={historyBusyId !== null}
                      onClick={() => void onHistoryToDraft(h)}
                    >
                      {historyBusyId === h.id ? <Loader2 className="size-4 animate-spin" /> : null}
                      В черновик
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      disabled={historyBusyId !== null}
                      onClick={() => void onExportHistoryJson(h)}
                    >
                      <FileJson className="size-4" />
                      JSON…
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="ghost"
                      className="text-destructive hover:bg-destructive/10 hover:text-destructive"
                      disabled={historyBusyId !== null}
                      onClick={() => void onHistoryDelete(h.id)}
                    >
                      <Trash2 className="size-4" />
                    </Button>
                  </div>
                </li>
              ))}
            </ul>
            </>
          )}
        </CardContent>
      </Card>

      <Dialog open={duplicateId !== null} onOpenChange={(o) => !o && setDuplicateId(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Копия профиля</DialogTitle>
            <DialogDescription>
              Будет создан новый профиль с тем же набором настроек. Имя должно отличаться от остальных, если хотите
              различать копии.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-2 py-2">
            <Label htmlFor="profile-dup-name">Имя копии</Label>
            <Input
              id="profile-dup-name"
              value={duplicateName}
              onChange={(e) => setDuplicateName(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") void onSaveDuplicate();
              }}
            />
          </div>
          <DialogFooter className="gap-2 sm:gap-0">
            <Button type="button" variant="outline" onClick={() => setDuplicateId(null)}>
              Отмена
            </Button>
            <Button type="button" onClick={() => void onSaveDuplicate()}>
              Сохранить копию
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <AlertDialog
        open={clearHistoryOpen}
        onOpenChange={(open) => {
          if (!open && clearHistoryBusy) return;
          setClearHistoryOpen(open);
        }}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Очистить всю историю?</AlertDialogTitle>
            <AlertDialogDescription>
              Все снимки конфигураций будут удалены из локальной базы. Профили и файлы на диске не затрагиваются.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter className="gap-2 sm:gap-0">
            <AlertDialogCancel disabled={clearHistoryBusy}>Отмена</AlertDialogCancel>
            <Button
              type="button"
              variant="destructive"
              loading={clearHistoryBusy}
              onClick={() => void onClearAllHistory()}
            >
              Очистить
            </Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <AlertDialog open={deleteId !== null} onOpenChange={(open) => !open && setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Удалить профиль?</AlertDialogTitle>
            <AlertDialogDescription>
              Действие необратимо. Файлы на диске игры не затрагиваются.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter className="gap-2 sm:gap-0">
            <AlertDialogCancel>Отмена</AlertDialogCancel>
            <Button type="button" variant="destructive" onClick={() => void confirmDelete()}>
              Удалить
            </Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <Dialog open={renameId !== null} onOpenChange={(o) => !o && setRenameId(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Переименовать профиль</DialogTitle>
            <DialogDescription>Новое имя отображается в списке и при загрузке в черновик.</DialogDescription>
          </DialogHeader>
          <div className="space-y-2 py-2">
            <Label htmlFor="profile-rename">Имя</Label>
            <Input
              id="profile-rename"
              value={renameName}
              onChange={(e) => setRenameName(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") void onSaveRename();
              }}
            />
          </div>
          <DialogFooter className="gap-2 sm:gap-0">
            <Button type="button" variant="outline" onClick={() => setRenameId(null)}>
              Отмена
            </Button>
            <Button type="button" onClick={() => void onSaveRename()}>
              Сохранить
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

function sanitizeFilePart(s: string): string {
  return s.replace(/[<>:"/\\|?*]/g, "_").trim() || "config";
}

function prettyJsonString(raw: string): string {
  try {
    return JSON.stringify(JSON.parse(raw), null, 2);
  } catch {
    return raw;
  }
}
