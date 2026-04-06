import { readVerboseLog, writeVerboseLog } from "@/lib/appPrefs";

/** Слушатели диагностики обновляют список записей журнала. */
export const GCE_APP_LOG_EVENT = "gce-app-log";

export type AppLogLevel = "debug" | "info" | "warn" | "error";

export type AppLogEntry = {
  t: number;
  level: AppLogLevel;
  message: string;
};

const MAX_ENTRIES = 200;
let buffer: AppLogEntry[] = [];
let verbose = typeof localStorage !== "undefined" ? readVerboseLog() : false;

export function syncVerboseFromStorage(): void {
  verbose = readVerboseLog();
}

export function setVerboseLogging(enabled: boolean): void {
  verbose = enabled;
  writeVerboseLog(enabled);
}

export function isVerboseLogging(): boolean {
  return verbose;
}

function push(level: AppLogLevel, message: string): void {
  const entry: AppLogEntry = { t: Date.now(), level, message };
  buffer = [...buffer.slice(-(MAX_ENTRIES - 1)), entry];
  if (typeof window !== "undefined") {
    window.dispatchEvent(new CustomEvent(GCE_APP_LOG_EVENT));
  }
  const toConsole = level === "error" || level === "warn" || verbose || level === "info";
  if (!toConsole) {
    return;
  }
  const line = `[GCE ${level}] ${message}`;
  if (level === "error") {
    console.error(line);
  } else if (level === "warn") {
    console.warn(line);
  } else {
    console.log(line);
  }
}

export function logApp(level: AppLogLevel, message: string): void {
  push(level, message);
}

export function logDebug(message: string): void {
  push("debug", message);
}

export function getLogEntries(): AppLogEntry[] {
  return [...buffer];
}

export function clearLogEntries(): void {
  buffer = [];
}
