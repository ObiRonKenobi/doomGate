import json
import math
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import pygame


# -----------------------------
# Core data (rooms still defined below for now)
# -----------------------------
from doomgate.data.game_core import make_game_core
from doomgate.game import merge_loaded_save

GAME: Dict[str, Any] = make_game_core()


def rect_from_pct(x: float, y: float, w: float, h: float, parent: pygame.Rect) -> pygame.Rect:
    # Backwards-compatible shim; moved to doomgate.ui.hotspots.
    from doomgate.ui.hotspots import rect_from_pct as _r

    return _r(x, y, w, h, parent)


def screen_rect_to_pct(r: pygame.Rect, parent: pygame.Rect) -> Tuple[float, float, float, float]:
    # Backwards-compatible shim; moved to doomgate.ui.hotspots.
    from doomgate.ui.hotspots import screen_rect_to_pct as _s

    return _s(r, parent)


def clamp_hotspot_pct_rect(l: float, t: float, w: float, h: float) -> Tuple[float, float, float, float]:
    # Backwards-compatible shim; moved to doomgate.ui.hotspots.
    from doomgate.ui.hotspots import clamp_hotspot_pct_rect as _c

    return _c(l, t, w, h)


HS_DEBUG_HANDLE_PX = 12
HS_DEBUG_EDGE_PX = 6
UI_DEBUG_HANDLE_PX = 12
UI_DEBUG_EDGE_PX = 6
HOTSPOT_LAYOUT_FILE = "hotspot_layout.json"
# When False, F3 hotspot overlay only if state["hotspotDebugUnlocked"] (set from Linda terminal later).
HOTSPOT_DEBUG_F3_FOR_EVERYONE = True


def hotspot_layout_path() -> str:
    # Backwards-compatible shim; moved to doomgate.ui.hotspots.
    from doomgate.ui.hotspots import hotspot_layout_path as _p

    return _p()


def room_map_floor(room: Dict[str, Any]) -> int:
    """Plasma-deck = 0, dig / antechamber basement = -1, hell-gate summit = +1."""
    return int(room.get("mapFloor", 0))


def apply_hotspot_layout_overrides(game: Dict[str, Any]) -> None:
    # Backwards-compatible shim; moved to doomgate.ui.hotspots.
    from doomgate.ui.hotspots import apply_hotspot_layout_overrides as _a

    _a(game)


def save_hotspot_layout_to_disk(game: Dict[str, Any]) -> Tuple[bool, str]:
    # Backwards-compatible shim; moved to doomgate.ui.hotspots.
    from doomgate.ui.hotspots import save_hotspot_layout_to_disk as _s

    return _s(game)


UI_LAYOUT_FILE = "ui_layout.json"
UI_LAYOUT_DEBUG_F5_FOR_EVERYONE = True


def ui_layout_path() -> str:
    # Backwards-compatible shim; moved to doomgate.ui.layout.
    from doomgate.ui.layout import ui_layout_path as _p

    return _p()


def default_ui_layout_overrides() -> Dict[str, Any]:
    # Backwards-compatible shim; moved to doomgate.ui.layout.
    from doomgate.ui.layout import default_ui_layout_overrides as _d

    return _d()


def load_ui_layout_overrides() -> Dict[str, Any]:
    # Backwards-compatible shim; moved to doomgate.ui.layout.
    from doomgate.ui.layout import load_ui_layout_overrides as _l

    return _l()


def save_ui_layout_overrides(ov: Dict[str, Any]) -> Tuple[bool, str]:
    # Backwards-compatible shim; moved to doomgate.ui.layout.
    from doomgate.ui.layout import save_ui_layout_overrides as _s

    return _s(ov)


def _apply_legacy_map_held_overrides(lay: Dict[str, Any], ov: Dict[str, Any]) -> None:
    # Backwards-compatible shim; moved to doomgate.ui.layout.
    from doomgate.ui.layout import _apply_legacy_map_held_overrides as _a

    _a(lay, ov)


def apply_ui_layout_overrides(lay: Dict[str, Any], ov: Optional[Dict[str, Any]]) -> None:
    # Backwards-compatible shim; moved to doomgate.ui.layout.
    from doomgate.ui.layout import apply_ui_layout_overrides as _a

    _a(lay, ov, GAME["commands"])


def sync_ui_layout_overrides_from_lay(lay: Dict[str, Any], ov: Dict[str, Any]) -> None:
    # Backwards-compatible shim; moved to doomgate.ui.layout.
    from doomgate.ui.layout import sync_ui_layout_overrides_from_lay as _s

    _s(lay, ov)


AUDIO_SETTINGS_FILE = "audio_settings.json"


def audio_settings_path() -> str:
    # Backwards-compatible shim; moved to doomgate.audio.
    from doomgate.audio import audio_settings_path as _p

    return _p()


def load_audio_settings() -> Dict[str, Any]:
    # Backwards-compatible shim; moved to doomgate.audio.
    from doomgate.audio import load_audio_settings as _load

    return _load()


def save_audio_settings(settings: Dict[str, Any]) -> None:
    # Backwards-compatible shim; moved to doomgate.audio.
    from doomgate.audio import save_audio_settings as _save

    _save(settings)


MUSIC_VOL_HOVER_DELAY_MS = 1000


def music_vol_popup_rect(music_btn: pygame.Rect, lay: Dict[str, Any]) -> pygame.Rect:
    # Backwards-compatible shim; moved to doomgate.audio.
    from doomgate.audio import music_vol_popup_rect as _r

    return _r(music_btn, lay, clamp)


def music_vol_track_inner(popup: pygame.Rect) -> pygame.Rect:
    # Backwards-compatible shim; moved to doomgate.audio.
    from doomgate.audio import music_vol_track_inner as _t

    return _t(popup)


def music_volume_from_track_x(track: pygame.Rect, x: float) -> float:
    # Backwards-compatible shim; moved to doomgate.audio.
    from doomgate.audio import music_volume_from_track_x as _v

    return _v(track, x)


def draw_music_volume_popup(
    screen: pygame.Surface,
    popup: pygame.Rect,
    volume: float,
    colors: Dict[str, Any],
    font: pygame.font.Font,
) -> None:
    # Backwards-compatible shim; moved to doomgate.audio.
    from doomgate.audio import draw_music_volume_popup as _draw

    _draw(screen, popup, volume, colors, font, clamp)


