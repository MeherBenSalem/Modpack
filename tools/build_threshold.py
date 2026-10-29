#!/usr/bin/env python3
"""Build the Threshold: the starting area every new Ashborn wakes in (KubeJS datapack + generated function).

  python3 tools/build_threshold.py

Writes, under pack/kubejs/data/remnants/:
  dimension_type/threshold.json, dimension/threshold.json   a void dimension frozen at dusk (fixed time)
  function/threshold/build.mcfunction                         every block of the ruin, as fill/setblock commands
  advancement/threshold/*.json                                 the three milestones the quests and toasts use
and pack/kubejs/startup_scripts/remnants_threshold_layout.js  the coordinates threshold.js reads.

The ruin is a floating island in the void. You wake in the Crypt (east), walk west down the Hall of Messages toward
the black sun on the horizon, cross the fog gate into the Arena, fell the Gatekeeper, and leave by the Ember Door on
the far side, up the Last Stair to the Waygate. Everything is deterministic (fixed RNG seed), so rebuilding gives the
same ruin; bump BUILD_VERSION when the layout changes and servers rebuild it on their next start.
"""
import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "pack" / "kubejs" / "data" / "remnants"
LAYOUT_JS = ROOT / "pack" / "kubejs" / "startup_scripts" / "remnants_threshold_layout.js"  # global is startup-only
BUILD_VERSION = 2

Y = 64  # floor level; players stand at Y + 1
CRYPT = dict(x1=-12, x2=0, z1=-6, z2=6)
HALL = dict(x1=-40, x2=-13, z1=-4, z2=4)
GATE_X = -41                       # the fog gate plane (z -3..3)
ARENA = dict(cx=-62, cz=0, r=19)
EXIT_X = -82                       # the Ember Door plane on the arena's far side
STAIR = dict(x1=-110, x2=-83, z1=-3, z2=3)
WAYGATE = dict(x1=-122, x2=-111, z1=-6, z2=6)

LAYOUT = {
    "version": BUILD_VERSION,
    "dimension": "remnants:threshold",
    "wake": [-3.5, Y + 1, 0.5, 90],            # x, y, z, yaw (90 faces west, toward the sun)
    "gate": {"x": GATE_X, "z1": -3, "z2": 3, "y1": Y + 1, "y2": Y + 5},
    "arena": {"cx": ARENA["cx"] + 0.5, "cz": ARENA["cz"] + 0.5, "r": ARENA["r"], "boss": [-70.5, Y + 1, 0.5]},
    "exit_door": {"x": EXIT_X, "z1": -2, "z2": 2, "y1": Y + 1, "y2": Y + 4},
    "stair_start": [-85.5, Y + 1, 0.5, 90],
    "waygate": {"x": -117, "z1": -2, "z2": 2},
    "ember_door": {"x1": -9, "x2": -7, "z": 6, "y1": Y + 1, "y2": Y + 3},   # crypt shortcut, opens after the boss
    "forceload": [-126, -26, 6, 26],
}

rng = random.Random(7)
cmds = []


def fill(x1, y1, z1, x2, y2, z2, block, mode=""):
    cmds.append(f"fill {x1} {y1} {z1} {x2} {y2} {z2} {block}{(' ' + mode) if mode else ''}")


def setblock(x, y, z, block):
    cmds.append(f"setblock {x} {y} {z} {block}")


def pick(*options):
    """Weighted pick: pick(("a", 3), ("b", 1))."""
    total = sum(w for _, w in options)
    r = rng.uniform(0, total)
    for b, w in options:
        r -= w
        if r <= 0:
            return b
    return options[-1][0]


FLOOR = (("minecraft:deepslate_tiles", 5), ("minecraft:cracked_deepslate_tiles", 4),
         ("minecraft:polished_deepslate", 2), ("minecraft:cobbled_deepslate", 1), ("minecraft:gravel", 1))
WALL = (("minecraft:deepslate_bricks", 6), ("minecraft:cracked_deepslate_bricks", 4),
        ("minecraft:polished_blackstone_bricks", 1), ("minecraft:cracked_polished_blackstone_bricks", 1))
ROCK = (("minecraft:deepslate", 6), ("minecraft:cobbled_deepslate", 2), ("minecraft:blackstone", 2),
        ("minecraft:tuff", 1))


