# Operations & Maintenance Guide

**Release Version**: `1.0.0-demo`  
**Platform**: WhatsApp XAUUSD MT5 Demo Trading System  

---

## Process Management

### 1. Starting All Services
Run the automated startup script:
```powershell
powershell -ExecutionPolicy Bypass -File ./scripts/start-all.ps1
```
This script automatically:
1. Runs Alembic database migrations (`006_reconciliation_and_reliability`).
2. Performs startup database integrity checks and WAL journal verification.
3. Recovers abandoned orchestration runs, stuck outbox events, and execution jobs.

To launch the FastAPI backend service manually:
```powershell
$env:PYTHONPATH="apps/trading-service"
uvicorn apps.trading-service.src.main:app --port 8000
```

To launch the Tauri desktop dashboard:
```powershell
pnpm desktop:dev
```

### 2. Stopping Services
To perform a clean, graceful shutdown:
```powershell
powershell -ExecutionPolicy Bypass -File ./scripts/stop-all.ps1
```

### 3. Checking Service Status
```powershell
powershell -ExecutionPolicy Bypass -File ./scripts/status-all.ps1
```

---

## Database Operations

### 1. Creating a Database Backup
```powershell
powershell -ExecutionPolicy Bypass -File ./scripts/backup-database.ps1
```
Backups are saved to `backups/trading_bot_backup_<TIMESTAMP>.db` and automatically verified using `PRAGMA integrity_check`.

### 2. Restoring a Database Backup
Restoring a database requires the explicit safety confirmation phrase `RESTORE DATABASE CONFIRM`:
```powershell
powershell -ExecutionPolicy Bypass -File ./scripts/restore-database.ps1 -BackupFile "backups/trading_bot_backup_20260726-081540.db" -ConfirmationPhrase "RESTORE DATABASE CONFIRM"
```

---

## Emergency Safety Procedures

### Emergency Stop XAUUSD
If emergency stop is triggered via the Tauri UI or `POST /api/v1/control/emergency-stop`:
- Trading automation is immediately set to `EMERGENCY_STOPPED`.
- All pending MT5 executions are blocked.
- To reset emergency stop, the phrase `RESET EMERGENCY STOP` must be entered in the UI.

### Emergency Close All Demo XAUUSD Positions
To close all active demo XAUUSD positions across the broker:
- Request phrase: `CLOSE ALL DEMO XAUUSD`.
- Scope: `APPLICATION_OWNED` (default) or `ALL_DEMO_XAUUSD`.
- Performs ticket-by-ticket closure and triggers immediate broker reconciliation.
