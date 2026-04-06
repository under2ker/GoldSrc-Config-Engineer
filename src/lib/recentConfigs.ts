import { dispatchRecentUpdated } from "@/lib/uiEvents";

const STORAGE_KEY = "gce:recent-configs";
const MAX_ITEMS = 10;

export type RecentConfigEntry = {
  id: string;
  name: string;
  modeLabel: string;
  savedAt: string;
  path: string;
};

function safeParse(raw: string | null): RecentConfigEntry[] {
  if (!raw) {
    return [];
  }
  try {
    const data = JSON.parse(raw) as unknown;
    if (!Array.isArray(data)) {
      return [];
    }
    return data.filter(
      (x): x is RecentConfigEntry =>
        typeof x === "object" &&
        x !== null &&
        typeof (x as RecentConfigEntry).path === "string" &&
        typeof (x as RecentConfigEntry).name === "string",
    );
  } catch {
    return [];
  }
}

export function loadRecentConfigs(): RecentConfigEntry[] {
  return safeParse(localStorage.getItem(STORAGE_KEY));
}

export function addRecentConfig(input: {
  path: string;
  modeLabel: string;
  name?: string;
}): void {
  const name = input.name ?? input.path.split(/[/\\]/).pop() ?? "config.cfg";
  const item: RecentConfigEntry = {
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
    name,
    modeLabel: input.modeLabel,
    savedAt: new Date().toISOString(),
    path: input.path,
  };
  const rest = loadRecentConfigs().filter((x) => x.path !== item.path);
  const next = [item, ...rest].slice(0, MAX_ITEMS);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  dispatchRecentUpdated();
}

export function clearRecentConfigs(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
    dispatchRecentUpdated();
  } catch {
    /* ignore */
  }
}
