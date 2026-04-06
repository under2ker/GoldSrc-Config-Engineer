import type { ReactNode } from "react";
import { CloudDownload, Loader2, RotateCcw } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { CatalogSyncReport } from "@/types/api";

type TFn = (key: string) => string;

export function CatalogSyncStats({ report, t }: { report: CatalogSyncReport; t: TFn }) {
  const errCount = report.errors.length;
  const cells = [
    { key: "checked", label: t("diagnosticsPage.catalog.statChecked"), value: report.checked },
    { key: "updated", label: t("diagnosticsPage.catalog.statUpdated"), value: report.updated },
    { key: "skipped", label: t("diagnosticsPage.catalog.statSkipped"), value: report.skippedNotModified },
    { key: "errors", label: t("diagnosticsPage.catalog.statErrors"), value: errCount },
  ];

  return (
    <div
      className={cn(
        "rounded-xl border border-border/70 bg-gradient-to-b from-muted/50 to-muted/20 p-4 shadow-sm",
        "dark:from-muted/30 dark:to-muted/10",
      )}
    >
      <p className="mb-3 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
        {t("diagnosticsPage.catalog.lastReportTitle")}
      </p>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4 sm:gap-3">
        {cells.map((c) => {
          const danger = c.key === "errors" && errCount > 0;
          return (
            <div
              key={c.key}
              className={cn(
                "rounded-lg border px-3 py-2.5 shadow-sm backdrop-blur-sm",
                danger
                  ? "border-destructive/35 bg-destructive/8 dark:bg-destructive/15"
                  : "border-border/60 bg-background/70 dark:bg-background/40",
              )}
            >
              <p className="text-[11px] leading-tight text-muted-foreground">{c.label}</p>
              <p
                className={cn(
                  "mt-0.5 text-xl font-semibold tabular-nums tracking-tight",
                  danger ? "text-destructive" : "text-foreground",
                )}
              >
                {c.value}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

type CatalogSyncSectionProps = {
  title: ReactNode;
  description: ReactNode;
  t: TFn;
  busy: "sync" | "reload" | null;
  lastReport: CatalogSyncReport | null;
  onSync: () => void;
  onReload: () => void;
  /** Показывать кнопки (например только в Tauri). */
  showActions: boolean;
  /** Текст под кнопками, если не Tauri и т.п. */
  footerNote?: ReactNode;
};

export function CatalogSyncSection({
  title,
  description,
  t,
  busy,
  lastReport,
  onSync,
  onReload,
  showActions,
  footerNote,
}: CatalogSyncSectionProps) {
  return (
    <Card className="overflow-hidden border-border/70 shadow-sm">
      <CardHeader className="space-y-0 border-b border-border/50 bg-muted/15 pb-4 pt-5 dark:bg-muted/10">
        <div className="flex gap-4">
          <div
            className={cn(
              "flex size-11 shrink-0 items-center justify-center rounded-2xl",
              "bg-primary/12 text-primary ring-1 ring-primary/15",
              "dark:bg-primary/15 dark:ring-primary/25",
            )}
            aria-hidden
          >
            <CloudDownload className="size-5" strokeWidth={2} />
          </div>
          <div className="min-w-0 flex-1 space-y-2">
            <CardTitle className="text-balance text-lg font-semibold leading-snug tracking-tight">{title}</CardTitle>
            <CardDescription className="text-pretty text-sm leading-relaxed">{description}</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4 pt-5">
        {showActions ? (
          <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-stretch">
            <Button
              type="button"
              className="w-full gap-2 sm:min-w-[200px] sm:flex-1 sm:max-w-xs"
              disabled={busy !== null}
              onClick={onSync}
            >
              {busy === "sync" ? (
                <>
                  <Loader2 className="size-4 shrink-0 animate-spin" />
                  {t("diagnosticsPage.catalog.syncing")}
                </>
              ) : (
                <>
                  <CloudDownload className="size-4 shrink-0" />
                  {t("diagnosticsPage.catalog.syncBtn")}
                </>
              )}
            </Button>
            <Button
              type="button"
              variant="outline"
              className="w-full gap-2 border-border/80 bg-background/50 sm:min-w-[180px] sm:w-auto sm:flex-initial"
              disabled={busy !== null}
              onClick={onReload}
            >
              {busy === "reload" ? (
                <>
                  <Loader2 className="size-4 shrink-0 animate-spin" />
                  {t("diagnosticsPage.catalog.syncing")}
                </>
              ) : (
                <>
                  <RotateCcw className="size-4 shrink-0" />
                  {t("diagnosticsPage.catalog.reloadBtn")}
                </>
              )}
            </Button>
          </div>
        ) : null}

        {footerNote ? <div className="text-sm text-muted-foreground">{footerNote}</div> : null}

        {lastReport ? <CatalogSyncStats report={lastReport} t={t} /> : null}
      </CardContent>
    </Card>
  );
}