def in_island(x, z):
    """Floor footprint: crypt + hall + arena + stair + waygate platform."""
    if CRYPT["x1"] - 1 <= x <= CRYPT["x2"] + 1 and CRYPT["z1"] - 1 <= z <= CRYPT["z2"] + 1:
        return True
    if HALL["x1"] <= x <= HALL["x2"] and HALL["z1"] - 1 <= z <= HALL["z2"] + 1:
        return True
    if (x - ARENA["cx"]) ** 2 + (z - ARENA["cz"]) ** 2 <= (ARENA["r"] + 2) ** 2:
        return True
    if STAIR["x1"] <= x <= STAIR["x2"] and STAIR["z1"] - 1 <= z <= STAIR["z2"] + 1:
        return True
    if (x - (-116)) ** 2 + z ** 2 <= 7 ** 2:
        return True
    return False


def stair_height(x):
    """The Last Stair climbs 6 blocks from the arena to the Waygate."""
    if x > STAIR["x2"]:
        return 0
    if x < STAIR["x1"]:
        return 6
    return min(6, (STAIR["x2"] - x) // 4)


def foundation():
    """A ragged slab of rock under the whole footprint, deeper in the middle, crumbling at the edges."""
    for x in range(-125, 4):
        z = -26
        while z <= 26:
            if not in_island(x, z):
                z += 1
                continue
            edge = sum(1 for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0), (0, 2), (0, -2))
                       if not in_island(x + dx, z + dz))
            top = Y + stair_height(x) - 1
            depth = 2 + rng.randint(0, 2) if edge else 6 + rng.randint(0, 6) + int(4 * math.sin(x / 7.0) ** 2)
            fill(x, top - depth, z, x, top, z, pick(*ROCK))
            z += 1


def floor():
    for x in range(-125, 4):
        for z in range(-26, 27):
            if in_island(x, z):
                setblock(x, Y + stair_height(x), z, pick(*FLOOR))


def crypt():
    c = CRYPT
    # walls 6 high, roof half caved in (the sky shows through the east end)
    for x in range(c["x1"] - 1, c["x2"] + 2):
        for z in (c["z1"] - 1, c["z2"] + 1):
            for y in range(Y + 1, Y + 7):
                setblock(x, y, z, pick(*WALL))
    for z in range(c["z1"] - 1, c["z2"] + 2):
        for y in range(Y + 1, Y + 7):
            setblock(c["x2"] + 1, y, z, pick(*WALL))
            if not (-2 <= z <= 2 and y <= Y + 4):          # the west archway into the hall
                setblock(c["x1"] - 1, y, z, pick(*WALL))
    for x in range(c["x1"] - 1, c["x2"] + 2):
        for z in range(c["z1"] - 1, c["z2"] + 2):
            if x < -6 or rng.random() < 0.25:               # the eastern half of the roof fell in
                setblock(x, Y + 7, z, pick(("minecraft:deepslate_tile_slab[type=bottom]", 3),
                                           ("minecraft:deepslate_bricks", 2)))
    # the open coffin you wake beside, and its rows of sealed neighbours
    for zc in (-4, 4):
        for xc in (-10, -6, -2):
            fill(xc - 1, Y + 1, zc, xc + 1, Y + 1, zc, "minecraft:polished_deepslate_slab[type=bottom]")
            setblock(xc + 2, Y + 1, zc, "minecraft:chiseled_deepslate")
            setblock(xc + 2, Y + 2, zc, "minecraft:candle[candles=3,lit=true]")
    fill(-4, Y + 1, 1, -2, Y + 1, 1, "minecraft:polished_deepslate_slab[type=bottom]")   # yours, broken open
    setblock(-1, Y + 1, 1, "minecraft:skeleton_skull[rotation=4]")
    # the Ember Door: a soul-fire doorway in the south wall that only answers those who faced the Gatekeeper
    d = LAYOUT["ember_door"]
    fill(d["x1"], d["y1"], d["z"], d["x2"], d["y2"], d["z"], "minecraft:air")
    fill(d["x1"] - 1, d["y1"], d["z"] + 1, d["x2"] + 1, d["y2"] + 1, d["z"] + 1, "minecraft:crying_obsidian")
    setblock(d["x1"] - 1, d["y2"] + 1, d["z"], "minecraft:soul_lantern[hanging=false]")
    setblock(d["x2"] + 1, d["y2"] + 1, d["z"], "minecraft:soul_lantern[hanging=false]")
    # light: candles and hanging soul lanterns on chains
    for x in (-11, -7, -3, 0):
        setblock(x, Y + 6, 0, "minecraft:chain")
        setblock(x, Y + 5, 0, "minecraft:soul_lantern[hanging=true]")
    for _ in range(14):
        setblock(rng.randint(c["x1"], c["x2"]), Y + 1, rng.choice((c["z1"], c["z2"], -5, 5)),
                 f"minecraft:candle[candles={rng.randint(1, 4)},lit=true]")
    for _ in range(10):
        setblock(rng.randint(c["x1"], c["x2"]), rng.randint(Y + 4, Y + 6), rng.choice((c["z1"], c["z2"])),
                 "minecraft:cobweb")


