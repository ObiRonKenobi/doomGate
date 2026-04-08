from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol


class LogLike(Protocol):
    def add(self, text: str, kind: str = "line") -> None: ...


def clamp_int(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, int(v)))


def default_state(game: Dict[str, Any]) -> Dict[str, Any]:
    n0 = int(game["meta"]["startLanterns"])
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
        "lanternCount": n0,
        "lanterns": n0,
        "alive": True,
        "godMode": False,
        "hotspotDebugUnlocked": False,
    }


def merge_loaded_save(game: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
    """Merge a JSON-loaded dict onto defaults and normalize lantern fields."""
    base = default_state(game)
    base.update(loaded)
    base.setdefault("flags", {})
    base.setdefault("seenRooms", {})
    base.setdefault("roomIntroShown", {})
    base.setdefault("pendingRoomPopup", None)
    base.setdefault("pendingVictoryPopup", False)
    base.setdefault("pendingLindaTerminal", False)
    base.setdefault("lindaWrongCount", 0)
    base.setdefault("godMode", False)
    base.setdefault("hotspotDebugUnlocked", False)
    base.setdefault("inventory", [])
    ap_m = int(game["meta"]["actionsPerLantern"])
    sp_m = int(base.get("actions", 0)) // ap_m
    mx = int(game["meta"]["lanternMaxCarry"])
    if "lanternCount" not in base or base.get("lanternCount") is None:
        base["lanternCount"] = clamp_int(
            int(base.get("lanterns", game["meta"]["startLanterns"])) + sp_m,
            1,
            mx,
        )
    base["lanternCount"] = clamp_int(int(base["lanternCount"]), 1, mx)
    lc_m = int(base["lanternCount"])
    if sp_m >= lc_m:
        base["lanterns"] = 0
    else:
        base["lanterns"] = lc_m - sp_m
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
    state["lanternCount"] = mx
    state["actions"] = int(game["meta"]["startActions"])
    state["lanterns"] = mx
    for iid in game["items"].keys():
        if iid not in state["inventory"]:
            state["inventory"].append(iid)
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
    if kind in {"inventory", "system"}:
        return 0
    return 1


def die(game: Dict[str, Any], state: Dict[str, Any], log: LogLike, text: str) -> None:
    if not state["alive"]:
        return
    if state.get("godMode"):
        log.add(text, "dead")
        log.add("(God mode — you're still here. That was for show.)", "sys")
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
    ap = game["meta"]["actionsPerLantern"]
    spent = state["actions"] // ap
    lc = int(state.get("lanternCount", game["meta"]["startLanterns"]))
    if spent >= lc:
        state["lanterns"] = 0
        die(game, state, log, game["deaths"]["darkness"])
    else:
        state["lanterns"] = lc - spent


def add_items(state: Dict[str, Any], items: List[str]) -> None:
    for it in items:
        if it not in state["inventory"]:
            state["inventory"].append(it)


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
    add_items(state, ["soulCoreBreaker"])
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
                add_items(state, res["add"])
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
        log.add("The way is blocked. Some lock—technical or infernal—still holds.", "warn")
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
        log.add("There's nothing meaningful there. Only ambience and liability.", "warn")
        apply_action(game, state, "interact", log)
        return

    if get_flag(state, "gameWon"):
        log.add("The rift is sealed. What remains is cleanup and therapy. Mostly therapy.", "dim")
        apply_action(game, state, "interact", log)
        return

    handler = obj.get(cmd)
    if handler is None:
        if hotspot_kind == "hazard":
            die(game, state, log, game["deaths"]["slime"])
            return
        log.add("That accomplishes nothing. The facility remains unimpressed.", "warn")
        apply_action(game, state, "interact", log)
        return

    if isinstance(handler, str):
        log.add(handler)
        apply_action(game, state, "interact", log)
        return

    if isinstance(handler, dict) and handler.get("special") == "lindaTerminal":
        state["pendingLindaTerminal"] = True
        apply_action(game, state, "interact", log)
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
            apply_action(game, state, "interact", log)
            announce_victory_if_won(state, log)
            return
        d = handler.get("default")
        if d:
            if d.get("text"):
                log.add(d["text"])
            if d.get("death"):
                die(game, state, log, game["deaths"].get(d["death"], "You die."))
            else:
                apply_action(game, state, "interact", log)
            return

    # Requirements
    if handler.get("requiresItem") and held != handler["requiresItem"]:
        log.add("That doesn't work. You might need a specific item.", "warn")
        apply_action(game, state, "interact", log)
        return
    if handler.get("requiresFlag") and not get_flag(state, handler["requiresFlag"]):
        if cmd == "take" and (handler.get("takeFailText") or handler.get("takeFailDeath")):
            if handler.get("takeFailText"):
                log.add(handler["takeFailText"])
            if handler.get("takeFailDeath"):
                die(game, state, log, game["deaths"].get(handler["takeFailDeath"], "You die."))
            else:
                apply_action(game, state, "interact", log)
            return
        log.add("Something else must happen first.", "warn")
        apply_action(game, state, "interact", log)
        return
    if handler.get("onceFlag") and get_flag(state, handler["onceFlag"]):
        log.add("You've already done that. Repetition is a hobby, not a solution.", "dim")
        apply_action(game, state, "interact", log)
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
        add_items(state, handler["gain"])

    add_lan = handler.get("addLanterns")
    if add_lan:
        mx = int(game["meta"]["lanternMaxCarry"])
        lc0 = int(state.get("lanternCount", game["meta"]["startLanterns"]))
        state["lanternCount"] = lc0
        nl = min(mx, lc0 + int(add_lan))
        if nl > lc0:
            state["lanternCount"] = nl
            ap = game["meta"]["actionsPerLantern"]
            sp = state["actions"] // ap
            state["lanterns"] = max(0, nl - sp)
        else:
            log.add("You can't carry any more Plasma Lantern charges.", "warn")

    if handler.get("consumeHeld") and held:
        remove_items(state, [held])

    apply_action(game, state, "interact", log)
    announce_victory_if_won(state, log)

