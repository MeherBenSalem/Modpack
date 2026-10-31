#!/usr/bin/env python3
"""Boot-test the real server pack: the zip from `build_pack.py --export`, installed and started the way a server
owner does it.

  python3 tools/build_pack.py --export && python3 tools/test_server.py [--keep-world] [--cmd "/some command" ...]
  python3 tools/test_server.py --hold 600        # stay up 10 minutes after "Done" (e.g. for test_client.py --server)

Unzips dist/<pack>-server.zip into a clean run/serverpack, accepts the EULA, sets online-mode=false and a test port
(test only: the shipped server.properties keeps online-mode=true), runs the shipped start.sh (which installs NeoForge
on first run), waits for "Done", optionally stays up (--hold), runs the given console commands, stops the server and
summarises every ERROR and WARN line of logs/latest.log, grouped. Writes run/serverpack/boot-report.json.
Exit code 0 only when the server reached "Done", no mod failed to load and nothing wrote a crash report.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEST_SEED = "remnants-s1"

# Lines that only exist because the test runs offline (the shipped pack keeps online-mode=true).
TEST_ONLY = re.compile(r"OFFLINE/INSECURE MODE|make no attempt to authenticate|online-mode\" to \"true|"
                       r"hackers to connect with any username")
LEVEL = re.compile(r"^\[[^\]]+\] \[([^\]/]+)/(WARN|ERROR|FATAL)\] \[([^\]]*)\]: (.*)$")


def server_zip(meta):
    z = ROOT / "dist" / f"{meta['file_name']}-{meta['version']}-server.zip"
    if not z.exists():
        sys.exit(f"{z.relative_to(ROOT)} not found: run python3 tools/build_pack.py --export first")
    return z


def lock(run):
    """One test server per directory at a time (another shell may be running this test)."""
    run.parent.mkdir(parents=True, exist_ok=True)
    lf = run.parent / f".{run.name}.lock"
    if lf.exists():
        try:
            pid = int(lf.read_text())
            os.kill(pid, 0)
            sys.exit(f"{run} is in use by test_server.py (pid {pid}); use --dir for a second server")
        except (ValueError, ProcessLookupError, PermissionError):
            pass
    lf.write_text(str(os.getpid()))
    return lf


def unpack(zpath, run, keep_world):
    saved = None
    if keep_world and (run / "world").exists():
        saved = run.parent / f".{run.name}-world"
        if saved.exists():
            shutil.rmtree(saved)
        (run / "world").rename(saved)
    if run.exists():
        shutil.rmtree(run)
    run.mkdir(parents=True)
    with zipfile.ZipFile(zpath) as z:
        for info in z.infolist():
            if info.filename.startswith("/") or ".." in Path(info.filename).parts:
                sys.exit(f"unsafe path in server zip: {info.filename}")
            z.extract(info, run)
            mode = info.external_attr >> 16 & 0o777
            if mode and not info.is_dir():
                os.chmod(run / info.filename, mode)  # like unzip: keep start.sh executable
    if saved:
        saved.rename(run / "world")


def prepare(run, port, xmx):
    (run / "eula.txt").write_text("eula=true\n")
    props = run / "server.properties"
    test_values = {"online-mode": "false", "server-port": str(port), "level-seed": TEST_SEED,
                   "motd": "Remnants server pack test"}
    lines, seen = [], set()
    for ln in props.read_text().splitlines():
        key = ln.split("=", 1)[0]
        if key in test_values and not ln.startswith("#"):
            ln = f"{key}={test_values[key]}"
            seen.add(key)
        lines.append(ln)
    lines += [f"{k}={v}" for k, v in test_values.items() if k not in seen]
    props.write_text("\n".join(lines) + "\n")
    if xmx:
        args = run / "user_jvm_args.txt"
        args.write_text(re.sub(r"^-Xm([sx])\S+$", lambda m: f"-Xm{m.group(1)}{xmx}", args.read_text(), flags=re.M))


def run_server(run, commands, timeout, hold, port):
    out_path = run / "console.log"
    with open(out_path, "w") as out:
        p = subprocess.Popen(["bash", "start.sh"], cwd=run, stdin=subprocess.PIPE, stdout=out,
                             stderr=subprocess.STDOUT, text=True)
        t0, done = time.time(), False
        while time.time() - t0 < timeout and p.poll() is None:
            time.sleep(3)
            if re.search(r"\]: Done \([0-9.]+s\)!", out_path.read_text(errors="replace")):
                done = True
                break
        boot = time.time() - t0
        if done:
            if hold:
                print(f"server up on port {port} after {round(boot)} s; holding up to {hold} s", flush=True)
                end = time.time() + hold
                while time.time() < end and p.poll() is None:
                    time.sleep(5)
                    text = out_path.read_text(errors="replace")
                    joins = len(re.findall(r"\]: \S+ joined the game", text))
                    if joins and len(re.findall(r"\]: \S+ lost connection", text)) >= joins:
                        break  # everyone who joined has left: the join test is over
            for c in commands + ["list"]:
                if p.poll() is not None:
                    break
                p.stdin.write(c.lstrip("/") + "\n")
                p.stdin.flush()
                time.sleep(4)
        if p.poll() is None:
            p.stdin.write("stop\n")
            p.stdin.flush()
        try:
            p.wait(timeout=180)
        except subprocess.TimeoutExpired:
            p.kill()
    return done, boot


def group(lines):
    """Group WARN/ERROR lines by level, logger and message with numbers, coordinates and paths blurred."""
    counts, sample = Counter(), {}
    for ln in lines:
        m = LEVEL.match(ln)
        level, logger, msg = m.group(2), m.group(3), m.group(4)
        norm = re.sub(r"Reference map '.*", "Reference map '...' for ... could not be read", msg)
        norm = re.sub(r"(/[\w.+\-%]+)+", "<path>", norm)
        norm = re.sub(r"-?\d+(\.\d+)?", "N", norm)[:140]
        key = (level, logger, norm)
        counts[key] += 1
        sample.setdefault(key, msg[:260])
    return [{"level": k[0], "logger": k[1], "count": n, "message": sample[k]}
            for k, n in sorted(counts.items(), key=lambda kv: (kv[0][0] != "ERROR", -kv[1], kv[0][1]))]


def summarise(text):
    lines = [ln for ln in text.splitlines() if LEVEL.match(ln)]
    test_only = [ln for ln in lines if TEST_ONLY.search(ln)]
    real = [ln for ln in lines if not TEST_ONLY.search(ln)]
    errors = [ln for ln in real if LEVEL.match(ln).group(2) != "WARN"]
    return {"error_lines": len(errors), "warn_lines": len(real) - len(errors),
            "test_only_warn_lines": len(test_only), "groups": group(real)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep-world", action="store_true", help="keep run/serverpack/world from the last run")
    ap.add_argument("--cmd", action="append", default=[], help="console command to run after Done (repeatable)")
    ap.add_argument("--hold", type=int, default=0,
                    help="stay up to this many seconds after Done (ends early once every player who joined has left)")
    ap.add_argument("--timeout", type=int, default=1200, help="seconds to wait for Done (includes the NeoForge install)")
    ap.add_argument("--port", type=int, default=25599)
    ap.add_argument("--dir", default=str(ROOT / "run" / "serverpack"))
    ap.add_argument("--xmx", help="test only: override -Xms/-Xmx in user_jvm_args.txt (e.g. 5G on a small machine)")
    args = ap.parse_args()
    meta = json.loads((ROOT / "src" / "pack.json").read_text())
    run = Path(args.dir).resolve()
    zpath = server_zip(meta)
    lf = lock(run)
    try:
        unpack(zpath, run, args.keep_world)
        n_jars = len(list((run / "mods").glob("*.jar")))
        prepare(run, args.port, args.xmx)
        done, boot = run_server(run, args.cmd, args.timeout, args.hold, args.port)
    finally:
        lf.unlink(missing_ok=True)
    log = run / "logs" / "latest.log"
    text = log.read_text(errors="replace") if log.exists() else (run / "console.log").read_text(errors="replace")
    mod_list = re.search(r"Mod List:\n(?:.*\n)*?(?=\S)", text)
    loaded = len(re.findall(r"^\t\t.+ \(([a-z0-9_]+)\)$", mod_list.group(0), re.M)) if mod_list else "?"
    done_s = re.findall(r"\]: Done \(([0-9.]+)s\)!", text)
    joined = re.findall(r"\]: (\S+) joined the game", text)
    crashes = sorted(c.name for c in (run / "crash-reports").glob("*.txt")) if (run / "crash-reports").exists() else []
    report = {"zip": zpath.name, "zip_mb": round(zpath.stat().st_size / 1e6, 1), "reached_done": done,
              "seconds_to_done": round(boot), "server_done_seconds": float(done_s[-1]) if done_s else None,
              "mod_jars": n_jars, "mods_loaded": loaded, "players_joined": joined, "crash_reports": crashes,
              **summarise(text)}
    (run / "boot-report.json").write_text(json.dumps(report, indent=1))
    print(json.dumps({k: v for k, v in report.items() if k != "groups"}, indent=1))
    for g in report["groups"]:
        print(f"{g['count']:4} {g['level']:5} [{g['logger']}] {g['message']}")
    print(f"full log: {log}")
    sys.exit(0 if done and not crashes and not re.search(r"Mod loading has failed|ModLoadingException", text) else 1)


if __name__ == "__main__":
    main()
