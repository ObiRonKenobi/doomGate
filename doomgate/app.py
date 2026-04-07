from __future__ import annotations


def run() -> int:
    """
    Temporary compatibility entrypoint.

    During the refactor we progressively move logic out of the legacy top-level
    `main.py` into the `doomgate/` package. For now, this delegates to it so the
    game remains runnable at each step.
    """
    from doomgate.ui_runtime import run as ui_run

    return int(ui_run())

