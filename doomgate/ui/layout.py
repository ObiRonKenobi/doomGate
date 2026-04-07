from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Tuple

import pygame

from ..util.paths import writable_path

UI_DEBUG_HANDLE_PX = 12
UI_DEBUG_EDGE_PX = 6

UI_LAYOUT_FILE = "ui_layout.json"
UI_LAYOUT_DEBUG_F5_FOR_EVERYONE = True

MIN_WINDOW_W, MIN_WINDOW_H = 800, 600
INITIAL_WINDOW_W, INITIAL_WINDOW_H = 1024, 768


def clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, v))


def layout_right_internals(
    right_panel: pygame.Rect,
    commands: List[Dict[str, Any]],
    *,
    manual_row: int = 36,
) -> Dict[str, Any]:
    """Place Held, minimap, inventory, command grid inside the right column."""
    held_h = 52
    gap2 = 8
    y0 = right_panel.y + 5
    rh = right_panel.h - 10
    map_w = max(128, min(252, int(right_panel.w * 0.58)))
    row_h = max(held_h + 8, 112)
    budget = rh - row_h - manual_row - gap2 * 3
    inv_h_single = max(72, min(140, int(max(80, budget) * 0.34)))
    map_h_legacy = max(72, min(140, int(max(80, budget) * 0.34)))
    inv_h = inv_h_single + gap2 + map_h_legacy
    cmd_h = budget - inv_h
    if cmd_h < 80:
        shave = 80 - cmd_h
        inv_h = max(120, inv_h - shave)
        cmd_h = budget - inv_h

    held_y = y0 + (row_h - held_h) // 2
    map_rect = pygame.Rect(right_panel.right - map_w, y0, map_w, row_h)
    held_w = map_rect.x - gap2 - right_panel.x
    held_rect = pygame.Rect(right_panel.x, held_y, held_w, held_h)
    inv_rect = pygame.Rect(right_panel.x, y0 + row_h + gap2, right_panel.w, inv_h)
    cmd_rect = pygame.Rect(right_panel.x, inv_rect.bottom + gap2, right_panel.w, max(80, cmd_h))
    extra_y = cmd_rect.bottom + gap2
    row_btn_h = manual_row - 4
    w3 = (cmd_rect.w - gap2 * 2) // 3
    manual_btn_rect = pygame.Rect(cmd_rect.x, extra_y, w3, row_btn_h)
    music_btn_rect = pygame.Rect(cmd_rect.x + w3 + gap2, extra_y, w3, row_btn_h)
    restart_btn_rect = pygame.Rect(cmd_rect.x + 2 * (w3 + gap2), extra_y, w3, row_btn_h)

    cols = 4
    rows = 2
    btn_h = max(26, min(36, (cmd_rect.h - gap2) // rows - gap2))
    btn_w = (cmd_rect.w - gap2 * (cols - 1)) // cols
    cmd_button_rects: List[Tuple[str, str, pygame.Rect]] = []
    for i, c in enumerate(commands):
        r_i = i // cols
        cc = i % cols
        bx = cmd_rect.x + cc * (btn_w + gap2)
        by_c = cmd_rect.y + r_i * (btn_h + gap2)
        cmd_button_rects.append((c["id"], c["label"], pygame.Rect(bx, by_c, btn_w, btn_h)))

    return {
        "held_rect": held_rect,
        "map_rect": map_rect,
        "inv_rect": inv_rect,
        "cmd_rect": cmd_rect,
        "manual_btn_rect": manual_btn_rect,
        "music_btn_rect": music_btn_rect,
        "restart_btn_rect": restart_btn_rect,
        "cmd_button_rects": cmd_button_rects,
        "top_row_y0": y0,
        "top_row_h": row_h,
    }


def ui_layout_path() -> str:
    return writable_path(UI_LAYOUT_FILE)


def default_ui_layout_overrides() -> Dict[str, Any]:
    return {
        "version": 2,
        "regions": {},
        "map_dx": 0,
        "map_dy": 0,
        "map_w": None,
        "map_h": None,
        "held_h": None,
    }


def load_ui_layout_overrides() -> Dict[str, Any]:
    ov = default_ui_layout_overrides()
    path = ui_layout_path()
    if not os.path.isfile(path):
        return ov
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return ov
    if not isinstance(data, dict):
        return ov
    if "regions" in data and isinstance(data["regions"], dict):
        ov["regions"] = dict(data["regions"])
    for k in ("map_dx", "map_dy", "map_w", "map_h", "held_h"):
        if k in data:
            ov[k] = data[k]
    if "version" in data:
        ov["version"] = data["version"]
    return ov


def save_ui_layout_overrides(ov: Dict[str, Any]) -> Tuple[bool, str]:
    path = ui_layout_path()
    reg = ov.get("regions")
    if isinstance(reg, dict) and len(reg) > 0:
        out: Dict[str, Any] = {"version": 2, "regions": {k: dict(v) for k, v in reg.items() if isinstance(v, dict)}}
    else:
        out = {
            "version": 1,
            "map_dx": int(ov.get("map_dx", 0)),
            "map_dy": int(ov.get("map_dy", 0)),
        }
        for k in ("map_w", "map_h", "held_h"):
            v = ov.get(k)
            if v is not None:
                out[k] = int(v)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)
    except OSError as exc:
        return False, str(exc)
    return True, path


def ui_rect_to_dict(r: pygame.Rect) -> Dict[str, int]:
    return {"x": int(r.x), "y": int(r.y), "w": int(r.w), "h": int(r.h)}


def ui_rect_from_dict(d: Optional[Dict[str, Any]]) -> Optional[pygame.Rect]:
    if not d or not isinstance(d, dict):
        return None
    try:
        return pygame.Rect(int(d["x"]), int(d["y"]), int(d["w"]), int(d["h"]))
    except (KeyError, TypeError, ValueError):
        return None


def ui_clamp_rect_in_parent(r: pygame.Rect, parent: pygame.Rect, *, min_w: int = 4, min_h: int = 4) -> pygame.Rect:
    o = pygame.Rect(r)
    o.w = max(min_w, min(o.w, parent.w))
    o.h = max(min_h, min(o.h, parent.h))
    o.x = clamp(int(o.x), parent.x, parent.right - o.w)
    o.y = clamp(int(o.y), parent.y, parent.bottom - o.h)
    return o


def ui_window_content_rect(W: int, H: int, pad: int, title_bar_h: int) -> pygame.Rect:
    inner_top = pad + title_bar_h
    return pygame.Rect(pad, inner_top, W - 2 * pad, H - inner_top - pad)


def ui_resize_handles_try_begin(
    r: pygame.Rect,
    pos: Tuple[int, int],
    *,
    handle_px: int = UI_DEBUG_HANDLE_PX,
    edge_px: int = UI_DEBUG_EDGE_PX,
) -> Optional[Dict[str, Any]]:
    """Hotspot-style hit test: corner scale, edge axis resize, interior move."""
    if not r.collidepoint(pos):
        return None
    hsz = max(6, min(handle_px, r.w // 2, r.h // 2))
    handle = pygame.Rect(r.right - hsz, r.bottom - hsz, hsz, hsz)
    if not handle.colliderect(r):
        handle = pygame.Rect(r.right - min(hsz, r.w), r.bottom - min(hsz, r.h), min(hsz, r.w), min(hsz, r.h))
    if handle.collidepoint(pos):
        return {"mode": "resize", "w0": float(max(1, r.w)), "h0": float(max(1, r.h)), "tl": (float(r.x), float(r.y))}
    et = max(2, min(edge_px, r.w // 3, r.h // 3))
    c = hsz
    inner_h = r.h - 2 * c
    inner_w = r.w - 2 * c
    if inner_h > 0:
        er = pygame.Rect(r.right - et, r.top + c, et, inner_h)
        if er.collidepoint(pos):
            return {"mode": "resize_e", "l0": float(r.x), "t0": float(r.y), "h0": float(r.h)}
        el = pygame.Rect(r.x, r.top + c, et, inner_h)
        if el.collidepoint(pos):
            return {"mode": "resize_w", "anchor_right": float(r.right), "t0": float(r.y), "h0": float(r.h)}
    if inner_w > 0:
        eb = pygame.Rect(r.left + c, r.bottom - et, inner_w, et)
        if eb.collidepoint(pos):
            return {"mode": "resize_s", "l0": float(r.x), "t0": float(r.y), "w0": float(r.w)}
        et_top = pygame.Rect(r.left + c, r.y, inner_w, et)
        if et_top.collidepoint(pos):
            return {"mode": "resize_n", "l0": float(r.x), "w0": float(r.w), "anchor_bottom": float(r.bottom)}
    return {"mode": "move", "grab": (float(pos[0] - r.x), float(pos[1] - r.y)), "w": float(r.w), "h": float(r.h)}


def ui_resize_handles_apply_motion(
    pos: Tuple[int, int],
    d: Dict[str, Any],
    parent: pygame.Rect,
    min_w: int,
    min_h: int,
    *,
    max_scale_corner: float = 8.0,
) -> pygame.Rect:
    px, py = parent.x, parent.y
    pr, pb = parent.right, parent.bottom

    if d["mode"] == "move":
        gx, gy = d["grab"]
        new_r = pygame.Rect(int(pos[0] - gx), int(pos[1] - gy), int(d["w"]), int(d["h"]))
    elif d["mode"] == "resize":
        tlx, tly = d["tl"]
        w0, h0 = d["w0"], d["h0"]
        dx = float(pos[0]) - tlx
        dy = float(pos[1]) - tly
        if dx < 2.0 or dy < 2.0:
            return pygame.Rect(int(tlx), int(tly), int(w0), int(h0))
        s = min(dx / w0, dy / h0)
        s = max(0.08, min(float(s), max_scale_corner))
        new_r = pygame.Rect(int(tlx), int(tly), max(min_w, int(w0 * s)), max(min_h, int(h0 * s)))
    elif d["mode"] == "resize_e":
        new_w = max(min_w, int(pos[0] - d["l0"]))
        new_r = pygame.Rect(int(d["l0"]), int(d["t0"]), new_w, int(d["h0"]))
    elif d["mode"] == "resize_s":
        new_h = max(min_h, int(pos[1] - d["t0"]))
        new_r = pygame.Rect(int(d["l0"]), int(d["t0"]), int(d["w0"]), new_h)
    elif d["mode"] == "resize_w":
        ar = d["anchor_right"]
        right_bound = max(px, int(ar) - min_w)
        nl = clamp(int(pos[0]), px, right_bound)
        new_w = max(min_w, int(ar - nl))
        new_r = pygame.Rect(nl, int(d["t0"]), new_w, int(d["h0"]))
    elif d["mode"] == "resize_n":
        ab = d["anchor_bottom"]
        bottom_bound = max(py, int(ab) - min_h)
        nt = clamp(int(pos[1]), py, bottom_bound)
        new_h = max(min_h, int(ab - nt))
        new_r = pygame.Rect(int(d["l0"]), nt, int(d["w0"]), new_h)
    else:
        new_r = pygame.Rect(px, py, min_w, min_h)

    new_r.w = max(min_w, min(new_r.w, parent.w))
    new_r.h = max(min_h, min(new_r.h, parent.h))
    new_r.x = clamp(int(new_r.x), px, pr - new_r.w)
    new_r.y = clamp(int(new_r.y), py, pb - new_r.h)
    return new_r


UI_EDIT_REGION_ORDER: List[Tuple[str, str, Tuple[int, int, int]]] = [
    ("cmd", "cmd_rect", (255, 200, 120)),
    ("inv", "inv_rect", (200, 255, 180)),
    ("map", "map_rect", (255, 120, 200)),
    ("held", "held_rect", (120, 200, 255)),
    ("right_panel", "right_panel", (200, 150, 100)),
    ("log", "log_rect", (150, 200, 255)),
    ("status", "status_rect", (180, 180, 255)),
    ("text_panel", "text_panel", (200, 220, 100)),
    ("viewport", "viewport_rect", (255, 100, 100)),
]

UI_EDIT_REGION_MINS: Dict[str, Tuple[int, int]] = {
    "viewport": (120, 100),
    "text_panel": (120, 80),
    "status": (80, 22),
    "log": (80, 40),
    "right_panel": (160, 120),
    "held": (48, 36),
    "map": (80, 48),
    "inv": (100, 72),
    "cmd": (120, 72),
}


def _apply_legacy_map_held_overrides(lay: Dict[str, Any], ov: Dict[str, Any]) -> None:
    rp = lay["right_panel"]
    gap2 = int(lay["layout_gap2"])
    y0 = int(lay["top_row_y0"])
    base_row_h = int(lay["top_row_h"])
    base_mr = lay["map_rect"]
    base_hr = lay["held_rect"]
    mw = int(ov["map_w"]) if ov.get("map_w") is not None else int(base_mr.w)
    mh = int(ov["map_h"]) if ov.get("map_h") is not None else int(base_mr.h)
    hh = int(ov["held_h"]) if ov.get("held_h") is not None else int(base_hr.h)
    mh = max(48, min(mh, base_row_h))
    hh = max(36, min(hh, base_row_h))
    mw = max(80, min(mw, max(80, rp.w - gap2 - 48)))
    mdx = int(ov.get("map_dx", 0))
    mdy = int(ov.get("map_dy", 0))
    row_h = base_row_h
    ref_y = y0 + (row_h - mh) // 2
    map_x = rp.right - mw + mdx
    map_y = ref_y + mdy
    min_held = 48
    map_x_min = rp.x + min_held + gap2
    map_x_max = rp.right - mw
    if map_x_max < map_x_min:
        map_x_max = map_x_min
    map_x = clamp(map_x, map_x_min, map_x_max)
    held_w = map_x - gap2 - rp.x
    held_y = y0 + (row_h - hh) // 2
    map_y = clamp(map_y, y0, y0 + row_h - mh)
    lay["map_rect"] = pygame.Rect(map_x, map_y, mw, mh)
    lay["held_rect"] = pygame.Rect(rp.x, held_y, max(40, held_w), hh)


def apply_ui_layout_overrides(lay: Dict[str, Any], ov: Optional[Dict[str, Any]], commands: List[Dict[str, Any]]) -> None:
    if not ov:
        return
    reg = ov.get("regions")
    if isinstance(reg, dict) and len(reg) > 0:
        W, H = lay["W"], lay["H"]
        pad = lay["pad"]
        title_bar_h = lay["title_bar_h"]
        gap = int(lay.get("gap_main", 8))
        gap2 = 8
        content = ui_window_content_rect(W, H, pad, title_bar_h)
        bottom_rect = lay["bottom_rect"]

        if ui_rect_from_dict(reg.get("viewport")) is not None:
            vr = ui_rect_from_dict(reg["viewport"])
            assert vr is not None
            vr = ui_clamp_rect_in_parent(vr, content, min_w=120, min_h=100)
            lay["viewport_rect"] = vr
            by = vr.bottom + gap
            bottom_rect = pygame.Rect(pad, by, W - pad * 2, H - by - pad)
            lay["bottom_rect"] = bottom_rect

        if ui_rect_from_dict(reg.get("text_panel")) is not None:
            tp = ui_rect_from_dict(reg["text_panel"])
            assert tp is not None
            lay["text_panel"] = ui_clamp_rect_in_parent(tp, bottom_rect, min_w=120, min_h=80)
        else:
            tw = int(bottom_rect.w * 0.56)
            lay["text_panel"] = pygame.Rect(bottom_rect.x, bottom_rect.y, tw, bottom_rect.h)

        tp2 = lay["text_panel"]
        if ui_rect_from_dict(reg.get("right_panel")) is not None:
            rp_r = ui_rect_from_dict(reg["right_panel"])
            assert rp_r is not None
            lay["right_panel"] = ui_clamp_rect_in_parent(rp_r, bottom_rect, min_w=160, min_h=120)
        else:
            lay["right_panel"] = pygame.Rect(tp2.right + gap, bottom_rect.y, bottom_rect.right - tp2.right - gap, bottom_rect.h)

        tp3 = lay["text_panel"]
        if ui_rect_from_dict(reg.get("status")) is not None:
            sr = ui_rect_from_dict(reg["status"])
            assert sr is not None
            lay["status_rect"] = ui_clamp_rect_in_parent(sr, tp3, min_w=80, min_h=22)
        else:
            lay["status_rect"] = pygame.Rect(tp3.x + 10, tp3.y + 10, tp3.w - 20, 26)
        if ui_rect_from_dict(reg.get("log")) is not None:
            lr = ui_rect_from_dict(reg["log"])
            assert lr is not None
            lay["log_rect"] = ui_clamp_rect_in_parent(lr, tp3, min_w=80, min_h=40)
        else:
            st = lay["status_rect"]
            log_top = st.bottom + 10
            lay["log_rect"] = pygame.Rect(tp3.x + 10, log_top, tp3.w - 20, tp3.bottom - log_top - 10)

        rp = lay["right_panel"]
        ri = layout_right_internals(rp, commands)
        lay["layout_gap2"] = gap2
        lay["top_row_y0"] = ri["top_row_y0"]
        lay["top_row_h"] = ri["top_row_h"]
        for k in ("manual_btn_rect", "music_btn_rect", "restart_btn_rect", "cmd_button_rects"):
            lay[k] = ri[k]
        for rkey, lkey in (("held", "held_rect"), ("map", "map_rect"), ("inv", "inv_rect"), ("cmd", "cmd_rect")):
            lay[lkey] = ri[lkey]

        rp2 = lay["right_panel"]
        mw, mh = UI_EDIT_REGION_MINS["map"]
        hw, hh = UI_EDIT_REGION_MINS["held"]
        iw, ih = UI_EDIT_REGION_MINS["inv"]
        cw, ch = UI_EDIT_REGION_MINS["cmd"]
        if ui_rect_from_dict(reg.get("held")) is not None:
            hr = ui_rect_from_dict(reg["held"])
            assert hr is not None
            lay["held_rect"] = ui_clamp_rect_in_parent(hr, rp2, min_w=hw, min_h=hh)
        if ui_rect_from_dict(reg.get("map")) is not None:
            mr = ui_rect_from_dict(reg["map"])
            assert mr is not None
            lay["map_rect"] = ui_clamp_rect_in_parent(mr, rp2, min_w=mw, min_h=mh)
        if ui_rect_from_dict(reg.get("inv")) is not None:
            ir_ = ui_rect_from_dict(reg["inv"])
            assert ir_ is not None
            lay["inv_rect"] = ui_clamp_rect_in_parent(ir_, rp2, min_w=iw, min_h=ih)
        if ui_rect_from_dict(reg.get("cmd")) is not None:
            cr = ui_rect_from_dict(reg["cmd"])
            assert cr is not None
            lay["cmd_rect"] = ui_clamp_rect_in_parent(cr, rp2, min_w=cw, min_h=ch)

        cmd_r = lay["cmd_rect"]
        manual_row = 36
        row_btn_h = manual_row - 4
        g2 = gap2
        w3 = (cmd_r.w - g2 * 2) // 3
        extra_y = cmd_r.bottom + g2
        lay["manual_btn_rect"] = pygame.Rect(cmd_r.x, extra_y, w3, row_btn_h)
        lay["music_btn_rect"] = pygame.Rect(cmd_r.x + w3 + g2, extra_y, w3, row_btn_h)
        lay["restart_btn_rect"] = pygame.Rect(cmd_r.x + 2 * (w3 + g2), extra_y, w3, row_btn_h)

        cols = 4
        rows = 2
        btn_h = max(26, min(36, (cmd_r.h - g2) // rows - g2))
        btn_w = (cmd_r.w - g2 * (cols - 1)) // cols
        cmd_button_rects: List[Tuple[str, str, pygame.Rect]] = []
        for i, c in enumerate(commands):
            r_i = i // cols
            cc = i % cols
            bx = cmd_r.x + cc * (btn_w + g2)
            by_c = cmd_r.y + r_i * (btn_h + g2)
            cmd_button_rects.append((c["id"], c["label"], pygame.Rect(bx, by_c, btn_w, btn_h)))
        lay["cmd_button_rects"] = cmd_button_rects
        return

    legacy = (
        ov.get("map_w") is not None
        or ov.get("map_h") is not None
        or ov.get("held_h") is not None
        or int(ov.get("map_dx", 0)) != 0
        or int(ov.get("map_dy", 0)) != 0
    )
    if legacy:
        _apply_legacy_map_held_overrides(lay, ov)


def sync_ui_layout_overrides_from_lay(lay: Dict[str, Any], ov: Dict[str, Any]) -> None:
    reg: Dict[str, Any] = {}
    for region_key, lay_key, _ in UI_EDIT_REGION_ORDER:
        rr = lay.get(lay_key)
        if isinstance(rr, pygame.Rect):
            reg[region_key] = ui_rect_to_dict(rr)
    ov["regions"] = reg
    ov["version"] = 2


def compute_layout(
    W: int,
    H: int,
    commands: List[Dict[str, Any]],
    *,
    pad: int = 14,
    title_bar_h: int = 40,
) -> Dict[str, Any]:
    W, H = max(MIN_WINDOW_W, W), max(MIN_WINDOW_H, H)
    inner_h = H - pad * 2 - title_bar_h
    gap = 8
    viewport_h = max(180, min(520, int(inner_h * 0.50)))
    bottom_h = inner_h - viewport_h - gap
    if bottom_h < 170:
        viewport_h = max(160, inner_h - gap - 170)
        bottom_h = inner_h - viewport_h - gap
    viewport_rect = pygame.Rect(pad, pad + title_bar_h, W - pad * 2, viewport_h)
    bottom_y = viewport_rect.bottom + gap
    bottom_rect = pygame.Rect(pad, bottom_y, W - pad * 2, H - bottom_y - pad)
    left_w = int(bottom_rect.w * 0.56)
    text_panel = pygame.Rect(bottom_rect.x, bottom_rect.y, left_w, bottom_rect.h)
    right_panel = pygame.Rect(text_panel.right + gap, bottom_rect.y, bottom_rect.w - left_w - gap, bottom_rect.h)
    status_h = 26
    status_rect = pygame.Rect(text_panel.x + 10, text_panel.y + 10, text_panel.w - 20, status_h)
    log_top = status_rect.bottom + 10
    log_rect = pygame.Rect(text_panel.x + 10, log_top, text_panel.w - 20, text_panel.bottom - log_top - 10)

    gap2 = 8
    ri = layout_right_internals(right_panel, commands)

    return {
        "W": W,
        "H": H,
        "pad": pad,
        "title_bar_h": title_bar_h,
        "viewport_rect": viewport_rect,
        "bottom_rect": bottom_rect,
        "gap_main": gap,
        "text_panel": text_panel,
        "right_panel": right_panel,
        "status_rect": status_rect,
        "log_rect": log_rect,
        "held_rect": ri["held_rect"],
        "inv_rect": ri["inv_rect"],
        "map_rect": ri["map_rect"],
        "cmd_rect": ri["cmd_rect"],
        "manual_btn_rect": ri["manual_btn_rect"],
        "music_btn_rect": ri["music_btn_rect"],
        "restart_btn_rect": ri["restart_btn_rect"],
        "cmd_button_rects": ri["cmd_button_rects"],
        "top_row_y0": ri["top_row_y0"],
        "top_row_h": ri["top_row_h"],
        "layout_gap2": gap2,
    }

