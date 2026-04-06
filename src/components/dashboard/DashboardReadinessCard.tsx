import { Gauge } from "lucide-react";
import { isTauri } from "@tauri-apps/api/core";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useI18n } from "@/lib/i18n";
import { pageCaptionClass } from "@/lib/layoutTokens";
import { cn } from "@/lib/utils";

export type DashboardReadinessInput = {
  loaded: boolean;
  modeCount: number;
  presetCount: number;
  recentCount: number;
  historySnapshotCount: number | null;
  profileCount: number;
  stagedProfileJson: string | null;
  /** Есть сырой .cfg после «Сгенерировать» на этой странице (сессия). */
  hasSessionGeneratedCfg: boolean;
};

/**
 * Оценка 0–100: четыре блока по 25 (ориентир visual set V-25).
 * 1) каталог режимов загружен;
 * 2) есть недавний сохранённый .cfg;
 * 3) настольная сборка: история или профили; браузер: черновик импорта или в каталоге есть пресеты;
 * 4) настольная сборка: и профили, и история; браузер — генерация на главной в этой сессии.
 */
export function computeReadinessScore(p: DashboardReadinessInput): number {
  let s = 0;
  if (p.loaded && p.modeCount > 0) {
    s += 25;
  }
  if (p.recentCount > 0) {
    s += 25;
  }
  if (isTauri()) {
    if ((p.historySnapshotCount ?? 0) > 0 || p.profileCount > 0) {
      s += 25;
    }
  } else if (
    (p.stagedProfileJson != null && p.stagedProfileJson.trim().length > 0) ||
    (p.loaded && p.presetCount > 0)
  ) {
    s += 25;
  }
  if (isTauri()) {
    if (p.profileCount > 0 && (p.historySnapshotCount ?? 0) > 0) {
      s += 25;
    }
  } else if (p.hasSessionGeneratedCfg) {
    s += 25;
  }
  return Math.min(100, s);
}

function readinessHintKey(score: number, isDesktop: boolean): string {
  if (score >= 100) {
    return "dashboard.readiness.hint100";
  }
  if (score >= 75) {
    return isDesktop ? "dashboard.readiness.hint75desktop" : "dashboard.readiness.hint75web";
  }
  if (score >= 50) {
    return "dashboard.readiness.hint50";
  }
  if (score >= 25) {
    return "dashboard.readiness.hint25";
  }
  return "dashboard.readiness.hint0";
}

type DashboardReadinessCardProps = DashboardReadinessInput;

export function DashboardReadinessCard(props: DashboardReadinessCardProps) {
  const { t } = useI18n();
  const score = computeReadinessScore(props);
  const desktop = isTauri();

  return (
    <Card className="border-border/80 shadow-sm">
      <CardHeader className="pb-2">
        <div className="flex items-start gap-3">
          <div
            className="flex size-10 shrink-0 items-center justify-center rounded-xl border border-emerald-500/25 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
            aria-hidden
          >
            <Gauge className="size-5" strokeWidth={1.75} />
          </div>
          <div className="min-w-0 space-y-1">
            <CardTitle className="text-base">{t("dashboard.readiness.title")}</CardTitle>
            <CardDescription className={cn(pageCaptionClass, "sm:text-sm")}>
              {desktop ? t("dashboard.readiness.descDesktop") : t("dashboard.readiness.descWeb")}
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-end justify-between gap-2">
          <span className="text-2xl font-semibold tabular-nums text-foreground">{score}</span>
          <span className="pb-0.5 text-xs text-muted-foreground">{t("dashboard.readiness.outOf100")}</span>
        </div>
        <Progress value={score} className="h-2" />
        <p className={pageCaptionClass}>{t(readinessHintKey(score, desktop))}</p>
      </CardContent>
    </Card>
  );
}
