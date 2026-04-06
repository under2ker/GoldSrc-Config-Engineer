import { create } from "zustand";
import type { AppLocale, ThemeMode } from "@/lib/appPrefs";
import { setVerboseLogging } from "@/lib/appLogger";
import {
  applyLocale,
  applyReduceMotion,
  applyTheme,
  readLocale,
  readReduceMotion,
  readSidebarCollapsed,
  readTheme,
  readVerboseLog,
  writeLocale,
  writeReduceMotion,
  writeSidebarCollapsed,
  writeTheme,
} from "@/lib/appPrefs";

type AppState = {
  locale: AppLocale;
  theme: ThemeMode;
  sidebarCollapsed: boolean;
  reduceMotion: boolean;
  verboseLog: boolean;
  setLocale: (locale: AppLocale) => void;
  setTheme: (theme: ThemeMode) => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  toggleSidebarCollapsed: () => void;
  setReduceMotion: (enabled: boolean) => void;
  setVerboseLog: (enabled: boolean) => void;
};

const initialTheme = readTheme();
const initialLocale = readLocale();
const initialSidebarCollapsed = readSidebarCollapsed();
const initialReduceMotion = readReduceMotion();
const initialVerboseLog = readVerboseLog();

export const useAppStore = create<AppState>((set, get) => ({
  locale: initialLocale,
  theme: initialTheme,
  sidebarCollapsed: initialSidebarCollapsed,
  reduceMotion: initialReduceMotion,
  verboseLog: initialVerboseLog,
  setLocale: (locale) => {
    writeLocale(locale);
    applyLocale(locale);
    set({ locale });
  },
  setTheme: (theme) => {
    writeTheme(theme);
    applyTheme(theme);
    set({ theme });
  },
  setSidebarCollapsed: (collapsed) => {
    writeSidebarCollapsed(collapsed);
    set({ sidebarCollapsed: collapsed });
  },
  toggleSidebarCollapsed: () => {
    const next = !get().sidebarCollapsed;
    writeSidebarCollapsed(next);
    set({ sidebarCollapsed: next });
  },
  setReduceMotion: (enabled) => {
    writeReduceMotion(enabled);
    applyReduceMotion(enabled);
    set({ reduceMotion: enabled });
  },
  setVerboseLog: (enabled) => {
    setVerboseLogging(enabled);
    set({ verboseLog: enabled });
  },
}));
