import pygame
from pygame.sprite import Sprite


class Alien(Sprite):
    """aliens... each..."""

    def __init__(self, ai_game):
        """create an alien"""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        # alien rectum
        self.image = pygame.image.load('images/alien.bmp')
        self.rect = self.image.get_rect()

        # start top left with these jabronis
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        # left or right?
        self.x = float(self.rect.x)

    def check_edges(self):
        """I know i'm supposed to color inside the lines...
        ...but i like to be myself"""
        screen_rect = self.screen.get_rect()
        if self.rect.right >= screen_rect.right or self.rect.left <= 0:
            return True

    def update(self):
        """Dance Monkey!!"""
        self.x += (self.settings.alien_speed *
                   self.settings.fleet_direction)
        self.rect.x = self.x