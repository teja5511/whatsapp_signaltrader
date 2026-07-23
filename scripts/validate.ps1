# WhatsApp MT5 Trading Bot - Workspace Validation Script
$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Running Monorepo Workspace Validation..." -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$WorkspaceRoot = Get-Location
$Failed = $false

# 1. Verify Required Documentation Files
Write-Host "[1/4] Verifying Documentation Files..." -ForegroundColor Yellow
$RequiredDocs = @(
    "README.md",
    "docs/REQUIREMENTS.md",
    "docs/ARCHITECTURE.md",
    "docs/TRADING_RULES.md",
    "docs/COMMAND_CLASSIFICATION.md",
    "docs/CAMPAIGN_STATE_MACHINE.md",
    "docs/DATA_MODEL.md",
    "docs/SECURITY_AND_SAFETY.md",
    "docs/ACCEPTANCE_CRITERIA.md",
    "docs/OPEN_DECISIONS.md",
    "docs/IMPLEMENTATION_ROADMAP.md",
    "docs/ASSUMPTIONS.md"
)

foreach ($doc in $RequiredDocs) {
    $fullPath = Join-Path $WorkspaceRoot $doc
    if (Test-Path $fullPath) {
        Write-Host "  [OK] $doc" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] Missing $doc" -ForegroundColor Red
        $Failed = $true
    }
}

# 2. Verify Monorepo Workspace Packages
Write-Host "`n[2/4] Verifying Monorepo Workspace Packages..." -ForegroundColor Yellow
$RequiredPackages = @(
    "packages/contracts/package.json",
    "packages/ui/package.json",
    "packages/parser-fixtures/package.json",
    "apps/whatsapp-worker/package.json",
    "apps/trading-service/pyproject.toml",
    "apps/desktop/package.json"
)

foreach ($pkg in $RequiredPackages) {
    $fullPath = Join-Path $WorkspaceRoot $pkg
    if (Test-Path $fullPath) {
        Write-Host "  [OK] $pkg" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] Missing $pkg" -ForegroundColor Red
        $Failed = $true
    }
}

# 3. Test Python Trading Service Pytest
Write-Host "`n[3/4] Running Python Trading Service Tests (pytest)..." -ForegroundColor Yellow
try {
    $TradingServicePath = Join-Path $WorkspaceRoot "apps\trading-service"
    $env:PYTHONPATH = "$TradingServicePath"
    python -m pytest "$TradingServicePath\tests"
    Write-Host "  [OK] Python Pytest Suite Passed" -ForegroundColor Green
} catch {
    Write-Host "  [FAIL] Pytest Suite Failed" -ForegroundColor Red
    $Failed = $true
}

# 4. Summary
Write-Host "`n============================================================" -ForegroundColor Cyan
if ($Failed) {
    Write-Host " Workspace Validation FAILED!" -ForegroundColor Red
    Exit 1
} else {
    Write-Host " Workspace Validation PASSED! All packages & tests healthy." -ForegroundColor Green
}
Write-Host "============================================================" -ForegroundColor Cyan
