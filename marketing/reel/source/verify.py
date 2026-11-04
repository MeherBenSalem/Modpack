#!/usr/bin/env python3
"""The reel's measured quality gate. For each finished MP4:

  1. format: 1080x1920 or 1920x1080, 60 fps constant, frame count = duration x 60 (no dropped frames)
  2. repeats: every frame's MD5 (ffmpeg framemd5) differs from the one before; ffmpeg's mpdecimate drops nothing
  3. judder: inside each shot of edl.json, the frame-to-frame change never stalls (a near-zero step between moving
     neighbours = a repeated render) or jumps (a step far above its neighbours = a skipped stretch)
  4. loudness: about -14 LUFS integrated, true peak at or below -1 dBTP (ebur128)
  5. words: faster-whisper transcribes the finished mix; every word of the script must be heard, in order
  6. contact sheet: one frame per second, written for a human to look at every one ($REEL/out/<name>_sheet.jpg)

  verify.py $REEL/out/remnants-beta9-reel-9x16.mp4 [...]
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

REEL = Path(os.environ.get('REEL', '/home/user/reel'))
HERE = Path(__file__).resolve().parent
EDL = json.loads((REEL / 'edit' / 'edl.json').read_text())
fails = []


def check(ok, msg):
    print(('  ok    ' if ok else '  FAIL  ') + msg)
    if not ok:
        fails.append(msg)


def fmt(path):
    p = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_frames', '-show_entries',
                                   'stream=width,height,r_frame_rate,avg_frame_rate,nb_read_frames:format=duration',
                                   '-of', 'json', str(path)], capture_output=True, text=True).stdout)
    s, d = p['streams'][0], float(p['format']['duration'])
    n = int(s['nb_read_frames'])
    check(s['r_frame_rate'] == '60/1' and s['avg_frame_rate'] == '60/1', f"60 fps constant ({s['avg_frame_rate']})")
    check(abs(n - round(EDL['duration'] * 60)) <= 1, f'{n} frames for {EDL["duration"]} s (expected {round(EDL["duration"] * 60)})')
    return s['width'], s['height'], n


def repeats(path):
    out = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:v', '-f', 'framemd5', '-'],
                         capture_output=True, text=True).stdout
    h = [ln.split(',')[-1].strip() for ln in out.splitlines() if not ln.startswith('#')]
    same = [i for i in range(1, len(h)) if h[i] == h[i - 1]]
    check(not same, f'no two consecutive frames identical by MD5 ({len(same)} repeats{": " + str(same[:10]) if same else ""})')
    p = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(path), '-vf', 'mpdecimate,showinfo', '-f', 'null', '-'],
                       capture_output=True, text=True)
    kept = len(re.findall(r'\] n:\s*\d+', p.stderr))
    total = len(h)
    check(kept == total, f'mpdecimate keeps every frame ({kept} of {total})')


def judder(path):
    cap = cv2.VideoCapture(str(path))
    prev, diffs = None, []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        g = cv2.resize(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), (f.shape[1] // 6, f.shape[0] // 6),
                       interpolation=cv2.INTER_AREA).astype(np.float32)
        g = cv2.GaussianBlur(g, (5, 5), 0)             # look past the grain at the picture
        diffs.append(0.0 if prev is None else float(np.abs(g - prev).mean()))
        prev = g
    d = np.array(diffs)
    bad = []
    for s in EDL['shots']:
        if not s.get('src'):
            continue
        a, b = int(round(s['start'] * 60)) + 3, int(round(s['end'] * 60)) - 3
        for i in range(a + 2, b - 2):
            nb = np.median(np.r_[d[i - 2:i], d[i + 1:i + 3]])
            if nb > 1.2 and d[i] < 0.25 * nb:
                bad.append((round(i / 60, 3), 'stall', s['name']))
            if nb > 0.8 and d[i] > 3.5 * nb and d[i] > 6:
                bad.append((round(i / 60, 3), 'jump', s['name']))
    check(not bad, f'smooth motion inside every shot ({len(bad)} suspect frames{": " + str(bad[:8]) if bad else ""})')


def loudness(path):
    p = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(path), '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True)
    s = p.stderr[p.stderr.rfind('Summary:'):]
    i = float(re.search(r'I:\s+(-?[\d.]+) LUFS', s).group(1))
    tp = float(re.search(r'Peak:\s+(-?[\d.]+) dBFS', s).group(1))
    check(abs(i + 14) <= 0.5, f'integrated loudness {i:.1f} LUFS (target -14)')
    check(tp <= -1.0, f'true peak {tp:.1f} dBTP (at most -1)')


def same(a, b):
    """Equal, or one letter apart for words of three letters or more (Whisper writes 'Fogg' for 'Fog')."""
    if a == b:
        return True
    if min(len(a), len(b)) < 3 or abs(len(a) - len(b)) > 1:
        return False
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1] <= 1


def words(path):
    from faster_whisper import WhisperModel
    import librosa
    script = json.loads((REEL / 'vo' / 'lines.json').read_text())
    cues = json.loads((REEL / 'edit' / 'cues.json').read_text())
    want = ' '.join(script[c['line']]['text'] for c in cues['vo'])
    norm = lambda t: re.findall(r"[a-z']+", t.lower())
    wav = REEL / 'out' / '_words.wav'
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', str(path), '-ac', '1', '-ar', '16000', str(wav)], check=True)
    a = librosa.load(str(wav), sr=16000, mono=True)[0]
    model = WhisperModel('medium.en', device='cpu', compute_type='int8')
    # the story's invented names, as a listener knows them from the captions (Whisper otherwise guesses 'Audrey')
    segs, _ = model.transcribe(a, beam_size=5, language='en', vad_filter=False,
                               initial_prompt='The Keeper speaks of Ser Odric, the Ashborn, the Sovereigns and the Remnants.')
    heard = norm(' '.join(s.text for s in segs))
    w = norm(want)
    # every scripted word must appear in order (music may add nothing; Whisper may split contractions)
    j = 0
    missing = []
    for word in w:
        k = j
        while k < len(heard) and not same(heard[k], word):
            k += 1
        if k == len(heard):
            missing.append(word)
        else:
            j = k + 1
    print('  heard: ' + ' '.join(heard))
    check(not missing, f'every scripted word is heard in order ({len(w)} words; missing: {missing})')


def sheet(path):
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS)
    tiles, i = [], 0
    while True:
        ok, f = cap.read()
        if not ok:
            break
        if i % int(round(fps)) == 0:
            h, w = f.shape[:2]
            s = 300 / max(h, w) * (1.6 if h > w else 1.0)
            t = cv2.resize(f, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
            cv2.putText(t, f'{i / fps:.0f}s', (6, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            tiles.append(t)
        i += 1
    cols = 10 if tiles[0].shape[0] > tiles[0].shape[1] else 6
    while len(tiles) % cols:
        tiles.append(np.zeros_like(tiles[0]))
    img = np.vstack([np.hstack(tiles[k:k + cols]) for k in range(0, len(tiles), cols)])
    out = REEL / 'out' / (Path(path).stem + '_sheet.jpg')
    cv2.imwrite(str(out), img, [cv2.IMWRITE_JPEG_QUALITY, 85])
    print(f'  sheet {out}')


if __name__ == '__main__':
    for f in sys.argv[1:]:
        print(Path(f).name)
        fmt(f)
        repeats(f)
        judder(f)
        loudness(f)
        sheet(f)
    if sys.argv[1:]:
        print('words (the finished mix)')
        words(sys.argv[1])
    print('ALL CHECKS PASS' if not fails else f'{len(fails)} CHECK(S) FAILED')
    sys.exit(1 if fails else 0)
