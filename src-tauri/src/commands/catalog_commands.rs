//! Синхронизация каталогов `data/*.json` с GitHub.

use tauri::AppHandle;

use crate::catalog_sync::{apply_local_catalog, sync_and_apply, CatalogSyncReport};

#[tauri::command]
pub fn catalog_sync_now(app: AppHandle) -> Result<CatalogSyncReport, String> {
    sync_and_apply(&app)
}

#[tauri::command]
pub fn catalog_reload_local(app: AppHandle) -> Result<(), String> {
    apply_local_catalog(&app)
}
