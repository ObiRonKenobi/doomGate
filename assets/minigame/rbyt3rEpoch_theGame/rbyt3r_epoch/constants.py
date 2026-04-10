"""Screen size, weapons, and palette for the arcade mini-game."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600

FPS = 60


class WeaponType(str, Enum):
    SWORD = "SWORD"
    PISTOL = "PISTOL"
    SHOTGUN = "SHOTGUN"
    PLASMA = "PLASMA"
    MINIGUN = "MINIGUN"
    ROCKET = "ROCKET"
    BFG = "BFG"


@dataclass
class Weapon:
    type: WeaponType
    damage: float
    fire_rate: int  # ms between shots
    bullet_speed: float
    color: tuple[int, int, int]
    spread: float = 0.0
    count: int = 1


SWORD_WEAPON = Weapon(
    type=WeaponType.SWORD,
    damage=35,
    fire_rate=350,
    bullet_speed=0,
    color=(226, 232, 240),
)

PISTOL_WEAPON = Weapon(
    type=WeaponType.PISTOL,
    damage=15,
    fire_rate=200,
    bullet_speed=12,
    color=(255, 255, 255),
)

SHOTGUN_WEAPON = Weapon(
    type=WeaponType.SHOTGUN,
    damage=12,
    fire_rate=700,
    bullet_speed=10,
    color=(249, 115, 22),
    spread=0.4,
    count=6,
)

PLASMA_WEAPON = Weapon(
    type=WeaponType.PLASMA,
    damage=50,
    fire_rate=900,
    bullet_speed=6,
    color=(168, 85, 247),
)

MINIGUN_WEAPON = Weapon(
    type=WeaponType.MINIGUN,
    damage=8,
    fire_rate=100,
    bullet_speed=14,
    color=(251, 191, 36),
)

ROCKET_WEAPON = Weapon(
    type=WeaponType.ROCKET,
    damage=28,
    fire_rate=820,
    bullet_speed=6,
    color=(255, 120, 40),
)

BFG_WEAPON = Weapon(
    type=WeaponType.BFG,
    damage=9999,
    fire_rate=2200,
    bullet_speed=9,
    color=(74, 222, 128),
)


# All firearms offered from armory picks (BFG is a separate milestone unlock).
STANDARD_ARMORY_GUNS = frozenset(
    {
        WeaponType.PISTOL,
        WeaponType.SHOTGUN,
        WeaponType.PLASMA,
        WeaponType.MINIGUN,
        WeaponType.ROCKET,
    }
)


# RGB
BG = (2, 6, 23)
GRID = (15, 23, 42)
