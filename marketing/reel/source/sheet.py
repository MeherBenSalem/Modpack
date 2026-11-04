#!/usr/bin/env python3
"""sheet.py <clip> [step_game_s=0.5] [cols=6]: a contact sheet of a raw capture, one frame per step of game time,
each tile labelled with its game time ($REEL/sheets/<clip>.jpg). Used to review every capture and to read off
event times (the swing that lands, the roll, the title appearing) for the edit."""
import os
import sys

import cv2
import numpy as np

REEL = os.environ.get('REEL', '/home/user/reel')
SLOW, CAP_FPS = float(os.environ.get('SLOW', '30')), 8.0
clip = sys.argv[1]
step = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 6
cap = cv2.VideoCapture(f'{REEL}/raw/{clip}.mkv')
n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
tiles, i, want = [], 0, 0.0
while True:
    ok, f = cap.read()
    if not ok:
        break
    g = i / CAP_FPS / SLOW
    if g >= want:
        t = cv2.resize(f, (320, 320), interpolation=cv2.INTER_AREA)
        cv2.putText(t, f'{g:.2f}', (6, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        tiles.append(t)
        want += step
    i += 1
while len(tiles) % cols:
    tiles.append(np.zeros_like(tiles[0]))
rows = [np.hstack(tiles[k:k + cols]) for k in range(0, len(tiles), cols)]
os.makedirs(f'{REEL}/sheets', exist_ok=True)
out = f'{REEL}/sheets/{clip}.jpg'
cv2.imwrite(out, np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 80])
print(out, len(tiles), 'tiles,', round(i / CAP_FPS / SLOW, 2), 'game s')
