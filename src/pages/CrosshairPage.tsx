import { useMemo, useState } from "react";
import { toast } from "sonner";
import { Copy, HelpCircle } from "lucide-react";
import { CrosshairCanvas } from "@/components/common/CrosshairCanvas";
import { CfgTextPreview } from "@/components/common/CfgTextPreview";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useDebouncedValue } from "@/hooks/useDebouncedValue";
import { pageCaptionClass, pageLeadClass, pageShellClass } from "@/lib/layoutTokens";
import { cn } from "@/lib/utils";

const COLOR_PRESETS = [
  { name: "Зелёный", value: "#00ff33" },
  { name: "Лайм", value: "#ccff00" },
  { name: "Белый", value: "#ffffff" },
  { name: "Жёлтый", value: "#ffcc00" },
  { name: "Красный", value: "#ff4444" },
  { name: "Голубой", value: "#66ccff" },
];

export function CrosshairPage() {
  const [armLength, setArmLength] = useState([6]);
  const [gap, setGap] = useState([2]);
  const [thickness, setThickness] = useState([2]);
  const [outline, setOutline] = useState(true);
  const [color, setColor] = useState(COLOR_PRESETS[0].value);
  const [useDarkBg, setUseDarkBg] = useState(true);

  const previewArm = useDebouncedValue(armLength[0], 48);
  const previewGap = useDebouncedValue(gap[0], 48);
  const previewThickness = useDebouncedValue(thickness[0], 48);

  const cfgLines = useMemo(() => {
    const a = armLength[0];
    const g = gap[0];
    const t = thickness[0];
    const cl = color;
    return [
      "// --- Превью прицела (Canvas) → ориентиры для GoldSrc / CS 1.6 ---",
      "// Реальные имена CVAR зависят от модов (WON / Steam, CS). Подстройте в игре.",
      `// arm≈${a} gap≈${g} thick=${t} color=${cl}`,
      "",
      `cl_crosshair_size "${Math.max(1, Math.round((a + g) / 2))}"`,
      `cl_dynamiccrosshair "0"`,
      `// cl_crosshair_translucent "0"`,
    ].join("\n");
  }, [armLength, gap, thickness, color]);

  const bg = useDarkBg ? "oklch(0.2 0.02 264)" : "oklch(0.95 0.01 264)";

  async function copyCfg() {
    try {
      await navigator.clipboard.writeText(cfgLines);
      toast.success("Скопировано в буфер");
    } catch {
      toast.error("Не удалось скопировать");
    }
  }

  return (
    <div className={pageShellClass}>
      <p className={pageLeadClass}>
        Слева — якорь превью (квадрат 1:1), справа — параметры. Значения ниже — ориентир для ручного ввода CVAR.
      </p>

      <div className="grid gap-6 lg:grid-cols-2 lg:items-stretch">
        <Card className="flex flex-col overflow-hidden shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle className="text-base font-semibold tracking-tight">Превью прицела</CardTitle>
            <CardDescription className="font-sans text-sm">
              Квадратная область совпадает с логическим холстом (фиксированные пропорции).
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-1 items-center justify-center bg-muted/20 px-4 py-6">
            <div
              className={cn(
                "relative flex aspect-square w-full max-w-[280px] items-center justify-center rounded-xl border border-border bg-background/80 shadow-inner",
                useDarkBg ? "bg-card" : "bg-background",
              )}
            >
              <CrosshairCanvas
                className="rounded-lg"
                armLength={previewArm}
                gap={previewGap}
                thickness={previewThickness}
                outline={outline}
                color={color}
                background={bg}
              />
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle className="text-base font-semibold tracking-tight">Параметры</CardTitle>
            <CardDescription className="font-sans text-sm">
              Слайдеры обновляют текст конфига сразу; canvas слегка сглажен (debounce).
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div
              className={cn(
                "flex flex-wrap items-center justify-between gap-4 rounded-lg border p-3 transition-[border-color,background-color,box-shadow]",
                useDarkBg
                  ? "border-primary/50 bg-primary/[0.08] shadow-sm"
                  : "border-border bg-transparent",
              )}
            >
              <div className="space-y-0.5">
                <Label htmlFor="ch-bg" className="text-sm font-medium">
                  Тёмный фон превью
                </Label>
                <p className={pageCaptionClass}>
                  {useDarkBg ? "Включено — фон как на тёмной карте." : "Выключено — светлая подложка."}
                </p>
              </div>
              <Switch id="ch-bg" checked={useDarkBg} onCheckedChange={setUseDarkBg} />
            </div>

            <div className="grid gap-3">
              <div className="grid gap-2 sm:grid-cols-[minmax(0,9rem)_1fr_2.5rem] sm:items-center sm:gap-3">
                <div className="flex min-h-[1.5rem] items-center gap-1.5">
                  <Label className="text-sm font-medium">Длина луча</Label>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <button
                        type="button"
                        className="rounded-sm text-muted-foreground outline-none hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring"
                        aria-label="Справка: cl_crosshair_size"
                      >
                        <HelpCircle className="size-3.5" />
                      </button>
                    </TooltipTrigger>
                    <TooltipContent className="max-w-xs text-xs leading-snug">
                      В конфиге обычно задаётся через <span className="font-mono">cl_crosshair_size</span>: условный размер
                      прицела в GoldSrc; слайдеры ниже дают ориентир для ручного подбора.
                    </TooltipContent>
                  </Tooltip>
                </div>
                <Slider className="py-1 sm:py-0" min={1} max={20} step={1} value={armLength} onValueChange={setArmLength} />
                <span className="text-right font-mono text-sm tabular-nums text-muted-foreground">{armLength[0]}</span>
              </div>
              <div className="grid gap-2 sm:grid-cols-[minmax(0,9rem)_1fr_2.5rem] sm:items-center sm:gap-3">
                <div className="flex min-h-[1.5rem] items-center gap-1.5">
                  <Label className="text-sm font-medium">Зазор</Label>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <button
                        type="button"
                        className="rounded-sm text-muted-foreground outline-none hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring"
                        aria-label="Справка: зазор прицела"
                      >
                        <HelpCircle className="size-3.5" />
                      </button>
                    </TooltipTrigger>
                    <TooltipContent className="max-w-xs text-xs leading-snug">
                      Визуальный зазор между центром и началом лучей; в чистом GoldSrc часть эффектов задаётся другими CVAR
                      (зависит от клиента).
                    </TooltipContent>
                  </Tooltip>
                </div>
                <Slider className="py-1 sm:py-0" min={0} max={12} step={1} value={gap} onValueChange={setGap} />
                <span className="text-right font-mono text-sm tabular-nums text-muted-foreground">{gap[0]}</span>
              </div>
              <div className="grid gap-2 sm:grid-cols-[minmax(0,9rem)_1fr_2.5rem] sm:items-center sm:gap-3">
                <div className="flex min-h-[1.5rem] items-center gap-1.5">
                  <Label className="text-sm font-medium">Толщина</Label>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <button
                        type="button"
                        className="rounded-sm text-muted-foreground outline-none hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring"
                      >
                        <HelpCircle className="size-3.5" />
                      </button>
                    </TooltipTrigger>
                    <TooltipContent className="max-w-xs text-xs leading-snug">
                      Толщина линий на превью; в .cfg может соответствовать параметрам вроде{" "}
                      <span className="font-mono">cl_crosshair_translucent</span> / размеру — уточняйте под свою сборку.
                    </TooltipContent>
                  </Tooltip>
                </div>
                <Slider className="py-1 sm:py-0" min={1} max={5} step={1} value={thickness} onValueChange={setThickness} />
                <span className="text-right font-mono text-sm tabular-nums text-muted-foreground">{thickness[0]}</span>
              </div>
            </div>

            <div className="flex flex-wrap items-center justify-between gap-4 rounded-lg border border-border p-3">
              <div className="space-y-0.5">
                <div className="flex items-center gap-1.5">
                  <Label htmlFor="ch-out" className="text-sm font-medium">
                    Обводка
                  </Label>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <button
                        type="button"
                        className="rounded-sm text-muted-foreground outline-none hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring"
                        aria-label="Справка: обводка прицела"
                      >
                        <HelpCircle className="size-3.5" />
                      </button>
                    </TooltipTrigger>
                    <TooltipContent className="max-w-xs text-xs leading-snug">
                      На превью — контрастная обводка лучей; в игре близкие эффекты задаются отдельными CVAR (например, прозрачность).
                    </TooltipContent>
                  </Tooltip>
                </div>
                <p className={pageCaptionClass}>Тёмная каёмка вокруг линий.</p>
              </div>
              <Switch id="ch-out" checked={outline} onCheckedChange={setOutline} />
            </div>

            <div className="space-y-2">
              <Label className="text-sm font-medium">Цвет</Label>
              <div className="flex flex-wrap gap-2">
                {COLOR_PRESETS.map((c) => (
                  <button
                    key={c.value}
                    type="button"
                    title={c.name}
                    className={cn(
                      "size-8 rounded-md border-2 transition-transform motion-safe:hover:scale-105",
                      color === c.value ? "border-primary ring-2 ring-ring" : "border-border",
                    )}
                    style={{ backgroundColor: c.value }}
                    onClick={() => setColor(c.value)}
                  />
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex flex-row flex-wrap items-center justify-between gap-2 space-y-0">
          <div>
            <CardTitle className="text-base font-semibold">Фрагмент для .cfg</CardTitle>
            <CardDescription className="font-sans">Скопируйте и доработайте под свою сборку.</CardDescription>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Tooltip>
              <TooltipTrigger asChild>
                <span className="cursor-help rounded-md border border-border/80 bg-muted/30 px-2 py-0.5 font-mono text-[10px] text-muted-foreground">
                  cl_dynamiccrosshair
                </span>
              </TooltipTrigger>
              <TooltipContent className="max-w-xs text-xs leading-snug">
                В фрагменте ниже отключено (<span className="font-mono">0</span>): статичный прицел при стрельбе — типичная настройка для соревновательного стиля.
              </TooltipContent>
            </Tooltip>
          </div>
          <Button type="button" size="sm" variant="outline" onClick={() => void copyCfg()}>
            <Copy className="size-4" />
            Копировать
          </Button>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto rounded-lg border border-border bg-muted/15">
            <CfgTextPreview text={cfgLines} className="p-3" fontSizePx={14} showLineNumbers />
          </div>
        </CardContent>
      </Card>

      <Separator className="opacity-50" />
      <p className={pageCaptionClass}>
        Дальше: сравнение двух пресетов рядом и подсказки по точным именам команд из игры.
      </p>
    </div>
  );
}
