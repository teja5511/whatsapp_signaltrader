// Prevents additional console window on Windows in release
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod secure_store;
mod process;
mod commands;

use std::sync::Arc;
use secure_store::SecureTokenStore;
use commands::*;

fn main() {
    let token_store = Arc::new(SecureTokenStore::new());

    tauri::Builder::default()
        .manage(token_store)
        .invoke_handler(tauri::generate_handler![
            secure_token_set,
            secure_token_exists,
            secure_token_clear,
            secure_api_request,
            get_app_version,
            get_platform_info,
            open_external_url
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
