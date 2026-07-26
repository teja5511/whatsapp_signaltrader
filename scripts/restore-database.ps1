# Database Restore Script for WhatsApp Trading Bot
param (
    [Parameter(Mandatory=$true)]
    [string]$BackupFile,

    [string]$DatabasePath = "trading_bot.db",

    [Parameter(Mandatory=$true)]
    [string]$ConfirmationPhrase
)

$ErrorActionPreference = "Stop"

if ($ConfirmationPhrase -ne "RESTORE DATABASE CONFIRM") {
    Write-Error "Invalid confirmation phrase '$ConfirmationPhrase'. Required: 'RESTORE DATABASE CONFIRM'"
    exit 1
}

if (-not (Test-Path -Path $BackupFile)) {
    Write-Error "Backup file '$BackupFile' does not exist."
    exit 1
}

# Pre-restore safety backup
if (Test-Path -Path $DatabasePath) {
    $preRestoreBackup = "trading_bot_prerestore_$(Get-Date -Format 'yyyyMMdd-HHmmss').db"
    Write-Host "Creating pre-restore safety copy at: $preRestoreBackup" -ForegroundColor Yellow
    Copy-Item -Path $DatabasePath -Destination $preRestoreBackup -Force
}

Write-Host "Restoring database from: $BackupFile to: $DatabasePath" -ForegroundColor Cyan
Copy-Item -Path $BackupFile -Destination $DatabasePath -Force

Write-Host "[OK] Database restored successfully." -ForegroundColor Green
