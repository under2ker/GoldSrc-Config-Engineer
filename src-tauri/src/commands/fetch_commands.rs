//! Загрузка текста по HTTP(S) для импорта (без выполнения кода с удалённого URL в Rust).

use std::time::Duration;

use reqwest::Url;

/// Как на странице импорта: не больше 512 КБ.
const MAX_BODY_BYTES: usize = 512 * 1024;

/// GET по `http`/`https`, тело как UTF-8. Размер ответа ограничен.
#[tauri::command]
pub fn fetch_text_from_url(url: String) -> Result<String, String> {
    let parsed = Url::parse(&url).map_err(|e| format!("Некорректный URL: {e}"))?;
    let scheme = parsed.scheme();
    if scheme != "http" && scheme != "https" {
        return Err("Разрешены только ссылки http:// и https://".into());
    }

    let client = reqwest::blocking::Client::builder()
        .timeout(Duration::from_secs(45))
        .redirect(reqwest::redirect::Policy::limited(8))
        .build()
        .map_err(|e| e.to_string())?;

    let resp = client.get(url).send().map_err(|e| e.to_string())?;
    if !resp.status().is_success() {
        return Err(format!("Сервер ответил {}", resp.status()));
    }

    let bytes = resp.bytes().map_err(|e| e.to_string())?;
    if bytes.len() > MAX_BODY_BYTES {
        return Err(format!(
            "Ответ больше {} КБ — сократите файл или скачайте вручную.",
            MAX_BODY_BYTES / 1024
        ));
    }

    String::from_utf8(bytes.to_vec()).map_err(|e| format!("Не UTF-8: {e}"))
}
