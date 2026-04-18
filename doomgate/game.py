from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Protocol


# Pieces needed before Soul-Core Breaker assembly; used for inventory voice cue.
_SOUL_CORE_PIECES = ("soulCoreFrame", "omegaCrystal", "neuralLink", "serpentineKey")
_SOUL_CORE_VOICE_FLAG = "heardAssembleSoulCoreBreaker"
_soul_core_voice_sound = None  # pygame.mixer.Sound cache


class LogLike(Protocol):
    def add(self, text: str, kind: str = "line") -> None: ...


def clamp_int(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, int(v)))


def default_state(game: Dict[str, Any]) -> Dict[str, Any]:
    n0 = int(game["meta"]["startLanterns"])
    ap = int(game["meta"]["actionsPerLantern"])
    return {
        "roomId": "hangar",
        "inventory": [],
        "heldItemId": None,
        "cmd": "look",
        "flags": {},
        "seenRooms": {},
        "roomIntroShown": {},
        "pendingRoomPopup": None,
        "pendingVictoryPopup": False,
        "pendingLindaTerminal": False,
        "lindaWrongCount": 0,
        "actions": game["meta"]["startActions"],
        # Charger packs you carry (consumed when refilling the orb meter).
        "lanterns": n0,
        # Plasma orb remaining actions (drains every timed action; refilled by using the charger tool).
        "plasma": ap,
        "alive": True,
        "godMode": False,
        "hotspotDebugUnlocked": False,
        "portraitExcitedUntil": 0,
    }


