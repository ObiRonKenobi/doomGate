from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Tuple

import pygame

from ..util.paths import writable_path

HS_DEBUG_HANDLE_PX = 12
HS_DEBUG_EDGE_PX = 6

HOTSPOT_LAYOUT_FILE = "hotspot_layout.json"


def hotspot_layout_path() -> str:
    return writable_path(HOTSPOT_LAYOUT_FILE)


def rect_from_pct(x: float, y: float, w: float, h: float, parent: pygame.Rect) -> pygame.Rect:
    return pygame.Rect(
        int(parent.x + parent.w * (x / 100.0)),
        int(parent.y + parent.h * (y / 100.0)),
        int(parent.w * (w / 100.0)),
        int(parent.h * (h / 100.0)),
    )


def screen_rect_to_pct(r: pygame.Rect, parent: pygame.Rect) -> Tuple[float, float, float, float]:
    rx = r.x - parent.x
    ry = r.y - parent.y
    pw = max(1, parent.w)
    ph = max(1, parent.h)
    return (
        100.0 * rx / pw,
        100.0 * ry / ph,
        100.0 * r.w / pw,
        100.0 * r.h / ph,
    )


def clamp_hotspot_pct_rect(l: float, t: float, w: float, h: float) -> Tuple[float, float, float, float]:
    l = max(0.0, min(float(l), 99.5))
    t = max(0.0, min(float(t), 99.5))
    w = max(0.25, min(float(w), 100.0 - l))
    h = max(0.25, min(float(h), 100.0 - t))
    return (l, t, w, h)


def apply_hotspot_layout_overrides(game: Dict[str, Any]) -> None:
    path = hotspot_layout_path()
    if not os.path.isfile(path):
        return
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return
    rooms_patch = data.get("rooms")
    if not isinstance(rooms_patch, dict):
        return
    for rid, hs_patch in rooms_patch.items():
        room = game["rooms"].get(rid)
        if not room or not isinstance(hs_patch, dict):
            continue
        by_id = {hs["id"]: hs for hs in room.get("hotspots", [])}
        for hid, rect in hs_patch.items():
            hs_obj = by_id.get(str(hid))
            if not hs_obj or not isinstance(rect, dict):
                continue
            for key in ("l", "t", "w", "h"):
                if key in rect:
                    hs_obj["rect"][key] = float(rect[key])
            l, t, wp, hp = clamp_hotspot_pct_rect(
                hs_obj["rect"]["l"],
                hs_obj["rect"]["t"],
                hs_obj["rect"]["w"],
                hs_obj["rect"]["h"],
            )
            hs_obj["rect"]["l"], hs_obj["rect"]["t"], hs_obj["rect"]["w"], hs_obj["rect"]["h"] = l, t, wp, hp


def save_hotspot_layout_to_disk(game: Dict[str, Any]) -> Tuple[bool, str]:
    path = hotspot_layout_path()
    out: Dict[str, Any] = {"version": 1, "rooms": {}}
    for rid, room in game["rooms"].items():
        bucket: Dict[str, Any] = {}
        for hs in room.get("hotspots", []):
            rr = hs["rect"]
            bucket[hs["id"]] = {
                "l": round(float(rr["l"]), 2),
                "t": round(float(rr["t"]), 2),
                "w": round(float(rr["w"]), 2),
                "h": round(float(rr["h"]), 2),
            }
        out["rooms"][rid] = bucket
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)
    except OSError as exc:
        return False, str(exc)
    return True, path


def clamp_int(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, v))


