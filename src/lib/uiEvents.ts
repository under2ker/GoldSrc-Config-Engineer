/** Открыть диалог справки (F1); слушатель в `MainLayout`. */
export const GCE_OPEN_HELP = "gce:open-help";

export function dispatchOpenHelp(): void {
  window.dispatchEvent(new Event(GCE_OPEN_HELP));
}

/** История «недавних .cfg» изменилась (очистка и т.д.). */
export const GCE_RECENT_UPDATED = "gce:recent-updated";

export function dispatchRecentUpdated(): void {
  window.dispatchEvent(new Event(GCE_RECENT_UPDATED));
}
