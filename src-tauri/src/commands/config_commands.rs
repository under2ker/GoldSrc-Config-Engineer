use std::collections::HashMap;

use goldsr_cfg_core::{
    check_dangerous, core_version, create_mode_config, create_preset_config, generate_modular_files,
    generate_single_cfg, list_alias_catalog_json, list_mode_summaries, list_pro_preset_summaries,
    parse_cfg_text_to_config, validate_settings_keys, AliasCatalogItem, CfgConfig, GameModeSummary,
    ModularFile, ProPresetSummary,
};
use serde::Serialize;

#[tauri::command]
pub fn ping() -> String {
    format!(
        "goldsr-cfg-v3 core={}",
        core_version()
    )
}

#[tauri::command]
pub fn get_game_modes() -> Result<Vec<GameModeSummary>, String> {
    list_mode_summaries()
}

#[tauri::command]
pub fn get_pro_presets() -> Result<Vec<ProPresetSummary>, String> {
    list_pro_preset_summaries()
}

#[derive(Debug, Serialize)]
pub struct GenerateConfigResult {
    pub content: String,
    pub label: String,
}

fn merge_alias_options(
    cfg: &mut CfgConfig,
    alias_preset: Option<String>,
    include_practice: Option<bool>,
    alias_enabled: Option<HashMap<String, bool>>,
) {
    if let Some(p) = alias_preset {
        cfg.alias_preset = p;
    }
    if let Some(b) = include_practice {
        cfg.include_practice = b;
    }
    if let Some(m) = alias_enabled {
        cfg.alias_enabled = m;
    }
}

/// Каталог алиасов из `data/aliases.json` (71+ пунктов) для UI.
#[tauri::command]
pub fn get_aliases_catalog() -> Result<Vec<AliasCatalogItem>, String> {
    list_alias_catalog_json()
}

/// `source`: `"mode"` | `"preset"`. `id` — ключ из `modes.json` / `presets.json`.
#[tauri::command]
pub fn generate_config(
    source: String,
    id: String,
    alias_preset: Option<String>,
    include_practice: Option<bool>,
    alias_enabled: Option<HashMap<String, bool>>,
) -> Result<GenerateConfigResult, String> {
    let mut cfg = match source.as_str() {
        "mode" => create_mode_config(&id)?,
        "preset" => create_preset_config(&id)?,
        _ => return Err(r#"source должен быть "mode" или "preset""#.into()),
    };
    merge_alias_options(&mut cfg, alias_preset, include_practice, alias_enabled);
    let _ = validate_settings_keys(&cfg.settings, false);
    let label = cfg
        .preset_name
        .clone()
        .or(cfg.mode.clone())
        .unwrap_or_else(|| id.clone());
    let content = generate_single_cfg(&cfg)?;
    Ok(GenerateConfigResult { content, label })
}

/// Список предупреждений по безопасности импорта (пусто — можно показывать текст).
#[tauri::command]
pub fn check_cfg_import_safety(text: String) -> Vec<String> {
    check_dangerous(&text)
}

/// Модульный набор файлов для режима/пресета (относительные пути + содержимое).
#[tauri::command]
pub fn export_modular_config(
    source: String,
    id: String,
    alias_preset: Option<String>,
    include_practice: Option<bool>,
    alias_enabled: Option<HashMap<String, bool>>,
) -> Result<Vec<ModularFile>, String> {
    let mut cfg = match source.as_str() {
        "mode" => create_mode_config(&id)?,
        "preset" => create_preset_config(&id)?,
        _ => return Err(r#"source должен быть "mode" или "preset""#.into()),
    };
    merge_alias_options(&mut cfg, alias_preset, include_practice, alias_enabled);
    let _ = validate_settings_keys(&cfg.settings, false);
    generate_modular_files(&cfg)
}

/// Разбор `.cfg` в JSON-объект настроек (`settings`, `binds`, `buy_binds`, …).
#[tauri::command]
pub fn parse_import_cfg(text: String) -> Result<serde_json::Value, String> {
    let cfg = parse_cfg_text_to_config(&text)?;
    serde_json::to_value(&cfg).map_err(|e| e.to_string())
}

fn cfg_from_json_str(config_json: &str) -> Result<CfgConfig, String> {
    serde_json::from_str(config_json).map_err(|e| e.to_string())
}

/// Один `.cfg` из сохранённого JSON профиля / импорта.
#[tauri::command]
pub fn generate_config_from_json(config_json: String) -> Result<GenerateConfigResult, String> {
    let cfg = cfg_from_json_str(&config_json)?;
    let _ = validate_settings_keys(&cfg.settings, false);
    let label = cfg
        .preset_name
        .clone()
        .or(cfg.mode.clone())
        .unwrap_or_else(|| "Профиль".into());
    let content = generate_single_cfg(&cfg)?;
    Ok(GenerateConfigResult { content, label })
}

/// Модульный набор из JSON (`CfgConfig`).
#[tauri::command]
pub fn export_modular_from_json(config_json: String) -> Result<Vec<ModularFile>, String> {
    let cfg = cfg_from_json_str(&config_json)?;
    let _ = validate_settings_keys(&cfg.settings, false);
    generate_modular_files(&cfg)
}

/// JSON-снимок `CfgConfig` для режима/пресета (история экспорта, повторная сборка).
#[tauri::command]
pub fn export_config_snapshot(
    source: String,
    id: String,
    alias_preset: Option<String>,
    include_practice: Option<bool>,
    alias_enabled: Option<HashMap<String, bool>>,
) -> Result<String, String> {
    let mut cfg = match source.as_str() {
        "mode" => create_mode_config(&id)?,
        "preset" => create_preset_config(&id)?,
        _ => return Err(r#"source должен быть "mode" или "preset""#.into()),
    };
    merge_alias_options(&mut cfg, alias_preset, include_practice, alias_enabled);
    let _ = validate_settings_keys(&cfg.settings, false);
    serde_json::to_string(&cfg).map_err(|e| e.to_string())
}

