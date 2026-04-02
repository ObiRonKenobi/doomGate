import json
import math
import os
import re
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import pygame


# -----------------------------
# Plasma lantern balance
# -----------------------------
# Each lantern charge: this many timed actions (MOVE / world interact) at 100%→0%, then the next charge starts.
_ACTIONS_PER_LANTERN = 15
_INITIAL_LANTERN_CHARGES = 3
_LANTERN_MAX_CARRY = 5


# -----------------------------
# Data (structured like JSON)
# -----------------------------

GAME: Dict[str, Any] = {
    "meta": {
        "title": "DOOMGATE: The Warlock's Crucible",
        "actionsPerLantern": _ACTIONS_PER_LANTERN,
        "startLanterns": _INITIAL_LANTERN_CHARGES,
        "lanternMaxCarry": _LANTERN_MAX_CARRY,
        "startActions": 0,
        "saveFile": "savegame.json",
    },
    "commands": [
        {"id": "look", "label": "LOOK"},
        {"id": "take", "label": "TAKE"},
        {"id": "use", "label": "USE"},
        {"id": "talk", "label": "TALK"},
        {"id": "open", "label": "OPEN"},
        {"id": "close", "label": "CLOSE"},
        {"id": "save", "label": "SAVE"},
        {"id": "load", "label": "LOAD"},
    ],
    "deaths": {
        "darkness": "The last Plasma Lantern dies. Blackness pours in—not empty dark, but hungry. Something that waited outside the light consumes you whole: no report, no remains, only the quiet proof that darkness here eats its fill.",
        "slime": "The ooze isn't coolant. The moment you commit, it climbs armor seams like living acid. You don't melt in a movie-monster way—you simply stop being a solvable problem. The pool settles, a shade smugger than before.",
        "crateTakeDeath": "You try to haul the entire crate like a hero lifting a trophy. Your spine disagrees with your casting. You go down hard on UAC decking and stay down. The hangar keeps breathing. Hours later, something hungry follows the smell of helpless.",
        "hatchPryDeath": "You heave at the sealed excavation hatch with bare hands. The frame shifts, clamps, and bites. Hydraulics torque shut on meat and bone like a vise with standards. You don't die of drama—you die of being attached to steel that won't open.",
        "lockerKickDeath": "You USE the locker the way a boot USES a door. Reinforced UAC steel answers. Your knee loses the argument; your leg folds wrong. You end up on the armory floor, vision narrowing. Infection and thirst take the second shift; the demons only need you to still be here.",
        "terminalFries": "The sigil doesn't stay on the glass—it completes through you. Voltage and something worse ride your nerves until the terminal gets the only reading it wants: zero.",
        "sealFlays": "You try to peel the blood-seal like a sticker. The glyph renegotiates ownership. It unthreads you layer by layer until there's nothing left to pocket—only a stain that used to be confident.",
        "glassKills": "Possessed glass doesn't choose an exit vector—it chooses all of them. Shards go through your elbow decision and through you on the return trip. The display case ends up wearing more of you than you take from it.",
        "knightKills": "The Hell Knight does not take questions. Claws and heat rewrite your posture in one motion. Your rifle never gets to file a dissenting opinion.",
        "altarKnightKills": "You commit to reaching the altar anyway. The Hell Knight commits to stopping that story. It closes the distance the way a door closes—final, with metal.",
        "cruxKills": "You bring fists and attitude to a boardroom hosted by a fused demon-executive. Crux answers with talons through the gaps in your armor. The rift applauds in heat.",
        "conduitFry": "Argent isn't household current. It rides your arm to the shoulder, cooks what it touches, and leaves a marine-shaped outline of bad judgment. The conduit snaps dark again—business as usual.",
        "crystalFlash": "You press in close for a 'better look.' The Omega Crystal answers with a containment flash that goes through your visor and out the back of your thoughts. Your suit logs one heartbeat, then static.",
        "riftTouch": "The wound in the world inhales curiosity. You come apart so cleanly there isn't even time for a clever last word—only scatter, then silence, where something else learns your name.",
    },
    "items": {
        "plasmaLantern": {
            "id": "plasmaLantern",
            "name": "Plasma Lantern",
            "desc": "A UAC-issued lantern that hums with caged argent. Its battery drains with every decision you make. Convenient.",
        },
        "stimpack": {
            "id": "stimpack",
            "name": "Stimpack",
            "desc": "A pressurized syringe of 'medical optimism.' It won't fix your life choices, but it might fix the next one.",
        },
        "redKeycard": {
            "id": "redKeycard",
            "name": "Red Access Keycard",
            "desc": "Stamped UAC SECURITY. Smells faintly of burnt plastic and bad policies.",
        },
        "plasmaCell": {
            "id": "plasmaCell",
            "name": "BFG Power Cell",
            "desc": "A dense argent-laced cell. It could power something beautiful. Or catastrophic. Usually both.",
        },
        "plasmaRifle": {
            "id": "plasmaRifle",
            "name": "Plasma Rifle (Uncharged)",
            "desc": "A sleek UAC plasma rifle. Currently as threatening as a stapler.",
        },
        "chargedPlasmaRifle": {
            "id": "chargedPlasmaRifle",
            "name": "Plasma Rifle (Charged)",
            "desc": "Now it crackles with neon-blue spite. The demons will appreciate your enthusiasm.",
        },
        "beacon": {
            "id": "beacon",
            "name": "Emergency Beacon",
            "desc": "A portable distress beacon. Loud. Annoying. A perfect decoy.",
        },
        "omegaCrystal": {
            "id": "omegaCrystal",
            "name": "Omega Crystal",
            "desc": "A stable argent energy core. It glows like a contained sin.",
        },
        "serpentineKey": {
            "id": "serpentineKey",
            "name": "Serpentine Key",
            "desc": "A biomechanical key forged from demonic metal. It twitches when you're not looking.",
        },
        "neuralLink": {
            "id": "neuralLink",
            "name": "Neural Link",
            "desc": "A prototype AI core. It feels like it is judging you. It is.",
        },
        "soulCoreFrame": {
            "id": "soulCoreFrame",
            "name": "Soul-Core Breaker Frame",
            "desc": "A UAC chassis built around something that definitely wasn't in the safety manual.",
        },
        "soulCoreBreaker": {
            "id": "soulCoreBreaker",
            "name": "Soul-Core Breaker",
            "desc": "A three-part exorcism strapped to a reactor. Point it at reality and pull the concept of 'no.'",
        },
    },
    "combinations": [
        {
            "a": "plasmaRifle",
            "b": "plasmaCell",
            "text": "You slam the BFG cell into the rifle. It whines, then purrs. Somewhere, a demon files a complaint.",
            "result": {"add": ["chargedPlasmaRifle"], "remove": ["plasmaRifle", "plasmaCell"]},
        },
        {
            "a": "soulCoreFrame",
            "b": "omegaCrystal",
            "text": "The Omega Crystal seats into the frame with a chime that sounds like a cathedral being fed into a shredder.",
            "result": {"setFlag": "framePowered"},
        },
        {
            "a": "soulCoreFrame",
            "b": "neuralLink",
            "text": "The Neural Link clicks into place. A soft voice rides the speakers: \"Try not to die holding that.\"",
            "result": {"setFlag": "frameLinked"},
        },
        {
            "a": "soulCoreFrame",
            "b": "serpentineKey",
            "text": "The Serpentine Key threads into the chassis like a living screw. The air tastes like old blood and new passwords.",
            "result": {"setFlag": "frameKeyed"},
        },
        {"a": "soulCoreFrame", "b": "soulCoreFrame", "special": "assembleSoulCoreBreaker"},
    ],
    "manualText": "\n".join(
        [
            "WELCOME TO DOOMGATE: THE WARLOCK'S CRUCIBLE",
            "",
            "This is a mouse-driven, Shadowgate-style adventure.",
            "",
            "HOW TO PLAY",
            "- Click a COMMAND (LOOK/TAKE/USE/TALK/OPEN/CLOSE).",
            "- Click objects in the viewport to apply the command.",
            "- Doors and exits: select USE, then click the door/passage to move.",
            "- Click an INVENTORY item to hold it (for USE, OPEN, etc.).",
            "- Use SAVE/LOAD often. Many actions can kill you instantly.",
            "",
            "PLASMA LANTERN (TORCH MECHANIC)",
            "- Each significant action consumes time.",
            f"- You start with {_INITIAL_LANTERN_CHARGES} lantern charges (max {_LANTERN_MAX_CARRY}); each charge lasts {_ACTIONS_PER_LANTERN} timed actions.",
            "- Pickups can add charges (not inventory items). When the last charge empties, you are consumed by darkness.",
            "",
            "WIN CONDITION",
            "- Assemble the Soul-Core Breaker and USE it on Director Crux in the Hell-Gate Chamber.",
        ]
    ),
}


