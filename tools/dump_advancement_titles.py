#!/usr/bin/env python3
"""Index the title of every advancement the pack's mods (and Minecraft, and the pack's KubeJS data) define.

  python3 tools/dump_advancement_titles.py [jar dirs...]   # default: run/client/mods and run/client/versions

Writes research/registry/advancement_titles.json: advancement id -> {"key": translation key} or {"text": literal}.
tools/build_quests.py uses it to name advancement tasks that have no title of their own ("lang:<key>", so the
book shows the advancement's name in the player's language). Run it after tools/test_client.py has downloaded the
mods (or point it at any folder of the pack's jars).
"""
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "research" / "registry" / "advancement_titles.json"
PATH = re.compile(r"^data/([^/]+)/advancements?/(.+)\.json$")


def title_of(data):
    display = data.get("display") if isinstance(data, dict) else None
    if not isinstance(display, dict):
        return None
    t = display.get("title")
    if isinstance(t, str):
        return {"text": t}
    if isinstance(t, dict):
        if t.get("translate"):
            return {"key": t["translate"]}
        if t.get("text"):
            return {"text": t["text"]}
    return None


def scan(name, read, out):
    for entry in name:
        m = PATH.match(entry)
        if not m:
            continue
        try:
            title = title_of(json.loads(read(entry)))
        except (ValueError, UnicodeDecodeError):
            continue
        if title:
            out.setdefault(f"{m.group(1)}:{m.group(2)}", title)


def main():
    dirs = [Path(a) for a in sys.argv[1:]] or [ROOT / "run" / "client" / "mods", ROOT / "run" / "client" / "versions"]
    out = {}
    kubejs = ROOT / "pack" / "kubejs"
    files = [f.relative_to(kubejs).as_posix() for f in kubejs.glob("data/*/advancement*/**/*.json")]
    scan(files, lambda e: (kubejs / e).read_text(), out)  # the pack's own advancements win
    jars = [j for d in dirs for j in sorted(d.rglob("*.jar"))]
    for jar in jars:
        try:
            with zipfile.ZipFile(jar) as z:
                scan(z.namelist(), lambda e: z.read(e).decode("utf8"), out)
        except zipfile.BadZipFile:
            continue
    if not out:
        sys.exit("no advancements found; run tools/test_client.py first or pass a folder of jars")
    OUT.write_text(json.dumps(dict(sorted(out.items())), indent=1, ensure_ascii=False) + "\n")
    print(f"{len(out)} advancement titles from {len(jars)} jars -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
