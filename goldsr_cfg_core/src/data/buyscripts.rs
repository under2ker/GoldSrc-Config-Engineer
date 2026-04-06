//! Справочник покупок: `config/buyscripts.cfg` из `data/buyscripts.json` (как в v2).

use chrono::Local;

/// Собрать содержимое `config/buyscripts.cfg` (алиасы `buy_*` и опционально дефолтные бинды на нумпад).
pub fn generate_buyscripts_cfg() -> Result<String, String> {
    const RAW: &str = include_str!(concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/../data/buyscripts.json"
    ));
    let v: serde_json::Value = serde_json::from_str(RAW).map_err(|e| e.to_string())?;
    let now = Local::now().format("%Y-%m-%d %H:%M").to_string();

    let mut lines: Vec<String> = vec![
        "// config/buyscripts.cfg — справочник покупок (data/buyscripts.json)".to_string(),
        format!("// {now}"),
        "// Привяжите клавиши в buy_binds или используйте алиасы в консоли.".to_string(),
        String::new(),
    ];

    if let Some(weapons) = v.get("weapons").and_then(|x| x.as_object()) {
        lines.push("// === WEAPONS ===".to_string());
        for (_cat, items) in weapons {
            let Some(obj) = items.as_object() else { continue };
            let mut keys: Vec<_> = obj.keys().cloned().collect();
            keys.sort();
            for key in keys {
                let Some(item) = obj.get(&key) else { continue };
                let Some(cmd) = item.get("command").and_then(|x| x.as_str()) else {
                    continue;
                };
                let alias = format!("buy_{}", key);
                push_alias(&mut lines, &alias, cmd);
            }
        }
        lines.push(String::new());
    }

    if let Some(equip) = v.get("equipment").and_then(|x| x.as_object()) {
        lines.push("// === EQUIPMENT ===".to_string());
        let mut keys: Vec<_> = equip.keys().cloned().collect();
        keys.sort();
        for key in keys {
            let Some(item) = equip.get(&key) else { continue };
            let Some(cmd) = item.get("command").and_then(|x| x.as_str()) else {
                continue;
            };
            let alias = format!("buy_{}", key);
            push_alias(&mut lines, &alias, cmd);
        }
        lines.push(String::new());
    }

    if let Some(presets) = v.get("presets").and_then(|x| x.as_object()) {
        lines.push("// === PRESET MACROS ===".to_string());
        let mut keys: Vec<_> = presets.keys().cloned().collect();
        keys.sort();
        for key in keys {
            let Some(item) = presets.get(&key) else { continue };
            let Some(cmd) = item.get("commands").and_then(|x| x.as_str()) else {
                continue;
            };
            push_alias(&mut lines, key.as_str(), cmd);
        }
        lines.push(String::new());
    }

    if let Some(db) = v.get("default_binds").and_then(|x| x.as_object()) {
        lines.push("// === DEFAULT NUMPAD (можно отключить, удалив блок) ===".to_string());
        let mut keys: Vec<_> = db.keys().cloned().collect();
        keys.sort();
        for k in keys {
            let Some(alias_cmd) = db.get(&k).and_then(|x| x.as_str()) else {
                continue;
            };
            lines.push(format!(r#"bind "{}" "{}""#, k, alias_cmd));
        }
    }

    Ok(lines.join("\n"))
}

fn push_alias(lines: &mut Vec<String>, name: &str, cmd: &str) {
    let safe = cmd.replace('"', "'");
    lines.push(format!(r#"alias {} "{}""#, name, safe));
}

#[cfg(test)]
mod tests {
    use super::generate_buyscripts_cfg;

    #[test]
    fn buyscripts_cfg_contains_weapon_and_preset_aliases() {
        let s = generate_buyscripts_cfg().expect("buyscripts");
        assert!(s.contains("WEAPONS"));
        assert!(s.contains("alias buy_"));
        assert!(s.contains("PRESET MACROS"));
    }
}
