#!/usr/bin/env python3
"""Boot-test the pack on a real NeoForge dedicated server.

  python3 tools/build_pack.py --export && python3 tools/test_server.py [--keep-world] [--cmd "/some command" ...]

Installs NeoForge (version from src/pack.json) into run/server, downloads every mod in dist/server-mods.tsv
(sha1-checked, cached in .cache/jars), copies the pack's config/, defaultconfigs/, kubejs/ and datapacks, starts the
server, waits for "Done", runs the given console commands, stops it, and summarises errors from the log.
Exit code 0 only when the server reached "Done" and no mod failed to load.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUN = ROOT / "run" / "server"
JARS = ROOT / ".cache" / "jars"
UA = "NightBeam-pack/1.0 (remnants-modpack test)"
COPY_DIRS = ["config", "defaultconfigs", "kubejs", "datapacks"]


def fetch(url, dest, sha1=None):
    if dest.exists() and (sha1 is None or hashlib.sha1(dest.read_bytes()).hexdigest() == sha1):
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=300) as r:
        data = r.read()
    if sha1 and hashlib.sha1(data).hexdigest() != sha1:
        sys.exit(f"sha1 mismatch for {url}")
    dest.write_bytes(data)


def install(meta):
    nf = meta["neoforge"]
    marker = RUN / f".installed-{nf}"
    if marker.exists():
        return
    RUN.mkdir(parents=True, exist_ok=True)
    inst = ROOT / ".cache" / f"neoforge-{nf}-installer.jar"
    fetch(f"https://maven.neoforged.net/releases/net/neoforged/neoforge/{nf}/neoforge-{nf}-installer.jar", inst)
    subprocess.run(["java", "-jar", str(inst), "--install-server", str(RUN)], check=True, cwd=RUN,
                   stdout=subprocess.DEVNULL)
    marker.write_text(nf)


def sync_mods():
    mods = RUN / "mods"
    if mods.exists():
        shutil.rmtree(mods)
    mods.mkdir()
    rows = [ln.split("\t") for ln in (ROOT / "dist" / "server-mods.tsv").read_text().splitlines() if ln.strip()]
    for name, url, sha1 in rows:
        cached = JARS / sha1 / name
        fetch(url, cached, sha1)
        shutil.copy2(cached, mods / name)
    return len(rows)


def sync_files(keep_world):
    for d in COPY_DIRS:
        src, dst = ROOT / "pack" / d, RUN / d
        if dst.exists():
            shutil.rmtree(dst)
        if src.exists():
            shutil.copytree(src, dst)
    if not keep_world and (RUN / "world").exists():
        shutil.rmtree(RUN / "world")
    (RUN / "eula.txt").write_text("eula=true\n")
    props = {"online-mode": "false", "motd": "Remnants S1 boot test", "spawn-protection": "0",
             "difficulty": "hard", "max-tick-time": "-1", "level-seed": "remnants-s1",
             "server-port": "25599", "sync-chunk-writes": "false"}
    (RUN / "server.properties").write_text("".join(f"{k}={v}\n" for k, v in props.items()))
    (RUN / "user_jvm_args.txt").write_text("-Xms4G\n-Xmx8G\n")


def run(commands, timeout):
    log = RUN / "boot.log"
    script = RUN / "run.sh"
    with open(log, "w") as out:
        p = subprocess.Popen(["bash", str(script), "nogui"], cwd=RUN, stdin=subprocess.PIPE, stdout=out,
                             stderr=subprocess.STDOUT, text=True)
        t0, done = time.time(), False
        while time.time() - t0 < timeout and p.poll() is None:
            time.sleep(3)
            text = log.read_text(errors="replace")
            if re.search(r"\]: Done \([0-9.]+s\)!", text):
                done = True
                break
        boot = time.time() - t0
        if done:
            for c in commands:
                p.stdin.write(c.lstrip("/") + "\n")
                p.stdin.flush()
                time.sleep(4)
            p.stdin.write("stop\n")
            p.stdin.flush()
        try:
            p.wait(timeout=180)
        except subprocess.TimeoutExpired:
            p.kill()
    return done, boot, log.read_text(errors="replace")


def summarise(text):
    errors = [ln for ln in text.splitlines() if re.search(r"/(ERROR|FATAL)\]|Exception|Mixin apply failed|"
                                                            r"Failed to load|missing mandatory dependenc", ln)]
    seen, out = set(), []
    for ln in errors:
        key = re.sub(r"^\[[^\]]*\] ", "", ln)[:160]
        if key not in seen:
            seen.add(key)
            out.append(ln[:300])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep-world", action="store_true")
    ap.add_argument("--cmd", action="append", default=[])
    ap.add_argument("--timeout", type=int, default=900)
    args = ap.parse_args()
    meta = json.loads((ROOT / "src" / "pack.json").read_text())
    install(meta)
    n = sync_mods()
    sync_files(args.keep_world)
    done, boot, text = run(args.cmd, args.timeout)
    errs = summarise(text)
    report = {"reached_done": done, "seconds_to_done": round(boot), "server_mods": n,
              "loaded_mods": (re.findall(r"Loading (\d+) mods", text) or ["?"])[-1], "error_lines": len(errs)}
    print(json.dumps(report, indent=1))
    for ln in errs[:80]:
        print(ln)
    print(f"full log: {RUN / 'boot.log'}")
    sys.exit(0 if done and not re.search(r"Mod loading has failed|ModLoadingException", text) else 1)


if __name__ == "__main__":
    main()
