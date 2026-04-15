class GameStats:
    """Stats: as they pertain to the game"""

    def __init__(self, ai_game):
        """Statistics, ready for launch!"""
        self.settings = ai_game.settings
        self.reset_stats()

        # start it... but don't... only kinda start it
        self.game_active = False

        # itialize the shizz out that highscore
        self.high_score = 0

    def reset_stats(self):
        """starting point"""
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1
        # Extra lives: first at 500k, then the required points ramp up with the game's scoring.
        self.extra_life_step = 500_000
        self.next_extra_life_at = 500_000