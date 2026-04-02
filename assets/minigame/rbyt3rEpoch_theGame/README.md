# RBYT3R Epoch

Fast top-down arcade survival: clear demon waves, grab pickups, spend surge meter for a screen-wide purge, and chase local high scores.

## Run

**Requirements:** Python 3.10+

```bash
pip install -r requirements.txt
python -m rbyt3r_epoch
```

**Controls:** WASD / arrows — move · mouse — aim and fire · Space — surge purge (when charged)

Scores are stored in `leaderboard.db` next to the project (SQLite, no network).

## Embed in another Pygame project

Run the mini-game in its own window (simplest):

```python
from rbyt3r_epoch import run_minigame

run_minigame()
```

To draw inside part of the screen, pass the parent surface and a rectangle (typically 800×600):

```python
import pygame
from rbyt3r_epoch.game import Rbyt3rEpochGame

# After pygame.display.set_mode(...) and each frame:
mini = Rbyt3rEpochGame(surface=screen, area=pygame.Rect(40, 40, 800, 600))
mini.run()  # owns the loop until quit; for tighter integration, factor tick/draw from game.py
```

For full integration (your main loop, your events), copy patterns from `Rbyt3rEpochGame.handle_events`, `update`, and `draw`, or subclass and split the loop.
