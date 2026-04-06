import { memo } from "react";
import { PieChart } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import type { ConfigCompletenessResult } from "@/lib/configCompleteness";
import { interpolate, useI18n } from "@/lib/i18n";
import { pageCaptionClass } from "@/lib/layoutTokens";
import { cn } from "@/lib/utils";

function progressToneClass(pct: number): string {
  if (pct >= 80) {
    return "bg-emerald-600 dark:bg-emerald-500";
  }
  if (pct >= 40) {
    return "bg-blue-600 dark:bg-blue-500";
  }
  return "bg-amber-600 dark:bg-amber-500";
}

function completenessHintKey(pct: number): string {
  if (pct >= 80) {
    return "dashboard.completeness.hintHigh";
  }
  if (pct >= 40) {
    return "dashboard.completeness.hintMid";
  }
  return "dashboard.completeness.hintLow";
}

type DashboardConfigCompletenessCardProps = {
  result: ConfigCompletenessResult | null;
};

export const DashboardConfigCompletenessCard = memo(function DashboardConfigCompletenessCard({
  result,
}: DashboardConfigCompletenessCardProps) {
  const { t } = useI18n();

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
              <CardTitle className="text-base">{t("dashboard.completeness.title")}</CardTitle>
              <CardDescription className={cn(pageCaptionClass, "sm:text-sm")}>
                {t("dashboard.completeness.descEmpty")}
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <p className={pageCaptionClass}>{t("dashboard.completeness.emptyBody")}</p>
        </CardContent>
      </Card>
    );
  }

  const { pct, done, total, sections } = result;
  const indicatorClass = progressToneClass(pct);

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
            <CardTitle className="text-base">{t("dashboard.completeness.title")}</CardTitle>
            <CardDescription className={cn(pageCaptionClass, "sm:text-sm")}>
              {t("dashboard.completeness.descHasData")}
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-end justify-between gap-2">
          <span className="text-2xl font-semibold tabular-nums text-foreground">{pct}%</span>
          <span className="pb-0.5 text-xs text-muted-foreground">
            {interpolate(t("dashboard.completeness.sectionsDone"), {
              done: String(done),
              total: String(total),
            })}
          </span>
        </div>
        <Progress value={pct} className="h-2" indicatorClassName={indicatorClass} />
        <p className={pageCaptionClass}>{t(completenessHintKey(pct))}</p>
        <ul
          className="grid gap-1.5 text-[11px] leading-snug text-muted-foreground sm:grid-cols-2"
          aria-label={t("dashboard.completeness.sectionsAria")}
        >
          {sections.map((s) => {
            const sk = `dashboard.completeness.section.${s.id}`;
            const tr = t(sk);
            const label = tr === sk ? s.label : tr;
            return (
              <li key={s.id} className="flex items-center gap-2">
                <span
                  className={cn(
                    "size-1.5 shrink-0 rounded-full",
                    s.ok ? "bg-emerald-500" : "bg-muted-foreground/35",
                  )}
                  aria-hidden
                />
                <span className={cn(s.ok ? "text-foreground/90" : "text-muted-foreground")}>{label}</span>
              </li>
            );
          })}
        </ul>
      </CardContent>
    </Card>
  );
});
