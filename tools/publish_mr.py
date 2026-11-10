#!/usr/bin/env python3
"""Upload a built release to Modrinth: the .mrpack as a new version of the modpack project.

  MODRINTH_TOKEN=... python3 tools/publish_mr.py --project <id> --changelog marketing/changelog/1.0.0-beta.11.md

Reads the version and Minecraft/NeoForge versions from src/pack.json and the .mrpack from dist/ (run
`python3 tools/build_pack.py --export` first). Uses the Modrinth API (POST /v2/version, multipart `data` + the file,
with the token in the Authorization header). The token is never printed. `--dry-run` prints the metadata and stops.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "https://api.modrinth.com/v2"
UA = "NightBeam-pack/1.0 (remnants-modpack publisher)"


def multipart(data, path):
    boundary = uuid.uuid4().hex
    head = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"data\"\r\n"
            f"Content-Type: application/json\r\n\r\n{json.dumps(data)}\r\n"
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{path.name}\"\r\n"
            f"Content-Type: application/x-modrinth-modpack+zip\r\n\r\n").encode()
    tail = f"\r\n--{boundary}--\r\n".encode()
    return head + path.read_bytes() + tail, f"multipart/form-data; boundary={boundary}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True, help="the Modrinth project id or slug")
    ap.add_argument("--changelog", required=True, help="markdown file with the patch notes")
    ap.add_argument("--release-type", default="beta", choices=["alpha", "beta", "release"])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    token = os.environ.get("MODRINTH_TOKEN", "").strip()
    if not token and not args.dry_run:
        sys.exit("MODRINTH_TOKEN is not set")
    meta = json.loads((ROOT / "src" / "pack.json").read_text())
    mrpack = ROOT / "dist" / f"{meta['file_name']}-{meta['version']}.mrpack"
    if not mrpack.exists():
        sys.exit(f"{mrpack.relative_to(ROOT)} not found; run build_pack.py --export")
    data = {"name": f"{meta['name']} {meta['version']}", "version_number": meta["version"],
            "changelog": (ROOT / args.changelog).read_text(), "dependencies": [],
            "game_versions": [meta["minecraft"]], "version_type": args.release_type, "loaders": ["neoforge"],
            "featured": True, "status": "listed", "project_id": args.project,
            "file_parts": ["file"], "primary_file": "file"}
    if args.dry_run:
        print(json.dumps({**data, "changelog": "...", "file": mrpack.name}, indent=1))
        return
    if not args.project.isalnum() or len(args.project) != 8:  # a slug: the API wants the id
        req = urllib.request.Request(f"{API}/project/{args.project}", headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            data["project_id"] = json.load(r)["id"]
    body, ctype = multipart(data, mrpack)
    print(f"uploading {mrpack.name} ({mrpack.stat().st_size / 1e6:.1f} MB)...", flush=True)
    req = urllib.request.Request(f"{API}/version", data=body, method="POST",
                                 headers={"Authorization": token, "User-Agent": UA, "Content-Type": ctype})
    try:
        with urllib.request.urlopen(req, timeout=3600) as r:
            out = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Modrinth upload failed: HTTP {e.code}: {e.read().decode('utf8', 'replace')[:500]}")
    print(f"Modrinth version {out['id']} ({out['version_number']}) uploaded")


if __name__ == "__main__":
    main()