def rect_from_pct(x: float, y: float, w: float, h: float, parent: pygame.Rect) -> pygame.Rect:
    return pygame.Rect(
        int(parent.x + parent.w * (x / 100.0)),
        int(parent.y + parent.h * (y / 100.0)),
        int(parent.w * (w / 100.0)),
        int(parent.h * (h / 100.0)),
    )


GAME["rooms"] = {
    "hangar": {
        "id": "hangar",
        "name": "Hangar Intake — The Crucible Facility",
        "theme": "hangar",
        "mapPos": [0, 2],
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
                "use": {"death": "terminalFries", "text": "You pound the terminal like it's a vending machine. The screen flashes a demonic sigil and screams in binary."},
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
        "enterText": "The labs are sealed behind a blast door like the building is trying to quarantine its own curiosity.\n\nThe blood-seal on the keypad isn’t just vandalism. It’s a prayer written by someone who knew the right symbols—and didn’t care who answered.\n\nCrux loved locked doors. He loved what was behind them more.",
        "desc": "A blast door blocks the Research Labs. A demonic seal has been painted over the keypad, like graffiti but with consequences.\n\nThe seal looks... unfinished.",
        "exits": {"south": "corridor", "north": "labs"},
        "rules": {"gateToNorthRequiresFlag": "brokeSeal"},
        "hotspots": [
            {"id": "toCorr", "name": "Corridor", "rect": {"l": 10, "t": 34, "w": 18, "h": 28}, "kind": "exit", "data": {"dir": "south"}},
            {"id": "door", "name": "Blast Door", "rect": {"l": 46, "t": 18, "w": 18, "h": 30}, "kind": "barrier"},
            {"id": "seal", "name": "Blood Seal", "rect": {"l": 50, "t": 54, "w": 14, "h": 16}, "kind": "object"},
        ],
        "objects": {
            "seal": {
                "look": "A blood-painted seal mixed with circuitry diagrams. Crux always did love cross-discipline collaboration.",
                "use": {"requiresItem": "stimpack", "onceFlag": "brokeSeal", "consumeHeld": True, "text": "You crack the Stimpack's seal and let a few drops spatter the glyph. The blood sizzles. The demonic paint flakes away like cheap nail polish."},
                "take": {"death": "sealFlays", "text": "You try to scrape the seal into your pocket. The seal tries to scrape you into the floor."},
            },
            "door": {
                "look": "A heavy blast door. It will not open politely.",
                "open": {"requiresFlag": "brokeSeal", "text": "The keypad chirps as if grateful. The blast door unlocks with a groan."},
            },
        },
    },
    "labs": {
        "id": "labs",
        "name": "Research Labs — Argent Containment",
        "theme": "labs",
        "mapPos": [3, 2],
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
                "use": {"death": "hatchPryDeath", "text": "You try to pry it open with your hands. The hatch remains employed. You do not."},
            }
        },
    },
    "excavation": {
        "id": "excavation",
        "name": "Excavation Site — Temple Breach",
        "theme": "excavation",
        "mapPos": [3, 4],
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
        "enterText": "This is the point of no return, dressed up as architecture.\n\nUAC plating tries to cover the old stone, but the stone remembers. The door ahead is not locked to keep you out—it's locked to keep something in.\n\nThe Serpentine Key will open it. The question is what you’re opening it *for*.",
        "desc": "An antechamber where UAC plating overlays ancient stone. A massive demonic door stands to the north, its lock shaped like a coiled serpent.\n\nYou can hear a distant heartbeat that isn't yours. Or Mars's.",
        "exits": {"south": "templeLift", "north": "hellGateChamber"},
        "rules": {"gateToNorthRequiresFlag": "unlockedGate"},
        "hotspots": [
            {"id": "toLift", "name": "Lift", "rect": {"l": 10, "t": 34, "w": 18, "h": 28}, "kind": "exit", "data": {"dir": "south"}},
            {"id": "toChamber", "name": "Demonic Door", "rect": {"l": 44, "t": 18, "w": 18, "h": 30}, "kind": "barrier"},
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

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
ROOMS_DIR = os.path.join(ASSETS_DIR, "rooms")
ITEMS_DIR = os.path.join(ASSETS_DIR, "items")
PROPS_DIR = os.path.join(ASSETS_DIR, "props")
UI_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "ui"))
TITLE_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "title"))
# Preferred stems (any of these extensions: .png .jpg .jpeg .webp .bmp)
TITLE_SCREEN_STEMS = ("crucible_facility", "crucible_exterior", "title", "title_screen")
# Title menu music in assets/title/ — preferred names first (extensions: .wav .ogg .mp3)
TITLE_MUSIC_STEMS = ("title_menu", "menu", "title_music", "theme")


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
    ap = GAME["meta"]["actionsPerLantern"]
    if ap <= 0 or state["lanterns"] <= 0:
        return 0.0
    seg = state["actions"] % ap
    return float(ap - seg) / float(ap)


