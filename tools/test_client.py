#!/usr/bin/env python3
"""Boot the full pack as a real client (software GL under Xvfb), join a world, screenshot it, report errors.

  python3 tools/build_pack.py --export && python3 tools/test_server.py   # (makes a world we can reuse)
  python3 tools/test_client.py [--seconds 240] [--world run/serverpack/world]
  python3 tools/test_server.py --hold 900 &  python3 tools/test_client.py --server localhost:25599 --curseforge
                                         # join the server pack's dedicated server (offline name "Ashborn")

Installs the NeoForge client into run/client, downloads every client-side and shared mod (sha1-checked), the
resource packs, and the non-sound vanilla assets, copies the pack's config/kubejs/defaultconfigs, then launches
offline with --quickPlaySingleplayer (or --quickPlayMultiplayer with --server). Writes run/client/boot.png and
run/client/boot-report.json (with ERROR/WARN lines of logs/latest.log grouped, as test_server.py does).
Exit code 0 when the client reached a loaded world without a crash report (with --server: and stayed connected).
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
import test_server  # noqa: E402  (reuse the log grouping)


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


def sync_mods(mods, curseforge=False):
    """Modrinth files where there are any (as the .mrpack installs), or with curseforge=True the CurseForge files
    (as the CurseForge app installs, and as the server pack bundles)."""
    for d in ("mods", "resourcepacks"):
        if (RUN / d).exists():
            shutil.rmtree(RUN / d)
        (RUN / d).mkdir(parents=True)
    for m in mods:
        mr, cf = m.get("modrinth"), m.get("curseforge")
        if cf and (curseforge or not mr):
            name, (cached, _) = cf["filename"], build_pack.cf_jar(cf["file_id"], cf["filename"])
        else:
            name = mr["filename"]
            cached = fetch(mr["url"], JARS / mr["sha1"] / name, mr["sha1"])
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


def offline_uuid(name):
    """The UUID an offline-mode server gives this name (Java's UUID.nameUUIDFromBytes("OfflinePlayer:" + name)), so
    mods that compare the client's own id with the server's (FTB Teams) see the same player."""
    h = bytearray(hashlib.md5(f"OfflinePlayer:{name}".encode()).digest())
    h[6] = h[6] & 0x0F | 0x30
    h[8] = h[8] & 0x3F | 0x80
    return uuid.UUID(bytes=bytes(h)).hex


def close_game_window(display=":7"):
    """Ask the game to quit the way a player closing the window does (WM_DELETE_WINDOW), so it leaves a server with
    a clean disconnect instead of a dropped connection. Xvfb has no window manager or xdotool, so talk to Xlib."""
    import ctypes

    class ClientMessage(ctypes.Structure):
        _fields_ = [("type", ctypes.c_int), ("serial", ctypes.c_ulong), ("send_event", ctypes.c_int),
                    ("display", ctypes.c_void_p), ("window", ctypes.c_ulong), ("message_type", ctypes.c_ulong),
                    ("format", ctypes.c_int), ("l", ctypes.c_long * 5)]

    class XEvent(ctypes.Union):
        _fields_ = [("xclient", ClientMessage), ("pad", ctypes.c_long * 24)]

    try:
        x = ctypes.cdll.LoadLibrary("libX11.so.6")
    except OSError:
        return False
    x.XOpenDisplay.restype = ctypes.c_void_p
    x.XOpenDisplay.argtypes = [ctypes.c_char_p]
    x.XDefaultRootWindow.restype = ctypes.c_ulong
    x.XDefaultRootWindow.argtypes = [ctypes.c_void_p]
    x.XInternAtom.restype = ctypes.c_ulong
    x.XInternAtom.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
    x.XQueryTree.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong),
                             ctypes.POINTER(ctypes.c_ulong), ctypes.POINTER(ctypes.POINTER(ctypes.c_ulong)),
                             ctypes.POINTER(ctypes.c_uint)]
    x.XFetchName.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.POINTER(ctypes.c_char_p)]
    x.XSendEvent.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int, ctypes.c_long, ctypes.POINTER(XEvent)]
    x.XFlush.argtypes = x.XCloseDisplay.argtypes = [ctypes.c_void_p]
    dpy = x.XOpenDisplay(display.encode())
    if not dpy:
        return False
    root, parent, n = ctypes.c_ulong(), ctypes.c_ulong(), ctypes.c_uint()
    children = ctypes.POINTER(ctypes.c_ulong)()
    x.XQueryTree(dpy, x.XDefaultRootWindow(dpy), ctypes.byref(root), ctypes.byref(parent), ctypes.byref(children),
                 ctypes.byref(n))
    protocols = x.XInternAtom(dpy, b"WM_PROTOCOLS", 0)
    delete = x.XInternAtom(dpy, b"WM_DELETE_WINDOW", 0)
    sent = False
    for i in range(n.value):
        name = ctypes.c_char_p()
        if not x.XFetchName(dpy, children[i], ctypes.byref(name)) or not name.value:
            continue  # GLFW's hidden helper window has no title
        ev = XEvent()
        ev.xclient.type, ev.xclient.window, ev.xclient.message_type = 33, children[i], protocols  # ClientMessage
        ev.xclient.format, ev.xclient.l[0] = 32, delete
        x.XSendEvent(dpy, children[i], 0, 0, ctypes.byref(ev))
        sent = True
    x.XFlush(dpy)
    x.XCloseDisplay(dpy)
    return sent


def substitute(arg, values):
    return re.sub(r"\$\{([a-z_]+)\}", lambda m: values.get(m.group(1), m.group(0)), arg)


def launch_command(nf_json_path, meta, size=(1280, 720), quick=True, server=None, xmx="8G"):
    nf = json.loads(nf_json_path.read_text())
    vanilla_path = RUN / "versions" / meta["minecraft"] / f"{meta['minecraft']}.json"
    vanilla = json.loads(vanilla_path.read_text())
    asset_id = assets(vanilla)
    seen = set()
    cp = library_paths(nf, seen) + library_paths(vanilla, seen)
    # No vanilla client jar on the classpath: NeoForge builds and loads its own patched copy.
    values = {
        "auth_player_name": "Ashborn", "version_name": f"neoforge-{meta['neoforge']}", "game_directory": str(RUN),
        "assets_root": str(RUN / "assets"), "assets_index_name": asset_id,
        # joining a server: the id it gives "Ashborn"; singleplayer: a new id, so a copied world starts a new player
        "auth_uuid": offline_uuid("Ashborn") if server else uuid.uuid4().hex,
        "auth_access_token": "0", "clientid": "0", "auth_xuid": "0", "user_type": "legacy",
        "version_type": "release", "library_directory": str(RUN / "libraries"), "classpath_separator": os.pathsep,
        "natives_directory": str(RUN / "natives"), "launcher_name": "remnants-test", "launcher_version": "1",
        "classpath": os.pathsep.join(str(p) for p in cp)}
    jvm = ["-Xms2G", f"-Xmx{xmx}", f"-Djava.library.path={RUN / 'natives'}", "-cp", values["classpath"]]
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
    if quick and server:
        game += ["--quickPlayMultiplayer", server]
    elif quick:
        game += ["--quickPlaySingleplayer", "remnants-test"]
    return ["java"] + jvm + [nf["mainClass"]] + game


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=int, default=240, help="how long to stay in the world after it loads")
    ap.add_argument("--timeout", type=int, default=1500)
    ap.add_argument("--world", default=str(ROOT / "run" / "serverpack" / "world"))
    ap.add_argument("--server", metavar="HOST:PORT",
                    help="join this dedicated server (offline mode, e.g. test_server.py's localhost:25599) instead of "
                         "a singleplayer world")
    ap.add_argument("--curseforge", action="store_true",
                    help="use the CurseForge file of every mod (what the CurseForge app installs) instead of Modrinth's")
    ap.add_argument("--xmx", default="8G", help="client heap (e.g. 5G when a test server runs on the same machine)")
    ap.add_argument("--size", default="1280x720", help="window and virtual screen size, e.g. 1920x1080")
    ap.add_argument("--menu", action="store_true",
                    help="stay on the title screen and screenshot it (run/client/menu.png)")
    ap.add_argument("--hold", type=int, default=0,
                    help="with --menu: keep the game open this many seconds after the screenshot (to drive it by hand)")
    args = ap.parse_args()
    meta = json.loads((ROOT / "src" / "pack.json").read_text())
    mods = json.loads((ROOT / "src" / "mods.json").read_text())
    nf_json = install_neoforge(meta)
    sync_mods([m for m in mods if m.get("decision") in ("include", "optional")], args.curseforge)
    sync_pack(None if args.server else args.world)
    size = tuple(int(v) for v in args.size.split("x"))
    cmd = launch_command(nf_json, meta, size, quick=not args.menu, server=args.server, xmx=args.xmx)
    env = dict(os.environ, LIBGL_ALWAYS_SOFTWARE="1", GALLIUM_DRIVER="llvmpipe",
               MESA_GL_VERSION_OVERRIDE="4.5", MESA_GLSL_VERSION_OVERRIDE="450")
    xvfb = subprocess.Popen(["Xvfb", ":7", "-screen", "0", f"{size[0]}x{size[1]}x24"], stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    env["DISPLAY"] = ":7"
    log_path = RUN / "boot.log"
    t0 = time.time()
    shot = False
    join_pos = 0
    in_world = False
    left = None
    loaded_at = t0
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
                    time.sleep(args.hold)
                    break
                # Singleplayer: the integrated server's join lines. Multiplayer: the client logs no join line of its
                # own, so take the first sign of a level after "Connecting to" (chat, Iris/FancyMenu level screens).
                conn = text.find("Connecting to ") if args.server else -1
                if not in_world and (re.search(r"joined the game|logged in with entity id", text) or conn >= 0 and
                                     re.search(r"\[CHAT\]|receiving_level_screen|dimension change: null|"
                                               r"Loaded \d+ advancements", text[conn:])):
                    in_world = True
                    loaded_at = time.time()
                    join_pos = len(text)
                if args.server:  # a refused, kicked or dropped connection ends the test
                    m = re.search(r"Client disconnected with reason: .*|Couldn't connect to server.*|"
                                  r"Lost connection.*|Negotiation failed.*", text[join_pos:])
                    if m:
                        left = m.group(0)[:300]
                        break
                if in_world and time.time() - loaded_at > args.seconds:
                    break
                if in_world and not shot and time.time() - loaded_at > 45:
                    subprocess.run(["import", "-display", ":7", "-window", "root", str(RUN / "boot.png")], env=env,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    shot = True
            final = RUN / ("boot-end.png" if shot else "boot.png")
            subprocess.run(["import", "-display", ":7", "-window", "root", str(final)], env=env,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if p.poll() is None and close_game_window():
                try:
                    p.wait(90)  # the game disconnects, saves and exits on its own
                except subprocess.TimeoutExpired:
                    pass
            if p.poll() is None:
                p.terminate()
                try:
                    p.wait(60)
                except subprocess.TimeoutExpired:
                    p.kill()
    finally:
        xvfb.terminate()
    text = log_path.read_text(errors="replace")
    latest = RUN / "logs" / "latest.log"
    latest_text = latest.read_text(errors="replace") if latest.exists() and latest.stat().st_mtime >= t0 else text
    crashes = sorted(c for c in (RUN / "crash-reports").glob("*.txt") if c.stat().st_mtime >= t0) \
        if (RUN / "crash-reports").exists() else []  # only this run's
    report = {"server": args.server, "reached_world": in_world, "disconnected": left,
              "seconds_in_world": round(time.time() - loaded_at) if in_world and not args.menu else 0,
              "seconds": round(time.time() - t0), "crash_reports": [c.name for c in crashes],
              **test_server.summarise(latest_text)}
    (RUN / "boot-report.json").write_text(json.dumps(report, indent=1))
    print(json.dumps({k: v for k, v in report.items() if k != "groups"}, indent=1))
    for g in report["groups"]:
        print(f"{g['count']:4} {g['level']:5} [{g['logger']}] {g['message']}")
    sys.exit(0 if in_world and not crashes and not left else 1)


if __name__ == "__main__":
    main()
