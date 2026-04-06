import { Wrench } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { interpolate, useI18n } from "@/lib/i18n";
import { pageLeadClass } from "@/lib/layoutTokens";
import { cn } from "@/lib/utils";

type DashboardHeroProps = {
  modeCount: number;
  presetCount: number;
  appVersion: string;
  loaded: boolean;
};

export function DashboardHero({
  modeCount,
  presetCount,
  appVersion,
  loaded,
}: DashboardHeroProps) {
  const { t } = useI18n();
  const ell = t("dashboard.ellipsis");
  return (
    <section
      className={cn(
        "relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950 p-6 shadow-lg sm:p-8",
        "dark:border-white/[0.06]",
      )}
    >
      <div
        className="pointer-events-none absolute -right-20 -top-24 size-[280px] rounded-full bg-indigo-500/15 blur-3xl sm:size-[400px]"
        aria-hidden
      />
      <div
        className="pointer-events-none absolute -bottom-24 -left-16 size-[240px] rounded-full bg-sky-500/10 blur-3xl"
        aria-hidden
      />

      <div className="relative z-[1] flex flex-col gap-5 sm:flex-row sm:items-start sm:gap-6">
        <div
          className="flex size-16 shrink-0 items-center justify-center rounded-2xl border border-white/10 bg-white/5 backdrop-blur-md sm:size-[72px]"
          aria-hidden
        >
          <Wrench className="size-9 text-primary sm:size-10" strokeWidth={1.75} />
        </div>
        <div className="min-w-0 flex-1 space-y-2">
          <h1 className="text-xl font-bold leading-snug tracking-tight text-slate-100 sm:text-2xl">
            {t("dashboard.hero.welcomePrefix")}{" "}
            <span className="bg-gradient-to-r from-blue-400 via-indigo-400 to-violet-400 bg-clip-text text-transparent">
              GoldSrc Config Engineer
            </span>
          </h1>
          <p className={cn(pageLeadClass, "max-w-xl text-slate-400 sm:text-[15px]")}>
            {t("dashboard.hero.lead")}
          </p>
        </div>
      </div>

      <div className="relative z-[1] mt-5 flex flex-wrap gap-2 sm:mt-6">
        <Badge
          variant="secondary"
          className="border border-indigo-500/25 bg-indigo-500/15 font-medium text-indigo-200 hover:bg-indigo-500/20"
        >
          {interpolate(t("dashboard.hero.modesBadge"), {
            val: loaded ? String(modeCount) : ell,
          })}
        </Badge>
        <Badge
          variant="secondary"
          className="border border-indigo-500/25 bg-indigo-500/15 font-medium text-indigo-200 hover:bg-indigo-500/20"
        >
          {interpolate(t("dashboard.hero.presetsBadge"), {
            val: loaded ? String(presetCount) : ell,
          })}
        </Badge>
        <Badge
          variant="secondary"
          className="border border-emerald-500/30 bg-emerald-500/15 font-medium text-emerald-200 hover:bg-emerald-500/20"
        >
          {interpolate(t("dashboard.hero.versionBadge"), { version: appVersion })}
        </Badge>
      </div>
    </section>
  );
}
