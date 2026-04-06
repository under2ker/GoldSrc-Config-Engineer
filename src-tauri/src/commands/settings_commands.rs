//! Ключ-значение в `app_settings` (лимит истории и др.).

use tauri::State;

use crate::commands::history_commands::{trim_history_to_limit, HISTORY_MAX_KEY};
use crate::db::{app_setting_get, app_setting_set, AppDb};

#[tauri::command]
pub fn app_settings_get(db: State<'_, AppDb>, key: String) -> Result<Option<String>, String> {
    let conn = db.0.lock().map_err(|e| e.to_string())?;
    app_setting_get(&conn, &key)
}

#[tauri::command]
pub fn app_settings_set(db: State<'_, AppDb>, key: String, value: String) -> Result<(), String> {
    let conn = db.0.lock().map_err(|e| e.to_string())?;
    app_setting_set(&conn, &key, &value)?;
    if key == HISTORY_MAX_KEY {
        trim_history_to_limit(&conn)?;
    }
    Ok(())
}
