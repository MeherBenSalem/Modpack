#!/usr/bin/env python3
"""Cuts the reel's Keeper lines out of the pack's own recordings (src/voice/raw/, voice/script.json) into
$REEL/vo/<id>.wav (48 kHz mono, untouched otherwise: no speed change, no time-stretch) and writes
$REEL/vo/lines.json with each line's real length and the word timings inside it (for the edit and captions).

A phrase starts just inside the measured silence before its first word and ends inside the first measured silence
after its last word (cut_points), with 12 ms fades, so no syllable or breath is clipped and nothing of the next phrase
leaks in."""
import json
import os
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[3]
REEL = Path(os.environ.get('REEL', '/home/user/reel'))
HERE = Path(__file__).resolve().parent
SR = 48000
script = json.loads((HERE / 'voice' / 'script.json').read_text())
words = json.loads((REEL / 'wordtimes.json').read_text())
out_dir = REEL / 'vo'
out_dir.mkdir(exist_ok=True)


def load(take):
    wav = out_dir / f'_{take}.wav'
    if not wav.exists():
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', str(ROOT / 'src/voice/raw' / f'{take}.mp3'),
                        '-ac', '1', '-ar', str(SR), str(wav)], check=True)
    return sf.read(wav, dtype='float32')[0]


def silences(a, thresh_db=-52, min_len=0.06):
    """Silent stretches of a take as (start, end) seconds: 10 ms frames below thresh_db for at least min_len."""
    hop = int(0.01 * SR)
    n = len(a) // hop
    e = 10 * np.log10(np.mean(a[:n * hop].reshape(n, hop) ** 2, axis=1) + 1e-12)
    quiet = e < thresh_db
    out, k = [], 0
    while k < n:
        if quiet[k]:
            j = k
            while j < n and quiet[j]:
                j += 1
            if (j - k) * 0.01 >= min_len:
                out.append((k * 0.01, j * 0.01))
            k = j
        else:
            k += 1
    return out


def cut_points(a, w0, w1, first, last):
    """Start in the silence before the first word (keeping 80 ms of it), end in the first silence after the last
    word (keeping up to 250 ms of its tail): measured on the audio, since Whisper's word edges are approximate."""
    sil = silences(a)
    start = 0.0
    if not first:
        before = [s for s in sil if s[1] <= w0['s'] + 0.12]
        if before:
            s0, s1 = before[-1]
            start = max(s0, s1 - 0.08)
    end = len(a) / SR
    if not last:
        after = [s for s in sil if s[0] >= w1['e'] - 0.2]
        if after:
            s0, s1 = after[0]
            end = min(s1 - 0.02, s0 + 0.25)
    return start, end


lines = {}
for ln in script['lines']:
    a = load(ln['take'])
    ws = words[ln['take']]
    i, j = ln['words']
    w0, w1 = ws[i], ws[j]
    start, end = cut_points(a, w0, w1, i == 0, j + 1 == len(ws))
    seg = a[int(start * SR):int(end * SR)].copy()
    f = int(0.012 * SR)
    seg[:f] *= np.linspace(0, 1, f)
    seg[-f:] *= np.linspace(1, 0, f)
    # trailing digital silence is trimmed to 120 ms past the last audible sample, so the slot length is honest
    loud = np.where(np.abs(seg) > 10 ** (-50 / 20))[0]
    if len(loud):
        seg = seg[:min(len(seg), loud[-1] + int(0.12 * SR))]
    sf.write(out_dir / f"{ln['id']}.wav", seg, SR)
    lines[ln['id']] = {'text': ln['text'], 'take': ln['take'], 'src': [round(start, 3), round(start + len(seg) / SR, 3)],
                       'dur': round(len(seg) / SR, 3),
                       'words': [{'w': w['w'], 's': round(w['s'] - start, 3), 'e': round(w['e'] - start, 3)}
                                 for w in ws[i:j + 1]]}
    print(f"{ln['id']:4s} {len(seg) / SR:5.2f} s  {ln['take']} [{start:.2f}-{start + len(seg) / SR:.2f}]  {ln['text']}")
(out_dir / 'lines.json').write_text(json.dumps(lines, indent=1))
print(f"total {sum(v['dur'] for v in lines.values()):.2f} s of voice")