class HotspotEditor:
    """
    Drag/resize hotspot rectangles in viewport space (F3/F4 tool).

    This editor is intentionally stateless between drags; it mutates the passed
    hotspot dicts (their pct-rect fields).
    """

    def __init__(self) -> None:
        self.drag: Optional[Dict[str, Any]] = None

    def try_begin(
        self,
        pos: Tuple[int, int],
        pairs: List[Tuple[Dict[str, Any], pygame.Rect, bool]],
    ) -> bool:
        for hs, r, _disabled in reversed(pairs):
            hsz = max(6, min(HS_DEBUG_HANDLE_PX, r.w // 2, r.h // 2))
            handle = pygame.Rect(r.right - hsz, r.bottom - hsz, hsz, hsz)
            if not handle.colliderect(r):
                handle = pygame.Rect(r.right - min(hsz, r.w), r.bottom - min(hsz, r.h), min(hsz, r.w), min(hsz, r.h))
            if handle.collidepoint(pos):
                self.drag = {"mode": "resize", "hs": hs, "w0": float(max(1, r.w)), "h0": float(max(1, r.h)), "tl": (float(r.x), float(r.y))}
                return True
            c = hsz
            et = max(2, min(HS_DEBUG_EDGE_PX, r.w // 3, r.h // 3))
            inner_h = r.h - 2 * c
            inner_w = r.w - 2 * c
            if inner_h > 0:
                er = pygame.Rect(r.right - et, r.top + c, et, inner_h)
                if er.collidepoint(pos):
                    self.drag = {"mode": "resize_e", "hs": hs, "l0": float(r.x), "t0": float(r.y), "h0": float(r.h)}
                    return True
                el = pygame.Rect(r.x, r.top + c, et, inner_h)
                if el.collidepoint(pos):
                    self.drag = {"mode": "resize_w", "hs": hs, "anchor_right": float(r.right), "t0": float(r.y), "h0": float(r.h)}
                    return True
            if inner_w > 0:
                eb = pygame.Rect(r.left + c, r.bottom - et, inner_w, et)
                if eb.collidepoint(pos):
                    self.drag = {"mode": "resize_s", "hs": hs, "l0": float(r.x), "t0": float(r.y), "w0": float(r.w)}
                    return True
                et_top = pygame.Rect(r.left + c, r.y, inner_w, et)
                if et_top.collidepoint(pos):
                    self.drag = {"mode": "resize_n", "hs": hs, "l0": float(r.x), "w0": float(r.w), "anchor_bottom": float(r.bottom)}
                    return True
            if r.collidepoint(pos):
                self.drag = {"mode": "move", "hs": hs, "grab": (float(pos[0] - r.x), float(pos[1] - r.y)), "w": r.w, "h": r.h}
                return True
        return False

    def apply_motion(self, pos: Tuple[int, int], viewport_rect: pygame.Rect) -> None:
        d = self.drag
        if d is None:
            return
        hs = d["hs"]

        def rect_to_hs_pct(new_r: pygame.Rect) -> None:
            new_r.clamp_ip(viewport_rect)
            l, t, wp, hp = screen_rect_to_pct(new_r, viewport_rect)
            l, t, wp, hp = clamp_hotspot_pct_rect(l, t, wp, hp)
            hs["rect"]["l"], hs["rect"]["t"], hs["rect"]["w"], hs["rect"]["h"] = l, t, wp, hp

        if d["mode"] == "move":
            gx, gy = d["grab"]
            new_r = pygame.Rect(int(pos[0] - gx), int(pos[1] - gy), int(d["w"]), int(d["h"]))
            rect_to_hs_pct(new_r)
        elif d["mode"] == "resize":
            tlx, tly = d["tl"]
            w0, h0 = d["w0"], d["h0"]
            dx = float(pos[0]) - tlx
            dy = float(pos[1]) - tly
            if dx < 2.0 or dy < 2.0:
                return
            s = min(dx / w0, dy / h0)
            s = max(0.08, min(float(s), 24.0))
            new_w = max(4, int(w0 * s))
            new_h = max(4, int(h0 * s))
            new_r = pygame.Rect(int(tlx), int(tly), new_w, new_h)
            rect_to_hs_pct(new_r)
        elif d["mode"] == "resize_e":
            new_w = max(4, int(pos[0] - d["l0"]))
            new_r = pygame.Rect(int(d["l0"]), int(d["t0"]), new_w, int(d["h0"]))
            rect_to_hs_pct(new_r)
        elif d["mode"] == "resize_s":
            new_h = max(4, int(pos[1] - d["t0"]))
            new_r = pygame.Rect(int(d["l0"]), int(d["t0"]), int(d["w0"]), new_h)
            rect_to_hs_pct(new_r)
        elif d["mode"] == "resize_w":
            ar = d["anchor_right"]
            right_bound = max(viewport_rect.x, int(ar) - 4)
            nl = clamp_int(int(pos[0]), viewport_rect.x, right_bound)
            new_w = max(4, int(ar - nl))
            new_r = pygame.Rect(nl, int(d["t0"]), new_w, int(d["h0"]))
            rect_to_hs_pct(new_r)
        elif d["mode"] == "resize_n":
            ab = d["anchor_bottom"]
            bottom_bound = max(viewport_rect.y, int(ab) - 4)
            nt = clamp_int(int(pos[1]), viewport_rect.y, bottom_bound)
            new_h = max(4, int(ab - nt))
            new_r = pygame.Rect(int(d["l0"]), nt, int(d["w0"]), new_h)
            rect_to_hs_pct(new_r)

    def end_drag(self) -> Optional[Dict[str, Any]]:
        d = self.drag
        self.drag = None
        if d is None:
            return None
        return d.get("hs")

