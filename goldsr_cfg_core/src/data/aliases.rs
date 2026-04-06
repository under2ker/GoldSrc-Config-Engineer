//! Каталог алиасов из `data/aliases.json` и генерация `config/aliases.cfg` (как в Python `generate_aliases_cfg`).

use chrono::Local;
use serde::Deserialize;
use serde_json::Value;

use crate::cfg_config::CfgConfig;
use crate::data::overlay;

pub(crate) const ALIASES_JSON_STR: &str = include_str!(concat!(
    env!("CARGO_MANIFEST_DIR"),
    "/../data/aliases.json"
));

#[derive(Debug, Clone, Deserialize, serde::Serialize)]
pub struct AliasCatalogItem {
    pub section: String,
    pub section_label: String,
    pub name: String,
    pub description: String,
    pub safety: String,
    pub required: bool,
}

#[derive(Debug, Clone, Deserialize)]
struct AliasSection {
    #[serde(rename = "_section_comment", default)]
    _section_comment: Option<String>,
    aliases: Vec<AliasDef>,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(untagged)]
enum AliasDef {
    PlusMinus(PlusMinusAlias),
    Tagged(TaggedAlias),
    Plain(PlainAlias),
}

#[derive(Debug, Clone, Deserialize)]
struct PlusMinusAlias {
    name: String,
    plus: String,
    minus: String,
    #[serde(default)]
    description: String,
    #[serde(default = "default_safety")]
    safety: String,
    #[serde(default)]
    required: bool,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(tag = "type", rename_all = "snake_case")]
enum TaggedAlias {
    Cycle {
        name: String,
        states: Vec<CycleState>,
        #[serde(default)]
        description: String,
        #[serde(default = "default_safety")]
        safety: String,
        #[serde(default)]
        required: bool,
    },
    Toggle {
        name: String,
        on: ToggleSide,
        off: ToggleSide,
        #[serde(default)]
        description: String,
        #[serde(default = "default_safety")]
        safety: String,
        #[serde(default)]
        required: bool,
    },
    KzChain {
        name: String,
        #[serde(default)]
        chain_id: Option<String>,
        steps: Vec<String>,
        #[serde(default)]
        description: String,
        #[serde(default = "default_safety")]
        safety: String,
        #[serde(default)]
        required: bool,
    },
    Simple {
        name: String,
        command: String,
        #[serde(default)]
        description: String,
        #[serde(default = "default_safety")]
        safety: String,
        #[serde(default)]
        required: bool,
    },
}

#[derive(Debug, Clone, Deserialize)]
struct ToggleSide {
    command: String,
}

#[derive(Debug, Clone, Deserialize)]
struct CycleState {
    name: String,
    command: String,
    next: String,
}

#[derive(Debug, Clone, Deserialize)]
struct PlainAlias {
    name: String,
    command: String,
    #[serde(default)]
    description: String,
    #[serde(default = "default_safety")]
    safety: String,
    #[serde(default)]
    required: bool,
}

fn default_safety() -> String {
    "SAFE".into()
}

fn section_label_ru(key: &str) -> String {
    match key {
        "movement" => "Движение".into(),
        "weapon" => "Оружие".into(),
        "communication" => "Коммуникация".into(),
        "utility" => "Утилиты".into(),
        "practice" => "Практика (sv_cheats)".into(),
        "kz_specific" => "KZ / climb".into(),
        "surf_specific" => "Surf".into(),
        _ => key.to_string(),
    }
}

fn section_active(cfg: &CfgConfig, sec_key: &str) -> bool {
    match sec_key {
        "kz_specific" => cfg.mode_key.as_deref() == Some("kz"),
        "surf_specific" => cfg.mode_key.as_deref() == Some("surf"),
        "practice" => cfg.include_practice,
        _ => true,
    }
}

fn alias_key(sec_key: &str, name: &str) -> String {
    format!("{sec_key}:{name}")
}

fn include_alias_named(cfg: &CfgConfig, sec_key: &str, name: &str, required: bool) -> bool {
    match cfg.alias_preset.as_str() {
        "minimal" => required,
        "full" => true,
        "custom" => *cfg.alias_enabled.get(&alias_key(sec_key, name)).unwrap_or(&false),
        _ => required,
    }
}

