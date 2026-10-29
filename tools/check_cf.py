#!/usr/bin/env python3
"""Check every CurseForge project/file id in src/mods.json against the live project (via api.cfwidget.com).

  python3 tools/check_cf.py          # exit 1 if any file isn't found in its project

A mod is WRONG when its file has another name, sits in the project under another id, or the project is a different
build (title says Forge or Fabric, not NeoForge) that doesn't list it. It is "unlisted" when the project simply doesn't
list the file; cfwidget shows only a project's newest files, so check those by hand, but both fail the run (the
owner's first import broke on exactly such ids). Responses are cached in .cache/cfwidget/ for a day.
"""
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache" / "cfwidget"


def project(pid):
    f = CACHE / f"{pid}.json"
    if f.exists() and time.time() - f.stat().st_mtime < 86400:
        return json.loads(f.read_text())
    for attempt in range(4):
        try:
            req = urllib.request.Request(f"https://api.cfwidget.com/{pid}",
                                         headers={"User-Agent": "remnants-modpack-check/1.0"})  # urllib's UA gets 403
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read())
            break
        except Exception as e:  # cfwidget answers 202 while it builds a page; retry
            if attempt == 3:
                return {"error": str(e)}
            time.sleep(2 ** attempt)
    CACHE.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(data))
    return data


def main():
    mods = json.loads((ROOT / "src" / "mods.json").read_text())
    bad, unlisted = [], []
    for m in mods:
        cf = m.get("curseforge") or {}
        if not cf.get("project_id"):
            continue
        d = project(cf["project_id"])
        if "title" not in d:
            unlisted.append(f"{m['slug']}: cfwidget error {d.get('error', d)}")
            continue
        files = {f["id"]: f for f in d.get("files", [])}
        title = d["title"]
        wrong_loader = re.search(r"\b(forge|fabric)\b", title, re.I) and not re.search(r"neoforge", title, re.I)
        if cf["file_id"] in files:
            if cf.get("filename") and files[cf["file_id"]]["name"] != cf["filename"]:
                bad.append(f"{m['slug']}: file {cf['file_id']} is {files[cf['file_id']]['name']}, expected {cf['filename']}")
        elif wrong_loader:
            bad.append(f"{m['slug']}: project {cf['project_id']} is \"{title}\" and doesn't list file {cf['file_id']}")
        elif cf.get("filename") and any(f["name"] == cf["filename"] for f in files.values()):
            bad.append(f"{m['slug']}: {cf['filename']} is in project {cf['project_id']} under another file id")
        else:
            unlisted.append(f"{m['slug']}: file {cf['file_id']} not in the newest files of \"{title}\"")
    for line in unlisted:
        print("unlisted:", line)
    for line in bad:
        print("WRONG:", line)
    print(f"{len(mods)} mods checked, {len(bad)} wrong, {len(unlisted)} unlisted")
    sys.exit(1 if bad or unlisted else 0)


if __name__ == "__main__":
    main()
