import pygame
from pygame.sprite import Sprite


class Bullet(Sprite):
    """Shoot 'em dead!!!"""

    def __init__(
        self,
        ai_game,
        *,
        vx: float = 0.0,
        vy: float = -1.0,
        speed: float = 3.0,
        style: str = "default",
    ):
        """Step 1: Load Gun"""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.vx = float(vx)
        self.vy = float(vy)
        self.speed = float(speed)
        self.style = str(style)
        self.image = self._make_surface(self.style)
        self.rect = self.image.get_rect()
        self.rect.midtop = ai_game.ship.rect.midtop
        self.mask = pygame.mask.from_surface(self.image)

        # Aim!
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

    def _make_surface(self, style: str) -> pygame.Surface:
        if style == "dual":
            # Smaller minigun tracer
            return self._make_teardrop_surface(w=18, h=28, glow=(0, 255, 255), core=(160, 80, 255), inner=(80, 255, 255))
        if style == "spread":
            return self._make_teardrop_surface(w=30, h=44, glow=(235, 255, 235), core=(245, 245, 245), inner=(40, 160, 60))
        if style == "crusher":
            # Big slow rocket-like shot.
            return self._make_teardrop_surface(w=84, h=118, glow=(220, 120, 255), core=(170, 40, 255), inner=(60, 255, 120), tip=(255, 255, 255))
        # default red/yellow
        return self._make_teardrop_surface(w=36, h=52, glow=(255, 235, 80), core=(255, 60, 40), inner=(255, 220, 80))

    def _make_teardrop_surface(
        self,
        *,
        w: int,
        h: int,
        glow: tuple[int, int, int],
        core: tuple[int, int, int],
        inner: tuple[int, int, int],
        tip: tuple[int, int, int] = (255, 255, 220),
    ) -> pygame.Surface:
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        cx = w // 2

        # Outer glow
        pygame.draw.circle(surf, (*glow, 170), (cx, h - h // 2), max(10, w // 2))
        pygame.draw.circle(surf, (*glow, 80), (cx, h - h // 2), max(12, w // 2 + 4))

        # Teardrop core
        pad = max(6, w // 6)
        base_y = h - max(10, h // 3)
        pts = [(cx, 0), (w - (pad + 1), base_y), (cx, h - 4), (pad, base_y)]
        pygame.draw.polygon(surf, (*core, 240), pts)
        pygame.draw.polygon(
            surf,
            (*inner, 220),
            [(cx, max(4, h // 9)), (w - (pad + 5), base_y - 4), (cx, h - (h // 5)), (pad + 5, base_y - 4)],
        )

        # Little hot tip
        pygame.draw.circle(surf, (*tip, 235), (cx, max(6, h // 7)), max(2, w // 9))
        return surf

    def update(self):
        """FIRE!!"""
        self.x += self.vx * self.speed
        self.y += self.vy * self.speed
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def draw_bullet(self):
        """TRACER ROUNDS!!"""
        self.screen.blit(self.image, self.rect)