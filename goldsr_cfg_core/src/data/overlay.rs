//! Переопределение содержимого `data/*.json` в рантайме (например после синхронизации с GitHub).

use std::collections::HashMap;
use std::sync::{LazyLock, RwLock};

/// Имена файлов каталога (корень репозитория `data/`).
pub const CATALOG_JSON_FILES: &[&str] = &[
    "modes.json",
    "presets.json",
    "aliases.json",
    "cvars.json",
    "buyscripts.json",
];

static OVERRIDES: LazyLock<RwLock<HashMap<String, String>>> =
    LazyLock::new(|| RwLock::new(HashMap::new()));

/// Подставить JSON из оверлея или встроенную строку.
pub fn resolve_json(file: &str, builtin: &str) -> String {
    let g = OVERRIDES.read().expect("data overlay lock");
    g.get(file)
        .cloned()
        .unwrap_or_else(|| builtin.to_string())
}

/// Заменить набор оверлеев (полная замена карты).
pub fn set_overrides(files: HashMap<String, String>) {
    let mut g = OVERRIDES.write().expect("data overlay lock");
    *g = files;
}

/// Сбросить оверлеи — снова используются только встроенные данные.
pub fn clear_overrides() {
    let mut g = OVERRIDES.write().expect("data overlay lock");
    g.clear();
}
