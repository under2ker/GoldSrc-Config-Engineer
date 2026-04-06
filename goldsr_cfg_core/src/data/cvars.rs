//! Каталог CVAR из `data/cvars.json` — категории и описания для комментариев в .cfg.

use std::collections::HashMap;
use std::sync::OnceLock;

use serde_json::Value;

const CVARS_JSON: &str = include_str!(concat!(
    env!("CARGO_MANIFEST_DIR"),
    "/../data/cvars.json"
));

#[derive(Debug)]
pub struct CvarsCatalog {
    /// cvar → описание (предпочтительно description_ru)
    descriptions: HashMap<String, String>,
    /// cvar → ключ верхнего уровня (video, audio, network, …)
    category: HashMap<String, String>,
}

impl CvarsCatalog {
    fn load() -> Result<Self, String> {
        let root: Value = serde_json::from_str(CVARS_JSON).map_err(|e| e.to_string())?;
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

    pub fn global() -> &'static Self {
        static CELL: OnceLock<CvarsCatalog> = OnceLock::new();
        CELL.get_or_init(|| CvarsCatalog::load().expect("cvars.json должен парситься"))
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
