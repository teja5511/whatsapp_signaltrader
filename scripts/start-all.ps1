# Process Startup Script for WhatsApp Trading Bot Services
$ErrorActionPreference = "Stop"

$root = $PSScriptRoot | Split-Path -Parent

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Starting WhatsApp XAUUSD Trading Bot Services..." -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Run Alembic Upgrade
Write-Host "[1/3] Running Alembic Database Migrations..." -ForegroundColor Yellow
$env:PYTHONPATH = "apps/trading-service"
python -m alembic -c apps/trading-service/alembic.ini upgrade head
if ($LASTEXITCODE -ne 0) {
    Write-Error "Alembic migration failed!"
    exit 1
}

# 2. Check Database & Startup Recovery
Write-Host "[2/3] Running Startup Recovery Checks..." -ForegroundColor Yellow
python -c "from src.recovery.startup import StartupRecoveryManager; res = StartupRecoveryManager().run_startup_recovery(); print('[OK] Startup recovery status:', res.database_integrity)"

# 3. Informational Summary
Write-Host "[3/3] Ready to run trading service & desktop application." -ForegroundColor Green
Write-Host "To start FastAPI Trading Service: uvicorn apps.trading-service.src.main:app --port 8000" -ForegroundColor Gray
Write-Host "To start Tauri Desktop App: pnpm desktop:dev" -ForegroundColor Gray
