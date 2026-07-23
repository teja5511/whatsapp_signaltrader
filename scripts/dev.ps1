# WhatsApp MT5 Trading Bot - Development Startup Script
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Starting Monorepo Development Services..." -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$WorkspaceRoot = Get-Location

# 1. Start Python Trading Service (FastAPI)
Write-Host "[1/3] Starting Python Trading Core (FastAPI) on port 8000..." -ForegroundColor Green
$TradingServicePath = Join-Path $WorkspaceRoot "apps\trading-service"
Start-Process powershell -ArgumentList "-NoExit -Command Set-Location '$TradingServicePath'; python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload"

# 2. Start WhatsApp Worker Service (Node.js)
Write-Host "[2/3] Starting WhatsApp Ingestion Worker on port 3001..." -ForegroundColor Green
$WorkerPath = Join-Path $WorkspaceRoot "apps\whatsapp-worker"
Start-Process powershell -ArgumentList "-NoExit -Command Set-Location '$WorkerPath'; npm run dev"

# 3. Start Desktop Dashboard (Vite / Tauri)
Write-Host "[3/3] Starting Desktop Dashboard Development Server on port 1420..." -ForegroundColor Green
$DesktopPath = Join-Path $WorkspaceRoot "apps\desktop"
Start-Process powershell -ArgumentList "-NoExit -Command Set-Location '$DesktopPath'; npm run dev"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " All services launched in background PowerShell windows." -ForegroundColor Cyan
Write-Host " FastAPI Core: http://127.0.0.1:8000/health" -ForegroundColor Cyan
Write-Host " WhatsApp Worker: http://127.0.0.1:3001/health" -ForegroundColor Cyan
Write-Host " Desktop Dashboard: http://localhost:1420" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