def player_face_frame_index(state: Dict[str, Any]) -> int:
    """Pick sprite index for status portrait (0=good … higher=worse)."""
    if get_flag(state, "gameWon"):
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
    n0 = int(GAME["meta"]["startLanterns"])
    return {
        "roomId": "hangar",
        "inventory": [],
        "heldItemId": None,
        "cmd": "look",
        "flags": {},
        "seenRooms": {},
        "roomIntroShown": {},
        "pendingRoomPopup": None,
        "actions": GAME["meta"]["startActions"],
        "lanternCount": n0,
        "lanterns": n0,
        "alive": True,
    }


def clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, v))


def item_def(item_id: str) -> Dict[str, Any]:
    return GAME["items"][item_id]


def room_def(room_id: str) -> Dict[str, Any]:
    return GAME["rooms"][room_id]


def has_item(state: Dict[str, Any], item_id: str) -> bool:
    return item_id in state["inventory"]


def get_flag(state: Dict[str, Any], name: str) -> bool:
    return bool(state["flags"].get(name, False))


def set_flag(state: Dict[str, Any], name: str, value: bool = True) -> None:
    state["flags"][name] = value


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
    if kind in {"inventory", "system"}:
        return 0
    return 1


def apply_action(state: Dict[str, Any], kind: str, log: ScrollLog) -> None:
    cost = action_cost(kind)
    if cost <= 0:
        return
    state["actions"] += cost
    ap = GAME["meta"]["actionsPerLantern"]
    spent = state["actions"] // ap
    lc = int(state.get("lanternCount", GAME["meta"]["startLanterns"]))
    if spent >= lc:
        state["lanterns"] = 0
        die(state, log, GAME["deaths"]["darkness"])
    else:
        state["lanterns"] = lc - spent


