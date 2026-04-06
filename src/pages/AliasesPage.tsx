import { useCallback, useDeferredValue, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "sonner";
import { Braces, ListFilter } from "lucide-react";
import rawAliases from "../../data/aliases.json";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Switch } from "@/components/ui/switch";
import { pageCaptionClass, pageLeadClass, pageSectionTitleClass, pageShellClass } from "@/lib/layoutTokens";
import { useConfigStore, type AliasPreset } from "@/stores/configStore";
import { cn } from "@/lib/utils";

const SECTION_LABEL: Record<string, string> = {
  movement: "Движение",
  weapon: "Оружие",
  communication: "Коммуникация",
  utility: "Утилиты",
  practice: "Практика (sv_cheats)",
  kz_specific: "KZ / climb",
  surf_specific: "Surf",
};

type FlatAlias = {
  key: string;
  section: string;
  sectionLabel: string;
  name: string;
  description: string;
  safety: string;
  required: boolean;
};

function flattenAliases(): FlatAlias[] {
  const db = rawAliases as Record<string, { aliases?: Array<Record<string, unknown>> }>;
  const out: FlatAlias[] = [];
  for (const [sec, data] of Object.entries(db)) {
    if (sec.startsWith("_") || !data?.aliases) continue;
    const sectionLabel = SECTION_LABEL[sec] ?? sec;
    for (const a of data.aliases) {
      const name = typeof a.name === "string" ? a.name : "";
      if (!name) continue;
      out.push({
        key: `${sec}:${name}`,
        section: sec,
        sectionLabel,
        name,
        description: typeof a.description === "string" ? a.description : "",
        safety: typeof a.safety === "string" ? a.safety : "SAFE",
        required: typeof a.required === "boolean" ? a.required : false,
      });
    }
  }
  return out;
}

