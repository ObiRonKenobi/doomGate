# Aligning clickable hotspots with your room art

Room backgrounds are full images. Exits and doors are usually **already drawn** in the art, so the game uses **invisible hitboxes** only (no overlay sprite). Objects not in the art can use **sprites** in `assets/props/<hotspotId>.png`.

## How hotspots work

Each hotspot has a `rect` in **percent of the viewport** (0–100):

- `l` — left edge (% from viewport left)
- `t` — top edge (% from viewport top)
- `w` — width (% of viewport width)
- `h` — height (% of viewport height)

These map to whatever size the window is after you resize or maximize.

## Calibrating a door or exit

1. Run the game and enter the room.
2. Press **F3** to toggle **hotspot debug** (green tinted rectangles + borders).
3. Adjust the numbers in `main.py` inside `GAME["rooms"]` → that room’s `hotspots` list until the rectangle sits on the door drawn in your PNG.
4. Toggle **F3** off when done.

Tips:

- Start with a slightly **larger** box than the door so it’s easy to click; tighten later.
- If your generator uses a different framing (crop, letterbox), percentages are still valid—they’re relative to the **viewport**, which always fills the top image area.

## Optional: force an overlay sprite

For any hotspot you can set:

```python
"showSprite": True
```

Defaults:

- **`exit`** and **`barrier`**: no overlay sprite (hitbox only). Background shows the door.
- **Other kinds**: overlay sprite if `assets/props/<id>.png` exists, else procedural pixel icon.

## Inventory pickup art

Place pixel icons at:

`assets/items/<itemId>.png`

For example: `redKeycard.png`, `omegaCrystal.png`. If a file is missing, the acquire popup shows a **placeholder** with the item name.
