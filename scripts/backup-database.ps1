# Database Backup Script for WhatsApp Trading Bot
param (
    [string]$DatabasePath = "trading_bot.db",
    [string]$BackupDir = "backups"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -Path $DatabasePath)) {
    Write-Error "Database file '$DatabasePath' does not exist."
    exit 1
}

if (-not (Test-Path -Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
}

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupFile = Join-Path -Path $BackupDir -ChildPath "trading_bot_backup_$timestamp.db"

Write-Host "Creating database backup at: $backupFile" -ForegroundColor Cyan
Copy-Item -Path $DatabasePath -Destination $backupFile -Force

$dbSize = (Get-Item $DatabasePath).Length
$backupSize = (Get-Item $backupFile).Length

Write-Host "Original size: $dbSize bytes, Backup size: $backupSize bytes" -ForegroundColor Green

$pyPath = $backupFile.Replace("\", "/")
$verifyScript = "import sqlite3, sys; conn = sqlite3.connect('$pyPath'); res = conn.execute('PRAGMA integrity_check').fetchone(); sys.exit(0 if res[0] == 'ok' else 1)"
python -c $verifyScript
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Backup integrity verified." -ForegroundColor Green
} else {
    Write-Error "[FAIL] Backup integrity check failed!"
    exit 1
}
