Param([switch]$Headless)

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

# xkcd-mcp â€” backend 10778 + Vite 10779
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

foreach ($p in 10778, 10779) {
    Get-NetTCPConnection -LocalPort $p -ErrorAction SilentlyContinue |
        ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
}

Start-Process -FilePath "uv" -ArgumentList "run", "xkcd-mcp", "--serve" -WorkingDirectory $root -WindowStyle Hidden
Start-Sleep -Seconds 2

Set-Location $PSScriptRoot
if (-not (Test-Path "node_modules")) {
    npm install
}
# 4b. Launch background task to open browser once frontend is ready (Auto-opened by Antigravity)
$frontendUrl = "http://127.0.0.1:10779/"
$pollAndOpen = "for (`$i = 0; `$i -lt 60; `$i++) { try { `$null = Invoke-WebRequest -Uri '$frontendUrl' -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; Start-Process '$frontendUrl'; exit } catch { Start-Sleep -Seconds 1 } }"
Start-Process powershell -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-Command", $pollAndOpen

Write-Host "Browser will open automatically when Vite is ready." -ForegroundColor Gray
npm run dev