MESSAGES = [  # the Hall of Messages: notes the Ashborn before you scratched into the floor
    ("Roll through,", "not away.", "", "— an Ashborn"),
    ("Fog ahead.", "Gatekeeper.", "He waits.", ""),
    ("Try", "dying.", "It helps.", ""),
    ("Runes lost", "here.", "Twice.", ""),
    ("Odric was", "kind once.", "Not now.", ""),
    ("Praise", "the ember!", "", ""),
    ("Shield?", "No.", "He breaks", "them."),
    ("Behind you", "is the", "only way", "back."),
]


def sign(x, z, lines, rotation):
    msgs = ",".join(json.dumps(json.dumps({"text": t})) for t in lines)
    setblock(x, Y + 1, z, f"minecraft:dark_oak_sign[rotation={rotation}]"
                          f"{{front_text:{{color:\"white\",has_glowing_text:1b,messages:[{msgs}]}}}}")


def hall():
    h = HALL
    for x in range(h["x1"], h["x2"] + 1):
        for z in (h["z1"] - 1, h["z2"] + 1):
            height = 5 if (x % 6) else 7                      # pillars every six blocks
            if rng.random() < 0.15:
                height = rng.randint(1, 3)                     # broken wall
            for y in range(Y + 1, Y + 1 + height):
                setblock(x, y, z, pick(*WALL) if x % 6 else "minecraft:polished_deepslate")
        if x % 6 == 0:                                         # ruined arches between the pillars
            if rng.random() < 0.6:
                fill(x, Y + 7, h["z1"] - 1, x, Y + 7, h["z2"] + 1, "minecraft:deepslate_brick_slab[type=bottom]")
            for z in (h["z1"], h["z2"]):
                setblock(x, Y + 1, z, "minecraft:soul_campfire[lit=true,signal_fire=false]")
    # statues of the Ashborn who never made it: armour stands, kneeling under their swords
    for i, x in enumerate(range(h["x2"] - 4, h["x1"], -9)):
        for z, rot in ((h["z1"], 0), (h["z2"], 180)):
            cmds.append(
                f"summon minecraft:armor_stand {x + 0.5} {Y + 1} {z + 0.5} {{Invulnerable:1b,NoGravity:1b,"
                f"ShowArms:1b,NoBasePlate:1b,Tags:[\"remnants_threshold\"],Rotation:[{rot}f,0f],"
                f"Pose:{{Head:[30f,0f,0f],RightArm:[-110f,0f,0f],LeftArm:[-110f,0f,0f]}},"
                f"HandItems:[{{id:\"minecraft:iron_sword\",count:1}},{{}}],"
                f"ArmorItems:[{{}},{{id:\"minecraft:chainmail_leggings\",count:1}},"
                f"{{id:\"minecraft:chainmail_chestplate\",count:1}},{{id:\"minecraft:iron_helmet\",count:1}}]}}")
    for i, lines in enumerate(MESSAGES):
        x = h["x2"] - 2 - i * 3
        sign(x, rng.choice((-1, 0, 1)), lines, rng.choice((3, 4, 5)))
    for _ in range(18):
        setblock(rng.randint(h["x1"], h["x2"]), Y + 1, rng.choice((h["z1"], h["z2"])),
                 pick(("minecraft:cobweb", 2), ("minecraft:skeleton_skull[rotation=6]", 1), ("minecraft:bone_block", 1),
                      ("minecraft:candle[candles=2,lit=true]", 3)))


