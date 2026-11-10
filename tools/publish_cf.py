#!/usr/bin/env python3
"""Upload a built release to CurseForge: the modpack zip, then the server pack as its additional file.

  CF_API_TOKEN=... python3 tools/publish_cf.py --project 1772691 --changelog marketing/changelog/1.0.0-beta.6.md

Reads the version and Minecraft version from src/pack.json and the files from dist/ (run
`python3 tools/build_pack.py --export` first). Uses the CurseForge Upload API (X-Api-Token, POST
/api/projects/{id}/upload-file with multipart `metadata` + `file`); the server pack is uploaded with `parentFileID`
set to the modpack file, which is how CurseForge attaches server packs. The token is never printed.
`--dry-run` prints the metadata and stops before uploading.
"""
import argparse
import time
import json
import os
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "https://minecraft.curseforge.com"
UA = "NightBeam-pack/1.0 (remnants-modpack publisher)"


def call(method, path, token, body=None, content_type=None, timeout=60):
    req = urllib.request.Request(API + path, data=body, method=method,
                                 headers={"X-Api-Token": token, "User-Agent": UA, "Accept": "application/json"})
    if content_type:
        req.add_header("Content-Type", content_type)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf8", "replace")


def multipart(metadata, path):
    boundary = uuid.uuid4().hex
    head = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"metadata\"\r\n"
            f"Content-Type: application/json\r\n\r\n{json.dumps(metadata)}\r\n"
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{path.name}\"\r\n"
            f"Content-Type: application/zip\r\n\r\n").encode()
    tail = f"\r\n--{boundary}--\r\n".encode()
    return head + path.read_bytes() + tail, f"multipart/form-data; boundary={boundary}"


def game_version_ids(token, mc):
    status, text = call("GET", "/api/game/versions", token)
    if status != 200:
        sys.exit(f"game versions: HTTP {status}: {text[:300]}")
    versions = json.loads(text)
    mc_ids = [v["id"] for v in versions if v.get("name") == mc]
    neo_ids = [v["id"] for v in versions if v.get("slug") == "neoforge" or v.get("name") == "NeoForge"]
    if not mc_ids:
        sys.exit(f"CurseForge has no game version named {mc}")
    return mc_ids[:1], neo_ids[:1]


def upload(token, project, metadata, path):
    body, ctype = multipart(metadata, path)
    print(f"uploading {path.name} ({path.stat().st_size / 1e6:.1f} MB)...", flush=True)
    status, text = call("POST", f"/api/projects/{project}/upload-file", token, body, ctype, timeout=3600)
    return status, text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", type=int, required=True)
    ap.add_argument("--changelog", required=True, help="markdown file with the patch notes")
    ap.add_argument("--release-type", default="beta", choices=["alpha", "beta", "release"])
    ap.add_argument("--server-for", type=int, metavar="FILE_ID",
                    help="upload only the server pack, under this already uploaded modpack file")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    token = os.environ.get("CF_API_TOKEN", "").strip()
    if not token and not args.dry_run:
        sys.exit("CF_API_TOKEN is not set")
    meta = json.loads((ROOT / "src" / "pack.json").read_text())
    dist = ROOT / "dist"
    client = next(iter(sorted(dist.glob(f"*{meta['version']}-curseforge.zip"))), None)
    server = next(iter(sorted(dist.glob(f"*{meta['version']}-server.zip"))), None)
    if not client or not server:
        sys.exit(f"dist/ has no {meta['version']} CurseForge and server zips; run build_pack.py --export")
    changelog = (ROOT / args.changelog).read_text()
    title = meta["name"]
    pack_meta = {"changelog": changelog, "changelogType": "markdown", "releaseType": args.release_type,
                 "displayName": f"{title} {meta['version']}"}
    server_meta = {"changelog": changelog, "changelogType": "markdown", "releaseType": args.release_type,
                   "displayName": f"{title} {meta['version']} Server Pack"}
    if args.dry_run:
        print(json.dumps({"client": client.name, "server": server.name, "pack": {**pack_meta, "changelog": "..."},
                          "server_pack": {**server_meta, "changelog": "..."}}, indent=1))
        return
    if args.server_for:
        return upload_server(token, args.project, server_meta, server, args.server_for)
    mc_ids, neo_ids = game_version_ids(token, meta["minecraft"])
    status, text = 0, ""
    for versions in (mc_ids + neo_ids, mc_ids):          # modpacks may refuse a loader version; retry without it
        status, text = upload(token, args.project, {**pack_meta, "gameVersions": versions}, client)
        if status == 200 or "version" not in text.lower():
            break
    if status != 200:
        sys.exit(f"modpack upload failed: HTTP {status}: {text[:500]}")
    file_id = json.loads(text)["id"]
    print(f"modpack file {file_id} uploaded")
    upload_server(token, args.project, server_meta, server, file_id)


def upload_server(token, project, server_meta, server, file_id):
    """Attach the server pack to modpack file `file_id`. A server error (5xx) is retried twice: the modpack file is
    already up, so starting over would upload it a second time. If it still fails, run the workflow again with
    server_for set to file_id."""
    status, text = 0, ""
    for attempt in range(3):
        if attempt:
            print(f"HTTP {status}; retrying in {30 * attempt} s", flush=True)
            time.sleep(30 * attempt)
        status, text = upload(token, project, {**server_meta, "parentFileID": file_id}, server)
        if status < 500:
            break
    if status != 200:
        sys.exit(f"server pack upload failed (the modpack file {file_id} is up; rerun with server_for={file_id}): "
                 f"HTTP {status}: {text[:500]}")
    print(f"server pack file {json.loads(text)['id']} uploaded under {file_id}")


if __name__ == "__main__":
    main()
