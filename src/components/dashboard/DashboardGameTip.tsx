import { Lightbulb, Shuffle } from "lucide-react";
import { useCallback, useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import {
  DID_YOU_KNOW_TIPS,
  type DidYouKnowTip,
  pickDailyTip,
  pickRandomTip,
} from "@/lib/didYouKnowTips";
import { interpolate, useI18n } from "@/lib/i18n";
import { pageLeadClass } from "@/lib/layoutTokens";
import { cn } from "@/lib/utils";

export function DashboardGameTip({ className }: { className?: string }) {
  const { t } = useI18n();
  const initial = useMemo(() => pickDailyTip(), []);
  const [tip, setTip] = useState<DidYouKnowTip>(initial);

  const onShuffle = useCallback(() => {
    setTip((cur) => pickRandomTip(cur.id));
  }, []);

  const categoryLabel = t(`dashboard.tipCategory.${tip.category}`);

  return (
    <div
      className={cn(
        "flex flex-col gap-3 rounded-xl border border-amber-500/25 bg-amber-500/5 px-4 py-3 text-sm text-foreground/90 sm:flex-row sm:items-start sm:justify-between",
        className,
      )}
    >
      <div className="flex min-w-0 flex-1 gap-3">
        <Lightbulb className="mt-0.5 size-5 shrink-0 text-amber-600 dark:text-amber-400" aria-hidden />
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <p className="text-xs font-semibold uppercase tracking-wide text-amber-800/90 dark:text-amber-200/90">
              {t("dashboard.gameTip.title")}
            </p>
            <span className="rounded-md border border-amber-500/30 bg-amber-500/10 px-1.5 py-0.5 text-[10px] font-medium text-amber-900/90 dark:text-amber-100/90">
              {categoryLabel}
            </span>
            <span className="text-[10px] text-muted-foreground">
              {interpolate(t("dashboard.gameTip.tipsMeta"), { count: String(DID_YOU_KNOW_TIPS.length) })}
            </span>
          </div>
          <p className={cn(pageLeadClass, "mt-1")}>{tip.text}</p>
        </div>
      </div>
      <Button
        type="button"
        variant="outline"
        size="sm"
        className="shrink-0 border-amber-500/35 bg-background/60"
        onClick={onShuffle}
      >
        <Shuffle className="size-3.5" aria-hidden />
        {t("dashboard.gameTip.moreTip")}
      </Button>
    </div>
  );
}
