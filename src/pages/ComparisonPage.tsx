import type { Change } from "diff";
import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import {
  Bar,
  BarChart,
  CartesianGrid,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { ArrowLeftRight, Copy, Download } from "lucide-react";
import { openCfgFile } from "@/lib/cfgFiles";
import { diffLinesLazy } from "@/lib/diffLazy";
import { ComparisonDiffTable } from "@/components/compare/ComparisonDiffTable";
import { DiffPartsVirtual, diffNeedsVirtualization } from "@/components/common/DiffPartsVirtual";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { pageCaptionClass, pageLeadClass, pageShellClass } from "@/lib/layoutTokens";
import { cn } from "@/lib/utils";

function buildDiffPlainText(parts: Change[]): string {
  const lines: string[] = [];
  for (const p of parts) {
    const raw = p.value.split("\n");
    for (let i = 0; i < raw.length; i++) {
      const line = raw[i];
      const isLastEmpty = i === raw.length - 1 && line === "";
      if (isLastEmpty) {
        continue;
      }
      if (p.added) {
        lines.push(`+${line}`);
      } else if (p.removed) {
        lines.push(`-${line}`);
      } else {
        lines.push(` ${line}`);
      }
    }
  }
  return lines.join("\n");
}

function downloadTextFile(filename: string, content: string): void {
  const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export function ComparisonPage() {
  const [labelA, setLabelA] = useState<string | null>(null);
  const [labelB, setLabelB] = useState<string | null>(null);
  const [textA, setTextA] = useState("");
  const [textB, setTextB] = useState("");
  const [busy, setBusy] = useState<"a" | "b" | null>(null);
  const [parts, setParts] = useState<Change[]>([]);
  const [diffLoading, setDiffLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setDiffLoading(true);
    void diffLinesLazy(textA, textB).then((p) => {
      if (!cancelled) {
        setParts(p);
        setDiffLoading(false);
      }
    });
    return () => {
      cancelled = true;
    };
  }, [textA, textB]);

  const diffBarData = useMemo(() => {
    let added = 0;
    let removed = 0;
    for (const p of parts) {
      const lines = p.value.split("\n").filter((line) => line.trim().length > 0).length;
      if (p.added) {
        added += lines;
      } else if (p.removed) {
        removed += lines;
      }
    }
    return [
      { label: "Добавлено (B)", count: added },
      { label: "Удалено (A)", count: removed },
    ];
  }, [parts]);

  const diffRadarData = useMemo(() => {
    let equal = 0;
    let added = 0;
    let removed = 0;
    for (const p of parts) {
      const lines = p.value.split("\n").filter((line) => line.trim().length > 0).length;
      if (p.added) {
        added += lines;
      } else if (p.removed) {
        removed += lines;
      } else {
        equal += lines;
      }
    }
    return [
      { metric: "Без изменений", value: equal },
      { metric: "Добавлено (B)", value: added },
      { metric: "Удалено (A)", value: removed },
    ];
  }, [parts]);

  const radarMax = useMemo(
    () => Math.max(1, ...diffRadarData.map((d) => d.value)),
    [diffRadarData],
  );

  async function pick(side: "a" | "b") {
    setBusy(side);
    try {
      const picked = await openCfgFile();
      if (!picked) {
        toast.message("Файл не выбран");
        return;
      }
      if (side === "a") {
        setLabelA(picked.path);
        setTextA(picked.text);
      } else {
        setLabelB(picked.path);
        setTextB(picked.text);
      }
      toast.success(side === "a" ? "Файл A" : "Файл B", { description: picked.path });
    } finally {
      setBusy(null);
    }
  }

  function swapSides() {
    if (!textA && !textB) {
      return;
    }
    const tA = textA;
    const tB = textB;
    const lA = labelA;
    const lB = labelB;
    setTextA(tB);
    setTextB(tA);
    setLabelA(lB);
    setLabelB(lA);
    toast.message("Стороны A и B поменяны местами");
  }

  return (
    <div className={pageShellClass}>
      <p className={pageLeadClass}>
        Построчное сравнение двух конфигов. Зелёный — появился в файле B. Красный — был в файле A. Совпадения без
        подсветки. Быстрый переход к этому разделу:{" "}
        <kbd className="rounded border bg-muted px-1.5 py-0.5 font-mono text-xs">Ctrl+Shift+G</kbd> /{" "}
        <kbd className="rounded border bg-muted px-1.5 py-0.5 font-mono text-xs">⌘⇧G</kbd> (полный список — F1).
      </p>

      <div className="flex flex-wrap gap-2">
        <Button type="button" loading={busy === "a"} onClick={() => void pick("a")}>
          Открыть файл A…
        </Button>
        <Button type="button" variant="secondary" loading={busy === "b"} onClick={() => void pick("b")}>
          Открыть файл B…
        </Button>
        <Button
          type="button"
          variant="outline"
          disabled={!textA && !textB}
          onClick={swapSides}
        >
          <ArrowLeftRight className="size-4" />
          Поменять A ↔ B
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader className="py-3">
            <CardTitle className="text-base">A</CardTitle>
            <CardDescription className="truncate font-mono text-xs">{labelA ?? "не выбран"}</CardDescription>
          </CardHeader>
          <CardContent className={pageCaptionClass}>
            {textA ? `${textA.split("\n").length} строк` : "—"}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="py-3">
            <CardTitle className="text-base">B</CardTitle>
            <CardDescription className="truncate font-mono text-xs">{labelB ?? "не выбран"}</CardDescription>
          </CardHeader>
          <CardContent className={pageCaptionClass}>
            {textB ? `${textB.split("\n").length} строк` : "—"}
          </CardContent>
        </Card>
      </div>

      {textA || textB ? (
        <div className="grid gap-4 lg:grid-cols-2">
          <Card>
            <CardHeader className="py-3">
              <CardTitle className="text-base">Столбцы</CardTitle>
              <CardDescription>Непустые строки в добавленных и удалённых фрагментах.</CardDescription>
            </CardHeader>
            <CardContent className="h-52">
              {diffLoading ? (
                <p className="text-sm text-muted-foreground">Загрузка…</p>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={diffBarData}
                    margin={{ left: 0, right: 8, top: 8, bottom: 4 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                    <XAxis dataKey="label" tick={{ fontSize: 10 }} interval={0} />
                    <YAxis allowDecimals={false} tick={{ fontSize: 10 }} width={28} />
                    <Tooltip
                      contentStyle={{
                        background: "var(--popover)",
                        border: "1px solid var(--border)",
                        borderRadius: "6px",
                        fontSize: "12px",
                      }}
                    />
                    <Bar dataKey="count" fill="var(--primary)" radius={[4, 4, 0, 0]} maxBarSize={56} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="py-3">
              <CardTitle className="text-base">Радар (распределение)</CardTitle>
              <CardDescription>
                Те же строки: общие, только в B, только в A — на одной диаграмме (ТЗ radar в дополнение к bar).
              </CardDescription>
            </CardHeader>
            <CardContent className="h-52">
              {diffLoading ? (
                <p className="text-sm text-muted-foreground">Загрузка…</p>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart
                    data={diffRadarData}
                    cx="50%"
                    cy="50%"
                    outerRadius="78%"
                  >
                    <PolarGrid stroke="var(--border)" />
                    <PolarAngleAxis dataKey="metric" tick={{ fontSize: 9, fill: "var(--muted-foreground)" }} />
                    <PolarRadiusAxis
                      angle={45}
                      domain={[0, radarMax]}
                      tick={{ fontSize: 9, fill: "var(--muted-foreground)" }}
                    />
                    <Tooltip
                      contentStyle={{
                        background: "var(--popover)",
                        border: "1px solid var(--border)",
                        borderRadius: "6px",
                        fontSize: "12px",
                      }}
                    />
                    <Radar
                      name="Строк"
                      dataKey="value"
                      stroke="var(--chart-2)"
                      fill="var(--chart-2)"
                      fillOpacity={0.35}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>
        </div>
      ) : null}

      <Card>
        <CardHeader className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <CardTitle>Отличия</CardTitle>
            <CardDescription>
              {diffLoading ? "Считаем…" : `${parts.length} фрагмент(ов)`}
            </CardDescription>
          </div>
          {!diffLoading && parts.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="gap-1.5"
                onClick={() => {
                  const t = buildDiffPlainText(parts);
                  void navigator.clipboard.writeText(t).then(
                    () => toast.success("Текст отличий скопирован"),
                    () => toast.error("Не удалось скопировать"),
                  );
                }}
              >
                <Copy className="size-3.5" />
                Копировать текст
              </Button>
              <Button
                type="button"
                variant="secondary"
                size="sm"
                className="gap-1.5"
                onClick={() => {
                  const t = buildDiffPlainText(parts);
                  downloadTextFile("compare-cfg-diff.txt", t);
                  toast.message("Файл сохранён", { description: "compare-cfg-diff.txt" });
                }}
              >
                <Download className="size-3.5" />
                Сохранить .txt
              </Button>
            </div>
          ) : null}
        </CardHeader>
        <CardContent>
          {diffLoading ? (
            <div className="flex h-[min(28rem,50vh)] items-center justify-center rounded-md border bg-muted/15">
              <p className="text-sm text-muted-foreground">Загрузка…</p>
            </div>
          ) : parts.length === 0 ? (
            <div className="flex h-[min(28rem,50vh)] items-center justify-center rounded-md border bg-muted/15">
              <p className="text-sm text-muted-foreground">Нет данных для сравнения или файлы совпадают.</p>
            </div>
          ) : (
            <Tabs defaultValue="blocks" className="w-full">
              <TabsList className="mb-3 w-full justify-start sm:w-auto">
                <TabsTrigger value="blocks">Блоки</TabsTrigger>
                <TabsTrigger value="table">Таблица</TabsTrigger>
              </TabsList>
              <TabsContent value="blocks" className="mt-0">
                {diffNeedsVirtualization(parts) ? (
                  <DiffPartsVirtual parts={parts} />
                ) : (
                  <ScrollArea className="h-[min(28rem,50vh)] rounded-md border bg-muted/15">
                    <div className="p-3 font-mono text-xs leading-relaxed">
                      {parts.map((part, i) => (
                        <pre
                          key={i}
                          className={cn(
                            "mb-1 overflow-x-auto whitespace-pre-wrap break-words rounded px-2 py-1",
                            part.added && "bg-emerald-500/15 text-emerald-900 dark:text-emerald-100",
                            part.removed && "bg-red-500/15 text-red-900 dark:text-red-100",
                            !part.added && !part.removed && "text-foreground/85",
                          )}
                        >
                          {part.value}
                        </pre>
                      ))}
                    </div>
                  </ScrollArea>
                )}
              </TabsContent>
              <TabsContent value="table" className="mt-0">
                <ComparisonDiffTable parts={parts} />
              </TabsContent>
            </Tabs>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
