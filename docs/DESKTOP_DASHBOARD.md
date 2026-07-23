# Tauri React Desktop Dashboard Overview

## Architecture
The desktop application is built with Tauri 2, React 18, TypeScript, Tailwind CSS, TanStack Query, and Zustand.

```
Tauri Desktop UI (React) --> Tauri Rust Secure Proxy --> Local FastAPI (127.0.0.1:8000)
                                                    --> Local WhatsApp Worker (127.0.0.1:8010)
```

## Security & Isolation
- **No Direct Access**: Desktop shell has ZERO direct access to SQLite database files, MT5 terminal packages, order execution, or WhatsApp session files.
- **Secure Token Storage**: `LOCAL_API_TOKEN` is managed via Rust secure proxy memory store. Token is never placed in `localStorage`, `sessionStorage`, URLs, logs, or plain JSON.
