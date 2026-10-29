#!/usr/bin/env python3
"""Generate the pack's data files from src/data/ into pack/kubejs/data/ (KubeJS loads it as a datapack).

- Better Combat movesets for Runeborn's armaments   (src/data/runeborn_movesets.yaml)
- Mob LootBags loot tables and the pack's boss tags (src/data/loot_bags.yaml)

Every modded id is checked against the lang dumps in research/registry/ so a typo fails the build.
"""
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "pack" / "kubejs" / "data"


def known_ids():
    ids = set()
    for f in (ROOT / "research" / "registry").glob("*_en_us.json"):
        for k in json.loads(f.read_text()):
            parts = k.split(".")
            if len(parts) >= 3 and parts[0] in ("item", "block", "entity"):
                ids.add(f"{parts[1]}:{parts[2]}")
    return ids


KNOWN = known_ids()
BAD = []


def check(i, where):
    if not i.startswith("minecraft:") and i not in KNOWN:
        BAD.append(f"{where}: {i}")


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def movesets():
    src = yaml.safe_load((ROOT / "src" / "data" / "runeborn_movesets.yaml").read_text())
    target = OUT / "runeborn" / "weapon_attributes"
    for old in target.glob("*.json"):
        old.unlink()
    n = 0
    for cls, items in src["weapons"].items():
        for item in items:
            check(f"runeborn:{item}", "moveset")
            preset = src["overrides"].get(item) or src["presets"].get(cls)
            if preset:
                write_json(target / f"{item}.json", {"parent": f"bettercombat:{preset}"})
                n += 1
    return n


def entry(item, weight, lo, hi, where):
    check(item, where)
    e = {"type": "minecraft:item", "name": item, "weight": weight}
    if (lo, hi) != (1, 1):
        e["functions"] = [{"function": "minecraft:set_count",
                           "count": {"type": "minecraft:uniform", "min": lo, "max": hi}}]
    return e


def loot_bags():
    src = yaml.safe_load((ROOT / "src" / "data" / "loot_bags.yaml").read_text())
    base = OUT / "mob_loot_bags" / "loot_table" / "bags"
    for tier, t in src["tiers"].items():
        lo, hi = t["rolls"]
        write_json(base / f"{tier}.json", {"type": "minecraft:chest", "pools": [{
            "rolls": {"type": "minecraft:uniform", "min": lo, "max": hi},
            "entries": [entry(*e, f"bag {tier}") for e in t["entries"]]}]})
        for dim, entries in src["dimensions"].items():
            write_json(base / tier / f"{dim}.json", {"type": "minecraft:chest", "pools": [{
                "rolls": 1, "entries": [entry(*e, f"bag {tier}/{dim}") for e in entries]}]})
    values = []
    for b in src["bosses"]:
        check(b, "boss tag")
        values.append({"id": b, "required": False})
    for ns in ("mob_loot_bags", "remnant_mobs"):
        write_json(OUT / ns / "tags" / "entity_type" / "bosses.json", {"replace": False, "values": values})
    return len(src["tiers"]), len(values)


def codex():
    """The Ashen Codex (Patchouli): book.json in data, categories and entries in assets (use_resource_pack)."""
    src = yaml.safe_load((ROOT / "src" / "data" / "codex.yaml").read_text())
    book = "ashen_codex"
    write_json(OUT / "remnants" / "patchouli_books" / book / "book.json", {
        "name": src["name"], "landing_text": src["landing"], "version": 1, "use_resource_pack": True,
        "model": "patchouli:book_brown", "book_texture": "patchouli:textures/gui/book_brown.png",
        "show_progress": False, "i18n": False})
    assets = ROOT / "pack" / "kubejs" / "assets" / "remnants" / "patchouli_books" / book / "en_us"
    if assets.exists():
        for old in assets.rglob("*.json"):
            old.unlink()
    n = 0
    for order, cat in enumerate(src["categories"]):
        check(cat["icon"], "codex")
        write_json(assets / "categories" / f"{cat['key']}.json", {
            "name": cat["name"], "description": cat["description"], "icon": cat["icon"], "sortnum": order})
        for eorder, e in enumerate(cat["entries"]):
            check(e["icon"], "codex")
            write_json(assets / "entries" / cat["key"] / f"{e['key']}.json", {
                "name": e["name"], "icon": e["icon"], "category": f"remnants:{cat['key']}", "sortnum": eorder,
                "pages": [{"type": "patchouli:text", "text": t} for t in e["pages"]]})
            n += 1
    return n


if __name__ == "__main__":
    n = movesets()
    tiers, bosses = loot_bags()
    entries = codex()
    print(f"{n} Runeborn movesets, {tiers} loot-bag tiers (+ Nether/End pools), {bosses} bosses tagged, "
          f"{entries} codex entries")
    if BAD:
        print("UNKNOWN IDS:\n  " + "\n  ".join(BAD))
        sys.exit(1)
