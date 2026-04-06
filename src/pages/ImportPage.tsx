import { useCallback, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link } from "react-router-dom";
import { isTauri } from "@tauri-apps/api/core";
import { toast } from "sonner";
import {
  BookmarkPlus,
  ClipboardPaste,
  FileWarning,
  FolderOpen,
  Globe,
  Inbox,
  Loader2,
  Trash2,
  Upload,
} from "lucide-react";
import { checkCfgImportSafety, fetchTextFromUrl, parseImportCfg, profileSave } from "@/lib/api";
import { openCfgFile } from "@/lib/cfgFiles";
import { readFileAsText } from "@/lib/readFileAsText";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  AlertDialog,
  AlertDialogAction,
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
import { CfgTextPreview } from "@/components/common/CfgTextPreview";
import { EmptyState } from "@/components/common/EmptyState";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { pageCaptionClass, pageLeadClass, pageShellClass } from "@/lib/layoutTokens";
import { addRecentConfig } from "@/lib/recentConfigs";
import { useConfigStore } from "@/stores/configStore";
import { useProfileStore } from "@/stores/profileStore";
import type { CfgConfigParsed } from "@/types/api";
import { cn } from "@/lib/utils";
import {
  type ImportUrlFormValues,
  importUrlFormSchema,
  type SaveProfileNameFormValues,
  saveProfileNameSchema,
} from "@/lib/formSchemas";

const MAX_IMPORT_BYTES = 512 * 1024;

