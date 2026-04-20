# DOOMGATE: The Warlock's Crucible (Python / Pygame)

This is a retro-inspired, Shadowgate-style point-and-click adventure implemented in **Python + Pygame**. (An early single-file browser prototype was removed; all game data and logic live in `main.py`.)

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

- Click a **command** (LOOK / TAKE / USE / TALK / OPEN / COMBINE / SAVE / LOAD)
- Click hotspots in the **viewport** to apply that command
- Click inventory items to hold them (for USE / OPEN logic)
- To craft/charge/build things: select **COMBINE**, then click two inventory items
- **Scroll the text log** with the mouse wheel (or drag the scrollbar)
- **F3** toggles **hotspot debug** overlays (use to line up doors with your room PNGs)
- The window is **resizable / maximizable**; the layout reflows to fit

## Art assets (optional)

- **In-game music (looped)**: put **`gameplay.wav`** in **`assets/music/`** (alternatives: `gameplay.ogg`, `gameplay.mp3`, or stems `game` / `ambient` / `ingame` with the same extensions). The **MUSIC** button on the right panel toggles playback.
- **Title screen (opening)**: put a wide pixel-art image in **`assets/title/`**. Recognized names (any of **`.png` `.jpg` `.jpeg` `.webp` `.bmp`**): `crucible_exterior`, `title`, or `title_screen` — e.g. **`crucible_exterior.jpg`**. Any other image file in that folder is used if the preferred names are missing. The image is scaled to fill the window with a light dim behind the text.
- **Room backgrounds**: `assets/rooms/<roomId>.png` (e.g. `hangar.png`, `hellGateChamber.png`)
- **Props** (for objects not drawn in the room): `assets/props/<hotspotId>.png`
- **Inventory icons** (pickup popup + preview): `assets/items/<itemId>.png`  
  See `HOTSPOT_CALIBRATION.md` for aligning click areas with your art.

## Save/Load

- SAVE/LOAD buttons persist state to `savegame.json` in the game folder.


Rip and Tear!
~ rbyt3r
