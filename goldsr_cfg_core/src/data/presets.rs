use serde::Deserialize;

use crate::data::overlay;
use crate::ProPresetSummary;

pub(crate) const PRESETS_JSON_STR: &str = include_str!(concat!(
    env!("CARGO_MANIFEST_DIR"),
    "/../data/presets.json"
));

#[derive(Deserialize)]
struct PresetEntry {
    name: String,
    team: String,
    role: String,
}

/// Краткий список про-пресетов из `data/presets.json`.
pub fn list_pro_preset_summaries() -> Result<Vec<ProPresetSummary>, String> {
    let raw = overlay::resolve_json("presets.json", PRESETS_JSON_STR);
    let map: std::collections::HashMap<String, PresetEntry> =
        serde_json::from_str(&raw).map_err(|e| e.to_string())?;
    let mut out: Vec<ProPresetSummary> = map
        .into_iter()
        .map(|(id, e)| ProPresetSummary {
            id,
            name: e.name,
            team: e.team,
            role: e.role,
        })
        .collect();
    out.sort_by(|a, b| a.name.cmp(&b.name));
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::list_pro_preset_summaries;

    #[test]
    fn presets_catalog_non_empty() {
        let presets = list_pro_preset_summaries().expect("parse presets.json");
        assert!(!presets.is_empty(), "presets.json must list at least one preset");
        assert!(
            presets.iter().all(|p| !p.id.is_empty()),
            "every preset must have a non-empty id"
        );
    }
}
