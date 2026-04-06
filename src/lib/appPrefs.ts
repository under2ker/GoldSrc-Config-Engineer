export type ThemeMode = "dark" | "light";
export type AppLocale = "ru" | "en";

const THEME_KEY = "goldsr_cfg_engineer_theme";
const LOCALE_KEY = "goldsr_cfg_engineer_locale";
const SIDEBAR_COLLAPSED_KEY = "goldsr_cfg_engineer_sidebar_collapsed";
const REDUCED_MOTION_KEY = "goldsr_cfg_engineer_reduced_motion";
const VERBOSE_LOG_KEY = "goldsr_cfg_engineer_verbose_log";

/** Если в localStorage нет явного выбора — ориентир на системную тему (WCAG / комфорт). */
function themeFromSystemPreference(): ThemeMode {
  if (typeof window === "undefined") {
    return "dark";
  }
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export function readTheme(): ThemeMode {
  try {
    const v = localStorage.getItem(THEME_KEY);
    if (v === "light" || v === "dark") {
      return v;
    }
  } catch {
    /* private mode / denied */
  }
  return themeFromSystemPreference();
}

export function writeTheme(t: ThemeMode): void {
  try {
    localStorage.setItem(THEME_KEY, t);
  } catch {
    /* ignore */
  }
}

export function applyTheme(t: ThemeMode): void {
  document.documentElement.classList.toggle("dark", t === "dark");
}

export function readLocale(): AppLocale {
  try {
    const v = localStorage.getItem(LOCALE_KEY);
    if (v === "ru" || v === "en") {
      return v;
    }
  } catch {
    /* ignore */
  }
  return "ru";
}

export function writeLocale(l: AppLocale): void {
  try {
    localStorage.setItem(LOCALE_KEY, l);
  } catch {
    /* ignore */
  }
}

export function applyLocale(l: AppLocale): void {
  document.documentElement.lang = l;
}

export function readSidebarCollapsed(): boolean {
  try {
    return localStorage.getItem(SIDEBAR_COLLAPSED_KEY) === "1";
  } catch {
    return false;
  }
}

export function writeSidebarCollapsed(collapsed: boolean): void {
  try {
    localStorage.setItem(SIDEBAR_COLLAPSED_KEY, collapsed ? "1" : "0");
  } catch {
    /* ignore */
  }
}

/** Явное «1»/«0» в LS; если ключа нет — учитывается системная настройка ОС. */
export function readReduceMotion(): boolean {
  try {
    const v = localStorage.getItem(REDUCED_MOTION_KEY);
    if (v === "1") {
      return true;
    }
    if (v === "0") {
      return false;
    }
  } catch {
    /* ignore */
  }
  if (typeof window === "undefined") {
    return false;
  }
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export function writeReduceMotion(enabled: boolean): void {
  try {
    localStorage.setItem(REDUCED_MOTION_KEY, enabled ? "1" : "0");
  } catch {
    /* ignore */
  }
}

export function applyReduceMotion(enabled: boolean): void {
  if (enabled) {
    document.documentElement.dataset.reducedMotion = "on";
  } else {
    delete document.documentElement.dataset.reducedMotion;
  }
}

export function readVerboseLog(): boolean {
  try {
    return localStorage.getItem(VERBOSE_LOG_KEY) === "1";
  } catch {
    return false;
  }
}

export function writeVerboseLog(enabled: boolean): void {
  try {
    localStorage.setItem(VERBOSE_LOG_KEY, enabled ? "1" : "0");
  } catch {
    /* ignore */
  }
}
