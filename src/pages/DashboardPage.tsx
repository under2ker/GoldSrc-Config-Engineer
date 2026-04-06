import { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { isTauri } from "@tauri-apps/api/core";
import { toast } from "sonner";
import pkg from "../../package.json";
import { exportConfigSnapshot, generateConfig, historyAppend, historyCount } from "@/lib/api";
import { saveCfgToDisk } from "@/lib/cfgFiles";
import { readLastModeId, writeLastModeId } from "@/lib/lastGenerationMode";
import { computeConfigCompleteness, parseCfgTextForCompleteness } from "@/lib/configCompleteness";
import { loadRecentConfigs, addRecentConfig, type RecentConfigEntry } from "@/lib/recentConfigs";
import { GCE_RECENT_UPDATED } from "@/lib/uiEvents";
import { useCatalogStore } from "@/stores/catalogStore";
import { useConfigStore } from "@/stores/configStore";
import { useProfileStore } from "@/stores/profileStore";
import { CfgTextPreview } from "@/components/common/CfgTextPreview";
import { DashboardHero } from "@/components/dashboard/DashboardHero";
import { DashboardConfigCompletenessCard } from "@/components/dashboard/DashboardConfigCompletenessCard";
import { DashboardReadinessCard } from "@/components/dashboard/DashboardReadinessCard";
import { DashboardInsightCards } from "@/components/dashboard/DashboardInsightCards";
import { DashboardGameTip } from "@/components/dashboard/DashboardGameTip";
import { DashboardQuickActions } from "@/components/dashboard/DashboardQuickActions";
import { DashboardRecentConfigs } from "@/components/dashboard/DashboardRecentConfigs";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { pageCaptionClass, pageLeadClass, pageOverlineClass, pageShellClass } from "@/lib/layoutTokens";
import { cfgConfigParsedSchema } from "@/types/api";

export function DashboardPage() {
  const [generatedPreview, setGeneratedPreview] = useState<string | null>(null);
  const [lastRawCfg, setLastRawCfg] = useState<string | null>(null);
  const [lastGenLabel, setLastGenLabel] = useState<string | null>(null);
  const [genError, setGenError] = useState<string | null>(null);
  const [saveNote, setSaveNote] = useState<string | null>(null);
  const [genLoading, setGenLoading] = useState(false);
  const [modeId, setModeId] = useState("");
  const [recent, setRecent] = useState<RecentConfigEntry[]>(() => loadRecentConfigs());
  const [historySnapshotCount, setHistorySnapshotCount] = useState<number | null>(null);

  const modes = useCatalogStore((s) => s.modes);
  const presets = useCatalogStore((s) => s.presets);
  const loaded = useCatalogStore((s) => s.loaded);
  const error = useCatalogStore((s) => s.error);
  const profileCount = useProfileStore((s) => s.profiles.length);
  const stagedProfileJson = useConfigStore((s) => s.stagedProfileJson);

  const refreshRecent = useCallback(() => {
    setRecent(loadRecentConfigs());
  }, []);

  useEffect(() => {
    void useCatalogStore.getState().load();
  }, []);

  useEffect(() => {
    if (!isTauri()) return;
    void historyCount()
      .then((n) => setHistorySnapshotCount(n))
      .catch(() => setHistorySnapshotCount(null));
  }, []);

  useEffect(() => {
    if (!isTauri()) return;
    const onVis = () => {
      if (document.visibilityState !== "visible") return;
      void historyCount()
        .then((n) => setHistorySnapshotCount(n))
        .catch(() => setHistorySnapshotCount(null));
      void useProfileStore.getState().refreshProfiles();
    };
    document.addEventListener("visibilitychange", onVis);
    return () => document.removeEventListener("visibilitychange", onVis);
  }, []);

  useEffect(() => {
    if (!loaded || modes.length === 0) {
      return;
    }
    setModeId((cur) => {
      if (cur && modes.some((m) => m.id === cur)) {
        return cur;
      }
      const persisted = readLastModeId();
      if (persisted && modes.some((m) => m.id === persisted)) {
        return persisted;
      }
      return modes.find((m) => m.id === "classic")?.id ?? modes[0].id;
    });
  }, [loaded, modes]);

  useEffect(() => {
    const onVis = () => {
      if (document.visibilityState === "visible") {
        refreshRecent();
      }
    };
    const onRecentEvt = () => refreshRecent();
    document.addEventListener("visibilitychange", onVis);
    window.addEventListener(GCE_RECENT_UPDATED, onRecentEvt);
    return () => {
      document.removeEventListener("visibilitychange", onVis);
      window.removeEventListener(GCE_RECENT_UPDATED, onRecentEvt);
    };
  }, [refreshRecent]);

  const currentMode = modes.find((m) => m.id === modeId);
  const currentModeLabel = currentMode
    ? `${currentMode.name_ru} (${currentMode.name_en})`
    : loaded
      ? "—"
      : "Загрузка…";

  const scrollToGenerate = useCallback(() => {
    document.getElementById("dashboard-generate")?.scrollIntoView({ behavior: "smooth" });
  }, []);

  const configCompleteness = useMemo(() => {
    try {
      let merged: Parameters<typeof computeConfigCompleteness>[0] | null = null;

      if (stagedProfileJson?.trim()) {
        const raw = JSON.parse(stagedProfileJson) as unknown;
        const parsed = cfgConfigParsedSchema.safeParse(raw);
        if (parsed.success) {
          merged = parsed.data;
        }
      }

      if (!merged && lastRawCfg?.trim()) {
        const p = parseCfgTextForCompleteness(lastRawCfg);
        merged = {
          settings: p.settings,
          binds: p.binds,
          buy_binds: p.buy_binds,
          mode: null,
          mode_key: null,
          preset_name: null,
        };
      }

      if (!merged) {
        return null;
      }

      const hasPayload =
        Object.keys(merged.settings).length > 0 ||
        Object.keys(merged.binds).length > 0 ||
        !!(merged.mode?.trim() || merged.mode_key?.trim() || merged.preset_name?.trim());

      if (!hasPayload) {
        return null;
      }

      return computeConfigCompleteness(merged, {
        sessionHasMode: Boolean(lastRawCfg?.trim() && modeId),
      });
    } catch {
      return null;
    }
  }, [stagedProfileJson, lastRawCfg, modeId]);

  const handleGenerate = useCallback(() => {
    setGenError(null);
    setGenLoading(true);
    const ao = useConfigStore.getState();
    void generateConfig("mode", modeId, {
      aliasPreset: ao.aliasPreset,
      includePractice: ao.includePractice,
      aliasEnabled: ao.aliasPreset === "custom" ? ao.aliasEnabled : null,
    })
      .then(async (r) => {
        writeLastModeId(modeId);
        setLastRawCfg(r.content);
        setLastGenLabel(r.label);
        setGeneratedPreview(`// ${r.label}\n${r.content}`);
        setSaveNote(null);
        toast.success("Конфиг сгенерирован", { description: r.label });
        if (isTauri()) {
          try {
            const snapshot = await exportConfigSnapshot("mode", modeId, {
              aliasPreset: ao.aliasPreset,
              includePractice: ao.includePractice,
              aliasEnabled: ao.aliasPreset === "custom" ? ao.aliasEnabled : null,
            });
            await historyAppend(snapshot, null);
            const n = await historyCount();
            setHistorySnapshotCount(n);
          } catch {
            /* история опциональна */
          }
        }
      })
      .catch((e: unknown) => {
        setGeneratedPreview(null);
        setLastRawCfg(null);
        setLastGenLabel(null);
        const msg = String(e);
        setGenError(msg);
        toast.error("Ошибка генерации", { description: msg });
      })
      .finally(() => setGenLoading(false));
  }, [modeId]);

  return (
    <div className={pageShellClass}>
      <DashboardHero
        modeCount={modes.length}
        presetCount={presets.length}
        appVersion={pkg.version}
        loaded={loaded}
      />

      <DashboardReadinessCard
        loaded={loaded}
        modeCount={modes.length}
        presetCount={presets.length}
        recentCount={recent.length}
        historySnapshotCount={historySnapshotCount}
        profileCount={profileCount}
        stagedProfileJson={stagedProfileJson}
        hasSessionGeneratedCfg={!!lastRawCfg}
      />

      <DashboardConfigCompletenessCard result={configCompleteness} />

      <DashboardInsightCards
        currentModeLabel={currentModeLabel}
        modeCount={modes.length}
        presetCount={presets.length}
        loaded={loaded}
        catalogError={error}
        lastSaved={recent[0] ?? null}
        hasDraft={!!lastRawCfg}
        draftSummary={lastGenLabel ?? undefined}
      />

      <DashboardGameTip />

      {isTauri() ? (
        <div className="grid gap-3 sm:grid-cols-2">
          <Card className="border-border/80 bg-muted/10 shadow-sm">
            <CardContent className="flex flex-col gap-3 py-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-sm font-medium">Локальные профили</p>
                <p className={pageCaptionClass}>
                  Сохранённые наборы (импорт → «Сохранить как профиль»):{" "}
                  <span className="font-medium text-foreground">{profileCount}</span>
                </p>
              </div>
              <Button type="button" variant="secondary" size="sm" asChild>
                <Link to="/profiles">Открыть профили</Link>
              </Button>
            </CardContent>
          </Card>
          <Card className="border-border/80 bg-muted/10 shadow-sm">
            <CardContent className="flex flex-col gap-3 py-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-sm font-medium">История снимков</p>
                <p className={pageCaptionClass}>
                  Записей в локальной истории:{" "}
                  <span className="font-medium text-foreground">
                    {historySnapshotCount === null ? "…" : historySnapshotCount}
                  </span>
                </p>
              </div>
              <Button type="button" variant="secondary" size="sm" asChild>
                <Link to="/profiles">К списку и истории</Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      ) : null}

      <DashboardQuickActions onGoToGenerate={scrollToGenerate} />

      <Card id="dashboard-generate" className="scroll-mt-4 border-border/80 shadow-sm">
        <CardHeader className="pb-4">
          <CardTitle className="text-lg">Генерация по режиму</CardTitle>
          <CardDescription>
            Выберите режим и сохраните результат как <code className="text-xs">.cfg</code> для игры.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {error ? (
            <p className="text-sm text-destructive">Список режимов не загрузился: {error}</p>
          ) : null}

          <div className="flex flex-col gap-4 lg:flex-row lg:items-end">
            <div className="min-w-0 flex-1 space-y-2">
              <Label htmlFor="dash-mode" className={pageOverlineClass}>
                Режим генерации
              </Label>
              <Select
                value={modeId}
                onValueChange={(v) => {
                  setModeId(v);
                  writeLastModeId(v);
                }}
                disabled={!loaded || modes.length === 0}
              >
                <SelectTrigger id="dash-mode" className="w-full">
                  <SelectValue placeholder="Выберите режим" />
                </SelectTrigger>
                <SelectContent>
                  {modes.map((m) => (
                    <SelectItem key={m.id} value={m.id}>
                      {m.name_ru}{" "}
                      <span className="text-muted-foreground">({m.name_en})</span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button
                type="button"
                variant="success"
                disabled={!loaded || !modeId}
                loading={genLoading}
                onClick={handleGenerate}
                className="min-w-[11rem]"
              >
                Сгенерировать .cfg
              </Button>
              <Button
                type="button"
                variant="secondary"
                disabled={!lastRawCfg}
                onClick={() => {
                  if (!lastRawCfg) {
                    return;
                  }
                  setSaveNote(null);
                  const modeRu = currentMode?.name_ru ?? modeId;
                  void saveCfgToDisk(lastRawCfg, "autoexec.cfg").then((p) => {
                    if (p) {
                      addRecentConfig({ path: p, modeLabel: modeRu });
                      refreshRecent();
                      setSaveNote(`Сохранено: ${p}`);
                      toast.success("Файл сохранён", { description: p });
                    } else {
                      setSaveNote("Сохранение отменено.");
                      toast.message("Сохранение отменено");
                    }
                  });
                }}
              >
                Сохранить как…
              </Button>
              <Button type="button" variant="outline" asChild>
                <Link to="/import">Импорт .cfg…</Link>
              </Button>
            </div>
          </div>

          {saveNote ? (
            <p className={pageLeadClass}>{saveNote}</p>
          ) : null}
          {genError ? <p className="text-sm text-destructive">{genError}</p> : null}

          {generatedPreview ? (
            <ScrollArea className="h-52 rounded-md border md:h-56">
              <CfgTextPreview
                text={generatedPreview}
                className="p-3"
                fontSizePx={14}
                showLineNumbers
              />
            </ScrollArea>
          ) : null}
        </CardContent>
      </Card>

      <DashboardRecentConfigs items={recent} />
    </div>
  );
}
