import { invoke } from "@tauri-apps/api/core";
import { z } from "zod";
import type { AliasPreset } from "@/stores/configStore";
import type { GreetResponse, PingResponse } from "../types/api";
import {
  cfgConfigParsedSchema,
  gameDetectResultSchema,
  gameModesResponseSchema,
  generateConfigResultSchema,
  modularFileSchema,
  proPresetsResponseSchema,
  type CfgConfigParsed,
  type AppPathsInfo,
  type GameDetectResult,
  appPathsInfoSchema,
  type GameModeSummary,
  type GenerateConfigResult,
  type GenerateConfigSource,
  type ModularFile,
  type Profile,
  type HistoryEntry,
  type ProPresetSummary,
  historyListSchema,
  aliasCatalogItemSchema,
  type AliasCatalogItem,
} from "../types/api";

export async function greet(name: string): Promise<GreetResponse> {
  return invoke<GreetResponse>("greet", { name });
}

export async function ping(): Promise<PingResponse> {
  return invoke<PingResponse>("ping");
}

export async function getGameModes(): Promise<GameModeSummary[]> {
  const raw = await invoke<unknown>("get_game_modes");
  return gameModesResponseSchema.parse(raw);
}

export async function getProPresets(): Promise<ProPresetSummary[]> {
  const raw = await invoke<unknown>("get_pro_presets");
  return proPresetsResponseSchema.parse(raw);
}

/** Каталог алиасов из `data/aliases.json` (синхронно с Rust; для проверки и тестов). */
export async function getAliasesCatalog(): Promise<AliasCatalogItem[]> {
  const raw = await invoke<unknown>("get_aliases_catalog");
  return z.array(aliasCatalogItemSchema).parse(raw);
}

export type AliasGenerationOptions = {
  aliasPreset?: AliasPreset | null;
  includePractice?: boolean | null;
  /** Для режима `custom`; для `minimal`/`full` можно не передавать. */
  aliasEnabled?: Record<string, boolean> | null;
};

export async function generateConfig(
  source: GenerateConfigSource,
  id: string,
  opts?: AliasGenerationOptions,
): Promise<GenerateConfigResult> {
  const raw = await invoke<unknown>("generate_config", {
    source,
    id,
    aliasPreset: opts?.aliasPreset ?? null,
    includePractice: opts?.includePractice ?? null,
    aliasEnabled: opts?.aliasEnabled ?? null,
  });
  return generateConfigResultSchema.parse(raw);
}

/** Предупреждения безопасности по тексту импорта (пустой массив — ок). */
export async function checkCfgImportSafety(text: string): Promise<string[]> {
  return invoke<string[]>("check_cfg_import_safety", { text });
}

/** Модульный набор `.cfg` (пути относительно папки записи, напр. `cstrike/`). */
export async function exportModularConfig(
  source: GenerateConfigSource,
  id: string,
  opts?: AliasGenerationOptions,
): Promise<ModularFile[]> {
  const raw = await invoke<unknown>("export_modular_config", {
    source,
    id,
    aliasPreset: opts?.aliasPreset ?? null,
    includePractice: opts?.includePractice ?? null,
    aliasEnabled: opts?.aliasEnabled ?? null,
  });
  const arr = z.array(modularFileSchema).parse(raw);
  return arr;
}

/** Разбор текста `.cfg` в JSON (`CfgConfig`: settings, binds, …). */
export async function parseImportCfg(text: string): Promise<CfgConfigParsed> {
  const raw = await invoke<unknown>("parse_import_cfg", { text });
  return cfgConfigParsedSchema.parse(raw);
}

/** Один `.cfg` из JSON профиля / импорта. */
export async function generateConfigFromJson(configJson: string): Promise<GenerateConfigResult> {
  const raw = await invoke<unknown>("generate_config_from_json", { configJson });
  return generateConfigResultSchema.parse(raw);
}

/** Модульный набор из JSON (`CfgConfig`). */
export async function exportModularFromJson(configJson: string): Promise<ModularFile[]> {
  const raw = await invoke<unknown>("export_modular_from_json", { configJson });
  return z.array(modularFileSchema).parse(raw);
}

/** JSON-снимок `CfgConfig` для текущего режима/пресета (история, повторный экспорт). */
export async function exportConfigSnapshot(
  source: GenerateConfigSource,
  id: string,
  opts?: AliasGenerationOptions,
): Promise<string> {
  return invoke<string>("export_config_snapshot", {
    source,
    id,
    aliasPreset: opts?.aliasPreset ?? null,
    includePractice: opts?.includePractice ?? null,
    aliasEnabled: opts?.aliasEnabled ?? null,
  });
}

export async function profileList(): Promise<Profile[]> {
  return invoke<Profile[]>("profile_list");
}

export async function profileSave(name: string, configJson: string): Promise<string> {
  return invoke<string>("profile_save", { name, configJson });
}

export async function profileLoad(id: string): Promise<string> {
  return invoke<string>("profile_load", { id });
}

export async function profileDelete(id: string): Promise<void> {
  return invoke<void>("profile_delete", { id });
}

export async function profileUpdate(
  id: string,
  patch: { name?: string | null; isFavorite?: boolean | null },
): Promise<void> {
  await invoke<void>("profile_update", {
    id,
    name: patch.name ?? null,
    is_favorite: patch.isFavorite ?? null,
  });
}

export async function historyAppend(configJson: string, profileId: string | null): Promise<number> {
  return invoke<number>("history_append", { configJson, profile_id: profileId });
}

export async function historyList(limit = 50): Promise<HistoryEntry[]> {
  const raw = await invoke<unknown>("history_list", { limit });
  return historyListSchema.parse(raw);
}

export async function historyLoad(id: number): Promise<string> {
  return invoke<string>("history_load", { id });
}

export async function historyDelete(id: number): Promise<void> {
  return invoke<void>("history_delete", { id });
}

/** Удалить все записи истории снимков. Возвращает число удалённых строк. */
export async function historyClear(): Promise<number> {
  return invoke<number>("history_clear");
}

/** Число записей в таблице истории (SQLite). */
export async function historyCount(): Promise<number> {
  return invoke<number>("history_count");
}

export async function appSettingsGet(key: string): Promise<string | null> {
  return invoke<string | null>("app_settings_get", { key });
}

export async function appSettingsSet(key: string, value: string): Promise<void> {
  await invoke<void>("app_settings_set", { key, value });
}

/** Загрузить текст по http(s) для импорта (только настольное приложение). */
export async function fetchTextFromUrl(url: string): Promise<string> {
  return invoke<string>("fetch_text_from_url", { url });
}

export async function detectGameInstallation(): Promise<GameDetectResult> {
  const raw = await invoke<unknown>("detect_game_installation");
  return gameDetectResultSchema.parse(raw);
}

export async function getAppPathsInfo(): Promise<AppPathsInfo> {
  const raw = await invoke<unknown>("get_app_paths_info");
  return appPathsInfoSchema.parse(raw);
}

export async function deployModularFiles(targetDir: string, files: ModularFile[]): Promise<void> {
  return invoke<void>("deploy_modular_files", { targetDir, files });
}
