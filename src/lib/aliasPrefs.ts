import type { AliasPreset } from "@/stores/configStore";

const KEY = "goldsr_cfg_engineer_alias_prefs";

export type StoredAliasPrefs = {
  aliasPreset: AliasPreset;
  includePractice: boolean;
  aliasEnabled: Record<string, boolean>;
};

export function readAliasPrefs(): Partial<StoredAliasPrefs> | null {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return null;
    const v = JSON.parse(raw) as unknown;
    if (!v || typeof v !== "object") return null;
    const o = v as Record<string, unknown>;
    const aliasPreset = o.aliasPreset;
    const includePractice = o.includePractice;
    const aliasEnabled = o.aliasEnabled;
    const out: Partial<StoredAliasPrefs> = {};
    if (aliasPreset === "minimal" || aliasPreset === "full" || aliasPreset === "custom") {
      out.aliasPreset = aliasPreset;
    }
    if (typeof includePractice === "boolean") {
      out.includePractice = includePractice;
    }
    if (aliasEnabled && typeof aliasEnabled === "object" && !Array.isArray(aliasEnabled)) {
      out.aliasEnabled = aliasEnabled as Record<string, boolean>;
    }
    return Object.keys(out).length > 0 ? out : null;
  } catch {
    return null;
  }
}

export function writeAliasPrefs(p: StoredAliasPrefs): void {
  try {
    localStorage.setItem(KEY, JSON.stringify(p));
  } catch {
    /* private mode */
  }
}
