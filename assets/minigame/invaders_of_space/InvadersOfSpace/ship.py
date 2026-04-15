import pygame

from pygame.sprite import Sprite


class Ship(Sprite):
    """a mast and some sails"""

    def __init__(self, ai_game):
        """Shovin' off"""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()

        # what ship?
        self.image = pygame.image.load('images/ship.bmp').convert()
        self.image.set_colorkey((255, 255, 255))
        self.rect = self.image.get_rect()

        # deja vu?
        self.rect.midbottom = self.screen_rect.midbottom

        # how come we can only fly left and right?
        self.x = float(self.rect.x)

        # but are we even moving?
        self.moving_right = False
        self.moving_left = False

    def update(self):
        """seriously, where are we?"""
        # stay in bounds now
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed

        # rectum?! we killed 'em!
        self.rect.x = self.x

    def blitme(self):
        """gotta find the blit!"""
        self.screen.blit(self.image, self.rect)

    def center_ship(self):
        """it's all about balance"""
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)