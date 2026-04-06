/** Подписи сегментов для breadcrumbs и заголовков (единый источник). */
export const ROUTE_LABELS: Record<string, string> = {
  dashboard: "Главная",
  "quick-setup": "Быстрая настройка",
  modes: "Режимы",
  presets: "Про-пресеты",
  crosshair: "Прицел",
  sensitivity: "Чувствительность мыши",
  compare: "Сравнение конфигов",
  export: "Экспорт",
  import: "Импорт",
  "launch-options": "Параметры запуска",
  preview: "Просмотр",
  diagnostics: "Диагностика",
  settings: "Настройки",
};

export function pathToBreadcrumbs(pathname: string): { href: string; label: string }[] {
  const segments = pathname.split("/").filter(Boolean);
  const out: { href: string; label: string }[] = [];
  let acc = "";
  for (const seg of segments) {
    acc += `/${seg}`;
    const label = ROUTE_LABELS[seg] ?? seg;
    out.push({ href: acc, label });
  }
  return out;
}
