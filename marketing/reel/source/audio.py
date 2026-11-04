#!/usr/bin/env python3
"""Builds the reel's three stems from $REEL/edit/cues.json (48 kHz):

  vo_raw.wav     the Keeper's lines (cut by build_vo.py) at their reel times, mono, untouched
  music.wav      "Epical Drums 03" from cues.music.src0, placed at cues.music.at (a short fade in), stereo
  sfx.wav        every sound effect, its measured main hit (sfx_hits.json) landing on the cue's frame, stereo

final.sh mixes them: the narration chain on the voice, the music and effects sidechain-ducked under it, mastered.
Nothing is synthesised; the effects are Mixkit recordings (fetch_sfx.sh), placed, levelled, panned and faded.
"""
import json
import os
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

REEL = Path(os.environ.get('REEL', '/home/user/reel'))
E = REEL / 'edit'
SR = 48000
cues = json.loads((E / 'cues.json').read_text())
N = int(round(cues['duration'] * SR))
HITS = json.loads((REEL / 'sfx_hits.json').read_text())


def decode(path, channels):
    tmp = E / f'_dec_{Path(path).stem}_{channels}.wav'
    if not tmp.exists():
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', str(path), '-ac', str(channels), '-ar', str(SR),
                        '-c:a', 'pcm_f32le', str(tmp)], check=True)
    a, _ = sf.read(tmp, dtype='float32', always_2d=True)
    return a


def place(buf, clip, at):
    i0 = int(round(at * SR))
    s0 = max(0, -i0)
    i0 = max(0, i0)
    n = min(len(clip) - s0, len(buf) - i0)
    if n > 0:
        buf[i0:i0 + n] += clip[s0:s0 + n]


# ---------------------------------------------------------------- voice
vo = np.zeros((N, 1), np.float32)
for c in cues['vo']:
    clip, sr = sf.read(REEL / 'vo' / f"{c['line']}.wav", dtype='float32', always_2d=True)
    assert sr == SR
    place(vo, clip, c['at'])
sf.write(E / 'vo_raw.wav', vo, SR, subtype='FLOAT')

# ---------------------------------------------------------------- music
m = cues['music']
song = decode(REEL / m['file'], 2)
pre = m.get('pre', 0.6)                    # start a little before src0 and fade in over it
s0 = int(round((m['src0'] - pre) * SR))
clip = song[s0:].copy()
f = int(pre * SR)
clip[:f] *= np.linspace(0, 1, f)[:, None] ** 2
mus = np.zeros((N, 2), np.float32)
place(mus, clip, m['at'] - pre)
tail = int(m.get('tail_fade', 0.0) * SR)
if tail:
    mus[N - tail:] *= np.linspace(1, 0, tail)[:, None]
for d in m.get('dips', []):                # [start, end, depth_db]: make room for a hit or a held breath
    a, b, db = int(d[0] * SR), int(d[1] * SR), d[2]
    g = np.ones(N, np.float32)
    ramp = int(0.06 * SR)
    g[a:b] = 10 ** (db / 20)
    g[a - ramp:a] = np.linspace(1, 10 ** (db / 20), ramp)
    g[b:b + ramp] = np.linspace(10 ** (db / 20), 1, min(ramp, N - b))
    mus *= g[:, None]
sf.write(E / 'music.wav', mus * 10 ** (m.get('gain_db', 0) / 20), SR, subtype='FLOAT')

# ---------------------------------------------------------------- effects
fx = np.zeros((N, 2), np.float32)
for c in cues['sfx']:
    a = decode(REEL / 'sfxlib' / f"{c['id']}.wav", 2)
    hit = c.get('hit', HITS[str(c['id'])]['hit'])
    a = a[int(max(0, hit - c.get('pre', hit)) * SR):]          # optionally trim a long lead-in before the hit
    lead = min(hit, c.get('pre', hit))
    if c.get('dur'):
        a = a[:int((lead + c['dur']) * SR)].copy()
        fo = int(min(0.25, c['dur'] * 0.3) * SR)
        a[-fo:] *= np.linspace(1, 0, fo)[:, None]
    fi = int(c.get('fade_in', 0.004) * SR)
    a[:fi] *= np.linspace(0, 1, fi)[:, None]
    pan = c.get('pan', 0.0)                                     # constant-power balance
    a = a * np.array([np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)]) * np.sqrt(2)
    place(fx, a * 10 ** (c.get('gain_db', 0) / 20), c['at'] - lead)
sf.write(E / 'sfx.wav', fx, SR, subtype='FLOAT')
print('stems written:', ', '.join(p.name for p in (E / 'vo_raw.wav', E / 'music.wav', E / 'sfx.wav')),
      f"({len(cues['vo'])} lines, {len(cues['sfx'])} effects)")