def gate():
    """The fog gate: an archway. The fog itself is particles (threshold.js); barrier blocks seal it in a fight."""
    g = LAYOUT["gate"]
    fill(GATE_X, Y + 1, -5, GATE_X, Y + 8, -4, "minecraft:polished_blackstone_bricks")
    fill(GATE_X, Y + 1, 4, GATE_X, Y + 8, 5, "minecraft:polished_blackstone_bricks")
    fill(GATE_X, Y + 7, -3, GATE_X, Y + 8, 3, "minecraft:polished_blackstone_bricks")
    fill(GATE_X, g["y1"], g["z1"], GATE_X, Y + 6, g["z2"], "minecraft:air")
    setblock(GATE_X, Y + 8, 0, "minecraft:chiseled_polished_blackstone")
    setblock(GATE_X + 1, Y + 7, -3, "minecraft:soul_lantern[hanging=true]")
    setblock(GATE_X + 1, Y + 7, 3, "minecraft:soul_lantern[hanging=true]")


def arena():
    cx, cz, r = ARENA["cx"], ARENA["cz"], ARENA["r"]
    # rim wall, broken in places, with standing braziers
    for a in range(0, 360, 2):
        x = round(cx + (r + 1) * math.cos(math.radians(a)))
        z = round(cz + (r + 1) * math.sin(math.radians(a)))
        if abs(z) <= 4 and (x > cx or x < cx):                    # leave the east (gate) and west (exit) mouths
            if x > cx and x >= GATE_X - 2 or x < cx and x <= EXIT_X + 2:
                continue
        height = rng.choice((3, 4, 4, 5, 6)) if rng.random() > 0.12 else 1
        for y in range(Y + 1, Y + 1 + height):
            setblock(x, y, z, pick(*WALL))
    for a in range(20, 360, 45):
        x = round(cx + (r - 1) * math.cos(math.radians(a)))
        z = round(cz + (r - 1) * math.sin(math.radians(a)))
        fill(x, Y + 1, z, x, Y + 3, z, "minecraft:polished_blackstone_bricks")
        setblock(x, Y + 4, z, "minecraft:campfire[lit=true,signal_fire=false]")
    # a circle of broken pillars, and the scorched ground where the Gatekeeper stands
    for a in range(0, 360, 60):
        x = round(cx + 9 * math.cos(math.radians(a + 30)))
        z = round(cz + 9 * math.sin(math.radians(a + 30)))
        h = rng.randint(2, 7)
        fill(x, Y + 1, z, x, Y + h, z, "minecraft:deepslate_bricks")
        if h > 4:
            setblock(x, Y + h + 1, z, "minecraft:deepslate_brick_slab[type=bottom]")
    for _ in range(90):
        a, d = rng.uniform(0, 2 * math.pi), rng.uniform(0, 6)
        setblock(round(cx - 6 + d * math.cos(a)), Y, round(cz + d * math.sin(a)),
                 pick(("minecraft:soul_soil", 3), ("minecraft:magma_block", 1), ("minecraft:blackstone", 2)))
    for _ in range(40):
        a, d = rng.uniform(0, 2 * math.pi), rng.uniform(3, r - 2)
        setblock(round(cx + d * math.cos(a)), Y + 1, round(cz + d * math.sin(a)),
                 pick(("minecraft:skeleton_skull[rotation=2]", 1), ("minecraft:bone_block", 1),
                      ("minecraft:cobblestone_slab[type=bottom]", 2), ("minecraft:dead_bush", 1)))


def exit_door():
    """The Ember Door: crying obsidian frame, soul fire light. Particles and the check live in threshold.js."""
    d = LAYOUT["exit_door"]
    fill(EXIT_X, Y + 1, -4, EXIT_X, Y + 6, -3, "minecraft:crying_obsidian")
    fill(EXIT_X, Y + 1, 3, EXIT_X, Y + 6, 4, "minecraft:crying_obsidian")
    fill(EXIT_X, Y + 5, -2, EXIT_X, Y + 6, 2, "minecraft:crying_obsidian")
    fill(EXIT_X, d["y1"], d["z1"], EXIT_X, d["y2"], d["z2"], "minecraft:barrier")
    setblock(EXIT_X + 1, Y + 1, -3, "minecraft:soul_campfire[lit=true,signal_fire=false]")
    setblock(EXIT_X + 1, Y + 1, 3, "minecraft:soul_campfire[lit=true,signal_fire=false]")


