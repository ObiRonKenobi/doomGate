from __future__ import annotations

from typing import Any, Dict

# Plasma lantern balance
_ACTIONS_PER_LANTERN = 15
_INITIAL_LANTERN_CHARGES = 3
_LANTERN_MAX_CARRY = 5


def make_game_core() -> Dict[str, Any]:
    """
    Core GAME dict without rooms.

    Rooms are intentionally kept separate so they can be edited/split without
    making this module massive.
    """
    from doomgate.data.rooms import build_rooms

    return {
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
            "terminalOverload": "The terminal accepts one wrong guess too many. Capacitors scream, argent bleed through the PCB, and the stack explodes like a bad IPO. Your last thought is that L.I.N.D.A. did warn you.",
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
        "lindaTerminalCodes": {
            "stonks": {"action": "minigame_rbyt3r"},
            "rbyt3r": {"action": "god_mode"},
        },
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
        "rooms": build_rooms(),
    }

