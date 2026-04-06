//! Каталог алиасов из `data/aliases.json` и генерация `config/aliases.cfg` (как в Python `generate_aliases_cfg`).

use chrono::Local;
use serde::Deserialize;
use serde_json::Value;

use crate::cfg_config::CfgConfig;

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

/// Список всех алиасов для UI (фильтр по режиму: KZ/Surf/practice — помечаем, но отдаём всё).
pub fn list_alias_catalog_json() -> Result<Vec<AliasCatalogItem>, String> {
    let root: Value = serde_json::from_str(ALIASES_JSON_STR).map_err(|e| e.to_string())?;
    let obj = root.as_object().ok_or("aliases.json: root must be object")?;
    let mut out = Vec::new();
    for (sec_key, sec_val) in obj {
        if sec_key.starts_with('_') {
            continue;
        }
        let aliases = sec_val
            .get("aliases")
            .and_then(|a| a.as_array())
            .cloned()
            .unwrap_or_default();
        let label = section_label_ru(sec_key);
        for a in aliases {
            let name = a.get("name").and_then(|v| v.as_str()).unwrap_or("").to_string();
            if name.is_empty() {
                continue;
            }
            let description = a
                .get("description")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string();
            let safety = a
                .get("safety")
                .and_then(|v| v.as_str())
                .unwrap_or("SAFE")
                .to_string();
            let required = a.get("required").and_then(|v| v.as_bool()).unwrap_or(false);
            out.push(AliasCatalogItem {
                section: sec_key.clone(),
                section_label: label.clone(),
                name,
                description,
                safety,
                required,
            });
        }
    }
    Ok(out)
}

fn emit_one_alias(
    cfg: &CfgConfig,
    sec_key: &str,
    a: &Value,
    lines: &mut Vec<String>,
) -> Result<(), String> {
    let safety = a
        .get("safety")
        .and_then(|v| v.as_str())
        .unwrap_or("SAFE");
    let desc = a
        .get("description")
        .and_then(|v| v.as_str())
        .unwrap_or("");
    let marker = format!("[{safety}]");
    let name = a
        .get("name")
        .and_then(|v| v.as_str())
        .ok_or("alias without name")?;
    let required = a.get("required").and_then(|v| v.as_bool()).unwrap_or(false);
    if !section_active(cfg, sec_key) {
        return Ok(());
    }
    if !include_alias_named(cfg, sec_key, name, required) {
        return Ok(());
    }

    if let Some(plus) = a.get("plus").and_then(|v| v.as_str()) {
        let minus = a.get("minus").and_then(|v| v.as_str()).unwrap_or("");
        lines.push(pad_comment(
            &format!(r#"alias "{name}" "{plus}""#),
            50,
            &format!("{marker} {desc} (нажатие)"),
        ));
        let minus_name = if let Some(rest) = name.strip_prefix('+') {
            format!("-{rest}")
        } else {
            name.replace('+', "-")
        };
        lines.push(pad_comment(
            &format!(r#"alias "{minus_name}" "{minus}""#),
            50,
            &format!("{marker} {desc} (отпускание)"),
        ));
    } else if a.get("type").and_then(|v| v.as_str()) == Some("cycle") {
        let states = a.get("states").and_then(|v| v.as_array()).cloned().unwrap_or_default();
        lines.push(format!("// {desc}"));
        for st in &states {
            let st_name = st.get("name").and_then(|v| v.as_str()).unwrap_or("");
            let cmd = st.get("command").and_then(|v| v.as_str()).unwrap_or("");
            let next = st.get("next").and_then(|v| v.as_str()).unwrap_or("");
            lines.push(pad_comment(
                &format!(r#"alias "{st_name}" "{cmd}; alias {name} {next}""#),
                50,
                &marker,
            ));
        }
        if let Some(first) = states.first() {
            let init = first.get("name").and_then(|v| v.as_str()).unwrap_or("");
            lines.push(pad_comment(
                &format!(r#"alias "{name}" "{init}""#),
                50,
                &format!("{marker} init"),
            ));
        }
    } else if a.get("type").and_then(|v| v.as_str()) == Some("toggle") {
        let on_cmd = a
            .get("on")
            .and_then(|o| o.get("command"))
            .and_then(|v| v.as_str())
            .unwrap_or("");
        let off_cmd = a
            .get("off")
            .and_then(|o| o.get("command"))
            .and_then(|v| v.as_str())
            .unwrap_or("");
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
    } else if a.get("type").and_then(|v| v.as_str()) == Some("kz_chain") {
        let cid = a
            .get("chain_id")
            .and_then(|v| v.as_str())
            .filter(|s| !s.is_empty())
            .unwrap_or(name);
        let steps = a.get("steps").and_then(|v| v.as_array()).cloned().unwrap_or_default();
        lines.push(format!("// {desc}"));
        lines.push(format!(
            "// KZ chain: bind \"KEY\" \"{cid}_go\" — one press per step ({} steps)",
            steps.len()
        ));
        for (i, step) in steps.iter().enumerate() {
            let cmd = step.as_str().unwrap_or("");
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
    } else {
        let cmd = a.get("command").and_then(|v| v.as_str()).unwrap_or("");
        lines.push(pad_comment(
            &format!(r#"alias "{name}" "{cmd}""#),
            50,
            &format!("{marker} {desc}"),
        ));
    }

    lines.push(String::new());
    Ok(())
}

/// Текст `aliases.cfg` (пустая строка, если не выбран ни один алиас).
pub fn generate_aliases_cfg(cfg: &CfgConfig) -> Result<String, String> {
    let root: Value = serde_json::from_str(ALIASES_JSON_STR).map_err(|e| e.to_string())?;
    let obj = root.as_object().ok_or("aliases.json: root must be object")?;

    let mut section_order: Vec<(&str, &str)> = vec![
        ("movement", "MOVEMENT ALIASES"),
        ("weapon", "WEAPON ALIASES"),
        ("communication", "COMMUNICATION ALIASES"),
        ("utility", "UTILITY ALIASES"),
    ];

    match cfg.mode_key.as_deref() {
        Some("kz") => section_order.push(("kz_specific", "KZ-SPECIFIC ALIASES")),
        Some("surf") => section_order.push(("surf_specific", "SURF-SPECIFIC ALIASES")),
        _ => {}
    }
    if cfg.include_practice {
        section_order.push(("practice", "PRACTICE MODE (sv_cheats 1)"));
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
    for (sec_key, sec_label) in section_order {
        if !section_active(cfg, sec_key) {
            continue;
        }
        let sec_val = match obj.get(sec_key) {
            Some(v) => v,
            None => continue,
        };
        let alias_list = sec_val
            .get("aliases")
            .and_then(|a| a.as_array())
            .cloned()
            .unwrap_or_default();
        if alias_list.is_empty() {
            continue;
        }

        let mut sec_lines: Vec<String> = Vec::new();
        for a in &alias_list {
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
