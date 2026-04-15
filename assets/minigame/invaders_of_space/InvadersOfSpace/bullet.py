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
        w, h = 18, 26
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        cx = w // 2

        # Outer glow (cyan)
        pygame.draw.circle(surf, (0, 255, 255, 180), (cx, h - 12), 9)
        pygame.draw.circle(surf, (0, 255, 255, 90), (cx, h - 12), 11)

        # Teardrop core (royal blue + cyan highlight)
        pts = [(cx, 0), (w - 4, h - 10), (cx, h - 2), (3, h - 10)]
        pygame.draw.polygon(surf, (45, 95, 255, 235), pts)
        pygame.draw.polygon(surf, (0, 240, 255, 210), [(cx, 3), (w - 7, h - 12), (cx, h - 6), (6, h - 12)])

        # Little hot tip
        pygame.draw.circle(surf, (230, 255, 255, 230), (cx, 4), 2)
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