export function AliasesPage() {
  const flat = useMemo(() => flattenAliases(), []);
  const aliasPreset = useConfigStore((s) => s.aliasPreset);
  const includePractice = useConfigStore((s) => s.includePractice);
  const aliasEnabled = useConfigStore((s) => s.aliasEnabled);
  const setAliasPreset = useConfigStore((s) => s.setAliasPreset);
  const setIncludePractice = useConfigStore((s) => s.setIncludePractice);
  const setAliasEnabled = useConfigStore((s) => s.setAliasEnabled);
  const bulkAliasEnabled = useConfigStore((s) => s.bulkAliasEnabled);

  const [filter, setFilter] = useState("");
  const deferredFilter = useDeferredValue(filter);

  const grouped = useMemo(() => {
    const map = new Map<string, FlatAlias[]>();
    for (const a of flat) {
      if (deferredFilter.trim()) {
        const q = deferredFilter.toLowerCase();
        const hay = `${a.sectionLabel} ${a.name} ${a.description} ${a.safety}`.toLowerCase();
        if (!hay.includes(q)) continue;
      }
      map.set(a.section, [...(map.get(a.section) ?? []), a]);
    }
    return map;
  }, [flat, deferredFilter]);

  const selectedCount = useMemo(() => Object.values(aliasEnabled).filter(Boolean).length, [aliasEnabled]);

  const applyRequired = useCallback(() => {
    const m: Record<string, boolean> = {};
    for (const a of flat) {
      if (a.required) m[a.key] = true;
    }
    bulkAliasEnabled(m);
    toast.message("Отмечены обязательные алиасы");
  }, [flat, bulkAliasEnabled]);

  const applyAll = useCallback(() => {
    const m: Record<string, boolean> = {};
    for (const a of flat) {
      m[a.key] = true;
    }
    bulkAliasEnabled(m);
    toast.message("Отмечены все алиасы из списка");
  }, [flat, bulkAliasEnabled]);

  const clearAll = useCallback(() => {
    bulkAliasEnabled({});
    toast.message("Сняты все отметки");
  }, [bulkAliasEnabled]);

  return (
    <div className={pageShellClass}>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className={pageLeadClass}>
            Набор из <span className="font-medium text-foreground">{flat.length}</span> скриптовых алиасов (как в
            GoldSrc 1.6). Они попадают в экспорт: один файл или модульный набор (
            <code className="text-xs">config/aliases.cfg</code> выполняется до биндов).
          </p>
          <p className="mt-2 text-sm">
            <Link to="/export" className="text-primary underline-offset-4 hover:underline">
              Экспорт
            </Link>
            {" · "}
            <Link to="/dashboard" className="text-primary underline-offset-4 hover:underline">
              Главная
            </Link>
          </p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Braces className="size-5 opacity-90" />
            Пресет алиасов
          </CardTitle>
          <CardDescription>
            «Минимум» — только обязательные; «Все» — весь каталог для текущего режима (KZ/Surf — доп. секции); «Свой
            набор» — чекбоксы ниже.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <RadioGroup
            value={aliasPreset}
            onValueChange={(v) => setAliasPreset(v as AliasPreset)}
            className="grid gap-3 sm:grid-cols-3"
          >
            <label
              className={cn(
                "flex cursor-pointer items-start gap-3 rounded-lg border p-3 transition-colors",
                aliasPreset === "minimal" ? "border-primary bg-primary/5" : "hover:bg-muted/40",
              )}
            >
              <RadioGroupItem value="minimal" id="ap-min" className="mt-1" />
              <div>
                <Label htmlFor="ap-min" className="cursor-pointer font-medium">
                  Минимум
                </Label>
                <p className={pageCaptionClass}>Только с флагом required в базе.</p>
              </div>
            </label>
            <label
              className={cn(
                "flex cursor-pointer items-start gap-3 rounded-lg border p-3 transition-colors",
                aliasPreset === "full" ? "border-primary bg-primary/5" : "hover:bg-muted/40",
              )}
            >
              <RadioGroupItem value="full" id="ap-full" className="mt-1" />
              <div>
                <Label htmlFor="ap-full" className="cursor-pointer font-medium">
                  Все
                </Label>
                <p className={pageCaptionClass}>Весь доступный каталог по режиму.</p>
              </div>
            </label>
            <label
              className={cn(
                "flex cursor-pointer items-start gap-3 rounded-lg border p-3 transition-colors",
                aliasPreset === "custom" ? "border-primary bg-primary/5" : "hover:bg-muted/40",
              )}
            >
              <RadioGroupItem value="custom" id="ap-cust" className="mt-1" />
              <div>
                <Label htmlFor="ap-cust" className="cursor-pointer font-medium">
                  Свой набор
                </Label>
                <p className={pageCaptionClass}>Выбор вручную ({selectedCount} вкл.).</p>
              </div>
            </label>
          </RadioGroup>

          <div className="flex flex-col gap-3 rounded-lg border bg-muted/20 p-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="space-y-1">
              <Label htmlFor="prac-sw">Секция практики (sv_cheats)</Label>
              <p className={pageCaptionClass}>
                Добавляет алиасы вроде <code className="text-[10px]">prac_on</code> — только локально / с разрешением
                сервера.
              </p>
            </div>
            <Switch id="prac-sw" checked={includePractice} onCheckedChange={setIncludePractice} />
          </div>
        </CardContent>
      </Card>

      {aliasPreset === "custom" ? (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <ListFilter className="size-4 opacity-80" />
              Выбор алиасов
            </CardTitle>
            <CardDescription>
              Отметьте команды для генерации. Ключ: <span className="font-mono text-xs">секция:имя</span>.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex flex-wrap gap-2">
              <Button type="button" size="sm" variant="secondary" onClick={applyRequired}>
                Только обязательные
              </Button>
              <Button type="button" size="sm" variant="secondary" onClick={applyAll}>
                Отметить все
              </Button>
              <Button type="button" size="sm" variant="outline" onClick={clearAll}>
                Снять все
              </Button>
            </div>
            <Label className={pageCaptionClass}>Фильтр по названию или описанию</Label>
            <input
              className="flex h-9 w-full max-w-md rounded-md border border-input bg-background px-3 text-sm shadow-sm"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              placeholder="Например: jump, netgraph, kz…"
            />
            <ScrollArea className="h-[min(28rem,55vh)] rounded-md border">
              <div className="space-y-6 p-3">
                {Array.from(grouped.entries()).map(([sec, items], idx, arr) => (
                  <div key={sec}>
                    <p className={cn(pageSectionTitleClass, "mb-2")}>
                      {SECTION_LABEL[sec] ?? sec}
                    </p>
                    <ul className="space-y-2">
                      {items.map((a) => (
                        <li
                          key={a.key}
                          className="flex items-start gap-3 rounded-md border border-transparent px-1 py-1 hover:bg-muted/30"
                        >
                          <input
                            id={a.key}
                            type="checkbox"
                            className="mt-1 size-4 shrink-0 rounded border border-input accent-primary"
                            checked={aliasEnabled[a.key] ?? false}
                            onChange={(e) => setAliasEnabled(a.key, e.target.checked)}
                          />
                          <label htmlFor={a.key} className="min-w-0 flex-1 cursor-pointer text-sm leading-snug">
                            <span className="font-mono text-xs text-foreground">{a.name}</span>{" "}
                            <Badge variant="outline" className="ml-1 align-middle text-[10px]">
                              {a.safety}
                            </Badge>
                            {a.required ? (
                              <Badge variant="secondary" className="ml-1 align-middle text-[10px]">
                                required
                              </Badge>
                            ) : null}
                            <span className={cn(pageCaptionClass, "mt-0.5 block")}>{a.description}</span>
                          </label>
                        </li>
                      ))}
                    </ul>
                    {idx < arr.length - 1 ? <Separator className="mt-4" /> : null}
                  </div>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      ) : (
        <Card className="border-dashed">
          <CardContent className="py-6 text-sm text-muted-foreground">
            Для пресетов «Минимум» и «Все» список не выводится — переключитесь на «Свой набор», чтобы отметить алиасы
            вручную.
          </CardContent>
        </Card>
      )}
    </div>
  );
}
