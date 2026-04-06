import { useCallback, useMemo } from "react";

import type { AppLocale } from "@/lib/appPrefs";
import en from "@/locales/en.json";
import ru from "@/locales/ru.json";
import { useAppStore } from "@/stores/appStore";

export type Messages = typeof ru;

const bundles: Record<AppLocale, Messages> = { ru, en };

function getByPath(obj: unknown, path: string): unknown {
  const parts = path.split(".");
  let cur: unknown = obj;
  for (const p of parts) {
    if (cur === null || cur === undefined || typeof cur !== "object") return undefined;
    cur = (cur as Record<string, unknown>)[p];
  }
  return cur;
}

/** Simple {{key}} interpolation for tooltip strings */
export function interpolate(
  template: string,
  vars: Record<string, string | number | undefined | null>,
): string {
  return template.replace(/\{\{(\w+)\}\}/g, (_, key: string) => {
    const v = vars[key];
    return v != null ? String(v) : "";
  });
}

export function getLayoutPage(
  locale: AppLocale,
  pathname: string,
): { title: string; subtitle?: string } | undefined {
  const pages = bundles[locale].layout.page as Record<
    string,
    { title: string; subtitle?: string }
  >;
  return pages[pathname];
}

export function getRouteSegmentLabel(segment: string, locale: AppLocale): string {
  const key = `route.${segment}`;
  const raw = getByPath(bundles[locale], key);
  return typeof raw === "string" ? raw : segment;
}

export function useI18n() {
  const locale = useAppStore((s) => s.locale);
  const messages = bundles[locale];

  const t = useCallback(
    (key: string) => {
      const v = getByPath(messages, key);
      return typeof v === "string" ? v : key;
    },
    [messages],
  );

  return useMemo(() => ({ t, locale, messages }), [t, locale, messages]);
}
