import { memo } from "react";
import { PieChart } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import type { ConfigCompletenessResult } from "@/lib/configCompleteness";
import { pageCaptionClass } from "@/lib/layoutTokens";
import { cn } from "@/lib/utils";

function progressTone(pct: number): { indicator: string; hint: string } {
  if (pct >= 80) {
    return {
      indicator: "bg-emerald-600 dark:bg-emerald-500",
      hint: "Большинство разделов представлены — при необходимости добейте сеть, звук и закупку в редакторе конфига.",
    };
  }
  if (pct >= 40) {
    return {
      indicator: "bg-blue-600 dark:bg-blue-500",
      hint: "Добавьте бинды, сетевые CVAR, прицел и чувствительность — как в v2 (индикатор по секциям).",
    };
  }
  return {
    indicator: "bg-amber-600 dark:bg-amber-500",
    hint: "Минимальный набор: сгенерируйте конфиг по режиму или импортируйте готовый .cfg, затем дополните разделы.",
  };
}

type DashboardConfigCompletenessCardProps = {
  result: ConfigCompletenessResult | null;
};

export const DashboardConfigCompletenessCard = memo(function DashboardConfigCompletenessCard({
  result,
}: DashboardConfigCompletenessCardProps) {
  if (!result) {
    return (
      <Card className="border-border/80 shadow-sm">
        <CardHeader className="pb-2">
          <div className="flex items-start gap-3">
            <div
              className="flex size-10 shrink-0 items-center justify-center rounded-xl border border-sky-500/25 bg-sky-500/10 text-sky-600 dark:text-sky-400"
              aria-hidden
            >
              <PieChart className="size-5" strokeWidth={1.75} />
            </div>
            <div className="min-w-0 space-y-1">
              <CardTitle className="text-base">Заполненность конфига</CardTitle>
              <CardDescription className={cn(pageCaptionClass, "sm:text-sm")}>
                Оценка по разделам (параметры, бинды, сеть, видео, прицел и др.) — как индикатор в версии на Python.
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <p className={pageCaptionClass}>
            Нет разобранного конфига: сгенерируйте .cfg на главной или импортируйте файл — тогда появится процент и
            полоса прогресса.
          </p>
        </CardContent>
      </Card>
    );
  }

  const { pct, done, total, sections } = result;
  const tone = progressTone(pct);

  return (
    <Card className="border-border/80 shadow-sm">
      <CardHeader className="pb-2">
        <div className="flex items-start gap-3">
          <div
            className="flex size-10 shrink-0 items-center justify-center rounded-xl border border-sky-500/25 bg-sky-500/10 text-sky-600 dark:text-sky-400"
            aria-hidden
          >
            <PieChart className="size-5" strokeWidth={1.75} />
          </div>
          <div className="min-w-0 space-y-1">
            <CardTitle className="text-base">Заполненность конфига</CardTitle>
            <CardDescription className={cn(pageCaptionClass, "sm:text-sm")}>
              Доля заполненных разделов по содержимому текущего черновика (импорт или последняя генерация на главной).
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-end justify-between gap-2">
          <span className="text-2xl font-semibold tabular-nums text-foreground">{pct}%</span>
          <span className="pb-0.5 text-xs text-muted-foreground">
            {done} из {total} разделов
          </span>
        </div>
        <Progress value={pct} className="h-2" indicatorClassName={tone.indicator} />
        <p className={pageCaptionClass}>{tone.hint}</p>
        <ul className="grid gap-1.5 text-[11px] leading-snug text-muted-foreground sm:grid-cols-2" aria-label="Разделы конфига">
          {sections.map((s) => (
            <li key={s.id} className="flex items-center gap-2">
              <span
                className={cn(
                  "size-1.5 shrink-0 rounded-full",
                  s.ok ? "bg-emerald-500" : "bg-muted-foreground/35",
                )}
                aria-hidden
              />
              <span className={cn(s.ok ? "text-foreground/90" : "text-muted-foreground")}>{s.label}</span>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
});
