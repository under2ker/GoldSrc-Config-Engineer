//! Безопасность импорта .cfg (порт логики `check_dangerous` из Python) и разбор текста в `CfgConfig`.

use regex::Regex;
use std::sync::OnceLock;

use crate::cfg_config::CfgConfig;

const DANGEROUS_COMMANDS: &[&str] = &[
    "exec",
    "download",
    "upload",
    "rcon",
    "rcon_password",
    "sv_cheats",
    "sv_password",
    "connect",
    "retry",
    "quit",
    "exit",
    "kill",
    "kickall",
    "ban",
    "banid",
    "removeid",
    "writecfg",
    "developer",
    "alias",
    "cl_filterstuffcmd",
];

fn is_dangerous(word: &str) -> bool {
    DANGEROUS_COMMANDS
        .iter()
        .any(|d| word.eq_ignore_ascii_case(d))
}

fn line_starts_as_comment(line: &str) -> bool {
    let t = line.trim_start();
    t.starts_with("//")
}

/// Быстрый скан опасных команд; непустой список — импорт следует блокировать или показать предупреждение.
pub fn check_dangerous(cfg_text: &str) -> Vec<String> {
    let mut warnings = Vec::new();
    for (line_num, raw) in cfg_text.lines().enumerate() {
        let line = raw.trim();
        if line.is_empty() || line_starts_as_comment(line) {
            continue;
        }
        let first_word = line
            .split_whitespace()
            .next()
            .unwrap_or("")
            .trim_matches('"')
            .to_lowercase();

        if is_dangerous(&first_word) {
            warnings.push(format!(
                "Строка {}: опасная команда «{}»",
                line_num + 1,
                first_word
            ));
        }

        if first_word == "bind" {
            let parts: Vec<&str> = line.split('"').collect();
            if parts.len() >= 4 {
                let bound_cmd = parts[3]
                    .split(';')
                    .next()
                    .unwrap_or("")
                    .trim()
                    .trim_start_matches('+')
                    .trim_start_matches('-')
                    .to_lowercase();
                if is_dangerous(&bound_cmd) {
                    warnings.push(format!(
                        "Строка {}: опасный bind на «{}»",
                        line_num + 1,
                        bound_cmd
                    ));
                }
            }
        }
    }
    warnings
}

fn bind_line_regex() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| {
        Regex::new(r#"(?i)^bind\s+"([^"]+)"\s+"(.*)"\s*$"#).expect("bind regex")
    })
}

/// Разбор содержимого `.cfg` в структуру настроек (cvar → settings, `bind` → binds). Пропускает `alias`, `exec`, комментарии.
pub fn parse_cfg_text_to_config(text: &str) -> Result<CfgConfig, String> {
    let bind_re = bind_line_regex();
    let mut cfg = CfgConfig::default();

    for raw in text.lines() {
        let line = raw.trim();
        if line.is_empty() || line.starts_with("//") {
            continue;
        }
        let lower = line.to_lowercase();
        if lower.starts_with("bind ") {
            if let Some(cap) = bind_re.captures(line) {
                let key = cap.get(1).map(|m| m.as_str().to_string()).unwrap_or_default();
                let cmd = cap.get(2).map(|m| m.as_str().to_string()).unwrap_or_default();
                if !key.is_empty() {
                    cfg.binds.insert(key, cmd);
                }
            }
            continue;
        }
        if lower.starts_with("alias ") || lower.starts_with("exec ") {
            continue;
        }
        if let Some((k, v)) = parse_cvar_line(line) {
            cfg.set(k, v);
        }
    }

    Ok(cfg)
}

fn parse_cvar_line(line: &str) -> Option<(String, String)> {
    let mut it = line.splitn(2, char::is_whitespace);
    let key = it.next()?.trim();
    if key.is_empty() {
        return None;
    }
    let rest = it.next()?.trim();
    if key.eq_ignore_ascii_case("bind")
        || key.eq_ignore_ascii_case("alias")
        || key.eq_ignore_ascii_case("exec")
    {
        return None;
    }
    let value = if rest.len() >= 2 && rest.starts_with('"') && rest.ends_with('"') {
        rest[1..rest.len() - 1].to_string()
    } else {
        rest.to_string()
    };
    Some((key.to_string(), value))
}
