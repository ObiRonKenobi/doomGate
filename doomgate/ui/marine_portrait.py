"""
Marine status portrait (bottom-right HUD): Doom-style pixel mug with named frame groups.

Place PNGs under assets/ui/ — see assets/ui/MARINE_PORTRAIT_README.md for filenames and prompts.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

import pygame

from doomgate.game import get_flag

# Animation: idle glances cycle slowly; "scared" (low plasma fill) cycles faster.
IDLE_GLANCE_CYCLE_MS = 2600
SCARED_GLANCE_CYCLE_MS = 820
# Active lantern charge under this fraction → scared expression + faster glances
LOW_PLASMA_FILL = 0.40


@dataclass
class MarinePortraitAtlas:
    idle: List[pygame.Surface]
    scared: List[pygame.Surface]
    excited: List[pygame.Surface]
    dead: List[pygame.Surface]


def _sorted_png_group(
    ui_dir: str, name_prefix: str, try_load_png: Callable[[str], Optional[pygame.Surface]]
) -> List[pygame.Surface]:
    """Load assets/ui/{name_prefix}*.png sorted by filename."""
    if not os.path.isdir(ui_dir):
        return []
    names = sorted(
        fn for fn in os.listdir(ui_dir) if fn.lower().startswith(name_prefix.lower()) and fn.lower().endswith(".png")
    )
    out: List[pygame.Surface] = []
    for fn in names:
        p = os.path.join(ui_dir, fn)
        surf = try_load_png(p)
        if surf is not None:
            out.append(surf)
    return out


def load_marine_portrait_atlas(
    ui_dir: str,
    try_load_png: Callable[[str], Optional[pygame.Surface]],
) -> Optional[MarinePortraitAtlas]:
    """
    Load grouped frames. If no marine_portrait_* files exist, returns None (caller uses legacy player_face_*.png).
    """
    idle = _sorted_png_group(ui_dir, "marine_portrait_idle_", try_load_png)
    scared = _sorted_png_group(ui_dir, "marine_portrait_scared_", try_load_png)
    excited = _sorted_png_group(ui_dir, "marine_portrait_excited_", try_load_png)
    dead = _sorted_png_group(ui_dir, "marine_portrait_dead_", try_load_png)

    if not idle and not scared and not excited and not dead:
        return None

    # Minimal fallbacks so logic never indexes an empty list
    if not idle:
        idle = dead or excited or scared
    if not scared:
        scared = idle
    if not excited:
        excited = idle[:1]
    if not dead:
        dead = idle[:1]

    return MarinePortraitAtlas(
        idle=list(idle),
        scared=list(scared),
        excited=list(excited),
        dead=list(dead),
    )


def _pick_cycle(frames: List[pygame.Surface], ticks_ms: int, cycle_ms: int) -> pygame.Surface:
    if not frames:
        raise RuntimeError("marine portrait: empty frame list")
    if cycle_ms <= 0:
        return frames[0]
    i = (ticks_ms // cycle_ms) % len(frames)
    return frames[i]


def pick_marine_portrait_surface(
    atlas: Optional[MarinePortraitAtlas],
    ticks_ms: int,
    state: Dict[str, Any],
    plasma_fill_01: float,
) -> Optional[pygame.Surface]:
    """
    Choose which portrait surface to draw. Returns None if atlas is None (use legacy indexing).
    """
    if atlas is None:
        return None

    if not state.get("alive", True):
        # In-game death should hold on dead_00 until restart/load.
        return atlas.dead[0]

    # Plot: you survive long enough to seal the gate, then die in the aftermath.
    # So: when the game is won, show the "dead" / beaten portraits too.
    if get_flag(state, "gameWon"):
        # Victory death image: prefer dead_01 if it exists, else fall back to dead_00.
        return atlas.dead[1] if len(atlas.dead) > 1 else atlas.dead[0]
    if state.get("godMode"):
        return atlas.idle[0]

    excited_until = int(state.get("portraitExcitedUntil", 0))
    if ticks_ms < excited_until and atlas.excited:
        return atlas.excited[ticks_ms // 200 % len(atlas.excited)]

    # Match orb drain: active lantern segment under 40% full → scared + faster glances (includes last charge nearly empty).
    low_plasma = plasma_fill_01 < LOW_PLASMA_FILL
    if low_plasma:
        return _pick_cycle(atlas.scared, ticks_ms, SCARED_GLANCE_CYCLE_MS)

    return _pick_cycle(atlas.idle, ticks_ms, IDLE_GLANCE_CYCLE_MS)


def legacy_player_face_frame_index(state: Dict[str, Any], game: Dict[str, Any]) -> int:
    """Original stress-based index when only player_face_*.png strip exists."""
    if get_flag(state, "gameWon"):
        return 0
    if state.get("godMode"):
        return 0
    if not state["alive"]:
        return 5
    ap = int(game["meta"]["actionsPerLantern"])
    ud = max(0, ap - (state["actions"] % ap))
    if state["lanterns"] <= 1 and state["alive"]:
        if state["lanterns"] == 0:
            return 5
        if ud <= ap // 3:
            return 4
        return 3
    if state["lanterns"] == 2 and ud <= ap // 4:
        return 2
    return 1 if state["lanterns"] <= 2 else 0
