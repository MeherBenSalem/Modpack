#!/usr/bin/env python3
"""Boot the full pack as a real client (software GL under Xvfb), join a world, screenshot it, report errors.

  python3 tools/build_pack.py --export && python3 tools/test_server.py   # (makes a world we can reuse)
  python3 tools/test_client.py [--seconds 240] [--world run/server/world]

Installs the NeoForge client into run/client, downloads every client-side and shared mod (sha1-checked), the
resource packs, and the non-sound vanilla assets, copies the pack's config/kubejs/defaultconfigs, then launches
offline with --quickPlaySingleplayer. Writes run/client/boot.png and run/client/boot-report.json.
Exit code 0 when the client reached a loaded world without a crash report.
"""
import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUN = ROOT / "run" / "client"
JARS = ROOT / ".cache" / "jars"
UA = "NightBeam-pack/1.0 (remnants-modpack client test)"
sys.path.insert(0, str(ROOT / "tools"))
import build_pack  # noqa: E402  (reuse the CurseForge URL helper and sha1 cache)


def fetch(url, dest, sha1=None):
    if dest.exists() and (sha1 is None or hashlib.sha1(dest.read_bytes()).hexdigest() == sha1):
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=300) as r:
        data = r.read()
    if sha1 and hashlib.sha1(data).hexdigest() != sha1:
        raise SystemExit(f"sha1 mismatch: {url}")
    dest.write_bytes(data)
    return dest


def install_neoforge(meta):
    nf, mc = meta["neoforge"], meta["minecraft"]
    vdir = RUN / "versions" / f"neoforge-{nf}"
    if (vdir / f"neoforge-{nf}.json").exists():
        return vdir / f"neoforge-{nf}.json"
    RUN.mkdir(parents=True, exist_ok=True)
    (RUN / "launcher_profiles.json").write_text('{"profiles": {}}')
    inst = ROOT / ".cache" / f"neoforge-{nf}-installer.jar"
    fetch(f"https://maven.neoforged.net/releases/net/neoforged/neoforge/{nf}/neoforge-{nf}-installer.jar", inst)
    subprocess.run(["java", "-jar", str(inst), "--install-client", str(RUN)], check=True, cwd=RUN,
                   stdout=subprocess.DEVNULL)
    return vdir / f"neoforge-{nf}.json"


def rule_ok(rules):
    if not rules:
        return True
    ok = False
    for r in rules:
        if "features" in r:
            continue
        os_rule = r.get("os", {})
        match = not os_rule or os_rule.get("name") == "linux"
        if match:
            ok = r["action"] == "allow"
    return ok


def library_paths(version_json, seen):
    out = []
    for lib in version_json.get("libraries", []):
        if not rule_ok(lib.get("rules")):
            continue
        art = lib.get("downloads", {}).get("artifact")
        if not art:
            continue
        key = ":".join(lib["name"].split(":")[:2] + lib["name"].split(":")[3:4])
        if key in seen:
            continue
        seen.add(key)
        path = RUN / "libraries" / art["path"]
        if not path.exists() and art.get("url"):
            fetch(art["url"], path, art.get("sha1"))
        out.append(path)
    return out


def assets(vanilla):
    idx = vanilla["assetIndex"]
    index_path = fetch(idx["url"], RUN / "assets" / "indexes" / f"{idx['id']}.json", idx["sha1"])
    objects = json.loads(index_path.read_text())["objects"]
    todo = []
    for name, o in objects.items():
        if name.endswith(".ogg"):  # sounds and music: a crash test doesn't need them
            continue
        h = o["hash"]
        dest = RUN / "assets" / "objects" / h[:2] / h
        if not dest.exists():
            todo.append((f"https://resources.download.minecraft.net/{h[:2]}/{h}", dest, h))
    with ThreadPoolExecutor(16) as pool:
        list(pool.map(lambda a: fetch(*a), todo))
    return idx["id"]


def sync_mods(mods):
    for d in ("mods", "resourcepacks"):
        if (RUN / d).exists():
            shutil.rmtree(RUN / d)
        (RUN / d).mkdir(parents=True)
    for m in mods:
        mr, cf = m.get("modrinth"), m.get("curseforge")
        if mr:
            name, url, sha1 = mr["filename"], mr["url"], mr["sha1"]
        else:
            name, url = cf["filename"], build_pack.forgecdn_url(cf["file_id"], cf["filename"])
            sha1 = build_pack.cached_sha1(cf["file_id"], cf["filename"])["sha1"]
        cached = fetch(url, JARS / sha1 / name, sha1)
        shutil.copy2(cached, RUN / m.get("folder", "mods") / name)


def sync_pack(world):
    for d in ("config", "defaultconfigs", "kubejs"):
        if (RUN / d).exists():
            shutil.rmtree(RUN / d)
        if (ROOT / "pack" / d).exists():
            shutil.copytree(ROOT / "pack" / d, RUN / d)
    saves = RUN / "saves" / "remnants-test"
    if saves.exists():
        shutil.rmtree(saves)
    if world and Path(world).exists():
        shutil.copytree(world, saves)
    for f in ("options.txt",):
        if (RUN / f).exists():
            (RUN / f).unlink()  # let Default Options apply the pack's options on a "fresh" install


