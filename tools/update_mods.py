#!/usr/bin/env python3
"""Move every mod in src/mods.json to its newest Minecraft 1.21.1 NeoForge file on Modrinth and CurseForge.

  python3 tools/update_mods.py            # report what would change
  python3 tools/update_mods.py --write    # update src/mods.json (then build_pack.py --export, check_cf.py, tests)
  python3 tools/update_mods.py --only omnivault,chronofall --write

Modrinth: /v2/project/{id}/version filtered to neoforge + 1.21.1, newest release or beta (alphas are skipped).
CurseForge: api.cfwidget.com's file list for the project, newest file tagged 1.21.1 + NeoForge (cfwidget lists a
project's recent files, which is where an update is). Fresh answers every run; no cache.
"""
import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODS = ROOT / "src" / "mods.json"
UA = "NightBeam-pack/1.0 (remnants-modpack updater)"
MC, LOADER = "1.21.1", "neoforge"


def get_json(url, tries=6):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as r:
                if r.status == 202:          # cfwidget is building the page
                    raise OSError("202")
                return json.loads(r.read())
        except Exception as e:  # noqa: BLE001 - network hiccups and cfwidget's 202 retry the same way
            if i == tries - 1:
                return {"error": str(e)}
            time.sleep(2 + 3 * i)


def newest_modrinth(project_id):
    q = urllib.parse.urlencode({"loaders": json.dumps([LOADER]), "game_versions": json.dumps([MC])})
    versions = get_json(f"https://api.modrinth.com/v2/project/{project_id}/version?{q}")
    if not isinstance(versions, list):
        return None
    versions = [v for v in versions if v.get("version_type") in ("release", "beta")]
    if not versions:
        return None
    v = max(versions, key=lambda v: v["date_published"])
    f = next((f for f in v["files"] if f.get("primary")), v["files"][0])
    return {"project_id": project_id, "version_id": v["id"], "version_number": v["version_number"],
            "filename": f["filename"], "url": f["url"], "sha1": f["hashes"]["sha1"],
            "sha512": f["hashes"]["sha512"], "size": f["size"], "date": v["date_published"]}


def newest_curseforge(project_id):
    d = get_json(f"https://api.cfwidget.com/{project_id}")
    files = [f for f in d.get("files", []) if MC in f.get("versions", []) and "NeoForge" in f.get("versions", [])
             and f.get("type") in ("release", "beta", None)]
    if not files:
        return None
    f = max(files, key=lambda f: f.get("uploaded_at", ""))
    return {"project_id": project_id, "file_id": f["id"], "filename": f["name"], "date": f.get("uploaded_at", "")}


def check(m):
    mr, cf = m.get("modrinth"), m.get("curseforge")
    new_mr = newest_modrinth(mr["project_id"]) if mr else None
    new_cf = newest_curseforge(cf["project_id"]) if cf else None
    return m["slug"], new_mr, new_cf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--only", help="comma-separated slugs")
    args = ap.parse_args()
    mods = json.loads(MODS.read_text())
    only = set(args.only.split(",")) if args.only else None
    todo = [m for m in mods if m.get("decision") in ("include", "optional") and (not only or m["slug"] in only)]
    with ThreadPoolExecutor(6) as ex:
        results = {slug: (mr, cf) for slug, mr, cf in ex.map(check, todo)}
    changed, problems = [], []
    for m in todo:
        new_mr, new_cf = results[m["slug"]]
        mr, cf = m.get("modrinth"), m.get("curseforge")
        line = []
        if mr:
            if not new_mr:
                problems.append(f"{m['slug']}: no Modrinth {MC} NeoForge file found (kept {mr['version_number']})")
            elif new_mr["version_id"] != mr["version_id"]:
                line.append(f"MR {mr['version_number']} -> {new_mr['version_number']}")
                if args.write:
                    new_mr.pop("date")
                    m["modrinth"] = new_mr
        if cf:
            if not new_cf:
                problems.append(f"{m['slug']}: no CurseForge {MC} NeoForge file in cfwidget's list (kept {cf['file_id']})")
            elif new_cf["file_id"] != cf["file_id"]:
                line.append(f"CF {cf['filename']} -> {new_cf['filename']}")
                if args.write:
                    m["curseforge"] = {"project_id": cf["project_id"], "file_id": new_cf["file_id"],
                                       "filename": new_cf["filename"]}
        if mr and cf and new_mr and new_cf and new_mr["filename"] != new_cf["filename"]:
            line.append(f"(names differ: MR {new_mr['filename']} / CF {new_cf['filename']})")
        if line:
            changed.append(f"{m['slug']}: " + "; ".join(line))
    print(f"{len(changed)} of {len(todo)} mods have newer files")
    for c in changed:
        print("  " + c)
    for p in problems:
        print("  ! " + p)
    if args.write and changed:
        MODS.write_text(json.dumps(mods, indent=1, ensure_ascii=False) + "\n")
        print("src/mods.json updated")


if __name__ == "__main__":
    sys.exit(main())
