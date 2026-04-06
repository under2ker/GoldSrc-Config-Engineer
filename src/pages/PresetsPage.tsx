import { useEffect, useMemo, useState } from "react";
import { Search, Sparkles } from "lucide-react";
import { toast } from "sonner";
import { generateConfig } from "@/lib/api";
import { saveCfgToDisk } from "@/lib/cfgFiles";
import { addRecentConfig } from "@/lib/recentConfigs";
import { useCatalogStore } from "@/stores/catalogStore";
import { useConfigStore } from "@/stores/configStore";
import type { ProPresetSummary } from "@/types/api";
import { CatalogAvatar } from "@/components/common/CatalogAvatar";
import { CatalogItemCard } from "@/components/common/CatalogItemCard";
import { CfgTextPreview } from "@/components/common/CfgTextPreview";
import { EmptyState } from "@/components/common/EmptyState";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import {
  CATALOG_GRID,
  pageCaptionClass,
  pageLeadClass,
  pageSectionGroupTitleClass,
  pageShellClass,
} from "@/lib/layoutTokens";

function groupPresetsByTeam(list: ProPresetSummary[]): [string, ProPresetSummary[]][] {
  const m = new Map<string, ProPresetSummary[]>();
  for (const p of list) {
    const team = p.team.trim() || "Другое";
    m.set(team, [...(m.get(team) ?? []), p]);
  }
  return Array.from(m.entries()).sort(([a], [b]) => a.localeCompare(b, "ru"));
}

