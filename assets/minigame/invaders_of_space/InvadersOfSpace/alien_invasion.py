"""
     ObiRonKenobi presents:

***    Invaders of Space     ***

"""

import sys
from time import sleep

import pygame

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien


class AlienInvasion:
    """old ass games made by old ass punks"""

    def __init__(self):
        """Initialize, start, let's play already!!"""
        pygame.init()
        self.settings = Settings()

        # DoomGate launches this as a subprocess; keep it windowed so it doesn't
        # hijack the user's whole display.
        self.screen = pygame.display.set_mode((1200, 800))
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Invaders of Space — BADONKS")

        # Scoreboard for the
        # Measuring Contest
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        # Button
        self.play_button = Button(self, "Play")

    def run_game(self):
        """ Ready... FIGHT!! """
        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()

    def _check_events(self):
        """How do your work this thing?"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        """just hit play!"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            # Fresh start
            self.settings.initialize_dynamic_settings()

            # No Cheating!
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()

            # All clear
            self.aliens.empty()
            self.bullets.empty()

            # Line 'em up!
            self._create_fleet()
            self.ship.center_ship()

            # Only One Blind Mouse included! Other Blind Mice sold separately!
            pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        """Buttons make light screen do funny things"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_ESCAPE:
            sys.exit()
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        """try pressing it twice lol"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        """No, Kenny! It's not pew-pew! It's BANG-BANG!!"""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        """BYE!"""
        # Velocity
        self.bullets.update()

        # out of sight out of mind lol
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """Kill 'em Dead!"""
        # deuces!
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True)

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            # fuggit
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # BEEFCAKE!!!
            self.stats.level += 1
            self.sb.prep_level()

    def _update_aliens(self):
        """
        Alien version 2.5.9 patch now available!! /s
        """
        self._check_fleet_edges()
        self.aliens.update()

        # Crash!?
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # Stay off my lawn!
        self._check_aliens_bottom()

    def _check_aliens_bottom(self):
        """.. But has the Eagle landed?"""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # I mean... i guess...
                self._ship_hit()
                break

    def _ship_hit(self):
        """Get f***ed!"""
        if self.stats.ships_left > 0:
            # Minus aliens equals plus points
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            # CLEAR!!
            self.aliens.empty()
            self.bullets.empty()

            # Rack 'em!
            self._create_fleet()
            self.ship.center_ship()

            # Stop! Wait a minute!
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _create_fleet(self):
        """creates like an alien fleet.. or something like that."""
        # Procreate and calculate
        # Shoulder width spacing
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        # How many of 'em are there?!
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height -
                             (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        # Bring it on!
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        """Aliens better fall in line!"""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """ Gotta keep the edges tight, bruh!"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Alien ships go brrr"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_screen(self):
        """in case the name of the funtion we're describing isn't
        indicative enough: This code updates the screen"""
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)

        # Who's keeping score?
        self.sb.show_score()

        # Press PLAY!
        if not self.stats.game_active:
            self.play_button.draw_button()

        pygame.display.flip()


if __name__ == '__main__':
    # GET SOME!!!
    ai = AlienInvasion()
    ai.run_game()