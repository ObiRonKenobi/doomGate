"""
     ObiRonKenobi presents:

***    Invaders of Space     ***

"""

import json
import os
import sys
from time import sleep

import pygame

from sfx import SR, make_doop, make_explosion, make_pew
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
        pygame.mixer.pre_init(SR, size=-16, channels=1, buffer=512)
        pygame.init()
        self.settings = Settings()

        # DoomGate launches this as a subprocess; keep it windowed so it doesn't
        # hijack the user's whole display.
        self.screen = pygame.display.set_mode((1200, 800))
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Invaders of Space — BADONKS")
        self.screen_rect = self.screen.get_rect()

        self.bg_image = self._load_background_image()
        self.sfx_pew = make_pew()
        self.sfx_doop = make_doop()
        self.sfx_explosion = make_explosion()

        # Scoreboard for the
        # Measuring Contest
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        # Persistent high scores (top 5)
        self.high_scores = self._load_high_scores()
        self.stats.high_score = self.high_scores[0]["score"] if self.high_scores else 0
        self.sb.prep_high_score()

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        # Button
        self.play_button = Button(self, "Play")

        # Auto-fire + high score entry
        self.firing = False
        self.last_fire_ms = 0
        self.hs_entry_active = False
        self.hs_initials = ""
        self.hs_pending_score = 0

    def _load_background_image(self):
        """Optional pixel-art galaxy: place images/galaxy_bg.png (see galaxy_prompt.txt)."""
        for name in ("galaxy_bg.png", "galaxy_bg.jpg", "galaxy_bg.webp"):
            path = os.path.join(os.path.dirname(__file__), "images", name)
            if os.path.isfile(path):
                try:
                    img = pygame.image.load(path).convert()
                    return pygame.transform.smoothscale(img, (self.screen_rect.w, self.screen_rect.h))
                except Exception:
                    pass
        return None

    def run_game(self):
        """ Ready... FIGHT!! """
        while True:
            self._check_events()

            if self.stats.game_active:
                self._maybe_autofire()
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
            if self.hs_entry_active:
                return
            self._start_new_game()

    def _start_new_game(self) -> None:
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
        self.firing = False
        self.last_fire_ms = 0

    def _check_keydown_events(self, event):
        """Buttons make light screen do funny things"""
        if self.hs_entry_active:
            self._handle_high_score_keydown(event)
            return
        if not self.stats.game_active:
            if event.key in (pygame.K_ESCAPE, pygame.K_q):
                sys.exit()
            self._start_new_game()
            return
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_ESCAPE:
            sys.exit()
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self.firing = True
            self._fire_bullet()

    def _check_keyup_events(self, event):
        """try pressing it twice lol"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        elif event.key == pygame.K_SPACE:
            self.firing = False

    def _maybe_autofire(self):
        if not self.firing:
            return
        now = pygame.time.get_ticks()
        if now - int(self.last_fire_ms) >= int(getattr(self.settings, "fire_cooldown_ms", 150)):
            self.last_fire_ms = now
            self._fire_bullet()

    def _high_score_path(self) -> str:
        # DoomGate can provide a writable path via env var so packaged builds can persist scores.
        p = os.environ.get("BADONKS_HIGHSCORES_PATH", "").strip()
        if p:
            return p
        return os.path.join(os.path.dirname(__file__), "highscores.json")

    def _seed_high_score_path(self) -> str:
        # Shipped seed scores (your dev highscores) live alongside the game.
        return os.path.join(os.path.dirname(__file__), "highscores_seed.json")

    def _load_high_scores(self):
        path = self._high_score_path()
        # Priority: player-save file first; if missing, fall back to shipped seed.
        for candidate in (path, self._seed_high_score_path()):
            try:
                with open(candidate, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    out = []
                    for r in data:
                        if isinstance(r, dict) and "initials" in r and "score" in r:
                            out.append({"initials": str(r["initials"])[:3].upper(), "score": int(r["score"])})
                    out.sort(key=lambda x: x["score"], reverse=True)
                    return out[:5]
            except Exception:
                pass
        return []

    def _save_high_scores(self):
        path = self._high_score_path()
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.high_scores[:5], f, indent=2)
        except Exception:
            pass

    def _qualifies_high_score(self, score: int) -> bool:
        if score <= 0:
            return False
        if len(self.high_scores) < 5:
            return True
        return score > int(self.high_scores[-1]["score"])

    def _begin_high_score_entry(self, score: int) -> None:
        self.hs_entry_active = True
        self.hs_initials = ""
        self.hs_pending_score = int(score)
        pygame.mouse.set_visible(True)

    def _commit_high_score(self) -> None:
        initials = (self.hs_initials.strip().upper() + "___")[:3]
        self.high_scores.append({"initials": initials, "score": int(self.hs_pending_score)})
        self.high_scores.sort(key=lambda x: x["score"], reverse=True)
        self.high_scores = self.high_scores[:5]
        self._save_high_scores()
        self.stats.high_score = int(self.high_scores[0]["score"]) if self.high_scores else 0
        self.sb.prep_high_score()
        self.hs_entry_active = False
        self.hs_initials = ""
        self.hs_pending_score = 0

    def _handle_high_score_keydown(self, event) -> None:
        if event.key == pygame.K_ESCAPE:
            self.hs_entry_active = False
            self.hs_initials = ""
            self.hs_pending_score = 0
            return
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            if len(self.hs_initials) == 3:
                self._commit_high_score()
            return
        if event.key == pygame.K_BACKSPACE:
            self.hs_initials = self.hs_initials[:-1]
            return
        ch = getattr(event, "unicode", "")
        if not ch:
            return
        ch = ch.upper()
        if len(self.hs_initials) < 3 and ("A" <= ch <= "Z" or "0" <= ch <= "9"):
            self.hs_initials += ch

    def _fire_bullet(self):
        """No, Kenny! It's not pew-pew! It's BANG-BANG!!"""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
            try:
                self.sfx_pew.play()
            except Exception:
                pass

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
            self._check_extra_life_award()
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
        # ships_left counts the current life too.
        if self.stats.ships_left > 1:
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
            try:
                self.sfx_explosion.play()
            except Exception:
                pass
            self.stats.game_active = False
            pygame.mouse.set_visible(True)
            if self._qualifies_high_score(self.stats.score):
                self._begin_high_score_entry(self.stats.score)

    def _check_extra_life_award(self) -> None:
        """Grant +1 life every 500,000 points."""
        step = 500_000
        nxt = int(getattr(self.stats, "next_extra_life_at", step))
        if nxt <= 0:
            nxt = step
        awarded = False
        while int(self.stats.score) >= nxt:
            self.stats.ships_left += 1
            nxt += step
            awarded = True
        self.stats.next_extra_life_at = nxt
        if awarded:
            self.sb.prep_ships()

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
        if self.stats.game_active:
            try:
                self.sfx_doop.play()
            except Exception:
                pass

    def _update_screen(self):
        """in case the name of the funtion we're describing isn't
        indicative enough: This code updates the screen"""
        if self.bg_image is not None:
            self.screen.blit(self.bg_image, (0, 0))
        else:
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
            self._draw_high_score_panel()

        pygame.display.flip()

    def _draw_high_score_panel(self):
        # Simple overlay leaderboard + initials entry prompt
        panel_w = min(520, self.screen_rect.w - 80)
        panel_h = min(360, self.screen_rect.h - 120)
        panel = pygame.Rect((self.screen_rect.w - panel_w) // 2, 110, panel_w, panel_h)
        pygame.draw.rect(self.screen, (0, 0, 0), panel, border_radius=10)
        pygame.draw.rect(self.screen, (30, 30, 30), panel, width=2, border_radius=10)

        title_font = pygame.font.SysFont(None, 54)
        body_font = pygame.font.SysFont(None, 40)
        t = title_font.render("HIGH SCORES", True, (230, 230, 230))
        self.screen.blit(t, t.get_rect(midtop=(panel.centerx, panel.top + 14)))

        y = panel.top + 80
        if not self.high_scores:
            msg = body_font.render("No scores yet. Be the problem.", True, (210, 210, 210))
            self.screen.blit(msg, msg.get_rect(center=(panel.centerx, y + 30)))
            y += 70
        else:
            for i, row in enumerate(self.high_scores[:5], start=1):
                line = f"{i}. {row['initials']:<3}   {int(row['score']):>6}"
                s = body_font.render(line, True, (210, 210, 210))
                self.screen.blit(s, (panel.left + 40, y))
                y += 36

        if self.hs_entry_active:
            y2 = panel.bottom - 110
            prompt = body_font.render("NEW HIGH SCORE! ENTER INITIALS:", True, (255, 230, 120))
            self.screen.blit(prompt, prompt.get_rect(center=(panel.centerx, y2)))
            initials = (self.hs_initials + "___")[:3]
            ins = title_font.render(initials, True, (255, 230, 120))
            self.screen.blit(ins, ins.get_rect(center=(panel.centerx, y2 + 55)))
            hint = pygame.font.SysFont(None, 28).render("ENTER to save · ESC to cancel", True, (170, 170, 170))
            self.screen.blit(hint, hint.get_rect(center=(panel.centerx, y2 + 92)))


if __name__ == '__main__':
    # GET SOME!!!
    ai = AlienInvasion()
    ai.run_game()