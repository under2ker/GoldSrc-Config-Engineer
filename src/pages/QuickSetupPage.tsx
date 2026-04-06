import { useEffect, useState } from "react";
import { toast } from "sonner";
import { generateConfig } from "@/lib/api";
import { saveCfgToDisk } from "@/lib/cfgFiles";
import { readLastModeId, writeLastModeId } from "@/lib/lastGenerationMode";
import { addRecentConfig } from "@/lib/recentConfigs";
import { useCatalogStore } from "@/stores/catalogStore";
import { useConfigStore } from "@/stores/configStore";
import { CfgTextPreview } from "@/components/common/CfgTextPreview";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
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
import { Switch } from "@/components/ui/switch";
import { pageCaptionClass, pageLeadClass, pageShellNarrowClass } from "@/lib/layoutTokens";
import { cn } from "@/lib/utils";

const STEP_LABELS = ["Старт", "Режим", "Пресет", "Готово"];

export function QuickSetupPage() {
  const modes = useCatalogStore((s) => s.modes);
  const presets = useCatalogStore((s) => s.presets);
  const loaded = useCatalogStore((s) => s.loaded);
  const catalogError = useCatalogStore((s) => s.error);

  const [step, setStep] = useState(0);
  const [modeId, setModeId] = useState("");
  const [usePreset, setUsePreset] = useState(false);
  const [presetId, setPresetId] = useState("");
  const [preview, setPreview] = useState<string | null>(null);
  const [rawCfg, setRawCfg] = useState<string | null>(null);
  const [defaultSaveName, setDefaultSaveName] = useState("autoexec.cfg");
  const [busy, setBusy] = useState(false);

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

  const progressPct = ((step + 1) / STEP_LABELS.length) * 100;

  function canNext(): boolean {
    if (step === 1) return !!modeId;
    if (step === 2) return !usePreset || !!presetId;
    return true;
  }

  async function runGenerate() {
    setBusy(true);
    try {
      const fromPreset = usePreset && presetId;
      const ao = useConfigStore.getState();
      const aliasOpts = {
        aliasPreset: ao.aliasPreset,
        includePractice: ao.includePractice,
        aliasEnabled: ao.aliasPreset === "custom" ? ao.aliasEnabled : null,
      };
      const r = fromPreset
        ? await generateConfig("preset", presetId, aliasOpts)
        : await generateConfig("mode", modeId, aliasOpts);
      if (!fromPreset) {
        writeLastModeId(modeId);
      }
      setRawCfg(r.content);
      setPreview(`// ${r.label}\n${r.content}`);
      setDefaultSaveName(fromPreset ? `preset-${presetId}.cfg` : `mode-${modeId}.cfg`);
      toast.success("Конфиг готов", { description: r.label });
    } catch (e: unknown) {
      setPreview(null);
      setRawCfg(null);
      const msg = String(e);
      toast.error("Ошибка генерации", { description: msg });
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className={pageShellNarrowClass}>
      <div>
        <p className={pageLeadClass}>
          Мастер из четырёх шагов: режим игры, опциональный про-пресет, генерация и сохранение.
        </p>
        {catalogError ? (
          <p className="mt-2 text-sm text-destructive">Не удалось загрузить список: {catalogError}</p>
        ) : null}
      </div>

      <div className="space-y-2">
        <div className={cn(pageCaptionClass, "flex justify-between")}>
          <span>
            Шаг {step + 1} из {STEP_LABELS.length}: {STEP_LABELS[step]}
          </span>
          <span>{Math.round(progressPct)}%</span>
        </div>
        <Progress value={loaded ? progressPct : 12} />
      </div>

      {!loaded ? (
        <Card>
          <CardHeader className="space-y-2">
            <Skeleton className="h-6 w-56" />
            <Skeleton className="h-4 w-full max-w-md" />
          </CardHeader>
          <CardContent className="space-y-4">
            <Skeleton className="h-24 w-full rounded-lg" />
            <div className="flex justify-end gap-2">
              <Skeleton className="h-9 w-24" />
              <Skeleton className="h-9 w-24" />
            </div>
          </CardContent>
        </Card>
      ) : null}

      <Card className={!loaded ? "hidden" : undefined}>
        <CardHeader>
          <CardTitle>{STEP_LABELS[step]}</CardTitle>
          <CardDescription>
            {step === 0 &&
              "Краткий путь к рабочему .cfg без ручного редактирования десятков CVAR."}
            {step === 1 && "Режим задаёт базовый набор параметров под выбранный стиль игры."}
            {step === 2 && "Про-пресет накладывает готовый сеттинг про-игрока (опционально)."}
            {step === 3 && "Сгенерируйте файл и сохраните его в папку с игрой через «Сохранить как…»."}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {step === 0 ? (
            <ul className="list-inside list-disc space-y-2 text-sm text-muted-foreground">
              <li>Режимы и про-пресеты подгружаются из встроенного каталога.</li>
              <li>На последнем шаге доступны превью и «Сохранить как…».</li>
              <li>Дальше сюда можно добавить сетевой профиль и пути к игре.</li>
            </ul>
          ) : null}

          {step === 1 ? (
            <div className="space-y-2">
              <Label htmlFor="qs-mode">Игровой режим</Label>
              <Select
                value={modeId}
                onValueChange={(v) => {
                  setModeId(v);
                  writeLastModeId(v);
                }}
                disabled={!loaded || modes.length === 0}
              >
                <SelectTrigger id="qs-mode">
                  <SelectValue placeholder="Выберите режим" />
                </SelectTrigger>
                <SelectContent>
                  {modes.map((m) => (
                    <SelectItem key={m.id} value={m.id}>
                      {m.name_ru} ({m.name_en})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          ) : null}

          {step === 2 ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between gap-4 rounded-lg border p-3">
                <div className="space-y-0.5">
                  <Label htmlFor="qs-preset-switch">Использовать про-пресет</Label>
                  <p className={pageCaptionClass}>
                    Если включено, в конфиге будет пресет, а не режим.
                  </p>
                </div>
                <Switch id="qs-preset-switch" checked={usePreset} onCheckedChange={setUsePreset} />
              </div>
              {usePreset ? (
                <div className="space-y-2">
                  <Label htmlFor="qs-preset">Пресет</Label>
                  <Select
                    value={presetId}
                    onValueChange={setPresetId}
                    disabled={!loaded || presets.length === 0}
                  >
                    <SelectTrigger id="qs-preset">
                      <SelectValue placeholder="Выберите пресет" />
                    </SelectTrigger>
                    <SelectContent>
                      {presets.map((p) => (
                        <SelectItem key={p.id} value={p.id}>
                          {p.name} — {p.team} / {p.role}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              ) : null}
            </div>
          ) : null}

          {step === 3 ? (
            <div className="space-y-4">
              <div className="rounded-md border bg-muted/40 p-3 text-sm">
                <p>
                  <span className="text-muted-foreground">Источник:</span>{" "}
                  {usePreset && presetId ? (
                    <>
                      пресет <code className="rounded bg-muted px-1">{presetId}</code>
                    </>
                  ) : (
                    <>
                      режим <code className="rounded bg-muted px-1">{modeId}</code>
                    </>
                  )}
                </p>
              </div>
              <Button
                type="button"
                variant="success"
                loading={busy}
                disabled={!loaded}
                onClick={() => void runGenerate()}
              >
                Сгенерировать конфиг
              </Button>
              {preview ? (
                <>
                  <Separator />
                  <ScrollArea className="h-56 rounded-md border">
                    <CfgTextPreview
                      text={preview}
                      className="p-3"
                      fontSizePx={14}
                      showLineNumbers
                    />
                  </ScrollArea>
                  <Button
                    type="button"
                    variant="secondary"
                    disabled={!rawCfg}
                    onClick={() => {
                      if (!rawCfg) return;
                      void saveCfgToDisk(rawCfg, defaultSaveName).then((p) => {
                        if (!p) {
                          toast.message("Сохранение отменено");
                          return;
                        }
                        const modeLabel =
                          usePreset && presetId
                            ? `Пресет: ${presets.find((x) => x.id === presetId)?.name ?? presetId}`
                            : `Режим: ${modes.find((x) => x.id === modeId)?.name_ru ?? modeId}`;
                        addRecentConfig({ path: p, modeLabel: `Быстрая настройка · ${modeLabel}` });
                        toast.success("Файл сохранён", { description: p });
                      });
                    }}
                  >
                    Сохранить как…
                  </Button>
                </>
              ) : null}
            </div>
          ) : null}
        </CardContent>
        <CardFooter className="flex flex-wrap justify-between gap-2">
          <Button
            type="button"
            variant="outline"
            disabled={step === 0}
            onClick={() => setStep((s) => Math.max(0, s - 1))}
          >
            Назад
          </Button>
          {step < STEP_LABELS.length - 1 ? (
            <Button
              type="button"
              disabled={!canNext()}
              onClick={() => canNext() && setStep((s) => Math.min(STEP_LABELS.length - 1, s + 1))}
            >
              Далее
            </Button>
          ) : null}
        </CardFooter>
      </Card>
    </div>
  );
}
