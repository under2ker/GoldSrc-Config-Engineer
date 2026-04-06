import type { Change } from "diff";
import { useMemo, useState } from "react";
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  type SortingState,
  useReactTable,
} from "@tanstack/react-table";
import { ArrowDown, ArrowUp, ArrowUpDown, Download } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { CfgLineCategory } from "@/lib/cfgLineCategory";
import { CFG_LINE_CATEGORY_LABEL, listCfgLineCategories } from "@/lib/cfgLineCategory";
import {
  type DiffTableRow,
  diffRowsToCsv,
  flattenDiffPartsToRows,
} from "@/lib/comparisonDiffRows";
import { cn } from "@/lib/utils";

const columnHelper = createColumnHelper<DiffTableRow>();

const KIND_LABEL: Record<DiffTableRow["kind"], string> = {
  added: "В B",
  removed: "Из A",
  unchanged: "Оба",
};

function KindBadge({ kind }: { kind: DiffTableRow["kind"] }) {
  return (
    <Badge
      variant="outline"
      className={cn(
        "font-normal",
        kind === "added" && "border-emerald-500/45 bg-emerald-500/10 text-emerald-900 dark:text-emerald-100",
        kind === "removed" && "border-red-500/45 bg-red-500/10 text-red-900 dark:text-red-100",
        kind === "unchanged" && "text-muted-foreground",
      )}
    >
      {KIND_LABEL[kind]}
    </Badge>
  );
}

type ComparisonDiffTableProps = {
  parts: Change[];
};

const PAGE_SIZES = [25, 50, 100, 200] as const;

export function ComparisonDiffTable({ parts }: ComparisonDiffTableProps) {
  const rawRows = useMemo(() => flattenDiffPartsToRows(parts), [parts]);
  const [sorting, setSorting] = useState<SortingState>([
    { id: "partIndex", desc: false },
    { id: "lineIndex", desc: false },
  ]);
  const [globalFilter, setGlobalFilter] = useState("");
  const [categoryFilter, setCategoryFilter] = useState<CfgLineCategory | "all">("all");

  const data = useMemo(() => {
    let rows = rawRows;
    if (categoryFilter !== "all") {
      rows = rows.filter((r) => r.category === categoryFilter);
    }
    const q = globalFilter.trim().toLowerCase();
    if (q) {
      rows = rows.filter((r) => r.text.toLowerCase().includes(q));
    }
    return rows;
  }, [rawRows, categoryFilter, globalFilter]);

  const columns = useMemo(
    () => [
      columnHelper.display({
        id: "idx",
        header: "#",
        enableSorting: false,
        cell: ({ row, table }) => {
          const page = table.getState().pagination.pageIndex;
          const size = table.getState().pagination.pageSize;
          return page * size + row.index + 1;
        },
      }),
      columnHelper.accessor("kind", {
        header: "Тип",
        cell: (info) => <KindBadge kind={info.getValue()} />,
      }),
      columnHelper.accessor("category", {
        header: "Категория",
        cell: (info) => (
          <span className="text-muted-foreground">{CFG_LINE_CATEGORY_LABEL[info.getValue()]}</span>
        ),
      }),
      columnHelper.accessor("text", {
        header: "Строка",
        cell: (info) => (
          <code className="block max-w-[min(48rem,70vw)] whitespace-pre-wrap break-all text-[11px] leading-snug text-foreground">
            {info.getValue() || " "}
          </code>
        ),
      }),
      columnHelper.accessor("partIndex", { header: "Фр." }),
      columnHelper.accessor("lineIndex", { header: "Стр." }),
    ],
    [],
  );

  const table = useReactTable({
    data,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: {
      pagination: { pageSize: 50, pageIndex: 0 },
    },
  });

  const exportCsv = () => {
    const rows = table.getSortedRowModel().rows.map((r) => r.original);
    const csv = diffRowsToCsv(rows);
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "compare-cfg-diff.csv";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-3">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <div className="flex min-w-0 flex-1 flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-end">
          <div className="min-w-[12rem] flex-1 space-y-1.5">
            <Label htmlFor="compare-filter-text">Поиск по тексту</Label>
            <Input
              id="compare-filter-text"
              value={globalFilter}
              onChange={(e) => {
                setGlobalFilter(e.target.value);
                table.setPageIndex(0);
              }}
              placeholder="Подстрока в строке…"
              className="h-9"
            />
          </div>
          <div className="w-full min-w-[12rem] space-y-1.5 sm:w-56">
            <Label htmlFor="compare-filter-cat">Категория CVAR</Label>
            <Select
              value={categoryFilter}
              onValueChange={(v) => {
                setCategoryFilter(v as CfgLineCategory | "all");
                table.setPageIndex(0);
              }}
            >
              <SelectTrigger id="compare-filter-cat" className="h-9">
                <SelectValue placeholder="Все" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Все категории</SelectItem>
                {listCfgLineCategories().map((c) => (
                  <SelectItem key={c} value={c}>
                    {CFG_LINE_CATEGORY_LABEL[c]}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
        <Button type="button" variant="secondary" size="sm" className="gap-1.5 shrink-0" onClick={exportCsv}>
          <Download className="size-3.5" />
          Экспорт CSV
        </Button>
      </div>

      <div className="rounded-md border border-border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((hg) => (
              <TableRow key={hg.id} className="hover:bg-transparent">
                {hg.headers.map((header) => {
                  const canSort = header.column.getCanSort();
                  const sorted = header.column.getIsSorted();
                  return (
                    <TableHead
                      key={header.id}
                      className={cn(canSort && "cursor-pointer select-none")}
                      onClick={canSort ? header.column.getToggleSortingHandler() : undefined}
                    >
                      <span className="inline-flex items-center gap-1">
                        {flexRender(header.column.columnDef.header, header.getContext())}
                        {canSort ? (
                          sorted === "asc" ? (
                            <ArrowUp className="size-3 opacity-70" />
                          ) : sorted === "desc" ? (
                            <ArrowDown className="size-3 opacity-70" />
                          ) : (
                            <ArrowUpDown className="size-3 opacity-40" />
                          )
                        ) : null}
                      </span>
                    </TableHead>
                  );
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows.length === 0 ? (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-24 text-center text-muted-foreground">
                  Нет строк по текущим фильтрам.
                </TableCell>
              </TableRow>
            ) : (
              table.getRowModel().rows.map((row) => (
                <TableRow key={row.id}>
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</TableCell>
                  ))}
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-xs text-muted-foreground">
          На странице {table.getRowModel().rows.length} · отфильтровано {data.length} из {rawRows.length} строк
        </p>
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground">На странице</span>
            <Select
              value={String(table.getState().pagination.pageSize)}
              onValueChange={(v) => {
                table.setPageSize(Number(v));
                table.setPageIndex(0);
              }}
            >
              <SelectTrigger className="h-8 w-[4.5rem]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {PAGE_SIZES.map((n) => (
                  <SelectItem key={n} value={String(n)}>
                    {n}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="flex items-center gap-1">
            <Button
              type="button"
              variant="outline"
              size="sm"
              className="h-8"
              disabled={!table.getCanPreviousPage()}
              onClick={() => table.previousPage()}
            >
              Назад
            </Button>
            <span className="px-2 text-xs text-muted-foreground">
              {table.getState().pagination.pageIndex + 1} / {table.getPageCount() || 1}
            </span>
            <Button
              type="button"
              variant="outline"
              size="sm"
              className="h-8"
              disabled={!table.getCanNextPage()}
              onClick={() => table.nextPage()}
            >
              Вперёд
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
