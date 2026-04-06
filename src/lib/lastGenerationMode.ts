/** Последний выбранный режим генерации (синхронизация дашборд / мастер / экспорт). */
const KEY = "gce:last-mode-id";

export function readLastModeId(): string | null {
  try {
    const v = localStorage.getItem(KEY);
    return v && v.length > 0 ? v : null;
  } catch {
    return null;
  }
}

export function writeLastModeId(id: string): void {
  try {
    localStorage.setItem(KEY, id);
  } catch {
    /* ignore */
  }
}