_ROOMS_LEGACY = None
"""
Legacy rooms dict (kept for reference during refactor).
Rooms now live in `doomgate/data/rooms.py`.

_ROOMS_LEGACY = {
    "hangar": {
        "id": "hangar",
        "name": "Hangar Intake — The Crucible Facility",
        "theme": "hangar",
        "mapPos": [0, 2],
        "mapFloor": 0,
        "enterText": "You came to Crucible Facility for one reason: Crux.\n\nYour handler said the director was running \"energy research.\" Then the distress beacon went silent, the comms filled with screaming, and the UAC stopped answering.\n\nSomewhere inside is what Crux stole from the dig site—an argent core wrapped in old runes. If you can find it, you can shut this place down. If you can't… Mars gets a new mouth.",
        "desc": "You stand in the hangar intake of the Crucible Facility. UAC steel ribs arch overhead, but the walls are scored with runes that look like they were etched by a knife made of screaming.\n\nA flickering terminal repeats a single line: \"L.I.N.D.A. ONLINE\".\nThe air smells of ozone, blood, and corporate denial.",
        "exits": {"north": "corridor", "east": "security"},
        "hotspots": [
            {"id": "toCorridor", "name": "North Door", "rect": {"l": 44, "t": 18, "w": 16, "h": 24}, "kind": "exit", "data": {"dir": "north"}},
            {"id": "toSecurity", "name": "Security Door", "rect": {"l": 78, "t": 30, "w": 18, "h": 26}, "kind": "exit", "data": {"dir": "east"}},
            {"id": "terminal", "name": "Flickering Terminal", "rect": {"l": 18, "t": 38, "w": 18, "h": 18}, "kind": "object"},
            {"id": "lanternCrate", "name": "UAC Supply Crate", "rect": {"l": 34, "t": 62, "w": 20, "h": 18}, "kind": "container"},
        ],
        "objects": {
            "terminal": {
                "look": "The terminal's text jitters. A voice crawls out of the static: \"Marine. If you're reading this, your squad isn't. Director Crux is in the lower temple. You need the Soul-Core Breaker. Three artifacts. Don't be brave—be correct.\"",
                "talk": "You speak into the mic. The response is immediate.\n\n\"Designation: L.I.N.D.A. Logistical Inference and Neutralization Directive AI. I am... compromised. But helpful. Probably.\"",
                "use": {"special": "lindaTerminal"},
            },
            "lanternCrate": {
                "look": "A dented supply crate with a UAC latch. Something inside hums politely.",
                "open": {
                    "onceFlag": "openedCrate",
                    "gain": ["stimpack"],
                    "addLanterns": 1,
                    "text": "You pop the latch. Inside: a spare Plasma Lantern charge and a Stimpack. The cell clamps to your harness; UAC still believes in benefits packages.",
                },
                "take": {"death": "crateTakeDeath", "text": "You try to take the entire crate. Your back files a formal complaint and resigns."},
            },
        },
    },
    "corridor": {
        "id": "corridor",
        "name": "Main Corridor — Steel & Sigils",
        "theme": "corridor",
        "mapPos": [1, 2],
        "mapFloor": 0,
        "enterText": "The facility’s spine is still lit, still humming—like the building refuses to admit it’s dead.\n\nGlyphs crawl over UAC logos in patient, obscene handwriting. This wasn’t an invasion. It was an invitation that got accepted.\n\nL.I.N.D.A. said Crux went down. That means the artifacts went down too. Keep moving.",
        "desc": "A long corridor of brushed metal and bad decisions. Emergency lights pulse red. Demonic glyphs crawl over the UAC logos as if mocking the concept of branding.\n\nTo the north, a blast door leads to the Research Labs. To the east, the Living Quarters stink of old fear.",
        "exits": {"south": "hangar", "north": "labsDoor", "east": "quarters"},
        "hotspots": [
            {"id": "toHangar", "name": "Hangar Door", "rect": {"l": 10, "t": 30, "w": 18, "h": 30}, "kind": "exit", "data": {"dir": "south"}},
            {"id": "toLabs", "name": "Blast Door", "rect": {"l": 44, "t": 16, "w": 18, "h": 28}, "kind": "exit", "data": {"dir": "north"}},
            {"id": "toQuarters", "name": "Quarters Hall", "rect": {"l": 76, "t": 34, "w": 18, "h": 26}, "kind": "exit", "data": {"dir": "east"}},
            {"id": "ooze", "name": "Glowing Ooze Pool", "rect": {"l": 42, "t": 76, "w": 20, "h": 12}, "kind": "hazard"},
        ],
        "objects": {
            "ooze": {
                "look": "A pool of luminous green sludge bubbles softly. It looks like coolant. It smells like lies.",
                "take": {"death": "slime"},
                "use": {"death": "slime"},
                "open": {"death": "slime"},
                "talk": {"death": "slime"},
                "close": {"death": "slime"},
            }
        },
    },
    "security": {
        "id": "security",
        "name": "Security Checkpoint — Locked Teeth",
        "theme": "security",
        "mapPos": [0, 3],
        "mapFloor": 0,
        "enterText": "The checkpoint tells its own story: panic, protocol, and then something stronger than both.\n\nSomeone tried to hold the line here. Someone failed. Whatever got in didn't need a keycard.",
        "desc": "A security checkpoint with overturned chairs and a shattered glass window. The keypad panel is smeared with something that used to have hopes.\n\nA side passage leads deeper into maintenance.",
        "exits": {"west": "hangar", "east": "maintenance", "north": "armory"},
        "hotspots": [
            {"id": "toHangar", "name": "Hangar Door", "rect": {"l": 10, "t": 34, "w": 18, "h": 28}, "kind": "exit", "data": {"dir": "west"}},
            {"id": "toMaint", "name": "Maintenance Passage", "rect": {"l": 76, "t": 38, "w": 18, "h": 26}, "kind": "exit", "data": {"dir": "east"}},
            {"id": "toArmory", "name": "Armory Door", "rect": {"l": 46, "t": 18, "w": 18, "h": 30}, "kind": "exit", "data": {"dir": "north"}},
            {"id": "corpse", "name": "Security Corpse", "rect": {"l": 60, "t": 70, "w": 18, "h": 16}, "kind": "object"},
        ],
        "objects": {
            "corpse": {
                "look": "A security officer lies face-down, still clutching a keycard like it's a favorite regret.",
                "take": {"onceFlag": "tookRedKey", "gain": ["redKeycard"], "text": "You pry the Red Access Keycard loose. The officer doesn't object. He seems busy."},
            },
        },
    },
    "maintenance": {
        "id": "maintenance",
        "name": "Maintenance Ductworks — The Belly of UAC",
        "theme": "maintenance",
        "mapPos": [1, 3],
        "mapFloor": 0,
        "enterText": "The walls sweat. The pipes hiss like they’re trying to warn you without lungs.\n\nSomething moved through here in a hurry—drag marks, scorched handprints, and the sour bite of argent where it shouldn’t be. This is where the facility started bleeding.\n\nIf Crux sealed the excavation hatch, it’s because he didn’t want anyone going down. Or coming up.",
        "desc": "Pipes. Steam. The sound of something large breathing where no lungs should be. A broken panel reveals a power conduit pulsing with argent.\n\nA sealed hatch to the north is marked: EXCAVATION.",
        "exits": {"west": "security", "north": "excavationHatch"},
        "hotspots": [
            {"id": "toSec", "name": "Checkpoint Door", "rect": {"l": 10, "t": 38, "w": 18, "h": 26}, "kind": "exit", "data": {"dir": "west"}},
            {"id": "toExc", "name": "Excavation Hatch", "rect": {"l": 44, "t": 18, "w": 18, "h": 28}, "kind": "exit", "data": {"dir": "north"}},
            {"id": "conduit", "name": "Argent Conduit", "rect": {"l": 66, "t": 50, "w": 18, "h": 26}, "kind": "object"},
        ],
        "objects": {
            "conduit": {
                "look": "A power conduit throbs with contained hell-light. A cell socket is half-melted, as if something was removed in a hurry.",
                "take": {"onceFlag": "tookCell", "gain": ["plasmaCell"], "text": "You yank a BFG Power Cell from the conduit. The lights dim, and the facility seems to glare at you."},
                "use": {"death": "conduitFry", "text": "You jam your fingers into the conduit. The conduit teaches you about electricity in a very hands-on way."},
            }
        },
    },
    "labsDoor": {
        "id": "labsDoor",
        "name": "Research Labs — Blast Door",
        "theme": "labsDoor",
        "mapPos": [2, 2],
        "mapFloor": 0,
        "enterText": "The labs are sealed behind a blast door like the building is trying to quarantine its own curiosity.\n\nThe blood-seal on the keypad isn’t just vandalism. It’s a prayer written by someone who knew the right symbols—and didn’t care who answered.\n\nCrux loved locked doors. He loved what was behind them more.",
        "desc": "A blast door blocks the Research Labs. A demonic seal has been painted over the keypad, like graffiti but with consequences.\n\nThe seal looks... unfinished.",
        "exits": {"south": "corridor", "north": "labs"},
        "rules": {"gateToNorthRequiresFlag": "brokeSeal"},
        "hotspots": [
            {"id": "toCorr", "name": "Corridor", "rect": {"l": 10, "t": 34, "w": 18, "h": 28}, "kind": "exit", "data": {"dir": "south"}},
            {
                "id": "toLabs",
                "name": "Into the Labs",
                "rect": {"l": 44, "t": 16, "w": 18, "h": 28},
                "kind": "exit",
                "data": {"dir": "north"},
            },
            {"id": "seal", "name": "Blood Seal", "rect": {"l": 50, "t": 54, "w": 14, "h": 16}, "kind": "object"},
        ],
        "objects": {
            "seal": {
                "look": "A blood-painted seal mixed with circuitry diagrams. Crux always did love cross-discipline collaboration.",
                "use": {"requiresItem": "stimpack", "onceFlag": "brokeSeal", "consumeHeld": True, "text": "You crack the Stimpack's seal and let a few drops spatter the glyph. The blood sizzles. The demonic paint flakes away like cheap nail polish."},
                "take": {"death": "sealFlays", "text": "You try to scrape the seal into your pocket. The seal tries to scrape you into the floor."},
            },
        },
    },
    "labs": {
        "id": "labs",
        "name": "Research Labs — Argent Containment",
        "theme": "labs",
        "mapPos": [3, 2],
        "mapFloor": 0,
        "enterText": "The labs smell like antiseptic and sulfur—cleanliness layered over corruption.\n\nContainment tubes are cracked from the inside. Not escaped. Hatched.\n\nIf Crux was chasing power, this is where he learned what power costs. The Omega Crystal is here somewhere. Don’t let it choose you.",
        "desc": "Benches of shattered glassware. Containment tubes cracked from the inside. The smell is antiseptic overlaid with sulfur—like a hospital built inside a volcano.\n\nA pedestal holds something bright. Too bright for this place.",
        "exits": {"south": "labsDoor", "east": "templeLift"},
        "hotspots": [
            {"id": "toDoor", "name": "Blast Door", "rect": {"l": 10, "t": 34, "w": 18, "h": 28}, "kind": "exit", "data": {"dir": "south"}},
            {"id": "toLift", "name": "Service Lift", "rect": {"l": 78, "t": 32, "w": 18, "h": 30}, "kind": "exit", "data": {"dir": "east"}},
            {"id": "crystal", "name": "Argent Pedestal", "rect": {"l": 48, "t": 54, "w": 14, "h": 20}, "kind": "object"},
        ],
        "objects": {
            "crystal": {
                "look": "A stable core of argent energy. It doesn't flicker. It waits.",
                "take": {"onceFlag": "tookCrystal", "gain": ["omegaCrystal"], "text": "You lift the Omega Crystal. It warms your armor like a pleased predator."},
                "use": {"death": "crystalFlash", "text": "You press your face close to the Crystal to 'study it.' Your visor fogs with doom."},
            }
        },
    },
    "quarters": {
        "id": "quarters",
        "name": "Living Quarters — Echoes of Payroll",
        "theme": "quarters",
        "mapPos": [2, 3],
        "mapFloor": 0,
        "enterText": "People tried to live here. That’s the worst part.\n\nBunks are stripped, lockers torn open, and the walls are scratched with the same looping symbol—over and over—like the facility was teaching them a new alphabet.\n\nSomebody hid the Soul-Core Breaker frame in here. They believed in a weapon. Or they believed in you.",
        "desc": "Bunks. Lockers. A poster about workplace safety that has been rewritten in blood. The intercom whispers static prayers.\n\nA cracked wall panel reveals a hidden recess.",
        "exits": {"west": "corridor", "east": "templeLift"},
        "hotspots": [
            {"id": "toCorr", "name": "Corridor", "rect": {"l": 10, "t": 34, "w": 18, "h": 28}, "kind": "exit", "data": {"dir": "west"}},
            {"id": "toLift", "name": "Service Lift", "rect": {"l": 78, "t": 32, "w": 18, "h": 30}, "kind": "exit", "data": {"dir": "east"}},
            {"id": "panel", "name": "Cracked Panel", "rect": {"l": 54, "t": 48, "w": 18, "h": 22}, "kind": "container"},
            {"id": "intercom", "name": "Intercom", "rect": {"l": 32, "t": 28, "w": 12, "h": 12}, "kind": "object"},
        ],
        "objects": {
            "intercom": {
                "look": "The intercom sputters a faint signal that doesn't belong to UAC.\n\n\"Marine,\" the voice says softly, \"Crux moved the Neural Link to Excavation. He likes to keep his toys near his tomb.\"",
                "talk": "\"I'm here,\" you say.\n\n\"Regrettably,\" the intercom replies.",
            },
            "panel": {
                "look": "A loose panel, pried open from inside. Someone hid something here with the urgency of a person who understood the concept of 'later.'",
                "open": {"onceFlag": "openedPanel", "gain": ["soulCoreFrame"], "text": "Behind the panel: the Soul-Core Breaker Frame. It feels heavier than its mass, like it contains a promise."},
            },
        },
    },
    "templeLift": {
        "id": "templeLift",
        "name": "Service Lift — Down to the Ruins",
        "theme": "lift",
        "mapPos": [3, 3],
        "mapFloor": 0,
        "enterText": "The lift is where the facility stops pretending it’s just steel.\n\nBone-white growths crawl over the frame, and the button panel has been reduced to a choice: up, or down.\n\nCrux went down. The artifacts went down. The ruin below predates Mars—and it’s awake enough to notice you.",
        "desc": "A freight lift fused with bone-white growths. The button panel has only two working lights: UP and DOWN. DOWN is lit like a dare.\n\nA voice crackles: \"The ruins predate Mars. Which is inconvenient for Mars.\"",
        "exits": {"west": "quarters", "east": "labs", "down": "excavation", "north": "hellGateAntechamber"},
        "hotspots": [
            {"id": "toQuarters", "name": "Quarters", "rect": {"l": 10, "t": 34, "w": 18, "h": 28}, "kind": "exit", "data": {"dir": "west"}},
            {"id": "toLabs", "name": "Labs", "rect": {"l": 78, "t": 34, "w": 18, "h": 28}, "kind": "exit", "data": {"dir": "east"}},
            {"id": "down", "name": "DOWN Button", "rect": {"l": 46, "t": 58, "w": 12, "h": 12}, "kind": "exit", "data": {"dir": "down"}},
            {"id": "north", "name": "North Gate", "rect": {"l": 44, "t": 18, "w": 18, "h": 30}, "kind": "exit", "data": {"dir": "north"}},
        ],
    },
    "excavationHatch": {
        "id": "excavationHatch",
        "name": "Excavation Hatch — Sealed",
        "theme": "hatch",
        "mapPos": [2, 4],
        "mapFloor": -1,
        "enterText": "The hatch is a boundary line—someone’s last attempt to draw “outside” and “inside” with a piece of steel.\n\nClaw marks gouge the frame from below. Whatever wanted out was strong. Whatever kept it in was desperate.\n\nIf you open this, you are choosing a direction for the whole story.",
        "desc": "A heavy hatch marked EXCAVATION. Claw marks score the frame from the inside.\n\nA biometric lock blinks an angry red.",
        "exits": {"south": "maintenance", "north": "excavation"},
        "rules": {"gateToNorthRequiresFlag": "openedHatch"},
        "hotspots": [
            {"id": "toMaint", "name": "Maintenance", "rect": {"l": 10, "t": 34, "w": 18, "h": 28}, "kind": "exit", "data": {"dir": "south"}},
            {"id": "hatch", "name": "Excavation Hatch", "rect": {"l": 46, "t": 18, "w": 18, "h": 30}, "kind": "barrier"},
        ],
        "objects": {
            "hatch": {
                "look": "The lock demands clearance that is, statistically speaking, dead.",
                "open": {"requiresItem": "redKeycard", "onceFlag": "openedHatch", "text": "You swipe the Red Keycard. The hatch unlatches with a thunk that sounds like a coffin approving your paperwork."},
                "use": {
                    "options": [
                        {
                            "requiresFlag": "openedHatch",
                            "text": "You duck through the hatch into the excavation shaft.",
                            "travelDir": "north",
                        }
                    ],
                    "default": {
                        "death": "hatchPryDeath",
                        "text": "You try to pry it open with your hands. The hatch remains employed. You do not.",
                    },
                },
            }
        },
    },
    "excavation": {
        "id": "excavation",
        "name": "Excavation Site — Temple Breach",
        "theme": "excavation",
        "mapPos": [3, 4],
        "mapFloor": -1,
        "enterText": "The dig site is where UAC broke the world on purpose.\n\nFloodlights glare into a wound cut through ancient stone. The air tastes like dust and ritual.\n\nSomewhere down here is the Neural Link—an AI core that shouldn’t exist, too clean to be old and too old to be clean. Crux kept it close. Like a confession.",
        "desc": "A vast pit where UAC dug into ancient black stone. Floodlights illuminate a demonic arch half-buried in dust. A Hell Knight stalks the edge, guarding something that glints near the altar.\n\nYour rifle feels suddenly inadequate in the philosophical sense.",
        "exits": {"south": "excavationHatch", "north": "hellGateAntechamber"},
        "hotspots": [
            {"id": "toHatch", "name": "Hatch", "rect": {"l": 10, "t": 34, "w": 18, "h": 28}, "kind": "exit", "data": {"dir": "south"}},
            {"id": "toAntechamber", "name": "Stone Stairs", "rect": {"l": 44, "t": 18, "w": 18, "h": 30}, "kind": "exit", "data": {"dir": "north"}},
            {"id": "hellKnight", "name": "Hell Knight", "rect": {"l": 58, "t": 42, "w": 18, "h": 28}, "kind": "enemy"},
            {"id": "altar", "name": "Ritual Altar", "rect": {"l": 44, "t": 62, "w": 18, "h": 16}, "kind": "object"},
        ],
        "objects": {
            "altar": {
                "look": "A cracked altar fused with circuitry. Something small lies in a notch: an AI core, impossibly clean.",
                "take": {
                    "requiresFlag": "knightGone",
                    "onceFlag": "tookLink",
                    "gain": ["neuralLink"],
                    "text": "With the Hell Knight distracted or dead, you grab the Neural Link. It is warm, like it knows your name.",
                    "takeFailText": "You step toward the altar. The Hell Knight steps toward you. Negotiations conclude.",
                    "takeFailDeath": "altarKnightKills",
                },
            },
            "hellKnight": {
                "look": "A Hell Knight: muscle, magma, and an HR policy written in screams.",
                "talk": {"death": "knightKills", "text": "You try a friendly wave. It returns an unfriendly murder."},
                "use": {
                    "options": [
                        {
                            "requiresItem": "beacon",
                            "onceFlag": "knightDistracted",
                            "text": "You arm the Emergency Beacon and toss it. It howls a siren and flashes strobe light. The Hell Knight turns, fascinated by the concept of noise.",
                            "setFlag": "knightGone",
                        },
                        {
                            "requiresItem": "chargedPlasmaRifle",
                            "requiresFlag": "knightDistracted",
                            "onceFlag": "knightDead",
                            "text": "While it's distracted, you level the charged Plasma Rifle and fire. Blue bolts tear through demon flesh like angry math. The Hell Knight collapses into ash and spite.",
                            "setFlag": "knightGone",
                        },
                    ],
                    "default": {"death": "knightKills", "text": "You square up for a fair fight. The Hell Knight accepts. Fairness does not."},
                },
            },
        },
    },
    "hellGateAntechamber": {
        "id": "hellGateAntechamber",
        "name": "Hell-Gate Antechamber — The Threshold",
        "theme": "antechamber",
        "mapPos": [4, 4],
        "mapFloor": -1,
        "enterText": "This is the point of no return, dressed up as architecture.\n\nUAC plating tries to cover the old stone, but the stone remembers. The door ahead is not locked to keep you out—it's locked to keep something in.\n\nThe Serpentine Key will open it. The question is what you’re opening it *for*.",
        "desc": "An antechamber where UAC plating overlays ancient stone. A massive demonic door stands to the north, its lock shaped like a coiled serpent.\n\nYou can hear a distant heartbeat that isn't yours. Or Mars's.",
        "exits": {"south": "templeLift", "north": "hellGateChamber"},
        "rules": {"gateToNorthRequiresFlag": "unlockedGate"},
        "hotspots": [
            {"id": "toLift", "name": "Lift", "rect": {"l": 10, "t": 34, "w": 18, "h": 28}, "kind": "exit", "data": {"dir": "south"}},
            {
                "id": "toChamber",
                "name": "Into the Hell-Gate",
                "rect": {"l": 44, "t": 16, "w": 18, "h": 28},
                "kind": "exit",
                "data": {"dir": "north"},
            },
            {"id": "serpentLock", "name": "Serpentine Lock", "rect": {"l": 50, "t": 52, "w": 12, "h": 14}, "kind": "object"},
        ],
        "objects": {
            "serpentLock": {
                "look": "A lock shaped like a serpent devouring its own tail. It wants a key. Obviously it does.",
                "use": {"requiresItem": "serpentineKey", "onceFlag": "unlockedGate", "text": "The Serpentine Key writhes into the lock. The door sighs open as if relieved to stop pretending it was closed."},
            }
        },
    },
    "armory": {
        "id": "armory",
        "name": "Armory Annex — Old Toys",
        "theme": "armory",
        "mapPos": [1, 4],
        "mapFloor": 0,
        "enterText": "The armory isn't empty. It's been harvested.\n\nThe lock marks are wrong—too hot, too clean, like something opened steel with a thought. Crux didn't just invite hell in. He gave it a supply room.",
        "desc": "A small armory annex. Most racks are empty. A reinforced weapons locker sits behind a red-lit keypad. One display case remains intact, holding a demonic-metal key that pulses like a living bruise.\n\nThe case has a UAC warning label: DO NOT OPEN. As if that ever worked.",
        "exits": {"south": "security"},
        "hotspots": [
            {"id": "toSec", "name": "Security", "rect": {"l": 10, "t": 34, "w": 18, "h": 28}, "kind": "exit", "data": {"dir": "south"}},
            {"id": "case", "name": "Display Case", "rect": {"l": 52, "t": 44, "w": 18, "h": 22}, "kind": "container"},
            {"id": "locker", "name": "Weapons Locker", "rect": {"l": 26, "t": 46, "w": 22, "h": 24}, "kind": "container"},
        ],
        "objects": {
            "case": {
                "look": "A sealed display case. The lock is simple—because the real lock is probably the curse.",
                "open": {"requiresItem": "redKeycard", "onceFlag": "openedCase", "gain": ["serpentineKey"], "text": "You pop the case. Cold air spills out. You take the Serpentine Key. The warning label silently updates to: TOLD YOU."},
                "use": {"death": "glassKills", "text": "You smash the glass with your elbow. The glass explodes outward and inward. Physics is also possessed."},
            },
            "locker": {
                "look": "A reinforced locker. The keypad glows red, as if it's embarrassed to be here.",
                "open": {"requiresItem": "redKeycard", "onceFlag": "openedLocker", "gain": ["plasmaRifle", "beacon"], "text": "The keypad accepts the Red Keycard with a cheerful beep. Inside: a Plasma Rifle (uncharged) and an Emergency Beacon."},
                "use": {"death": "lockerKickDeath", "text": "You try to 'use' the locker by kicking it. The locker wins."},
            },
        },
    },
    "hellGateChamber": {
        "id": "hellGateChamber",
        "name": "Hell-Gate Chamber — The Crucible",
        "theme": "hellgate",
        "mapPos": [4, 3],
        "mapFloor": 1,
        "enterText": "The heart of the facility. The throat of the rift.\n\nCrux didn’t lose control. He traded it. The air vibrates with a contract written in heat and teeth.\n\nIf you built the Soul-Core Breaker for any reason, it was for this moment. End the rift. End Crux. Then get out—before the Titan decides you’re interesting.",
        "desc": "The chamber is half factory, half cathedral. A rift churns at the far end, vomiting heat and whispers. Director Malcom Crux stands before it, fused with a demonic entity—robes made of cables, horns made of ambition.\n\nAbove the rift, a Titan-class silhouette presses against reality like a hand against thin ice.",
        "exits": {"south": "hellGateAntechamber"},
        "hotspots": [
            {"id": "toAnte", "name": "Antechamber", "rect": {"l": 10, "t": 34, "w": 18, "h": 28}, "kind": "exit", "data": {"dir": "south"}},
            {"id": "crux", "name": "Director Crux", "rect": {"l": 52, "t": 36, "w": 16, "h": 24}, "kind": "boss"},
            {"id": "rift", "name": "Hell Rift", "rect": {"l": 74, "t": 26, "w": 18, "h": 40}, "kind": "hazard"},
        ],
        "objects": {
            "rift": {
                "look": "A wound in the world. It bleeds light and laughter.",
                "use": {"death": "riftTouch"},
                "take": {"death": "riftTouch"},
                "open": {"death": "riftTouch"},
                "talk": {"death": "riftTouch"},
                "close": {"death": "riftTouch"},
            },
            "crux": {
                "look": "Crux's face is still there, somewhere under the demonic growth. His eyes burn with executive certainty.",
                "talk": "\"Marine,\" Crux purrs, voice doubled with something older. \"You are late. But late is still on time for sacrifice.\"",
                "use": {
                    "options": [
                        {
                            "requiresItem": "soulCoreBreaker",
                            "text": "You raise the Soul-Core Breaker. It screams—not in pain, but in joy. A beam of inverted helllight lances into the rift.\n\nThe Titan howls as reality clamps down like a jaw. Crux's fused form spasms, then is dragged backward, clawing at the air like a man trying to keep his job.\n\nA voice whispers: \"Seal achieved. Please evacuate. Or don't. I'm not your mother.\"",
                            "setFlag": "gameWon",
                        }
                    ],
                    "default": {"death": "cruxKills", "text": "You attempt an unassisted solution to an apocalyptic problem. Crux appreciates the comedy before removing your head."},
                },
            },
        },
    },
}
"""
apply_hotspot_layout_overrides(GAME)

from doomgate.util.paths import resource_path

ASSETS_DIR = resource_path("assets")
ROOMS_DIR = resource_path("assets", "rooms")
ITEMS_DIR = resource_path("assets", "items")
PROPS_DIR = resource_path("assets", "props")
UI_DIR = resource_path("assets", "ui")
TITLE_DIR = resource_path("assets", "title")
MUSIC_DIR = resource_path("assets", "music")
# Preferred stems (any of these extensions: .png .jpg .jpeg .webp .bmp)
TITLE_SCREEN_STEMS = ("crucible_facility", "crucible_exterior", "title", "title_screen")
# Title menu music in assets/title/ — preferred names first (extensions: .wav .ogg .mp3)
TITLE_MUSIC_STEMS = ("title_menu", "menu", "title_music", "theme")
# In-game looped music in assets/music/ — put **gameplay.wav** here (or .ogg/.mp3); see GAMEPLAY_MUSIC_STEMS order
GAMEPLAY_MUSIC_STEMS = ("gameplay", "game", "ambient", "ingame")


