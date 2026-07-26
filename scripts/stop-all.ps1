# Graceful Shutdown Script for WhatsApp Trading Bot
Write-Host "Gracefully stopping all WhatsApp Trading Bot processes..." -ForegroundColor Yellow

$pythonProcs = Get-Process python -ErrorAction SilentlyContinue
foreach ($p in $pythonProcs) {
    if ($p.CommandLine -like "*uvicorn*" -or $p.CommandLine -like "*trading-service*") {
        Write-Host "Stopping Python service process PID: $($p.Id)" -ForegroundColor Cyan
        Stop-Process -Id $p.Id -Force
    }
}

$nodeProcs = Get-Process node -ErrorAction SilentlyContinue
foreach ($p in $nodeProcs) {
    if ($p.CommandLine -like "*whatsapp-worker*") {
        Write-Host "Stopping WhatsApp worker process PID: $($p.Id)" -ForegroundColor Cyan
        Stop-Process -Id $p.Id -Force
    }
}

Write-Host "[OK] All bot services stopped." -ForegroundColor Green
