import pygame
from pygame.sprite import Sprite


class Bullet(Sprite):
    """Shoot 'em dead!!!"""

    def __init__(self, ai_game):
        """Step 1: Load Gun"""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = self.settings.bullet_color

        # Ready....
        self.rect = pygame.Rect(0, 0, self.settings.bullet_width,
                                self.settings.bullet_height)
        self.rect.midtop = ai_game.ship.rect.midtop

        # Aim!
        self.y = float(self.rect.y)

    def update(self):
        """FIRE!!"""
        # mathing up a bullet
        self.y -= self.settings.bullet_speed
        # still mathing a bullet
        self.rect.y = self.y

    def draw_bullet(self):
        """TRACER ROUNDS!!"""
        pygame.draw.rect(self.screen, self.color, self.rect)