def resolve_title_music_path() -> Optional[str]:
    """First matching file under assets/title/ (see TITLE_MUSIC_STEMS)."""
    exts = (".wav", ".ogg", ".mp3")
    if not os.path.isdir(TITLE_DIR):
        return None
    for stem in TITLE_MUSIC_STEMS:
        for ext in exts:
            p = os.path.normpath(os.path.join(TITLE_DIR, stem + ext))
            if os.path.isfile(p):
                return p
    return None


def resolve_gameplay_music_path() -> Optional[str]:
    """First matching file under assets/music/ (see GAMEPLAY_MUSIC_STEMS). Prefer gameplay.wav."""
    exts = (".wav", ".ogg", ".mp3")
    if not os.path.isdir(MUSIC_DIR):
        return None
    for stem in GAMEPLAY_MUSIC_STEMS:
        for ext in exts:
            p = os.path.normpath(os.path.join(MUSIC_DIR, stem + ext))
            if os.path.isfile(p):
                return p
    return None


def load_ui_player_face_frames() -> List[pygame.Surface]:
    """Optional PNG sequence: assets/ui/player_face_00.png … (sorted by name)."""
    if not os.path.isdir(UI_DIR):
        return []
    names = sorted(
        fn
        for fn in os.listdir(UI_DIR)
        if fn.lower().startswith("player_face") and fn.lower().endswith(".png")
    )
    out: List[pygame.Surface] = []
    for fn in names:
        surf = try_load_png(os.path.join(UI_DIR, fn))
        if surf is not None:
            out.append(surf)
    return out


def load_plasma_orb_decor() -> Optional[pygame.Surface]:
    """Optional frame/glass overlay for the lantern orb (used only if sprite frames missing)."""
    for name in ("plasma_orb_decor.png", "plasma_lantern_decor.png"):
        p = os.path.join(UI_DIR, name)
        s = try_load_png(p)
        if s is not None:
            return s
    return None


# Discrete HUD sprites: assets/ui/plasma_orb_{0,10,...,100}.png (see docstring on load_plasma_orb_frames).
PLASMA_ORB_LEVELS: Tuple[int, ...] = tuple(range(0, 101, 10))


def load_plasma_orb_frames() -> Dict[int, Optional[pygame.Surface]]:
    """Load 11 PNGs: plasma_orb_100.png … plasma_orb_0.png (10% steps). Missing files stay None."""
    out: Dict[int, Optional[pygame.Surface]] = {}
    for pct in PLASMA_ORB_LEVELS:
        p = os.path.join(UI_DIR, f"plasma_orb_{pct}.png")
        out[pct] = try_load_png(p)
    return out


def plasma_percent_bucket(fill01: float) -> int:
    """Orb art: 100 only when pool full; (90%,100%)→90; (80%,90%]→80; …; (0,10%]→10; 0→0."""
    f = max(0.0, min(1.0, float(fill01)))
    if f >= 1.0:
        return 100
    if f <= 0.0:
        return 0
    if f > 0.9:
        return 90
    if f > 0.8:
        return 80
    if f > 0.7:
        return 70
    if f > 0.6:
        return 60
    if f > 0.5:
        return 50
    if f > 0.4:
        return 40
    if f > 0.3:
        return 30
    if f > 0.2:
        return 20
    if f > 0.1:
        return 10
    return 10


