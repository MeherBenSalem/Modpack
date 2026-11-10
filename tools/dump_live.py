#!/usr/bin/env python3
"""Dump what the game really registers into research/registry/live/, for tools/validate_pack.py.

  python3 tools/build_pack.py --export && python3 tools/dump_live.py [--xmx 6G]
  python3 tools/dump_live.py --from run/serverpack/kubejs/exported/live     # compact an existing raw dump

Boots the server pack exactly as tools/test_server.py does, with one extra KubeJS script (tools/dev/dump_live.js,
never shipped) that writes, once the server has loaded, every id the game registered and every recipe it ended up
with: after all mods, datapacks and the pack's own KubeJS scripts (forge.js removes and rebuilds hundreds of
recipes, so the jars alone do not say what a player can craft). The raw dump is then compacted into

  research/registry/live/ids.json       item, block, entity_type, structure, biome, dimension, advancement,
                                        loot_table, command: sorted id lists (recipe-unlock advancements left out)
  research/registry/live/tags.json      item, structure, entity_type and biome tags -> members
  research/registry/live/recipes.json   recipe id -> {"t": type, "o": [output items], "i": [[alternatives], ...]}
                                        (one entry per ingredient slot, so amounts can be counted; an
                                        alternative is an item id or "#tag"; fluids are left out)
  research/registry/live/loot.json      loot table id -> {"i": [items], "t": [item tags], "r": [other tables]}
                                        (empty tables left out), and "natural_blocks": every block a worldgen
                                        feature places

Commit the files with the mod update that changed them: the validator and CI read them without booting.
"""
import argparse
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "research" / "registry" / "live"
SCRIPT = ROOT / "tools" / "dev" / "dump_live.js"
sys.path.insert(0, str(ROOT / "tools"))

OUTPUT_KEYS = ("result", "results", "output", "outputs")
# Keys that never hold an ingredient (outputs, metadata, and blocks/fluids/entities a machine recipe names).
SKIP_KEYS = set(OUTPUT_KEYS) | {
    "type", "category", "group", "pattern", "show_notification", "experience", "cookingtime", "processing_time",
    "heat_requirement", "neoforge:conditions", "conditions", "sound", "recipe_book_tab", "transitional_item",
    "fluid", "fluid_tag", "fluids", "block", "entity", "amount", "count", "chance", "id", "components",
    "kubejs:ingredient_actions"}


def outputs_of(recipe):
    """Every item a recipe can produce (Create's processing recipes list several, some by chance)."""
    out = []

    def take(v):
        if isinstance(v, str):
            out.append(v)
        elif isinstance(v, list):
            for x in v:
                take(x)
        elif isinstance(v, dict):
            item = v.get("id") or v.get("item")
            if isinstance(item, str) and "fluid" not in v and v.get("type") != "fluid_stack":
                out.append(item)
            elif isinstance(item, dict):
                take(item)
    for key in OUTPUT_KEYS:
        if key in recipe:
            take(recipe[key])
    return sorted(set(out))


def alternatives(node):
    """One ingredient -> the list of things that satisfy it ('mod:item' or '#tag'); None if it is not an item
    ingredient (a fluid, an empty slot)."""
    if isinstance(node, str):
        return [node]
    if isinstance(node, list):
        alts = []
        for x in node:
            alts += alternatives(x) or []
        return alts or None
    if not isinstance(node, dict):
        return None
    kind = node.get("type", "")
    if "fluid" in kind or "fluid" in node or "fluid_tag" in node:
        return None
    if isinstance(node.get("item"), str):
        return [node["item"]]
    if isinstance(node.get("tag"), str):
        return ["#" + node["tag"]]
    if isinstance(node.get("items"), (list, str)):          # neoforge:components and friends
        items = node["items"]
        return [items] if isinstance(items, str) else [i for i in items if isinstance(i, str)] or None
    if isinstance(node.get("children"), list):               # neoforge:compound: any child
        return alternatives(node["children"])
    for key in ("base", "ingredient"):                       # neoforge:difference, wrapped ingredients
        if key in node and kind:
            return alternatives(node[key])
    return None


SINGLE = ("ingredient", "template", "base", "addition", "tool", "container", "input")   # one ingredient each
LISTS = ("ingredients", "inputs")                                                       # a list: all are needed


def inputs_of(recipe):
    """Every ingredient of a recipe as a list of alternative lists (all of them are needed)."""
    needs = []

    def add(node):
        alts = alternatives(node)
        if alts:
            needs.append(sorted(set(alts)))

    def walk(node):
        if isinstance(node, list):
            for v in node:
                walk(v)
            return
        if not isinstance(node, dict):
            return
        if isinstance(node.get("item"), str) or isinstance(node.get("tag"), str):
            return add(node)                                  # an ingredient somewhere a mod put it
        for k, v in node.items():
            if k in SKIP_KEYS:
                continue
            if k == "key" and isinstance(v, dict):            # shaped: one entry per slot the letter fills
                grid = "".join(node.get("pattern", []))
                for letter, ing in sorted(v.items()):
                    for _ in range(grid.count(letter) if grid else 1):
                        add(ing)
            elif k in SINGLE:
                add(v)
            elif k in LISTS and isinstance(v, list):
                for ing in v:
                    add(ing)
            else:
                walk(v)
    walk(recipe)
    return needs


