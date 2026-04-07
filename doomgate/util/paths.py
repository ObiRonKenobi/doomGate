from __future__ import annotations

import os
import sys
from typing import Final


_PKG_DIR: Final[str] = os.path.dirname(os.path.abspath(__file__))


def runtime_root_dir() -> str:
    """
    Return a stable writable folder near the executable/script.

    - In normal runs: project folder containing the entry script.
    - In PyInstaller onefile/onedir: folder containing the built executable.
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    # Keep behavior close to prior codebase: path near repository root.
    # `doomgate/util/paths.py` → `doomgate/` → project root
    return os.path.dirname(os.path.dirname(_PKG_DIR))


def resource_dir() -> str:
    """
    Return the directory where bundled read-only resources live.

    In PyInstaller, resources are typically unpacked into `sys._MEIPASS`.
    """
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return str(base)
    return runtime_root_dir()


def resource_path(*parts: str) -> str:
    return os.path.join(resource_dir(), *parts)


def writable_path(*parts: str) -> str:
    return os.path.join(runtime_root_dir(), *parts)

