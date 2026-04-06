//! Пути к данным приложения (прозрачность для пользователя и поддержки).

use serde::Serialize;
use tauri::{AppHandle, Manager};

#[derive(Debug, Serialize)]
pub struct AppPathsInfo {
    pub app_data_dir: String,
    pub sqlite_db_path: String,
}

/// Каталог данных приложения и путь к файлу SQLite (как в `db.rs`).
#[tauri::command]
pub fn get_app_paths_info(app: AppHandle) -> Result<AppPathsInfo, String> {
    let dir = app.path().app_local_data_dir().map_err(|e| e.to_string())?;
    let _ = std::fs::create_dir_all(&dir);
    let db_path = dir.join("gce_app.sqlite");
    Ok(AppPathsInfo {
        app_data_dir: dir.to_str().ok_or("некорректный путь к данным приложения")?.to_string(),
        sqlite_db_path: db_path
            .to_str()
            .ok_or("некорректный путь к файлу базы")?
            .to_string(),
    })
}
