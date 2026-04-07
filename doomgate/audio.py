from __future__ import annotations

import json
import os
from typing import Any, Dict

import pygame

from .util.paths import writable_path

AUDIO_SETTINGS_FILE = "audio_settings.json"
MUSIC_VOL_HOVER_DELAY_MS = 1000


def audio_settings_path() -> str:
    return writable_path(AUDIO_SETTINGS_FILE)


def load_audio_settings() -> Dict[str, Any]:
    out: Dict[str, Any] = {"music_volume": 1.0}
    path = audio_settings_path()
    if not os.path.isfile(path):
        return out
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return out
    if not isinstance(data, dict):
        return out
    v = data.get("music_volume")
    if isinstance(v, (int, float)):
        out["music_volume"] = max(0.0, min(1.0, float(v)))
    return out


def save_audio_settings(settings: Dict[str, Any]) -> None:
    path = audio_settings_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {"music_volume": round(float(settings.get("music_volume", 1.0)), 4)},
                f,
                indent=2,
            )
    except OSError:
        pass


def music_vol_popup_rect(music_btn: pygame.Rect, lay: Dict[str, Any], clamp_fn) -> pygame.Rect:
    """Place the popup so it does not overlap the command row (SAVE / LOAD / verbs)."""
    W, H = lay["W"], lay["H"]
    pad = lay["pad"]
    tb = lay["title_bar_h"]
    cmd_rect = lay["cmd_rect"]
    pw, ph = 184, 48
    x = int(music_btn.centerx - pw // 2)
    top_min = pad + tb + 4
    y_above = int(music_btn.y - ph - 8)
    min_clear_above = int(cmd_rect.bottom + 8)
    if y_above >= min_clear_above and y_above >= top_min:
        y = y_above
    else:
        y = int(music_btn.bottom + 8)
    y = clamp_fn(y, top_min, H - pad - ph)
    x = clamp_fn(x, pad, W - pad - pw)
    pr = pygame.Rect(x, y, pw, ph)
    if pr.colliderect(cmd_rect.inflate(0, 4)):
        y = int(max(music_btn.bottom + 8, cmd_rect.bottom + 8))
        y = clamp_fn(y, top_min, H - pad - ph)
        pr = pygame.Rect(x, y, pw, ph)
    return pr


def music_vol_track_inner(popup: pygame.Rect) -> pygame.Rect:
    return pygame.Rect(popup.x + 12, popup.y + 30, popup.w - 24, 10)


def music_volume_from_track_x(track: pygame.Rect, x: float) -> float:
    return max(0.0, min(1.0, (float(x) - track.x) / max(1, track.w)))


def draw_music_volume_popup(
    screen: pygame.Surface,
    popup: pygame.Rect,
    volume: float,
    colors: Dict[str, Any],
    font: pygame.font.Font,
    clamp_fn,
) -> None:
    pygame.draw.rect(screen, colors["panel2"], popup, border_radius=8)
    pygame.draw.rect(screen, colors["border"], popup, width=1, border_radius=8)
    screen.blit(font.render("Music volume", True, colors["text"]), (popup.x + 12, popup.y + 8))
    tr = music_vol_track_inner(popup)
    pygame.draw.rect(screen, (14, 20, 16), tr, border_radius=4)
    fill_w = max(0, int(round(tr.w * volume)))
    if fill_w > 0:
        pygame.draw.rect(screen, colors["accent_dim"], pygame.Rect(tr.x, tr.y, fill_w, tr.h), border_radius=4)
    pygame.draw.rect(screen, colors["accent"], tr, width=1, border_radius=4)
    cx = int(tr.x + volume * tr.w)
    cx = clamp_fn(cx, tr.x + 3, tr.x + tr.w - 3)
    knob = pygame.Rect(0, 0, 12, 20)
    knob.center = (cx, tr.centery)
    pygame.draw.rect(screen, colors["text"], knob, border_radius=5)
    pygame.draw.rect(screen, colors["accent"], knob, width=1, border_radius=5)
    pct = int(round(volume * 100))
    pct_s = font.render(f"{pct}%", True, colors["muted"])
    screen.blit(pct_s, (popup.right - pct_s.get_width() - 12, popup.y + 8))

