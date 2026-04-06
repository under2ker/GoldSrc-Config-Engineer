import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";
import { isTauri } from "@tauri-apps/api/core";
import { CheckCircle2, ClipboardList, Loader2, XCircle } from "lucide-react";
import {
  getAliasesCatalog,
  getAppPathsInfo,
  getGameModes,
  getProPresets,
  historyCount,
  ping,
} from "@/lib/api";
import { catalogReloadLocalWithUi, catalogSyncNowWithUi } from "@/lib/catalogSyncUi";
import {
  clearLogEntries,
  GCE_APP_LOG_EVENT,
  getLogEntries,
  isVerboseLogging,
  type AppLogEntry,
} from "@/lib/appLogger";
import { diffLinesLazy } from "@/lib/diffLazy";
import { loadRecentConfigs } from "@/lib/recentConfigs";
import { useCatalogStore } from "@/stores/catalogStore";
import { CatalogSyncSection } from "@/components/catalog/CatalogSyncSection";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import { pageLeadClass, pageShellNarrowClass } from "@/lib/layoutTokens";
import { useI18n } from "@/lib/i18n";
import { cn } from "@/lib/utils";
import type { CatalogSyncReport } from "@/types/api";

type CheckRow = {
  id: string;
  label: string;
  ok: boolean;
  detail: string;
};

function formatLogTime(t: number): string {
  try {
    return new Date(t).toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  } catch {
    return String(t);
  }
}

