"""Local high scores (SQLite, stdlib only)."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import List, Tuple

# Shipped with the game; shown until real players beat these scores (empty DB only).
# Edit initials (3 letters) and scores before release.
SHIPPED_HIGH_SCORES: List[Tuple[str, int]] = [
    ("SDL", 88_888),
    ("BYT", 77_770),
    ("R3D", 66_660),
    ("LDU", 55_550),
    ("G8R", 44_440),
]

_SCHEMA = """
CREATE TABLE IF NOT EXISTS leaderboard (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    initials TEXT NOT NULL,
    score INTEGER NOT NULL,
    date DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""


def _connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute(_SCHEMA)
    conn.commit()
    return conn


def ensure_default_scores(db_path: Path) -> None:
    """If the leaderboard is empty, insert SHIPPED_HIGH_SCORES (first install / new save)."""
    with _connect(db_path) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM leaderboard")
        if int(cur.fetchone()[0]) > 0:
            return
        for initials, score in SHIPPED_HIGH_SCORES:
            conn.execute(
                "INSERT INTO leaderboard (initials, score) VALUES (?, ?)",
                (initials.upper()[:3], int(score)),
            )
        conn.commit()


def get_top_scores(db_path: Path, limit: int = 5) -> List[Tuple[str, int]]:
    ensure_default_scores(db_path)
    with _connect(db_path) as conn:
        cur = conn.execute(
            "SELECT initials, score FROM leaderboard ORDER BY score DESC LIMIT ?",
            (limit,),
        )
        return [(str(r[0]), int(r[1])) for r in cur.fetchall()]


def is_high_score(db_path: Path, score: int, limit: int = 5) -> bool:
    rows = get_top_scores(db_path, limit)
    if len(rows) < limit:
        return True
    return score > rows[-1][1]


def submit_score(db_path: Path, initials: str, score: int) -> None:
    initials = initials.upper().strip()[:3]
    if len(initials) != 3 or not initials.isalpha():
        raise ValueError("Initials must be 3 letters")
    with _connect(db_path) as conn:
        conn.execute(
            "INSERT INTO leaderboard (initials, score) VALUES (?, ?)",
            (initials, score),
        )
        conn.commit()
