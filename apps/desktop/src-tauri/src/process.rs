pub fn get_app_version_info() -> String {
    "1.0.0".to_string()
}

pub fn get_platform_info() -> String {
    format!("{}-{}", std::env::consts::OS, std::env::consts::ARCH)
}