fn pad_comment(base: &str, col: usize, comment: &str) -> String {
    let n = base.chars().count();
    let pad = col.saturating_sub(n).max(1);
    format!("{}{}// {}", base, " ".repeat(pad), comment)
}

fn load_sections(raw: &str) -> Result<Vec<(String, AliasSection)>, String> {
    let root: Value = serde_json::from_str(raw).map_err(|e| e.to_string())?;
    let obj = root.as_object().ok_or("aliases.json: root must be object")?;
    let mut out = Vec::new();
    for (sec_key, sec_val) in obj {
        if sec_key.starts_with('_') {
            continue;
        }
        let sec: AliasSection =
            serde_json::from_value(sec_val.clone()).map_err(|e| format!("section {sec_key}: {e}"))?;
        out.push((sec_key.clone(), sec));
    }
    Ok(out)
}

/// Список всех алиасов для UI (фильтр по режиму: KZ/Surf/practice — помечаем, но отдаём всё).
pub fn list_alias_catalog_json() -> Result<Vec<AliasCatalogItem>, String> {
    let raw = overlay::resolve_json("aliases.json", ALIASES_JSON_STR);
    let sections = load_sections(&raw)?;
    let mut out = Vec::new();
    for (sec_key, sec) in sections {
        let label = section_label_ru(&sec_key);
        for a in sec.aliases {
            catalog_push_item(&sec_key, &label, &a, &mut out);
        }
    }
    Ok(out)
}

fn catalog_push_item(sec_key: &str, label: &str, a: &AliasDef, out: &mut Vec<AliasCatalogItem>) {
    let (name, description, safety, required) = match a {
        AliasDef::PlusMinus(p) => (
            p.name.clone(),
            p.description.clone(),
            p.safety.clone(),
            p.required,
        ),
        AliasDef::Tagged(tagged) => match tagged {
            TaggedAlias::Cycle {
                name,
                description,
                safety,
                required,
                ..
            } => (
                name.clone(),
                description.clone(),
                safety.clone(),
                *required,
            ),
            TaggedAlias::Toggle {
                name,
                description,
                safety,
                required,
                ..
            } => (
                name.clone(),
                description.clone(),
                safety.clone(),
                *required,
            ),
            TaggedAlias::KzChain {
                name,
                description,
                safety,
                required,
                ..
            } => (
                name.clone(),
                description.clone(),
                safety.clone(),
                *required,
            ),
            TaggedAlias::Simple {
                name,
                description,
                safety,
                required,
                ..
            } => (
                name.clone(),
                description.clone(),
                safety.clone(),
                *required,
            ),
        },
        AliasDef::Plain(p) => (
            p.name.clone(),
            p.description.clone(),
            p.safety.clone(),
            p.required,
        ),
    };
    if name.is_empty() {
        return;
    }
    out.push(AliasCatalogItem {
        section: sec_key.to_string(),
        section_label: label.to_string(),
        name,
        description,
        safety,
        required,
    });
}

