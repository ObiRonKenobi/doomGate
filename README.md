# DOOMGATE: The Warlock's Crucible (Python / Pygame)

This is a retro-inspired, Shadowgate-style point-and-click adventure implemented in **Python + Pygame**.

## Run

1. Install Python 3.10+.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the game:

```bash
python main.py
```

A **title screen** appears first: press **any key** or **click** (“Press Any Key to RIP AND TEAR!”). **ESC** quits (also from the title screen).

## Controls (mouse-only)

- Click a **command** (LOOK / TAKE / USE / TALK / OPEN / CLOSE / SAVE / LOAD)
- Click hotspots in the **viewport** to apply that command
- Click inventory items to hold them (for USE / OPEN logic and item combinations)
- **Scroll the text log** with the mouse wheel (or drag the scrollbar)
- **F3** toggles **hotspot debug** overlays (use to line up doors with your room PNGs)
- The window is **resizable / maximizable**; the layout reflows to fit

## Art assets (optional)

- **Room backgrounds**: `assets/rooms/<roomId>.png` (e.g. `hangar.png`, `hellGateChamber.png`)
- **Props** (for objects not drawn in the room): `assets/props/<hotspotId>.png`
- **Inventory icons** (pickup popup + preview): `assets/items/<itemId>.png`  
  See `HOTSPOT_CALIBRATION.md` for aligning click areas with your art.

## Save/Load

- SAVE/LOAD buttons persist state to `savegame.json` in the game folder.