export function PresetsPage() {
  const presets = useCatalogStore((s) => s.presets);
  const loaded = useCatalogStore((s) => s.loaded);
  const error = useCatalogStore((s) => s.error);
  const [generatingId, setGeneratingId] = useState<string | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [rawCfg, setRawCfg] = useState<string | null>(null);
  const [genError, setGenError] = useState<string | null>(null);
  const [saveNote, setSaveNote] = useState<string | null>(null);
  const [defaultSaveName, setDefaultSaveName] = useState("pro_preset.cfg");
  const [savePresetLabel, setSavePresetLabel] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [sortOrder, setSortOrder] = useState<"catalog" | "name">("catalog");

  const filteredPresets = useMemo(() => {
    const q = query.trim().toLowerCase();
    let list = !q
      ? presets
      : presets.filter(
          (p) =>
            p.id.toLowerCase().includes(q) ||
            p.name.toLowerCase().includes(q) ||
            p.team.toLowerCase().includes(q) ||
            p.role.toLowerCase().includes(q),
        );
    if (sortOrder === "name") {
      list = [...list].sort((a, b) => a.name.localeCompare(b.name, "ru"));
    }
    return list;
  }, [presets, query, sortOrder]);

  const grouped = useMemo(() => groupPresetsByTeam(filteredPresets), [filteredPresets]);

  useEffect(() => {
    void useCatalogStore.getState().load();
  }, []);

  async function onGenerate(presetId: string) {
    setGenError(null);
    setSaveNote(null);
    setGeneratingId(presetId);
    try {
      const ao = useConfigStore.getState();
      const r = await generateConfig("preset", presetId, {
        aliasPreset: ao.aliasPreset,
        includePractice: ao.includePractice,
        aliasEnabled: ao.aliasPreset === "custom" ? ao.aliasEnabled : null,
      });
      setRawCfg(r.content);
      setDefaultSaveName(`preset-${presetId}.cfg`);
      setSavePresetLabel(presets.find((p) => p.id === presetId)?.name ?? presetId);
      setPreview(`// ${r.label}\n${r.content}`);
      toast.success("Конфиг сгенерирован", { description: r.label });
    } catch (e: unknown) {
      setRawCfg(null);
      setPreview(null);
      const msg = String(e);
      setGenError(msg);
      toast.error("Ошибка генерации", { description: msg });
    } finally {
      setGeneratingId(null);
    }
  }

  return (
    <div className={pageShellClass}>
      <p className={pageLeadClass}>
        Про-пресеты из каталога: сгруппированы по команде, единая сетка с экраном «Режимы». Быстрый переход:{" "}
        <kbd className="rounded border bg-muted px-1.5 py-0.5 font-mono text-xs">Ctrl+Shift+B</kbd> /{" "}
        <kbd className="rounded border bg-muted px-1.5 py-0.5 font-mono text-xs">⌘⇧B</kbd> (все клавиши — F1).
      </p>

      {error ? (
        <p className="text-sm text-destructive">{error}</p>
      ) : null}
      {genError ? <p className="text-sm text-destructive">{genError}</p> : null}

      {loaded && presets.length > 0 ? (
        <div className="flex max-w-2xl flex-col gap-3 sm:flex-row sm:items-end">
          <div className="relative min-w-0 flex-1">
            <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Поиск по нику, команде, роли…"
              className="pl-9"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              aria-label="Фильтр пресетов"
            />
          </div>
          <div className="w-full space-y-1.5 sm:w-56">
            <span className={pageCaptionClass}>Порядок</span>
            <Select value={sortOrder} onValueChange={(v) => setSortOrder(v as "catalog" | "name")}>
              <SelectTrigger aria-label="Порядок списка пресетов">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="catalog">Как в списке</SelectItem>
                <SelectItem value="name">По нику (А‑Я)</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      ) : null}

      {!loaded ? (
        <div className={CATALOG_GRID}>
          {Array.from({ length: 6 }).map((_, i) => (
            <Card key={i}>
              <CardHeader className="space-y-2">
                <Skeleton className="h-5 w-2/3" />
                <Skeleton className="h-4 w-full" />
              </CardHeader>
              <div className="border-t p-4">
                <Skeleton className="h-9 w-full" />
              </div>
            </Card>
          ))}
        </div>
      ) : presets.length === 0 ? (
        <EmptyState
          icon={Sparkles}
          title="Нет про-пресетов"
          description="Список пресетов пуст или не загрузился. Откройте «Диагностика» или перезапустите программу."
        />
      ) : grouped.length === 0 ? (
        <p className="text-sm text-muted-foreground">Ничего не найдено — сбросьте фильтр.</p>
      ) : (
        <div className="space-y-8">
          {grouped.map(([team, list]) => (
            <section key={team} className="space-y-4">
              <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-border/70 pb-2">
                <h2 className={pageSectionGroupTitleClass}>
                  {team}
                </h2>
                <span className="text-xs tabular-nums text-muted-foreground">{list.length}</span>
              </div>
              <div className={CATALOG_GRID}>
                {list.map((p) => (
                  <CatalogItemCard
                    key={p.id}
                    title={p.name}
                    codeBadge={p.id}
                    avatar={<CatalogAvatar title={p.name} />}
                    description={<span className="font-sans text-muted-foreground">{p.role}</span>}
                    footer={
                      <Button
                        type="button"
                        variant="success"
                        className="w-full"
                        disabled={generatingId !== null}
                        loading={generatingId === p.id}
                        onClick={() => void onGenerate(p.id)}
                      >
                        Сгенерировать .cfg
                      </Button>
                    }
                  />
                ))}
              </div>
            </section>
          ))}
        </div>
      )}

      {saveNote ? (
        <p className="text-sm text-muted-foreground">{saveNote}</p>
      ) : null}

      {preview ? (
        <Card>
          <CardHeader className="flex flex-row flex-wrap items-center justify-between gap-2 space-y-0">
            <CardTitle className="text-base font-semibold">Превью</CardTitle>
            <Button
              type="button"
              variant="outline"
              size="sm"
              disabled={!rawCfg}
              onClick={() => {
                if (!rawCfg) return;
                setSaveNote(null);
                void saveCfgToDisk(rawCfg, defaultSaveName).then((path) => {
                  if (path) {
                    addRecentConfig({
                      path,
                      modeLabel: savePresetLabel ? `Пресеты · ${savePresetLabel}` : "Пресеты",
                    });
                    setSaveNote(`Сохранено: ${path}`);
                    toast.success("Файл сохранён", { description: path });
                  } else {
                    setSaveNote("Сохранение отменено.");
                    toast.message("Сохранение отменено");
                  }
                });
              }}
            >
              Сохранить как…
            </Button>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-64 rounded-md border border-border bg-muted/10">
              <CfgTextPreview
                text={preview}
                className="p-3"
                fontSizePx={14}
                showLineNumbers
              />
            </ScrollArea>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
