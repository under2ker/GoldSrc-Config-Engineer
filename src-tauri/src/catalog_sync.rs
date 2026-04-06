//! Синхронизация `data/*.json` с GitHub (If-Modified-Since), бэкап и откат при невалидном JSON.

use std::collections::HashMap;
use std::fs;
use std::io::Write;
use std::path::{Path, PathBuf};
use std::time::Duration;

use goldsr_cfg_core::{apply_data_overrides, CATALOG_JSON_FILES};
use reqwest::blocking::Client;
use reqwest::header::{HeaderMap, HeaderValue, IF_MODIFIED_SINCE};
use serde::{Deserialize, Serialize};
use tauri::AppHandle;
use tauri::Manager;

const DEFAULT_CATALOG_BASE: &str =
    "https://raw.githubusercontent.com/under2ker/GoldSrc-Config-Engineer/main/data";

fn catalog_base_url() -> String {
    std::env::var("GCE_CATALOG_BASE_URL").unwrap_or_else(|_| DEFAULT_CATALOG_BASE.to_string())
}

#[derive(Debug, Default, Serialize, Deserialize)]
struct CatalogMeta {
    /// Имя файла → значение заголовка Last-Modified с сервера (для If-Modified-Since).
    last_modified: HashMap<String, String>,
}

fn catalog_dir(app: &AppHandle) -> Result<PathBuf, String> {
    let dir = app
        .path()
        .app_local_data_dir()
        .map_err(|e| e.to_string())?
        .join("catalog_data");
    fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
    Ok(dir)
}

fn meta_path(dir: &Path) -> PathBuf {
    dir.join("catalog_meta.json")
}

fn load_meta(dir: &Path) -> CatalogMeta {
    let p = meta_path(dir);
    if !p.exists() {
        return CatalogMeta::default();
    }
    fs::read_to_string(&p)
        .ok()
        .and_then(|s| serde_json::from_str(&s).ok())
        .unwrap_or_default()
}

fn save_meta(dir: &Path, meta: &CatalogMeta) -> Result<(), String> {
    let p = meta_path(dir);
    let tmp = dir.join("catalog_meta.json.tmp");
    let mut f = fs::File::create(&tmp).map_err(|e| e.to_string())?;
    serde_json::to_writer_pretty(&mut f, meta).map_err(|e| e.to_string())?;
    f.flush().map_err(|e| e.to_string())?;
    drop(f);
    fs::rename(&tmp, &p).map_err(|e| e.to_string())?;
    Ok(())
}

fn validate_json(text: &str) -> Result<(), String> {
    serde_json::from_str::<serde_json::Value>(text).map_err(|e| format!("невалидный JSON: {e}"))?;
    Ok(())
}

fn path_with_suffix(path: &Path, suffix: &str) -> PathBuf {
    let mut s = path.as_os_str().to_os_string();
    s.push(suffix);
    PathBuf::from(s)
}

/// Сохранить с бэкапом `имя.json.bak`; при ошибке записи откат из бэкапа.
fn write_with_backup(path: &Path, body: &str) -> Result<(), String> {
    validate_json(body)?;
    if path.exists() {
        let bak = path_with_suffix(path, ".bak");
        fs::copy(path, &bak).map_err(|e| format!("backup {bak:?}: {e}"))?;
    }
    let tmp = path_with_suffix(path, ".tmp");
    fs::write(&tmp, body).map_err(|e| e.to_string())?;
    fs::rename(&tmp, path).map_err(|e| e.to_string())?;
    Ok(())
}

fn restore_from_backup(path: &Path) -> Result<(), String> {
    let bak = path_with_suffix(path, ".bak");
    if bak.exists() {
        fs::copy(&bak, path).map_err(|e| e.to_string())?;
    }
    Ok(())
}

/// Скачать обновления, затем применить оверлеи в `goldsr_cfg_core`.
pub fn sync_and_apply(app: &AppHandle) -> Result<CatalogSyncReport, String> {
    let dir = catalog_dir(app)?;
    let mut meta = load_meta(&dir);
    let client = Client::builder()
        .timeout(Duration::from_secs(18))
        .build()
        .map_err(|e| e.to_string())?;

    let base = catalog_base_url();
    let base = base.trim_end_matches('/');

    let mut report = CatalogSyncReport::default();

    for file in CATALOG_JSON_FILES.iter() {
        report.checked += 1;
        let url = format!("{base}/{file}");
        let mut headers = HeaderMap::new();
        if let Some(ims) = meta.last_modified.get(*file) {
            if let Ok(hv) = HeaderValue::from_str(ims) {
                headers.insert(IF_MODIFIED_SINCE, hv);
            }
        }

        let resp = match client.get(&url).headers(headers).send() {
            Ok(r) => r,
            Err(e) => {
                report
                    .errors
                    .push(format!("{file}: запрос: {e}"));
                continue;
            }
        };

        let status = resp.status();
        if status == 304 {
            report.skipped_not_modified += 1;
            continue;
        }
        if !status.is_success() {
            report
                .errors
                .push(format!("{file}: HTTP {}", status.as_u16()));
            continue;
        }

        let hdrs = resp.headers().clone();
        let body = match resp.text() {
            Ok(t) => t,
            Err(e) => {
                report.errors.push(format!("{file}: чтение тела: {e}"));
                continue;
            }
        };

        let path = dir.join(file);
        if let Err(e) = validate_json(&body) {
            report.errors.push(format!("{file}: {e}"));
            continue;
        }

        if let Err(e) = write_with_backup(&path, &body) {
            report.errors.push(format!("{file}: запись: {e}"));
            let _ = restore_from_backup(&path);
            continue;
        }

        if let Some(lm) = hdrs.get("last-modified").and_then(|v| v.to_str().ok()) {
            meta.last_modified.insert((*file).to_string(), lm.to_string());
        }
        report.updated += 1;
    }

    save_meta(&dir, &meta)?;

    // Применить все файлы из каталога (частичный набор допустим).
    let mut files: HashMap<String, String> = HashMap::new();
    for file in CATALOG_JSON_FILES.iter() {
        let p = dir.join(file);
        if p.is_file() {
            let s = fs::read_to_string(&p).map_err(|e| e.to_string())?;
            validate_json(&s)?;
            files.insert((*file).to_string(), s);
        }
    }

    apply_data_overrides(files).map_err(|e| format!("apply_data_overrides: {e}"))?;

    Ok(report)
}

/// Загрузить JSON с диска в core (без сети), например после ручной подстановки файлов.
pub fn apply_local_catalog(app: &AppHandle) -> Result<(), String> {
    let dir = catalog_dir(app)?;
    let mut files: HashMap<String, String> = HashMap::new();
    for file in CATALOG_JSON_FILES.iter() {
        let p = dir.join(file);
        if p.is_file() {
            let s = fs::read_to_string(&p).map_err(|e| e.to_string())?;
            validate_json(&s)?;
            files.insert((*file).to_string(), s);
        }
    }
    apply_data_overrides(files)
}

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CatalogSyncReport {
    pub checked: usize,
    pub updated: usize,
    pub skipped_not_modified: usize,
    pub errors: Vec<String>,
}
