#!/usr/bin/env python3
"""Build Remnants | The Modpack from src/mods.json and the files in pack/.

  python3 tools/build_pack.py            # write pack/mods/*.pw.toml, pack/index.toml, pack/pack.toml
  python3 tools/build_pack.py --export   # also write dist/: CurseForge zip, Modrinth .mrpack, server pack zip

src/mods.json is the curated list: one object per mod with "name", "slug", "side" (both|client|server), "decision"
(include|optional) and at least one of "modrinth" {project_id, version_id, filename, url, sha1, sha512, size} or
"curseforge" {project_id, file_id, filename}. The output is packwiz-compatible, so `packwiz refresh` and
packwiz-installer work on it later. Hashes for CurseForge-only files are downloaded once and cached in .cache/.

The server pack (dist/*-server.zip) is self-contained, as CurseForge server packs are: every server-side mod as its
CurseForge file (sha1-checked, cached in .cache/jars/), the pack's server-relevant files, the NeoForge installer, and
start scripts, JVM flags, server.properties and SERVER.md from tools/server/.
"""
import argparse
import hashlib
import json
import os
import re
import sys
import threading
import tomllib
import urllib.parse
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACK = ROOT / "pack"
DIST = ROOT / "dist"
CACHE = ROOT / ".cache"
JARS = CACHE / "jars"
SRC = ROOT / "src"
SERVER_TEMPLATES = ROOT / "tools" / "server"
UA = "NightBeam-pack/1.0 (remnants-modpack)"

# Files under pack/ that never go into a pack (packwiz's own metadata and editor leftovers).
SKIP_INDEX = {"pack.toml", "index.toml", ".packwizignore"}


def toml_str(s):
    return json.dumps(s, ensure_ascii=False)


def forgecdn_url(file_id, filename):
    fid = str(file_id)
    return f"https://edge.forgecdn.net/files/{fid[:-3]}/{int(fid[-3:])}/{urllib.parse.quote(filename)}"


_sha1_lock = threading.Lock()


# Committed: the sha1 of every CurseForge file the pack uses, so a fresh build (CI) checks each download against
# what was tested here instead of trusting the first download. export() adds new files to it.
PINNED_SHA1 = ROOT / "src" / "cf_sha1.json"


def _sha1_memo():
    memo = CACHE / "cf_sha1.json"
    data = json.loads(memo.read_text()) if memo.exists() else {}
    if PINNED_SHA1.exists():
        data.update(json.loads(PINNED_SHA1.read_text()))
    return data


def pin_cf_sha1(mods):
    """Write src/cf_sha1.json: the recorded sha1 and size of each included mod's CurseForge file."""
    memo = _sha1_memo()
    pinned = {}
    for m in mods:
        cf = m.get("curseforge") or {}
        if m.get("decision") in ("include", "optional") and str(cf.get("file_id")) in memo:
            pinned[str(cf["file_id"])] = memo[str(cf["file_id"])]
    PINNED_SHA1.write_text(json.dumps(pinned, indent=1, sort_keys=True) + "\n")


def _file_sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def cf_jar(file_id, filename):
    """The CurseForge file itself: downloaded once into .cache/jars/<sha1>/<filename>, its sha1 recorded in
    .cache/cf_sha1.json, and checked against that record every time it is used. Returns (path, {sha1, size})."""
    key = str(file_id)
    known = _sha1_memo().get(key)
    if known:
        path = JARS / known["sha1"] / filename
        if path.exists() and _file_sha1(path) == known["sha1"]:
            return path, known
    req = urllib.request.Request(forgecdn_url(file_id, filename), headers={"User-Agent": UA})
    h, size = hashlib.sha1(), 0
    JARS.mkdir(parents=True, exist_ok=True)
    tmp = JARS / f".{key}.part"
    with urllib.request.urlopen(req, timeout=300) as r, open(tmp, "wb") as out:
        for chunk in iter(lambda: r.read(1 << 16), b""):
            h.update(chunk)
            out.write(chunk)
            size += len(chunk)
    info = {"sha1": h.hexdigest(), "size": size}
    if known and known["sha1"] != info["sha1"]:
        tmp.unlink()
        sys.exit(f"sha1 mismatch for CurseForge file {key} ({filename}): expected {known['sha1']}, got {info['sha1']}")
    path = JARS / info["sha1"] / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    os.replace(tmp, path)
    with _sha1_lock:
        memo = _sha1_memo()
        memo[key] = info
        part = CACHE / f"cf_sha1.json.{threading.get_ident()}"
        part.write_text(json.dumps(memo, indent=1, sort_keys=True))
        os.replace(part, CACHE / "cf_sha1.json")  # atomic: readers never see half a file
    return path, info


def cached_sha1(file_id, filename):
    """sha1 of a CurseForge file (packwiz needs it; cfwidget does not give hashes)."""
    return cf_jar(file_id, filename)[1]


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


def folder(m):
    """mods/ for jars; resource packs (Fresh Animations) live in resourcepacks/."""
    return m.get("folder", "mods")


