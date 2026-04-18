$ErrorActionPreference = "Stop"

Set-Location (Resolve-Path (Join-Path $PSScriptRoot ".."))

New-Item -ItemType Directory -Force dist | Out-Null

python -m PyInstaller `
  --noconfirm `
  --clean `
  --onedir `
  --name DoomGate `
  --collect-all pygame `
  --hidden-import doomgate `
  --hidden-import doomgate.ui_runtime `
  --add-data "assets;assets" `
  main.py

Write-Host ""
Write-Host "Built onedir -> dist\DoomGate"
Write-Host "Zip dist\DoomGate for friends."