def viewport_corner_meter_layout(viewport_rect: pygame.Rect) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
    """(lx, ly, r) left plasma, (rx, ry, r) right face — hug bottom + outer edges of the room viewport (UI chrome)."""
    vw, vh = viewport_rect.w, viewport_rect.h
    r = int(min(vw, vh) * 0.15)
    r = clamp(r, 34, min(vw, vh) // 2 - 4)
    # Circles sit on the bottom edge and tuck against left / right viewport edges (extension of the frame UI)
    margin_x = 3
    margin_bottom = 2
    ly = viewport_rect.bottom - r - margin_bottom
    lx = viewport_rect.left + r + margin_x
    rx = viewport_rect.right - r - margin_x
    return (lx, ly, r), (rx, ly, r)


def plasma_charge_fraction(state: Dict[str, Any]) -> float:
    """0..1 charge of the *active* lantern only (resets to 1.0 when a new lantern starts)."""
    if state.get("godMode"):
        return 1.0
    ap = GAME["meta"]["actionsPerLantern"]
    if ap <= 0 or state["lanterns"] <= 0:
        return 0.0
    seg = state["actions"] % ap
    return float(ap - seg) / float(ap)


def player_face_frame_index(state: Dict[str, Any]) -> int:
    """Pick sprite index for status portrait (0=good … higher=worse)."""
    if get_flag(state, "gameWon"):
        return 0
    if state.get("godMode"):
        return 0
    if not state["alive"]:
        return 5
    ap = GAME["meta"]["actionsPerLantern"]
    ud = max(0, ap - (state["actions"] % ap))
    if state["lanterns"] <= 1 and state["alive"]:
        if state["lanterns"] == 0:
            return 5
        if ud <= ap // 3:
            return 4
        return 3
    if state["lanterns"] == 2 and ud <= ap // 4:
        return 2
    return 1 if state["lanterns"] <= 2 else 0


def _fill_circle_from_bottom(
    target: pygame.Surface, cx: int, cy: int, r: int, fill01: float, rgb: Tuple[int, int, int]
) -> None:
    fill01 = float(clamp(int(fill01 * 1000), 0, 1000)) / 1000.0
    if fill01 <= 0:
        return
    y_end = cy + r
    y_start = cy + r - int(2 * r * fill01) - 1
    for y in range(y_start, y_end + 1):
        dy = y - cy
        if abs(dy) > r:
            continue
        half = int(math.sqrt(max(0, r * r - dy * dy)))
        pygame.draw.line(target, rgb, (cx - half, y), (cx + half, y))


def draw_plasma_lantern_meter(
    screen: pygame.Surface,
    cx: int,
    cy: int,
    r: int,
    fill01: float,
    frames: Dict[int, Optional[pygame.Surface]],
    decor: Optional[pygame.Surface],
    colors: Dict[str, Any],
    lantern_remaining: int,
    lantern_max: int,
    font: pygame.font.Font,
) -> None:
    pct = plasma_percent_bucket(fill01)
    surf = frames.get(pct) if frames else None
    if surf is not None:
        side = max(32, int(r * 2) + 4)
        scaled = pygame.transform.scale(surf, (side, side))
        screen.blit(scaled, scaled.get_rect(center=(cx, cy)))
    else:
        # Fallback: procedural fill + optional decor (no art assets yet)
        pygame.draw.circle(screen, (12, 18, 14), (cx, cy), r + 2)
        pygame.draw.circle(screen, colors["accent"], (cx, cy), r + 2, width=2)
        pygame.draw.circle(screen, (4, 8, 6), (cx, cy), r)
        inner = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        ix, iy = r + 2, r + 2
        tier01 = pct / 100.0
        _fill_circle_from_bottom(inner, ix, iy, r - 2, tier01, colors["accent"])
        screen.blit(inner, (cx - ix, cy - iy))
        pygame.draw.circle(screen, colors["accent_dim"], (cx, cy), r, width=1)
        if decor is not None:
            dw = min(r * 2 + 8, decor.get_width())
            dh = min(r * 2 + 8, decor.get_height())
            d = pygame.transform.smoothscale(decor, (dw, dh))
            screen.blit(d, d.get_rect(center=(cx, cy)))
    label = f"{lantern_remaining}/{lantern_max}"
    tx = cx + r - font.size(label)[0] - 2
    ty = cy - r + 2
    screen.blit(font.render(label, True, (0, 0, 0)), (tx + 1, ty + 1))
    screen.blit(font.render(label, True, colors["accent_dim"]), (tx, ty))


def draw_player_status_meter(
    screen: pygame.Surface,
    cx: int,
    cy: int,
    r: int,
    frame_idx: int,
    frames: List[pygame.Surface],
    colors: Dict[str, Any],
) -> None:
    pygame.draw.circle(screen, (14, 18, 16), (cx, cy), r + 2)
    pygame.draw.circle(screen, colors["accent"], (cx, cy), r + 2, width=2)
    if frames:
        img = frames[frame_idx % len(frames)]
        side = min(r * 2, max(32, int(r * 1.85)))
        scaled = pygame.transform.smoothscale(img, (side, side))
        screen.blit(scaled, scaled.get_rect(center=(cx, cy)))
    else:
        # Placeholder Doom-style mug until PNGs exist
        pygame.draw.circle(screen, (90, 72, 58), (cx, cy), r - 2)
        eye = (255, 220, 200)
        pygame.draw.circle(screen, eye, (cx - r // 3, cy - r // 8), max(3, r // 10))
        pygame.draw.circle(screen, eye, (cx + r // 3, cy - r // 8), max(3, r // 10))
        mouth_h = clamp(r // 4 + frame_idx * 2, 2, r // 2)
        pygame.draw.arc(screen, (40, 28, 24), pygame.Rect(cx - r // 2, cy, r, mouth_h), math.pi * 0.1, math.pi * 0.9, 2)
    pygame.draw.circle(screen, colors["accent_dim"], (cx, cy), r, width=1)


def draw_viewport_corner_meters(
    screen: pygame.Surface,
    lx: int,
    ly: int,
    rl: int,
    rx: int,
    ry: int,
    rr: int,
    state: Dict[str, Any],
    colors: Dict[str, Any],
    face_frames: List[pygame.Surface],
    plasma_frames: Dict[int, Optional[pygame.Surface]],
    plasma_decor: Optional[pygame.Surface],
    font_small: pygame.font.Font,
) -> None:
    fill = plasma_charge_fraction(state)
    lmax = int(GAME["meta"]["lanternMaxCarry"])
    # Remaining charges (lanternCount − spent); orb label matches status PLASMA LANTERN line.
    lantern_remaining = int(state.get("lanterns", 0))
    draw_plasma_lantern_meter(
        screen, lx, ly, rl, fill, plasma_frames, plasma_decor, colors, lantern_remaining, lmax, font_small
    )
    fidx = player_face_frame_index(state)
    draw_player_status_meter(screen, rx, ry, rr, fidx, face_frames, colors)


def try_load_png(path: str) -> Optional[pygame.Surface]:
    try:
        if not os.path.exists(path):
            return None
        img = pygame.image.load(path)
        # Convert using alpha if present
        return img.convert_alpha() if img.get_alpha() is not None else img.convert()
    except Exception:
        return None


def scale_image_cover(src: pygame.Surface, tw: int, th: int) -> pygame.Surface:
    """Scale uniformly to cover tw×th; crop center (no letterboxing)."""
    iw, ih = src.get_size()
    if iw <= 0 or ih <= 0 or tw <= 0 or th <= 0:
        return pygame.transform.scale(src, (max(1, tw), max(1, th)))
    scale = max(tw / iw, th / ih)
    nw = max(1, int(iw * scale))
    nh = max(1, int(ih * scale))
    try:
        scaled = pygame.transform.smoothscale(src, (nw, nh))
        x = (nw - tw) // 2
        y = (nh - th) // 2
        rect = pygame.Rect(x, y, tw, th)
        return scaled.subsurface(rect).copy()
    except Exception:
        return pygame.transform.smoothscale(src, (tw, th))


def load_title_background_image() -> Optional[pygame.Surface]:
    """Load first available title image: preferred names (any ext), then any image in assets/title/."""
    exts = (".png", ".jpg", ".jpeg", ".webp", ".bmp")

    def load_path(p: str) -> Optional[pygame.Surface]:
        try:
            p = os.path.normpath(p)
            if not os.path.isfile(p):
                return None
            img = pygame.image.load(p)
            # Prefer alpha-capable format so RGBA PNGs and room art don't turn into flat black/wrong pixels.
            try:
                return img.convert_alpha()
            except Exception:
                try:
                    return img.convert()
                except Exception:
                    return img
        except Exception:
            return None

    if os.path.isdir(TITLE_DIR):
        for stem in TITLE_SCREEN_STEMS:
            for ext in exts:
                p = os.path.join(TITLE_DIR, stem + ext)
                surf = load_path(p)
                if surf is not None:
                    return surf
        try:
            names = sorted(os.listdir(TITLE_DIR))
        except OSError:
            names = []
        for fn in names:
            if fn.startswith(".") or fn.lower() == ".gitkeep":
                continue
            low = fn.lower()
            if not any(low.endswith(e) for e in exts):
                continue
            surf = load_path(os.path.join(TITLE_DIR, fn))
            if surf is not None:
                return surf
    return None


def hotspot_show_overlay(hs: Dict[str, Any]) -> bool:
    """Exits and barriers are usually already painted in room art—hitbox only. Optional per-hotspot override."""
    if hs.get("showSprite") is True:
        return True
    if hs.get("showSprite") is False:
        return False
    return hs["kind"] not in ("exit", "barrier")


def wrap_text_lines(font: pygame.font.Font, text: str, max_width: int) -> List[str]:
    def break_long_token(tok: str) -> List[str]:
        if max_width <= 8 or font.size(tok)[0] <= max_width:
            return [tok]
        parts: List[str] = []
        acc = ""
        for ch in tok:
            t = acc + ch
            if font.size(t)[0] <= max_width:
                acc = t
            else:
                if acc:
                    parts.append(acc)
                acc = ch
        if acc:
            parts.append(acc)
        return parts

    words = text.replace("\n", " \n ").split()
    lines: List[str] = []
    cur = ""
    for w in words:
        if w == "\n":
            if cur:
                lines.append(cur)
                cur = ""
            continue
        for piece in break_long_token(w):
            test = (cur + " " + piece).strip() if cur else piece
            if font.size(test)[0] <= max_width:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = piece
    if cur:
        lines.append(cur)
    return lines


# Strip redundant facility subtitle; plasma orb shows drain in the viewport meter.
_STATUS_FACILITY_SUFFIX = re.compile(r"\s*[—\-]\s*THE CRUCIBLE FACILITY\s*$", re.IGNORECASE)


def room_name_for_status_bar(room_name: str) -> str:
    return _STATUS_FACILITY_SUFFIX.sub("", room_name.strip()).strip()


def truncate_after_prefix_to_width(
    font: pygame.font.Font, prefix: str, body: str, max_total_w: int
) -> str:
    """Fit prefix+body in max_total_w (measures full string; for status lines)."""
    if max_total_w <= 0:
        return ""
    full = prefix + body
    if font.size(full)[0] <= max_total_w:
        return body
    ell = "…"
    if font.size(prefix + ell)[0] > max_total_w:
        return ell if font.size(ell)[0] <= max_total_w else ""
    lo, hi = 0, len(body)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        cand = prefix + body[:mid] + ell
        if font.size(cand)[0] <= max_total_w:
            lo = mid
        else:
            hi = mid - 1
    return body[:lo] + ell if lo > 0 else ell


# -----------------------------
# State
# -----------------------------


def default_state() -> Dict[str, Any]:
    from doomgate.game import default_state as _s

    return _s(GAME)


def clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, v))


def layout_right_internals(
    right_panel: pygame.Rect,
    commands: List[Dict[str, Any]],
    *,
    manual_row: int = 36,
) -> Dict[str, Any]:
    """Place Held, minimap, inventory, command grid inside the right column (matches compute_layout)."""
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
    """Hotspot-style hit test: corner scale, edge axis resize, interior move. Returns drag payload or None."""
    if not r.collidepoint(pos):
        # allow grabbing resize handles that might extend — still inside rect in our layout
        return None
    hsz = max(6, min(handle_px, r.w // 2, r.h // 2))
    handle = pygame.Rect(r.right - hsz, r.bottom - hsz, hsz, hsz)
    if not handle.colliderect(r):
        handle = pygame.Rect(r.right - min(hsz, r.w), r.bottom - min(hsz, r.h), min(hsz, r.w), min(hsz, r.h))
    if handle.collidepoint(pos):
        return {
            "mode": "resize",
            "w0": float(max(1, r.w)),
            "h0": float(max(1, r.h)),
            "tl": (float(r.x), float(r.y)),
        }
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
    return {
        "mode": "move",
        "grab": (float(pos[0] - r.x), float(pos[1] - r.y)),
        "w": float(r.w),
        "h": float(r.h),
    }


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


def enable_god_mode(state: Dict[str, Any], log: Any) -> None:
    """Debug: invulnerability, pegged lantern/orb, every item, full map reveal."""
    from doomgate.game import enable_god_mode as _g

    _g(GAME, state, log)


def item_def(item_id: str) -> Dict[str, Any]:
    from doomgate.game import item_def as _i

    return _i(GAME, item_id)


def room_def(room_id: str) -> Dict[str, Any]:
    from doomgate.game import room_def as _r

    return _r(GAME, room_id)


def has_item(state: Dict[str, Any], item_id: str) -> bool:
    from doomgate.game import has_item as _h

    return _h(state, item_id)


def get_flag(state: Dict[str, Any], name: str) -> bool:
    from doomgate.game import get_flag as _g

    return _g(state, name)


def set_flag(state: Dict[str, Any], name: str, value: bool = True) -> None:
    from doomgate.game import set_flag as _s

    _s(state, name, value)


# -----------------------------
# UI components
# -----------------------------


@dataclass
class Button:
    rect: pygame.Rect
    label: str
    value: str
    active: bool = False
    danger: bool = False

    def draw(self, surf: pygame.Surface, font: pygame.font.Font, colors: Dict[str, Any]) -> None:
        border = colors["accent"] if self.active else colors["border"]
        bg = colors["cmd_active_bg"] if self.active else colors["cmd_bg"]
        if self.danger:
            border = colors["danger_border"]
            bg = colors["danger_bg"]
        pygame.draw.rect(surf, bg, self.rect, border_radius=8)
        pygame.draw.rect(surf, border, self.rect, width=1, border_radius=8)
        text = font.render(self.label, True, colors["text"])
        surf.blit(text, text.get_rect(center=self.rect.center))


class ScrollLog:
    def __init__(self) -> None:
        self.lines: List[Tuple[str, str]] = []  # (text, kind) logical lines (may wrap when drawn)
        self.scroll_px: int = 0
        self.max_lines: int = 800
        self._snap_to_bottom: bool = True

    def add(self, text: str, kind: str = "line") -> None:
        for chunk in str(text).split("\n"):
            self.lines.append((chunk, kind))
        if len(self.lines) > self.max_lines:
            self.lines = self.lines[-self.max_lines :]
        self._snap_to_bottom = True

    def scroll(self, delta_px: int) -> None:
        self.scroll_px = max(0, self.scroll_px + delta_px)

    def _build_wrapped(self, font: pygame.font.Font, max_width: int) -> List[Tuple[str, str]]:
        out: List[Tuple[str, str]] = []
        for text, kind in self.lines:
            parts = wrap_text_lines(font, text, max_width)
            if not parts:
                out.append(("", kind))
            else:
                for p in parts:
                    out.append((p, kind))
        return out

    def draw(self, surf: pygame.Surface, rect: pygame.Rect, font: pygame.font.Font, colors: Dict[str, Any]) -> None:
        pygame.draw.rect(surf, colors["log_bg"], rect)
        pygame.draw.rect(surf, colors["log_border"], rect, 1)

        inner = rect.inflate(-10, -10)
        maxw = max(40, inner.w - 4)
        display_lines = self._build_wrapped(font, maxw)

        line_h = font.get_linesize()
        content_h = len(display_lines) * line_h
        view_h = rect.h - 10
        max_scroll = max(0, content_h - view_h)
        if self._snap_to_bottom:
            self.scroll_px = max_scroll
            self._snap_to_bottom = False
        self.scroll_px = clamp(self.scroll_px, 0, max_scroll)

        clip = surf.subsurface(inner)
        clip.fill(colors["log_bg_inner"])

        y = -self.scroll_px
        for text, kind in display_lines:
            if y > clip.get_height():
                break
            if y + line_h >= 0:
                color = colors["log_text"]
                if kind == "dim":
                    color = colors["log_dim"]
                elif kind == "warn":
                    color = colors["warn"]
                elif kind == "dead":
                    color = colors["dead"]
                elif kind == "sys":
                    color = colors["sys"]
                elif kind == "title":
                    color = colors["title"]
                clip.blit(font.render(text, True, color), (0, y))
            y += line_h

        if max_scroll > 0:
            track = pygame.Rect(rect.right - 8, rect.y + 4, 4, rect.h - 8)
            pygame.draw.rect(surf, colors["scroll_track"], track, border_radius=3)
            thumb_h = max(18, int(track.h * (view_h / max(content_h, 1))))
            thumb_y = track.y + int((track.h - thumb_h) * (self.scroll_px / max_scroll))
            thumb = pygame.Rect(track.x, thumb_y, track.w, thumb_h)
            pygame.draw.rect(surf, colors["scroll_thumb"], thumb, border_radius=3)

    def wheel(self, y: int) -> None:
        # pygame wheel: y > 0 means up
        self.scroll(-y * 28)


def announce_victory_if_won(state: Dict[str, Any], log: ScrollLog) -> None:
    from doomgate.game import announce_victory_if_won as _a

    _a(state, log)


# -----------------------------
# Pixelated background generator
# -----------------------------


def seeded_rand(n: int) -> int:
    # small deterministic LCG
    return (1103515245 * n + 12345) & 0x7FFFFFFF


def pix_bg(theme: str, size: Tuple[int, int]) -> pygame.Surface:
    w, h = size
    # Create a low-res surface and scale up with NEAREST for pixelation.
    base_w, base_h = max(40, w // 12), max(34, h // 12)
    low = pygame.Surface((base_w, base_h))

    # Theme palettes (industrial doom-ish)
    palettes = {
        "hangar": [(10, 14, 12), (18, 26, 22), (43, 52, 48), (124, 15, 15), (25, 255, 106)],
        "corridor": [(9, 12, 10), (20, 28, 24), (52, 62, 56), (255, 43, 43), (255, 211, 77)],
        "security": [(8, 10, 9), (24, 30, 27), (60, 72, 66), (255, 211, 77), (25, 255, 106)],
        "maintenance": [(6, 9, 8), (18, 24, 21), (42, 52, 48), (25, 255, 106), (255, 43, 43)],
        "labsDoor": [(7, 9, 8), (18, 23, 20), (44, 56, 50), (124, 15, 15), (255, 211, 77)],
        "labs": [(7, 10, 9), (18, 26, 22), (34, 44, 40), (25, 255, 106), (180, 220, 200)],
        "quarters": [(7, 9, 8), (18, 23, 20), (38, 48, 44), (124, 15, 15), (25, 255, 106)],
        "lift": [(7, 9, 8), (20, 26, 23), (46, 56, 52), (255, 211, 77), (25, 255, 106)],
        "hatch": [(7, 9, 8), (20, 26, 23), (46, 56, 52), (255, 43, 43), (255, 211, 77)],
        "excavation": [(6, 8, 7), (18, 22, 20), (36, 44, 40), (255, 43, 43), (255, 211, 77)],
        "antechamber": [(6, 8, 7), (16, 21, 19), (32, 42, 38), (25, 255, 106), (255, 211, 77)],
        "armory": [(6, 8, 7), (16, 21, 19), (32, 42, 38), (255, 43, 43), (255, 211, 77)],
        "hellgate": [(5, 6, 6), (12, 14, 14), (28, 30, 30), (255, 43, 43), (255, 211, 77)],
    }
    pal = palettes.get(theme, palettes["corridor"])

    seed = sum(ord(c) for c in theme) + base_w * 31 + base_h * 17
    for y in range(base_h):
        for x in range(base_w):
            r = seeded_rand(seed + x * 997 + y * 463)
            c = pal[(r // 97) % len(pal)]
            # add subtle noise and gradients
            shade = ((r >> 8) & 7) - 3
            rr = clamp(c[0] + shade + int(8 * (y / base_h)), 0, 255)
            gg = clamp(c[1] + shade + int(6 * (y / base_h)), 0, 255)
            bb = clamp(c[2] + shade + int(6 * (y / base_h)), 0, 255)
            low.set_at((x, y), (rr, gg, bb))

    # Plot-faithful overlays in low-res so they pixelate cleanly when scaled:
    # UAC industrial panels + demonic temple shapes (arches, runes, blood, terminals, rift glow).
    def box(x: int, y: int, ww: int, hh: int, col: Tuple[int, int, int], border: Optional[Tuple[int, int, int]] = None) -> None:
        pygame.draw.rect(low, col, pygame.Rect(x, y, ww, hh), border_radius=2)
        if border:
            pygame.draw.rect(low, border, pygame.Rect(x, y, ww, hh), width=1, border_radius=2)

    def rune(x: int, y: int, col: Tuple[int, int, int]) -> None:
        pygame.draw.line(low, col, (x, y), (x + 6, y + 2), width=1)
        pygame.draw.line(low, col, (x + 6, y + 2), (x + 2, y + 8), width=1)
        pygame.draw.line(low, col, (x + 2, y + 8), (x + 8, y + 10), width=1)

    def blood_smear(x: int, y: int, ww: int, hh: int) -> None:
        pygame.draw.rect(low, (80, 10, 10), pygame.Rect(x, y, ww, hh))
        pygame.draw.line(low, (124, 15, 15), (x, y), (x + ww, y + hh), width=1)

    def arch(cx: int, top: int, rad: int, col: Tuple[int, int, int]) -> None:
        pygame.draw.circle(low, col, (cx, top + rad), rad, width=2)
        pygame.draw.rect(low, col, pygame.Rect(cx - rad, top + rad, rad * 2, 3))

    accent = pal[-1]
    steel = pal[2]
    dark = pal[0]
    danger = (255, 43, 43)
    gold = (255, 211, 77)

    # UAC paneling (horizontal bands + rivets)
    for y in range(6, base_h, 10):
        pygame.draw.line(low, (steel[0] + 6, steel[1] + 6, steel[2] + 6), (2, y), (base_w - 3, y), width=1)
        for x in range(6, base_w, 12):
            low.set_at((x, y), (min(255, steel[0] + 40), min(255, steel[1] + 40), min(255, steel[2] + 40)))

    # Demonic runes crawling over walls
    for i in range(6):
        rr = seeded_rand(seed + i * 1337)
        rx = 4 + (rr % max(1, base_w - 14))
        ry = 6 + ((rr >> 8) % max(1, base_h - 16))
        rune(rx, ry, (min(255, accent[0]), min(255, accent[1] // 2), min(255, accent[2] // 2)))

    # Theme-specific silhouettes
    if theme == "hangar":
        # Ribbed hangar arches + terminal glow + crate blocks
        for cx in range(8, base_w, 12):
            arch(cx, 2, 7, (30, 40, 36))
        box(base_w // 2 - 10, base_h // 2 - 4, 20, 10, (12, 16, 14), border=(25, 255, 106))
        box(base_w // 2 - 18, base_h - 12, 14, 8, (22, 30, 26), border=(40, 52, 48))
        box(base_w // 2 + 6, base_h - 12, 14, 8, (22, 30, 26), border=(40, 52, 48))
    elif theme == "corridor":
        # Perspective corridor + hazard pool hint
        pygame.draw.polygon(low, (14, 18, 16), [(2, 10), (base_w - 3, 10), (base_w - 10, base_h - 3), (10, base_h - 3)])
        pygame.draw.line(low, danger, (base_w // 2, 2), (base_w // 2, base_h - 3), width=1)
        box(base_w // 2 - 6, base_h - 10, 12, 4, (20, 40, 24), border=(25, 255, 106))
    elif theme == "security":
        # Checkpoint window + locker block
        box(6, 12, base_w // 3, base_h // 3, (16, 20, 18), border=(40, 52, 48))
        box(base_w // 2 - 9, base_h // 2 - 2, 18, 12, (10, 14, 12), border=gold)
        blood_smear(base_w - 18, base_h - 14, 10, 6)
    elif theme == "maintenance":
        # Pipes + argent conduit column
        pygame.draw.line(low, (40, 52, 48), (2, base_h // 3), (base_w - 3, base_h // 3), width=2)
        pygame.draw.line(low, accent, (base_w // 2, 2), (base_w // 2, base_h - 3), width=2)
        box(base_w // 2 - 2, base_h // 2 - 6, 4, 12, (10, 14, 12), border=accent)
    elif theme == "labsDoor":
        # Blast door + blood seal circle
        box(base_w // 2 - 14, 8, 28, base_h - 16, (22, 30, 26), border=(40, 52, 48))
        pygame.draw.circle(low, (90, 10, 10), (base_w // 2, base_h // 2), 9)
        pygame.draw.circle(low, danger, (base_w // 2, base_h // 2), 9, width=1)
    elif theme == "labs":
        # Containment bays + crystal pedestal glow
        for x in range(8, base_w - 8, 14):
            box(x, base_h // 2 - 8, 10, 16, (14, 18, 16), border=(30, 40, 36))
        pygame.draw.circle(low, (25, 255, 106), (base_w // 2, base_h // 2), 5)
        pygame.draw.circle(low, (180, 220, 200), (base_w // 2, base_h // 2), 7, width=1)
    elif theme == "quarters":
        # Bunk blocks + safety poster smear
        box(6, 14, base_w // 3, base_h - 24, (20, 26, 23), border=(40, 52, 48))
        box(base_w // 2, 16, base_w // 3, base_h // 2, (14, 18, 16), border=(30, 40, 36))
        blood_smear(base_w // 2 + 2, 10, 10, 6)
    elif theme == "lift":
        # Elevator frame + up/down lights
        box(base_w // 2 - 14, 6, 28, base_h - 12, (22, 30, 26), border=(40, 52, 48))
        box(base_w // 2 - 2, base_h // 2 - 1, 4, 2, gold)
        box(base_w // 2 - 2, base_h // 2 + 4, 4, 2, (25, 255, 106))
    elif theme == "hatch":
        # Hatch plate + red lock
        box(base_w // 2 - 14, 8, 28, base_h - 16, (22, 30, 26), border=(40, 52, 48))
        box(base_w // 2 - 3, base_h // 2 - 2, 6, 6, (20, 10, 10), border=danger)
    elif theme == "excavation":
        # Dig pit wedge + arch fragment
        pygame.draw.polygon(low, (14, 18, 16), [(6, base_h - 3), (base_w // 2, base_h // 2), (base_w - 6, base_h - 3)])
        pygame.draw.arc(low, danger, pygame.Rect(base_w // 2 - 10, base_h // 2 - 10, 20, 20), 3.14, 0, width=1)
    elif theme == "antechamber":
        # Stone + UAC plating + lock glow
        box(4, 6, base_w - 8, base_h - 12, (12, 14, 14), border=(28, 30, 30))
        box(base_w // 2 - 12, 8, 24, base_h - 16, (18, 24, 21), border=(40, 52, 48))
        pygame.draw.circle(low, accent, (base_w // 2, base_h // 2), 4)
    elif theme == "armory":
        # Racks + glass case glow
        box(6, base_h // 2 - 8, base_w - 12, 16, (14, 18, 16), border=(30, 40, 36))
        box(base_w // 2 - 8, base_h // 2 - 6, 16, 12, (10, 14, 12), border=danger)
    elif theme == "hellgate":
        # Cathedral columns + rift glow
        for x in range(8, base_w, 16):
            box(x, 8, 6, base_h - 16, (16, 18, 18), border=(28, 30, 30))
        pygame.draw.circle(low, (90, 10, 10), (base_w - 10, base_h // 2), 9)
        pygame.draw.circle(low, danger, (base_w - 10, base_h // 2), 7)
        pygame.draw.circle(low, gold, (base_w - 10, base_h // 2), 4)

    hi = pygame.transform.scale(low, (w, h))
    return hi.convert()


# -----------------------------
# Pixel sprites for hotspots (always visible)
# -----------------------------


def sprite_pixel_icon(kind: str, obj_id: str, theme: str, px: int = 16, scale: int = 2) -> pygame.Surface:
    """
    Create a tiny pixel sprite (procedural) and scale it up with NEAREST.
    This avoids external assets and keeps the 'pixelated' vibe.
    """
    low = pygame.Surface((px, px), pygame.SRCALPHA)

    def p(x: int, y: int, col: Tuple[int, int, int, int]) -> None:
        if 0 <= x < px and 0 <= y < px:
            low.set_at((x, y), col)

    # Common palette
    steel = (50, 64, 58, 255)
    dark = (12, 16, 14, 255)
    green = (25, 255, 106, 255)
    red = (255, 43, 43, 255)
    gold = (255, 211, 77, 255)
    bone = (180, 220, 200, 255)

    # Background fill (subtle)
    for y in range(px):
        for x in range(px):
            if (x + y) % 7 == 0:
                p(x, y, (0, 0, 0, 0))

    # Icon by object/hotspot
    k = kind
    oid = obj_id

    if k == "exit" or oid.startswith("to"):
        # door
        for y in range(3, px - 2):
            for x in range(5, px - 5):
                p(x, y, steel)
        for y in range(4, px - 3):
            p(6, y, dark)
            p(px - 7, y, dark)
        p(px - 7, px // 2, gold)
    elif oid in {"terminal", "intercom"}:
        # screen
        for y in range(4, 11):
            for x in range(3, px - 3):
                p(x, y, dark)
        for x in range(4, px - 4):
            p(x, 5, green)
        for x in range(4, px - 6):
            p(x, 7, green)
        for y in range(11, 14):
            for x in range(4, px - 4):
                p(x, y, steel)
    elif oid in {"lanternCrate", "locker", "case", "panel"}:
        # container box
        for y in range(5, px - 4):
            for x in range(4, px - 4):
                p(x, y, steel)
        for x in range(4, px - 4):
            p(x, 5, dark)
        p(px // 2, px // 2, green if oid in {"panel"} else gold)
    elif oid in {"corpse"}:
        # skull-ish
        for y in range(4, 11):
            for x in range(5, px - 5):
                p(x, y, bone)
        p(6, 7, dark)
        p(px - 7, 7, dark)
        p(px // 2, 10, dark)
    elif oid in {"conduit"}:
        # battery/cell
        for y in range(4, px - 4):
            for x in range(6, px - 6):
                p(x, y, green)
        for x in range(7, px - 7):
            p(x, 6, bone)
        p(px // 2, 3, gold)
    elif oid in {"ooze", "rift"} or k == "hazard":
        # slime / rift
        col = (25, 255, 106, 255) if oid == "ooze" else red
        for y in range(5, px - 5):
            for x in range(5, px - 5):
                if (x - px // 2) ** 2 + (y - px // 2) ** 2 <= 25:
                    p(x, y, col)
        p(px // 2 - 2, px // 2, gold)
    elif oid in {"crystal"}:
        # crystal
        for y in range(4, px - 4):
            for x in range(7, px - 7):
                p(x, y, green)
        for i in range(4, px - 4):
            p(px // 2, i, bone)
        p(px // 2, 3, gold)
    elif oid in {"altar"}:
        # altar block
        for y in range(9, px - 4):
            for x in range(4, px - 4):
                p(x, y, steel)
        for x in range(6, px - 6):
            p(x, 8, red)
    elif oid in {"hellKnight"} or k == "enemy":
        # horned head
        for y in range(6, 12):
            for x in range(5, px - 5):
                p(x, y, red)
        p(4, 6, gold)
        p(px - 5, 6, gold)
        p(px // 2, 12, dark)
    elif oid in {"serpentLock"}:
        # keyhole coil
        for i in range(5, px - 5):
            p(i, 6, green)
            p(i, 10, green)
        p(5, 8, green)
        p(px - 6, 8, green)
        p(px // 2, 8, gold)
    elif oid in {"crux"} or k == "boss":
        # robed silhouette
        for y in range(4, px - 3):
            for x in range(px // 2 - 3, px // 2 + 4):
                p(x, y, (60, 20, 20, 255))
        p(px // 2 - 4, 6, gold)
        p(px // 2 + 4, 6, gold)
        for y in range(10, px - 3):
            for x in range(px // 2 - 6, px // 2 + 7):
                p(x, y, (40, 52, 48, 255))

    hi = pygame.transform.scale(low, (px * scale, px * scale))
    return hi.convert_alpha()


# -----------------------------
# Game logic
# -----------------------------


def action_cost(kind: str) -> int:
    from doomgate.game import action_cost as _c

    return _c(kind)


def apply_action(state: Dict[str, Any], kind: str, log: ScrollLog) -> None:
    from doomgate.game import apply_action as _a

    _a(GAME, state, kind, log)


def die(state: Dict[str, Any], log: ScrollLog, text: str) -> None:
    from doomgate.game import die as _d

    _d(GAME, state, log, text)


def add_items(state: Dict[str, Any], items: List[str]) -> None:
    from doomgate.game import add_items as _a

    _a(state, items)


def remove_items(state: Dict[str, Any], items: List[str]) -> None:
    from doomgate.game import remove_items as _r

    _r(state, items)


def try_combination(
    state: Dict[str, Any],
    log: ScrollLog,
    a: str,
    b: str,
    acquired: Optional[List[str]] = None,
) -> bool:
    from doomgate.game import try_combination as _t

    return _t(GAME, state, log, a, b, acquired=acquired)


def assemble_soul_core_breaker(
    state: Dict[str, Any],
    log: ScrollLog,
    acquired: Optional[List[str]] = None,
) -> None:
    from doomgate.game import assemble_soul_core_breaker as _a

    _a(GAME, state, log, acquired=acquired)


def can_exit(state: Dict[str, Any], room: Dict[str, Any], direction: str) -> bool:
    from doomgate.game import can_exit as _c

    return _c(state, room, direction)


def move(state: Dict[str, Any], log: ScrollLog, direction: str) -> None:
    from doomgate.game import move as _m

    _m(GAME, state, log, direction)


def resolve_object_action(
    state: Dict[str, Any],
    log: ScrollLog,
    obj_id: str,
    cmd: str,
    hotspot_kind: str,
    acquired: Optional[List[str]] = None,
) -> None:
    from doomgate.game import resolve_object_action as _r

    _r(GAME, state, log, obj_id, cmd, hotspot_kind, acquired=acquired)


# -----------------------------
# App
# -----------------------------


MIN_WINDOW_W, MIN_WINDOW_H = 800, 600
INITIAL_WINDOW_W, INITIAL_WINDOW_H = 1024, 768


def compute_layout(
    W: int,
    H: int,
    *,
    pad: int = 14,
    title_bar_h: int = 40,
) -> Dict[str, Any]:
    # Backwards-compatible shim; moved to doomgate.ui.layout.
    from doomgate.ui.layout import compute_layout as _c

    return _c(W, H, GAME["commands"], pad=pad, title_bar_h=title_bar_h)


def run() -> int:
    pygame.init()
    try:
        pygame.mixer.init()
    except Exception:
        pass
    pygame.display.set_caption(GAME["meta"]["title"])
    title_music_path = resolve_title_music_path()
    gameplay_music_path = resolve_gameplay_music_path()

    screen = pygame.display.set_mode((INITIAL_WINDOW_W, INITIAL_WINDOW_H), pygame.RESIZABLE)
    clock = pygame.time.Clock()

    colors = {
        "bg": (8, 10, 9),
        "panel": (18, 24, 21),
        "panel2": (14, 20, 17),
        "border": (34, 48, 40),
        "accent": (25, 255, 106),
        "accent_dim": (15, 181, 82),
        "text": (205, 221, 213),
        "muted": (124, 140, 131),
        "warn": (255, 211, 77),
        "dead": (255, 140, 140),
        "sys": (125, 255, 179),
        "title": (198, 255, 216),
        "danger_border": (130, 40, 40),
        "danger_bg": (20, 10, 10),
        "cmd_bg": (10, 14, 12),
        "cmd_active_bg": (18, 34, 26),
        "log_bg": (7, 11, 8),
        "log_bg_inner": (6, 10, 7),
        "log_border": (15, 26, 20),
        "log_text": (25, 255, 106),
        "log_dim": (18, 185, 90),
        "scroll_track": (24, 36, 30),
        "scroll_thumb": (65, 92, 80),
        "hotspot": (25, 255, 106, 26),
        "hotspot_border": (25, 255, 106, 120),
        "hotspot_hover": (25, 255, 106, 46),
    }

    font_ui = pygame.font.SysFont("consolas", 16)
    font_mono = pygame.font.SysFont("consolas", 15)
    font_small = pygame.font.SysFont("consolas", 13)
    title_fbig = pygame.font.SysFont("consolas", 44, bold=True)
    title_fmed = pygame.font.SysFont("consolas", 24)

    state = default_state()
    log = ScrollLog()

    def log_title(t: str) -> None:
        log.add(t, "title")

    def log_dim(t: str) -> None:
        log.add(t, "dim")

    def log_sys(t: str) -> None:
        log.add(t, "sys")

    def intro() -> None:
        log_title("DOOMGATE: THE WARLOCK'S CRUCIBLE")
        log_dim("A Shadowgate-style point-and-click survival adventure (Python/Pygame).")
        log.add(room_def(state["roomId"])["desc"])
        log_sys("Tip: SAVE often. Wrong choices can be terminal. (So can right ones, if you get cocky.)")

    def save_game() -> None:
        payload = json.dumps(state, indent=2)
        from doomgate.util.paths import writable_path

        path = writable_path(GAME["meta"]["saveFile"])
        with open(path, "w", encoding="utf-8") as f:
            f.write(payload)
        log_sys(f"Saved to {GAME['meta']['saveFile']}.")

    def load_game() -> None:
        nonlocal inv_scroll_px
        from doomgate.util.paths import writable_path

        path = writable_path(GAME["meta"]["saveFile"])
        if not os.path.exists(path):
            log.add("No save found.", "warn")
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            if not isinstance(loaded, dict):
                raise ValueError("Bad save")
            base = merge_loaded_save(GAME, loaded)
            state.clear()
            state.update(base)
            inv_scroll_px = 0
            log_sys("Loaded save.")
            log.add(room_def(state["roomId"])["desc"])
        except Exception:
            log.add("Save data is corrupted. (The file got possessed.)", "warn")

    def restart() -> None:
        nonlocal title_screen, intro_done, inv_scroll_px
        nonlocal music_vol_dragging, music_vol_hover_ms, music_vol_popup_visible
        state.clear()
        state.update(default_state())
        log.lines.clear()
        log.scroll_px = 0
        title_screen = False
        intro_done = False
        item_popup_queue.clear()
        nonlocal active_room_popup, active_manual_popup, active_linda_popup, hs_debug_drag, ui_layout_debug_drag
        active_room_popup = None
        active_manual_popup = None
        active_linda_popup = None
        hs_debug_drag = None
        ui_layout_debug_drag = None
        inv_scroll_px = 0
        music_vol_dragging = False
        music_vol_hover_ms = 0
        music_vol_popup_visible = False
        intro()
        intro_done = True
        state["seenRooms"][state["roomId"]] = True
        if not state.get("roomIntroShown", {}).get(state["roomId"], False) and room_def(state["roomId"]).get("enterText"):
            state.setdefault("roomIntroShown", {})[state["roomId"]] = True
            state["pendingRoomPopup"] = state["roomId"]
        bg_cache.clear()
        sprite_cache.clear()
        start_gameplay_music()

    title_screen = True
    intro_done = False
    item_popup_queue: List[str] = []
    active_room_popup: Optional[Dict[str, Any]] = None
    active_manual_popup: Optional[Dict[str, Any]] = None
    active_linda_popup: Optional[Dict[str, Any]] = None
    hs_debug_drag: Optional[Dict[str, Any]] = None
    inv_scroll_px = 0
    layout_state: Dict[str, Any] = {}
    item_thumb_cache: Dict[str, pygame.Surface] = {}
    debug_hotspots = False
    ui_layout_ov: Dict[str, Any] = load_ui_layout_overrides()
    debug_ui_layout = False
    ui_layout_debug_drag: Optional[Dict[str, Any]] = None
    gameplay_music_on = True
    _audio_loaded = load_audio_settings()
    music_volume = float(_audio_loaded["music_volume"])
    music_vol_dragging = False
    music_vol_hover_ms = 0
    music_vol_popup_visible = False

    def set_music_volume(vol: float) -> None:
        nonlocal music_volume
        music_volume = max(0.0, min(1.0, float(vol)))
        try:
            pygame.mixer.music.set_volume(music_volume)
        except Exception:
            pass
        save_audio_settings({"music_volume": music_volume})

    try:
        pygame.mixer.music.set_volume(music_volume)
    except Exception:
        pass

    ui_face_frames: List[pygame.Surface] = load_ui_player_face_frames()
    plasma_orb_frames: Dict[int, Optional[pygame.Surface]] = load_plasma_orb_frames()
    plasma_orb_decor: Optional[pygame.Surface] = load_plasma_orb_decor()

    def stop_title_menu_music() -> None:
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def start_title_menu_music() -> None:
        if not title_music_path:
            return
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
            pygame.mixer.music.load(title_music_path)
            pygame.mixer.music.set_volume(music_volume)
            pygame.mixer.music.play(loops=-1)
        except Exception:
            pass

    def stop_gameplay_music() -> None:
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def start_gameplay_music() -> None:
        if not gameplay_music_path or not gameplay_music_on:
            return
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
            pygame.mixer.music.load(gameplay_music_path)
            pygame.mixer.music.set_volume(music_volume)
            pygame.mixer.music.play(loops=-1)
        except Exception:
            pass

    def enter_game_from_title() -> None:
        nonlocal title_screen, intro_done
        stop_title_menu_music()
        start_gameplay_music()
        title_screen = False
        if not intro_done:
            intro()
            intro_done = True
            state["seenRooms"][state["roomId"]] = True
            if not state.get("roomIntroShown", {}).get(state["roomId"], False) and room_def(state["roomId"]).get("enterText"):
                state.setdefault("roomIntroShown", {})[state["roomId"]] = True
                state["pendingRoomPopup"] = state["roomId"]

    # Utility: minimap
    def draw_box(surf: pygame.Surface, r: pygame.Rect, title: str) -> None:
        pygame.draw.rect(surf, colors["panel2"], r, border_radius=10)
        pygame.draw.rect(surf, colors["border"], r, 1, border_radius=10)
        surf.blit(font_small.render(title, True, colors["text"]), (r.x + 10, r.y + 8))

    def draw_status() -> None:
        status_rect = layout_state["status_rect"]
        pygame.draw.rect(screen, (0, 0, 0), status_rect, border_radius=10)
        pygame.draw.rect(screen, colors["border"], status_rect, 1, border_radius=10)
        room_u = room_name_for_status_bar(room_def(state["roomId"])["name"]).upper()
        threat = (
            "DEAD"
            if not state["alive"]
            else (
                "SEALED"
                if get_flag(state, "gameWon")
                else ("DEBUG" if state.get("godMode") else ("CRITICAL" if state["lanterns"] <= 1 else "ACTIVE"))
            )
        )
        gap = 18
        inner_pad = 10
        max_line_w = max(40, status_rect.w - inner_pad * 2)
        prefix = "ROOM: "
        tail_chunks = [
            f"PLASMA LANTERN: {state['lanterns']}",
            f"ACTIONS: {state['actions']}",
            f"THREAT: {threat}",
        ]
        fixed_w = sum(font_small.size(c)[0] for c in tail_chunks) + gap * len(tail_chunks)
        max_room_segment_w = max_line_w - fixed_w
        room_fit = truncate_after_prefix_to_width(font_small, prefix, room_u, max_room_segment_w)
        chunks = [prefix + room_fit, *tail_chunks]
        x = status_rect.x + inner_pad
        for ch in chunks:
            if "THREAT:" in ch and threat == "CRITICAL":
                col = colors["warn"]
            elif "THREAT:" in ch and threat == "DEBUG":
                col = colors["accent_dim"]
            elif threat == "DEAD" and "THREAT:" in ch:
                col = colors["dead"]
            else:
                col = colors["muted"]
            screen.blit(font_small.render(ch, True, col), (x, status_rect.y + 6))
            x += font_small.size(ch)[0] + gap

    def current_cmd() -> str:
        return state["cmd"]

    def set_cmd(cmd: str, cmd_buttons: List[Button]) -> None:
        state["cmd"] = cmd
        for b in cmd_buttons:
            b.active = b.value == cmd

    def held_item_name() -> str:
        hid = state.get("heldItemId")
        return item_def(hid)["name"] if hid else "—"

    def draw_held() -> None:
        held_rect = layout_state["held_rect"]
        draw_box(screen, held_rect, "Held")
        cmd = current_cmd().upper()
        y_line = held_rect.y + 30
        cmd_surf = font_small.render(f"Command: {cmd}", True, colors["muted"])
        item_surf = font_small.render(f"Item: {held_item_name()}", True, colors["accent_dim"])
        screen.blit(cmd_surf, (held_rect.x + 10, y_line))
        item_x = held_rect.right - item_surf.get_width() - 10
        item_x = max(item_x, held_rect.x + 10 + cmd_surf.get_width() + 14)
        screen.blit(item_surf, (item_x, y_line))

    inv_buttons: List[Tuple[str, pygame.Rect]] = []

    def draw_inventory() -> None:
        nonlocal inv_buttons, inv_scroll_px
        inv_buttons = []
        inv_rect = layout_state["inv_rect"]
        draw_box(screen, inv_rect, "Inventory")
        items = state["inventory"]
        area = pygame.Rect(inv_rect.x + 10, inv_rect.y + 30, inv_rect.w - 20, inv_rect.h - 40)
        cols_i = 3
        bh = 28
        row_stride = bh + 8
        nrows = (len(items) + cols_i - 1) // cols_i if items else 0
        content_h = nrows * row_stride - 8 if nrows > 0 else 0
        max_scroll = max(0, content_h - area.h)
        inv_scroll_px = clamp(int(inv_scroll_px), 0, max_scroll)
        inner_w = area.w - (10 if max_scroll > 0 else 0)
        bw = (inner_w - 8 * (cols_i - 1)) // cols_i

        old_clip = screen.get_clip()
        screen.set_clip(area)
        try:
            for idx, iid in enumerate(items):
                r = idx // cols_i
                c = idx % cols_i
                row_y = area.y + r * row_stride - inv_scroll_px
                rect = pygame.Rect(area.x + c * (bw + 8), row_y, bw, bh)
                inv_buttons.append((iid, rect))
                if not rect.colliderect(area):
                    continue
                selected = state.get("heldItemId") == iid
                bg = (18, 34, 26) if selected else (10, 14, 12)
                border = colors["accent"] if selected else colors["border"]
                pygame.draw.rect(screen, bg, rect, border_radius=8)
                pygame.draw.rect(screen, border, rect, 1, border_radius=8)
                screen.blit(
                    font_small.render(item_def(iid)["name"][:18], True, colors["text"]),
                    (rect.x + 8, rect.y + 6),
                )
            if not items:
                screen.blit(font_small.render("(empty)", True, colors["muted"]), (area.x, area.y))
        finally:
            screen.set_clip(old_clip)
        if max_scroll > 0:
            track = pygame.Rect(area.right - 5, area.y, 4, area.h)
            pygame.draw.rect(screen, (30, 44, 38), track, border_radius=2)
            thumb_h = max(12, int(area.h * min(1.0, area.h / float(max(content_h, 1)))))
            prog = inv_scroll_px / float(max_scroll)
            ty = area.y + int((area.h - thumb_h) * prog)
            thumb = pygame.Rect(track.x, ty, 4, thumb_h)
            pygame.draw.rect(screen, (70, 120, 90), thumb, border_radius=2)

    def draw_minimap() -> None:
        map_rect = layout_state["map_rect"]
        draw_box(screen, map_rect, "Minimap")
        size = 5
        grid_area = pygame.Rect(map_rect.x + 10, map_rect.y + 28, map_rect.w - 20, map_rect.h - 32)
        gap = 4
        cell = min((grid_area.w - gap * (size - 1)) // size, (grid_area.h - gap * (size - 1)) // size)
        pos_to_room: Dict[Tuple[int, int], str] = {}
        centers: Dict[str, Tuple[int, int]] = {}
        rects: Dict[str, pygame.Rect] = {}
        for rid, r in GAME["rooms"].items():
            mp = r.get("mapPos")
            if mp and len(mp) == 2:
                pos_to_room[(mp[0], mp[1])] = rid
        here_id = state["roomId"]
        player_f = room_map_floor(room_def(here_id))

        for y in range(size):
            for x in range(size):
                rr = pygame.Rect(grid_area.x + x * (cell + gap), grid_area.y + y * (cell + gap), cell, cell)
                rid = pos_to_room.get((x, y))
                if rid:
                    centers[rid] = (rr.centerx, rr.centery)
                    rects[rid] = rr
                seen = rid and state["seenRooms"].get(rid, False)
                here = rid == here_id
                fl = room_map_floor(room_def(rid)) if rid else 0
                bg = (10, 14, 12)
                if seen and rid:
                    if fl == player_f:
                        bg = (210, 218, 214)
                    elif fl > player_f:
                        bg = (52, 28, 34)
                    else:
                        bg = (22, 30, 52)
                br = colors["border"]
                if seen:
                    br = (35, 90, 62) if (not rid or fl == player_f) else (70, 90, 110)
                pygame.draw.rect(screen, bg, rr, border_radius=6)
                pygame.draw.rect(screen, br, rr, 1, border_radius=6)
                if here:
                    pygame.draw.rect(screen, colors["warn"], rr, 2, border_radius=6)
                marker = "■" if seen and rid else "·"
                mk_col = colors["text"] if seen and rid else colors["muted"]
                if seen and rid and fl != player_f:
                    mk_col = (240, 230, 220) if fl > player_f else (200, 210, 235)
                screen.blit(font_small.render(marker, True, mk_col), (rr.centerx - 4, rr.centery - 8))

        pair_done: set[Tuple[str, str]] = set()
        for rid, room in GAME["rooms"].items():
            mp = room.get("mapPos")
            if not mp or len(mp) != 2:
                continue
            for dire, tid in room.get("exits", {}).items():
                key = tuple(sorted((rid, tid)))
                if key in pair_done:
                    continue
                pair_done.add(key)
                p0 = centers.get(rid)
                p1 = centers.get(tid)
                if not p0 or not p1:
                    continue
                f0 = room_map_floor(room_def(rid))
                f1 = room_map_floor(room_def(tid))
                is_vert_travel = dire in ("down", "up") or f0 != f1
                if is_vert_travel:
                    pygame.draw.line(screen, (100, 150, 210), p0, p1, 2)
                    mx = (p0[0] + p1[0]) // 2
                    my = (p0[1] + p1[1]) // 2
                    screen.blit(font_small.render("Δ", True, (160, 200, 245)), (mx - 3, my - 8))
                else:
                    pygame.draw.line(screen, (38, 72, 58), p0, p1, 1)

    # Hotspots are computed each frame from room data
    def get_hotspot_rects() -> List[Tuple[Dict[str, Any], pygame.Rect, bool]]:
        viewport_rect = layout_state["viewport_rect"]
        room = room_def(state["roomId"])
        out = []
        for hs in room.get("hotspots", []):
            disabled = False
            if hs["kind"] == "exit":
                target = room.get("exits", {}).get(hs.get("data", {}).get("dir"))
                if not target:
                    disabled = True
                if hs.get("data", {}).get("dir") == "north":
                    rules = room.get("rules", {})
                    gate = rules.get("gateToNorthRequiresFlag")
                    if gate and not get_flag(state, gate):
                        disabled = True
            r = rect_from_pct(hs["rect"]["l"], hs["rect"]["t"], hs["rect"]["w"], hs["rect"]["h"], viewport_rect)
            out.append((hs, r, disabled))
        return out

    def hs_debug_try_begin(pos: Tuple[int, int]) -> bool:
        nonlocal hs_debug_drag
        if not debug_hotspots:
            return False
        pairs = get_hotspot_rects()
        for hs, r, _disabled in reversed(pairs):
            hsz = max(6, min(HS_DEBUG_HANDLE_PX, r.w // 2, r.h // 2))
            handle = pygame.Rect(r.right - hsz, r.bottom - hsz, hsz, hsz)
            if not handle.colliderect(r):
                handle = pygame.Rect(r.right - min(hsz, r.w), r.bottom - min(hsz, r.h), min(hsz, r.w), min(hsz, r.h))
            if handle.collidepoint(pos):
                hs_debug_drag = {
                    "mode": "resize",
                    "hs": hs,
                    "w0": float(max(1, r.w)),
                    "h0": float(max(1, r.h)),
                    "tl": (float(r.x), float(r.y)),
                }
                return True
            c = hsz
            et = max(2, min(HS_DEBUG_EDGE_PX, r.w // 3, r.h // 3))
            inner_h = r.h - 2 * c
            inner_w = r.w - 2 * c
            if inner_h > 0:
                er = pygame.Rect(r.right - et, r.top + c, et, inner_h)
                if er.collidepoint(pos):
                    hs_debug_drag = {
                        "mode": "resize_e",
                        "hs": hs,
                        "l0": float(r.x),
                        "t0": float(r.y),
                        "h0": float(r.h),
                    }
                    return True
                el = pygame.Rect(r.x, r.top + c, et, inner_h)
                if el.collidepoint(pos):
                    hs_debug_drag = {
                        "mode": "resize_w",
                        "hs": hs,
                        "anchor_right": float(r.right),
                        "t0": float(r.y),
                        "h0": float(r.h),
                    }
                    return True
            if inner_w > 0:
                eb = pygame.Rect(r.left + c, r.bottom - et, inner_w, et)
                if eb.collidepoint(pos):
                    hs_debug_drag = {
                        "mode": "resize_s",
                        "hs": hs,
                        "l0": float(r.x),
                        "t0": float(r.y),
                        "w0": float(r.w),
                    }
                    return True
                et_top = pygame.Rect(r.left + c, r.y, inner_w, et)
                if et_top.collidepoint(pos):
                    hs_debug_drag = {
                        "mode": "resize_n",
                        "hs": hs,
                        "l0": float(r.x),
                        "w0": float(r.w),
                        "anchor_bottom": float(r.bottom),
                    }
                    return True
            if r.collidepoint(pos):
                hs_debug_drag = {
                    "mode": "move",
                    "hs": hs,
                    "grab": (float(pos[0] - r.x), float(pos[1] - r.y)),
                    "w": r.w,
                    "h": r.h,
                }
                return True
        return False

    def hs_debug_apply_motion(pos: Tuple[int, int]) -> None:
        d = hs_debug_drag
        if d is None:
            return
        vr = layout_state["viewport_rect"]
        hs = d["hs"]

        def rect_to_hs_pct(new_r: pygame.Rect) -> None:
            new_r.clamp_ip(vr)
            l, t, wp, hp = screen_rect_to_pct(new_r, vr)
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
            right_bound = max(vr.x, int(ar) - 4)
            nl = clamp(int(pos[0]), vr.x, right_bound)
            new_w = max(4, int(ar - nl))
            new_r = pygame.Rect(nl, int(d["t0"]), new_w, int(d["h0"]))
            rect_to_hs_pct(new_r)
        elif d["mode"] == "resize_n":
            ab = d["anchor_bottom"]
            bottom_bound = max(vr.y, int(ab) - 4)
            nt = clamp(int(pos[1]), vr.y, bottom_bound)
            new_h = max(4, int(ab - nt))
            new_r = pygame.Rect(int(d["l0"]), nt, int(d["w0"]), new_h)
            rect_to_hs_pct(new_r)

    def hs_debug_end_drag() -> None:
        nonlocal hs_debug_drag
        if hs_debug_drag is None:
            return
        hs = hs_debug_drag["hs"]
        rr = hs["rect"]
        log_sys(
            f'HOTSPOT {state["roomId"]}/{hs["id"]} rect: '
            f'{{"l": {rr["l"]:.2f}, "t": {rr["t"]:.2f}, "w": {rr["w"]:.2f}, "h": {rr["h"]:.2f}}}'
        )
        hs_debug_drag = None

    def ui_layout_parent_rect(region: str, ls: Dict[str, Any]) -> pygame.Rect:
        if region == "viewport":
            return ui_window_content_rect(ls["W"], ls["H"], ls["pad"], ls["title_bar_h"])
        if region in ("text_panel", "right_panel"):
            return ls["bottom_rect"]
        if region in ("status", "log"):
            return ls["text_panel"]
        return ls["right_panel"]

    def ui_layout_debug_try_begin(pos: Tuple[int, int]) -> bool:
        nonlocal ui_layout_debug_drag
        if not debug_ui_layout:
            return False
        right_children = ("cmd_rect", "inv_rect", "map_rect", "held_rect")
        for region_key, lay_key, _col in UI_EDIT_REGION_ORDER:
            r = layout_state[lay_key]
            if region_key == "right_panel":
                if not r.collidepoint(pos):
                    continue
                if any(layout_state[k].collidepoint(pos) for k in right_children):
                    continue
            elif not r.collidepoint(pos):
                continue
            payload = ui_resize_handles_try_begin(r, pos)
            if payload:
                ui_layout_debug_drag = {"region": region_key, "lay_key": lay_key, **payload}
                return True
        return False

    def ui_layout_debug_apply_motion(pos: Tuple[int, int]) -> None:
        d = ui_layout_debug_drag
        if d is None:
            return
        region = str(d["region"])
        parent = ui_layout_parent_rect(region, layout_state)
        min_w, min_h = UI_EDIT_REGION_MINS[region]
        new_r = ui_resize_handles_apply_motion(pos, d, parent, min_w, min_h)
        ui_layout_ov.setdefault("regions", {})
        ui_layout_ov["regions"][region] = ui_rect_to_dict(new_r)

    def ui_layout_debug_end_drag() -> None:
        nonlocal ui_layout_debug_drag
        if ui_layout_debug_drag is None:
            return
        d = ui_layout_debug_drag
        rk = str(d.get("region", ""))
        rr = ui_layout_ov.get("regions", {}).get(rk)
        log_sys(f"UI layout {rk} ({d.get('mode')}): {rr}")
        ui_layout_debug_drag = None

    def draw_ui_layout_debug_overlay() -> None:
        if not debug_ui_layout:
            return
        for _rk, lay_key, col in UI_EDIT_REGION_ORDER:
            r = layout_state[lay_key]
            dbg = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
            dbg.fill((*col, 26))
            screen.blit(dbg, r.topleft)
            pygame.draw.rect(screen, col, r, 1, border_radius=6)
            hsz = max(6, min(UI_DEBUG_HANDLE_PX, r.w // 2, r.h // 2))
            h_r = pygame.Rect(r.right - hsz, r.bottom - hsz, hsz, hsz)
            pygame.draw.rect(screen, (255, 255, 220), h_r, width=2, border_radius=2)

    def do_hotspot_click(hs: Dict[str, Any]) -> None:
        cmd = current_cmd()
        if cmd == "save":
            save_game()
            return
        if cmd == "load":
            load_game()
            return
        if not state["alive"]:
            log.add("You're dead. The facility requires you to stop being dead first. (Restart or Load.)", "warn")
            return
        if hs["kind"] == "exit":
            if cmd != "use":
                log.add("Select USE, then click the door or passage to go through. No free movement—this is an adventure game.", "warn")
                apply_action(state, "interact", log)
                return
            move(state, log, hs["data"]["dir"])
            return
        acquired: List[str] = []
        resolve_object_action(state, log, hs["id"], cmd, hs["kind"], acquired=acquired)
        for gid in acquired:
            item_popup_queue.append(gid)

    def open_manual() -> None:
        nonlocal active_manual_popup
        if active_manual_popup is not None:
            return
        active_manual_popup = {"scroll": 0}

    def load_item_preview(item_id: str, max_side: int = 140) -> pygame.Surface:
        if item_id not in item_thumb_cache:
            path = os.path.join(ITEMS_DIR, f"{item_id}.png")
            loaded = try_load_png(path)
            if loaded is not None:
                s = max(loaded.get_width(), loaded.get_height())
                scale = max_side / max(1, s)
                w = max(1, int(loaded.get_width() * scale))
                h = max(1, int(loaded.get_height() * scale))
                item_thumb_cache[item_id] = pygame.transform.scale(loaded, (w, h))
            else:
                thumb = pygame.Surface((max_side, max_side), pygame.SRCALPHA)
                thumb.fill((20, 28, 24, 255))
                pygame.draw.rect(thumb, colors["accent_dim"], thumb.get_rect(), width=2)
                t = font_small.render(item_def(item_id)["name"][:12], True, colors["text"])
                thumb.blit(t, t.get_rect(center=(max_side // 2, max_side // 2)))
                item_thumb_cache[item_id] = thumb.convert_alpha()
        return item_thumb_cache[item_id]

    def draw_item_acquire_popup(item_id: str) -> None:
        W, H = screen.get_size()
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 210))
        screen.blit(overlay, (0, 0))
        panel_w = min(420, W - 40)
        panel_h = min(320, H - 40)
        panel = pygame.Rect((W - panel_w) // 2, (H - panel_h) // 2, panel_w, panel_h)
        pygame.draw.rect(screen, colors["panel"], panel, border_radius=14)
        pygame.draw.rect(screen, colors["accent_dim"], panel, width=2, border_radius=14)
        it = item_def(item_id)
        title_s = font_ui.render(it["name"], True, colors["title"])
        screen.blit(title_s, (panel.x + 20, panel.y + 16))
        img = load_item_preview(item_id, max_side=min(160, panel_h - 120))
        ix = panel.x + (panel.w - img.get_width()) // 2
        screen.blit(img, (ix, panel.y + 48))
        body_font = font_mono
        desc_lines = wrap_text_lines(body_font, it.get("desc", ""), panel.w - 40)
        y = panel.y + 52 + img.get_height() + 10
        for line in desc_lines[:6]:
            screen.blit(body_font.render(line, True, colors["log_text"]), (panel.x + 20, y))
            y += body_font.get_linesize()
        prompt = font_small.render("Click or press any key to continue", True, colors["warn"])
        screen.blit(prompt, prompt.get_rect(center=(panel.centerx, panel.bottom - 28)))

    def draw_manual_popup(popup: Dict[str, Any]) -> None:
        W, H = screen.get_size()
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 130))
        screen.blit(overlay, (0, 0))

        panel_w = min(680, W - 60)
        panel_h = min(420, H - 60)
        panel = pygame.Rect((W - panel_w) // 2, (H - panel_h) // 2, panel_w, panel_h)

        pygame.draw.rect(screen, (0, 0, 0), panel, border_radius=10)
        pygame.draw.rect(screen, colors["accent"], panel, width=2, border_radius=10)

        title_s = font_mono.render("UAC FIELD MANUAL", True, colors["accent"])
        screen.blit(title_s, (panel.x + 18, panel.y + 14))

        inner = pygame.Rect(panel.x + 16, panel.y + 44, panel.w - 32, panel.h - 84)
        pygame.draw.rect(screen, (0, 0, 0), inner)

        inner_w = max(40, inner.w - 4)
        lines: List[str] = []
        for para in GAME["manualText"].split("\n"):
            if para == "":
                lines.append("")
            else:
                lines.extend(wrap_text_lines(font_mono, para, inner_w))

        lh = font_mono.get_linesize()
        visible = max(1, int((inner.h - 10) // lh))
        max_scroll = max(0, len(lines) - visible)
        scroll = clamp(int(popup.get("scroll", 0)), 0, max_scroll)
        popup["scroll"] = scroll

        y = inner.y + 6
        for i in range(scroll, min(len(lines), scroll + visible)):
            screen.blit(font_mono.render(lines[i], True, colors["accent"]), (inner.x + 2, y))
            y += lh

        hint = "↑↓ SCROLL  ·  CLICK OR KEY TO CLOSE"
        if max_scroll > 0:
            lo = scroll + 1
            hi = min(scroll + visible, len(lines))
            hint = f"LINES {lo}-{hi} / {len(lines)}  ·  " + hint
        prompt = font_small.render(hint, True, colors["warn"])
        screen.blit(prompt, prompt.get_rect(center=(panel.centerx, panel.bottom - 22)))

    def draw_room_intro_popup(popup: Dict[str, Any]) -> None:
        W, H = screen.get_size()
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 130))
        screen.blit(overlay, (0, 0))

        room_id = popup["roomId"]
        full_text: str = popup["text"]
        shown: str = full_text[: int(popup.get("idx", 0))]

        panel_w = min(680, W - 60)
        panel_h = min(380, H - 60)
        panel = pygame.Rect((W - panel_w) // 2, (H - panel_h) // 2, panel_w, panel_h)

        # Terminal look: black glass + green border
        pygame.draw.rect(screen, (0, 0, 0), panel, border_radius=10)
        pygame.draw.rect(screen, colors["accent"], panel, width=2, border_radius=10)

        title = room_def(room_id).get("name", room_id).upper()
        title_s = font_mono.render(title, True, colors["accent"])
        screen.blit(title_s, (panel.x + 18, panel.y + 14))

        inner = pygame.Rect(panel.x + 16, panel.y + 44, panel.w - 32, panel.h - 84)
        pygame.draw.rect(screen, (0, 0, 0), inner)

        body_font = font_mono
        lines = wrap_text_lines(body_font, shown, inner.w - 4)
        y = inner.y + 6
        max_lines = max(1, int((inner.h - 10) / body_font.get_linesize()))
        for line in lines[-max_lines:]:
            screen.blit(body_font.render(line, True, colors["accent"]), (inner.x + 2, y))
            y += body_font.get_linesize()

        done = bool(popup.get("done", False))
        prompt_txt = "CLICK TO CLOSE" if done else "CLICK TO SKIP"
        prompt = font_small.render(prompt_txt, True, colors["warn"])
        screen.blit(prompt, prompt.get_rect(center=(panel.centerx, panel.bottom - 22)))

    def draw_linda_popup(popup: Dict[str, Any]) -> None:
        W, H = screen.get_size()
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 130))
        screen.blit(overlay, (0, 0))

        panel_w = min(680, W - 60)
        panel_h = min(420, H - 60)
        panel = pygame.Rect((W - panel_w) // 2, (H - panel_h) // 2, panel_w, panel_h)
        pygame.draw.rect(screen, (0, 0, 0), panel, border_radius=10)
        pygame.draw.rect(screen, colors["accent"], panel, width=2, border_radius=10)

        title_s = font_mono.render("L.I.N.D.A. — ACCESS", True, colors["accent"])
        screen.blit(title_s, (panel.x + 18, panel.y + 14))

        inner = pygame.Rect(panel.x + 16, panel.y + 44, panel.w - 32, panel.h - 96)
        pygame.draw.rect(screen, (0, 0, 0), inner)

        full_text: str = popup["full_text"]
        shown: str = full_text[: int(popup.get("idx", 0))]
        body_font = font_mono
        lines = wrap_text_lines(body_font, shown, inner.w - 4)
        y = inner.y + 6
        lh = body_font.get_linesize()
        max_lines = max(1, int((inner.h - 70) / lh))
        for line in lines[-max_lines:]:
            screen.blit(body_font.render(line, True, colors["accent"]), (inner.x + 2, y))
            y += lh

        if popup.get("phase") == "entry":
            inp = str(popup.get("input", ""))
            blink = (pygame.time.get_ticks() // 520) % 2
            prompt_line = "> " + inp + ("█" if blink else "")
            screen.blit(body_font.render(prompt_line, True, colors["warn"]), (inner.x + 2, inner.bottom - 44))
            hint = font_small.render("ENTER — submit   ESC / Q — close (Q if code field empty)", True, colors["muted"])
            screen.blit(hint, (panel.x + 18, panel.bottom - 26))

    def launch_rbyt3r_minigame() -> None:
        """Run RBYT3R Epoch in a subprocess so DoomGate state and pygame stay intact."""
        here = os.path.dirname(os.path.abspath(__file__))
        env_path = os.environ.get("RBYT3R_EPOCH_PATH", "").strip()
        candidates: List[str] = []
        if env_path:
            candidates.append(env_path)
        candidates.extend(
            [
                os.path.join(here, "assets", "minigame", "rbyt3rEpoch_theGame"),
                os.path.join(here, "rbyt3rEpoch_theGame"),
                os.path.normpath(os.path.join(here, "..", "rbyt3rEpoch_theGame")),
            ]
        )
        repo_root: Optional[str] = None
        for c in candidates:
            if c and os.path.isdir(os.path.join(c, "rbyt3r_epoch")):
                repo_root = c
                break
        if repo_root is None:
            log.add(
                "RBYT3R Epoch not found. Expected assets/minigame/rbyt3rEpoch_theGame (or set RBYT3R_EPOCH_PATH), "
                "then enter STONKS again.",
                "warn",
            )
            return
        try:
            subprocess.run([sys.executable, "-m", "rbyt3r_epoch"], cwd=repo_root, check=False)
        except OSError as exc:
            log.add(f"Could not launch RBYT3R Epoch: {exc}", "warn")

    def submit_linda_code() -> None:
        nonlocal active_linda_popup
        if active_linda_popup is None or active_linda_popup.get("phase") != "entry":
            return
        raw = str(active_linda_popup.get("input", ""))
        code = raw.strip().lower()
        codes = GAME.get("lindaTerminalCodes") or {}
        entry = codes.get(code)
        try:
            pygame.key.stop_text_input()
        except Exception:
            pass
        if entry is not None:
            action = entry.get("action") if isinstance(entry, dict) else entry
            state["lindaWrongCount"] = 0
            active_linda_popup = None
            if action == "minigame_rbyt3r":
                launch_rbyt3r_minigame()
            elif action == "god_mode":
                enable_god_mode(state, log)
            return
        state["lindaWrongCount"] = int(state.get("lindaWrongCount", 0)) + 1
        if state["lindaWrongCount"] >= 3:
            active_linda_popup = None
            die(state, log, GAME["deaths"]["terminalOverload"])
            return
        apply_action(state, "interact", log)
        log.add("Proceed at your own risk!", "warn")
        active_linda_popup["full_text"] = "Proceed at your own risk!\n\nENTER CODE:\n\n"
        active_linda_popup["idx"] = 0
        active_linda_popup["done"] = False
        active_linda_popup["phase"] = "typewriter"
        active_linda_popup["input"] = ""
        active_linda_popup["acc_ms"] = 0

    # Cache loaded title art; retry periodically if missing so files can appear without restart.
    title_bg_cached: Optional[pygame.Surface] = None
    title_bg_miss_cooldown: int = 0

    def get_title_screen_image() -> Optional[pygame.Surface]:
        nonlocal title_bg_cached, title_bg_miss_cooldown
        if title_bg_cached is not None:
            return title_bg_cached
        if title_bg_miss_cooldown > 0:
            title_bg_miss_cooldown -= 1
            return None
        surf = load_title_background_image()
        if surf is not None:
            title_bg_cached = surf
            return surf
        title_bg_miss_cooldown = 30
        return None

    title_bg_cached = load_title_background_image()

    def draw_title_scr() -> None:
        W, H = screen.get_size()
        src = get_title_screen_image()
        if src is not None:
            screen.blit(scale_image_cover(src, W, H), (0, 0))
        else:
            screen.fill(colors["bg"])

        rows: List[Tuple[pygame.font.Font, str, Tuple[int, int, int]]] = [
            (title_fbig, "DOOMGATE", (240, 255, 245)),
            (title_fmed, "THE WARLOCK'S CRUCIBLE", (210, 235, 220)),
            (title_fmed, "Press Any Key to RIP AND TEAR!", colors["warn"]),
            (font_small, "Mouse click also works · ESC quits", (200, 220, 210)),
        ]
        rendered = [f.render(t, True, c) for f, t, c in rows]
        gaps = (10, 16, 14)
        pad_x, pad_y = 36, 30
        max_line_w = max(s.get_width() for s in rendered)
        total_h = pad_y * 2 + sum(s.get_height() for s in rendered) + sum(gaps)
        total_w = max_line_w + pad_x * 2
        px = (W - total_w) // 2
        py = (H - total_h) // 2

        panel = pygame.Surface((total_w, total_h), pygame.SRCALPHA)
        pr = panel.get_rect()
        pygame.draw.rect(panel, (6, 10, 9, 200), pr, border_radius=18)
        pygame.draw.rect(panel, (40, 58, 48, 230), pr, width=2, border_radius=18)
        screen.blit(panel, (px, py))

        y = int(py + pad_y)
        for i, surf in enumerate(rendered):
            x = int(px + (total_w - surf.get_width()) // 2)
            screen.blit(surf, (x, y))
            if i < len(gaps):
                y += surf.get_height() + gaps[i]

    # Background cache per room (prefer external art) + per theme fallback
    bg_cache: Dict[Tuple[str, int, int], pygame.Surface] = {}
    bg_fallback_cache: Dict[Tuple[str, int, int], pygame.Surface] = {}
    # Sprite cache per hotspot id/kind/theme (prefer external sprites)
    sprite_cache: Dict[Tuple[Any, ...], pygame.Surface] = {}

    hovering_hotspot: Optional[str] = None
    inv_buttons: List[Tuple[str, pygame.Rect]] = []

    if title_screen:
        start_title_menu_music()

    running = True
    while running:
        dt_ms = clock.tick(60)
        mx, my = pygame.mouse.get_pos()
        lay = compute_layout(*screen.get_size())
        apply_ui_layout_overrides(lay, ui_layout_ov)
        layout_state.clear()
        layout_state.update(lay)
        pad = lay["pad"]
        viewport_rect = lay["viewport_rect"]
        log_rect = lay["log_rect"]
        text_panel = lay["text_panel"]
        right_panel = lay["right_panel"]
        status_rect = lay["status_rect"]

        cmd_buttons: List[Button] = []
        for cid, clabel, r in lay["cmd_button_rects"]:
            cmd_buttons.append(Button(r, clabel, cid, active=(cid == state["cmd"])))
        manual_btn = Button(lay["manual_btn_rect"], "MANUAL", "manual")
        music_lbl = "MUSIC ON" if gameplay_music_on else "MUSIC OFF"
        music_btn = Button(lay["music_btn_rect"], music_lbl, "music_toggle")
        restart_btn = Button(lay["restart_btn_rect"], "RESTART", "restart", danger=True)

        if not title_screen:
            on_save_load = any(
                b.rect.collidepoint((mx, my)) for b in cmd_buttons if b.value in ("save", "load")
            )
            _vpr_hover = music_vol_popup_rect(music_btn.rect, lay)
            if on_save_load:
                music_vol_hover_ms = 0
                if not music_vol_dragging:
                    music_vol_popup_visible = False
            elif music_btn.rect.collidepoint((mx, my)):
                music_vol_hover_ms = min(music_vol_hover_ms + int(dt_ms), MUSIC_VOL_HOVER_DELAY_MS * 3)
                if music_vol_hover_ms >= MUSIC_VOL_HOVER_DELAY_MS:
                    music_vol_popup_visible = True
            elif music_vol_popup_visible and _vpr_hover.collidepoint((mx, my)):
                pass
            elif music_vol_dragging:
                music_vol_popup_visible = True
            else:
                music_vol_hover_ms = 0
                if not music_vol_dragging:
                    music_vol_popup_visible = False
        else:
            music_vol_hover_ms = 0
            music_vol_popup_visible = False

        # Activate pending room popup (first-visit flavor text)
        if (
            active_room_popup is None
            and active_manual_popup is None
            and not title_screen
            and not item_popup_queue
            and isinstance(state.get("pendingRoomPopup"), str)
            and room_def(state["pendingRoomPopup"]).get("enterText")
        ):
            rid = state["pendingRoomPopup"]
            full = room_def(rid).get("enterText", "")
            active_room_popup = {"roomId": rid, "text": full, "idx": 0, "done": False, "acc_ms": 0}
            state["pendingRoomPopup"] = None

        if (
            active_linda_popup is None
            and state.get("pendingLindaTerminal")
            and not title_screen
            and active_manual_popup is None
            and active_room_popup is None
            and not item_popup_queue
        ):
            wc = int(state.get("lindaWrongCount", 0))
            ft = "ENTER CODE:\n\n" if wc <= 0 else "Proceed at your own risk!\n\nENTER CODE:\n\n"
            active_linda_popup = {
                "full_text": ft,
                "idx": 0,
                "done": False,
                "phase": "typewriter",
                "input": "",
                "acc_ms": 0,
            }
            state["pendingLindaTerminal"] = False

        # Typewriter effect update
        if active_room_popup is not None and not active_room_popup.get("done", False):
            active_room_popup["acc_ms"] = int(active_room_popup.get("acc_ms", 0)) + int(dt_ms)
            cps = 45  # characters per second
            step_ms = max(1, int(1000 / cps))
            while active_room_popup["acc_ms"] >= step_ms and not active_room_popup.get("done", False):
                active_room_popup["acc_ms"] -= step_ms
                active_room_popup["idx"] = int(active_room_popup.get("idx", 0)) + 1
                if active_room_popup["idx"] >= len(active_room_popup["text"]):
                    active_room_popup["idx"] = len(active_room_popup["text"])
                    active_room_popup["done"] = True

        if active_linda_popup is not None and active_linda_popup.get("phase") == "typewriter" and not active_linda_popup.get("done", False):
            active_linda_popup["acc_ms"] = int(active_linda_popup.get("acc_ms", 0)) + int(dt_ms)
            cps = 45
            step_ms = max(1, int(1000 / cps))
            ft = active_linda_popup["full_text"]
            while active_linda_popup["acc_ms"] >= step_ms and not active_linda_popup.get("done", False):
                active_linda_popup["acc_ms"] -= step_ms
                active_linda_popup["idx"] = int(active_linda_popup.get("idx", 0)) + 1
                if active_linda_popup["idx"] >= len(ft):
                    active_linda_popup["idx"] = len(ft)
                    active_linda_popup["done"] = True
                    active_linda_popup["phase"] = "entry"
                    try:
                        pygame.key.start_text_input()
                    except Exception:
                        pass

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                nw = max(MIN_WINDOW_W, event.w)
                nh = max(MIN_WINDOW_H, event.h)
                screen = pygame.display.set_mode((nw, nh), pygame.RESIZABLE)
                bg_cache.clear()
                sprite_cache.clear()
                bg_fallback_cache.clear()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if active_linda_popup is not None:
                    active_linda_popup = None
                    try:
                        pygame.key.stop_text_input()
                    except Exception:
                        pass
                elif active_room_popup is not None:
                    active_room_popup = None
                elif active_manual_popup is not None:
                    active_manual_popup = None
                elif item_popup_queue:
                    item_popup_queue.pop(0)
                else:
                    running = False
            elif active_linda_popup is not None:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q and not str(active_linda_popup.get("input", "")).strip():
                        active_linda_popup = None
                        try:
                            pygame.key.stop_text_input()
                        except Exception:
                            pass
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        submit_linda_code()
                    elif event.key == pygame.K_BACKSPACE:
                        if active_linda_popup.get("phase") == "entry":
                            s = str(active_linda_popup.get("input", ""))
                            active_linda_popup["input"] = s[:-1]
                elif event.type == pygame.TEXTINPUT:
                    if active_linda_popup.get("phase") == "entry":
                        t = getattr(event, "text", "") or ""
                        if t:
                            active_linda_popup["input"] = str(active_linda_popup.get("input", "")) + t
                elif event.type == pygame.MOUSEBUTTONDOWN and getattr(event, "button", 0) == 1:
                    if active_linda_popup.get("phase") == "typewriter":
                        ft = active_linda_popup["full_text"]
                        if not active_linda_popup.get("done", False):
                            active_linda_popup["idx"] = len(ft)
                            active_linda_popup["done"] = True
                            active_linda_popup["phase"] = "entry"
                            try:
                                pygame.key.start_text_input()
                            except Exception:
                                pass
                else:
                    pass
            elif active_room_popup is not None:
                # While visible: swallow all input so the room can't be interacted with.
                if event.type == pygame.MOUSEBUTTONDOWN and getattr(event, "button", 0) == 1:
                    if not active_room_popup.get("done", False):
                        active_room_popup["idx"] = len(active_room_popup["text"])
                        active_room_popup["done"] = True
                    else:
                        active_room_popup = None
                elif event.type == pygame.KEYDOWN:
                    if not active_room_popup.get("done", False):
                        active_room_popup["idx"] = len(active_room_popup["text"])
                        active_room_popup["done"] = True
                    else:
                        active_room_popup = None
                else:
                    # Ignore any other events (wheel, resize handled above, etc.)
                    pass
            elif active_manual_popup is not None:
                if event.type == pygame.MOUSEWHEEL:
                    cur = int(active_manual_popup.get("scroll", 0))
                    active_manual_popup["scroll"] = cur - event.y
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        active_manual_popup["scroll"] = int(active_manual_popup.get("scroll", 0)) - 1
                    elif event.key == pygame.K_DOWN:
                        active_manual_popup["scroll"] = int(active_manual_popup.get("scroll", 0)) + 1
                    else:
                        active_manual_popup = None
                elif event.type == pygame.MOUSEBUTTONDOWN and getattr(event, "button", 0) == 1:
                    active_manual_popup = None
                else:
                    pass
            elif item_popup_queue:
                if event.type == pygame.KEYDOWN or (
                    event.type == pygame.MOUSEBUTTONDOWN and getattr(event, "button", 0) == 1
                ):
                    item_popup_queue.pop(0)
            elif title_screen:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    enter_game_from_title()
                elif event.type == pygame.KEYDOWN and event.key != pygame.K_ESCAPE:
                    enter_game_from_title()
            elif event.type == pygame.MOUSEWHEEL:
                inv_r = layout_state.get("inv_rect")
                if (
                    inv_r
                    and inv_r.collidepoint(mx, my)
                    and not title_screen
                    and active_room_popup is None
                    and active_linda_popup is None
                    and active_manual_popup is None
                    and not item_popup_queue
                ):
                    inv_scroll_px -= event.y * 36
                elif log_rect.collidepoint(mx, my):
                    log.wheel(event.y)
            elif event.type == pygame.MOUSEMOTION:
                if (
                    music_vol_dragging
                    and pygame.mouse.get_pressed()[0]
                    and not title_screen
                    and music_vol_popup_visible
                ):
                    vpr = music_vol_popup_rect(music_btn.rect, lay)
                    tin = music_vol_track_inner(vpr)
                    set_music_volume(music_volume_from_track_x(tin, event.pos[0]))
                elif (
                    debug_hotspots
                    and hs_debug_drag is not None
                    and pygame.mouse.get_pressed()[0]
                    and not title_screen
                    and active_room_popup is None
                    and active_linda_popup is None
                    and active_manual_popup is None
                    and not item_popup_queue
                ):
                    hs_debug_apply_motion(event.pos)
                elif (
                    debug_ui_layout
                    and ui_layout_debug_drag is not None
                    and pygame.mouse.get_pressed()[0]
                    and not title_screen
                    and active_room_popup is None
                    and active_linda_popup is None
                    and active_manual_popup is None
                    and not item_popup_queue
                ):
                    ui_layout_debug_apply_motion(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if music_vol_dragging:
                    music_vol_dragging = False
                elif (
                    ui_layout_debug_drag is not None
                    and not title_screen
                    and active_room_popup is None
                    and active_linda_popup is None
                ):
                    ui_layout_debug_end_drag()
                elif (
                    hs_debug_drag is not None
                    and not title_screen
                    and active_room_popup is None
                    and active_linda_popup is None
                ):
                    hs_debug_end_drag()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if (
                    debug_ui_layout
                    and not title_screen
                    and active_room_popup is None
                    and active_linda_popup is None
                    and active_manual_popup is None
                    and not item_popup_queue
                    and ui_layout_debug_try_begin(event.pos)
                ):
                    continue
                for b in cmd_buttons:
                    if b.rect.collidepoint(event.pos):
                        if b.value == "save":
                            save_game()
                            apply_action(state, "system", log)
                        elif b.value == "load":
                            load_game()
                            apply_action(state, "system", log)
                        else:
                            set_cmd(b.value, cmd_buttons)
                            apply_action(state, "inventory", log)
                        break
                else:
                    if manual_btn.rect.collidepoint(event.pos):
                        open_manual()
                        apply_action(state, "system", log)
                        continue
                    if not title_screen and music_vol_popup_visible:
                        vpr = music_vol_popup_rect(music_btn.rect, lay)
                        if vpr.collidepoint(event.pos):
                            music_vol_dragging = True
                            tin = music_vol_track_inner(vpr)
                            set_music_volume(music_volume_from_track_x(tin, event.pos[0]))
                            apply_action(state, "system", log)
                            continue
                    if music_btn.rect.collidepoint(event.pos):
                        gameplay_music_on = not gameplay_music_on
                        if gameplay_music_on:
                            start_gameplay_music()
                        else:
                            stop_gameplay_music()
                        apply_action(state, "system", log)
                        continue
                    if restart_btn.rect.collidepoint(event.pos):
                        restart()
                        apply_action(state, "system", log)
                        continue

                    clicked_inv = False
                    for iid, r in inv_buttons:
                        if r.collidepoint(event.pos):
                            clicked_inv = True
                            if not state["alive"]:
                                break
                            acquired_inv: List[str] = []
                            if state["cmd"] == "use" and state.get("heldItemId") and state["heldItemId"] != iid:
                                ok = try_combination(state, log, state["heldItemId"], iid, acquired=acquired_inv)
                                for gid in acquired_inv:
                                    item_popup_queue.append(gid)
                                if not ok:
                                    log.add("Those items refuse to cooperate. Probably for ethical reasons.", "warn")
                                    apply_action(state, "interact", log)
                                break
                            if state["cmd"] == "use" and state.get("heldItemId") == iid:
                                if iid == "soulCoreFrame":
                                    had_breaker = has_item(state, "soulCoreBreaker")
                                    try_combination(state, log, iid, iid, acquired=acquired_inv)
                                    if not had_breaker and has_item(state, "soulCoreBreaker"):
                                        for gid in acquired_inv:
                                            item_popup_queue.append(gid)
                                    else:
                                        state["heldItemId"] = None
                                    break
                                ok_self = try_combination(state, log, iid, iid, acquired=acquired_inv)
                                for gid in acquired_inv:
                                    item_popup_queue.append(gid)
                                if not ok_self:
                                    state["heldItemId"] = None
                                    apply_action(state, "inventory", log)
                                break
                            state["heldItemId"] = None if state.get("heldItemId") == iid else iid
                            apply_action(state, "inventory", log)
                            break
                    if clicked_inv:
                        continue

                    if viewport_rect.collidepoint(event.pos):
                        if (
                            debug_hotspots
                            and not title_screen
                            and active_room_popup is None
                            and active_linda_popup is None
                            and active_manual_popup is None
                            and not item_popup_queue
                            and hs_debug_try_begin(event.pos)
                        ):
                            continue
                        if not debug_hotspots:
                            for hs, r, disabled in get_hotspot_rects():
                                if disabled:
                                    continue
                                if r.collidepoint(event.pos):
                                    do_hotspot_click(hs)
                                    break

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
                if (
                    not title_screen
                    and not item_popup_queue
                    and active_room_popup is None
                    and active_manual_popup is None
                    and active_linda_popup is None
                ):
                    if not HOTSPOT_DEBUG_F3_FOR_EVERYONE and not state.get("hotspotDebugUnlocked"):
                        log.add("Hotspot layout mode is locked.", "dim")
                    else:
                        debug_hotspots = not debug_hotspots
                        if not debug_hotspots:
                            hs_debug_drag = None
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F4:
                if (
                    debug_hotspots
                    and not title_screen
                    and not item_popup_queue
                    and active_room_popup is None
                    and active_manual_popup is None
                    and active_linda_popup is None
                ):
                    ok, msg = save_hotspot_layout_to_disk(GAME)
                    if ok:
                        log_sys(f"Hotspot layout saved to {os.path.basename(msg)} (loaded on next game start).")
                    else:
                        log_sys(f"Hotspot layout save failed: {msg}")
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F5:
                if (
                    not title_screen
                    and not item_popup_queue
                    and active_room_popup is None
                    and active_manual_popup is None
                    and active_linda_popup is None
                ):
                    if not UI_LAYOUT_DEBUG_F5_FOR_EVERYONE and not state.get("uiLayoutDebugUnlocked"):
                        log.add("UI layout mode is locked.", "dim")
                    else:
                        debug_ui_layout = not debug_ui_layout
                        if debug_ui_layout:
                            log_sys(
                                "UI layout: all tinted panels — move body, edges = axis resize, corner = uniform scale "
                                "(same as F3). Right column empty stripe = right_panel. F6 saves ui_layout.json."
                            )
                        else:
                            ui_layout_debug_drag = None
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F6:
                if (
                    debug_ui_layout
                    and not title_screen
                    and not item_popup_queue
                    and active_room_popup is None
                    and active_manual_popup is None
                    and active_linda_popup is None
                ):
                    sync_ui_layout_overrides_from_lay(layout_state, ui_layout_ov)
                    ok, msg = save_ui_layout_overrides(ui_layout_ov)
                    if ok:
                        log_sys(f"UI layout saved to {os.path.basename(msg)} (loaded on next game start).")
                    else:
                        log_sys(f"UI layout save failed: {msg}")

        if title_screen:
            draw_title_scr()
            pygame.display.flip()
            continue

        if active_room_popup is not None or active_linda_popup is not None:
            # Freeze world interaction while popup is present, but still render the room underneath.
            pass

        # Draw background
        screen.fill(colors["bg"])
        title = font_ui.render(GAME["meta"]["title"], True, colors["text"])
        screen.blit(title, (pad, pad))
        subtitle = font_small.render(
            "Shadowgate • Mouse-only • F3/F4: hotspot layout • F5/F6: UI layout (minimap + Held)",
            True,
            colors["muted"],
        )
        screen.blit(subtitle, (pad + 2, pad + 18))

        room_id = state["roomId"]
        theme = room_def(room_id).get("theme", "corridor")
        bg_key = (room_id, viewport_rect.w, viewport_rect.h)
        bg = bg_cache.get(bg_key)
        if bg is None:
            bg_path = os.path.join(ROOMS_DIR, f"{room_id}.png")
            loaded = try_load_png(bg_path)
            if loaded is not None:
                bg = pygame.transform.smoothscale(loaded, (viewport_rect.w, viewport_rect.h))
            else:
                fb_key = (theme, viewport_rect.w, viewport_rect.h)
                if fb_key not in bg_fallback_cache:
                    bg_fallback_cache[fb_key] = pix_bg(theme, (viewport_rect.w, viewport_rect.h))
                bg = bg_fallback_cache[fb_key]
            bg_cache[bg_key] = bg

        screen.blit(bg, viewport_rect.topleft)
        pygame.draw.rect(screen, colors["border"], viewport_rect, 2, border_radius=10)

        room_name = room_def(state["roomId"])["name"]
        rn = font_small.render(room_name, True, colors["accent_dim"])
        screen.blit(rn, (viewport_rect.x + 12, viewport_rect.y + 10))

        hovering_hotspot = None
        hs_list = get_hotspot_rects()
        for hs, r, disabled in hs_list:
            if disabled:
                continue
            show_ov = hotspot_show_overlay(hs)
            if show_ov:
                cache_key = (hs["kind"], hs["id"], theme, viewport_rect.w, viewport_rect.h)
                spr = sprite_cache.get(cache_key)
                if spr is None:
                    cand1 = os.path.join(PROPS_DIR, f"{hs['id']}.png")
                    cand2 = os.path.join(PROPS_DIR, f"{hs['kind']}_{hs['id']}.png")
                    loaded = try_load_png(cand2) or try_load_png(cand1)
                    if loaded is not None:
                        target_h = max(24, min(r.h - 6, 64))
                        scale = target_h / max(1, loaded.get_height())
                        target_w = int(loaded.get_width() * scale)
                        spr = pygame.transform.scale(loaded, (max(1, target_w), max(1, int(target_h))))
                    else:
                        spr = sprite_pixel_icon(hs["kind"], hs["id"], theme, px=16, scale=2)
                    sprite_cache[cache_key] = spr
                screen.blit(spr, spr.get_rect(center=r.center))

            if debug_hotspots:
                dbg = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
                dbg.fill((25, 255, 106, 40))
                screen.blit(dbg, r.topleft)
                pygame.draw.rect(screen, colors["accent"], r, width=1, border_radius=4)
                hsz = max(6, min(HS_DEBUG_HANDLE_PX, r.w // 2, r.h // 2))
                h_r = pygame.Rect(r.right - hsz, r.bottom - hsz, hsz, hsz)
                pygame.draw.rect(screen, (255, 255, 220), h_r, width=2, border_radius=2)
                c = hsz
                et = max(2, min(HS_DEBUG_EDGE_PX, r.w // 3, r.h // 3))
                inner_h = r.h - 2 * c
                inner_w = r.w - 2 * c
                edge_col = (130, 210, 255)
                if inner_h > 0:
                    pygame.draw.rect(screen, edge_col, pygame.Rect(r.right - et, r.top + c, et, inner_h), 1)
                    pygame.draw.rect(screen, edge_col, pygame.Rect(r.x, r.top + c, et, inner_h), 1)
                if inner_w > 0:
                    pygame.draw.rect(screen, edge_col, pygame.Rect(r.left + c, r.bottom - et, inner_w, et), 1)
                    pygame.draw.rect(screen, edge_col, pygame.Rect(r.left + c, r.y, inner_w, et), 1)

            hover = r.collidepoint((mx, my)) and viewport_rect.collidepoint((mx, my))
            if hover:
                hovering_hotspot = hs["name"]
            if hover:
                pygame.draw.rect(screen, colors["hotspot_hover"], r, border_radius=6)
                pygame.draw.rect(screen, colors["hotspot_border"], r, 1, border_radius=6)

        (meter_lx, meter_ly, meter_r), (meter_rx, meter_ry, meter_rr) = viewport_corner_meter_layout(viewport_rect)
        draw_viewport_corner_meters(
            screen,
            meter_lx,
            meter_ly,
            meter_r,
            meter_rx,
            meter_ry,
            meter_rr,
            state,
            colors,
            ui_face_frames,
            plasma_orb_frames,
            plasma_orb_decor,
            font_small,
        )
        if hovering_hotspot:
            # Bottom strip of the room: just above the viewport frame / panel transition, right of plasma meter
            tip_x = meter_lx + meter_r + 8
            max_tip_w = max(120, (meter_rx - meter_rr - 8) - tip_x - 8)
            tip_lines = wrap_text_lines(font_small, hovering_hotspot, max_tip_w)
            ls = font_small.get_linesize()
            tip_h = len(tip_lines) * ls
            edge_pad = 5
            tip_y = viewport_rect.bottom - edge_pad - tip_h
            for ti, tline in enumerate(tip_lines):
                screen.blit(font_small.render(tline, True, colors["warn"]), (tip_x, tip_y + ti * ls))

        pygame.draw.rect(screen, colors["panel"], text_panel, border_radius=10)
        pygame.draw.rect(screen, colors["border"], text_panel, 1, border_radius=10)
        pygame.draw.rect(screen, colors["panel2"], right_panel, border_radius=10)
        pygame.draw.rect(screen, colors["border"], right_panel, 1, border_radius=10)

        draw_status()
        log.draw(screen, log_rect, font_mono, colors)
        draw_held()
        draw_inventory()
        draw_minimap()
        draw_ui_layout_debug_overlay()

        for b in cmd_buttons:
            b.draw(screen, font_small, colors)

        manual_btn.draw(screen, font_small, colors)
        music_btn.draw(screen, font_small, colors)
        restart_btn.draw(screen, font_small, colors)

        music_vpr = music_vol_popup_rect(music_btn.rect, lay)
        if not title_screen and music_vol_popup_visible:
            draw_music_volume_popup(screen, music_vpr, music_volume, colors, font_small)

        hint_y = status_rect.bottom + 2
        if manual_btn.rect.collidepoint((mx, my)):
            screen.blit(font_small.render("Click: Manual", True, colors["muted"]), (status_rect.x + 10, hint_y))
        elif not title_screen and music_btn.rect.collidepoint((mx, my)):
            if music_vol_popup_visible:
                hint_m = "Music: click to toggle · drag slider to set volume"
            else:
                remain = max(0, (MUSIC_VOL_HOVER_DELAY_MS - music_vol_hover_ms + 999) // 1000)
                hint_m = f"Music: hover {remain}s more for volume · click toggles playback"
            screen.blit(font_small.render(hint_m, True, colors["muted"]), (status_rect.x + 10, hint_y))
        elif not title_screen and music_vol_popup_visible and music_vpr.collidepoint((mx, my)):
            screen.blit(
                font_small.render("Drag the slider to set music volume", True, colors["muted"]),
                (status_rect.x + 10, hint_y),
            )
        elif restart_btn.rect.collidepoint((mx, my)):
            screen.blit(font_small.render("Click: Restart", True, colors["muted"]), (status_rect.x + 10, hint_y))

        if item_popup_queue:
            draw_item_acquire_popup(item_popup_queue[0])
        if active_room_popup is not None:
            draw_room_intro_popup(active_room_popup)
        if active_linda_popup is not None:
            draw_linda_popup(active_linda_popup)
        if active_manual_popup is not None:
            draw_manual_popup(active_manual_popup)

        pygame.display.flip()

    stop_title_menu_music()
    stop_gameplay_music()
    pygame.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(run())

