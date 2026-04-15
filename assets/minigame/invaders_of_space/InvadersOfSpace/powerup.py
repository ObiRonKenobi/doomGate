import math
import random

import pygame
from pygame.sprite import Sprite


class PowerUp(Sprite):
    """Weapon upgrade that drifts downward."""

    def __init__(self, ai_game, weapon_id: int):
        super().__init__()
        self.screen = ai_game.screen
        self.screen_rect = ai_game.screen.get_rect()
        self.settings = ai_game.settings
        self.weapon_id = int(weapon_id)
        self.image = self._make_icon_surface(self.weapon_id)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.t0 = pygame.time.get_ticks()
        self.vx = 0.0
        # Two phases for smooth, snowflake-like drift.
        self.drift_phase_a = random.random() * math.tau
        self.drift_phase_b = random.random() * math.tau
        self.center_bias = random.uniform(0.85, 1.15)

    def _make_icon_surface(self, weapon_id: int) -> pygame.Surface:
        # High-contrast "bubble" pickup (easy to see on galaxy BG).
        w, h = 120, 120
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        cx, cy = w // 2, h // 2

        # Outer bubble ring (hot pink)
        pygame.draw.circle(surf, (255, 60, 220, 210), (cx, cy), 54, width=6)
        pygame.draw.circle(surf, (255, 60, 220, 90), (cx, cy), 60, width=5)

        # Inner glassy fill (very light)
        pygame.draw.circle(surf, (235, 255, 255, 55), (cx, cy), 46)
        pygame.draw.circle(surf, (255, 255, 255, 80), (cx - 18, cy - 20), 16)
        pygame.draw.circle(surf, (255, 255, 255, 55), (cx - 24, cy - 30), 8)

        # Weapon indicator inside the bubble
        if weapon_id == 1:
            col = (120, 255, 255, 230)  # cyan
            col2 = (170, 80, 255, 230)  # purple
            pygame.draw.line(surf, col, (cx - 12, cy - 26), (cx - 12, cy + 30), 8)
            pygame.draw.line(surf, col2, (cx + 12, cy - 26), (cx + 12, cy + 30), 8)
        elif weapon_id == 2:
            col = (245, 245, 245, 220)  # white
            col2 = (40, 160, 60, 220)  # forest
            pygame.draw.polygon(surf, col2, [(cx, cy - 30), (cx + 34, cy + 18), (cx, cy + 2), (cx - 34, cy + 18)])
            pygame.draw.polygon(surf, col, [(cx, cy - 24), (cx + 26, cy + 10), (cx, cy), (cx - 26, cy + 10)])
        else:
            col = (170, 40, 255, 220)  # purple
            col2 = (60, 255, 120, 220)  # neon green
            pygame.draw.circle(surf, col, (cx, cy), 30)
            pygame.draw.circle(surf, col2, (cx, cy), 19)
            pygame.draw.circle(surf, (255, 255, 255, 230), (cx, cy), 8)
        return surf

    def update(self):
        now = pygame.time.get_ticks()
        t = (now - self.t0) / 1000.0
        # Slow downward drift (catchable).
        self.y += 0.042

        # Snowflake-like drift: smooth (no jitter), slowly varying side-to-side.
        wave_vx = (
            math.sin(t * 0.85 + self.drift_phase_a) * 0.42
            + math.sin(t * 1.55 + self.drift_phase_b) * 0.26
        )
        # Gentle bias toward center so it doesn't pinball between walls.
        cx = (self.screen_rect.w - self.rect.w) * 0.5
        center_dx = cx - self.x
        center_pull = max(-0.28, min(0.28, center_dx * 0.0034)) * self.center_bias

        target_vx = wave_vx + center_pull
        self.vx = (self.vx * 0.97) + (target_vx * 0.03)
        self.vx = max(-0.62, min(0.62, self.vx))
        self.x += self.vx

        # Near walls: damp and steer inward instead of hard "ping" away.
        max_x = float(self.screen_rect.w - self.rect.w)
        edge = min(48.0, max_x * 0.12)
        if self.x < edge:
            t_edge = max(0.0, min(1.0, (edge - self.x) / max(1.0, edge)))
            self.vx += center_pull * (0.55 + 0.45 * t_edge) + (edge - self.x) * 0.006
            self.vx *= 1.0 - 0.08 * t_edge
        elif self.x > max_x - edge:
            t_edge = max(0.0, min(1.0, (self.x - (max_x - edge)) / max(1.0, edge)))
            self.vx += center_pull * (0.55 + 0.45 * t_edge) - (self.x - (max_x - edge)) * 0.006
            self.vx *= 1.0 - 0.08 * t_edge

        if self.x < 0.0:
            self.x = 0.0
            self.vx = self.vx * 0.25 + center_pull * 0.55
        elif self.x > max_x:
            self.x = max_x
            self.vx = self.vx * 0.25 + center_pull * 0.55
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
