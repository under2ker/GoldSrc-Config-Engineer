//! Снимок настроек конфига (аналог Python `CfgConfig`).

use std::collections::HashMap;

fn default_alias_preset() -> String {
    "minimal".to_string()
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct CfgConfig {
    pub settings: HashMap<String, String>,
    pub binds: HashMap<String, String>,
    pub buy_binds: HashMap<String, String>,
    pub mode: Option<String>,
    pub mode_key: Option<String>,
    pub preset_name: Option<String>,
    pub description: String,
    /// Секция practice в aliases.json (команды с sv_cheats и т.д.).
    #[serde(default)]
    pub include_practice: bool,
    /// `minimal` — только `required: true`; `full` — все подходящие секции; `custom` — только `alias_enabled`.
    #[serde(default = "default_alias_preset")]
    pub alias_preset: String,
    /// Ключи `section:name` → включён ли алиас (для `alias_preset == "custom"`).
    #[serde(default)]
    pub alias_enabled: HashMap<String, bool>,
}

impl Default for CfgConfig {
    fn default() -> Self {
        Self {
            settings: HashMap::new(),
            binds: HashMap::new(),
            buy_binds: HashMap::new(),
            mode: None,
            mode_key: None,
            preset_name: None,
            description: String::new(),
            include_practice: false,
            alias_preset: default_alias_preset(),
            alias_enabled: HashMap::new(),
        }
    }
}

impl CfgConfig {
    pub fn set(&mut self, cvar: impl Into<String>, value: impl Into<String>) {
        self.settings.insert(cvar.into(), value.into());
    }

    pub fn merge_settings(&mut self, other: HashMap<String, String>) {
        self.settings.extend(other);
    }

    pub fn merge_binds(&mut self, other: HashMap<String, String>) {
        self.binds.extend(other);
    }
}
