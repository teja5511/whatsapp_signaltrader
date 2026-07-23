# Desktop Security Architecture & Capabilities

## Security Rules
1. **Loopback Only**: All network connections default to `127.0.0.1`. Non-loopback plain HTTP requests are strictly blocked.
2. **Token Protection**: `LOCAL_API_TOKEN` is injected into `Authorization: Bearer <token>` headers inside the Rust secure request proxy.
3. **No Unrestricted Capabilities**: Tauri shell capabilities restrict direct filesystem and shell command execution.
