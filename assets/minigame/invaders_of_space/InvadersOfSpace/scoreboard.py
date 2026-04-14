import pygame.font
from pygame.sprite import Group

from ship import Ship


class Scoreboard:
    """the class name says it all"""

    def __init__(self, ai_game):
        """Derp! Score keeper keeps score!"""
        self.ai_game = ai_game
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = ai_game.settings
        self.stats = ai_game.stats

        # Font and such
        self.text_color = (30, 30, 30)
        self.font = pygame.font.SysFont(None, 48)
        self.font_small = pygame.font.SysFont(None, 30)
        self._lives_bottom_y = 20

        # numbers and such.
        self.prep_ships()
        self.prep_score()
        self.prep_high_score()
        self.prep_level()
        self.prep_hint()

    def prep_score(self):
        """pictures of numbers..."""
        rounded_score = round(self.stats.score, -1)
        score_str = "SCORE: {:,}".format(rounded_score)
        self.score_image = self.font.render(score_str, True,
                                            self.text_color, self.settings.bg_color)

        # Display current score, top-left (leave room for high score in the center)
        self.score_rect = self.score_image.get_rect()
        self.score_rect.left = 20
        self.score_rect.top = int(getattr(self, "_lives_bottom_y", 20)) + 6

    def prep_high_score(self):
        """more pictures of numbers"""
        """#FIXME# the high score ends after game is closed. persistent highscore would require generating
        an accessible save file"""
        high_score = round(self.stats.high_score, -1)
        high_score_str = "{:,}".format(high_score)
        self.high_score_image = self.font.render(high_score_str, True,
                                                 self.text_color, self.settings.bg_color)

        # Recent highscore dead center
        self.high_score_rect = self.high_score_image.get_rect()
        self.high_score_rect.centerx = self.screen_rect.centerx
        self.high_score_rect.top = self.score_rect.top

    def prep_level(self):
        """Why is space white anyway?"""
        level_str = str(self.stats.level)
        self.level_image = self.font.render(level_str, True,
                                            self.text_color, self.settings.bg_color)

        # game below score, score above game... some shit...
        self.level_rect = self.level_image.get_rect()
        self.level_rect.right = self.score_rect.right
        self.level_rect.top = self.score_rect.bottom + 10

    def prep_hint(self):
        """small hint text that won't collide with scores"""
        self.hint_image = self.font_small.render("Q / ESC: Quit", True, self.text_color, self.settings.bg_color)
        self.hint_rect = self.hint_image.get_rect()
        self.hint_rect.right = self.screen_rect.right - 20
        self.hint_rect.top = 26

    def prep_ships(self):
        """Gotta grab them 1-ups!!"""
        self.ships = Group()
        for ship_number in range(self.stats.ships_left):
            ship = Ship(self.ai_game)
            ship.rect.x = 10 + ship_number * ship.rect.width
            ship.rect.y = 10
            self.ships.add(ship)
        # Keep the score text below the lives meter.
        if self.ships.sprites():
            self._lives_bottom_y = max(s.rect.bottom for s in self.ships.sprites())
        else:
            self._lives_bottom_y = 20
        # Reposition score/level now that lives height may have changed.
        if hasattr(self, "score_rect"):
            self.score_rect.top = int(self._lives_bottom_y) + 6
        if hasattr(self, "level_rect"):
            self.level_rect.top = self.score_rect.bottom + 10

    def check_high_score(self):
        """Is there a higher high score?"""
        if self.stats.score > self.stats.high_score:
            self.stats.high_score = self.stats.score
            self.prep_high_score()

    def show_score(self):
        """paint with all the colors of the wind"""
        self.screen.blit(self.score_image, self.score_rect)
        self.screen.blit(self.high_score_image, self.high_score_rect)
        self.screen.blit(self.hint_image, self.hint_rect)
        self.screen.blit(self.level_image, self.level_rect)
        self.ships.draw(self.screen)