def write_pack(mods, meta):
    wanted = set()
    for m in mods:
        d = PACK / folder(m)
        d.mkdir(parents=True, exist_ok=True)
        p = d / f"{m['slug']}.pw.toml"
        p.write_text(pw_toml(m))
        wanted.add(p)
    for stale in PACK.glob("*/*.pw.toml"):
        if stale not in wanted:
            stale.unlink()

    entries = []
    for f in sorted(PACK.rglob("*")):
        rel = f.relative_to(PACK).as_posix()
        if f.is_dir() or rel in SKIP_INDEX:
            continue
        entry = [f"file = {toml_str(rel)}", f"hash = {toml_str(sha256(f))}"]
        if rel.endswith(".pw.toml"):
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
        if f.is_file() and rel not in SKIP_INDEX and not rel.endswith(".pw.toml"):
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
        mr_files.append({"path": f"{folder(m)}/{mr['filename']}", "hashes": {"sha1": mr["sha1"], "sha512": mr["sha512"]},
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

    # Server pack: self-contained, like CurseForge server packs. See write_server_pack.
    problems += write_server_pack(mods, meta, DIST / f"{base}-server.zip")
    pin_cf_sha1(mods)
    return problems


# Parts of the pack a dedicated server never reads: client-only mods' configs, client configs, KubeJS client
# scripts and assets (sounds, textures, lang, book text). Paths relative to pack/.
CLIENT_ONLY = ("config/defaultoptions/", "config/fancymenu/", "config/dynamic_fps.json", "kubejs/assets/",
               "kubejs/client_scripts/")
SERVER_DIRS = ("config", "defaultconfigs", "kubejs", "datapacks")


def server_side(m):
    return m.get("side", "both") != "client" and folder(m) == "mods"


def server_file(rel):
    """Whether pack/<rel> belongs in the server pack."""
    if rel.split("/")[0] not in SERVER_DIRS or rel.startswith(CLIENT_ONLY):
        return False
    name = rel.rsplit("/", 1)[-1]
    return not (rel.startswith("config/") and re.search(r"[-_.]client\.(toml|json5?|cfg|properties|snbt)$", name))


def neoforge_installer(version):
    path = CACHE / f"neoforge-{version}-installer.jar"
    if not path.exists():
        url = f"https://maven.neoforged.net/releases/net/neoforged/neoforge/{version}/neoforge-{version}-installer.jar"
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=300) as r:
            data = r.read()
        with urllib.request.urlopen(urllib.request.Request(url + ".sha1", headers={"User-Agent": UA}), timeout=60) as r:
            want = r.read().decode().split()[0]
        if hashlib.sha1(data).hexdigest() != want:
            sys.exit(f"sha1 mismatch for {url}")
        CACHE.mkdir(exist_ok=True)
        path.write_bytes(data)
    return path


def write_server_pack(mods, meta, dest):
    """mods/ (every server-side mod, as its CurseForge file), the pack's server files, the NeoForge installer,
    start.sh/start.bat, user_jvm_args.txt, server.properties and SERVER.md."""
    problems = []
    server_mods = [m for m in mods if server_side(m)]
    missing = [m["slug"] for m in server_mods if not m.get("curseforge")]
    if missing:
        problems.append(f"server pack is missing {len(missing)} mods with no CurseForge file: {', '.join(missing)}")
        server_mods = [m for m in server_mods if m.get("curseforge")]
    with ThreadPoolExecutor(8) as pool:
        jars = list(pool.map(lambda m: cf_jar(m["curseforge"]["file_id"], m["curseforge"]["filename"])[0], server_mods))
    names = [m["curseforge"]["filename"] for m in server_mods]
    if len(set(names)) != len(names):
        sys.exit("server pack: two mods have the same file name")

    nf = meta["neoforge"]
    subst = {"@NAME@": meta["name"], "@VERSION@": meta["version"], "@NEOFORGE@": nf,
             "@MOTD@": f"{meta['name']} {meta['version']}".replace("\\", "\\\\")}

    def template(name):
        text = (SERVER_TEMPLATES / name).read_text()
        for k, v in subst.items():
            text = text.replace(k, v)
        return text

    def add_text(z, name, text, mode=0o644):
        info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
        info.external_attr = (0o100000 | mode) << 16
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info, text)

    tmp = dest.with_suffix(".zip.part")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        add_text(z, "start.sh", template("start.sh"), 0o755)
        add_text(z, "start.bat", template("start.bat").replace("\r\n", "\n").replace("\n", "\r\n"))
        for name in ("user_jvm_args.txt", "server.properties", "SERVER.md"):
            add_text(z, name, template(name))
        z.write(neoforge_installer(nf), f"neoforge-{nf}-installer.jar")
        for path, name in zip(jars, names):
            z.write(path, f"mods/{name}")
        for f, rel in override_files():
            if server_file(rel):
                z.write(f, rel)
    os.replace(tmp, dest)
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
