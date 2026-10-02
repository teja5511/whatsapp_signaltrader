# Starts the trading service, the WhatsApp worker, and the dashboard.
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root

function Import-DotEnv([string]$Path) {
    if (-not (Test-Path $Path)) { return }
    Get-Content $Path | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#") -or -not $line.Contains("=")) { return }
        $name, $value = $line.Split("=", 2)
        $name = $name.Trim()
        $value = $value.Trim()
        if ($value.Length -ge 2 -and (($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'")))) {
            $value = $value.Substring(1, $value.Length - 2)
        }
        Set-Item -Path "Env:$name" -Value $value
    }
}

function Test-Listening([int]$Port) {
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $wait = $client.BeginConnect("127.0.0.1", $Port, $null, $null)
        $ok = $wait.AsyncWaitHandle.WaitOne(400) -and $client.Connected
        return [bool]$ok
    } catch {
        return $false
    } finally {
        $client.Close()
    }
}

Import-DotEnv (Join-Path $root ".env")
$env:MT5_ADAPTER_MODE = "real"
$env:WHATSAPP_ADAPTER_MODE = "real"
$env:WHATSAPP_QR_EXPOSE_OVER_LOCAL_API = "true"
$env:WHATSAPP_DATA_DIR = Join-Path $root "apps\whatsapp-worker\data"
if (-not $env:WHATSAPP_WORKER_PORT) { $env:WHATSAPP_WORKER_PORT = "8010" }

$pnpm = (Get-Command pnpm.cmd -ErrorAction SilentlyContinue).Source
if (-not $pnpm) { $pnpm = (Get-Command pnpm -ErrorAction SilentlyContinue).Source }
if (-not $pnpm) { throw "pnpm was not found on PATH." }

if (-not (Test-Listening 8000)) {
    Write-Host "Starting trading service on http://127.0.0.1:8000"
    Start-Process -FilePath "python" -ArgumentList "-m","uvicorn","src.main:app","--host","127.0.0.1","--port","8000" -WorkingDirectory (Join-Path $root "apps\trading-service") -WindowStyle Minimized
} else {
    Write-Host "Trading service is already running on port 8000"
}

if (-not (Test-Listening 8010)) {
    Write-Host "Starting WhatsApp worker on http://127.0.0.1:8010"
    Start-Process -FilePath $pnpm -ArgumentList "--filter","@whatsapp-bot/whatsapp-worker","dev" -WorkingDirectory $root -WindowStyle Minimized
} else {
    Write-Host "WhatsApp worker is already running on port 8010"
}

if (-not (Test-Listening 1420)) {
    Write-Host "Starting dashboard on http://localhost:1420"
    Start-Process -FilePath $pnpm -ArgumentList "desktop:dev" -WorkingDirectory $root -WindowStyle Minimized
} else {
    Write-Host "Dashboard is already running on port 1420"
}

$deadline = (Get-Date).AddSeconds(40)
while ((Get-Date) -lt $deadline -and -not (Test-Listening 1420)) {
    Start-Sleep -Milliseconds 500
}

Start-Process "http://localhost:1420/"
Write-Host "Dashboard: http://localhost:1420/"
Write-Host "Link WhatsApp from the WhatsApp page in that window."
