from __future__ import annotations

import json
import os
from typing import Any, Callable, Dict, Optional

from doomgate.game import merge_loaded_save

SAVE_SLOT_COUNT = 3


def slot_filename(slot: int) -> str:
    if slot < 0 or slot >= SAVE_SLOT_COUNT:
        raise ValueError("slot out of range")
    return f"savegame{slot + 1}.json"


def slot_path(game: Dict[str, Any], slot: int, writable_path: Callable[..., str]) -> str:
    return writable_path(slot_filename(slot))


def legacy_single_save_path(game: Dict[str, Any], writable_path: Callable[..., str]) -> str:
    return writable_path(str(game["meta"]["saveFile"]))


def effective_load_path(
    game: Dict[str, Any], slot: int, writable_path: Callable[..., str]
) -> Optional[str]:
    """Path to read for this slot: numbered file, or legacy savegame.json for slot 0 only."""
    p = slot_path(game, slot, writable_path)
    if os.path.isfile(p):
        return p
    if slot == 0:
        leg = legacy_single_save_path(game, writable_path)
        if os.path.isfile(leg):
            return leg
    return None


def peek_slot(
    game: Dict[str, Any], slot: int, writable_path: Callable[..., str]
) -> Optional[Dict[str, Any]]:
    """
    Return display metadata for a slot, or None if empty/unreadable.
    Keys: roomId, roomName, actions, alive
    """
    path = effective_load_path(game, slot, writable_path)
    if not path:
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        if not isinstance(raw, dict):
            return None
        rid = str(raw.get("roomId", ""))
        rooms = game.get("rooms") or {}
        if rid in rooms:
            room_name = str(rooms[rid].get("name", rid))
        else:
            room_name = rid or "Unknown"
        return {
            "path": path,
            "roomId": rid,
            "roomName": room_name,
            "actions": int(raw.get("actions", 0)),
            "alive": bool(raw.get("alive", True)),
        }
    except Exception:
        return None


def write_slot(
    game: Dict[str, Any], state: Dict[str, Any], slot: int, writable_path: Callable[..., str]
) -> str:
    """Write current state to the numbered slot file. Removes legacy savegame.json when saving slot 0."""
    path = slot_path(game, slot, writable_path)
    payload = json.dumps(state, indent=2)
    with open(path, "w", encoding="utf-8") as f:
        f.write(payload)
    if slot == 0:
        leg = legacy_single_save_path(game, writable_path)
        if (
            os.path.isfile(leg)
            and os.path.normcase(os.path.abspath(leg)) != os.path.normcase(os.path.abspath(path))
        ):
            try:
                os.remove(leg)
            except OSError:
                pass
    return path


def load_slot_into_state(
    game: Dict[str, Any],
    state: Dict[str, Any],
    slot: int,
    writable_path: Callable[..., str],
) -> bool:
    """Replace state from disk. Returns False if slot is empty or corrupt."""
    path = effective_load_path(game, slot, writable_path)
    if not path:
        return False
    try:
        with open(path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        if not isinstance(loaded, dict):
            return False
        base = merge_loaded_save(game, loaded)
        state.clear()
        state.update(base)
        return True
    except Exception:
        return False
