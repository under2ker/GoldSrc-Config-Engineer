import { BarChart3, FileText, Zap } from "lucide-react";
import { Link } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { interpolate, useI18n } from "@/lib/i18n";
import { pageCaptionClass, pageSectionTitleClass } from "@/lib/layoutTokens";
import { cn } from "@/lib/utils";
import type { RecentConfigEntry } from "@/lib/recentConfigs";

type DashboardInsightCardsProps = {
  currentModeLabel: string;
  modeCount: number;
  presetCount: number;
  loaded: boolean;
  catalogError: string | null;
  lastSaved: RecentConfigEntry | null;
  hasDraft: boolean;
  draftSummary?: string | null;
  /** Счётчики из SQLite (только настольная сборка). */
  sqliteStats?: { profileCount: number; historyCount: number | null } | null;
};

export function DashboardInsightCards({
  currentModeLabel,
  modeCount,
  presetCount,
  loaded,
  catalogError,
  lastSaved,
  hasDraft,
  draftSummary,
  sqliteStats,
}: DashboardInsightCardsProps) {
  const { t } = useI18n();
  const ell = t("dashboard.ellipsis");

  return (
    <div className="grid gap-6 md:grid-cols-3">
      <Card className="border-border/80 shadow-sm">
        <CardContent className="flex gap-4 p-5">
          <div
            className="flex size-11 shrink-0 items-center justify-center rounded-xl border border-amber-500/25 bg-amber-500/10 text-amber-600 dark:text-amber-400"
            aria-hidden
          >
            <Zap className="size-5" strokeWidth={1.75} />
          </div>
          <div className="min-w-0 space-y-1">
            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              {t("dashboard.insight.quickGen")}
            </p>
            <p className="truncate text-sm font-medium text-foreground" title={currentModeLabel}>
              {loaded ? currentModeLabel : t("dashboard.loadingModesList")}
            </p>
            <p className={pageCaptionClass}>{t("dashboard.insight.quickGenHint")}</p>
          </div>
        </CardContent>
      </Card>

      <Card className="border-border/80 shadow-sm">
        <CardContent className="flex gap-4 p-5">
          <div
            className="flex size-11 shrink-0 items-center justify-center rounded-xl border border-sky-500/25 bg-sky-500/10 text-sky-600 dark:text-sky-400"
            aria-hidden
          >
            <FileText className="size-5" strokeWidth={1.75} />
          </div>
          <div className="min-w-0 space-y-1">
            <p className={pageSectionTitleClass}>{t("dashboard.insight.lastConfig")}</p>
            {lastSaved ? (
              <>
                <p className="truncate text-sm font-medium text-foreground" title={lastSaved.path}>
                  {lastSaved.name}
                </p>
                <p className={cn(pageCaptionClass, "truncate")}>{lastSaved.modeLabel}</p>
              </>
            ) : hasDraft ? (
              <>
                <p className="text-sm font-medium text-foreground">{t("dashboard.insight.draftInMemory")}</p>
                <p className={cn(pageCaptionClass, "line-clamp-2")}>
                  {draftSummary ?? t("dashboard.insight.draftHintDefault")}
                </p>
              </>
            ) : (
              <>
                <p className="text-sm text-muted-foreground">{t("dashboard.insight.noSaves")}</p>
                <p className={pageCaptionClass}>{t("dashboard.insight.noSavesHint")}</p>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      <Card className="border-border/80 shadow-sm">
        <CardContent className="flex gap-4 p-5">
          <div
            className="flex size-11 shrink-0 items-center justify-center rounded-xl border border-violet-500/25 bg-violet-500/10 text-violet-600 dark:text-violet-400"
            aria-hidden
          >
            <BarChart3 className="size-5" strokeWidth={1.75} />
          </div>
          <div className="min-w-0 space-y-1">
            <p className={pageSectionTitleClass}>{t("dashboard.insight.stats")}</p>
            {catalogError ? (
              <p className="text-sm text-destructive">{t("dashboard.insight.statsLoadError")}</p>
            ) : (
              <p className="text-sm font-medium text-foreground">
                {loaded
                  ? interpolate(t("dashboard.insight.statsLine"), {
                      modes: String(modeCount),
                      presets: String(presetCount),
                    })
                  : ell}
              </p>
            )}
            <p className={pageCaptionClass}>{t("dashboard.insight.statsCaption")}</p>
            {sqliteStats ? (
              <div className="space-y-1 border-t border-border/60 pt-2">
                <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  {t("dashboard.insight.sqliteTitle")}
                </p>
                <p className="text-sm font-medium text-foreground tabular-nums">
                  {sqliteStats.historyCount === null
                    ? interpolate(t("dashboard.insight.sqliteLinePending"), {
                        profiles: String(sqliteStats.profileCount),
                      })
                    : interpolate(t("dashboard.insight.sqliteLine"), {
                        profiles: String(sqliteStats.profileCount),
                        snapshots: String(sqliteStats.historyCount),
                      })}
                </p>
                <Link
                  to="/profiles"
                  className="inline-block text-xs font-medium text-primary underline-offset-4 hover:underline"
                >
                  {t("dashboard.insight.sqliteLink")}
                </Link>
              </div>
            ) : null}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
