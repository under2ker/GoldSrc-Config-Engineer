//! Каталог CVAR из `data/cvars.json` — категории и описания для комментариев в .cfg.

use std::collections::HashMap;
use std::sync::{Arc, RwLock};

use serde_json::Value;

use crate::data::overlay;

const CVARS_JSON: &str = include_str!(concat!(
    env!("CARGO_MANIFEST_DIR"),
    "/../data/cvars.json"
));

static CAT: RwLock<Option<Arc<CvarsCatalog>>> = RwLock::new(None);

#[derive(Debug)]
pub struct CvarsCatalog {
    /// cvar → описание (предпочтительно description_ru)
    descriptions: HashMap<String, String>,
    /// cvar → ключ верхнего уровня (video, audio, network, …)
    category: HashMap<String, String>,
}

impl CvarsCatalog {
    fn load_from_str(raw: &str) -> Result<Self, String> {
        let root: Value = serde_json::from_str(raw).map_err(|e| e.to_string())?;
        let obj = root
            .as_object()
            .ok_or_else(|| "cvars.json: ожидался объект".to_string())?;

        let mut descriptions = HashMap::new();
        let mut category = HashMap::new();

        for (cat, cvars_val) in obj {
            let cvars = cvars_val.as_object().ok_or_else(|| {
                format!("cvars.json: категория {cat} не объект")
            })?;
            for (cvar_name, info) in cvars {
                category.insert(cvar_name.clone(), cat.clone());
                let desc = info
                    .get("description_ru")
                    .and_then(|v| v.as_str())
                    .or_else(|| info.get("description_en").and_then(|v| v.as_str()))
                    .unwrap_or("")
                    .to_string();
                descriptions.insert(cvar_name.clone(), desc);
            }
        }

        Ok(Self {
            descriptions,
            category,
        })
    }

    pub fn global() -> Arc<Self> {
        {
            let r = CAT.read().expect("cvars catalog");
            if let Some(ref a) = *r {
                return a.clone();
            }
        }
        let mut w = CAT.write().expect("cvars catalog");
        if w.is_none() {
            let raw = overlay::resolve_json("cvars.json", CVARS_JSON);
            let cat = CvarsCatalog::load_from_str(&raw).expect("cvars.json должен парситься");
            *w = Some(Arc::new(cat));
        }
        w.as_ref().expect("cvars init").clone()
    }

    /// Перечитать каталог после смены оверлея `cvars.json`.
    pub fn reload_global() -> Result<(), String> {
        let raw = overlay::resolve_json("cvars.json", CVARS_JSON);
        let cat = CvarsCatalog::load_from_str(&raw)?;
        *CAT.write().expect("cvars catalog") = Some(Arc::new(cat));
        Ok(())
    }

    pub fn description(&self, cvar: &str) -> Option<&str> {
        self.descriptions.get(cvar).map(|s| s.as_str())
    }

    /// Категория из JSON; неизвестные CVAR попадут в `other`.
    pub fn category_of(&self, cvar: &str) -> &str {
        self.category.get(cvar).map(|s| s.as_str()).unwrap_or("other")
    }

    pub fn is_known_cvar(&self, name: &str) -> bool {
        self.category.contains_key(name)
    }
}
