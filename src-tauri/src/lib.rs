mod commands;
mod db;

use commands::config_commands::{
    check_cfg_import_safety, export_config_snapshot, export_modular_config, export_modular_from_json,
    generate_config, generate_config_from_json, get_aliases_catalog, get_game_modes, get_pro_presets,
    parse_import_cfg, ping,
};
use commands::fetch_commands::fetch_text_from_url;
use commands::history_commands::{
    history_append, history_clear, history_count, history_delete, history_list, history_load,
};
use commands::settings_commands::{app_settings_get, app_settings_set};
use commands::game_commands::{
    deploy_modular_files, detect_game_installation, execute_console_command_stub,
};
use commands::app_commands::get_app_paths_info;
use commands::hello::greet;
use commands::profile_commands::{profile_delete, profile_list, profile_load, profile_save, profile_update};
use db::AppDb;
use tauri::Manager;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_opener::init())
        .setup(|app| {
            let db = AppDb::open(app.handle())?;
            app.manage(db);
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            greet,
            ping,
            get_game_modes,
            get_pro_presets,
            get_aliases_catalog,
            generate_config,
            check_cfg_import_safety,
            export_modular_config,
            export_modular_from_json,
            generate_config_from_json,
            parse_import_cfg,
            export_config_snapshot,
            profile_save,
            profile_list,
            profile_load,
            profile_delete,
            profile_update,
            history_append,
            history_clear,
            history_count,
            history_list,
            history_load,
            history_delete,
            app_settings_get,
            app_settings_set,
            fetch_text_from_url,
            get_app_paths_info,
            detect_game_installation,
            deploy_modular_files,
            execute_console_command_stub,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
