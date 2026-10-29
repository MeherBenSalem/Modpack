#!/usr/bin/env python3
"""Build Remnants | The Modpack from src/mods.json and the files in pack/.

  python3 modpack/tools/build_pack.py            # write pack/mods/*.pw.toml, pack/index.toml, pack/pack.toml
  python3 modpack/tools/build_pack.py --export   # also write dist/: CurseForge zip, Modrinth .mrpack, server mod list

src/mods.json is the curated list: one object per mod with "name", "slug", "side" (both|client|server), "decision"
(include|optional) and at least one of "modrinth" {project_id, version_id, filename, url, sha1, sha512, size} or
"curseforge" {project_id, file_id, filename}. The output is packwiz-compatible, so `packwiz refresh` and
packwiz-installer work on it later. Hashes for CurseForge-only files are downloaded once and cached in .cache/.
"""
import argparse
import hashlib
import json
import os
import sys
import tomllib
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACK = ROOT / "pack"
DIST = ROOT / "dist"
CACHE = ROOT / ".cache"
SRC = ROOT / "src"
UA = "NightBeam-pack/1.0 (remnants-modpack)"

# Files under pack/ that never go into a pack (packwiz's own metadata and editor leftovers).
SKIP_INDEX = {"pack.toml", "index.toml", ".packwizignore"}


def toml_str(s):
    return json.dumps(s, ensure_ascii=False)


def forgecdn_url(file_id, filename):
    fid = str(file_id)
    return f"https://edge.forgecdn.net/files/{fid[:-3]}/{int(fid[-3:])}/{filename}"


def cached_sha1(file_id, filename):
    """sha1 of a CurseForge file (packwiz needs it; cfwidget does not give hashes)."""
    CACHE.mkdir(exist_ok=True)
    memo = CACHE / "cf_sha1.json"
    known = json.loads(memo.read_text()) if memo.exists() else {}
    key = str(file_id)
    if key not in known:
        req = urllib.request.Request(forgecdn_url(file_id, filename), headers={"User-Agent": UA})
        h = hashlib.sha1()
        size = 0
        with urllib.request.urlopen(req, timeout=120) as r:
            for chunk in iter(lambda: r.read(1 << 16), b""):
                h.update(chunk)
                size += len(chunk)
        known[key] = {"sha1": h.hexdigest(), "size": size}
        memo.write_text(json.dumps(known, indent=1, sort_keys=True))
    return known[key]


def pw_toml(mod):
    mr, cf = mod.get("modrinth"), mod.get("curseforge")
    filename = (mr or cf)["filename"]
    lines = [f"name = {toml_str(mod['name'])}", f"filename = {toml_str(filename)}",
             f"side = {toml_str(mod.get('side', 'both'))}", ""]
    if mod.get("decision") == "optional":
        lines[3:3] = ["", "[option]", "optional = true", f"default = {str(mod.get('optional_default', True)).lower()}",
                      f"description = {toml_str(mod.get('reason', ''))}"]
    lines.append("[download]")
    if mr:
        lines += [f"url = {toml_str(mr['url'])}", 'hash-format = "sha512"', f"hash = {toml_str(mr['sha512'])}"]
    else:
        info = cached_sha1(cf["file_id"], cf["filename"])
        lines += ['hash-format = "sha1"', f"hash = {toml_str(info['sha1'])}", 'mode = "metadata:curseforge"']
    lines += ["", "[update]"]
    if cf:
        lines += ["[update.curseforge]", f"file-id = {int(cf['file_id'])}", f"project-id = {int(cf['project_id'])}"]
    if mr:
        lines += ["[update.modrinth]", f"mod-id = {toml_str(mr['project_id'])}", f"version = {toml_str(mr['version_id'])}"]
    return "\n".join(lines) + "\n"


def load_mods():
    mods = json.loads((SRC / "mods.json").read_text())
    out, seen = [], set()
    for m in mods:
        if m.get("decision") not in ("include", "optional"):
            continue
        if not (m.get("modrinth") or m.get("curseforge")):
            sys.exit(f"{m['slug']}: no Modrinth or CurseForge file")
        if m["slug"] in seen:
            sys.exit(f"{m['slug']}: listed twice")
        seen.add(m["slug"])
        out.append(m)
    return out


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_pack(mods, meta):
    mods_dir = PACK / "mods"
    mods_dir.mkdir(parents=True, exist_ok=True)
    wanted = set()
    for m in mods:
        p = mods_dir / f"{m['slug']}.pw.toml"
        p.write_text(pw_toml(m))
        wanted.add(p.name)
    for stale in mods_dir.glob("*.pw.toml"):
        if stale.name not in wanted:
            stale.unlink()

    entries = []
    for f in sorted(PACK.rglob("*")):
        rel = f.relative_to(PACK).as_posix()
        if f.is_dir() or rel in SKIP_INDEX:
            continue
        entry = [f"file = {toml_str(rel)}", f"hash = {toml_str(sha256(f))}"]
        if rel.startswith("mods/") and rel.endswith(".pw.toml"):
            entry.append("metafile = true")
        entries.append("[[files]]\n" + "\n".join(entry))
    (PACK / "index.toml").write_text('hash-format = "sha256"\n\n' + "\n\n".join(entries) + "\n")

    pack_toml = "\n".join([
        f"name = {toml_str(meta['name'])}",
        f"author = {toml_str(meta['author'])}",
        f"version = {toml_str(meta['version'])}",
        'pack-format = "packwiz:1.1.0"', "",
        "[index]", 'file = "index.toml"', 'hash-format = "sha256"', f"hash = {toml_str(sha256(PACK / 'index.toml'))}", "",
        "[versions]", f"minecraft = {toml_str(meta['minecraft'])}", f"neoforge = {toml_str(meta['neoforge'])}", ""])
    (PACK / "pack.toml").write_text(pack_toml)
    return len(entries)


