import { BarChart3, FileText, Zap } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
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
}: DashboardInsightCardsProps) {
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
              Быстрая генерация
            </p>
            <p className="truncate text-sm font-medium text-foreground" title={currentModeLabel}>
              {loaded ? currentModeLabel : "Загрузка списка режимов…"}
            </p>
            <p className={pageCaptionClass}>
              Режим ниже — кнопка «Сгенерировать .cfg»
            </p>
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
            <p className={pageSectionTitleClass}>
              Последний конфиг
            </p>
            {lastSaved ? (
              <>
                <p className="truncate text-sm font-medium text-foreground" title={lastSaved.path}>
                  {lastSaved.name}
                </p>
                <p className={cn(pageCaptionClass, "truncate")}>
                  {lastSaved.modeLabel}
                </p>
              </>
            ) : hasDraft ? (
              <>
                <p className="text-sm font-medium text-foreground">Черновик в памяти</p>
                <p className={cn(pageCaptionClass, "line-clamp-2")}>
                  {draftSummary ?? "Сохраните файл на диск, чтобы он попал в историю"}
                </p>
              </>
            ) : (
              <>
                <p className="text-sm text-muted-foreground">Пока нет сохранений</p>
                <p className={pageCaptionClass}>
                  Сгенерируйте и нажмите «Сохранить как…»
                </p>
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
            <p className={pageSectionTitleClass}>
              Статистика
            </p>
            {catalogError ? (
              <p className="text-sm text-destructive">Не удалось загрузить список</p>
            ) : (
              <p className="text-sm font-medium text-foreground">
                {loaded ? `${modeCount} режимов · ${presetCount} пресетов` : "…"}
              </p>
            )}
            <p className={pageCaptionClass}>Встроенные режимы и про-пресеты</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
