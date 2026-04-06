import type { AppLocale } from "@/lib/appPrefs";

/** Короткая относительная подпись для списков «недавно» (локаль из настроек). */
export function formatRelativeTime(iso: string, locale: AppLocale): string {
  const then = new Date(iso).getTime();
  const now = Date.now();
  const diffSec = Math.round((then - now) / 1000);
  const loc = locale === "en" ? "en" : "ru";
  const rtf = new Intl.RelativeTimeFormat(loc, { numeric: "auto" });

  const absMin = Math.abs(Math.round(diffSec / 60));
  if (absMin < 60) {
    return rtf.format(Math.round(diffSec / 60), "minute");
  }
  const absH = Math.abs(Math.round(diffSec / 3600));
  if (absH < 24) {
    return rtf.format(Math.round(diffSec / 3600), "hour");
  }
  const absD = Math.abs(Math.round(diffSec / 86400));
  if (absD < 7) {
    return rtf.format(Math.round(diffSec / 86400), "day");
  }
  return new Date(iso).toLocaleDateString(loc, {
    day: "numeric",
    month: "short",
    year: new Date(iso).getFullYear() === new Date().getFullYear() ? undefined : "numeric",
  });
}

/** @deprecated используйте {@link formatRelativeTime} с локалью */
export function formatRelativeRu(iso: string): string {
  return formatRelativeTime(iso, "ru");
}
