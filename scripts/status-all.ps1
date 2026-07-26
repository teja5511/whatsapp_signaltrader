# Service Status Script for WhatsApp Trading Bot
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " WhatsApp XAUUSD Trading Bot Status" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Database & Migrations
$env:PYTHONPATH = "apps/trading-service"
Write-Host "Database Revision:" -ForegroundColor Yellow
python -m alembic -c apps/trading-service/alembic.ini current

# 2. Running Processes
Write-Host "`nRunning Service Processes:" -ForegroundColor Yellow
$py = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*uvicorn*" -or $_.CommandLine -like "*trading-service*" }
if ($py) {
    Write-Host "  [RUNNING] Python Trading Service (PID: $($py.Id))" -ForegroundColor Green
} else {
    Write-Host "  [STOPPED] Python Trading Service" -ForegroundColor Red
}

$node = Get-Process node -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*whatsapp-worker*" }
if ($node) {
    Write-Host "  [RUNNING] WhatsApp Worker (PID: $($node.Id))" -ForegroundColor Green
} else {
    Write-Host "  [STOPPED] WhatsApp Worker" -ForegroundColor Red
}
