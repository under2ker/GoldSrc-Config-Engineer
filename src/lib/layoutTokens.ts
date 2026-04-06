/**
 * Общие константы раскладки: max-width контентной колонки, шаг сетки кратный 4px (gap-4 / gap-6),
 * каталог — одинаковое число колонок на «Режимы» и «Про-пресеты».
 */
export const PAGE_MAX_W = "max-w-5xl";

/** Узкая колонка: мастера, диагностика, настройки (читаемость длинных форм). */
export const PAGE_MAX_W_NARROW = "max-w-2xl";

/** Вертикальный ритм между секциями страницы (24px). */
export const PAGE_STACK = "flex flex-col gap-6";

/** Вводный абзац под шапкой приложения (типографика вторичного текста). */
export const pageLeadClass = "text-sm leading-relaxed text-muted-foreground";

/** Заголовок секции внутри контента страницы (не глобальный H1 шапки). */
export const pageSectionTitleClass =
  "text-xs font-semibold uppercase tracking-wider text-muted-foreground";

/** Мелкий вторичный текст: подписи в карточках, пояснения к меткам. */
export const pageCaptionClass = "text-xs leading-relaxed text-muted-foreground";

/**
 * Строка над метрикой / полем: uppercase, без жирного (как «overline» в UI-китах).
 * Для жирных заголовков секций см. pageSectionTitleClass.
 */
export const pageOverlineClass = "text-xs uppercase tracking-wide text-muted-foreground";

/** Заголовок группы контента (команда пресетов, крупнее pageSectionTitleClass). */
export const pageSectionGroupTitleClass =
  "text-sm font-semibold uppercase tracking-wide text-muted-foreground";

export const pageShellClass = `mx-auto w-full ${PAGE_MAX_W} ${PAGE_STACK}`;

export const pageShellNarrowClass = `mx-auto w-full ${PAGE_MAX_W_NARROW} ${PAGE_STACK}`;

/**
 * Заголовки групп навигации в сайдбаре (узкая колонка, кегль ~10px).
 * См. также `--sidebar-*` в `globals.css`.
 */
export const sidebarNavGroupLabelClass =
  "mb-2 px-2 text-[10px] font-semibold uppercase tracking-[0.12em] text-muted-foreground";

/** Подпись строки состояния в сайдбаре («Недавний .cfg»). */
export const sidebarStatusOverlineClass =
  "text-[10px] font-semibold uppercase tracking-[0.08em] text-muted-foreground";

/** Вторичная строка под логотипом в шапке сайдбара. */
export const sidebarBrandMetaClass = "mt-0.5 text-xs leading-relaxed text-muted-foreground";

/** Основной текст строки недавнего файла в сайдбаре. */
export const sidebarRecentNameClass = "truncate text-xs leading-relaxed text-sidebar-foreground/95";

/** Карточки каталога: 1 → 2 (sm) → 3 (xl), без расхождения 2 vs 3 между экранами. */
export const CATALOG_GRID = "grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-3";
