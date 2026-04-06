//! Валидация CVAR (расширение: диапазоны из cvars.json).

use std::collections::HashMap;

use crate::data::cvars::CvarsCatalog;

/// Проверка, что все ключи известны каталогу (строгий режим).
pub fn validate_settings_keys(settings: &HashMap<String, String>, strict: bool) -> Result<(), String> {
    if !strict {
        return Ok(());
    }
    let cat = CvarsCatalog::global();
    for key in settings.keys() {
        if !cat.is_known_cvar(key) {
            return Err(format!("Неизвестный CVAR: {key}"));
        }
    }
    Ok(())
}
