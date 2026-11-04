#!/usr/bin/env python3
"""stabilize.py <clip>...: measures the camera path of a capture so slow pans can be made perfectly smooth.

The capture rig turned the camera with the mouse, and the game turns it in whole pixels of mouse movement (0.15
degrees each). A slow, deliberate pan therefore moves in single-pixel ticks every 50-150 ms of game time, which reads
as a faint stutter at 60 fps. This measures each real render's global shift against the previous one (phase
correlation on the luminance, 1/4 scale), accumulates the camera path, low-passes it (Gaussian, sigma 0.12 s of game
time) and stores, per render, the sub-pixel correction that moves it onto the smooth path:
$REEL/idx/<clip>_stab.json. compose.py applies it to every render of a shot marked 'stab' (a translation of a few
pixels at most; nothing is invented or retimed).
"""
import json
import os
import sys

import cv2
import numpy as np

REEL = os.environ.get('REEL', '/home/user/reel')
SCALE = 4


def main(name):
    j = json.load(open(f'{REEL}/idx/{name}.json'))
    idx, t = j['idx'], np.array(j['t'])
    want = set(idx)
    cap = cv2.VideoCapture(f'{REEL}/raw/{name}.mkv')
    prev, path, n = None, [], 0
    win = None
    x = y = 0.0
    while True:
        ok = cap.grab()
        if not ok:
            break
        if n in want:
            _, f = cap.retrieve()
            g = cv2.resize(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), (f.shape[1] // SCALE, f.shape[0] // SCALE),
                           interpolation=cv2.INTER_AREA).astype(np.float32)
            if win is None:
                win = cv2.createHanningWindow(g.shape[::-1], cv2.CV_32F)
            if prev is not None:
                (dx, dy), resp = cv2.phaseCorrelate(prev, g, win)
                if resp < 0.05 or abs(dx) > 40 or abs(dy) > 40:   # a cut, a flash, a particle storm: no estimate
                    dx = dy = 0.0
                x += dx * SCALE
                y += dy * SCALE
            path.append((x, y))
            prev = g
        n += 1
    p = np.array(path)
    # Gaussian low-pass in game time (renders are not evenly spaced)
    sm = np.zeros_like(p)
    for i in range(len(t)):
        w = np.exp(-0.5 * ((t - t[i]) / 0.12) ** 2)
        sm[i] = (w[:, None] * p).sum(0) / w.sum()
    corr = sm - p
    json.dump({'corr': np.round(corr, 3).tolist()}, open(f'{REEL}/idx/{name}_stab.json', 'w'))
    print(f'{name}: {len(p)} renders, correction up to {np.abs(corr).max(0).round(2)} px (x, y), '
          f'rms {np.sqrt((corr ** 2).mean(0)).round(2)}')


if __name__ == '__main__':
    for c in sys.argv[1:]:
        main(c)
