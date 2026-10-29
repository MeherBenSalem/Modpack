#!/usr/bin/env python3
"""Dump quest-checkable ids from every cached server jar into research/registry/ (reads jars as zip data only).

  python3 tools/dump_registry.py     # after tools/test_server.py has filled .cache/jars

For each jar: assets/<ns>/lang/en_us.json -> research/registry/<ns>_en_us.json (if not already there), and
advancement, structure, dimension and loot-table ids -> research/registry/<ns>_ids.json as {"ids": [...]}.
build_quests.py --check and build_data.py validate against these files.
"""
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "research" / "registry"
KINDS = {"advancement": "", "worldgen/structure": "", "dimension": "", "loot_table": "loot:"}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    per_ns = {}
    for jar in sorted((ROOT / ".cache" / "jars").glob("*/*.jar")):
        try:
            z = zipfile.ZipFile(jar)
        except zipfile.BadZipFile:
            continue
        for n in z.namelist():
            m = re.match(r"assets/([a-z0-9_.-]+)/lang/en_us\.json$", n)
            if m:
                dest = OUT / f"{m.group(1)}_en_us.json"
                if not dest.exists():
                    try:
                        dest.write_text(json.dumps(json.loads(z.read(n)), indent=1, ensure_ascii=False))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        pass
                continue
            m = re.match(r"data/([a-z0-9_.-]+)/(advancement|worldgen/structure|dimension|loot_table)/(.+)\.json$", n)
            if m:
                ns, kind, path = m.groups()
                per_ns.setdefault(ns, set()).add(f"{KINDS[kind]}{ns}:{path}")
    for ns, ids in per_ns.items():
        (OUT / f"{ns}_ids.json").write_text(json.dumps({"ids": sorted(ids)}, indent=1))
    print(f"{len(per_ns)} namespaces dumped to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
