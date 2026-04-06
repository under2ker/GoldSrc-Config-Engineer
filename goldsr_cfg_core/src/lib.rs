//! Чистая логика и каталоги данных (режимы, пресеты, …) без зависимости от Tauri.

mod cfg_config;
mod data;
mod exporter;
mod generator;
mod importer;
mod validator;

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct GameModeSummary {
    pub id: String,
    pub name_en: String,
    pub name_ru: String,
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct ProPresetSummary {
    pub id: String,
    pub name: String,
    pub team: String,
    pub role: String,
}

pub use data::aliases::{generate_aliases_cfg, list_alias_catalog_json, AliasCatalogItem};
pub use cfg_config::CfgConfig;
pub use exporter::{generate_modular_files, ModularFile};
pub use generator::{create_mode_config, create_preset_config, generate_single_cfg};
pub use data::modes::list_mode_summaries;
pub use data::presets::list_pro_preset_summaries;
pub use importer::{check_dangerous, parse_cfg_text_to_config};
pub use validator::validate_settings_keys;

/// Версия crate (для отладки и health-check).
pub fn core_version() -> &'static str {
    env!("CARGO_PKG_VERSION")
}

#[cfg(test)]
mod version_tests {
    use super::core_version;

    #[test]
    fn core_version_is_semver_like() {
        let v = core_version();
        assert!(!v.is_empty(), "core_version must not be empty");
        assert!(
            v.chars().all(|c| c.is_ascii_digit() || c == '.'),
            "unexpected core_version: {v}"
        );
    }
}