fn emit_one_alias(
    cfg: &CfgConfig,
    sec_key: &str,
    a: &AliasDef,
    lines: &mut Vec<String>,
) -> Result<(), String> {
    match a {
        AliasDef::PlusMinus(p) => {
            let safety = p.safety.as_str();
            let desc = p.description.as_str();
            let marker = format!("[{safety}]");
            let name = p.name.as_str();
            let required = p.required;
            if !section_active(cfg, sec_key) {
                return Ok(());
            }
            if !include_alias_named(cfg, sec_key, name, required) {
                return Ok(());
            }
            lines.push(pad_comment(
                &format!(r#"alias "{name}" "{}""#, p.plus),
                50,
                &format!("{marker} {desc} (нажатие)"),
            ));
            let minus_name = if let Some(rest) = name.strip_prefix('+') {
                format!("-{rest}")
            } else {
                name.replace('+', "-")
            };
            lines.push(pad_comment(
                &format!(r#"alias "{minus_name}" "{}""#, p.minus),
                50,
                &format!("{marker} {desc} (отпускание)"),
            ));
            lines.push(String::new());
            Ok(())
        }
        AliasDef::Tagged(TaggedAlias::Cycle {
            name,
            states,
            description,
            safety,
            required,
        }) => {
            let safety = safety.as_str();
            let desc = description.as_str();
            let marker = format!("[{safety}]");
            let name = name.as_str();
            let required = *required;
            if !section_active(cfg, sec_key) {
                return Ok(());
            }
            if !include_alias_named(cfg, sec_key, name, required) {
                return Ok(());
            }
            lines.push(format!("// {desc}"));
            for st in states {
                let st_name = st.name.as_str();
                let cmd = st.command.as_str();
                let next = st.next.as_str();
                lines.push(pad_comment(
                    &format!(r#"alias "{st_name}" "{cmd}; alias {name} {next}""#),
                    50,
                    &marker,
                ));
            }
            if let Some(first) = states.first() {
                let init = first.name.as_str();
                lines.push(pad_comment(
                    &format!(r#"alias "{name}" "{init}""#),
                    50,
                    &format!("{marker} init"),
                ));
            }
            lines.push(String::new());
            Ok(())
        }
        AliasDef::Tagged(TaggedAlias::Toggle {
            name,
            on,
            off,
            description,
            safety,
            required,
        }) => {
            let safety = safety.as_str();
            let desc = description.as_str();
            let marker = format!("[{safety}]");
            let name = name.as_str();
            let required = *required;
            let on_cmd = on.command.as_str();
            let off_cmd = off.command.as_str();
            if !section_active(cfg, sec_key) {
                return Ok(());
            }
            if !include_alias_named(cfg, sec_key, name, required) {
                return Ok(());
            }
            let on_name = format!("{name}_on");
            let off_name = format!("{name}_off");
            lines.push(format!("// {desc}"));
            lines.push(pad_comment(
                &format!(r#"alias "{on_name}" "{on_cmd}; alias {name} {off_name}""#),
                50,
                &marker,
            ));
            lines.push(pad_comment(
                &format!(r#"alias "{off_name}" "{off_cmd}; alias {name} {on_name}""#),
                50,
                &marker,
            ));
            lines.push(pad_comment(
                &format!(r#"alias "{name}" "{on_name}""#),
                50,
                &format!("{marker} init"),
            ));
            lines.push(String::new());
            Ok(())
        }
        AliasDef::Tagged(TaggedAlias::KzChain {
            name,
            chain_id,
            steps,
            description,
            safety,
            required,
        }) => {
            let safety = safety.as_str();
            let desc = description.as_str();
            let marker = format!("[{safety}]");
            let name = name.as_str();
            let required = *required;
            if !section_active(cfg, sec_key) {
                return Ok(());
            }
            if !include_alias_named(cfg, sec_key, name, required) {
                return Ok(());
            }
            let cid = chain_id
                .as_deref()
                .filter(|s| !s.is_empty())
                .unwrap_or(name);
            let steps = steps.as_slice();
            lines.push(format!("// {desc}"));
            lines.push(format!(
                "// KZ chain: bind \"KEY\" \"{cid}_go\" — one press per step ({} steps)",
                steps.len()
            ));
            for (i, step) in steps.iter().enumerate() {
                let cmd = step.as_str();
                let cur = format!("{cid}_{}", i + 1);
                let nxt = if i + 1 < steps.len() {
                    format!("{}_{}", cid, i + 2)
                } else {
                    format!("{cid}_1")
                };
                lines.push(pad_comment(
                    &format!(r#"alias "{cur}" "{cmd}; alias {cid}_go {nxt}""#),
                    50,
                    &marker,
                ));
            }
            lines.push(pad_comment(
                &format!(r#"alias "{cid}_go" "{cid}_1""#),
                50,
                &format!("{marker} entry"),
            ));
            lines.push(String::new());
            Ok(())
        }
        AliasDef::Tagged(TaggedAlias::Simple {
            name,
            command,
            description,
            safety,
            required,
        }) => {
            let safety = safety.as_str();
            let desc = description.as_str();
            let marker = format!("[{safety}]");
            let name = name.as_str();
            let cmd = command.as_str();
            let required = *required;
            if !section_active(cfg, sec_key) {
                return Ok(());
            }
            if !include_alias_named(cfg, sec_key, name, required) {
                return Ok(());
            }
            lines.push(pad_comment(
                &format!(r#"alias "{name}" "{cmd}""#),
                50,
                &format!("{marker} {desc}"),
            ));
            lines.push(String::new());
            Ok(())
        }
        AliasDef::Plain(p) => {
            let safety = p.safety.as_str();
            let desc = p.description.as_str();
            let marker = format!("[{safety}]");
            let name = p.name.as_str();
            let cmd = p.command.as_str();
            let required = p.required;
            if !section_active(cfg, sec_key) {
                return Ok(());
            }
            if !include_alias_named(cfg, sec_key, name, required) {
                return Ok(());
            }
            lines.push(pad_comment(
                &format!(r#"alias "{name}" "{cmd}""#),
                50,
                &format!("{marker} {desc}"),
            ));
            lines.push(String::new());
            Ok(())
        }
    }
}

/// Текст `aliases.cfg` (пустая строка, если не выбран ни один алиас).
pub fn generate_aliases_cfg(cfg: &CfgConfig) -> Result<String, String> {
    let raw = overlay::resolve_json("aliases.json", ALIASES_JSON_STR);
    let sections: Vec<(String, AliasSection)> = load_sections(&raw)?;
    let by_key: std::collections::HashMap<String, &AliasSection> =
        sections.iter().map(|(k, v)| (k.clone(), v)).collect();

    let section_order: Vec<(&str, &str)> = vec![
        ("movement", "MOVEMENT ALIASES"),
        ("weapon", "WEAPON ALIASES"),
        ("communication", "COMMUNICATION ALIASES"),
        ("utility", "UTILITY ALIASES"),
    ];

    let mut order: Vec<(&str, &str)> = section_order;
    match cfg.mode_key.as_deref() {
        Some("kz") => order.push(("kz_specific", "KZ-SPECIFIC ALIASES")),
        Some("surf") => order.push(("surf_specific", "SURF-SPECIFIC ALIASES")),
        _ => {}
    }
    if cfg.include_practice {
        order.push(("practice", "PRACTICE MODE (sv_cheats 1)"));
    }

    let now = Local::now().format("%Y-%m-%d %H:%M").to_string();
    let mut lines: Vec<String> = vec![
        "// ================================================================".to_string(),
        "// ALIASES.CFG — All script aliases".to_string(),
        "// Generated by GoldSrc Config Engineer v3.0".to_string(),
        format!("// Date: {now}"),
        "// ================================================================".to_string(),
        String::new(),
    ];

    let mut any = false;
    for (sec_key, sec_label) in order {
        if !section_active(cfg, sec_key) {
            continue;
        }
        let sec_val = match by_key.get(sec_key) {
            Some(v) => *v,
            None => continue,
        };
        let alias_list = &sec_val.aliases;
        if alias_list.is_empty() {
            continue;
        }

        let mut sec_lines: Vec<String> = Vec::new();
        for a in alias_list {
            let mut chunk = Vec::new();
            emit_one_alias(cfg, sec_key, a, &mut chunk)?;
            if chunk.iter().any(|l| l.starts_with("alias ")) {
                sec_lines.extend(chunk);
                any = true;
            }
        }
        if sec_lines.is_empty() {
            continue;
        }

        lines.push("// --------------------------------".to_string());
        lines.push(format!("// {sec_label}"));
        lines.push("// --------------------------------".to_string());
        lines.push(String::new());
        lines.extend(sec_lines);
    }

    if !any {
        return Ok(String::new());
    }

    Ok(lines.join("\n"))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn catalog_non_empty() {
        let v = list_alias_catalog_json().unwrap();
        assert!(v.len() >= 65, "expected catalog from aliases.json, got {}", v.len());
    }

    #[test]
    fn minimal_generates() {
        let mut cfg = CfgConfig::default();
        cfg.mode_key = Some("classic".into());
        cfg.alias_preset = "minimal".into();
        cfg.include_practice = false;
        let s = generate_aliases_cfg(&cfg).unwrap();
        assert!(s.contains("alias \"+duckjump\""));
        assert!(!s.contains("prac_on"));
    }

    #[test]
    fn full_includes_more() {
        let mut cfg = CfgConfig::default();
        cfg.mode_key = Some("classic".into());
        cfg.alias_preset = "full".into();
        let s = generate_aliases_cfg(&cfg).unwrap();
        assert!(s.len() > 5000);
    }
}
