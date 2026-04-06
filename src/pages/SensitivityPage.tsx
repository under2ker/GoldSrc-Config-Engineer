import { useMemo, useState } from "react";
import { MousePointer2 } from "lucide-react";
import { approxCmPer360, compareIndex } from "@/lib/csSensitivity";
import { pageCaptionClass, pageLeadClass, pageOverlineClass, pageShellClass } from "@/lib/layoutTokens";
import { cn } from "@/lib/utils";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";

function parseNum(s: string, fallback: number): number {
  const n = Number.parseFloat(s.replace(",", "."));
  return Number.isFinite(n) ? n : fallback;
}

export function SensitivityPage() {
  const [dpiStr, setDpiStr] = useState("800");
  const [sensStr, setSensStr] = useState("3");
  const [mYaw, setMYaw] = useState([0.022]);

  const dpi = parseNum(dpiStr, 800);
  const sens = parseNum(sensStr, 3);
  const idx = useMemo(() => compareIndex(dpi, sens), [dpi, sens]);
  const cm = useMemo(() => approxCmPer360(dpi, sens, mYaw[0]), [dpi, sens, mYaw]);

  return (
    <div className={pageShellClass}>
      <div className="flex flex-wrap items-start gap-3">
        <div className="flex size-10 shrink-0 items-center justify-center rounded-xl border border-primary/30 bg-primary/10">
          <MousePointer2 className="size-5 text-primary" strokeWidth={1.75} aria-hidden />
        </div>
        <div className="min-w-0 space-y-1">
          <p className="text-sm font-medium text-foreground">Чувствительность мыши</p>
          <p className={pageLeadClass}>
            Оценка длины дуги на полный оборот и индекс для сравнения с чужими конфигами. Точный ход в игре зависит от
            акселерации, сырого ввода и остальных CVAR — проверяйте на сервере или в AIM-карте.
          </p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle className="text-base">Ваши значения</CardTitle>
            <CardDescription>DPI мыши и чувствительность из игры (меню Options → Mouse).</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="se-dpi">DPI мыши</Label>
              <Input
                id="se-dpi"
                inputMode="decimal"
                value={dpiStr}
                onChange={(e) => setDpiStr(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="se-sens">Чувствительность в CS 1.6</Label>
              <Input
                id="se-sens"
                inputMode="decimal"
                value={sensStr}
                onChange={(e) => setSensStr(e.target.value)}
              />
            </div>
            <div className="grid gap-2 sm:grid-cols-[minmax(0,10rem)_1fr_minmax(0,4.5rem)] sm:items-center sm:gap-3">
              <Label className="text-sm font-medium leading-snug sm:min-h-[2.5rem] sm:py-1">
                m_yaw (по умолчанию 0.022)
              </Label>
              <Slider
                className="py-1 sm:py-0"
                min={0.015}
                max={0.03}
                step={0.0005}
                value={mYaw}
                onValueChange={setMYaw}
              />
              <span className="text-right font-mono text-sm tabular-nums text-muted-foreground sm:min-w-0">
                {mYaw[0].toFixed(4)}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card className="border-primary/15 shadow-sm">
          <CardHeader>
            <CardTitle className="text-base">Результат</CardTitle>
            <CardDescription>Ориентиры — подставьте свои реальные DPI и sens из конфига.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 text-sm">
            <div className="rounded-lg border bg-muted/30 p-4">
              <p className={pageOverlineClass}>Индекс для сравнения</p>
              <p className="mt-1 text-2xl font-semibold tabular-nums">{idx > 0 ? Math.round(idx) : "—"}</p>
              <p className={cn(pageCaptionClass, "mt-2")}>
                DPI × чувствительность — удобно сравнивать с чужими настройками.
              </p>
            </div>
            <div className="rounded-lg border bg-muted/30 p-4">
              <p className={pageOverlineClass}>Примерно см на 360°</p>
              <p className="mt-1 text-2xl font-semibold tabular-nums">
                {cm > 0 ? `${cm.toFixed(1)} см` : "—"}
              </p>
              <p className={cn(pageCaptionClass, "mt-2")}>
                Оценка по распространённой формуле для CS 1.6 при m_yaw ≈ 0.022; при сильно другом m_yaw смотрите
                ползунок слева.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
