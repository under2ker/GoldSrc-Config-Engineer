//! История снимков конфига (SQLite).

use serde::Serialize;
use tauri::State;

use crate::db::{app_setting_get, AppDb};

pub(crate) const HISTORY_MAX_KEY: &str = "history_max_entries";
const DEFAULT_HISTORY_MAX: i64 = 100;
const MIN_HISTORY_MAX: i64 = 10;
const MAX_HISTORY_MAX: i64 = 500;

#[derive(Debug, Serialize)]
pub struct HistoryRow {
    pub id: i64,
    pub profile_id: Option<String>,
    pub created_at: String,
    pub size_bytes: i64,
}

#[tauri::command]
pub fn history_append(
    db: State<'_, AppDb>,
    config_json: String,
    profile_id: Option<String>,
) -> Result<i64, String> {
    let conn = db.0.lock().map_err(|e| e.to_string())?;
    let now = chrono::Utc::now().to_rfc3339();
    let size = config_json.len() as i64;
    conn.execute(
        "INSERT INTO history (profile_id, config_json, created_at, size_bytes) VALUES (?1, ?2, ?3, ?4)",
        rusqlite::params![&profile_id, &config_json, &now, &size],
    )
    .map_err(|e| e.to_string())?;
    let id = conn.last_insert_rowid();
    trim_history_to_limit(&conn)?;
    Ok(id)
}

fn history_max_entries(conn: &rusqlite::Connection) -> Result<i64, String> {
    let raw = app_setting_get(conn, HISTORY_MAX_KEY)?;
    let n = raw
        .and_then(|s| s.parse::<i64>().ok())
        .unwrap_or(DEFAULT_HISTORY_MAX);
    Ok(n.clamp(MIN_HISTORY_MAX, MAX_HISTORY_MAX))
}

/// Удаляет самые старые записи, если превышен лимит из настроек.
pub(crate) fn trim_history_to_limit(conn: &rusqlite::Connection) -> Result<(), String> {
    let max = history_max_entries(conn)?;
    let count: i64 = conn
        .query_row("SELECT COUNT(*) FROM history", [], |r| r.get(0))
        .map_err(|e| e.to_string())?;
    if count <= max {
        return Ok(());
    }
    let excess = count - max;
    conn.execute(
        "DELETE FROM history WHERE id IN (SELECT id FROM history ORDER BY id ASC LIMIT ?1)",
        [excess],
    )
    .map_err(|e| e.to_string())?;
    Ok(())
}

#[tauri::command]
pub fn history_count(db: State<'_, AppDb>) -> Result<i64, String> {
    let conn = db.0.lock().map_err(|e| e.to_string())?;
    let n: i64 = conn
        .query_row("SELECT COUNT(*) FROM history", [], |r| r.get(0))
        .map_err(|e| e.to_string())?;
    Ok(n)
}

#[tauri::command]
pub fn history_clear(db: State<'_, AppDb>) -> Result<u64, String> {
    let conn = db.0.lock().map_err(|e| e.to_string())?;
    let n = conn
        .execute("DELETE FROM history", [])
        .map_err(|e| e.to_string())?;
    Ok(n as u64)
}

#[tauri::command]
pub fn history_list(db: State<'_, AppDb>, limit: u32) -> Result<Vec<HistoryRow>, String> {
    let conn = db.0.lock().map_err(|e| e.to_string())?;
    let lim: i64 = limit.max(1).min(500).into();
    let mut stmt = conn
        .prepare(
            "SELECT id, profile_id, created_at, size_bytes FROM history ORDER BY id DESC LIMIT ?1",
        )
        .map_err(|e| e.to_string())?;
    let rows = stmt
        .query_map([lim], |row| {
            let pid: Option<String> = row.get(1)?;
            Ok(HistoryRow {
                id: row.get(0)?,
                profile_id: pid,
                created_at: row.get(2)?,
                size_bytes: row.get(3)?,
            })
        })
        .map_err(|e| e.to_string())?;
    let mut out = Vec::new();
    for r in rows {
        out.push(r.map_err(|e| e.to_string())?);
    }
    Ok(out)
}

#[tauri::command]
pub fn history_load(db: State<'_, AppDb>, id: i64) -> Result<String, String> {
    let conn = db.0.lock().map_err(|e| e.to_string())?;
    let json: String = conn
        .query_row(
            "SELECT config_json FROM history WHERE id = ?1",
            [id],
            |row| row.get(0),
        )
        .map_err(|e| e.to_string())?;
    Ok(json)
}

#[tauri::command]
pub fn history_delete(db: State<'_, AppDb>, id: i64) -> Result<(), String> {
    let conn = db.0.lock().map_err(|e| e.to_string())?;
    conn.execute("DELETE FROM history WHERE id = ?1", [id])
        .map_err(|e| e.to_string())?;
    Ok(())
}
