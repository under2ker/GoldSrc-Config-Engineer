/**
 * Контракты IPC с Rust (Tauri invoke) + Zod для ответов.
 */
import { z } from "zod";

export const gameModeSummarySchema = z.object({
  id: z.string(),
  name_en: z.string(),
  name_ru: z.string(),
});

export const proPresetSummarySchema = z.object({
  id: z.string(),
  name: z.string(),
  team: z.string(),
  role: z.string(),
});

export type GameModeSummary = z.infer<typeof gameModeSummarySchema>;
export type ProPresetSummary = z.infer<typeof proPresetSummarySchema>;

export const gameModesResponseSchema = z.array(gameModeSummarySchema);
export const proPresetsResponseSchema = z.array(proPresetSummarySchema);

export const generateConfigSourceSchema = z.enum(["mode", "preset"]);

export const generateConfigResultSchema = z.object({
  content: z.string(),
  label: z.string(),
});

export type GenerateConfigSource = z.infer<typeof generateConfigSourceSchema>;
export type GenerateConfigResult = z.infer<typeof generateConfigResultSchema>;

/** Ответ простой строковой команды */
export type GreetResponse = string;

/** health-check backend */
export type PingResponse = string;

/** Профиль в локальной БД (SQLite через Tauri). */
export type Profile = {
  id: string;
  name: string;
  updated_at: string;
  is_favorite: boolean;
};

/** Запись истории снимков конфига (без полного JSON в списке). */
export type HistoryEntry = {
  id: number;
  profile_id: string | null;
  created_at: string;
  size_bytes: number;
};

export const historyEntrySchema = z.object({
  id: z.number(),
  profile_id: z.string().nullable(),
  created_at: z.string(),
  size_bytes: z.number(),
});

export const historyListSchema = z.array(historyEntrySchema);

export const modularFileSchema = z.object({
  relative_path: z.string(),
  content: z.string(),
});

export type ModularFile = z.infer<typeof modularFileSchema>;

export const gameDetectResultSchema = z.object({
  path: z.string().nullable(),
  hint: z.string(),
});

export type GameDetectResult = z.infer<typeof gameDetectResultSchema>;

export const appPathsInfoSchema = z.object({
  app_data_dir: z.string(),
  sqlite_db_path: z.string(),
});

export type AppPathsInfo = z.infer<typeof appPathsInfoSchema>;

/** Отчёт `catalog_sync_now` (Tauri): синхронизация `data/*.json` с GitHub. */
export const catalogSyncReportSchema = z.object({
  checked: z.number(),
  updated: z.number(),
  skippedNotModified: z.number(),
  errors: z.array(z.string()),
});

export type CatalogSyncReport = z.infer<typeof catalogSyncReportSchema>;

/** Снимок `CfgConfig` после разбора `.cfg` (совпадает с `goldsr_cfg_core::CfgConfig`). */
export const cfgConfigParsedSchema = z.object({
  settings: z.record(z.string(), z.string()),
  binds: z.record(z.string(), z.string()),
  buy_binds: z.record(z.string(), z.string()),
  mode: z.string().nullable().optional(),
  mode_key: z.string().nullable().optional(),
  preset_name: z.string().nullable().optional(),
  description: z.string(),
});

export type CfgConfigParsed = z.infer<typeof cfgConfigParsedSchema>;

export const aliasCatalogItemSchema = z.object({
  section: z.string(),
  section_label: z.string(),
  name: z.string(),
  description: z.string(),
  safety: z.string(),
  required: z.boolean(),
});

export type AliasCatalogItem = z.infer<typeof aliasCatalogItemSchema>;
