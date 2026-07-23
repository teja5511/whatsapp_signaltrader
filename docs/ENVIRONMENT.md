# Development Environment & Monorepo Setup Guide

Document Version: 1.0.0 (Phase 2 Scaffolding)  
Status: Active  

---

## 1. Prerequisites & Toolchain

Ensure the following tools are installed on your Windows host:

- **Windows 10 / 11 x64**
- **Node.js**: `v18.0.0+` (Detected: `v24.12.0`)
- **Package Manager**: `pnpm` or `npm` (Detected: `pnpm` & `npm 11.14.1`)
- **Python**: `3.11+` (Detected: `3.12.8`)
- **Rust / Cargo**: `1.75+` (Required for Tauri desktop bundle builds)
- **MetaTrader 5**: Windows client terminal connected to an Exness Demo Account

---

## 2. Directory Layout & Architecture

```text
whatsapp_trading_bot/
├── apps/
│   ├── desktop/             # Tauri React desktop dashboard shell
│   ├── whatsapp-worker/     # Node.js TypeScript WhatsApp worker shell
│   └── trading-service/     # Python FastAPI trading core service shell
├── packages/
│   ├── contracts/           # Shared TypeScript domain contracts / interfaces
│   ├── ui/                  # Shared React UI components / tokens
│   └── parser-fixtures/     # Benchmark signal & command JSON test fixtures
├── scripts/
│   ├── dev.ps1              # Monorepo development services startup script
│   └── validate.ps1         # Monorepo health validation script
├── docs/                    # System specifications (Phase 1 Freeze)
├── package.json             # Root monorepo workspace manifest
├── pnpm-workspace.yaml      # Workspace packages definition
├── pyproject.toml           # Python root dependencies & tool config
├── README.md                # Project README
└── .gitignore               # Workspace gitignore
```

---

## 3. Development Workflow & Running Services

### 3.1 Workspace Health Validation
To verify all required documentation files, package manifests, and baseline Python pytest health checks:

```powershell
powershell -ExecutionPolicy Bypass -File ./scripts/validate.ps1
```

### 3.2 Running Development Services
To launch all monorepo application shells concurrently in background PowerShell windows:

```powershell
powershell -ExecutionPolicy Bypass -File ./scripts/dev.ps1
```

Serviced endpoints:
- **FastAPI Core**: `http://127.0.0.1:8000/health` & `http://127.0.0.1:8000/api/v1/status`
- **WhatsApp Worker**: `http://127.0.0.1:3001/health`
- **Desktop Dashboard**: `http://localhost:1420`
