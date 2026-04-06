import type { Change } from "diff";

/** Динамический импорт `diff`, чтобы не раздувать начальный бандл. */
export async function diffLinesLazy(a: string, b: string): Promise<Change[]> {
  const { diffLines } = await import("diff");
  return diffLines(a, b);
}