def merge_loaded_save(game: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
    """Merge a JSON-loaded dict onto defaults and normalize plasma/charger fields."""
    base = default_state(game)
    base.update(loaded)
    if base.get("cmd") == "close":
        base["cmd"] = "whistle"
    base.setdefault("flags", {})
    base.setdefault("seenRooms", {})
    base.setdefault("roomIntroShown", {})
    base.setdefault("pendingRoomPopup", None)
    base.setdefault("pendingVictoryPopup", False)
    base.setdefault("pendingLindaTerminal", False)
    base.setdefault("lindaWrongCount", 0)
    base.setdefault("godMode", False)
    base.setdefault("hotspotDebugUnlocked", False)
    base.setdefault("portraitExcitedUntil", 0)
    base.setdefault("inventory", [])

    ap = int(game["meta"]["actionsPerLantern"])
    mx = int(game["meta"]["lanternMaxCarry"])
    # Old saves may have lanternCount/lanterns computed from actions. We now treat lanterns as charger packs carried.
    if "lanterns" not in base or base.get("lanterns") is None:
        base["lanterns"] = int(game["meta"]["startLanterns"])
    base["lanterns"] = clamp_int(int(base.get("lanterns", 0)), 0, mx)
    # Plasma orb remaining actions. If missing, derive from old action segment (full when modulo is 0).
    if "plasma" not in base or base.get("plasma") is None:
        seg = int(base.get("actions", 0)) % max(ap, 1)
        base["plasma"] = ap if seg == 0 else max(0, ap - seg)
    base["plasma"] = clamp_int(int(base.get("plasma", ap)), 0, max(ap, 1))
    sort_inventory(game, base)
    return base


def item_def(game: Dict[str, Any], item_id: str) -> Dict[str, Any]:
    return game["items"][item_id]


def room_def(game: Dict[str, Any], room_id: str) -> Dict[str, Any]:
    return game["rooms"][room_id]


def has_item(state: Dict[str, Any], item_id: str) -> bool:
    return item_id in state["inventory"]


def get_flag(state: Dict[str, Any], name: str) -> bool:
    return bool(state["flags"].get(name, False))


def set_flag(state: Dict[str, Any], name: str, value: bool = True) -> None:
    state["flags"][name] = value


def enable_god_mode(game: Dict[str, Any], state: Dict[str, Any], log: LogLike) -> None:
    state["godMode"] = True
    state["alive"] = True
    mx = int(game["meta"]["lanternMaxCarry"])
    state["actions"] = int(game["meta"]["startActions"])
    state["lanterns"] = mx
    state["plasma"] = int(game["meta"]["actionsPerLantern"])
    for iid in game["items"].keys():
        if iid not in state["inventory"]:
            state["inventory"].append(iid)
    sort_inventory(game, state)
    # Cheat gives all items; play assemble line immediately (does not use add_items).
    _emit_soul_core_voice()
    state.setdefault("seenRooms", {})
    for rid in game["rooms"].keys():
        state["seenRooms"][rid] = True
    log.add(
        "L.I.N.D.A. DEBUG: God mode. No real death, lantern full, whole kit, map revealed.",
        "sys",
    )


def announce_victory_if_won(state: Dict[str, Any], log: LogLike) -> None:
    if not get_flag(state, "gameWon"):
        return
    if state.get("pendingVictoryPopup"):
        return
    state["pendingVictoryPopup"] = True


def action_cost(kind: str) -> int:
    if kind in {"inventory", "system", "look"}:
        return 0
    return 1


def apply_object_interaction_cost(game: Dict[str, Any], state: Dict[str, Any], log: LogLike, cmd: str) -> None:
    """Spend plasma for hotspot/object interactions; LOOK and WHISTLE do not drain the orb."""
    apply_action(game, state, "look" if cmd in {"look", "whistle"} else "interact", log)


def die(game: Dict[str, Any], state: Dict[str, Any], log: LogLike, text: str) -> None:
    if not state["alive"]:
        return
    if state.get("godMode"):
        log.add(text, "dead")
        log.add("(God mode ... you're still here. That was for show.)", "sys")
        return
    state["alive"] = False
    log.add(text, "dead")
    log.add("YOU HAVE DIED. (Save early. Save often. Shadowgate would.)", "dead")


def apply_action(game: Dict[str, Any], state: Dict[str, Any], kind: str, log: LogLike) -> None:
    cost = action_cost(kind)
    if cost <= 0:
        return
    if state.get("godMode"):
        return
    state["actions"] += cost
    ap = int(game["meta"]["actionsPerLantern"])
    state["plasma"] = int(state.get("plasma", ap)) - cost
    if kind == "charge_plasma":
        # Charging consumes time but refills the orb immediately afterward.
        state["plasma"] = ap
    if int(state.get("plasma", 0)) <= 0:
        state["plasma"] = 0
        die(game, state, log, game["deaths"]["darkness"])


def sort_inventory(game: Dict[str, Any], state: Dict[str, Any]) -> None:
    """Alphabetical by display name, then item id."""
    inv = state.get("inventory")
    if not inv:
        return
    inv.sort(key=lambda iid: (item_def(game, iid)["name"].lower(), iid.lower()))


def _emit_soul_core_voice() -> None:
    """Play the assemble Soul-Core voice line if mixer/file are available."""
    try:
        import pygame
        from doomgate.util.paths import resource_path

        global _soul_core_voice_sound
        p = resource_path("assets", "sfx", "assemble_soul_core_breaker.wav")
        if not os.path.isfile(p):
            return
        if pygame.mixer.get_init() is None:
            return
        if _soul_core_voice_sound is None:
            _soul_core_voice_sound = pygame.mixer.Sound(p)
        _soul_core_voice_sound.play()
    except Exception:
        pass


def _maybe_play_soul_core_voice(state: Dict[str, Any], have_before: int, have_after: int) -> None:
    if get_flag(state, _SOUL_CORE_VOICE_FLAG):
        return
    if have_before >= len(_SOUL_CORE_PIECES) or have_after < len(_SOUL_CORE_PIECES):
        return
    set_flag(state, _SOUL_CORE_VOICE_FLAG, True)
    _emit_soul_core_voice()


def add_items(game: Dict[str, Any], state: Dict[str, Any], items: List[str]) -> None:
    have_before = sum(1 for it in _SOUL_CORE_PIECES if it in state.get("inventory", []))
    for it in items:
        if it not in state["inventory"]:
            state["inventory"].append(it)
    sort_inventory(game, state)
    have_after = sum(1 for it in _SOUL_CORE_PIECES if it in state.get("inventory", []))
    _maybe_play_soul_core_voice(state, have_before, have_after)


def remove_items(state: Dict[str, Any], items: List[str]) -> None:
    for it in items:
        if it in state["inventory"]:
            state["inventory"].remove(it)
        if state["heldItemId"] == it:
            state["heldItemId"] = None


def assemble_soul_core_breaker(
    game: Dict[str, Any],
    state: Dict[str, Any],
    log: LogLike,
    acquired: Optional[List[str]] = None,
) -> None:
    if not has_item(state, "soulCoreFrame"):
        log.add("You don't have the frame. Assembling nothing is a bold new engineering discipline.", "warn")
        apply_action(game, state, "interact", log)
        return
    ok = get_flag(state, "framePowered") and get_flag(state, "frameLinked") and get_flag(state, "frameKeyed")
    if not ok:
        log.add("The frame refuses to complete. It needs power (Omega Crystal), a mind (Neural Link), and a key (Serpentine Key).", "warn")
        apply_action(game, state, "interact", log)
        return
    if has_item(state, "soulCoreBreaker"):
        log.add("The Soul-Core Breaker is already assembled. Please stop petting it.", "dim")
        apply_action(game, state, "interact", log)
        return
    log.add("The frame locks, hums, and then clicks into something final. You have built a weapon that would make a priest faint and an engineer cry.", "sys")
    remove_items(state, ["soulCoreFrame"])
    if acquired is not None:
        acquired.append("soulCoreBreaker")
    add_items(game, state, ["soulCoreBreaker"])
    state["heldItemId"] = "soulCoreBreaker"
    apply_action(game, state, "interact", log)


def try_combination(
    game: Dict[str, Any],
    state: Dict[str, Any],
    log: LogLike,
    a: str,
    b: str,
    acquired: Optional[List[str]] = None,
) -> bool:
    x, y = (a, b) if a <= b else (b, a)
    for c in game["combinations"]:
        ca, cb = (c["a"], c["b"]) if c["a"] <= c["b"] else (c["b"], c["a"])
        if ca == x and cb == y:
            if c.get("special") == "assembleSoulCoreBreaker":
                assemble_soul_core_breaker(game, state, log, acquired=acquired)
                return True
            if c.get("text"):
                log.add(c["text"])
            res = c.get("result", {})
            if "add" in res:
                for gid in res["add"]:
                    if gid not in state["inventory"] and acquired is not None:
                        acquired.append(gid)
                add_items(game, state, res["add"])
            if "remove" in res:
                remove_items(state, res["remove"])
            if "setFlag" in res:
                set_flag(state, res["setFlag"], True)
            apply_action(game, state, "interact", log)
            return True
    return False


def can_exit(state: Dict[str, Any], room: Dict[str, Any], direction: str) -> bool:
    rules = room.get("rules", {})
    if direction == "north" and rules.get("gateToNorthRequiresFlag"):
        return get_flag(state, rules["gateToNorthRequiresFlag"])
    return True


def move(game: Dict[str, Any], state: Dict[str, Any], log: LogLike, direction: str) -> None:
    room = room_def(game, state["roomId"])
    target = room.get("exits", {}).get(direction)
    if not target:
        log.add("You can't go that way. The facility refuses your suggestion.", "warn")
        apply_action(game, state, "interact", log)
        return
    if not can_exit(state, room, direction):
        log.add("The way is blocked. Some lock ... technical or infernal ... still holds.", "warn")
        apply_action(game, state, "interact", log)
        return
    first_time = not state.get("roomIntroShown", {}).get(target, False)
    state["roomId"] = target
    state["seenRooms"][target] = True
    if "roomIntroShown" not in state or not isinstance(state["roomIntroShown"], dict):
        state["roomIntroShown"] = {}
    state["roomIntroShown"][target] = True
    apply_action(game, state, "move", log)
    log.add(f">> {room_def(game, target)['name']}", "dim")
    log.add(room_def(game, target)["desc"])
    if first_time:
        enter_text = room_def(game, target).get("enterText")
        if enter_text:
            state["pendingRoomPopup"] = target


def _next_whistle_line(game: Dict[str, Any], state: Dict[str, Any]) -> str:
    lines = game.get("whistleLines")
    if not isinstance(lines, list) or not lines:
        return "You whistle. The Crucible withholds applause."
    flags = state.setdefault("flags", {})
    i = int(flags.get("_whistle_i", 0))
    flags["_whistle_i"] = i + 1
    return str(lines[i % len(lines)])


def resolve_object_action(
    game: Dict[str, Any],
    state: Dict[str, Any],
    log: LogLike,
    obj_id: str,
    cmd: str,
    hotspot_kind: str,
    acquired: Optional[List[str]] = None,
) -> None:
    room = room_def(game, state["roomId"])
    obj = room.get("objects", {}).get(obj_id)
    if not obj:
        if hotspot_kind == "hazard":
            die(game, state, log, game["deaths"]["slime"])
            return
        if cmd == "whistle":
            log.add(_next_whistle_line(game, state), "dim")
            return
        log.add("There's nothing meaningful there. Only ambience and liability.", "warn")
        apply_object_interaction_cost(game, state, log, cmd)
        return

    if get_flag(state, "gameWon"):
        if cmd == "whistle":
            log.add(_next_whistle_line(game, state), "dim")
            return
        log.add("The rift is sealed. What remains is cleanup and therapy. Mostly therapy.", "dim")
        apply_object_interaction_cost(game, state, log, cmd)
        return

    handler = obj.get(cmd)
    if handler is None:
        if hotspot_kind == "hazard":
            die(game, state, log, game["deaths"]["slime"])
            return
        if cmd == "whistle":
            log.add(_next_whistle_line(game, state), "dim")
            return
        log.add("That accomplishes nothing. The facility remains unimpressed.", "warn")
        apply_object_interaction_cost(game, state, log, cmd)
        return

    if isinstance(handler, str):
        log.add(handler)
        apply_object_interaction_cost(game, state, log, cmd)
        return

    if isinstance(handler, dict) and handler.get("special") == "lindaTerminal":
        state["pendingLindaTerminal"] = True
        apply_object_interaction_cost(game, state, log, cmd)
        return

    if isinstance(handler, dict) and handler.get("special") == "cycleText":
        lines = handler.get("lines")
        if not isinstance(lines, list) or not lines:
            log.add("Static. Whatever answer you wanted isn't on this channel.", "dim")
            apply_object_interaction_cost(game, state, log, cmd)
            return
        flag_key = str(handler.get("flag") or f"cycle_{state.get('roomId','')}_{obj_id}_{cmd}")
        i = int(state.get("flags", {}).get(flag_key, 0))
        text = str(lines[i % len(lines)])
        log.add(text)
        state.setdefault("flags", {})[flag_key] = i + 1
        apply_object_interaction_cost(game, state, log, cmd)
        return

    # Death handler (skip when an option list handles branching — e.g. hatch pry vs. pass through)
    if handler.get("death") and not handler.get("options"):
        if handler.get("text"):
            log.add(handler["text"])
        die(game, state, log, game["deaths"].get(handler["death"], "You die in a way that is educational to everyone except you."))
        return

    held = state.get("heldItemId")

    # Option list handler (enemy puzzle)
    if cmd == "use" and handler.get("options"):
        for opt in handler["options"]:
            if opt.get("requiresItem") and held != opt["requiresItem"]:
                continue
            if opt.get("requiresFlag") and not get_flag(state, opt["requiresFlag"]):
                continue
            if opt.get("onceFlag") and get_flag(state, opt["onceFlag"]):
                continue
            if opt.get("text"):
                log.add(opt["text"])
            td = opt.get("travelDir")
            if td:
                move(game, state, log, str(td))
                announce_victory_if_won(state, log)
                return
            if opt.get("setFlag"):
                set_flag(state, opt["setFlag"], True)
            if opt.get("onceFlag"):
                set_flag(state, opt["onceFlag"], True)
            apply_object_interaction_cost(game, state, log, cmd)
            announce_victory_if_won(state, log)
            return
        d = handler.get("default")
        if d:
            if d.get("text"):
                log.add(d["text"])
            if d.get("death"):
                die(game, state, log, game["deaths"].get(d["death"], "You die."))
            else:
                apply_object_interaction_cost(game, state, log, cmd)
            return

    # Requirements
    if handler.get("requiresItem") and held != handler["requiresItem"]:
        log.add("That doesn't work. You might need a specific item.", "warn")
        apply_object_interaction_cost(game, state, log, cmd)
        return
    if handler.get("requiresFlag") and not get_flag(state, handler["requiresFlag"]):
        if cmd == "take" and (handler.get("takeFailText") or handler.get("takeFailDeath")):
            if handler.get("takeFailText"):
                log.add(handler["takeFailText"])
            if handler.get("takeFailDeath"):
                die(game, state, log, game["deaths"].get(handler["takeFailDeath"], "You die."))
            else:
                apply_object_interaction_cost(game, state, log, cmd)
            return
        log.add("Something else must happen first.", "warn")
        apply_object_interaction_cost(game, state, log, cmd)
        return
    if handler.get("onceFlag") and get_flag(state, handler["onceFlag"]):
        log.add("You've already done that. Repetition is a hobby, not a solution.", "dim")
        apply_object_interaction_cost(game, state, log, cmd)
        return

    if handler.get("text"):
        log.add(handler["text"])

    if handler.get("onceFlag"):
        set_flag(state, handler["onceFlag"], True)
    if handler.get("setFlag"):
        set_flag(state, handler["setFlag"], True)

    if handler.get("gain"):
        for gid in handler["gain"]:
            if gid not in state["inventory"] and acquired is not None:
                acquired.append(gid)
        add_items(game, state, handler["gain"])

    add_lan = handler.get("addLanterns")
    if add_lan:
        mx = int(game["meta"]["lanternMaxCarry"])
        cur = int(state.get("lanterns", 0))
        nl = min(mx, cur + int(add_lan))
        if nl > cur:
            state["lanterns"] = nl
        else:
            log.add("You can't carry any more Plasma Charger packs.", "warn")

    if handler.get("consumeHeld") and held:
        remove_items(state, [held])

    apply_object_interaction_cost(game, state, log, cmd)
    announce_victory_if_won(state, log)