def stair_and_waygate():
    s = STAIR
    for x in range(s["x1"], s["x2"] + 1):
        h = stair_height(x)
        for z in (s["z1"] - 1, s["z2"] + 1):
            if rng.random() > 0.3:
                fill(x, Y + h + 1, z, x, Y + h + rng.randint(1, 2), z, pick(*WALL))
        if x % 4 == 0:
            setblock(x, Y + h + 1, s["z1"], "minecraft:candle[candles=4,lit=true]")
    # the Waygate: a ring of standing stones around a crying-obsidian arch that faces the sun
    top = Y + 6
    for a in range(0, 360, 30):
        x = round(-116 + 6 * math.cos(math.radians(a)))
        z = round(6 * math.sin(math.radians(a)))
        fill(x, top + 1, z, x, top + rng.randint(2, 4), z, "minecraft:polished_blackstone_bricks")
    fill(-119, top + 1, -2, -119, top + 6, -2, "minecraft:crying_obsidian")
    fill(-119, top + 1, 2, -119, top + 6, 2, "minecraft:crying_obsidian")
    fill(-119, top + 6, -1, -119, top + 6, 1, "minecraft:crying_obsidian")
    setblock(-119, top + 7, 0, "minecraft:gilded_blackstone")
    setblock(-116, top, 0, "minecraft:lodestone")


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def advancement(key, icon, title, desc, frame="task", hidden=False):
    write_json(DATA / "advancement" / "threshold" / f"{key}.json", {
        **({"parent": "remnants:threshold/woke"} if key != "woke" else {}),
        "display": {"icon": {"id": icon}, "title": {"text": title}, "description": {"text": desc},
                    "frame": frame, "show_toast": True, "announce_to_chat": key == "gatekeeper", "hidden": hidden,
                    **({"background": "minecraft:textures/block/deepslate_tiles.png"} if key == "woke" else {})},
        "criteria": {"granted": {"trigger": "minecraft:impossible"}}})


def main():
    write_json(DATA / "dimension_type" / "threshold.json", {
        "ultrawarm": False, "natural": False, "piglin_safe": False, "respawn_anchor_works": False,
        "bed_works": False, "has_raids": False, "has_skylight": True, "has_ceiling": False,
        "coordinate_scale": 1.0, "ambient_light": 0.0, "fixed_time": 12350, "logical_height": 256,
        "height": 256, "min_y": 0, "infiniburn": "#minecraft:infiniburn_overworld",
        "effects": "minecraft:overworld", "monster_spawn_light_level": 0, "monster_spawn_block_light_limit": 0})
    write_json(DATA / "dimension" / "threshold.json", {
        "type": "remnants:threshold",
        "generator": {"type": "minecraft:flat", "settings": {
            "biome": "minecraft:the_void", "layers": [], "lakes": False, "features": False,
            "structure_overrides": []}}})
    foundation()
    floor()
    crypt()
    hall()
    gate()
    arena()
    exit_door()
    stair_and_waygate()
    fn = DATA / "function" / "threshold" / "build.mcfunction"
    fn.parent.mkdir(parents=True, exist_ok=True)
    fn.write_text(f"# Generated by tools/build_threshold.py (layout v{BUILD_VERSION}). Run in remnants:threshold.\n"
                  "kill @e[tag=remnants_threshold]\n" + "\n".join(cmds) + "\n")
    advancement("woke", "minecraft:skeleton_skull", "The Threshold", "Wake in the crypt where the Ashborn rise.")
    advancement("gatekeeper", "minecraft:wither_skeleton_skull", "Gatekeeper Felled",
                "Fell Ser Odric, Gatekeeper of the Threshold.", frame="challenge")
    advancement("beyond", "minecraft:lodestone", "Beyond the Gate", "Step through the Waygate into the world.",
                frame="goal")
    LAYOUT_JS.parent.mkdir(parents=True, exist_ok=True)
    LAYOUT_JS.write_text("// priority: 100\n// Generated by tools/build_threshold.py. Do not edit.\n"
                         f"global.THRESHOLD = {json.dumps(LAYOUT, indent=2)}\n")
    print(f"{len(cmds)} commands -> {fn.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
