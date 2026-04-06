//! Генерация текста одного .cfg (`generate_single_cfg`) и фабрики конфигов.

use std::collections::{BTreeMap, HashMap};

use chrono::Local;
use serde::Deserialize;

use crate::cfg_config::CfgConfig;
use crate::data::aliases::generate_aliases_cfg;
use crate::data::cvars::CvarsCatalog;
use crate::data::modes::MODES_JSON_STR;
use crate::data::presets::PRESETS_JSON_STR;

pub(crate) static CAT_ORDER: &[&str] = &[
    "network", "video", "audio", "input", "gameplay", "demo", "other",
];

#[derive(Debug, Deserialize)]
struct ModeFull {
    #[serde(default)]
    name_en: String,
    #[serde(default)]
    settings: HashMap<String, serde_json::Value>,
    #[serde(default)]
    binds: HashMap<String, String>,
    #[serde(default)]
    buy_binds: HashMap<String, String>,
}

#[derive(Debug, Deserialize)]
#[allow(dead_code)]
struct PresetFull {
    name: String,
    #[serde(default)]
    team: String,
    #[serde(default)]
    country: String,
    #[serde(default)]
    role: String,
    #[serde(default)]
    description_en: String,
    #[serde(default)]
    description_ru: String,
    #[serde(default)]
    settings: HashMap<String, serde_json::Value>,
}

fn json_to_cfg_string(v: &serde_json::Value) -> String {
    match v {
        serde_json::Value::String(s) => s.clone(),
        serde_json::Value::Number(n) => n.to_string(),
        serde_json::Value::Bool(b) => {
            if *b {
                "1".into()
            } else {
                "0".into()
            }
        }
        serde_json::Value::Null => String::new(),
        serde_json::Value::Array(_) | serde_json::Value::Object(_) => v.to_string(),
    }
}

/// Собрать конфиг из режима (`modes.json`, ключ — id).
pub fn create_mode_config(mode_key: &str) -> Result<CfgConfig, String> {
    let map: HashMap<String, ModeFull> =
        serde_json::from_str(MODES_JSON_STR).map_err(|e| e.to_string())?;
    let mode_data = map
        .get(mode_key)
        .ok_or_else(|| format!("Unknown mode: {mode_key}"))?;

    let mut cfg = CfgConfig::default();
    cfg.mode = Some(if mode_data.name_en.is_empty() {
        mode_key.to_string()
    } else {
        mode_data.name_en.clone()
    });
    cfg.mode_key = Some(mode_key.to_string());

    for (k, v) in &mode_data.settings {
        cfg.set(k, json_to_cfg_string(v));
    }
    cfg.merge_binds(mode_data.binds.clone());
    cfg.buy_binds.extend(mode_data.buy_binds.clone());
    Ok(cfg)
}

/// Собрать конфиг из про-пресета (`presets.json`).
pub fn create_preset_config(preset_key: &str) -> Result<CfgConfig, String> {
    let map: HashMap<String, PresetFull> =
        serde_json::from_str(PRESETS_JSON_STR).map_err(|e| e.to_string())?;
    let preset_data = map
        .get(preset_key)
        .ok_or_else(|| format!("Unknown preset: {preset_key}"))?;

    let mut cfg = CfgConfig::default();
    cfg.preset_name = Some(preset_data.name.clone());
    cfg.description = preset_data.description_en.clone();
    for (k, v) in &preset_data.settings {
        cfg.set(k, json_to_cfg_string(v));
    }
    Ok(cfg)
}

pub(crate) fn categorize_settings(
    catalog: &CvarsCatalog,
    settings: &HashMap<String, String>,
) -> HashMap<String, BTreeMap<String, String>> {
    let mut out: HashMap<String, BTreeMap<String, String>> = HashMap::new();
    for (cvar, value) in settings {
        let cat = catalog.category_of(cvar).to_string();
        out.entry(cat).or_default().insert(cvar.clone(), value.clone());
    }
    out
}

pub(crate) fn fmt_cvar_line(catalog: &CvarsCatalog, cvar: &str, value: &str, col: usize) -> String {
    let base = if value.starts_with('"') && value.ends_with('"') {
        format!("{cvar} {value}")
    } else {
        format!("{cvar} \"{value}\"")
    };
    let desc = catalog.description(cvar).unwrap_or("");
    if desc.is_empty() {
        return base;
    }
    let pad = col.saturating_sub(base.chars().count()).max(1);
    format!("{base}{} // {desc}", " ".repeat(pad))
}

