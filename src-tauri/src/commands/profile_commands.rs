//! CRUD профилей в SQLite.

use serde::Serialize;
use tauri::State;
use uuid::Uuid;

use crate::db::AppDb;

#[derive(Debug, Serialize)]
pub struct ProfileRow {
    pub id: String,
    pub name: String,
    pub updated_at: String,
    pub is_favorite: bool,
}

#[tauri::command]
pub fn profile_save(
    db: State<'_, AppDb>,
    name: String,
    config_json: String,
) -> Result<String, String> {
    let conn = db.0.lock().map_err(|e| e.to_string())?;
    let id = Uuid::new_v4().to_string();
    let now = chrono::Utc::now().to_rfc3339();
    conn.execute(
        "INSERT INTO profiles (id, name, config_json, created_at, updated_at, is_favorite) VALUES (?1, ?2, ?3, ?4, ?5, 0)",
        rusqlite::params![&id, &name, &config_json, &now, &now],
    )
    .map_err(|e| e.to_string())?;
    Ok(id)
}

#[tauri::command]
pub fn profile_list(db: State<'_, AppDb>) -> Result<Vec<ProfileRow>, String> {
    let conn = db.0.lock().map_err(|e| e.to_string())?;
    let mut stmt = conn
        .prepare(
            "SELECT id, name, updated_at, is_favorite FROM profiles ORDER BY is_favorite DESC, updated_at DESC",
        )
        .map_err(|e| e.to_string())?;
    let rows = stmt
        .query_map([], |row| {
            Ok(ProfileRow {
                id: row.get(0)?,
                name: row.get(1)?,
                updated_at: row.get(2)?,
                is_favorite: row.get::<_, i64>(3)? != 0,
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
pub fn profile_load(db: State<'_, AppDb>, id: String) -> Result<String, String> {
    let conn = db.0.lock().map_err(|e| e.to_string())?;
    let json: String = conn
        .query_row(
            "SELECT config_json FROM profiles WHERE id = ?1",
            [&id],
            |row| row.get(0),
        )
        .map_err(|e| e.to_string())?;
    Ok(json)
}

#[tauri::command]
pub fn profile_delete(db: State<'_, AppDb>, id: String) -> Result<(), String> {
    let conn = db.0.lock().map_err(|e| e.to_string())?;
    conn.execute("DELETE FROM profiles WHERE id = ?1", [&id])
        .map_err(|e| e.to_string())?;
    Ok(())
}

/// Обновить имя и/или признак избранного (передать только меняемые поля).
#[tauri::command]
pub fn profile_update(
    db: State<'_, AppDb>,
    id: String,
    name: Option<String>,
    is_favorite: Option<bool>,
) -> Result<(), String> {
    if name.is_none() && is_favorite.is_none() {
        return Ok(());
    }
    let conn = db.0.lock().map_err(|e| e.to_string())?;
    let now = chrono::Utc::now().to_rfc3339();
    match (name, is_favorite) {
        (Some(n), Some(fav)) => {
            conn.execute(
                "UPDATE profiles SET name = ?1, is_favorite = ?2, updated_at = ?3 WHERE id = ?4",
                rusqlite::params![&n, if fav { 1 } else { 0 }, &now, &id],
            )
            .map_err(|e| e.to_string())?;
        }
        (Some(n), None) => {
            conn.execute(
                "UPDATE profiles SET name = ?1, updated_at = ?2 WHERE id = ?3",
                rusqlite::params![&n, &now, &id],
            )
            .map_err(|e| e.to_string())?;
        }
        (None, Some(fav)) => {
            conn.execute(
                "UPDATE profiles SET is_favorite = ?1, updated_at = ?2 WHERE id = ?3",
                rusqlite::params![if fav { 1 } else { 0 }, &now, &id],
            )
            .map_err(|e| e.to_string())?;
        }
        (None, None) => {}
    }
    Ok(())
}
