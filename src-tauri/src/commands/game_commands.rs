//! Путь к игре и выкладка файлов на диск (без отправки в консоль — заготовка).

use std::collections::HashSet;
use std::path::{Path, PathBuf};

use goldsr_cfg_core::ModularFile;
use serde::Serialize;

#[derive(Debug, Serialize)]
pub struct GameDetectResult {
    pub path: Option<String>,
    pub hint: String,
}

/// Типичные хвосты пути от корня диска: Steam в Program Files и отдельная библиотека на `D:\Steam\...`.
#[cfg(windows)]
const STEAM_HL_RELATIVE: &[&str] = &[
    r"Program Files (x86)\Steam\steamapps\common\Half-Life",
    r"Program Files\Steam\steamapps\common\Half-Life",
    r"Steam\steamapps\common\Half-Life",
];

/// Где искать `libraryfolders.vdf` относительно корня диска.
#[cfg(windows)]
const STEAM_LIBRARYFOLDERS_VDF: &[&str] = &[
    r"Program Files (x86)\Steam\config\libraryfolders.vdf",
    r"Program Files\Steam\config\libraryfolders.vdf",
    r"Steam\config\libraryfolders.vdf",
];

#[cfg(windows)]
fn half_life_ok(base: &Path) -> bool {
    base.join("hl.exe").is_file() && base.join("cstrike").is_dir()
}

/// Парсинг путей библиотек Steam из `libraryfolders.vdf` (ключ `"path"` в кавычках).
#[cfg(windows)]
fn steam_library_roots_from_vdf(content: &str) -> Vec<String> {
    let mut out = Vec::new();
    for line in content.lines() {
        let line = line.trim_start();
        if line.starts_with("//") {
            continue;
        }
        let Some(rest) = line.strip_prefix("\"path\"") else {
            continue;
        };
        let rest = rest.trim_start();
        let Some(rest) = rest.strip_prefix('"') else {
            continue;
        };
        let Some(end) = rest.find('"') else {
            continue;
        };
        let raw = &rest[..end];
        if raw.is_empty() {
            continue;
        }
        // В VDF обратные слэши удваиваются: `D:\\Steam` → путь `D:\Steam`
        let normalized = raw.replace("\\\\", "\\");
        out.push(normalized);
    }
    out
}

#[cfg(windows)]
fn unique_vdf_paths() -> Vec<PathBuf> {
    let mut seen = HashSet::new();
    let mut files = Vec::new();
    for letter in 'A'..='Z' {
        let drive_root = format!("{}:\\", letter);
        let root = Path::new(&drive_root);
        if !root.exists() {
            continue;
        }
        for rel in STEAM_LIBRARYFOLDERS_VDF {
            let p = root.join(rel);
            if p.is_file() {
                let key = p.to_string_lossy().to_string();
                if seen.insert(key) {
                    files.push(p);
                }
            }
        }
    }
    files
}

#[cfg(windows)]
fn detect_half_life_on_windows() -> Option<(String, String)> {
    // 1) Типовые пути на всех дисках
    for letter in 'A'..='Z' {
        let drive_root = format!("{}:\\", letter);
        let root = Path::new(&drive_root);
        if !root.exists() {
            continue;
        }
        for rel in STEAM_HL_RELATIVE {
            let base = root.join(rel);
            if half_life_ok(&base) {
                let path_str = base.to_string_lossy().into_owned();
                let hint = format!(
                    "Найдена Half-Life с CS ({}\\…).",
                    drive_root.trim_end_matches('\\')
                );
                return Some((path_str, hint));
            }
        }
    }

    // 2) Пути из libraryfolders.vdf (доп. библиотеки Steam на других дисках)
    for vdf_path in unique_vdf_paths() {
        let content = match std::fs::read_to_string(&vdf_path) {
            Ok(s) => s,
            Err(_) => continue,
        };
        let content = content.trim_start_matches('\u{feff}');
        for lib_root in steam_library_roots_from_vdf(content) {
            let hl = PathBuf::from(&lib_root).join("steamapps/common/Half-Life");
            if half_life_ok(&hl) {
                let path_str = hl.to_string_lossy().into_owned();
                return Some((
                    path_str,
                    "Найдена Half-Life по списку библиотек Steam (libraryfolders.vdf).".into(),
                ));
            }
        }
    }

    None
}

#[tauri::command]
pub fn detect_game_installation() -> GameDetectResult {
    #[cfg(windows)]
    if let Some((path, hint)) = detect_half_life_on_windows() {
        return GameDetectResult {
            path: Some(path),
            hint,
        };
    }

    GameDetectResult {
        path: None,
        hint: "Авто-поиск (диски A:–Z:, типовые пути Steam и libraryfolders.vdf) не нашёл hl.exe с папкой cstrike. Укажите папку вручную."
            .into(),
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

#[cfg(all(test, windows))]
mod tests {
    use super::steam_library_roots_from_vdf;

    #[test]
    fn vdf_extracts_path_values() {
        let vdf = r#""path"		"D:\\SteamLibrary"
	"path"		"E:\\Games\\Steam""#;
        let roots = steam_library_roots_from_vdf(vdf);
        assert_eq!(roots.len(), 2);
        assert!(roots[0].contains("SteamLibrary") || roots[0].ends_with("SteamLibrary"));
        assert!(roots[1].contains("Games") || roots[1].contains("Steam"));
    }
}