pub(crate) fn console_banner(cfg: &CfgConfig) -> Vec<String> {
    let n_cvars = cfg.settings.len();
    let n_binds = cfg.binds.len() + cfg.buy_binds.len();
    let profile = cfg
        .preset_name
        .as_deref()
        .or(cfg.mode.as_deref())
        .unwrap_or("Custom");
    let date = Local::now().format("%Y-%m-%d %H:%M").to_string();

    vec![
        r#"echo """#.into(),
        r#"echo "=============================================="#.into(),
        r#"echo " .d8888b.   .d8888b.   .d8888b.  8888888888   "#.into(),
        r#"echo "d88P  Y88b d88P  Y88b d88P  Y88b 888          "#.into(),
        r#"echo "888    888 Y88b.      888    888 888           "#.into(),
        r#"echo "888         Y888b.    888        8888888       "#.into(),
        r#"echo "888  88888     Y88b.  888        888           "#.into(),
        r#"echo "888    888       888  888    888 888           "#.into(),
        r#"echo "Y88b  d88P Y88b  d88P Y88b  d88P 888          "#.into(),
        r#"echo " Y8888P88   Y8888PP    Y8888PP  8888888888    "#.into(),
        r#"echo """#.into(),
        r#"echo "  GoldSrc Config Engineer :: CS 1.6""#.into(),
        r#"echo "=============================================="#.into(),
        r#"echo """#.into(),
        format!(r#"echo "  [*] Config loaded: {profile}""#),
        format!(r#"echo "  [*] CVars applied: {n_cvars}""#),
        format!(r#"echo "  [*] Binds set:     {n_binds}""#),
        format!(r#"echo "  [*] Generated:     {date}""#),
        r#"echo """#.into(),
        r#"echo "  -----------------------------------------------""#.into(),
        r#"echo "   Settings applied successfully!""#.into(),
        r#"echo "   GL HF! :)""#.into(),
        r#"echo "  -----------------------------------------------""#.into(),
        r#"echo """#.into(),
    ]
}

/// Один цельный `.cfg` (как `generate_single_cfg` в Python).
pub fn generate_single_cfg(cfg: &CfgConfig) -> Result<String, String> {
    let catalog = CvarsCatalog::global();
    let now = Local::now().format("%Y-%m-%d %H:%M").to_string();

    let mut lines: Vec<String> = Vec::new();
    lines.push("// ================================================================".into());
    lines.push("// Generated by GoldSrc Config Engineer v3.0".into());
    if let Some(ref m) = cfg.mode {
        lines.push(format!("// Mode: {m}"));
    }
    if let Some(ref p) = cfg.preset_name {
        lines.push(format!("// Preset: {p}"));
    }
    lines.push(format!("// Date: {now}"));
    if !cfg.description.is_empty() {
        lines.push(format!("// {}", cfg.description));
    }
    lines.push("// ================================================================".into());
    lines.push(String::new());

    lines.extend(console_banner(cfg));
    lines.push(String::new());

    let categorized = categorize_settings(catalog, &cfg.settings);

    let category_labels: HashMap<&str, &str> = [
        ("video", "VIDEO"),
        ("audio", "AUDIO"),
        ("input", "MOUSE / INPUT"),
        ("network", "NETWORK"),
        ("gameplay", "GAMEPLAY / HUD"),
        ("demo", "DEMO"),
        ("other", "OTHER"),
    ]
    .into_iter()
    .collect();

    for cat_key in CAT_ORDER {
        let cat_settings = match categorized.get(*cat_key) {
            Some(s) if !s.is_empty() => s,
            _ => continue,
        };
        let label_owned = category_labels
            .get(cat_key)
            .map(|s| (*s).to_string())
            .unwrap_or_else(|| cat_key.to_uppercase());
        lines.push(format!("// === {label_owned} ==="));
        for (cvar, value) in cat_settings {
            lines.push(fmt_cvar_line(catalog, cvar, value, 40));
        }
        lines.push(String::new());
    }

    // Категории вне списка (если появятся новые секции в cvars.json)
    let mut extra: Vec<_> = categorized
        .keys()
        .filter(|k| !CAT_ORDER.contains(&k.as_str()))
        .cloned()
        .collect();
    extra.sort();
    for cat_key in extra {
        let cat_settings = &categorized[&cat_key];
        if cat_settings.is_empty() {
            continue;
        }
        lines.push(format!("// === {} ===", cat_key.to_uppercase()));
        for (cvar, value) in cat_settings {
            lines.push(fmt_cvar_line(catalog, cvar, value, 40));
        }
        lines.push(String::new());
    }

    let aliases_txt = generate_aliases_cfg(cfg)?;
    if !aliases_txt.is_empty() {
        lines.push("// === ALIASES (same as config/aliases.cfg in modular export) ===".into());
        lines.push(aliases_txt);
        lines.push(String::new());
    }

    if !cfg.binds.is_empty() {
        lines.push("// === BINDS ===".into());
        let mut keys: Vec<_> = cfg.binds.keys().cloned().collect();
        keys.sort();
        for key in keys {
            let cmd = &cfg.binds[&key];
            lines.push(format!(r#"bind "{key}" "{cmd}""#));
        }
        lines.push(String::new());
    }

    if !cfg.buy_binds.is_empty() {
        lines.push("// === BUY BINDS ===".into());
        let mut keys: Vec<_> = cfg.buy_binds.keys().cloned().collect();
        keys.sort();
        for key in keys {
            let cmd = &cfg.buy_binds[&key];
            lines.push(format!(r#"bind "{key}" "{cmd}""#));
        }
        lines.push(String::new());
    }

    Ok(lines.join("\n"))
}
