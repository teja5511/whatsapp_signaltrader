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
Write-Host "[3/3] System environment configured for Real MT5 Terminal & WhatsApp Web!" -ForegroundColor Green
Write-Host ""
Write-Host "Launch Commands for Real Trading Mode:" -ForegroundColor Yellow
Write-Host '1. Start Trading Service (FastAPI):' -ForegroundColor Cyan
Write-Host '   cd apps/trading-service; $env:MT5_ADAPTER_MODE="real"; python -m uvicorn src.main:app --port 8000' -ForegroundColor Gray
Write-Host ""
Write-Host '2. Start WhatsApp Worker (Baileys):' -ForegroundColor Cyan
Write-Host '   $env:WHATSAPP_ADAPTER_MODE="real"; pnpm whatsapp:dev' -ForegroundColor Gray
Write-Host ""
Write-Host '3. Start Desktop Dashboard App:' -ForegroundColor Cyan
Write-Host '   pnpm desktop:dev' -ForegroundColor Gray
Write-Host "============================================================" -ForegroundColor Cyan
