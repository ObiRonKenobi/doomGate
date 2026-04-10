"""
RBYT3R Epoch — twin-stick style arcade mini-game (Pygame).

Designed so you can later embed it in another project by passing a surface
and draw rectangle (see `Rbyt3rEpochGame` constructor).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field, replace
from enum import Enum, auto
from pathlib import Path
from typing import List, Optional

import pygame

from .constants import (
    BG,
    BFG_WEAPON,
    CANVAS_HEIGHT,
    CANVAS_WIDTH,
    FPS,
    MINIGUN_WEAPON,
    PISTOL_WEAPON,
    PLASMA_WEAPON,
    ROCKET_WEAPON,
    SHOTGUN_WEAPON,
    STANDARD_ARMORY_GUNS,
    SWORD_WEAPON,
    Weapon,
    WeaponType,
)
from . import audio_synth as sfx
from . import leaderboard as lb
from .pickup_art import surface_for_powerup


class UIScreen(Enum):
    TITLE = auto()
    PLAYING = auto()
    DIALOGUE = auto()
    DEATH_CHOICE = auto()
    GAME_OVER = auto()
    INITIALS = auto()


Choice = str  # WEAPON, HEALTH, MAGIC, CHOOSE_*


@dataclass
class Vector:
    x: float
    y: float


@dataclass
class Player:
    id: str
    pos: Vector
    radius: float
    health: float
    max_health: float
    magic: float
    max_magic: float
    aether_charges: int
    max_aether_charges: int
    speed: float
    color: tuple[int, int, int]
    weapon: Weapon
    score: int
    rooms_cleared: int
    lives: int
    score_lives_claimed: int
    unlocked_weapons: List[Weapon] = field(default_factory=list)
    weapon_index: int = 0


@dataclass
class Enemy:
    id: str
    pos: Vector
    radius: float
    health: float
    max_health: float
    speed: float
    color: tuple[int, int, int]
    type: str  # BASIC, TANK, BOSS
    last_shot: float
    shoot_cooldown: float


@dataclass
class Bullet:
    id: str
    pos: Vector
    vel: Vector
    radius: float
    damage: float
    color: tuple[int, int, int]
    owner: str
    max_distance: Optional[float] = None
    distance_traveled: float = 0.0
    kind: str = "normal"
    fragment_at: Optional[float] = None
    prev_pos: Optional[Vector] = None


@dataclass
class PowerUp:
    id: str
    pos: Vector
    type: str
    radius: float


@dataclass
class Explosion:
    id: str
    pos: Vector
    radius: float
    max_radius: float
    duration: float
    start_time: float
    style: str = "plasma"  # plasma | rocket | rocket_frag (fixed AoE rings)


def spawn_enemies(room_num: int) -> List[Enemy]:
    is_boss_room = room_num % 6 == 0
    difficulty = 1 + (room_num * 0.15)

    if is_boss_room:
        return [
            Enemy(
                id=f"boss-{pygame.time.get_ticks()}",
                pos=Vector(x=CANVAS_WIDTH / 2, y=-100),
                radius=60,
                health=600 * difficulty,
                max_health=600 * difficulty,
                speed=0.3,
                color=(244, 63, 94),
                type="BOSS",
                last_shot=0.0,
                shoot_cooldown=1500 / difficulty,
            )
        ]

    count = 3 + int(room_num * 1.5)
    out: List[Enemy] = []
    for i in range(count):
        side = random.randint(0, 3)
        if side == 0:
            x, y = random.random() * CANVAS_WIDTH, -50.0
        elif side == 1:
            x, y = CANVAS_WIDTH + 50.0, random.random() * CANVAS_HEIGHT
        elif side == 2:
            x, y = random.random() * CANVAS_WIDTH, CANVAS_HEIGHT + 50.0
        else:
            x, y = -50.0, random.random() * CANVAS_HEIGHT

        is_tank = room_num >= 10 and (i == 0 or random.random() < 0.2)
        if is_tank:
            out.append(
                Enemy(
                    id=f"enemy-tank-{pygame.time.get_ticks()}-{i}",
                    pos=Vector(x=x, y=y),
                    radius=25,
                    health=60 * difficulty,
                    max_health=60 * difficulty,
                    speed=0.4 + random.random() * 0.2,
                    color=(34, 197, 94),
                    type="TANK",
                    last_shot=0.0,
                    shoot_cooldown=3000 / difficulty,
                )
            )
        else:
            out.append(
                Enemy(
                    id=f"enemy-{pygame.time.get_ticks()}-{i}",
                    pos=Vector(x=x, y=y),
                    radius=15,
                    health=30 * difficulty,
                    max_health=30 * difficulty,
                    speed=0.6 + random.random() * (0.3 + room_num * 0.02),
                    color=(239, 68, 68),
                    type="BASIC",
                    last_shot=0.0,
                    shoot_cooldown=2500 / difficulty,
                )
            )
    return out


def _point_segment_distance(px: float, py: float, x1: float, y1: float, x2: float, y2: float) -> float:
    vx, vy = x2 - x1, y2 - y1
    wx, wy = px - x1, py - y1
    c1 = vx * wx + vy * wy
    if c1 <= 0:
        return math.hypot(px - x1, py - y1)
    c2 = vx * vx + vy * vy
    if c2 <= c1:
        return math.hypot(px - x2, py - y2)
    t = c1 / (c2 or 1e-9)
    projx = x1 + t * vx
    projy = y1 + t * vy
    return math.hypot(px - projx, py - projy)


def _seg_hits_enemy(
    ax: float, ay: float, bx: float, by: float, ex: float, ey: float, enemy_r: float, bullet_r: float
) -> bool:
    return _point_segment_distance(ex, ey, ax, ay, bx, by) <= enemy_r + bullet_r


def _weapon_by_choice(choice: Choice) -> Weapon:
    return {
        "CHOOSE_PISTOL": PISTOL_WEAPON,
        "CHOOSE_SHOTGUN": SHOTGUN_WEAPON,
        "CHOOSE_PLASMA": PLASMA_WEAPON,
        "CHOOSE_MINIGUN": MINIGUN_WEAPON,
        "CHOOSE_ROCKET": ROCKET_WEAPON,
        "CHOOSE_BFG": BFG_WEAPON,
    }[choice]


def _weapon_types_from_unlocks(weapons: List[Weapon]) -> set:
    return {w.type for w in weapons}


def _all_standard_guns_unlocked(weapons: List[Weapon]) -> bool:
    return STANDARD_ARMORY_GUNS <= _weapon_types_from_unlocks(weapons)


class Rbyt3rEpochGame:
    """
    Standalone or embedded arcade session.

    If `surface` is None, creates an 800x600 window. If you embed this in
    another Pygame project, pass the parent's surface and `area` where the
    mini-game should be drawn; mouse coordinates are translated into that rect.
    """

    def __init__(
        self,
        surface: Optional[pygame.Surface] = None,
        area: Optional[pygame.Rect] = None,
        db_path: Optional[Path] = None,
    ) -> None:
        self._owns_display = surface is None
        if surface is None:
            pygame.init()
            pygame.display.set_caption("RBYT3R Epoch")
            self.screen = pygame.display.set_mode((CANVAS_WIDTH, CANVAS_HEIGHT))
            self.area = pygame.Rect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)
        else:
            self.area = area if area is not None else surface.get_rect()
            self.screen = surface.subsurface(self.area) if area is not None else surface
        self.db_path = db_path or Path(__file__).resolve().parent.parent / "leaderboard.db"

        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.SysFont("consolas", 14)
        self.font_med = pygame.font.SysFont("consolas", 18)
        self.font_large = pygame.font.SysFont("consolas", 28, bold=True)
        self.font_title = pygame.font.SysFont("consolas", 52, bold=True)

        self._sounds = sfx.try_load_sounds()

        self.ui = UIScreen.TITLE
        self.running = True

        self.player = self._new_player()
        self.enemies: List[Enemy] = spawn_enemies(1)
        self.bullets: List[Bullet] = []
        self.power_ups: List[PowerUp] = [
            PowerUp(
                id="initial-gun",
                pos=Vector(x=CANVAS_WIDTH / 2 + 100, y=CANVAS_HEIGHT / 2),
                type="WEAPON_UPGRADE",
                radius=10,
            )
        ]
        self.explosions: List[Explosion] = []
        self.room_number = 1
        self.is_game_over = False
        self.in_dialogue = False

        self.mouse_btn = False
        self.mouse_xy = (CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2)

        self.last_fire_time = 0.0
        self.last_space_time = 0.0
        self.melee_active_until = 0.0
        self.melee_angle = 0.0

        self.screen_shake = 0.0

        self.show_initials = False
        self.initials_buffer = ""
        self.dialogue_weapon_options: List[tuple[str, str, str]] = []

        self._rocket_swirl_phase = 0.0
        self._time_ms = 0.0

    def _new_player(self) -> Player:
        start = [SWORD_WEAPON]
        return Player(
            id="player",
            pos=Vector(x=CANVAS_WIDTH / 2, y=CANVAS_HEIGHT / 2),
            radius=15,
            health=100,
            max_health=100,
            magic=0,
            max_magic=100,
            aether_charges=0,
            max_aether_charges=1,
            speed=4.0,
            color=(16, 185, 129),
            weapon=SWORD_WEAPON,
            score=0,
            rooms_cleared=0,
            lives=0,
            score_lives_claimed=0,
            unlocked_weapons=start,
            weapon_index=0,
        )

    def _cycle_weapon_slot(self, delta: int) -> None:
        p = self.player
        n = len(p.unlocked_weapons)
        if n <= 1:
            return
        idx = (p.weapon_index + delta) % n
        w = p.unlocked_weapons[idx]
        self.player = replace(p, weapon=w, weapon_index=idx)

    def _ensure_pistol_unlock(self, p: Player) -> Player:
        for i, w in enumerate(p.unlocked_weapons):
            if w.type == WeaponType.PISTOL:
                return replace(p, weapon=p.unlocked_weapons[i], weapon_index=i)
        uw = list(p.unlocked_weapons) + [PISTOL_WEAPON]
        return replace(p, weapon=PISTOL_WEAPON, unlocked_weapons=uw, weapon_index=len(uw) - 1)

    def _sfx_fire(self, wt: WeaponType) -> None:
        s = self._sounds
        if s is None:
            return
        if wt == WeaponType.SWORD:
            s.swoosh.play()
        elif wt == WeaponType.SHOTGUN:
            s.pew_shotgun.play()
        elif wt == WeaponType.PLASMA:
            s.pew_plasma.play()
        elif wt == WeaponType.MINIGUN:
            s.pew_light.play()
        elif wt == WeaponType.ROCKET:
            s.pew_heavy.play()
        elif wt == WeaponType.BFG:
            s.pew_bfg.play()
        else:
            s.pew_mid.play()

    def _sfx_kill(self) -> None:
        if self._sounds is not None:
            self._sounds.boom.play()

    def _sfx_doof(self) -> None:
        if self._sounds is not None:
            self._sounds.doof.play()

    def _sfx_warning(self) -> None:
        if self._sounds is not None:
            self._sounds.warning.play()

    def _sfx_death_scream(self) -> None:
        if self._sounds is not None:
            self._sounds.death_scream.play()

    ROCKET_BLAST_RADIUS = 40.0
    ROCKET_FRAG_BLAST_RADIUS = 20.0
    PLASMA_PROJ_RADIUS_REF = 12.0

    def _spawn_rocket_frag_detonation(
        self,
        impact: Vector,
        time: float,
        new_explosions: List[Explosion],
    ) -> None:
        r = self.ROCKET_FRAG_BLAST_RADIUS
        new_explosions.append(
            Explosion(
                id=f"rkf-blast-{time}-{random.random()}",
                pos=Vector(impact.x, impact.y),
                radius=r,
                max_radius=r,
                duration=340,
                start_time=time,
                style="rocket_frag",
            )
        )

    def _spawn_rocket_detonation(
        self,
        impact: Vector,
        vel: Vector,
        rocket_damage: float,
        time: float,
        new_explosions: List[Explosion],
        new_bullets: List[Bullet],
        active_ids: Optional[set] = None,
    ) -> None:
        """Primary AoE (~50% of plasma 80px), three rim frags with rotating clock placement."""
        br = self.ROCKET_BLAST_RADIUS
        frag_r = max(2.0, self.PLASMA_PROJ_RADIUS_REF * 0.15)
        frag_dmg = rocket_damage * 1.15
        self._rocket_swirl_phase += math.tau / 12

        new_explosions.append(
            Explosion(
                id=f"rk-blast-{time}-{random.random()}",
                pos=Vector(impact.x, impact.y),
                radius=br,
                max_radius=br,
                duration=420,
                start_time=time,
                style="rocket",
            )
        )
        aim = math.atan2(vel.y, vel.x) if (vel.x * vel.x + vel.y * vel.y) > 1e-6 else 0.0
        base = aim + self._rocket_swirl_phase
        for k in range(3):
            ang = base + k * (math.tau / 3)
            sx = impact.x + math.cos(ang) * br
            sy = impact.y + math.sin(ang) * br
            ox, oy = math.cos(ang), math.sin(ang)
            tx, ty = -oy, ox
            sp = 5.0
            tw = 2.5
            fid = f"rkfrag-{time}-{k}-{random.random()}"
            new_bullets.append(
                Bullet(
                    id=fid,
                    pos=Vector(sx, sy),
                    vel=Vector(ox * sp + tx * tw, oy * sp + ty * tw),
                    radius=frag_r,
                    damage=frag_dmg,
                    color=(255, 140, 55),
                    owner="PLAYER",
                    max_distance=55,
                    distance_traveled=0,
                    kind="rocket_frag",
                )
            )
            if active_ids is not None:
                active_ids.add(fid)

    def _award_score_life_milestones(self, p: Player) -> Player:
        m = p.score // 1000
        if m <= p.score_lives_claimed:
            return p
        gained = m - p.score_lives_claimed
        return replace(p, lives=p.lives + gained, score_lives_claimed=m)

    def _death_choice_continue(self) -> None:
        p = self.player
        if p.lives <= 0 or self.ui != UIScreen.DEATH_CHOICE:
            return
        self.player = replace(p, lives=p.lives - 1, health=p.max_health)
        self.bullets = []
        self.screen_shake = 0.0
        self.ui = UIScreen.PLAYING

    def _death_choice_rects(self) -> tuple[pygame.Rect, pygame.Rect]:
        return (
            pygame.Rect(100, 300, 260, 76),
            pygame.Rect(CANVAS_WIDTH - 360, 300, 260, 76),
        )

    def _click_death_choice(self, lx: float, ly: float) -> None:
        cont, quit_r = self._death_choice_rects()
        if cont.collidepoint(lx, ly):
            self._death_choice_continue()
        elif quit_r.collidepoint(lx, ly):
            self._reset_run_to_title()

    def _to_local(self, pos: tuple[int, int]) -> tuple[float, float]:
        x, y = pos
        return (x - self.area.x, y - self.area.y)

    def _translate_mouse(self) -> None:
        if pygame.mouse.get_focused():
            self.mouse_xy = self._to_local(pygame.mouse.get_pos())

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                # Quit back to parent (e.g. DoomGate) from any screen — standalone subprocess run.
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.running = False
                    continue
                if self.ui == UIScreen.DEATH_CHOICE:
                    if event.key == pygame.K_1:
                        self._death_choice_continue()
                    elif event.key == pygame.K_2:
                        self._reset_run_to_title()
                    continue
                if (
                    self.ui == UIScreen.PLAYING
                    and not self.is_game_over
                    and not self.in_dialogue
                ):
                    if event.key == pygame.K_UP:
                        self._cycle_weapon_slot(-1)
                        continue
                    if event.key == pygame.K_DOWN:
                        self._cycle_weapon_slot(1)
                        continue
                if self.ui == UIScreen.INITIALS:
                    self._initials_keydown(event)
                elif self.ui == UIScreen.DIALOGUE:
                    self._dialogue_keydown(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.mouse_btn = True
                    self._click_ui(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_btn = False
            elif event.type == pygame.MOUSEMOTION:
                self._translate_mouse()
            elif event.type == pygame.MOUSEWHEEL:
                if (
                    self.ui == UIScreen.PLAYING
                    and not self.is_game_over
                    and not self.in_dialogue
                ):
                    if event.y > 0:
                        self._cycle_weapon_slot(-1)
                    elif event.y < 0:
                        self._cycle_weapon_slot(1)

        self._translate_mouse()

    def _click_ui(self, pos: tuple[int, int]) -> None:
        lx, ly = self._to_local(pos)
        if self.ui == UIScreen.TITLE:
            r = pygame.Rect(CANVAS_WIDTH // 2 - 120, CANVAS_HEIGHT // 2 + 40, 240, 50)
            if r.collidepoint(lx, ly):
                self._start_game()
        elif self.ui == UIScreen.GAME_OVER and not self.show_initials:
            r = pygame.Rect(CANVAS_WIDTH // 2 - 150, CANVAS_HEIGHT // 2 + 40, 300, 50)
            if r.collidepoint(lx, ly):
                self._restart()
        elif self.ui == UIScreen.DIALOGUE:
            self._click_dialogue(lx, ly)
        elif self.ui == UIScreen.DEATH_CHOICE:
            self._click_death_choice(lx, ly)

    def _click_dialogue(self, lx: float, ly: float) -> None:
        rn = self.room_number
        is_weapon = rn % 5 == 0
        if is_weapon:
            for i, rect in enumerate(self._dialogue_weapon_rects()):
                if rect.collidepoint(lx, ly):
                    choice = self.dialogue_weapon_options[i][0]
                    self._apply_choice(choice)
                    return
        else:
            rects = self._dialogue_standard_rects()
            labels = ["WEAPON", "HEALTH", "MAGIC"]
            for i, r in enumerate(rects):
                if r.collidepoint(lx, ly):
                    self._apply_choice(labels[i])
                    return

    def _dialogue_weapon_rects(self) -> List[pygame.Rect]:
        return [
            pygame.Rect(150, 260, 220, 72),
            pygame.Rect(CANVAS_WIDTH - 370, 260, 220, 72),
        ]

    def _dialogue_standard_rects(self) -> List[pygame.Rect]:
        return [
            pygame.Rect(80, 260, 200, 72),
            pygame.Rect(300, 260, 200, 72),
            pygame.Rect(520, 260, 200, 72),
        ]

    def _dialogue_keydown(self, event: pygame.event.Event) -> None:
        rn = self.room_number
        is_weapon = rn % 5 == 0
        if event.key == pygame.K_1:
            if is_weapon and len(self.dialogue_weapon_options) >= 1:
                self._apply_choice(self.dialogue_weapon_options[0][0])
            elif not is_weapon:
                self._apply_choice("WEAPON")
        elif event.key == pygame.K_2:
            if is_weapon and len(self.dialogue_weapon_options) >= 2:
                self._apply_choice(self.dialogue_weapon_options[1][0])
            elif not is_weapon:
                self._apply_choice("HEALTH")
        elif event.key == pygame.K_3 and not is_weapon:
            self._apply_choice("MAGIC")

    def _initials_keydown(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_BACKSPACE:
            self.initials_buffer = self.initials_buffer[:-1]
        elif event.key == pygame.K_RETURN and len(self.initials_buffer) == 3:
            try:
                lb.submit_score(self.db_path, self.initials_buffer, self.player.score)
            except ValueError:
                pass
            self.show_initials = False
            self.ui = UIScreen.GAME_OVER
        elif event.unicode and len(event.unicode) == 1 and event.unicode.isalpha():
            if len(self.initials_buffer) < 3:
                self.initials_buffer += event.unicode.upper()

    def _bootstrap_new_run(self) -> None:
        self.player = self._new_player()
        self.enemies = spawn_enemies(1)
        self.bullets = []
        self.power_ups = [
            PowerUp(
                id="initial-gun",
                pos=Vector(x=CANVAS_WIDTH / 2 + 100, y=CANVAS_HEIGHT / 2),
                type="WEAPON_UPGRADE",
                radius=10,
            )
        ]
        self.explosions = []
        self.room_number = 1
        self.is_game_over = False
        self.in_dialogue = False
        self.show_initials = False

    def _start_game(self) -> None:
        self._bootstrap_new_run()
        self.ui = UIScreen.PLAYING

    def _reset_run_to_title(self) -> None:
        self._bootstrap_new_run()
        self.ui = UIScreen.TITLE

    def _restart(self) -> None:
        self._reset_run_to_title()

    def _open_dialogue_weapon_options(self) -> None:
        p = self.player
        if _all_standard_guns_unlocked(p.unlocked_weapons):
            opts = [
                ("CHOOSE_BFG", "BFG 9000", "Huge green bolt — vaporizes its lane"),
                ("CHOOSE_CALIBRATE", "Tune-up", "+5 dmg, faster fire on current gun"),
            ]
            random.shuffle(opts)
            self.dialogue_weapon_options = opts
            return

        pool = [
            ("CHOOSE_PISTOL", "Pistol", "Fast single shots"),
            ("CHOOSE_SHOTGUN", "Shotgun", "Spread burst"),
            ("CHOOSE_PLASMA", "Plasma", "Big slow hits"),
            ("CHOOSE_MINIGUN", "Minigun", "Spray parallel"),
            ("CHOOSE_ROCKET", "Rocket launcher", "Splits into 3 frag bomblets"),
        ]
        owned = _weapon_types_from_unlocks(p.unlocked_weapons)
        available = [o for o in pool if _weapon_by_choice(o[0]).type not in owned]
        random.shuffle(available)
        if len(available) >= 2:
            self.dialogue_weapon_options = available[:2]
        elif len(available) == 1:
            pair = [
                available[0],
                ("CHOOSE_CALIBRATE", "Tune-up", "+5 dmg, faster fire on current gun"),
            ]
            random.shuffle(pair)
            self.dialogue_weapon_options = pair
        else:
            self.dialogue_weapon_options = [
                ("CHOOSE_CALIBRATE", "Tune-up", "+5 dmg, faster fire on current gun"),
                ("CHOOSE_CALIBRATE", "Fine-tune", "+5 dmg, faster fire on current gun"),
            ]

    def _apply_choice(self, choice: Choice) -> None:
        p = self.player
        if choice == "WEAPON":
            w = replace(
                p.weapon,
                damage=p.weapon.damage + 5,
                fire_rate=max(100, p.weapon.fire_rate - 20),
            )
            uw = [replace(x, damage=w.damage, fire_rate=w.fire_rate) if x.type == p.weapon.type else x for x in p.unlocked_weapons]
            p = replace(p, weapon=w, unlocked_weapons=uw)
        elif choice == "HEALTH":
            p = replace(p, max_health=p.max_health + 20, health=p.max_health + 20)
        elif choice == "MAGIC":
            p = replace(p, max_aether_charges=min(3, p.max_aether_charges + 1))
        elif choice == "LIFE":
            p = replace(p, lives=p.lives + 1)
        elif choice == "CHOOSE_CALIBRATE":
            w = replace(
                p.weapon,
                damage=p.weapon.damage + 5,
                fire_rate=max(80, p.weapon.fire_rate - 20),
            )
            uw = [replace(x, damage=w.damage, fire_rate=w.fire_rate) if x.type == p.weapon.type else x for x in p.unlocked_weapons]
            p = replace(p, weapon=w, unlocked_weapons=uw)
        elif choice.startswith("CHOOSE_"):
            nw = _weapon_by_choice(choice)
            uw = list(p.unlocked_weapons)
            if any(x.type == nw.type for x in uw):
                idx = next(i for i, x in enumerate(uw) if x.type == nw.type)
                bumped = replace(
                    uw[idx],
                    damage=uw[idx].damage + 5,
                    fire_rate=max(80, uw[idx].fire_rate - 15),
                )
                uw[idx] = bumped
                p = replace(p, weapon=bumped, unlocked_weapons=uw, weapon_index=idx)
            else:
                uw.append(nw)
                idx = len(uw) - 1
                p = replace(p, weapon=nw, unlocked_weapons=uw, weapon_index=idx)

        next_room = self.room_number + 1
        new_power = list(self.power_ups)
        if next_room % 2 == 0:
            new_power.append(
                PowerUp(
                    id=f"health-{pygame.time.get_ticks()}",
                    pos=Vector(x=CANVAS_WIDTH / 2, y=CANVAS_HEIGHT / 2),
                    type="HEALTH",
                    radius=12,
                )
            )
        self.player = p
        self.room_number = next_room
        self.enemies = spawn_enemies(next_room)
        self.power_ups = new_power
        self.in_dialogue = False
        self.ui = UIScreen.PLAYING

    def update(self) -> None:
        self._time_ms = float(pygame.time.get_ticks())
        self.clock.tick(FPS)

        if self.ui != UIScreen.PLAYING or self.is_game_over or self.in_dialogue:
            return

        self._game_tick(self._time_ms)

    def _game_tick(self, time: float) -> None:
        p = self.player
        orig_health_frame = {e.id: e.health for e in self.enemies}
        enemies = [replace(e) for e in self.enemies]

        if p.magic >= p.max_magic and p.aether_charges < p.max_aether_charges:
            p = replace(p, magic=0, aether_charges=p.aether_charges + 1)

        move_x = 0.0
        move_y = 0.0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            move_x += 1
        if keys[pygame.K_a]:
            move_x -= 1
        if keys[pygame.K_s]:
            move_y += 1
        if keys[pygame.K_w]:
            move_y -= 1

        if move_x != 0 or move_y != 0:
            ln = math.hypot(move_x, move_y)
            p = replace(
                p,
                pos=Vector(
                    x=max(p.radius, min(CANVAS_WIDTH - p.radius, p.pos.x + (move_x / ln) * p.speed)),
                    y=max(p.radius, min(CANVAS_HEIGHT - p.radius, p.pos.y + (move_y / ln) * p.speed)),
                ),
            )

        new_explosions: List[Explosion] = []
        for ex in self.explosions:
            nd = ex.duration - 16
            if nd <= 0:
                continue
            if ex.style in ("rocket", "rocket_frag"):
                new_explosions.append(replace(ex, duration=nd, radius=ex.max_radius))
            else:
                nr = ex.radius + (ex.max_radius - ex.radius) * 0.1
                new_explosions.append(replace(ex, radius=nr, duration=nd))

        if keys[pygame.K_SPACE] and p.aether_charges > 0 and time - self.last_space_time > 500:
            self.last_space_time = time
            p = replace(p, aether_charges=p.aether_charges - 1)
            new_explosions.append(
                Explosion(
                    id=f"explosion-{int(time)}",
                    pos=Vector(p.pos.x, p.pos.y),
                    radius=0,
                    max_radius=250,
                    duration=1000,
                    start_time=time,
                )
            )

        new_bullets: List[Bullet] = []
        for b in self.bullets:
            ox, oy = b.pos.x, b.pos.y
            dx, dy = b.vel.x, b.vel.y
            step = math.hypot(dx, dy)
            nb = replace(
                b,
                pos=Vector(b.pos.x + dx, b.pos.y + dy),
                distance_traveled=b.distance_traveled + step,
                prev_pos=Vector(ox, oy),
            )
            inside = (
                nb.pos.x > -50
                and nb.pos.x < CANVAS_WIDTH + 50
                and nb.pos.y > -50
                and nb.pos.y < CANVAS_HEIGHT + 50
            )
            in_range = b.max_distance is None or nb.distance_traveled < b.max_distance
            in_arena = 0 <= nb.pos.x <= CANVAS_WIDTH and 0 <= nb.pos.y <= CANVAS_HEIGHT
            if b.kind == "rocket":
                if not in_arena:
                    self._spawn_rocket_detonation(
                        Vector(b.pos.x, b.pos.y),
                        Vector(b.vel.x, b.vel.y),
                        b.damage,
                        time,
                        new_explosions,
                        new_bullets,
                    )
                    self._sfx_doof()
                    continue
            if b.kind == "rocket_frag":
                if not in_arena or not in_range:
                    self._spawn_rocket_frag_detonation(Vector(b.pos.x, b.pos.y), time, new_explosions)
                    self._sfx_doof()
                    continue
            if inside and in_range:
                new_bullets.append(nb)

        mx, my = self.mouse_xy
        if self.mouse_btn and time - self.last_fire_time > p.weapon.fire_rate:
            self.last_fire_time = time
            self._sfx_fire(p.weapon.type)
            dx = mx - p.pos.x
            dy = my - p.pos.y
            angle = math.atan2(dy, dx)

            if p.weapon.type == WeaponType.SWORD:
                self.melee_active_until = time + 100
                self.melee_angle = angle
                melee_range = 110.0
                new_en: List[Enemy] = []
                for enemy in enemies:
                    edx = enemy.pos.x - p.pos.x
                    edy = enemy.pos.y - p.pos.y
                    dist = math.hypot(edx, edy)
                    e_ang = math.atan2(edy, edx)
                    diff = abs(e_ang - angle)
                    while diff > math.pi:
                        diff = abs(diff - 2 * math.pi)
                    if dist < melee_range and diff < 1.4:
                        new_en.append(replace(enemy, health=enemy.health - p.weapon.damage))
                    else:
                        new_en.append(enemy)
                enemies = new_en

            elif p.weapon.type == WeaponType.SHOTGUN:
                count = p.weapon.count
                spread = p.weapon.spread
                for i in range(count):
                    offset = (i - (count - 1) / 2) * (spread / max(count, 1))
                    new_bullets.append(
                        Bullet(
                            id=f"b-{random.random()}",
                            pos=Vector(p.pos.x, p.pos.y),
                            vel=Vector(
                                math.cos(angle + offset) * p.weapon.bullet_speed,
                                math.sin(angle + offset) * p.weapon.bullet_speed,
                            ),
                            radius=4,
                            damage=p.weapon.damage,
                            color=p.weapon.color,
                            owner="PLAYER",
                            max_distance=200,
                            distance_traveled=0,
                            kind="shot",
                        )
                    )
            elif p.weapon.type == WeaponType.PLASMA:
                new_bullets.append(
                    Bullet(
                        id=f"b-{random.random()}",
                        pos=Vector(p.pos.x, p.pos.y),
                        vel=Vector(
                            math.cos(angle) * p.weapon.bullet_speed,
                            math.sin(angle) * p.weapon.bullet_speed,
                        ),
                        radius=12,
                        damage=p.weapon.damage,
                        color=p.weapon.color,
                        owner="PLAYER",
                        distance_traveled=0,
                        kind="plasma",
                    )
                )
            elif p.weapon.type == WeaponType.MINIGUN:
                perp = angle + math.pi / 2
                for off in (-8.0, 8.0):
                    new_bullets.append(
                        Bullet(
                            id=f"b-{random.random()}",
                            pos=Vector(
                                p.pos.x + math.cos(perp) * off,
                                p.pos.y + math.sin(perp) * off,
                            ),
                            vel=Vector(
                                math.cos(angle) * p.weapon.bullet_speed,
                                math.sin(angle) * p.weapon.bullet_speed,
                            ),
                            radius=4,
                            damage=p.weapon.damage,
                            color=p.weapon.color,
                            owner="PLAYER",
                            distance_traveled=0,
                            kind="minigun",
                        )
                    )
            elif p.weapon.type == WeaponType.ROCKET:
                new_bullets.append(
                    Bullet(
                        id=f"rk-{random.random()}",
                        pos=Vector(p.pos.x, p.pos.y),
                        vel=Vector(
                            math.cos(angle) * p.weapon.bullet_speed,
                            math.sin(angle) * p.weapon.bullet_speed,
                        ),
                        radius=12,
                        damage=p.weapon.damage,
                        color=p.weapon.color,
                        owner="PLAYER",
                        distance_traveled=0,
                        kind="rocket",
                    )
                )
            elif p.weapon.type == WeaponType.BFG:
                new_bullets.append(
                    Bullet(
                        id=f"bfg-{random.random()}",
                        pos=Vector(p.pos.x, p.pos.y),
                        vel=Vector(
                            math.cos(angle) * p.weapon.bullet_speed,
                            math.sin(angle) * p.weapon.bullet_speed,
                        ),
                        radius=22,
                        damage=p.weapon.damage,
                        color=(45, 212, 191),
                        owner="PLAYER",
                        max_distance=780,
                        distance_traveled=0,
                        kind="bfg",
                    )
                )
            elif p.weapon.type == WeaponType.PISTOL:
                new_bullets.append(
                    Bullet(
                        id=f"b-{random.random()}",
                        pos=Vector(p.pos.x, p.pos.y),
                        vel=Vector(
                            math.cos(angle) * p.weapon.bullet_speed,
                            math.sin(angle) * p.weapon.bullet_speed,
                        ),
                        radius=6,
                        damage=p.weapon.damage,
                        color=p.weapon.color,
                        owner="PLAYER",
                        distance_traveled=0,
                        kind="round",
                    )
                )

        moved_enemies: List[Enemy] = []
        for enemy in enemies:
            dx = p.pos.x - enemy.pos.x
            dy = p.pos.y - enemy.pos.y
            length = math.hypot(dx, dy) or 1e-9
            next_pos = Vector(
                x=enemy.pos.x + (dx / length) * enemy.speed,
                y=enemy.pos.y + (dy / length) * enemy.speed,
            )
            if length < p.radius + enemy.radius:
                p = replace(p, health=p.health - 0.5)
                self.screen_shake = min(12.0, self.screen_shake + 2.0)

            last_shot = enemy.last_shot
            if time - last_shot > enemy.shoot_cooldown:
                last_shot = time
                if enemy.type == "BOSS":
                    for i in range(8):
                        ang = (i / 8) * math.pi * 2
                        new_bullets.append(
                            Bullet(
                                id=f"eb-{i}-{time}",
                                pos=Vector(enemy.pos.x, enemy.pos.y),
                                vel=Vector(math.cos(ang) * 3, math.sin(ang) * 3),
                                radius=6,
                                damage=10,
                                color=(244, 63, 94),
                                owner="ENEMY",
                                distance_traveled=0,
                            )
                        )
                    new_bullets.append(
                        Bullet(
                            id=f"ebd-{time}",
                            pos=Vector(enemy.pos.x, enemy.pos.y),
                            vel=Vector((dx / length) * 5, (dy / length) * 5),
                            radius=8,
                            damage=15,
                            color=(251, 113, 133),
                            owner="ENEMY",
                            distance_traveled=0,
                        )
                    )
                else:
                    new_bullets.append(
                        Bullet(
                            id=f"eb-{time}-{enemy.id}",
                            pos=Vector(enemy.pos.x, enemy.pos.y),
                            vel=Vector((dx / length) * 4, (dy / length) * 4),
                            radius=4,
                            damage=5,
                            color=(248, 113, 113),
                            owner="ENEMY",
                            distance_traveled=0,
                        )
                    )

            moved_enemies.append(replace(enemy, pos=next_pos, last_shot=last_shot))

        active_ids = {b.id for b in new_bullets}
        splashes: List[tuple[float, float, float, float, str]] = []
        bfg_doof_ids: set[str] = set()
        hit_enemies: List[Enemy] = []
        for enemy in moved_enemies:
            h = enemy.health
            for bullet in new_bullets:
                if bullet.owner != "PLAYER" or bullet.id not in active_ids:
                    continue
                if bullet.kind == "bfg":
                    ax = bullet.prev_pos.x if bullet.prev_pos else bullet.pos.x - bullet.vel.x
                    ay = bullet.prev_pos.y if bullet.prev_pos else bullet.pos.y - bullet.vel.y
                    bx, by = bullet.pos.x, bullet.pos.y
                    if _seg_hits_enemy(ax, ay, bx, by, enemy.pos.x, enemy.pos.y, enemy.radius, bullet.radius):
                        h = 0
                        if bullet.id not in bfg_doof_ids:
                            self._sfx_doof()
                            bfg_doof_ids.add(bullet.id)
                    continue
                if bullet.kind == "rocket":
                    dist = math.hypot(bullet.pos.x - enemy.pos.x, bullet.pos.y - enemy.pos.y)
                    if dist < bullet.radius + enemy.radius:
                        active_ids.discard(bullet.id)
                        self._sfx_doof()
                        self._spawn_rocket_detonation(
                            Vector(bullet.pos.x, bullet.pos.y),
                            Vector(bullet.vel.x, bullet.vel.y),
                            bullet.damage,
                            time,
                            new_explosions,
                            new_bullets,
                            active_ids,
                        )
                    continue
                if bullet.kind == "rocket_frag":
                    dist = math.hypot(bullet.pos.x - enemy.pos.x, bullet.pos.y - enemy.pos.y)
                    if dist < bullet.radius + enemy.radius:
                        active_ids.discard(bullet.id)
                        self._sfx_doof()
                        self._spawn_rocket_frag_detonation(
                            Vector(bullet.pos.x, bullet.pos.y),
                            time,
                            new_explosions,
                        )
                    continue
                dist = math.hypot(bullet.pos.x - enemy.pos.x, bullet.pos.y - enemy.pos.y)
                if dist < bullet.radius + enemy.radius:
                    h -= bullet.damage
                    self._sfx_doof()
                    active_ids.discard(bullet.id)
                    if bullet.kind == "plasma":
                        new_explosions.append(
                            Explosion(
                                id=f"plasma-{time}-{random.random()}",
                                pos=Vector(bullet.pos.x, bullet.pos.y),
                                radius=0,
                                max_radius=80,
                                duration=500,
                                start_time=time,
                            )
                        )
            for ex in new_explosions:
                dist = math.hypot(ex.pos.x - enemy.pos.x, ex.pos.y - enemy.pos.y)
                r_kill = ex.max_radius if ex.style in ("rocket", "rocket_frag") else ex.radius
                if dist < r_kill + enemy.radius:
                    h = 0

            hit_enemies.append(replace(enemy, health=h))

        if splashes:
            splashed: List[Enemy] = []
            for enemy in hit_enemies:
                hh = enemy.health
                for sx, sy, sr, sd, skip_id in splashes:
                    if enemy.id == skip_id:
                        continue
                    if math.hypot(enemy.pos.x - sx, enemy.pos.y - sy) < sr + enemy.radius:
                        hh -= sd
                splashed.append(replace(enemy, health=hh))
            hit_enemies = splashed

        for enemy in hit_enemies:
            if enemy.health <= 0 < orig_health_frame[enemy.id]:
                self._sfx_kill()
                p = replace(p, score=p.score + 10)
                if p.aether_charges < p.max_aether_charges:
                    p = replace(p, magic=min(p.max_magic, p.magic + 5))

        p = self._award_score_life_milestones(p)

        final_enemies = [e for e in hit_enemies if e.health > 0]

        for bullet in new_bullets:
            if bullet.owner == "ENEMY" and bullet.id in active_ids:
                dist = math.hypot(bullet.pos.x - p.pos.x, bullet.pos.y - p.pos.y)
                if dist < bullet.radius + p.radius:
                    p = replace(p, health=p.health - bullet.damage)
                    self._sfx_warning()
                    active_ids.discard(bullet.id)
                    self.screen_shake = min(12.0, self.screen_shake + 3.0)

        final_bullets = [b for b in new_bullets if b.id in active_ids]

        new_power_ups: List[PowerUp] = []
        for pu in self.power_ups:
            dist = math.hypot(pu.pos.x - p.pos.x, pu.pos.y - p.pos.y)
            if dist < pu.radius + p.radius:
                if pu.type == "WEAPON_UPGRADE":
                    p = self._ensure_pistol_unlock(p)
                elif pu.type == "HEALTH":
                    p = replace(p, health=min(p.max_health, p.health + p.max_health * 0.25))
                continue
            new_power_ups.append(pu)

        next_room = self.room_number
        in_dialogue = self.in_dialogue
        fe = final_enemies
        fp = new_power_ups

        if len(final_enemies) == 0 and not self.in_dialogue:
            p = replace(p, rooms_cleared=p.rooms_cleared + 1)
            rn = self.room_number
            if rn % 15 == 0:
                p = replace(p, lives=p.lives + 1)
                in_dialogue = True
                self._open_dialogue_weapon_options()
                self.ui = UIScreen.DIALOGUE
            elif rn % 5 == 0:
                in_dialogue = True
                self._open_dialogue_weapon_options()
                self.ui = UIScreen.DIALOGUE
            elif rn % 3 == 0:
                in_dialogue = True
                self.ui = UIScreen.DIALOGUE
            else:
                next_room = rn + 1
                fe = spawn_enemies(next_room)
                if next_room % 2 == 0:
                    fp = list(new_power_ups) + [
                        PowerUp(
                            id=f"health-{int(time)}",
                            pos=Vector(CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2),
                            type="HEALTH",
                            radius=12,
                        )
                    ]

        is_game_over = self.is_game_over
        if p.health <= 0:
            self._sfx_death_scream()
            if p.lives > 0:
                self.ui = UIScreen.DEATH_CHOICE
            else:
                is_game_over = True
                if lb.is_high_score(self.db_path, p.score):
                    self.show_initials = True
                    self.initials_buffer = ""
                    self.ui = UIScreen.INITIALS
                else:
                    self.ui = UIScreen.GAME_OVER

        self.screen_shake = max(0.0, self.screen_shake - 0.5)

        self.player = p
        self.enemies = fe
        self.bullets = final_bullets
        self.power_ups = fp
        self.explosions = new_explosions
        self.room_number = next_room
        self.in_dialogue = in_dialogue
        self.is_game_over = is_game_over

    def draw(self) -> None:
        shake_x = random.uniform(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        shake_y = random.uniform(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0

        def sx(x: float) -> float:
            return x + shake_x

        def sy(y: float) -> float:
            return y + shake_y

        surf = self.screen
        surf.fill(BG)

        if self.ui == UIScreen.TITLE:
            self._draw_title()
            return

        for gx in range(0, CANVAS_WIDTH, 40):
            pygame.draw.line(surf, (30, 41, 59), (sx(gx), sy(0)), (sx(gx), sy(CANVAS_HEIGHT)), 1)
        for gy in range(0, CANVAS_HEIGHT, 40):
            pygame.draw.line(surf, (30, 41, 59), (sx(0), sy(gy)), (sx(CANVAS_WIDTH), sy(gy)), 1)

        if self.ui in (
            UIScreen.PLAYING,
            UIScreen.DIALOGUE,
            UIScreen.DEATH_CHOICE,
            UIScreen.GAME_OVER,
            UIScreen.INITIALS,
        ):
            for pu in self.power_ups:
                spr = surface_for_powerup(pu.type)
                rct = spr.get_rect(center=(int(sx(pu.pos.x)), int(sy(pu.pos.y))))
                surf.blit(spr, rct)

            for ex in self.explosions:
                if ex.duration > 0 and ex.radius > 0:
                    col = (
                        (249, 115, 22)
                        if ex.style in ("rocket", "rocket_frag")
                        else (59, 130, 246)
                    )
                    pygame.draw.circle(
                        surf,
                        col,
                        (int(sx(ex.pos.x)), int(sy(ex.pos.y))),
                        max(1, int(ex.radius)),
                        2,
                    )

            for b in self.bullets:
                cx, cy = int(sx(b.pos.x)), int(sy(b.pos.y))
                if b.kind == "bfg":
                    pygame.draw.circle(surf, (21, 128, 61), (cx, cy), int(b.radius) + 4, 2)
                pygame.draw.circle(surf, b.color, (cx, cy), int(b.radius))

            for e in self.enemies:
                sc = 4 if e.type == "BOSS" else 1.5 if e.type == "TANK" else 1.0
                w, h = int(20 * sc), int(20 * sc)
                px = int(sx(e.pos.x)) - w // 2
                py = int(sy(e.pos.y)) - h // 2
                pygame.draw.rect(surf, e.color, (px, py, w, h), border_radius=4)
                bar_w = w
                pygame.draw.rect(surf, (51, 65, 85), (px, py - 15, bar_w, 4))
                bw = int(bar_w * (e.health / e.max_health))
                if bw > 0:
                    pygame.draw.rect(surf, e.color, (px, py - 15, bw, 4))

            p = self.player
            px, py = int(sx(p.pos.x)), int(sy(p.pos.y))
            if pygame.time.get_ticks() < self.melee_active_until:
                ml = 85
                ax = px + math.cos(self.melee_angle) * 40
                ay = py + math.sin(self.melee_angle) * 40
                ex = px + math.cos(self.melee_angle) * ml
                ey = py + math.sin(self.melee_angle) * ml
                pygame.draw.line(surf, (255, 255, 255), (ax, ay), (ex, ey), 4)

            wt = p.weapon.type
            if wt == WeaponType.BFG:
                body_w = 30
            elif wt == WeaponType.SHOTGUN:
                body_w = 24
            elif wt == WeaponType.PISTOL:
                body_w = 16
            else:
                body_w = 20
            bx0 = px - body_w // 2
            pygame.draw.rect(surf, (51, 65, 85), (bx0, py - 6, body_w, 16), border_radius=2)
            pygame.draw.rect(surf, (148, 163, 184), (bx0 + 2, py - 16, body_w - 4, 12), border_radius=4)
            pygame.draw.rect(surf, (56, 189, 248), (bx0 + 4, py - 13, body_w - 8, 6), border_radius=1)
            if wt == WeaponType.SWORD:
                pygame.draw.line(surf, (226, 232, 240), (px + 10, py - 12), (px + 34, py + 28), 4)
            elif wt == WeaponType.BFG:
                pygame.draw.rect(surf, (22, 163, 74), (px + 10, py - 10, 44, 18), border_radius=3)
                pygame.draw.circle(surf, (74, 222, 128), (px + 52, py - 1), 9)
                pygame.draw.circle(surf, (21, 128, 61), (px + 52, py - 1), 9, 2)
            elif wt == WeaponType.ROCKET:
                pygame.draw.rect(surf, (234, 88, 12), (px + 12, py - 6, 36, 12), border_radius=2)
                pygame.draw.polygon(surf, (251, 146, 60), [(px + 48, py), (px + 58, py - 4), (px + 58, py + 4)])
            elif wt == WeaponType.MINIGUN:
                pygame.draw.rect(surf, (251, 191, 36), (px + 10, py - 2, 10, 6), border_radius=1)
                pygame.draw.rect(surf, (251, 191, 36), (px + 22, py - 2, 10, 6), border_radius=1)
                pygame.draw.rect(surf, (180, 83, 9), (px + 8, py + 4, 26, 5), border_radius=1)
            elif wt == WeaponType.SHOTGUN:
                pygame.draw.rect(surf, (253, 186, 116), (px + 12, py - 4, 8, 8), border_radius=2)
                pygame.draw.rect(surf, (253, 186, 116), (px + 22, py - 4, 8, 8), border_radius=2)
                pygame.draw.rect(surf, (120, 53, 15), (px + 10, py + 4, 22, 5), border_radius=1)
            elif wt == WeaponType.PLASMA:
                pygame.draw.ellipse(surf, (147, 51, 234), (px + 10, py - 6, 22, 14))
                pygame.draw.ellipse(surf, (192, 132, 252), (px + 14, py - 3, 10, 8))
            elif wt == WeaponType.PISTOL:
                pygame.draw.rect(surf, (226, 232, 240), (px + 10, py, 12, 5), border_radius=1)
                pygame.draw.rect(surf, (100, 116, 139), (px + 20, py - 1, 6, 3), border_radius=0)
            else:
                pygame.draw.rect(surf, (59, 130, 246), (px + 10, py, 16, 5), border_radius=1)

            hp_pct = p.health / p.max_health
            pygame.draw.rect(surf, (15, 23, 42), (16, 16, 200, 12))
            pygame.draw.rect(surf, (16, 185, 129), (16, 16, int(200 * hp_pct), 12))
            t = self.font_small.render(
                f"HP {int(p.health)}/{int(p.max_health)}  Score {p.score:06d}  Sector {self.room_number}",
                True,
                (148, 163, 184),
            )
            surf.blit(t, (16, 32))
            slot_txt = f"{p.weapon.type.value}"
            if len(p.unlocked_weapons) > 1:
                slot_txt += f"  ({p.weapon_index + 1}/{len(p.unlocked_weapons)})  ↑↓ / wheel"
            wpn_h = self.font_small.render(slot_txt, True, (226, 232, 240))
            surf.blit(wpn_h, (16, 46))

            mg_pct = p.magic / p.max_magic
            pygame.draw.rect(surf, (15, 23, 42), (16, 62, 200, 10))
            pygame.draw.rect(surf, (59, 130, 246), (16, 62, int(200 * mg_pct), 10))
            ch = f"Surge x{p.aether_charges}" if p.aether_charges else ""
            t2 = self.font_small.render(
                f"Surge {int(p.magic)}/{int(p.max_magic)} {ch}  Reboots {p.lives} (+1/1000 pts)  [SPACE]",
                True,
                (96, 165, 250),
            )
            surf.blit(t2, (16, 80))

            if self.ui == UIScreen.PLAYING:
                hq = self.font_small.render("ESC / Q — quit to DoomGate", True, (100, 116, 139))
                surf.blit(hq, (CANVAS_WIDTH - hq.get_width() - 12, CANVAS_HEIGHT - 22))

        if self.ui == UIScreen.DIALOGUE:
            self._draw_dialogue_overlay()
        elif self.ui == UIScreen.DEATH_CHOICE:
            self._draw_death_choice_overlay()
        elif self.ui == UIScreen.GAME_OVER and not self.show_initials:
            self._draw_game_over()
        elif self.ui == UIScreen.INITIALS:
            self._draw_initials_overlay()

    def _draw_title(self) -> None:
        s = self.screen
        t = self.font_title.render("RBYT3R EPOCH", True, (241, 245, 249))
        s.blit(t, (CANVAS_WIDTH // 2 - t.get_width() // 2, 120))
        sub = self.font_med.render(
            "WASD move · mouse aim/fire · ↑↓ or wheel switch weapons · SPACE surge",
            True,
            (148, 163, 184),
        )
        s.blit(sub, (CANVAS_WIDTH // 2 - sub.get_width() // 2, 200))
        quit_h = self.font_small.render("ESC or Q — quit to DoomGate", True, (100, 116, 139))
        s.blit(quit_h, (CANVAS_WIDTH // 2 - quit_h.get_width() // 2, 232))
        btn = pygame.Rect(CANVAS_WIDTH // 2 - 120, CANVAS_HEIGHT // 2 + 40, 240, 50)
        pygame.draw.rect(s, (16, 185, 129), btn, border_radius=8)
        lt = self.font_large.render("START", True, (15, 23, 42))
        s.blit(lt, (btn.centerx - lt.get_width() // 2, btn.centery - lt.get_height() // 2))
        scores = lb.get_top_scores(self.db_path)
        y = CANVAS_HEIGHT - 120
        self._draw_leaderboard_small(scores, y)

    def _draw_leaderboard_small(self, scores: List[tuple[str, int]], y: int) -> None:
        if not scores:
            return
        s = self.screen
        h = self.font_small.render("TOP 5", True, (148, 163, 184))
        s.blit(h, (CANVAS_WIDTH // 2 - h.get_width() // 2, y))
        for i, (ini, sc) in enumerate(scores[:5]):
            row = self.font_small.render(f"{i + 1}. {ini}  {sc:,}", True, (203, 213, 225))
            s.blit(row, (CANVAS_WIDTH // 2 - row.get_width() // 2, y + 22 + i * 18))

    def _draw_death_choice_overlay(self) -> None:
        s = self.screen
        ov = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT), pygame.SRCALPHA)
        ov.fill((2, 6, 23, 220))
        s.blit(ov, (0, 0))
        title = self.font_large.render("SIGNAL LOST", True, (248, 113, 113))
        s.blit(title, (CANVAS_WIDTH // 2 - title.get_width() // 2, 88))
        n = self.player.lives
        sub = self.font_med.render(
            f"{n} extra life{'s' if n != 1 else ''} in reserve — spend one to continue?",
            True,
            (226, 232, 240),
        )
        s.blit(sub, (CANVAS_WIDTH // 2 - sub.get_width() // 2, 142))
        hint = self.font_small.render(
            "1 — CONTINUE   ·   2 — QUIT TO START   (or click)",
            True,
            (100, 116, 139),
        )
        s.blit(hint, (CANVAS_WIDTH // 2 - hint.get_width() // 2, 182))
        cont, quit_r = self._death_choice_rects()
        pygame.draw.rect(s, (16, 185, 129), cont, border_radius=8)
        c1 = self.font_med.render("CONTINUE", True, (15, 23, 42))
        s.blit(c1, (cont.centerx - c1.get_width() // 2, cont.centery - c1.get_height() // 2 - 8))
        c2 = self.font_small.render("−1 reboot · full HP", True, (21, 65, 51))
        s.blit(c2, (cont.centerx - c2.get_width() // 2, cont.centery + 6))
        pygame.draw.rect(s, (30, 41, 59), quit_r, border_radius=8)
        pygame.draw.rect(s, (100, 116, 139), quit_r, 2, border_radius=8)
        q1 = self.font_med.render("QUIT TO START", True, (248, 250, 252))
        s.blit(q1, (quit_r.centerx - q1.get_width() // 2, quit_r.centery - q1.get_height() // 2 - 8))
        q2 = self.font_small.render("Back to title · new run", True, (148, 163, 184))
        s.blit(q2, (quit_r.centerx - q2.get_width() // 2, quit_r.centery + 6))

    def _draw_dialogue_overlay(self) -> None:
        s = self.screen
        ov = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT), pygame.SRCALPHA)
        ov.fill((2, 6, 23, 220))
        s.blit(ov, (0, 0))
        rn = self.room_number
        is_weapon = rn % 5 == 0
        if rn % 15 == 0:
            msg = "Sector milestone — reboot credit earned. Pick a weapon."
        elif is_weapon:
            msg = "Armory unlock — choose your loadout."
        else:
            msg = "Combat tuning — pick an upgrade."
        t = self.font_large.render(msg, True, (226, 232, 240))
        s.blit(t, (CANVAS_WIDTH // 2 - t.get_width() // 2, 100))
        hint = self.font_small.render(
            "Click or 1–3 (armory: 1–2) — use ↑↓ / mouse wheel to swap guns in combat",
            True,
            (100, 116, 139),
        )
        s.blit(hint, (CANVAS_WIDTH // 2 - hint.get_width() // 2, 150))

        if is_weapon:
            for i, rect in enumerate(self._dialogue_weapon_rects()):
                if i >= len(self.dialogue_weapon_options):
                    break
                cid, title, desc = self.dialogue_weapon_options[i]
                pygame.draw.rect(s, (30, 41, 59), rect, border_radius=8)
                pygame.draw.rect(s, (71, 85, 105), rect, 2, border_radius=8)
                tt = self.font_med.render(title, True, (248, 250, 252))
                s.blit(tt, (rect.x + 16, rect.y + 12))
                ds = self.font_small.render(desc, True, (148, 163, 184))
                s.blit(ds, (rect.x + 16, rect.y + 38))
        else:
            labels = [
                ("WEAPON", "Sharper / faster"),
                ("HEALTH", "Max HP + heal"),
                ("MAGIC", "+Surge charge cap"),
            ]
            for i, rect in enumerate(self._dialogue_standard_rects()):
                pygame.draw.rect(s, (30, 41, 59), rect, border_radius=8)
                pygame.draw.rect(s, (71, 85, 105), rect, 2, border_radius=8)
                tt = self.font_med.render(labels[i][0], True, (248, 250, 252))
                s.blit(tt, (rect.x + 16, rect.y + 12))
                ds = self.font_small.render(labels[i][1], True, (148, 163, 184))
                s.blit(ds, (rect.x + 16, rect.y + 38))

    def _draw_game_over(self) -> None:
        s = self.screen
        ov = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT), pygame.SRCALPHA)
        ov.fill((2, 6, 23, 210))
        s.blit(ov, (0, 0))
        t = self.font_title.render("GAME OVER", True, (248, 250, 252))
        s.blit(t, (CANVAS_WIDTH // 2 - t.get_width() // 2, 140))
        sc = self.font_large.render(f"Score {self.player.score}  Sectors {self.player.rooms_cleared}", True, (148, 163, 184))
        s.blit(sc, (CANVAS_WIDTH // 2 - sc.get_width() // 2, 220))
        btn = pygame.Rect(CANVAS_WIDTH // 2 - 150, CANVAS_HEIGHT // 2 + 40, 300, 50)
        pygame.draw.rect(s, (241, 245, 249), btn, border_radius=8)
        lt = self.font_large.render("BACK TO START", True, (15, 23, 42))
        s.blit(lt, (btn.centerx - lt.get_width() // 2, btn.centery - lt.get_height() // 2))

    def _draw_initials_overlay(self) -> None:
        s = self.screen
        ov = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT), pygame.SRCALPHA)
        ov.fill((2, 6, 23, 230))
        s.blit(ov, (0, 0))
        t = self.font_large.render("HIGH SCORE — enter initials", True, (16, 185, 129))
        s.blit(t, (CANVAS_WIDTH // 2 - t.get_width() // 2, 160))
        sc = self.font_title.render(str(int(self.player.score)), True, (241, 245, 249))
        s.blit(sc, (CANVAS_WIDTH // 2 - sc.get_width() // 2, 220))
        letters = (self.initials_buffer + "___")[:3]
        disp = self.font_title.render(" ".join(letters), True, (248, 250, 252))
        s.blit(disp, (CANVAS_WIDTH // 2 - disp.get_width() // 2, 300))
        h2 = self.font_small.render("A-Z then ENTER — BACKSPACE to fix", True, (100, 116, 139))
        s.blit(h2, (CANVAS_WIDTH // 2 - h2.get_width() // 2, 380))

    def run(self) -> None:
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            if self._owns_display:
                pygame.display.flip()
        if self._owns_display:
            pygame.quit()


def run_minigame(
    surface: Optional[pygame.Surface] = None,
    area: Optional[pygame.Rect] = None,
    db_path: Optional[Path] = None,
) -> None:
    """Run the arcade loop until the window closes (standalone or embedded)."""
    g = Rbyt3rEpochGame(surface=surface, area=area, db_path=db_path)
    g.run()