def override_files():
    for f in sorted(PACK.rglob("*")):
        rel = f.relative_to(PACK).as_posix()
        if f.is_file() and rel not in SKIP_INDEX and not rel.startswith("mods/"):
            yield f, rel


def export(mods, meta):
    DIST.mkdir(exist_ok=True)
    base = f"{meta['file_name']}-{meta['version']}"
    problems = []

    # CurseForge: manifest.json + overrides/
    cf_files, not_on_cf = [], []
    for m in mods:
        cf = m.get("curseforge")
        if cf:
            cf_files.append({"projectID": int(cf["project_id"]), "fileID": int(cf["file_id"]), "required": True})
        else:
            not_on_cf.append(m["slug"])
    manifest = {"minecraft": {"version": meta["minecraft"],
                              "modLoaders": [{"id": f"neoforge-{meta['neoforge']}", "primary": True}]},
                "manifestType": "minecraftModpack", "manifestVersion": 1, "name": meta["name"],
                "version": meta["version"], "author": meta["author"], "files": cf_files, "overrides": "overrides"}
    modlist = "<ul>\n" + "".join(f"<li>{m['name']}</li>\n" for m in mods) + "</ul>\n"
    with zipfile.ZipFile(DIST / f"{base}-curseforge.zip", "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("manifest.json", json.dumps(manifest, indent=2))
        z.writestr("modlist.html", modlist)
        for f, rel in override_files():
            z.write(f, f"overrides/{rel}")
    if not_on_cf:
        problems.append(f"CurseForge export is missing {len(not_on_cf)} Modrinth-only mods: {', '.join(not_on_cf)}")

    # Modrinth: modrinth.index.json + overrides/ (client-only files go to client-overrides/ only when needed)
    env = {"both": ("required", "required"), "client": ("required", "unsupported"), "server": ("unsupported", "required")}
    mr_files, not_on_mr = [], []
    for m in mods:
        mr = m.get("modrinth")
        if not mr:
            not_on_mr.append(m["slug"])
            continue
        client, server = env[m.get("side", "both")]
        if m.get("decision") == "optional":
            client = "optional" if client == "required" else client
        mr_files.append({"path": f"mods/{mr['filename']}", "hashes": {"sha1": mr["sha1"], "sha512": mr["sha512"]},
                         "env": {"client": client, "server": server}, "downloads": [mr["url"]],
                         "fileSize": int(mr["size"])})
    index = {"formatVersion": 1, "game": "minecraft", "versionId": meta["version"], "name": meta["name"],
             "summary": meta["summary"], "files": mr_files,
             "dependencies": {"minecraft": meta["minecraft"], "neoforge": meta["neoforge"]}}
    with zipfile.ZipFile(DIST / f"{base}.mrpack", "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("modrinth.index.json", json.dumps(index, indent=2))
        for f, rel in override_files():
            z.write(f, f"overrides/{rel}")
    if not_on_mr:
        problems.append(f"Modrinth export is missing {len(not_on_mr)} CurseForge-only mods: {', '.join(not_on_mr)}")

    # Server: every mod that runs on a dedicated server, with a direct URL and its sha1.
    rows = []
    for m in mods:
        if m.get("side", "both") == "client":
            continue
        mr, cf = m.get("modrinth"), m.get("curseforge")
        if mr:
            rows.append(f"{mr['filename']}\t{mr['url']}\t{mr['sha1']}")
        else:
            rows.append(f"{cf['filename']}\t{forgecdn_url(cf['file_id'], cf['filename'])}\t"
                        f"{cached_sha1(cf['file_id'], cf['filename'])['sha1']}")
    (DIST / "server-mods.tsv").write_text("\n".join(rows) + "\n")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--export", action="store_true")
    args = ap.parse_args()
    meta = json.loads((SRC / "pack.json").read_text())
    mods = load_mods()
    n = write_pack(mods, meta)
    tomllib.loads((PACK / "pack.toml").read_text())  # sanity: valid TOML
    sides = {s: sum(1 for m in mods if m.get("side", "both") == s) for s in ("both", "client", "server")}
    print(f"{len(mods)} mods ({sides['both']} both, {sides['client']} client, {sides['server']} server); "
          f"{n} files indexed")
    if args.export:
        for p in export(mods, meta):
            print("WARNING:", p)
        for f in sorted(DIST.iterdir()):
            print(f"dist/{f.name}  {f.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