def die(state: Dict[str, Any], log: ScrollLog, text: str) -> None:
    if not state["alive"]:
        return
    state["alive"] = False
    log.add(text, "dead")
    log.add("YOU HAVE DIED. (Save early. Save often. Shadowgate would.)", "dead")


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


def try_combination(
    state: Dict[str, Any],
    log: ScrollLog,
    a: str,
    b: str,
    acquired: Optional[List[str]] = None,
) -> bool:
    x, y = (a, b) if a <= b else (b, a)
    for c in GAME["combinations"]:
        ca, cb = (c["a"], c["b"]) if c["a"] <= c["b"] else (c["b"], c["a"])
        if ca == x and cb == y:
            if c.get("special") == "assembleSoulCoreBreaker":
                assemble_soul_core_breaker(state, log, acquired=acquired)
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
            apply_action(state, "interact", log)
            return True
    return False


def assemble_soul_core_breaker(
    state: Dict[str, Any],
    log: ScrollLog,
    acquired: Optional[List[str]] = None,
) -> None:
    if not has_item(state, "soulCoreFrame"):
        log.add("You don't have the frame. Assembling nothing is a bold new engineering discipline.", "warn")
        apply_action(state, "interact", log)
        return
    ok = get_flag(state, "framePowered") and get_flag(state, "frameLinked") and get_flag(state, "frameKeyed")
    if not ok:
        log.add("The frame refuses to complete. It needs power (Omega Crystal), a mind (Neural Link), and a key (Serpentine Key).", "warn")
        apply_action(state, "interact", log)
        return
    if has_item(state, "soulCoreBreaker"):
        log.add("The Soul-Core Breaker is already assembled. Please stop petting it.", "dim")
        apply_action(state, "interact", log)
        return
    log.add("The frame locks, hums, and then clicks into something final. You have built a weapon that would make a priest faint and an engineer cry.", "sys")
    remove_items(state, ["soulCoreFrame"])
    if acquired is not None:
        acquired.append("soulCoreBreaker")
    add_items(state, ["soulCoreBreaker"])
    state["heldItemId"] = "soulCoreBreaker"
    apply_action(state, "interact", log)


