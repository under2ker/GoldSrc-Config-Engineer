//! Путь к игре и выкладка файлов на диск (без отправки в консоль — заготовка).

use std::path::Path;

use goldsr_cfg_core::ModularFile;
use serde::Serialize;

#[derive(Debug, Serialize)]
pub struct GameDetectResult {
    pub path: Option<String>,
    pub hint: String,
}

#[tauri::command]
pub fn detect_game_installation() -> GameDetectResult {
    #[cfg(windows)]
    {
        let candidates = [
            r"C:\Program Files (x86)\Steam\steamapps\common\Half-Life",
            r"C:\Program Files\Steam\steamapps\common\Half-Life",
        ];
        for c in candidates {
            let base = Path::new(c);
            if base.join("hl.exe").is_file() && base.join("cstrike").is_dir() {
                return GameDetectResult {
                    path: Some(c.to_string()),
                    hint: "Найдена установка Steam Half-Life.".into(),
                };
            }
        }
    }
    GameDetectResult {
        path: None,
        hint: "Авто-поиск не нашёл hl.exe. Укажите папку с игрой вручную.".into(),
    }
}

#[tauri::command]
pub fn deploy_modular_files(target_dir: String, files: Vec<ModularFile>) -> Result<(), String> {
    let base = Path::new(&target_dir);
    if !base.is_absolute() {
        return Err("Путь должен быть абсолютным.".into());
    }
    for f in files {
        let path = base.join(&f.relative_path);
        if let Some(parent) = path.parent() {
            std::fs::create_dir_all(parent).map_err(|e| e.to_string())?;
        }
        std::fs::write(&path, f.content.as_bytes()).map_err(|e| e.to_string())?;
    }
    Ok(())
}

#[tauri::command]
pub fn execute_console_command_stub() -> Result<(), String> {
    Err("Отправка команд в консоль игры пока не реализована.".into())
}
