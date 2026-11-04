#!/usr/bin/env python3
"""prep.py <clip>...: indexes a slowed-clock capture: which captured frames are new renders, and the game time of each.

The game ran with its clock slowed 30x and the screen was grabbed at 8 fps, so every rendered frame (about 4 a real
second) appears in the capture at least once. A frame counts as new when any pixel visibly changes from the
previous capture (encoding noise stays below 6 levels, a real change is far above). Writes $REEL/idx/<clip>.json."""
import json
import os
import sys

import cv2
import numpy as np

REEL = os.environ.get('REEL', '/home/user/reel')
SLOW, CAP_FPS, THRESH = float(os.environ.get('SLOW', '30')), 8.0, 8
os.makedirs(f'{REEL}/idx', exist_ok=True)
for name in sys.argv[1:]:
    cap = cv2.VideoCapture(f'{REEL}/raw/{name}.mkv')
    prev, n, idx, motion = None, 0, [], []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        g = cv2.resize(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), (480, 480), interpolation=cv2.INTER_AREA).astype(np.int16)
        d = None if prev is None else np.abs(g - prev)
        if d is None or d.max() > THRESH:
            idx.append(n)
            motion.append(0.0 if d is None else round(float(d.mean()), 3))
        prev, n = g, n + 1
    # a render's game time is when it first appeared on screen
    times = [round(i / CAP_FPS / SLOW, 5) for i in idx]
    gaps = np.diff(times) if len(times) > 1 else np.array([1 / 60])
    json.dump({'name': name, 'frames': n, 'game_len': round(n / CAP_FPS / SLOW, 4), 'idx': idx, 't': times,
               'motion': motion}, open(f'{REEL}/idx/{name}.json', 'w'))
    print(f'{name}: {len(idx)} renders over {n / CAP_FPS / SLOW:.2f} game s ({len(idx) / max(1e-9, n / CAP_FPS / SLOW):.0f}/s), '
          f'median gap {np.median(gaps) * 1000:.1f} ms, max {gaps.max() * 1000:.1f} ms')
