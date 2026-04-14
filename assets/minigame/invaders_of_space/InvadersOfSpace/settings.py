class Settings:
    """this is the setting class...
    ... its a class full of settings..."""

    def __init__(self):
        """ Settings, ENGAGE! """
        # size matters, right ladies?
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (230, 230, 230)

        # Number of lives (3 is enough)
        self.ship_limit = 3

        # idkfa
        self.bullet_width = 5
        self.bullet_height = 15
        self.bullet_color = (60, 60, 60)
        self.bullets_allowed = 5

        # Aliens dropping it like its hot
        self.fleet_drop_speed = 10

        # mayhem acceleration
        self.speedup_scale = 1.1
        # score stonks, bruh!
        self.score_scale = 1.5

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """initializing speed variables like a boss!"""
        self.ship_speed = 1.5
        self.bullet_speed = 3.0
        self.alien_speed = 0.35

        # fleet_direction of 1 represents right; -1 represents left.
        self.fleet_direction = 1

        # yeah 50... why not...
        self.alien_points = 50

    def increase_speed(self):
        """Quickly, now! Quickly!"""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale

        self.alien_points = int(self.alien_points * self.score_scale)