"""
RBYT3R Epoch — twin-stick style arcade mini-game (Pygame).

Designed so you can later embed it in another project by passing a surface
and draw rectangle (see `Rbyt3rEpochGame` constructor).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from enum import Enum, auto
from pathlib import Path
from typing import List, Optional

import pygame

from .constants import (
    BG,
    CANVAS_HEIGHT,
    CANVAS_WIDTH,
    FPS,
    MINIGUN_WEAPON,
    PISTOL_WEAPON,
    PLASMA_WEAPON,
    SHOTGUN_WEAPON,
    SWORD_WEAPON,
    Weapon,
    WeaponType,
)
from . import leaderboard as lb


class UIScreen(Enum):
    TITLE = auto()
    PLAYING = auto()
    DIALOGUE = auto()
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


def _weapon_by_choice(choice: Choice) -> Weapon:
    return {
        "CHOOSE_PISTOL": PISTOL_WEAPON,
        "CHOOSE_SHOTGUN": SHOTGUN_WEAPON,
        "CHOOSE_PLASMA": PLASMA_WEAPON,
        "CHOOSE_MINIGUN": MINIGUN_WEAPON,
    }[choice]


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

        self._time_ms = 0.0

    def _new_player(self) -> Player:
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
        )

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

        self._translate_mouse()

    def _click_ui(self, pos: tuple[int, int]) -> None:
        lx, ly = self._to_local(pos)
        if self.ui == UIScreen.TITLE:
            r = pygame.Rect(CANVAS_WIDTH // 2 - 120, CANVAS_HEIGHT // 2 + 40, 240, 50)
            if r.collidepoint(lx, ly):
                self._start_game()
        elif self.ui == UIScreen.GAME_OVER and not self.show_initials:
            r = pygame.Rect(CANVAS_WIDTH // 2 - 120, CANVAS_HEIGHT // 2 + 40, 240, 50)
            if r.collidepoint(lx, ly):
                self._restart()
        elif self.ui == UIScreen.DIALOGUE:
            self._click_dialogue(lx, ly)

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

    def _start_game(self) -> None:
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
        self.ui = UIScreen.PLAYING

    def _restart(self) -> None:
        self._start_game()

    def _open_dialogue_weapon_options(self) -> None:
        opts = [
            ("CHOOSE_PISTOL", "Pistol", "Fast single shots"),
            ("CHOOSE_SHOTGUN", "Shotgun", "Spread burst"),
            ("CHOOSE_PLASMA", "Plasma", "Big slow hits"),
            ("CHOOSE_MINIGUN", "Minigun", "Spray parallel"),
        ]
        random.shuffle(opts)
        self.dialogue_weapon_options = opts[:2]

    def _apply_choice(self, choice: Choice) -> None:
        p = self.player
        if choice == "WEAPON":
            p = replace(
                p,
                weapon=replace(
                    p.weapon,
                    damage=p.weapon.damage + 5,
                    fire_rate=max(100, p.weapon.fire_rate - 20),
                ),
            )
        elif choice == "HEALTH":
            p = replace(p, max_health=p.max_health + 20, health=p.max_health + 20)
        elif choice == "MAGIC":
            p = replace(p, max_aether_charges=min(3, p.max_aether_charges + 1))
        elif choice == "LIFE":
            p = replace(p, lives=p.lives + 1)
        elif choice.startswith("CHOOSE_"):
            p = replace(p, weapon=_weapon_by_choice(choice))

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
        enemies = [replace(e) for e in self.enemies]

        if p.magic >= p.max_magic and p.aether_charges < p.max_aether_charges:
            p = replace(p, magic=0, aether_charges=p.aether_charges + 1)

        move_x = 0.0
        move_y = 0.0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_x += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move_x -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move_y += 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:
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
            nr = ex.radius + (ex.max_radius - ex.radius) * 0.1
            nd = ex.duration - 16
            if nd > 0:
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
            dx, dy = b.vel.x, b.vel.y
            dist = math.hypot(dx, dy)
            nb = replace(
                b,
                pos=Vector(b.pos.x + dx, b.pos.y + dy),
                distance_traveled=b.distance_traveled + dist,
            )
            inside = (
                nb.pos.x > -50
                and nb.pos.x < CANVAS_WIDTH + 50
                and nb.pos.y > -50
                and nb.pos.y < CANVAS_HEIGHT + 50
            )
            in_range = b.max_distance is None or nb.distance_traveled < b.max_distance
            if inside and in_range:
                new_bullets.append(nb)

        mx, my = self.mouse_xy
        if self.mouse_btn and time - self.last_fire_time > p.weapon.fire_rate:
            self.last_fire_time = time
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
                        )
                    )
            else:
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
                        color=(255, 255, 255),
                        owner="PLAYER",
                        distance_traveled=0,
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
        hit_enemies: List[Enemy] = []
        for enemy in moved_enemies:
            h = enemy.health
            for bullet in new_bullets:
                if bullet.owner != "PLAYER" or bullet.id not in active_ids:
                    continue
                dist = math.hypot(bullet.pos.x - enemy.pos.x, bullet.pos.y - enemy.pos.y)
                if dist < bullet.radius + enemy.radius:
                    h -= bullet.damage
                    active_ids.discard(bullet.id)
                    if p.weapon.type == WeaponType.PLASMA:
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
                if dist < ex.radius + enemy.radius:
                    h = 0

            prev_h = enemy.health
            if h <= 0 < prev_h:
                p = replace(p, score=p.score + 10)
                if p.aether_charges < p.max_aether_charges:
                    p = replace(p, magic=min(p.max_magic, p.magic + 5))

            hit_enemies.append(replace(enemy, health=h))

        final_enemies = [e for e in hit_enemies if e.health > 0]

        for bullet in new_bullets:
            if bullet.owner == "ENEMY" and bullet.id in active_ids:
                dist = math.hypot(bullet.pos.x - p.pos.x, bullet.pos.y - p.pos.y)
                if dist < bullet.radius + p.radius:
                    p = replace(p, health=p.health - bullet.damage)
                    active_ids.discard(bullet.id)
                    self.screen_shake = min(12.0, self.screen_shake + 3.0)

        final_bullets = [b for b in new_bullets if b.id in active_ids]

        new_power_ups: List[PowerUp] = []
        for pu in self.power_ups:
            dist = math.hypot(pu.pos.x - p.pos.x, pu.pos.y - p.pos.y)
            if dist < pu.radius + p.radius:
                if pu.type == "WEAPON_UPGRADE":
                    p = replace(p, weapon=PISTOL_WEAPON)
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
            if p.lives > 0:
                p = replace(p, lives=p.lives - 1, health=p.max_health)
                final_bullets = []
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
            UIScreen.GAME_OVER,
            UIScreen.INITIALS,
        ):
            for pu in self.power_ups:
                col = (251, 191, 36) if pu.type == "WEAPON_UPGRADE" else (244, 63, 94)
                pygame.draw.circle(surf, col, (int(sx(pu.pos.x)), int(sy(pu.pos.y))), int(pu.radius))

            for ex in self.explosions:
                if ex.duration > 0 and ex.radius > 0:
                    pygame.draw.circle(
                        surf,
                        (59, 130, 246),
                        (int(sx(ex.pos.x)), int(sy(ex.pos.y))),
                        max(1, int(ex.radius)),
                        2,
                    )

            for b in self.bullets:
                pygame.draw.circle(
                    surf, b.color, (int(sx(b.pos.x)), int(sy(b.pos.y))), int(b.radius)
                )

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

            pygame.draw.rect(surf, (51, 65, 85), (px - 10, py - 5, 20, 15), border_radius=2)
            pygame.draw.rect(surf, (148, 163, 184), (px - 8, py - 15, 16, 12), border_radius=4)
            pygame.draw.rect(surf, (56, 189, 248), (px - 6, py - 12, 12, 6), border_radius=1)
            if p.weapon.type == WeaponType.SWORD:
                pygame.draw.line(surf, (226, 232, 240), (px + 8, py - 10), (px + 28, py + 30), 3)
            else:
                pygame.draw.rect(surf, (59, 130, 246), (px + 8, py, 15, 5), border_radius=1)

            hp_pct = p.health / p.max_health
            pygame.draw.rect(surf, (15, 23, 42), (16, 16, 200, 12))
            pygame.draw.rect(surf, (16, 185, 129), (16, 16, int(200 * hp_pct), 12))
            t = self.font_small.render(
                f"HP {int(p.health)}/{int(p.max_health)}  Score {p.score:06d}  Sector {self.room_number}",
                True,
                (148, 163, 184),
            )
            surf.blit(t, (16, 32))

            mg_pct = p.magic / p.max_magic
            pygame.draw.rect(surf, (15, 23, 42), (16, 52, 200, 10))
            pygame.draw.rect(surf, (59, 130, 246), (16, 52, int(200 * mg_pct), 10))
            ch = f"Surge x{p.aether_charges}" if p.aether_charges else ""
            t2 = self.font_small.render(
                f"Surge meter  {int(p.magic)}/{int(p.max_magic)}  {ch}  Reboots {p.lives}  [SPACE] purge",
                True,
                (96, 165, 250),
            )
            surf.blit(t2, (16, 66))

            if self.ui == UIScreen.PLAYING:
                hq = self.font_small.render("ESC / Q — quit to DoomGate", True, (100, 116, 139))
                surf.blit(hq, (CANVAS_WIDTH - hq.get_width() - 12, CANVAS_HEIGHT - 22))

        if self.ui == UIScreen.DIALOGUE:
            self._draw_dialogue_overlay()
        elif self.ui == UIScreen.GAME_OVER and not self.show_initials:
            self._draw_game_over()
        elif self.ui == UIScreen.INITIALS:
            self._draw_initials_overlay()

    def _draw_title(self) -> None:
        s = self.screen
        t = self.font_title.render("RBYT3R EPOCH", True, (241, 245, 249))
        s.blit(t, (CANVAS_WIDTH // 2 - t.get_width() // 2, 120))
        sub = self.font_med.render("Arcade demon wave survival — WASD move, mouse fire, SPACE surge", True, (148, 163, 184))
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
        h = self.font_small.render("TOP RUNS", True, (148, 163, 184))
        s.blit(h, (CANVAS_WIDTH // 2 - h.get_width() // 2, y))
        for i, (ini, sc) in enumerate(scores[:5]):
            row = self.font_small.render(f"{i + 1}. {ini}  {sc}", True, (203, 213, 225))
            s.blit(row, (CANVAS_WIDTH // 2 - row.get_width() // 2, y + 22 + i * 18))

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
        hint = self.font_small.render("Click buttons or press 1-3 (1-2 for weapons)", True, (100, 116, 139))
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
        btn = pygame.Rect(CANVAS_WIDTH // 2 - 120, CANVAS_HEIGHT // 2 + 40, 240, 50)
        pygame.draw.rect(s, (241, 245, 249), btn, border_radius=8)
        lt = self.font_large.render("AGAIN", True, (15, 23, 42))
        s.blit(lt, (btn.centerx - lt.get_width() // 2, btn.centery - lt.get_height() // 2))
        scores = lb.get_top_scores(self.db_path)
        self._draw_leaderboard_small(scores, CANVAS_HEIGHT - 100)

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
