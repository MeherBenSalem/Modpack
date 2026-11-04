#!/usr/bin/env python3
"""Installs the real client (tools/test_client.py's installer: NeoForge, every CurseForge mod file the server pack
bundles, the pack's config/kubejs/defaultconfigs) into run/client and writes the launch command line to
$REEL/client_cmd.json, so capture/game.sh can relaunch it on the slowed clock in a window of any size.

  python3 client_prep.py [--size 1080x1920]
"""
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
REEL = Path(os.environ.get('REEL', '/home/user/reel'))
sys.path.insert(0, str(ROOT / 'tools'))
import test_client as tc  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--size', default='1080x1920')
ap.add_argument('--server', default='localhost:25599')
a = ap.parse_args()
meta = json.loads((ROOT / 'src' / 'pack.json').read_text())
mods = json.loads((ROOT / 'src' / 'mods.json').read_text())
nf = tc.install_neoforge(meta)
tc.sync_mods([m for m in mods if m.get('decision') in ('include', 'optional')], curseforge=True)
tc.sync_pack(None)
w, h = (int(v) for v in a.size.split('x'))
cmd = tc.launch_command(nf, meta, (w, h), quick=True, server=a.server, xmx='5G')
REEL.mkdir(parents=True, exist_ok=True)
(REEL / 'client_cmd.json').write_text(json.dumps({'cwd': str(tc.RUN), 'cmd': cmd}))
print('client ready:', tc.RUN, len(cmd), 'args')
