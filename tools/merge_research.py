#!/usr/bin/env python3
"""Turn the research data plus src/curation.yaml into src/mods.json (the list build_pack.py reads).

  python3 tools/merge_research.py

research/*_mods.json hold every mod that was checked (versions, hashes, sides, dependencies). src/curation.yaml
holds the pack's decisions: which slugs are in, which are optional, and why. Required dependencies of chosen mods
are pulled in automatically when the research has them, and reported when it doesn't.
"""
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
FIELDS = ("name", "slug", "category", "side", "license", "modrinth", "curseforge", "required_deps", "optional_deps")


def main():
    known = {}
    for f in sorted((ROOT / "research").glob("*_mods.json")):
        for m in json.loads(f.read_text()):
            known.setdefault(m["slug"], m)
    cur = yaml.safe_load((ROOT / "src" / "curation.yaml").read_text())
    side_fix = cur.get("side_overrides", {})
    chosen = {}
    for decision in ("include", "optional"):
        for group, entries in (cur.get(decision) or {}).items():
            for e in entries:
                slug, reason = (e, "") if isinstance(e, str) else next(iter(e.items()))
                if slug not in known:
                    sys.exit(f"{slug}: not in research/*_mods.json")
                chosen[slug] = (decision, group, reason)

    missing, added = [], []
    queue = list(chosen)
    while queue:
        slug = queue.pop()
        for dep in known[slug].get("required_deps") or []:
            if dep in chosen or dep in cur.get("provided", []):
                continue
            if dep in known:
                chosen[dep] = ("include", "library", f"required by {slug}")
                added.append(dep)
                queue.append(dep)
            else:
                missing.append(f"{dep} (required by {slug})")

    out = []
    for slug, (decision, group, reason) in sorted(chosen.items(), key=lambda kv: (kv[1][1], kv[0])):
        m = {k: known[slug].get(k) for k in FIELDS if known[slug].get(k) is not None}
        m["side"] = side_fix.get(slug, m.get("side", "both"))
        if m["side"] == "server":
            # Singleplayer runs an integrated server on the client, so "server-side" worldgen and structure mods
            # must be installed on clients too. Only client-only mods ever skip a side.
            m["side"] = "both"
        if slug in (cur.get("curseforge_overrides") or {}):
            m["curseforge"] = cur["curseforge_overrides"][slug]
        if (m.get("modrinth") or m.get("curseforge") or {}).get("filename", "").endswith(".zip"):
            m["folder"] = "resourcepacks"
        m.update(decision=decision, group=group, reason=reason or known[slug].get("reason", ""))
        if not (m.get("modrinth") or m.get("curseforge")):
            missing.append(f"{slug} (no file)")
        out.append(m)
    (ROOT / "src" / "mods.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"{len(out)} mods ({sum(1 for m in out if m['decision'] == 'optional')} optional); "
          f"{len(added)} libraries pulled in: {', '.join(sorted(added)) or '-'}")
    no_cf = [m["slug"] for m in out if not m.get("curseforge") or not m["curseforge"].get("file_id")]
    no_mr = [m["slug"] for m in out if not m.get("modrinth")]
    if no_cf:
        print(f"no CurseForge file id ({len(no_cf)}): {', '.join(no_cf)}")
    if no_mr:
        print(f"not on Modrinth ({len(no_mr)}): {', '.join(no_mr)}")
    if missing:
        print("MISSING:\n  " + "\n  ".join(missing))
        sys.exit(1)


if __name__ == "__main__":
    main()