export function ImportPage() {
  const [path, setPath] = useState<string | null>(null);
  const [text, setText] = useState<string | null>(null);
  const [warnings, setWarnings] = useState<string[] | null>(null);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [parsed, setParsed] = useState<CfgConfigParsed | null>(null);
  const [saveProfileOpen, setSaveProfileOpen] = useState(false);
  const [saveProfileBusy, setSaveProfileBusy] = useState(false);
  const [urlBusy, setUrlBusy] = useState(false);

  const importUrlForm = useForm<ImportUrlFormValues>({
    resolver: zodResolver(importUrlFormSchema),
    defaultValues: { importUrl: "" },
    mode: "onSubmit",
  });

  const saveProfileForm = useForm<SaveProfileNameFormValues>({
    resolver: zodResolver(saveProfileNameSchema),
    defaultValues: { profileName: "" },
    mode: "onSubmit",
  });

  const reset = useCallback(() => {
    setPath(null);
    setText(null);
    setWarnings(null);
    setParsed(null);
    useConfigStore.getState().clearStagedProfile();
    toast.message("Импорт сброшен");
  }, []);

  const ingestText = useCallback(async (raw: string, displayPath: string) => {
    if (raw.length > MAX_IMPORT_BYTES) {
      toast.error("Файл слишком большой", {
        description: `Ограничение ${Math.round(MAX_IMPORT_BYTES / 1024)} КБ — укоротите конфиг или разбейте на части.`,
      });
      return;
    }
    setBusy(true);
    try {
      const w = await checkCfgImportSafety(raw);
      setPath(displayPath);
      setText(raw);
      setWarnings(w);
      if (w.length > 0) {
        toast.warning("Файл открыт с замечаниями", {
          description: `${w.length} предупреждений — проверьте список ниже.`,
        });
      } else {
        toast.success("Файл открыт", { description: displayPath });
      }
      addRecentConfig({
        path: displayPath,
        modeLabel: "Импорт",
      });
      if (isTauri()) {
        try {
          const p = await parseImportCfg(raw);
          setParsed(p);
          useConfigStore.getState().setStagedProfile(JSON.stringify(p), displayPath);
        } catch (pe: unknown) {
          setParsed(null);
          useConfigStore.getState().clearStagedProfile();
          toast.error("Разбор структуры не удался", { description: String(pe) });
        }
      } else {
        setParsed(null);
        useConfigStore.getState().clearStagedProfile();
      }
    } catch (e: unknown) {
      toast.error("Не удалось обработать файл", { description: String(e) });
    } finally {
      setBusy(false);
    }
  }, []);

  async function onSaveProfile(values: SaveProfileNameFormValues) {
    if (!parsed) return;
    setSaveProfileBusy(true);
    try {
      await profileSave(values.profileName, JSON.stringify(parsed));
      toast.success("Профиль сохранён");
      setSaveProfileOpen(false);
      saveProfileForm.reset({ profileName: "" });
      await useProfileStore.getState().refreshProfiles();
    } catch (e: unknown) {
      toast.error("Не удалось сохранить", { description: String(e) });
    } finally {
      setSaveProfileBusy(false);
    }
  }

  async function onPasteClipboard() {
    try {
      const t = await navigator.clipboard.readText();
      if (!t.trim()) {
        toast.message("Буфер обмена пуст");
        return;
      }
      await ingestText(t.trimEnd(), "clipboard.cfg");
    } catch {
      toast.error("Не удалось прочитать буфер", {
        description: "Разрешите доступ к буферу или вставьте текст вручную в «Просмотр».",
      });
    }
  }

  async function onFetchUrl(values: ImportUrlFormValues) {
    const u = values.importUrl;
    if (!isTauri()) return;
    setUrlBusy(true);
    try {
      const raw = await fetchTextFromUrl(u);
      await ingestText(raw, u);
    } catch (e: unknown) {
      toast.error("Не удалось загрузить", { description: String(e) });
    } finally {
      setUrlBusy(false);
    }
  }

  async function onPickFile() {
    try {
      const picked = await openCfgFile();
      if (!picked) {
        toast.message("Файл не выбран");
        return;
      }
      await ingestText(picked.text, picked.path);
    } catch (e: unknown) {
      toast.error("Не удалось прочитать файл", { description: String(e) });
    }
  }

  function onDragOver(e: React.DragEvent) {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  }

  function onDragLeave(e: React.DragEvent) {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  }

  function onDrop(e: React.DragEvent) {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const file = e.dataTransfer.files[0];
    if (!file) {
      toast.message("Файл не найден");
      return;
    }
    if (!file.name.toLowerCase().endsWith(".cfg")) {
      toast.error("Ожидается файл .cfg", { description: file.name });
      return;
    }
    void readFileAsText(file).then(
      (t) => ingestText(t, file.name),
      () => toast.error("Не удалось прочитать файл"),
    );
  }

  return (
    <div className={pageShellClass}>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className={pageLeadClass}>
            Откройте .cfg или перетащите его в область ниже. Опасные команды подсвечиваются предупреждениями — конфиг не
            уходит в сеть.
          </p>
          <p className="mt-2 flex flex-wrap gap-x-3 gap-y-1 text-sm">
            <Link to="/dashboard" className="text-primary underline-offset-4 hover:underline">
              На главную
            </Link>
            {isTauri() ? (
              <Link to="/profiles" className="text-primary underline-offset-4 hover:underline">
                Профили
              </Link>
            ) : null}
          </p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FolderOpen className="size-5 opacity-90" />
            Импорт из файла
          </CardTitle>
          <CardDescription>Выбор файла с диска или перетаскивание в окно программы.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onDrop={onDrop}
            className={cn(
              "group flex min-h-[132px] flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed px-4 py-8 text-center transition-[border-color,background-color,box-shadow]",
              dragActive
                ? "border-primary bg-primary/12 shadow-md"
                : "border-muted-foreground/35 bg-gradient-to-b from-muted/30 to-muted/15 hover:border-primary/50 hover:bg-accent/15 hover:shadow-sm",
            )}
          >
            <Upload
              className={cn(
                "size-8 text-muted-foreground transition-colors group-hover:text-primary",
                dragActive && "text-primary",
              )}
              aria-hidden
            />
            <p className="text-sm text-muted-foreground group-hover:text-foreground/90">
              Перетащите <span className="font-medium text-foreground">.cfg</span> сюда
            </p>
            <p className={pageCaptionClass}>или выберите файл ниже</p>
          </div>

          <div className="flex flex-wrap items-center gap-2 rounded-lg border border-border bg-muted/25 p-3">
            <Button type="button" variant="default" onClick={() => void onPickFile()} loading={busy}>
              Выбрать .cfg…
            </Button>
            <Button
              type="button"
              variant="secondary"
              disabled={busy}
              onClick={() => void onPasteClipboard()}
            >
              <ClipboardPaste className="size-4" />
              Вставить из буфера
            </Button>
            <Button
              type="button"
              variant="outline"
              disabled={!text}
              onClick={() => setConfirmOpen(true)}
            >
              <Trash2 className="size-4" />
              Сбросить
            </Button>
          </div>

          {path ? (
            <div className="flex flex-wrap items-center gap-2 text-sm">
              <span className="text-muted-foreground">Файл:</span>
              <Badge variant="secondary" className="max-w-full truncate font-mono text-xs">
                {path}
              </Badge>
            </div>
          ) : null}

          {warnings && warnings.length > 0 ? (
            <div className="rounded-md border border-warning/45 bg-warning/10 px-3 py-2">
              <p className="mb-2 flex items-center gap-2 text-sm font-medium text-warning-foreground">
                <FileWarning className="size-4 shrink-0 text-warning" aria-hidden />
                Предупреждения ({warnings.length})
              </p>
              <ul className="list-inside list-disc space-y-1 text-sm text-warning-foreground/90">
                {warnings.map((w, i) => (
                  <li key={`${i}-${w.slice(0, 32)}`}>{w}</li>
                ))}
              </ul>
            </div>
          ) : null}

          {parsed && isTauri() ? (
            <div className="rounded-lg border border-border bg-muted/20 px-3 py-3 text-sm">
              <p className="font-medium text-foreground">Разбор структуры</p>
              <ul className="mt-2 space-y-1 text-muted-foreground">
                <li>
                  Параметры (settings):{" "}
                  <span className="font-medium text-foreground">{Object.keys(parsed.settings).length}</span>
                </li>
                <li>
                  Бинды: <span className="font-medium text-foreground">{Object.keys(parsed.binds).length}</span>
                </li>
                <li>
                  Buy-бинды:{" "}
                  <span className="font-medium text-foreground">{Object.keys(parsed.buy_binds).length}</span>
                </li>
              </ul>
              <Button
                type="button"
                className="mt-3"
                variant="secondary"
                onClick={() => setSaveProfileOpen(true)}
              >
                <BookmarkPlus className="size-4" />
                Сохранить как профиль…
              </Button>
              <p className={cn(pageCaptionClass, "mt-3")}>
                Скриптовые алиасы (отдельно от этого файла) настраиваются в разделе{" "}
                <Link to="/aliases" className="text-primary underline-offset-4 hover:underline">
                  Алиасы
                </Link>{" "}
                — они попадут в экспорт вместе с режимом или пресетом.
              </p>
            </div>
          ) : null}

          {text ? (
            <ScrollArea className="h-[min(24rem,50vh)] rounded-md border border-border bg-muted/10">
              <CfgTextPreview text={text} className="p-3" fontSizePx={14} showLineNumbers />
            </ScrollArea>
          ) : (
            <EmptyState
              className="min-h-[200px] py-10"
              icon={Inbox}
              title="Нет файла"
              description="Выберите .cfg кнопкой выше или перетащите его в пунктирную область. Содержимое не уходит в сеть — только проверка и превью локально."
            />
          )}
        </CardContent>
      </Card>

      {isTauri() ? (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe className="size-5 opacity-90" />
              По ссылке
            </CardTitle>
            <CardDescription>
              Прямая загрузка текста по http(s). Убедитесь, что это доверенный источник и что по ссылке отдаётся обычный
              текст конфига, а не HTML-страница.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Form {...importUrlForm}>
              <form
                className="flex flex-col gap-3 sm:flex-row sm:items-end"
                onSubmit={importUrlForm.handleSubmit((v) => void onFetchUrl(v))}
              >
                <FormField
                  control={importUrlForm.control}
                  name="importUrl"
                  render={({ field }) => (
                    <FormItem className="min-w-0 flex-1">
                      <FormLabel>URL</FormLabel>
                      <FormControl>
                        <Input
                          {...field}
                          id="import-url"
                          type="url"
                          autoComplete="url"
                          placeholder="https://…/config.cfg"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <div className="flex flex-wrap gap-2">
                  <Button type="submit" disabled={urlBusy || busy}>
                    {urlBusy ? <Loader2 className="size-4 animate-spin" /> : null}
                    Загрузить
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    disabled={urlBusy || !importUrlForm.watch("importUrl").trim()}
                    onClick={() => importUrlForm.reset({ importUrl: "" })}
                  >
                    Очистить поле
                  </Button>
                </div>
              </form>
            </Form>
          </CardContent>
        </Card>
      ) : null}

      <AlertDialog open={confirmOpen} onOpenChange={setConfirmOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Сбросить импорт?</AlertDialogTitle>
            <AlertDialogDescription>
              Текущий путь, текст и предупреждения будут очищены. Файл на диске не изменяется.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter className="gap-2 sm:gap-0">
            <AlertDialogCancel>Отмена</AlertDialogCancel>
            <AlertDialogAction asChild>
              <Button type="button" variant="destructive" onClick={() => reset()}>
                Сбросить
              </Button>
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <Dialog
        open={saveProfileOpen}
        onOpenChange={(open) => {
          setSaveProfileOpen(open);
          if (open) saveProfileForm.reset({ profileName: "" });
        }}
      >
        <DialogContent>
          <Form {...saveProfileForm}>
            <form
              className="space-y-4"
              onSubmit={saveProfileForm.handleSubmit((v) => void onSaveProfile(v))}
            >
              <DialogHeader>
                <DialogTitle>Сохранить как профиль</DialogTitle>
                <DialogDescription>
                  Имя для списка на странице «Профили». Данные только на этом устройстве.
                </DialogDescription>
              </DialogHeader>
              <FormField
                control={saveProfileForm.control}
                name="profileName"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="sr-only">Имя профиля</FormLabel>
                    <FormControl>
                      <Input
                        {...field}
                        placeholder="Например: мой конфиг с сервера"
                        autoFocus
                        autoComplete="off"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <DialogFooter className="gap-2 sm:gap-0">
                <Button type="button" variant="outline" onClick={() => setSaveProfileOpen(false)}>
                  Отмена
                </Button>
                <Button type="submit" loading={saveProfileBusy} disabled={!parsed}>
                  Сохранить
                </Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
