import type { Change } from "diff";
import type { CfgLineCategory } from "@/lib/cfgLineCategory";
import { inferCfgLineCategory } from "@/lib/cfgLineCategory";

export type DiffTableRow = {
  id: string;
  partIndex: number;
  lineIndex: number;
  kind: "added" | "removed" | "unchanged";
  text: string;
  category: CfgLineCategory;
};

/** Разбивает фрагменты diff на строки (для таблицы и CSV). */
export function flattenDiffPartsToRows(parts: Change[]): DiffTableRow[] {
  const out: DiffTableRow[] = [];
  for (let pi = 0; pi < parts.length; pi++) {
    const p = parts[pi]!;
    const kind: DiffTableRow["kind"] = p.added ? "added" : p.removed ? "removed" : "unchanged";
    const lines = p.value.split(/\r?\n/);
    for (let li = 0; li < lines.length; li++) {
      const text = lines[li] ?? "";
      if (text === "" && li === lines.length - 1 && li > 0) {
        continue;
      }
      out.push({
        id: `${pi}-${li}`,
        partIndex: pi,
        lineIndex: li,
        kind,
        text,
        category: inferCfgLineCategory(text),
      });
    }
  }
  return out;
}

export function diffRowsToCsv(rows: DiffTableRow[]): string {
  const header = ["kind", "category", "part", "line", "text"];
  const lines = [header.join(",")];
  for (const r of rows) {
    const cells = [
      r.kind,
      r.category,
      String(r.partIndex),
      String(r.lineIndex),
      `"${r.text.replace(/"/g, '""').replace(/\r?\n/g, "\\n")}"`,
    ];
    lines.push(cells.join(","));
  }
  return lines.join("\r\n");
}
