//! Проверка, что все файлы в `../data/*.json` — валидный JSON (чеклист §104).
use std::env;
use std::fs;
use std::path::Path;

fn main() {
    let manifest_dir = env::var_os("CARGO_MANIFEST_DIR").expect("CARGO_MANIFEST_DIR");
    let data_dir = Path::new(&manifest_dir).join("../data");

    let entries = fs::read_dir(&data_dir).unwrap_or_else(|e| {
        panic!(
            "goldsr_cfg_core build: cannot read data directory {}: {e}",
            data_dir.display()
        )
    });

    for entry in entries {
        let entry = entry.expect("goldsr_cfg_core build: read_dir entry");
        let path = entry.path();
        if path.extension().and_then(|s| s.to_str()) != Some("json") {
            continue;
        }
        println!("cargo:rerun-if-changed={}", path.display());

        let raw = fs::read_to_string(&path).unwrap_or_else(|e| {
            panic!(
                "goldsr_cfg_core build: cannot read {}: {e}",
                path.display()
            )
        });
        serde_json::from_str::<serde_json::Value>(&raw).unwrap_or_else(|e| {
            panic!(
                "goldsr_cfg_core build: invalid JSON in {}: {e}",
                path.display()
            )
        });
    }
}
