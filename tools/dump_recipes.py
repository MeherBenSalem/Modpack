#!/usr/bin/env python3
"""Index every recipe the pack ships, for designing progression gates.

  python3 tools/dump_recipes.py                 # writes .cache/recipes.json
  python3 tools/dump_recipes.py --find omnivault:terminal [--uses]

Reads data/<ns>/recipe/**.json from every included mod jar in .cache/jars/<sha1>/ (and the vanilla data jar copied to
.cache/vanilla-1.21.1-extra.jar). Each entry: type, result item, and the flat list of ingredient items/tags
(`#tag`), so a gate can be checked against what a recipe really needs. NeoForge conditions are kept as-is.
"""
import argparse
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JARS = ROOT / ".cache" / "jars"
OUT = ROOT / ".cache" / "recipes.json"
VANILLA = ROOT / ".cache" / "vanilla-1.21.1-extra.jar"


def ingredients(node, out):
    """Collect item ids and #tags from any ingredient shape (vanilla, NeoForge, Create, FD...)."""
    if isinstance(node, dict):
        if "item" in node and isinstance(node["item"], str):
            out.append(node["item"])
        if "tag" in node and isinstance(node["tag"], str):
            out.append("#" + node["tag"])
        if "id" in node and isinstance(node["id"], str) and ("count" in node or len(node) == 1):
            out.append(node["id"])
        for k, v in node.items():
            if k in ("result", "results", "output", "type", "conditions", "neoforge:conditions", "id", "item", "tag"):
                continue
            ingredients(v, out)
    elif isinstance(node, list):
        for v in node:
            ingredients(v, out)
    return out


def result_of(r):
    for key in ("result", "output", "results"):
        v = r.get(key)
        if v is None:
            continue
        if isinstance(v, list):
            v = v[0] if v else None
        if isinstance(v, dict):
            return v.get("id") or v.get("item")
        if isinstance(v, str):
            return v
    return None


def included_jars():
    """Jars are cached by sha1 (build_pack.py / test_server.py); keep the ones an included mod points at."""
    mods = json.loads((ROOT / "src" / "mods.json").read_text())
    cf_sha1 = {}
    for memo in (ROOT / ".cache" / "cf_sha1.json", ROOT / "src" / "cf_sha1.json"):
        if memo.exists():
            cf_sha1.update(json.loads(memo.read_text()))
    want = set()
    for m in mods:
        if m.get("decision") not in ("include", "optional"):
            continue
        if (m.get("modrinth") or {}).get("sha1"):
            want.add(m["modrinth"]["sha1"])
        cf = m.get("curseforge") or {}
        rec = cf_sha1.get(str(cf.get("file_id")))
        if isinstance(rec, dict) and rec.get("sha1"):
            want.add(rec["sha1"])
    return [jar for d in sorted(JARS.iterdir()) if d.is_dir() and d.name in want for jar in sorted(d.glob("*.jar"))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--find", help="item id: print recipes that make it")
    ap.add_argument("--uses", action="store_true", help="with --find: print recipes that use it instead")
    args = ap.parse_args()
    if args.find and OUT.exists():
        recipes = json.loads(OUT.read_text())
    else:
        recipes = {}
        jars = included_jars() + ([VANILLA] if VANILLA.exists() else [])
        for jar in jars:
            with zipfile.ZipFile(jar) as z:
                for n in z.namelist():
                    parts = n.split("/")
                    if len(parts) < 4 or parts[0] != "data" or parts[2] not in ("recipe", "recipes") \
                            or not n.endswith(".json"):
                        continue
                    try:
                        r = json.loads(z.read(n))
                    except Exception:
                        continue
                    rid = f"{parts[1]}:{'/'.join(parts[3:])[:-5]}"
                    recipes[rid] = {"type": r.get("type"), "result": result_of(r),
                                    "in": sorted(set(ingredients(r, []))), "jar": jar.name,
                                    "conditions": r.get("neoforge:conditions")}
        OUT.write_text(json.dumps(recipes, indent=0, sort_keys=True))
        print(f"{len(recipes)} recipes from {len(jars)} jars -> {OUT.relative_to(ROOT)}")
    if args.find:
        for rid, r in sorted(recipes.items()):
            hit = args.find in r["in"] if args.uses else r["result"] == args.find
            if hit:
                print(f"{rid}  [{r['type']}]  {r['result']}  <- {', '.join(r['in'])}")


if __name__ == "__main__":
    sys.exit(main())
