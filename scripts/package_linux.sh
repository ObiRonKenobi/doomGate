#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

mkdir -p dist

python -m PyInstaller \
  --noconfirm \
  --clean \
  --onedir \
  --name DoomGate \
  --collect-all pygame \
  --hidden-import doomgate \
  --hidden-import doomgate.ui_runtime \
  --add-data "assets:assets" \
  main.py

echo ""
echo "Built onedir -> dist/DoomGate"
echo "tar czf dist/DoomGate_linux.tar.gz -C dist DoomGate"
