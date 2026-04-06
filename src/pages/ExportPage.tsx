import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { isTauri } from "@tauri-apps/api/core";
import { open } from "@tauri-apps/plugin-dialog";
import { toast } from "sonner";
import {
  deployModularFiles,
  exportConfigSnapshot,
  exportModularConfig,
  generateConfig,
  historyAppend,
} from "@/lib/api";
import type { ModularFile } from "@/types/api";
import { saveCfgToDisk } from "@/lib/cfgFiles";
import { readLastModeId, writeLastModeId } from "@/lib/lastGenerationMode";
import { addRecentConfig } from "@/lib/recentConfigs";
import { useCatalogStore } from "@/stores/catalogStore";
import { useConfigStore } from "@/stores/configStore";
import { CfgTextPreview } from "@/components/common/CfgTextPreview";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { pageCaptionClass, pageLeadClass, pageShellClass } from "@/lib/layoutTokens";
import { cn } from "@/lib/utils";

type ExportSource = "mode" | "preset";

export function ExportPage() {
  const modes = useCatalogStore((s) => s.modes);
  const presets = useCatalogStore((s) => s.presets);
  const loaded = useCatalogStore((s) => s.loaded);
  const aliasPreset = useConfigStore((s) => s.aliasPreset);
  const includePractice = useConfigStore((s) => s.includePractice);
  const aliasEnabled = useConfigStore((s) => s.aliasEnabled);

  const [tab, setTab] = useState("single");
  const [source, setSource] = useState<ExportSource>("mode");
  const [modeId, setModeId] = useState("");
  const [presetId, setPresetId] = useState("");
  const [preview, setPreview] = useState<string | null>(null);
  const [rawCfg, setRawCfg] = useState<string | null>(null);
  const [saveName, setSaveName] = useState("autoexec.cfg");
  const [busy, setBusy] = useState(false);
  const [modularFiles, setModularFiles] = useState<ModularFile[] | null>(null);
  const [modularPreviewRel, setModularPreviewRel] = useState<string | null>(null);
  const [modularBusy, setModularBusy] = useState(false);

  useEffect(() => {
    void useCatalogStore.getState().load();
  }, []);

  useEffect(() => {
    if (!loaded || modes.length === 0) return;
    setModeId((cur) => {
      if (cur && modes.some((m) => m.id === cur)) return cur;
      const persisted = readLastModeId();
      if (persisted && modes.some((m) => m.id === persisted)) return persisted;
      return modes.find((m) => m.id === "classic")?.id ?? modes[0].id;
    });
  }, [loaded, modes]);

  useEffect(() => {
    if (!loaded || presets.length === 0) return;
    setPresetId((cur) => {
      if (cur && presets.some((p) => p.id === cur)) return cur;
      return presets[0].id;
    });
  }, [loaded, presets]);

  async function runExport() {
    setBusy(true);
    try {
      const id = source === "mode" ? modeId : presetId;
      if (source === "mode") {
        writeLastModeId(modeId);
      }
      const r = await generateConfig(source, id, {
        aliasPreset,
        includePractice,
        aliasEnabled: aliasPreset === "custom" ? aliasEnabled : null,
      });
      setRawCfg(r.content);
      setPreview(`// ${r.label}\n${r.content}`);
      setSaveName(source === "mode" ? `mode-${modeId}.cfg` : `preset-${presetId}.cfg`);
      let desc = r.label;
      if (isTauri()) {
        try {
          const snapshot = await exportConfigSnapshot(source, id, {
            aliasPreset,
            includePractice,
            aliasEnabled: aliasPreset === "custom" ? aliasEnabled : null,
          });
          await historyAppend(snapshot, null);
          desc += " · снимок в истории";
        } catch {
          /* не блокируем экспорт */
        }
      }
      toast.success("Экспорт подготовлен", { description: desc });
    } catch (e: unknown) {
      setPreview(null);
      setRawCfg(null);
      toast.error("Ошибка", { description: String(e) });
    } finally {
      setBusy(false);
    }
  }

  async function runModularExport() {
    setModularBusy(true);
    try {
      const id = source === "mode" ? modeId : presetId;
      if (source === "mode") {
        writeLastModeId(modeId);
      }
      const files = await exportModularConfig(source, id, {
        aliasPreset,
        includePractice,
        aliasEnabled: aliasPreset === "custom" ? aliasEnabled : null,
      });
      setModularFiles(files);
      setModularPreviewRel(files[0]?.relative_path ?? null);
      let desc = `${files.length} файлов`;
      if (isTauri()) {
        try {
          const snapshot = await exportConfigSnapshot(source, id, {
            aliasPreset,
            includePractice,
            aliasEnabled: aliasPreset === "custom" ? aliasEnabled : null,
          });
          await historyAppend(snapshot, null);
          desc += " · снимок в истории";
        } catch {
          /* история не обязательна */
        }
      }
      toast.success("Модульный набор готов", { description: desc });
    } catch (e: unknown) {
      setModularFiles(null);
      setModularPreviewRel(null);
      toast.error("Ошибка", { description: String(e) });
    } finally {
      setModularBusy(false);
    }
  }

  async function writeModularToFolder() {
    if (!modularFiles?.length || !isTauri()) return;
    const dir = await open({
      directory: true,
      multiple: false,
      title: "Куда записать файлы (например папка cstrike)",
    });
    if (dir === null) return;
    const target = typeof dir === "string" ? dir : dir[0];
    try {
      await deployModularFiles(target, modularFiles);
      toast.success("Файлы записаны", { description: target });
    } catch (e: unknown) {
      toast.error("Не удалось записать", { description: String(e) });
    }
  }

  return (
    <div className={pageShellClass}>
      <p className={pageLeadClass}>
        Один цельный файл или модульный набор (отдельные `config/*.cfg` и `autoexec.cfg`). В программе для Windows можно
        сразу записать набор в выбранную папку. Скриптовые алиасы настраиваются на странице{" "}
        <Link to="/aliases" className="font-medium text-primary underline-offset-4 hover:underline">
          Алиасы
        </Link>{" "}
        (в модульном экспорте создаётся <code className="rounded bg-muted px-1 text-xs">config/aliases.cfg</code> и
        подключается первым). После выгрузки удобно задать{" "}
        <Link to="/launch-options" className="font-medium text-primary underline-offset-4 hover:underline">
          параметры запуска Steam
        </Link>
        , чтобы игра подхватила <code className="rounded bg-muted px-1 text-xs">autoexec.cfg</code>.
      </p>
      <div className={cn(pageCaptionClass, "flex flex-wrap items-center gap-2")}>
        <span>Текущий пресет алиасов:</span>
        <Badge variant="secondary">{aliasPreset}</Badge>
        {includePractice ? <Badge variant="outline">практика</Badge> : null}
        <Button
          type="button"
          variant="ghost"
          size="sm"
          className="h-7 text-xs"
          onClick={() => {
            useConfigStore.setState({
              aliasPreset: "minimal",
              includePractice: false,
              aliasEnabled: {},
            });
            toast.message("Алиасы сброшены к минимуму");
          }}
        >
          Сбросить алиасы
        </Button>
      </div>

      {!loaded ? (
        <Card>
          <CardHeader className="space-y-2">
            <Skeleton className="h-6 w-48" />
            <Skeleton className="h-4 w-full max-w-lg" />
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-4">
              <Skeleton className="h-10 flex-1" />
              <Skeleton className="h-10 flex-1" />
            </div>
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-9 w-40" />
          </CardContent>
        </Card>
      ) : (
      <Tabs value={tab} onValueChange={setTab}>
        <TabsList className="grid w-full max-w-md grid-cols-2">
          <TabsTrigger value="single">Один файл</TabsTrigger>
          <TabsTrigger value="modular">Модульный</TabsTrigger>
        </TabsList>
        <TabsContent value="single" className="space-y-6 pt-4">
          <Card>
            <CardHeader>
              <CardTitle>Параметры</CardTitle>
              <CardDescription>Выберите источник и сформируйте текст конфига.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-3">
                <Label>Тип</Label>
                <RadioGroup
                  value={source}
                  onValueChange={(v) => setSource(v as ExportSource)}
                  className="flex flex-col gap-2 sm:flex-row sm:gap-6"
                >
                  <label className="flex cursor-pointer items-center gap-2 text-sm">
                    <RadioGroupItem value="mode" id="exp-mode" />
                    <span>Режим</span>
                  </label>
                  <label className="flex cursor-pointer items-center gap-2 text-sm">
                    <RadioGroupItem value="preset" id="exp-preset" />
                    <span>Про-пресет</span>
                  </label>
                </RadioGroup>
              </div>

              {source === "mode" ? (
                <div className="space-y-2">
                  <Label htmlFor="exp-mode-select">Режим</Label>
                  <Select
                    value={modeId}
                    onValueChange={(v) => {
                      setModeId(v);
                      writeLastModeId(v);
                    }}
                    disabled={!loaded || !modes.length}
                  >
                    <SelectTrigger id="exp-mode-select">
                      <SelectValue placeholder="Режим" />
                    </SelectTrigger>
                    <SelectContent>
                      {modes.map((m) => (
                        <SelectItem key={m.id} value={m.id}>
                          {m.name_ru}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              ) : (
                <div className="space-y-2">
                  <Label htmlFor="exp-preset-select">Пресет</Label>
                  <Select
                    value={presetId}
                    onValueChange={setPresetId}
                    disabled={!loaded || !presets.length}
                  >
                    <SelectTrigger id="exp-preset-select">
                      <SelectValue placeholder="Пресет" />
                    </SelectTrigger>
                    <SelectContent>
                      {presets.map((p) => (
                        <SelectItem key={p.id} value={p.id}>
                          {p.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}

              <Button
                type="button"
                variant="success"
                loading={busy}
                disabled={!loaded}
                onClick={() => void runExport()}
              >
                Сформировать .cfg
              </Button>

              {preview && rawCfg ? (
                <>
                  <Separator />
                  <div className="space-y-2">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-sm text-muted-foreground">Превью</span>
                      <Badge variant="outline" className="text-[10px]">
                        готово к сохранению
                      </Badge>
                    </div>
                    <ScrollArea className="h-64 rounded-md border">
                      <CfgTextPreview
                        text={preview}
                        className="p-3"
                        fontSizePx={14}
                        showLineNumbers
                      />
                    </ScrollArea>
                  </div>
                  <Button
                    type="button"
                    variant="secondary"
                    onClick={() =>
                      void saveCfgToDisk(rawCfg, saveName).then((p) => {
                        if (!p) {
                          toast.message("Отменено");
                          return;
                        }
                        const modeLabel =
                          source === "mode"
                            ? `Экспорт · ${modes.find((m) => m.id === modeId)?.name_ru ?? modeId}`
                            : `Экспорт · пресет ${presets.find((x) => x.id === presetId)?.name ?? presetId}`;
                        addRecentConfig({ path: p, modeLabel });
                        toast.success("Сохранено", { description: p });
                      })
                    }
                  >
                    Сохранить как…
                  </Button>
                </>
              ) : null}
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="modular" className="pt-4">
          <Card>
            <CardHeader>
              <CardTitle>Модульный экспорт</CardTitle>
              <CardDescription>
                Категории в отдельные <code className="text-xs">config/*.cfg</code>, при необходимости{" "}
                <code className="text-xs">config/aliases.cfg</code>, <code className="text-xs">binds</code>, справочник{" "}
                <code className="text-xs">config/buyscripts.cfg</code>, <code className="text-xs">buy_binds</code>, затем{" "}
                <code className="text-xs">autoexec.cfg</code> с цепочкой <code className="text-xs">exec</code>.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button
                type="button"
                variant="success"
                loading={modularBusy}
                onClick={() => void runModularExport()}
                disabled={modularBusy || !loaded}
              >
                {modularBusy ? "Сборка…" : "Собрать модульный набор"}
              </Button>
              {modularFiles && modularFiles.length > 0 ? (
                <>
                  <p className="text-sm text-muted-foreground">
                    Файлов: <span className="font-medium text-foreground">{modularFiles.length}</span>
                    {isTauri()
                      ? ". Ниже предпросмотр; кнопка «Записать всё в папку» сохранит файлы на диск."
                      : ". В браузере скопируйте содержимое вручную или используйте настольную версию."}
                  </p>
                  <div className="space-y-2">
                    <Label htmlFor="modular-file">Файл для предпросмотра</Label>
                    <Select
                      value={modularPreviewRel ?? undefined}
                      onValueChange={(v) => setModularPreviewRel(v)}
                    >
                      <SelectTrigger id="modular-file">
                        <SelectValue placeholder="Выберите файл" />
                      </SelectTrigger>
                      <SelectContent>
                        {modularFiles.map((f) => (
                          <SelectItem key={f.relative_path} value={f.relative_path}>
                            {f.relative_path}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <ScrollArea className="h-64 rounded-md border">
                    <CfgTextPreview
                      text={
                        modularFiles.find((f) => f.relative_path === modularPreviewRel)?.content ?? ""
                      }
                      className="p-3"
                      fontSizePx={13}
                      showLineNumbers
                    />
                  </ScrollArea>
                  {isTauri() ? (
                    <Button type="button" variant="secondary" onClick={() => void writeModularToFolder()}>
                      Записать всё в папку…
                    </Button>
                  ) : null}
                </>
              ) : (
                <p className="text-sm text-muted-foreground">
                  Выберите режим или пресет на вкладке «Один файл» (те же переключатели выше), затем нажмите «Собрать
                  модульный набор».
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
      )}
    </div>
  );
}
