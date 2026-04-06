use serde::Deserialize;

use crate::GameModeSummary;

pub(crate) const MODES_JSON_STR: &str = include_str!(concat!(
    env!("CARGO_MANIFEST_DIR"),
    "/../data/modes.json"
));

#[derive(Deserialize)]
struct ModeEntry {
    name_en: String,
    name_ru: String,
}

/// Список игровых режимов из `data/modes.json` (ключ → id).
pub fn list_mode_summaries() -> Result<Vec<GameModeSummary>, String> {
    let map: std::collections::HashMap<String, ModeEntry> =
        serde_json::from_str(MODES_JSON_STR).map_err(|e| e.to_string())?;
    let mut out: Vec<GameModeSummary> = map
        .into_iter()
        .map(|(id, e)| GameModeSummary {
            id,
            name_en: e.name_en,
            name_ru: e.name_ru,
        })
        .collect();
    out.sort_by(|a, b| a.id.cmp(&b.id));
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::list_mode_summaries;

    #[test]
    fn modes_catalog_non_empty() {
        let modes = list_mode_summaries().expect("parse modes.json");
        assert!(!modes.is_empty(), "modes.json must list at least one mode");
        assert!(
            modes.iter().all(|m| !m.id.is_empty()),
            "every mode must have a non-empty id"
        );
    }
}
