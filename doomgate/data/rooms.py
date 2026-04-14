from __future__ import annotations

from typing import Any, Dict


def build_rooms() -> Dict[str, Any]:
    # Intentionally left as a plain dict for easy editing and to keep imports simple for PyInstaller.
    return {
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
                        "text": "You pop the latch. Inside: a spare plasma charger pack and a vial of demon blood. The glass is warm, like it hates you personally.",
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
                {"id": "toLabs", "name": "Into the Labs", "rect": {"l": 44, "t": 16, "w": 18, "h": 28}, "kind": "exit", "data": {"dir": "north"}},
                {"id": "seal", "name": "Blood Seal", "rect": {"l": 50, "t": 54, "w": 14, "h": 16}, "kind": "object"},
            ],
            "objects": {
                "seal": {
                    "look": "A blood-painted seal mixed with circuitry diagrams. Crux always did love cross-discipline collaboration.",
                    "use": {"requiresItem": "stimpack", "onceFlag": "brokeSeal", "consumeHeld": True, "text": "You uncap the vial and let a few drops spatter the glyph. The blood sizzles. The demonic paint flakes away like cheap nail polish."},
                    "take": {"death": "sealFlays", "text": "You try to scrape the seal into your pocket. The seal tries to scrape you into the floor."},
                }
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
                    "talk": {
                        "special": "cycleText",
                        "flag": "quartersIntercomTalk",
                        "lines": [
                            "\"I'm here,\" you say.\n\n\"Regrettably,\" the intercom replies.",
                            "\"Knock knock,\" you say into the speaker.\n\nA pause. Then Crux, dry as bone: \"Shut up, dude.\"",
                            "\"If you can hear me, press one for 'haunted facility,'\" you say.\n\n\"Pressing one,\" Crux says. \"Also pressing 'end you.'\"",
                            "\"You know, this intercom has great range,\" you say.\n\n\"So do my regrets,\" Crux answers. \"Stop talking.\"",
                            "\"Any last words?\" you ask.\n\nCrux exhales. \"Yes. Less. From you.\"",
                        ],
                    },
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
            "enterText": "The lift is where the facility stops pretending it’s just steel.\n\nBone-white growths crawl over the frame, and the button panel has been reduced to a choice: up, or down.\n\nDOWN lands at the excavation hatch—the last UAC seal before the dig. The breach beyond is not a shortcut. It’s a bill.",
            "desc": "A freight lift fused with bone-white growths. The button panel has only two working lights: UP and DOWN. DOWN is lit like a dare; beneath you is the hatch room, not the pit itself.\n\nA voice crackles: \"The ruins predate Mars. Which is inconvenient for Mars.\"",
            "exits": {"west": "quarters", "east": "labs", "down": "excavationHatch"},
            "hotspots": [
                {"id": "toQuarters", "name": "Quarters", "rect": {"l": 10, "t": 34, "w": 18, "h": 28}, "kind": "exit", "data": {"dir": "west"}},
                {"id": "toLabs", "name": "Labs", "rect": {"l": 78, "t": 34, "w": 18, "h": 28}, "kind": "exit", "data": {"dir": "east"}},
                {"id": "down", "name": "DOWN Button", "rect": {"l": 46, "t": 58, "w": 12, "h": 12}, "kind": "exit", "data": {"dir": "down"}},
            ],
        },
        "excavationHatch": {
            "id": "excavationHatch",
            "name": "Excavation Hatch — Sealed",
            "theme": "hatch",
            "mapPos": [2, 4],
            "mapFloor": -1,
            "enterText": "The hatch is a boundary line—someone’s last attempt to draw “outside” and “inside” with a piece of steel.\n\nClaw marks gouge the frame from below. Whatever wanted out was strong. Whatever kept it in was desperate.\n\nIf you open this, you are choosing a direction for the whole story.",
            "desc": "A heavy hatch marked EXCAVATION. Claw marks score the frame from the inside.\n\nThe freight lift opens onto this landing—DOWN from the service deck, UP when you need to breathe facility air again.\n\nA biometric lock blinks an angry red.",
            "exits": {"south": "maintenance", "north": "excavation", "up": "templeLift"},
            "rules": {"gateToNorthRequiresFlag": "openedHatch"},
            "hotspots": [
                {"id": "toMaint", "name": "Maintenance", "rect": {"l": 10, "t": 34, "w": 18, "h": 28}, "kind": "exit", "data": {"dir": "south"}},
                {"id": "toLift", "name": "Service Lift", "rect": {"l": 72, "t": 52, "w": 18, "h": 24}, "kind": "exit", "data": {"dir": "up"}},
                {"id": "hatch", "name": "Excavation Hatch", "rect": {"l": 46, "t": 18, "w": 18, "h": 30}, "kind": "barrier"},
            ],
            "objects": {
                "hatch": {
                    "look": "The lock demands clearance that is, statistically speaking, dead.",
                    "open": {"requiresItem": "redKeycard", "onceFlag": "openedHatch", "text": "You swipe the Red Keycard. The hatch unlatches with a thunk that sounds like a coffin approving your paperwork."},
                    "use": {
                        "options": [{"requiresFlag": "openedHatch", "text": "You duck through the hatch into the excavation shaft.", "travelDir": "north"}],
                        "default": {"death": "hatchPryDeath", "text": "You try to pry it open with your hands. The hatch remains employed. You do not."},
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
            "desc": "A vast pit where UAC dug into ancient black stone. Floodlights illuminate a demonic arch half-buried in dust. A Hell Knight stalks the edge, guarding something that glints near the altar.\n\nStone stairs climb north toward the hell-gate threshold—there is no other way up from the dig.\n\nYour rifle feels suddenly inadequate in the philosophical sense.",
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
                            {"requiresItem": "beacon", "onceFlag": "knightDistracted", "text": "You arm the Emergency Beacon and toss it. It howls a siren and flashes strobe light. The Hell Knight turns, fascinated by the concept of noise.", "setFlag": "knightGone"},
                            {"requiresItem": "chargedPlasmaRifle", "requiresFlag": "knightDistracted", "onceFlag": "knightDead", "text": "While it's distracted, you level the charged Plasma Rifle and fire. Blue bolts tear through demon flesh like angry math. The Hell Knight collapses into ash and spite.", "setFlag": "knightGone"},
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
            "desc": "An antechamber where UAC plating overlays ancient stone. A massive demonic door stands to the north, its lock shaped like a coiled serpent.\n\nSouth, the stone stairs return only to the excavation pit—the serpent threshold is never a lift ride away from the dig.\n\nYou can hear a distant heartbeat that isn't yours. Or Mars's.",
            "exits": {"south": "excavation", "north": "hellGateChamber"},
            "rules": {"gateToNorthRequiresFlag": "unlockedGate"},
            "hotspots": [
                {"id": "toExcavation", "name": "Stone Stairs", "rect": {"l": 10, "t": 34, "w": 18, "h": 28}, "kind": "exit", "data": {"dir": "south"}},
                {"id": "toChamber", "name": "Into the Hell-Gate", "rect": {"l": 44, "t": 16, "w": 18, "h": 28}, "kind": "exit", "data": {"dir": "north"}},
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
                "rift": {"look": "A wound in the world. It bleeds light and laughter.", "use": {"death": "riftTouch"}, "take": {"death": "riftTouch"}, "open": {"death": "riftTouch"}, "talk": {"death": "riftTouch"}, "close": {"death": "riftTouch"}},
                "crux": {
                    "look": "Crux's face is still there, somewhere under the demonic growth. His eyes burn with executive certainty.",
                    "talk": "\"Marine,\" Crux purrs, voice doubled with something older. \"You are late. But late is still on time for sacrifice.\"",
                    "use": {"options": [{"requiresItem": "soulCoreBreaker", "text": "You raise the Soul-Core Breaker. It screams—not in pain, but in joy. A beam of inverted helllight lances into the rift.\n\nThe Titan howls as reality clamps down like a jaw. Crux's fused form spasms, then is dragged backward, clawing at the air like a man trying to keep his job.\n\nA voice whispers: \"Seal achieved. Please evacuate. Or don't. I'm not your mother.\"", "setFlag": "gameWon"}], "default": {"death": "cruxKills", "text": "You attempt an unassisted solution to an apocalyptic problem. Crux appreciates the comedy before removing your head."}},
                },
            },
        },
    }

