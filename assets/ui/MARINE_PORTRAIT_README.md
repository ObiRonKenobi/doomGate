# Marine HUD portrait (bottom-right)

Pixel-art portraits for the Doom-style status face next to the plasma orb. Drop **PNG** files into this folder (`assets/ui/`).

## How many poses?

The engine cycles **sorted filenames** per group (`idle_*`, `scared_*`, etc.). Recommended set:

| Group | Count | Role |
|--------|------:|------|
| `marine_portrait_idle_*` | **3** | Neutral: center → glance left → glance right (slow cycle ~2.6s per step) |
| `marine_portrait_scared_*` | **3** | Scared + same three directions (fast cycle ~0.82s per step when orb charge **under 40%**) |
| `marine_portrait_excited_*` | **2** | Item pickup flash (~2.8s); two frames give a quick “bounce” when cycled fast |
| `marine_portrait_dead_*` | **1** | Defeat / death |

**Recommended total: 9 PNGs** (3 + 3 + 2 + 1).

**Minimum viable:** 8 files if you use only **one** excited frame (`marine_portrait_excited_00.png` only).

Optional extras: add `marine_portrait_excited_02.png` or a second `marine_portrait_dead_01.png` — the loader picks up any `*.png` matching the prefix, sorted by name.

## File names

| Output filename | Pose |
|-----------------|------|
| `marine_portrait_idle_00.png` | Idle — eyes forward |
| `marine_portrait_idle_01.png` | Idle — glance left |
| `marine_portrait_idle_02.png` | Idle — glance right |
| `marine_portrait_scared_00.png` | Scared — eyes forward |
| `marine_portrait_scared_01.png` | Scared — glance left |
| `marine_portrait_scared_02.png` | Scared — glance right |
| `marine_portrait_excited_00.png` | Excited — primary |
| `marine_portrait_excited_01.png` | Excited — alternate |
| `marine_portrait_dead_00.png` | Dead — beaten / bloody |

If **no** `marine_portrait_*.png` files exist, the game falls back to optional `player_face_*.png`, then the built-in placeholder.

## Art rules (all images)

- **Style:** Dark **Doom (1993) HUD** pixel art, chunky readable pixels, limited palette, high contrast, bust-up portrait centered for a circular crop.
- **Gear:** Marine **helmet** with a **large open glass face panel** (visor open or raised) so the **face reads clearly**.
- **Character:** Doomguy energy; **black hair**; **black-framed glasses** (same design in every frame).
- **Size:** About **128×128 to 256×256** px, square.
- **Transparency:** Final PNG must have a **real alpha channel**. Checkerboard in the prompt is only for authoring preview in Gemini—remove it in export or use color-to-alpha on the checker colors if the model bakes them in.

---

## Gemini-ready prompts (one per image)

Use **image generation**. Generate **one image per prompt**; save with the filename in the heading. Each prompt is **standalone** (full style block repeated for consistency).

---

### 1 — `marine_portrait_idle_00.png`

Pixel art HUD portrait, dark Doom 1993 aesthetic, chunky retro game sprite, limited palette, high contrast, bust-up, centered composition that fits a circle crop, square canvas, transparent background (no checkerboard in final export). Doom marine tactical helmet with a large open glass face panel; face fully visible. Same character in all frames: Doomguy-style marine, short black hair, black rectangular glasses. Neutral determined expression, eyes looking straight ahead, slight stern frown, subtle green rim light optional.

---

### 2 — `marine_portrait_idle_01.png`

Pixel art HUD portrait, dark Doom 1993 aesthetic, chunky retro game sprite, limited palette, high contrast, bust-up, centered composition that fits a circle crop, square canvas, transparent background (no checkerboard in final export). Same marine as idle_00: open glass face panel, black hair, black rectangular glasses. Head turned slightly left, eyes glancing left, neutral mouth, classic Doom status-bar “looking around” feel.

---

### 3 — `marine_portrait_idle_02.png`

Pixel art HUD portrait, dark Doom 1993 aesthetic, chunky retro game sprite, limited palette, high contrast, bust-up, centered composition that fits a circle crop, square canvas, transparent background (no checkerboard in final export). Same marine as idle_00: open glass face panel, black hair, black rectangular glasses. Head turned slightly right, eyes glancing right, neutral mouth.

---

### 4 — `marine_portrait_scared_00.png`

Pixel art HUD portrait, dark Doom 1993 aesthetic, chunky retro game sprite, limited palette, high contrast, bust-up, centered composition that fits a circle crop, square canvas, transparent background (no checkerboard in final export). Same marine design: open face panel, black hair, black glasses. **Scared** expression: wide eyes, raised brows, slightly open mouth, pale stress, dark shadows under eyes; eyes forward as if something is wrong in front of you.

---

### 5 — `marine_portrait_scared_01.png`

Pixel art HUD portrait, dark Doom 1993 aesthetic, chunky retro game sprite, limited palette, high contrast, bust-up, centered composition that fits a circle crop, square canvas, transparent background (no checkerboard in final export). Same scared marine: open face panel, black hair, black glasses. Head tilted left, eyes darting left, fear, clenched or tight mouth, sweating optional.

---

### 6 — `marine_portrait_scared_02.png`

Pixel art HUD portrait, dark Doom 1993 aesthetic, chunky retro game sprite, limited palette, high contrast, bust-up, centered composition that fits a circle crop, square canvas, transparent background (no checkerboard in final export). Same scared marine: open face panel, black hair, black glasses. Head tilted right, eyes darting right, fear, clenched jaw.

---

### 7 — `marine_portrait_excited_00.png`

Pixel art HUD portrait, dark Doom 1993 aesthetic, chunky retro game sprite, limited palette, high contrast, bust-up, centered composition that fits a circle crop, square canvas, transparent background (no checkerboard in final export). Same marine: open face panel, black hair, black glasses. **Excited** expression: big grin, eyebrows up, eyes wide, slight head tilt, “just looted something good” energy.

---

### 8 — `marine_portrait_excited_01.png`

Pixel art HUD portrait, dark Doom 1993 aesthetic, chunky retro game sprite, limited palette, high contrast, bust-up, centered composition that fits a circle crop, square canvas, transparent background (no checkerboard in final export). Same marine and excited mood: open face panel, black hair, black glasses. Alternate excited pose: eyes squeezed in a fierce happy squint, teeth showing, fist pump not visible (face only), energetic.

---

### 9 — `marine_portrait_dead_00.png`

Pixel art HUD portrait, dark Doom 1993 aesthetic, chunky retro game sprite, limited palette, high contrast, bust-up, centered composition that fits a circle crop, square canvas, transparent background (no checkerboard in final export). Same marine identity: open or cracked face panel, black hair, black glasses **damaged or askew**. **Defeated**: blood on face, one eye half closed, pain and exhaustion, messy hair, dark blood splatter, no gore porn—readable Doom-style hurt face.

---

## Engine behaviour

- **Idle:** cycles `idle_*` slowly (classic Doom glance).
- **Scared:** when **active lantern charge** in the orb is **under 40%**, uses `scared_*` faster.
- **Excited:** for **~2.8s** after **gaining an item**.
- **Dead:** when the player is dead.

Tunables: `doomgate/ui/marine_portrait.py` (`LOW_PLASMA_FILL`, cycle ms), `PORTRAIT_EXCITED_MS` in `ui_runtime.py`.
