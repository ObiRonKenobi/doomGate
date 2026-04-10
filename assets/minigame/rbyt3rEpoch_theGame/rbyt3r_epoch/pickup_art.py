"""
Rudimentary pixel-art style pickup sprites for RBYT3R Epoch (cached surfaces).
"""

from __future__ import annotations

from typing import Optional

import pygame

_HEALTH: Optional[pygame.Surface] = None
_WEAPON: Optional[pygame.Surface] = None


def surface_for_powerup(pu_type: str) -> pygame.Surface:
    """WEAPON_UPGRADE = weapon kit; HEALTH = medkit-style cross."""
    if pu_type == "HEALTH":
        return _health_medkit()
    return _weapon_crate()


def _health_medkit() -> pygame.Surface:
    global _HEALTH
    if _HEALTH is not None:
        return _HEALTH
    # Base pixel grid (chunky), then scale up with nearest for retro look
    w, h = 14, 14
    low = pygame.Surface((w, h), pygame.SRCALPHA)
    cx, cy = w // 2, h // 2
    r = 6
    for y in range(h):
        for x in range(w):
            d2 = (x - cx) ** 2 + (y - cy) ** 2
            if d2 <= r * r:
                # soft vignette: outer ring darker
                if d2 > (r - 2) * (r - 2):
                    low.set_at((x, y), (153, 27, 27, 255))
                elif d2 > (r - 4) * (r - 4):
                    low.set_at((x, y), (220, 38, 38, 255))
                else:
                    low.set_at((x, y), (248, 113, 113, 255))
    # White "+" (3 px arms on 14 grid)
    for i in range(-4, 5):
        x, y = cx + i, cy
        if 0 <= x < w and 0 <= y < h:
            low.set_at((x, y), (255, 255, 255, 255))
    for j in range(-4, 5):
        x, y = cx, cy + j
        if 0 <= x < w and 0 <= y < h:
            low.set_at((x, y), (255, 255, 255, 255))
    out = pygame.transform.scale(low, (26, 26))
    _HEALTH = out
    return out


def _weapon_crate() -> pygame.Surface:
    global _WEAPON
    if _WEAPON is not None:
        return _WEAPON
    low = pygame.Surface((14, 14), pygame.SRCALPHA)
    # Mini "blaster" + ammo chip — reads at a glance vs plain dot
    # Barrel (horizontal)
    pygame.draw.rect(low, (120, 53, 15), (2, 6, 10, 4))
    pygame.draw.rect(low, (251, 191, 36), (3, 7, 8, 2))
    pygame.draw.rect(low, (254, 243, 199), (4, 7, 4, 1))
    # Grip
    pygame.draw.rect(low, (146, 64, 14), (10, 8, 2, 5))
    # Muzzle flash hint
    pygame.draw.rect(low, (253, 224, 71), (1, 7, 2, 2))
    out = pygame.transform.scale(low, (26, 26))
    _WEAPON = out
    return out
