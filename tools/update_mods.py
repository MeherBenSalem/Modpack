#!/usr/bin/env python3
"""Move every mod in src/mods.json to its newest Minecraft 1.21.1 NeoForge file on Modrinth and CurseForge.

  python3 tools/update_mods.py            # report what would change
  python3 tools/update_mods.py --write    # update src/mods.json (then build_pack.py --export, check_cf.py, tests)
  python3 tools/update_mods.py --only omnivault,chronofall --write

Modrinth: /v2/project/{id}/version filtered to neoforge + 1.21.1, newest release or beta (alphas are skipped).
CurseForge: the newest file tagged 1.21.1 + NeoForge in api.cfwidget.com's file list for the project and in
curseforge.com's own file list (cfwidget can be hours behind: on 2026-11-10 it still showed FancyMenu 3.9.14 while
3.10.0 was public). Resource packs (folder "resourcepacks") have no loader tag, so they are matched on 1.21.1 alone.
Fresh answers every run; no cache.

A mod only moves when BOTH platforms have the same new version (same file name, or the same version number in it),
so the CurseForge zip, the server pack built from CurseForge files and the Modrinth pack never drift apart; a
version that is public on one platform only is reported as "waiting" and the mod stays where it is.
"""
import argparse
import json
import re
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


def newest_modrinth(project_id, resource_pack=False):
    query = {"game_versions": json.dumps([MC])}
    if not resource_pack:
        query["loaders"] = json.dumps([LOADER])
    versions = get_json(f"https://api.modrinth.com/v2/project/{project_id}/version?{urllib.parse.urlencode(query)}")
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


def _cf_wanted(versions, resource_pack):
    return MC in versions and (resource_pack or "NeoForge" in versions)


def cfwidget_files(project_id, resource_pack):
    d = get_json(f"https://api.cfwidget.com/{project_id}")
    return [{"file_id": f["id"], "filename": f["name"], "date": f.get("uploaded_at", "")}
            for f in d.get("files", []) if _cf_wanted(f.get("versions", []), resource_pack)
            and f.get("type") in ("release", "beta", None)]


def curseforge_site_files(project_id, resource_pack, pages=3):
    """curseforge.com's own list, newest first: public (approved) release and beta files only."""
    out = []
    for page in range(pages):
        d = get_json(f"https://www.curseforge.com/api/v1/mods/{project_id}/files?pageIndex={page}&pageSize=50"
                     "&sort=dateCreated&sortDescending=true", tries=3)
        data = d.get("data") if isinstance(d, dict) else None
        if not data:
            break
        out += [{"file_id": f["id"], "filename": f["fileName"], "date": f.get("dateCreated", "")}
                for f in data if _cf_wanted(f.get("gameVersions", []), resource_pack)
                and f.get("status") == 4 and f.get("releaseType") in (1, 2)]
        if out or len(data) < 50:
            break
    return out


def newest_curseforge(project_id, resource_pack=False):
    files = cfwidget_files(project_id, resource_pack) + curseforge_site_files(project_id, resource_pack)
    if not files:
        return None
    f = max(files, key=lambda f: (f["date"][:19], f["file_id"]))
    return {"project_id": project_id, "file_id": f["file_id"], "filename": f["filename"], "date": f["date"]}


def same_release(mr, cf):
    """True when the Modrinth and the CurseForge file are the same release: equal names, or names that differ only
    in punctuation or a platform suffix (particlerain-4.0.3+1.21.1 / particlerain-4.0.3-1.21.1,
    FreshAnimations_v1.11.2_1.20+.zip / FreshAnimations_v1.11.2_1.20.zip, Terralith_1.21.1_v2.6.2_Neoforge /
    Terralith_1.21.x_v2.6.2) and carry the same version numbers."""
    def numbers(name):
        stem = re.sub(r"1\.2\d(\.\d+|\.x)?\+?", "", name.rsplit(".", 1)[0])   # the Minecraft version, however it is written
        return re.findall(r"\d+", stem)
    return mr["filename"] == cf["filename"] or numbers(mr["filename"]) == numbers(cf["filename"])


def check(m):
    mr, cf = m.get("modrinth"), m.get("curseforge")
    rp = m.get("folder") == "resourcepacks"
    new_mr = newest_modrinth(mr["project_id"], rp) if mr else None
    new_cf = newest_curseforge(cf["project_id"], rp) if cf else None
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
    changed, problems, waiting = [], [], []
    for m in todo:
        new_mr, new_cf = results[m["slug"]]
        mr, cf = m.get("modrinth"), m.get("curseforge")
        mr_newer = bool(mr and new_mr and new_mr["version_id"] != mr["version_id"])
        cf_newer = bool(cf and new_cf and new_cf["file_id"] != cf["file_id"])
        if mr and not new_mr:
            problems.append(f"{m['slug']}: no Modrinth {MC} NeoForge file found (kept {mr['version_number']})")
        if cf and not new_cf:
            problems.append(f"{m['slug']}: no CurseForge {MC} NeoForge file found (kept {cf['file_id']})")
        if not (mr_newer or cf_newer):
            continue
        if mr and cf:
            # Both platforms or neither: the newest file on each must be the same release.
            if not (new_mr and new_cf and same_release(new_mr, new_cf)):
                ahead = "Modrinth" if mr_newer and not cf_newer else "CurseForge" if cf_newer and not mr_newer else "both"
                waiting.append(f"{m['slug']}: newest differs ({ahead} ahead): MR "
                               f"{new_mr['filename'] if new_mr else '-'} / CF {new_cf['filename'] if new_cf else '-'}"
                               f"; kept {mr['version_number']}")
                continue
        line = []
        if mr_newer:
            line.append(f"MR {mr['version_number']} -> {new_mr['version_number']}")
            if args.write:
                new_mr.pop("date")
                m["modrinth"] = new_mr
        if cf_newer:
            line.append(f"CF {cf['filename']} -> {new_cf['filename']} (file {new_cf['file_id']})")
            if args.write:
                m["curseforge"] = {"project_id": cf["project_id"], "file_id": new_cf["file_id"],
                                   "filename": new_cf["filename"]}
        changed.append(f"{m['slug']}: " + "; ".join(line))
    print(f"{len(changed)} of {len(todo)} mods have newer files")
    for c in changed:
        print("  " + c)
    for w in waiting:
        print("  waiting: " + w)
    for p in problems:
        print("  ! " + p)
    if args.write and changed:
        MODS.write_text(json.dumps(mods, indent=1, ensure_ascii=False) + "\n")
        print("src/mods.json updated")


if __name__ == "__main__":
    sys.exit(main())
