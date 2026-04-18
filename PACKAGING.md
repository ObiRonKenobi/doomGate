# Packaging DoomGate (Windows + Linux)

This repo is a Python + Pygame project. For friend testing and later Steam, the usual approach is **PyInstaller** producing:

- Windows: a folder build (`onedir`) zipped for distribution
- Linux: a folder build (`onedir`) tar.gz’d for distribution

The codebase already supports frozen builds via `sys._MEIPASS` / `sys.frozen` in `doomgate/util/paths.py`.

## Prereqs

### Both platforms

- Python **3.11+** recommended (match whatever you build with)
- Install deps:

```bash
python -m pip install -r requirements.txt
python -m pip install pyinstaller
```

### Linux runtime libs (distro-specific)

Pygame needs SDL2-ish system libraries on Linux (names vary by distro). On Debian/Ubuntu-ish systems you commonly install packages like:

- `libsdl2-2.0-0`
- `libsdl2-image-2.0-0`
- `libsdl2-mixer-2.0-0`
- `libsdl2-ttf-2.0-0`

If audio fails on Linux, install mixer deps first.

## Quick builds

From the repository root:

- **Windows (PowerShell)**: `scripts/package_windows.ps1`
- **Linux (bash)**: `scripts/package_linux.sh`

Outputs are written to `dist/`.

## What players run

- Windows: `DoomGate.exe` inside the `DoomGate` output folder
- Linux: `DoomGate` inside the `DoomGate` output folder (you may need `chmod +x DoomGate` if the archive strips permissions)

## Common gotchas

- **Case sensitivity**: Linux file systems are case-sensitive. Keep asset paths consistent.
- **Do not commit user settings**: `audio_settings.json` is local; don’t ship your personal copy to friends.
- **Defender / SmartScreen (Windows)**: unsigned PyInstaller builds can trigger warnings. Code signing is a later “public release” step.

## Installers (optional, later)

- Windows: wrap the `onedir` folder with Inno Setup / NSIS if you want Start Menu shortcuts.
- Linux: `.deb`, Flatpak, or distro packages are optional; tarballs are typical for indie testing.
