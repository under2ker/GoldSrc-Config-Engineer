import { useEffect, useMemo, useState } from "react";
import { LayoutGrid, Search } from "lucide-react";
import { toast } from "sonner";
import { generateConfig } from "@/lib/api";
import { saveCfgToDisk } from "@/lib/cfgFiles";
import { addRecentConfig } from "@/lib/recentConfigs";
import { useCatalogStore } from "@/stores/catalogStore";
import { useConfigStore } from "@/stores/configStore";
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
import { CATALOG_GRID, pageCaptionClass, pageLeadClass, pageShellClass } from "@/lib/layoutTokens";

export function GameModesPage() {
  const modes = useCatalogStore((s) => s.modes);
  const loaded = useCatalogStore((s) => s.loaded);
  const error = useCatalogStore((s) => s.error);
  const [generatingId, setGeneratingId] = useState<string | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [rawCfg, setRawCfg] = useState<string | null>(null);
  const [genError, setGenError] = useState<string | null>(null);
  const [saveNote, setSaveNote] = useState<string | null>(null);
  const [defaultSaveName, setDefaultSaveName] = useState("autoexec.cfg");
  const [saveModeLabel, setSaveModeLabel] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [sortOrder, setSortOrder] = useState<"catalog" | "name">("catalog");

  const filteredModes = useMemo(() => {
    const q = query.trim().toLowerCase();
    let list = !q
      ? modes
      : modes.filter(
          (m) =>
            m.id.toLowerCase().includes(q) ||
            m.name_ru.toLowerCase().includes(q) ||
            m.name_en.toLowerCase().includes(q),
        );
    if (sortOrder === "name") {
      list = [...list].sort((a, b) => a.name_ru.localeCompare(b.name_ru, "ru"));
    }
    return list;
  }, [modes, query, sortOrder]);

  useEffect(() => {
    void useCatalogStore.getState().load();
  }, []);

  async function onGenerate(modeId: string) {
    setGenError(null);
    setSaveNote(null);
    setGeneratingId(modeId);
    try {
      const ao = useConfigStore.getState();
      const r = await generateConfig("mode", modeId, {
        aliasPreset: ao.aliasPreset,
        includePractice: ao.includePractice,
        aliasEnabled: ao.aliasPreset === "custom" ? ao.aliasEnabled : null,
      });
      setRawCfg(r.content);
      setDefaultSaveName(`mode-${modeId}.cfg`);
      setSaveModeLabel(modes.find((m) => m.id === modeId)?.name_ru ?? modeId);
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
        Выберите режим и сгенерируйте готовый фрагмент конфига для CS 1.6.
      </p>

      {error ? (
        <p className="text-sm text-destructive">{error}</p>
      ) : null}
      {genError ? <p className="text-sm text-destructive">{genError}</p> : null}

      {loaded && modes.length > 0 ? (
        <div className="flex max-w-2xl flex-col gap-3 sm:flex-row sm:items-end">
          <div className="relative min-w-0 flex-1">
            <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Поиск по названию или id…"
              className="pl-9"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              aria-label="Фильтр режимов"
            />
          </div>
          <div className="w-full space-y-1.5 sm:w-56">
            <span className={pageCaptionClass}>Порядок</span>
            <Select value={sortOrder} onValueChange={(v) => setSortOrder(v as "catalog" | "name")}>
              <SelectTrigger aria-label="Порядок списка режимов">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="catalog">Как в списке</SelectItem>
                <SelectItem value="name">По названию (А‑Я)</SelectItem>
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
                <Skeleton className="h-5 w-3/4" />
                <Skeleton className="h-4 w-full" />
              </CardHeader>
              <div className="border-t p-4">
                <Skeleton className="h-9 w-full" />
              </div>
            </Card>
          ))}
        </div>
      ) : modes.length === 0 ? (
        <EmptyState
          icon={LayoutGrid}
          title="Нет режимов"
          description="Список режимов пуст или не загрузился. Откройте «Диагностика» и перезапустите программу."
        />
      ) : filteredModes.length === 0 ? (
        <p className="text-sm text-muted-foreground">Ничего не найдено — сбросьте фильтр.</p>
      ) : (
        <div className={CATALOG_GRID}>
          {filteredModes.map((m) => (
            <CatalogItemCard
              key={m.id}
              title={m.name_ru}
              codeBadge={m.id}
              avatar={<CatalogAvatar title={m.name_ru} />}
              description={<span className="font-sans">{m.name_en}</span>}
              footer={
                <Button
                  type="button"
                  variant="success"
                  className="w-full"
                  disabled={generatingId !== null}
                  loading={generatingId === m.id}
                  onClick={() => void onGenerate(m.id)}
                >
                  Сгенерировать .cfg
                </Button>
              }
            />
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
                void saveCfgToDisk(rawCfg, defaultSaveName).then((p) => {
                  if (p) {
                    addRecentConfig({
                      path: p,
                      modeLabel: saveModeLabel ? `Режимы · ${saveModeLabel}` : "Режимы",
                    });
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