export function DiagnosticsPage() {
  const { t } = useI18n();
  const [rows, setRows] = useState<CheckRow[]>([]);
  const [running, setRunning] = useState(false);
  const [logLines, setLogLines] = useState<AppLogEntry[]>(() => getLogEntries());
  const [catalogBusy, setCatalogBusy] = useState<"sync" | "reload" | null>(null);
  const [lastCatalogReport, setLastCatalogReport] = useState<CatalogSyncReport | null>(null);

  const run = useCallback(async () => {
    setRunning(true);
    const next: CheckRow[] = [];

    try {
      const id = await ping();
      next.push({
        id: "ping",
        label: "Связь с генератором конфигов",
        ok: id.length > 0,
        detail: id || "нет ответа",
      });
    } catch (e) {
      next.push({
        id: "ping",
        label: "Связь с генератором конфигов",
        ok: false,
        detail: String(e),
      });
    }

    try {
      const modes = await getGameModes();
      next.push({
        id: "modes",
        label: "Список режимов",
        ok: modes.length > 0,
        detail: okDetail(modes.length, "режимов"),
      });
    } catch (e) {
      next.push({
        id: "modes",
        label: "Список режимов",
        ok: false,
        detail: String(e),
      });
    }

    try {
      const presets = await getProPresets();
      next.push({
        id: "presets",
        label: "Список про-пресетов",
        ok: presets.length > 0,
        detail: okDetail(presets.length, "пресетов"),
      });
    } catch (e) {
      next.push({
        id: "presets",
        label: "Список про-пресетов",
        ok: false,
        detail: String(e),
      });
    }

    if (isTauri()) {
      try {
        const catalog = await getAliasesCatalog();
        next.push({
          id: "aliases",
          label: "Каталог алиасов",
          ok: catalog.length > 0,
          detail: `${catalog.length} записей`,
        });
      } catch (e) {
        next.push({
          id: "aliases",
          label: "Каталог алиасов",
          ok: false,
          detail: String(e),
        });
      }

      try {
        const n = await historyCount();
        next.push({
          id: "history_db",
          label: "История снимков (база)",
          ok: true,
          detail: `${n} записей`,
        });
      } catch (e) {
        next.push({
          id: "history_db",
          label: "История снимков (база)",
          ok: false,
          detail: String(e),
        });
      }

      try {
        const paths = await getAppPathsInfo();
        next.push({
          id: "app_paths",
          label: "Пути данных приложения",
          ok: paths.sqlite_db_path.length > 0,
          detail: `SQLite: ${paths.sqlite_db_path}`,
        });
      } catch (e) {
        next.push({
          id: "app_paths",
          label: "Пути данных приложения",
          ok: false,
          detail: String(e),
        });
      }
    } else {
      next.push({
        id: "aliases",
        label: "Каталог алиасов",
        ok: true,
        detail: "полная проверка в программе для Windows / macOS / Linux",
      });
    }

    let storageOk = false;
    let storageDetail = "";
    try {
      const k = "__gce_diag__";
      localStorage.setItem(k, "1");
      storageOk = localStorage.getItem(k) === "1";
      localStorage.removeItem(k);
      storageDetail = storageOk ? "локальные настройки сохраняются" : "ошибка записи";
    } catch (e) {
      storageDetail = String(e);
    }
    next.push({
      id: "storage",
      label: "Локальное хранилище настроек",
      ok: storageOk,
      detail: storageDetail,
    });

    let recent = loadRecentConfigs();
    next.push({
      id: "recent",
      label: "История недавних .cfg",
      ok: true,
      detail:
        recent.length === 0
          ? "записей нет (появятся после сохранения или импорта)"
          : `${recent.length} записей в списке`,
    });

    try {
      const a = "bind w +forward\nalias x y\n";
      const b = "bind w +forward\nalias x z\n";
      const d = await diffLinesLazy(a, b);
      const diffOk = d.length > 0;
      next.push({
        id: "diff",
        label: "Сравнение конфигов (тест)",
        ok: diffOk,
        detail: diffOk ? `разбор тестового примера: ${d.length} частей` : "не сработало",
      });
    } catch (e) {
      next.push({
        id: "diff",
        label: "Сравнение конфигов (тест)",
        ok: false,
        detail: String(e),
      });
    }

    setRows(next);
    setRunning(false);
  }, []);

  useEffect(() => {
    void useCatalogStore.getState().load();
  }, []);

  useEffect(() => {
    void run();
  }, [run]);

  useEffect(() => {
    const sync = () => setLogLines(getLogEntries());
    sync();
    window.addEventListener(GCE_APP_LOG_EVENT, sync);
    return () => window.removeEventListener(GCE_APP_LOG_EVENT, sync);
  }, []);

  const passed = rows.filter((r) => r.ok).length;
  const total = rows.length;
  const score = total > 0 ? Math.round((passed / total) * 100) : 0;

  return (
    <div className={pageShellNarrowClass}>
      <p className={pageLeadClass}>
        Быстрая проверка окружения перед работой с конфигами. Оценка условная (по числу пройденных проверок).
      </p>

      <Card>
        <CardHeader className="flex flex-row flex-wrap items-center justify-between gap-4 space-y-0">
          <div>
            <CardTitle>Состояние</CardTitle>
            <CardDescription>
              Пройдено {passed} из {total || "…"} проверок
            </CardDescription>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              disabled={running || rows.length === 0}
              onClick={() => {
                const text = rows.map((r) => `${r.ok ? "OK" : "FAIL"}\t${r.label}\t${r.detail}`).join("\n");
                void navigator.clipboard.writeText(text).then(
                  () => {
                    toast.success("Сводка скопирована", { description: `${rows.length} строк` });
                  },
                  () => toast.error("Не удалось скопировать в буфер"),
                );
              }}
            >
              Копировать сводку
            </Button>
            <Button type="button" variant="secondary" size="sm" disabled={running} onClick={() => void run()}>
              {running ? (
                <>
                  <Loader2 className="size-4 animate-spin" />
                  Проверка…
                </>
              ) : (
                "Повторить"
              )}
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Оценка</span>
              <span className="font-medium">{score}/100</span>
            </div>
            <Progress value={score} />
          </div>
          <ul className="space-y-3">
            {rows.map((r) => (
              <li
                key={r.id}
                className={cn(
                  "flex gap-3 rounded-lg border p-3 text-sm",
                  r.ok ? "border-border bg-card" : "border-destructive/40 bg-destructive/5",
                )}
              >
                {r.ok ? (
                  <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-success" />
                ) : (
                  <XCircle className="mt-0.5 size-5 shrink-0 text-destructive" />
                )}
                <div className="min-w-0">
                  <p className="font-medium leading-tight">{r.label}</p>
                  <p className="mt-1 break-words text-muted-foreground">{r.detail}</p>
                </div>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <CatalogSyncSection
        title={t("diagnosticsPage.catalog.title")}
        description={t("diagnosticsPage.catalog.description")}
        t={t}
        busy={catalogBusy}
        lastReport={lastCatalogReport}
        showActions={isTauri()}
        footerNote={
          !isTauri() ? (
            <p className="text-sm text-muted-foreground">{t("diagnosticsPage.catalog.desktopOnly")}</p>
          ) : undefined
        }
        onSync={() => {
          void (async () => {
            setCatalogBusy("sync");
            try {
              const r = await catalogSyncNowWithUi(t);
              setLastCatalogReport(r);
            } catch (e) {
              toast.error(String(e));
            } finally {
              setCatalogBusy(null);
            }
          })();
        }}
        onReload={() => {
          void (async () => {
            setCatalogBusy("reload");
            try {
              await catalogReloadLocalWithUi(t);
            } catch (e) {
              toast.error(String(e));
            } finally {
              setCatalogBusy(null);
            }
          })();
        }}
      />

      <Card>
        <CardHeader className="flex flex-row flex-wrap items-center justify-between gap-4 space-y-0">
          <div>
            <CardTitle className="flex items-center gap-2">
              <ClipboardList className="size-5 opacity-80" aria-hidden />
              Журнал сессии
            </CardTitle>
            <CardDescription>
              Последние события ({logLines.length}). Verbose: {isVerboseLogging() ? "вкл." : "выкл."} — переключатель в
              «Настройки».
            </CardDescription>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => {
                const text = logLines
                  .map((e) => `[${formatLogTime(e.t)}] ${e.level}: ${e.message}`)
                  .join("\n");
                void navigator.clipboard.writeText(text).then(
                  () => toast.success("Журнал скопирован"),
                  () => toast.error("Не удалось скопировать"),
                );
              }}
            >
              Копировать всё
            </Button>
            <Button
              type="button"
              variant="secondary"
              size="sm"
              onClick={() => {
                clearLogEntries();
                setLogLines([]);
                toast.message("Журнал очищен");
              }}
            >
              Очистить буфер
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {logLines.length === 0 ? (
            <p className={pageLeadClass}>
              Записей пока нет — перейдите по разделам или включите подробный журнал в настройках.
            </p>
          ) : (
            <ScrollArea className="h-48 rounded-md border border-border bg-muted/10">
              <ul className="space-y-1 p-3 font-mono text-[11px] leading-relaxed">
                {logLines
                  .slice(-80)
                  .reverse()
                  .map((e, i) => (
                    <li
                      key={`${e.t}-${i}`}
                      className={cn(
                        "break-all",
                        e.level === "error" && "text-destructive",
                        e.level === "warn" && "text-amber-700 dark:text-amber-300",
                        e.level === "debug" && "text-muted-foreground",
                      )}
                    >
                      <span className="text-muted-foreground">{formatLogTime(e.t)}</span>{" "}
                      <span className="font-semibold">{e.level}</span> {e.message}
                    </li>
                  ))}
              </ul>
            </ScrollArea>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function okDetail(n: number, unit: string): string {
  if (n <= 0) return `загружено ${n} ${unit}`;
  return `загружено ${n} ${unit}`;
}
