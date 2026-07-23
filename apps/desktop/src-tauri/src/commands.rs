use std::collections::HashMap;
use std::sync::Arc;
use tauri::State;
use serde::{Deserialize, Serialize};

use crate::secure_store::SecureTokenStore;
use crate::process;

#[derive(Debug, Serialize, Deserialize)]
pub struct ApiResponse {
    pub status: u16,
    pub body: String,
    pub ok: bool,
}

#[tauri::command]
pub fn secure_token_set(token: String, state: State<'_, Arc<SecureTokenStore>>) -> Result<(), String> {
    if token.trim().is_empty() {
        return Err("Token cannot be empty".to_string());
    }
    state.set_token(token.trim().to_string());
    Ok(())
}

#[tauri::command]
pub fn secure_token_exists(state: State<'_, Arc<SecureTokenStore>>) -> bool {
    state.exists()
}

#[tauri::command]
pub fn secure_token_clear(state: State<'_, Arc<SecureTokenStore>>) -> Result<(), String> {
    state.clear();
    Ok(())
}

#[tauri::command]
pub async fn secure_api_request(
    url: String,
    method: String,
    body: Option<String>,
    headers: Option<HashMap<String, String>>,
    state: State<'_, Arc<SecureTokenStore>>,
) -> Result<ApiResponse, String> {
    // Validate local loopback default
    let is_loopback = url.starts_with("http://127.0.0.1") || url.starts_with("http://localhost");
    if !is_loopback && !url.starts_with("https://") {
        return Err("Untrusted external non-HTTPS URL blocked for security.".to_string());
    }

    let client = reqwest::Client::new();
    let mut builder = match method.to_uppercase().as_str() {
        "GET" => client.get(&url),
        "POST" => client.post(&url),
        "PUT" => client.put(&url),
        "DELETE" => client.delete(&url),
        "PATCH" => client.patch(&url),
        _ => return Err(format!("Unsupported HTTP method: {}", method)),
    };

    // Attach custom headers
    if let Some(hdrs) = headers {
        for (k, v) in hdrs {
            if k.to_lowercase() != "authorization" {
                builder = builder.header(&k, &v);
            }
        }
    }

    // Attach Bearer token from secure store
    if let Some(token) = state.get_token() {
        builder = builder.header("Authorization", format!("Bearer {}", token));
    }

    // Attach request body if present
    if let Some(b) = body {
        builder = builder.header("Content-Type", "application/json").body(b);
    }

    match builder.send().await {
        Ok(res) => {
            let status = res.status().as_u16();
            let ok = res.status().is_success();
            let body = res.text().await.unwrap_or_default();
            Ok(ApiResponse { status, body, ok })
        }
        Err(e) => Err(format!("API Request Failed: {}", e)),
    }
}

#[tauri::command]
pub fn get_app_version() -> String {
    process::get_app_version_info()
}

#[tauri::command]
pub fn get_platform_info() -> String {
    process::get_platform_info()
}

#[tauri::command]
pub fn open_external_url(url: String) -> Result<(), String> {
    if !url.starts_with("http://") && !url.starts_with("https://") {
        return Err("Invalid external URL scheme".to_string());
    }
    // Safe shell-less URL opener placeholder
    Ok(())
}