def substitute(arg, values):
    return re.sub(r"\$\{([a-z_]+)\}", lambda m: values.get(m.group(1), m.group(0)), arg)


def launch_command(nf_json_path, meta, size=(1280, 720), quick=True):
    nf = json.loads(nf_json_path.read_text())
    vanilla_path = RUN / "versions" / meta["minecraft"] / f"{meta['minecraft']}.json"
    vanilla = json.loads(vanilla_path.read_text())
    asset_id = assets(vanilla)
    seen = set()
    cp = library_paths(nf, seen) + library_paths(vanilla, seen)
    # No vanilla client jar on the classpath: NeoForge builds and loads its own patched copy.
    values = {
        "auth_player_name": "Ashborn", "version_name": f"neoforge-{meta['neoforge']}", "game_directory": str(RUN),
        "assets_root": str(RUN / "assets"), "assets_index_name": asset_id, "auth_uuid": uuid.uuid4().hex,
        "auth_access_token": "0", "clientid": "0", "auth_xuid": "0", "user_type": "legacy",
        "version_type": "release", "library_directory": str(RUN / "libraries"), "classpath_separator": os.pathsep,
        "natives_directory": str(RUN / "natives"), "launcher_name": "remnants-test", "launcher_version": "1",
        "classpath": os.pathsep.join(str(p) for p in cp)}
    jvm = ["-Xms2G", "-Xmx8G", f"-Djava.library.path={RUN / 'natives'}", "-cp", values["classpath"]]
    for src in (nf.get("arguments", {}).get("jvm", []),):
        for a in src:
            if isinstance(a, str):
                jvm.append(substitute(a, values))
    game = []
    for src in (vanilla["arguments"]["game"], nf.get("arguments", {}).get("game", [])):
        for a in src:
            if isinstance(a, str):
                game.append(substitute(a, values))
    game += ["--width", str(size[0]), "--height", str(size[1])]
    if quick:
        game += ["--quickPlaySingleplayer", "remnants-test"]
    return ["java"] + jvm + [nf["mainClass"]] + game


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=int, default=240, help="how long to stay in the world after it loads")
    ap.add_argument("--timeout", type=int, default=1500)
    ap.add_argument("--world", default=str(ROOT / "run" / "server" / "world"))
    ap.add_argument("--size", default="1280x720", help="window and virtual screen size, e.g. 1920x1080")
    ap.add_argument("--menu", action="store_true",
                    help="stay on the title screen and screenshot it (run/client/menu.png)")
    args = ap.parse_args()
    meta = json.loads((ROOT / "src" / "pack.json").read_text())
    mods = json.loads((ROOT / "src" / "mods.json").read_text())
    nf_json = install_neoforge(meta)
    sync_mods([m for m in mods if m.get("decision") in ("include", "optional")])
    sync_pack(args.world)
    size = tuple(int(v) for v in args.size.split("x"))
    cmd = launch_command(nf_json, meta, size, quick=not args.menu)
    env = dict(os.environ, LIBGL_ALWAYS_SOFTWARE="1", GALLIUM_DRIVER="llvmpipe",
               MESA_GL_VERSION_OVERRIDE="4.5", MESA_GLSL_VERSION_OVERRIDE="450")
    xvfb = subprocess.Popen(["Xvfb", ":7", "-screen", "0", f"{size[0]}x{size[1]}x24"], stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    env["DISPLAY"] = ":7"
    log_path = RUN / "boot.log"
    t0 = time.time()
    in_world = False
    try:
        with open(log_path, "w") as out:
            p = subprocess.Popen(cmd, cwd=RUN, env=env, stdout=out, stderr=subprocess.STDOUT)
            while time.time() - t0 < args.timeout and p.poll() is None:
                time.sleep(5)
                text = log_path.read_text(errors="replace")
                if args.menu and re.search(r"Game took [0-9.]+ seconds to start", text):
                    time.sleep(20)
                    subprocess.run(["import", "-display", ":7", "-window", "root", str(RUN / "menu.png")], env=env,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    in_world = True
                    break
                if not in_world and re.search(r"joined the game|logged in with entity id", text):
                    in_world = True
                    loaded_at = time.time()
                if in_world and time.time() - loaded_at > args.seconds:
                    break
            subprocess.run(["import", "-display", ":7", "-window", "root", str(RUN / "boot.png")], env=env,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if p.poll() is None:
                p.terminate()
                try:
                    p.wait(60)
                except subprocess.TimeoutExpired:
                    p.kill()
    finally:
        xvfb.terminate()
    text = log_path.read_text(errors="replace")
    crashes = sorted(c for c in (RUN / "crash-reports").glob("*.txt") if c.stat().st_mtime >= t0) \
        if (RUN / "crash-reports").exists() else []  # only this run's
    report = {"reached_world": in_world, "seconds": round(time.time() - t0), "crash_reports": [c.name for c in crashes],
              "mods_loaded": (re.findall(r"Loading (\d+) mods", text) or ["?"])[-1],
              "errors": len(re.findall(r"/(ERROR|FATAL)\]", text))}
    (RUN / "boot-report.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))
    for ln in [ln for ln in text.splitlines() if re.search(r"/(ERROR|FATAL)\]", ln)][:40]:
        print(ln[:300])
    sys.exit(0 if in_world and not crashes else 1)


if __name__ == "__main__":
    main()
