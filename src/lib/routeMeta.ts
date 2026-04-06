import type { AppLocale } from "@/lib/appPrefs";
import { getRouteSegmentLabel } from "@/lib/i18n";

export function pathToBreadcrumbs(
  pathname: string,
  locale: AppLocale,
): { href: string; label: string }[] {
  const segments = pathname.split("/").filter(Boolean);
  const out: { href: string; label: string }[] = [];
  let acc = "";
  for (const seg of segments) {
    acc += `/${seg}`;
    const label = getRouteSegmentLabel(seg, locale);
    out.push({ href: acc, label });
  }
  return out;
}
