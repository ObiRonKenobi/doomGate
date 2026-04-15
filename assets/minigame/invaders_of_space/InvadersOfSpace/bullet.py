import pygame
from pygame.sprite import Sprite


class Bullet(Sprite):
    """Shoot 'em dead!!!"""

    def __init__(self, ai_game):
        """Step 1: Load Gun"""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.image = self._make_fireball_surface()
        self.rect = self.image.get_rect()
        self.rect.midtop = ai_game.ship.rect.midtop
        self.mask = pygame.mask.from_surface(self.image)

        # Aim!
        self.y = float(self.rect.y)

    def _make_fireball_surface(self) -> pygame.Surface:
        # ~200% larger than prior (18x26).
        w, h = 36, 52
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        cx = w // 2

        # Outer glow (yellow)
        pygame.draw.circle(surf, (255, 235, 80, 170), (cx, h - 24), 18)
        pygame.draw.circle(surf, (255, 235, 80, 80), (cx, h - 24), 22)

        # Teardrop core (red with yellow-hot inner)
        pts = [(cx, 0), (w - 7, h - 20), (cx, h - 4), (6, h - 20)]
        pygame.draw.polygon(surf, (255, 60, 40, 240), pts)
        pygame.draw.polygon(surf, (255, 220, 80, 220), [(cx, 6), (w - 12, h - 24), (cx, h - 12), (11, h - 24)])

        # Little hot tip
        pygame.draw.circle(surf, (255, 255, 220, 235), (cx, 8), 4)
        return surf

    def update(self):
        """FIRE!!"""
        # mathing up a bullet
        self.y -= self.settings.bullet_speed
        # still mathing a bullet
        self.rect.y = self.y

    def draw_bullet(self):
        """TRACER ROUNDS!!"""
        self.screen.blit(self.image, self.rect)