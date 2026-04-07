"""
DoomGate launcher (backward compatible).

- Run the game: `python main.py`
- Preferred package entry: `python -m doomgate`
"""

from __future__ import annotations


def main() -> int:
    from doomgate.ui_runtime import run

    return int(run())


if __name__ == "__main__":
    raise SystemExit(main())