def can_exit(state: Dict[str, Any], room: Dict[str, Any], direction: str) -> bool:
    rules = room.get("rules", {})
    if direction == "north" and rules.get("gateToNorthRequiresFlag"):
        return get_flag(state, rules["gateToNorthRequiresFlag"])
    return True


def move(state: Dict[str, Any], log: ScrollLog, direction: str) -> None:
    room = room_def(state["roomId"])
    target = room.get("exits", {}).get(direction)
    if not target:
        log.add("You can't go that way. The facility refuses your suggestion.", "warn")
        apply_action(state, "interact", log)
        return
    if not can_exit(state, room, direction):
        log.add("The way is blocked. Some lock—technical or infernal—still holds.", "warn")
        apply_action(state, "interact", log)
        return
    first_time = not state.get("roomIntroShown", {}).get(target, False)
    state["roomId"] = target
    state["seenRooms"][target] = True
    if "roomIntroShown" not in state or not isinstance(state["roomIntroShown"], dict):
        state["roomIntroShown"] = {}
    state["roomIntroShown"][target] = True
    apply_action(state, "move", log)
    log.add(f">> {room_def(target)['name']}", "dim")
    log.add(room_def(target)["desc"])
    if first_time:
        enter_text = room_def(target).get("enterText")
        if enter_text:
            state["pendingRoomPopup"] = target