def loot_of(table):
    """Items, item tags and other loot tables a loot table can hand out."""
    items, tags, refs = set(), set(), set()

    def walk(node):
        if isinstance(node, list):
            for v in node:
                walk(v)
        elif isinstance(node, dict):
            kind = str(node.get("type", "")).split(":")[-1]
            if kind == "item" and isinstance(node.get("name"), str):
                items.add(node["name"])
            elif kind == "tag" and isinstance(node.get("name"), str):
                tags.add(node["name"])
            elif kind == "loot_table":
                ref = node.get("value", node.get("name"))
                if isinstance(ref, str):
                    refs.add(ref)
                else:
                    walk(ref)                                  # an inline table
            for k in ("pools", "entries", "children"):
                if k in node:
                    walk(node[k])
    walk(table)
    return {"i": sorted(items), "t": sorted(tags), "r": sorted(refs)}


def compact(raw):
    ids = json.loads((raw / "ids.json").read_text())
    tags = json.loads((raw / "tags.json").read_text())
    recipes = json.loads((raw / "recipes.json").read_text())
    done = json.loads((raw / "done.json").read_text())
    if done.get("failed"):
        print(f"WARNING: {len(done['failed'])} entries could not be encoded: {done['failed'][:5]}")
    ids["advancement"] = [a for a in ids["advancement"] if "recipes/" not in a.split(":", 1)[1]]
    out_recipes = {}
    for rid, text in sorted(recipes.items()):
        r = json.loads(text)
        needs = inputs_of(r)
        transitional = r.get("transitional_item")
        if isinstance(transitional, dict):                    # Create's sequenced assembly makes this on the way
            t = transitional.get("id") or transitional.get("item")
            needs = [[a for a in alts if a != t] for alts in needs]
            needs = [alts for alts in needs if alts]
        out_recipes[rid] = {"t": r.get("type", ""), "o": outputs_of(r), "i": needs}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "ids.json").write_text(json.dumps(ids, indent=0, sort_keys=True) + "\n")
    keep = {k: tags.get(k, {}) for k in ("item", "structure", "entity_type", "biome")}
    (OUT / "tags.json").write_text(json.dumps(keep, separators=(",", ":"), sort_keys=True) + "\n")

    def one_per_line(mapping):
        lines = [f"{json.dumps(k)}:{json.dumps(v, separators=(',', ':'))}" for k, v in mapping.items()]
        return "{\n" + ",\n".join(lines) + "\n}\n"

    (OUT / "recipes.json").write_text(one_per_line(out_recipes))
    loot = {}
    for tid, text in sorted(json.loads((raw / "loot.json").read_text()).items()):
        entry = loot_of(json.loads(text))
        if entry["i"] or entry["t"] or entry["r"]:
            loot[tid] = entry
    natural = set()
    for text in json.loads((raw / "features.json").read_text()).values():
        natural.update(re.findall(r'"Name":"([a-z0-9_.-]+:[a-z0-9_./-]+)"', text))
    loot["natural_blocks"] = sorted(natural)
    (OUT / "loot.json").write_text(one_per_line(loot))
    print(f"{len(ids['item'])} items, {len(ids['advancement'])} advancements, {len(ids['structure'])} structures, "
          f"{len(out_recipes)} recipes, {len(loot) - 1} loot tables, {len(natural)} worldgen blocks "
          f"-> {OUT.relative_to(ROOT)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="raw", help="compact this raw dump folder instead of booting a server")
    ap.add_argument("--xmx", help="test only: server heap, e.g. 5G on a small machine")
    ap.add_argument("--dir", default=str(ROOT / "run" / "dumplive"))
    ap.add_argument("--port", type=int, default=25598)
    args = ap.parse_args()
    if args.raw:
        return compact(Path(args.raw))
    import test_server
    meta = json.loads((ROOT / "src" / "pack.json").read_text())
    run = Path(args.dir).resolve()
    lf = test_server.lock(run)
    try:
        test_server.unpack(test_server.server_zip(meta), run, False)
        test_server.prepare(run, args.port, args.xmx)
        shutil.copy2(SCRIPT, run / "kubejs" / "server_scripts" / "zz_dump_live.js")
        done, _ = test_server.run_server(run, [], 1200, 0, args.port)
    finally:
        lf.unlink(missing_ok=True)
    raw = run / "kubejs" / "exported" / "live"
    if not done or not (raw / "done.json").exists():
        sys.exit(f"the server did not finish loading or wrote no dump; see {run / 'logs' / 'latest.log'}")
    compact(raw)


if __name__ == "__main__":
    sys.exit(main())