def resolve_object_action(
    state: Dict[str, Any],
    log: ScrollLog,
    obj_id: str,
    cmd: str,
    hotspot_kind: str,
    acquired: Optional[List[str]] = None,
) -> None:
    room = room_def(state["roomId"])
    obj = room.get("objects", {}).get(obj_id)
    if not obj:
        if hotspot_kind == "hazard":
            die(state, log, GAME["deaths"]["slime"])
            return
        log.add("There's nothing meaningful there. Only ambience and liability.", "warn")
        apply_action(state, "interact", log)
        return

    if get_flag(state, "gameWon"):
        log.add("The rift is sealed. What remains is cleanup and therapy. Mostly therapy.", "dim")
        apply_action(state, "interact", log)
        return

    handler = obj.get(cmd)
    if handler is None:
        if hotspot_kind == "hazard":
            die(state, log, GAME["deaths"]["slime"])
            return
        log.add("That accomplishes nothing. The facility remains unimpressed.", "warn")
        apply_action(state, "interact", log)
        return

    if isinstance(handler, str):
        log.add(handler)
        apply_action(state, "interact", log)
        return

    # Death handler
    if handler.get("death"):
        if handler.get("text"):
            log.add(handler["text"])
        die(state, log, GAME["deaths"].get(handler["death"], "You die in a way that is educational to everyone except you."))
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
            if opt.get("setFlag"):
                set_flag(state, opt["setFlag"], True)
            if opt.get("onceFlag"):
                set_flag(state, opt["onceFlag"], True)
            apply_action(state, "interact", log)
            if get_flag(state, "gameWon"):
                log.add("VICTORY", "title")
                log.add("The rift seals. The facility groans like a dying god of metal. You run. Or you don't. Either way, history gets a footnote.", "sys")
            return
        d = handler.get("default")
        if d:
            if d.get("text"):
                log.add(d["text"])
            if d.get("death"):
                die(state, log, GAME["deaths"].get(d["death"], "You die."))
            else:
                apply_action(state, "interact", log)
            return

    # Requirements
    if handler.get("requiresItem") and held != handler["requiresItem"]:
        log.add("That doesn't work. You might need a specific item.", "warn")
        apply_action(state, "interact", log)
        return
    if handler.get("requiresFlag") and not get_flag(state, handler["requiresFlag"]):
        if cmd == "take" and (handler.get("takeFailText") or handler.get("takeFailDeath")):
            if handler.get("takeFailText"):
                log.add(handler["takeFailText"])
            if handler.get("takeFailDeath"):
                die(state, log, GAME["deaths"].get(handler["takeFailDeath"], "You die."))
            else:
                apply_action(state, "interact", log)
            return
        log.add("Something else must happen first.", "warn")
        apply_action(state, "interact", log)
        return
    if handler.get("onceFlag") and get_flag(state, handler["onceFlag"]):
        log.add("You've already done that. Repetition is a hobby, not a solution.", "dim")
        apply_action(state, "interact", log)
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
        mx = int(GAME["meta"]["lanternMaxCarry"])
        lc0 = int(state.get("lanternCount", GAME["meta"]["startLanterns"]))
        state["lanternCount"] = lc0
        nl = min(mx, lc0 + int(add_lan))
        if nl > lc0:
            state["lanternCount"] = nl
            ap = GAME["meta"]["actionsPerLantern"]
            sp = state["actions"] // ap
            state["lanterns"] = max(0, nl - sp)
        else:
            log.add("You can't carry any more Plasma Lantern charges.", "warn")

    if handler.get("consumeHeld") and held:
        remove_items(state, [held])

    apply_action(state, "interact", log)

    if get_flag(state, "gameWon"):
        log.add("VICTORY", "title")
        log.add("The rift seals. The facility groans like a dying god of metal. You run. Or you don't. Either way, history gets a footnote.", "sys")


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

    held_h = 52
    gap2 = 8
    rh = right_panel.h - 10
    manual_row = 36
    # Proportional inventory + map, remainder for commands
    inv_h = max(72, min(140, int((rh - held_h - manual_row - gap2 * 4) * 0.34)))
    map_h = max(72, min(140, int((rh - held_h - manual_row - gap2 * 4) * 0.34)))
    cmd_h = rh - held_h - manual_row - inv_h - map_h - gap2 * 4
    if cmd_h < 80:
        shave = 80 - cmd_h
        inv_h = max(60, inv_h - shave // 2)
        map_h = max(60, map_h - shave // 2)
        cmd_h = rh - held_h - manual_row - inv_h - map_h - gap2 * 4

    held_rect = pygame.Rect(right_panel.x, right_panel.y + 5, right_panel.w, held_h)
    inv_rect = pygame.Rect(right_panel.x, held_rect.bottom + gap2, right_panel.w, inv_h)
    map_rect = pygame.Rect(right_panel.x, inv_rect.bottom + gap2, right_panel.w, map_h)
    cmd_rect = pygame.Rect(right_panel.x, map_rect.bottom + gap2, right_panel.w, max(80, cmd_h))
    extra_y = cmd_rect.bottom + gap2
    manual_btn_rect = pygame.Rect(cmd_rect.x, extra_y, (cmd_rect.w - gap2) // 2, manual_row - 4)
    restart_btn_rect = pygame.Rect(
        cmd_rect.x + (cmd_rect.w - gap2) // 2 + gap2,
        extra_y,
        (cmd_rect.w - gap2) // 2,
        manual_row - 4,
    )

    cols = 4
    rows = 2
    btn_h = max(26, min(36, (cmd_rect.h - gap2) // rows - gap2))
    btn_w = (cmd_rect.w - gap2 * (cols - 1)) // cols
    cmd_button_rects: List[Tuple[str, str, pygame.Rect]] = []
    for i, c in enumerate(GAME["commands"]):
        r = i // cols
        cc = i % cols
        bx = cmd_rect.x + cc * (btn_w + gap2)
        by = cmd_rect.y + r * (btn_h + gap2)
        cmd_button_rects.append((c["id"], c["label"], pygame.Rect(bx, by, btn_w, btn_h)))

    return {
        "W": W,
        "H": H,
        "pad": pad,
        "title_bar_h": title_bar_h,
        "viewport_rect": viewport_rect,
        "text_panel": text_panel,
        "right_panel": right_panel,
        "status_rect": status_rect,
        "log_rect": log_rect,
        "held_rect": held_rect,
        "inv_rect": inv_rect,
        "map_rect": map_rect,
        "cmd_rect": cmd_rect,
        "manual_btn_rect": manual_btn_rect,
        "restart_btn_rect": restart_btn_rect,
        "cmd_button_rects": cmd_button_rects,
    }


def main() -> int:
    pygame.init()
    try:
        pygame.mixer.init()
    except Exception:
        pass
    pygame.display.set_caption(GAME["meta"]["title"])
    title_music_path = resolve_title_music_path()

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
        path = os.path.join(os.path.dirname(__file__), GAME["meta"]["saveFile"])
        with open(path, "w", encoding="utf-8") as f:
            f.write(payload)
        log_sys(f"Saved to {GAME['meta']['saveFile']}.")

    def load_game() -> None:
        path = os.path.join(os.path.dirname(__file__), GAME["meta"]["saveFile"])
        if not os.path.exists(path):
            log.add("No save found.", "warn")
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            if not isinstance(loaded, dict):
                raise ValueError("Bad save")
            # merge with defaults
            base = default_state()
            base.update(loaded)
            base.setdefault("flags", {})
            base.setdefault("seenRooms", {})
            base.setdefault("roomIntroShown", {})
            base.setdefault("pendingRoomPopup", None)
            base.setdefault("inventory", [])
            ap_m = GAME["meta"]["actionsPerLantern"]
            sp_m = base.get("actions", 0) // ap_m
            if "lanternCount" not in base or base.get("lanternCount") is None:
                base["lanternCount"] = clamp(
                    int(base.get("lanterns", GAME["meta"]["startLanterns"])) + sp_m,
                    1,
                    int(GAME["meta"]["lanternMaxCarry"]),
                )
            base["lanternCount"] = clamp(
                int(base["lanternCount"]),
                1,
                int(GAME["meta"]["lanternMaxCarry"]),
            )
            lc_m = base["lanternCount"]
            if sp_m >= lc_m:
                base["lanterns"] = 0
            else:
                base["lanterns"] = lc_m - sp_m
            state.clear()
            state.update(base)
            log_sys("Loaded save.")
            log.add(room_def(state["roomId"])["desc"])
        except Exception:
            log.add("Save data is corrupted. (The file got possessed.)", "warn")

    def restart() -> None:
        nonlocal title_screen, intro_done
        state.clear()
        state.update(default_state())
        log.lines.clear()
        log.scroll_px = 0
        title_screen = False
        intro_done = False
        item_popup_queue.clear()
        nonlocal active_room_popup, active_manual_popup
        active_room_popup = None
        active_manual_popup = None
        intro()
        intro_done = True
        state["seenRooms"][state["roomId"]] = True
        if not state.get("roomIntroShown", {}).get(state["roomId"], False) and room_def(state["roomId"]).get("enterText"):
            state.setdefault("roomIntroShown", {})[state["roomId"]] = True
            state["pendingRoomPopup"] = state["roomId"]
        bg_cache.clear()
        sprite_cache.clear()

    title_screen = True
    intro_done = False
    item_popup_queue: List[str] = []
    active_room_popup: Optional[Dict[str, Any]] = None
    active_manual_popup: Optional[Dict[str, Any]] = None
    layout_state: Dict[str, Any] = {}
    item_thumb_cache: Dict[str, pygame.Surface] = {}
    debug_hotspots = False
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
            pygame.mixer.music.play(loops=-1)
        except Exception:
            pass

    def enter_game_from_title() -> None:
        nonlocal title_screen, intro_done
        stop_title_menu_music()
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
        threat = "DEAD" if not state["alive"] else ("SEALED" if get_flag(state, "gameWon") else ("CRITICAL" if state["lanterns"] <= 1 else "ACTIVE"))
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
            col = colors["warn"] if ("THREAT:" in ch and threat == "CRITICAL") else (colors["dead"] if threat == "DEAD" and "THREAT:" in ch else colors["muted"])
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
        screen.blit(font_small.render(f"Command: {cmd}", True, colors["muted"]), (held_rect.x + 10, held_rect.y + 30))
        iw = max(held_rect.x + 160, held_rect.x + held_rect.w // 2)
        screen.blit(font_small.render(f"Item: {held_item_name()}", True, colors["accent_dim"]), (iw, held_rect.y + 30))

    inv_buttons: List[Tuple[str, pygame.Rect]] = []

    def draw_inventory() -> None:
        nonlocal inv_buttons
        inv_buttons = []
        inv_rect = layout_state["inv_rect"]
        draw_box(screen, inv_rect, "Inventory")
        items = state["inventory"]
        area = pygame.Rect(inv_rect.x + 10, inv_rect.y + 30, inv_rect.w - 20, inv_rect.h - 40)
        cols_i = 3
        bw = (area.w - 8 * (cols_i - 1)) // cols_i
        bh = 28
        for idx, iid in enumerate(items):
            r = idx // cols_i
            c = idx % cols_i
            rect = pygame.Rect(area.x + c * (bw + 8), area.y + r * (bh + 8), bw, bh)
            inv_buttons.append((iid, rect))
            selected = state.get("heldItemId") == iid
            bg = (18, 34, 26) if selected else (10, 14, 12)
            border = colors["accent"] if selected else colors["border"]
            pygame.draw.rect(screen, bg, rect, border_radius=8)
            pygame.draw.rect(screen, border, rect, 1, border_radius=8)
            screen.blit(font_small.render(item_def(iid)["name"][:18], True, colors["text"]), (rect.x + 8, rect.y + 6))
        if not items:
            screen.blit(font_small.render("(empty)", True, colors["muted"]), (area.x, area.y))

    def draw_minimap() -> None:
        map_rect = layout_state["map_rect"]
        draw_box(screen, map_rect, "Minimap")
        size = 5
        grid_area = pygame.Rect(map_rect.x + 10, map_rect.y + 30, map_rect.w - 20, map_rect.h - 40)
        cell = min((grid_area.w - 4 * (size - 1)) // size, (grid_area.h - 4 * (size - 1)) // size)
        # build room positions
        pos_to_room: Dict[Tuple[int, int], str] = {}
        for rid, r in GAME["rooms"].items():
            mp = r.get("mapPos")
            if mp and len(mp) == 2:
                pos_to_room[(mp[0], mp[1])] = rid
        for y in range(size):
            for x in range(size):
                rr = pygame.Rect(grid_area.x + x * (cell + 4), grid_area.y + y * (cell + 4), cell, cell)
                rid = pos_to_room.get((x, y))
                seen = rid and state["seenRooms"].get(rid, False)
                here = rid == state["roomId"]
                bg = (10, 14, 12)
                br = colors["border"]
                if seen:
                    bg = (16, 28, 22)
                    br = (35, 90, 62)
                pygame.draw.rect(screen, bg, rr, border_radius=6)
                pygame.draw.rect(screen, br, rr, 1, border_radius=6)
                if here:
                    pygame.draw.rect(screen, colors["warn"], rr, 2, border_radius=6)
                # marker
                marker = "■" if seen else "·"
                screen.blit(font_small.render(marker, True, colors["text"] if seen else colors["muted"]), (rr.centerx - 4, rr.centery - 8))

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
        restart_btn = Button(lay["restart_btn_rect"], "RESTART", "restart", danger=True)

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
                if active_room_popup is not None:
                    active_room_popup = None
                elif active_manual_popup is not None:
                    active_manual_popup = None
                elif item_popup_queue:
                    item_popup_queue.pop(0)
                else:
                    running = False
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
                if log_rect.collidepoint(mx, my):
                    log.wheel(event.y)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
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
                ):
                    debug_hotspots = not debug_hotspots

        if title_screen:
            draw_title_scr()
            pygame.display.flip()
            continue

        if active_room_popup is not None:
            # Freeze world interaction while popup is present, but still render the room underneath.
            pass

        # Draw background
        screen.fill(colors["bg"])
        title = font_ui.render(GAME["meta"]["title"], True, colors["text"])
        screen.blit(title, (pad, pad))
        subtitle = font_small.render(
            "Shadowgate mechanics • Doom industrial hell aesthetic • Mouse-only • F3: hotspot debug",
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

        for b in cmd_buttons:
            b.draw(screen, font_small, colors)

        manual_btn.draw(screen, font_small, colors)
        restart_btn.draw(screen, font_small, colors)

        if manual_btn.rect.collidepoint((mx, my)):
            screen.blit(font_small.render("Click: Manual", True, colors["muted"]), (status_rect.x + 10, status_rect.bottom + 2))
        if restart_btn.rect.collidepoint((mx, my)):
            screen.blit(font_small.render("Click: Restart", True, colors["muted"]), (status_rect.x + 120, status_rect.bottom + 2))

        if item_popup_queue:
            draw_item_acquire_popup(item_popup_queue[0])
        if active_room_popup is not None:
            draw_room_intro_popup(active_room_popup)
        if active_manual_popup is not None:
            draw_manual_popup(active_manual_popup)

        pygame.display.flip()

    stop_title_menu_music()
    pygame.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

