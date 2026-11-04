#!/usr/bin/env python3
"""The reel's single source of truth: the beat grid, the Keeper's lines, the shots and what plays when.

Writes $REEL/edit/edl.json (picture: shots, framing, overlays), $REEL/edit/cues.json (sound: voice, music, effects)
and ../SCRIPT.md (the script with its line timing fit check). Refuses a plan where a line would not fit its slot,
two lines would overlap, or a shot would play its footage slower than real time.

Music: "Epical Drums 03" (Grigoriy Nuzhny, Mixkit), 80 BPM, beats on 3.04 + 0.75 n s of the source. One continuous
excerpt from source 126.04 s (bar 41) is placed at reel 4.0 s, so the source's breakdown (142.5-146.3) sits under
the fog gate, its drop (147.04) lands at reel 25.0 on the first clash with Ser Odric, and its last hit (171.04) at
reel 49.0 on the title. The track's own ending closes the reel.
"""
import json
import os
from pathlib import Path

REEL = Path(os.environ.get('REEL', '/home/user/reel'))
HERE = Path(__file__).resolve().parent
OUT = REEL / 'edit'
OUT.mkdir(parents=True, exist_ok=True)

FPS = 60
BEAT = 0.75
MUSIC_SRC0 = 126.04          # source time placed at MUSIC_AT
MUSIC_AT = 4.0
DURATION = 53.5


def beat(n):
    """Reel time of the n-th beat after the music enters (n may be fractional)."""
    return round(MUSIC_AT + n * BEAT, 4)


def src_to_reel(s):
    return round(MUSIC_AT + (s - MUSIC_SRC0), 4)


LINES = json.loads((REEL / 'vo' / 'lines.json').read_text())

# ---------------------------------------------------------------- the Keeper: line id -> reel start time
VO = {
    'V1': 0.70,
    'V2': 1.70,
    'V3': 5.55,
    'V4': 12.55,
    'V5': 18.05,
    'V6': 21.75,
    'V7': 25.85,
    'V9': 37.35,
    'V11': 43.35,
    'V13': 50.15,
}
# Each line owns a slot that ends where the next line (or a hard musical moment) begins.
SLOT_END = {'V1': 1.70, 'V2': 5.0, 'V3': 12.4, 'V4': 18.0, 'V5': 21.7, 'V6': 25.0, 'V7': 31.0, 'V9': 43.0,
            'V11': 49.0, 'V13': DURATION}


def word_time(line, word_prefix, which='s', nth=0):
    hits = [w for w in LINES[line]['words'] if w['w'].lower().strip('.,!?').startswith(word_prefix)]
    return round(VO[line] + hits[nth][which], 4)


def fit_check():
    rows, ok = [], True
    order = sorted(VO, key=VO.get)
    for a, b in zip(order, order[1:] + [None]):
        end = VO[a] + LINES[a]['dur']
        slot = SLOT_END[a] - VO[a]
        fits = LINES[a]['dur'] <= slot + 1e-6 and (b is None or end <= VO[b] - 0.05)
        ok &= fits
        rows.append((a, VO[a], LINES[a]['dur'], slot, fits))
    return ok, rows


# ---------------------------------------------------------------- shots
# src: capture name; g0: game time (s) of the capture at the shot's first frame; speed: 1.0 = real time (never
# less); vx: portrait window centre x keys [[local, x]], hy: landscape window centre y keys.
def shot(name, src, start, end, g0, speed=1.0, **kw):
    s = {'name': name, 'src': src, 'start': round(start, 4), 'end': round(end, 4)}
    if src:
        assert speed >= 1.0, f'{name}: footage may not play slower than real time'
        s['map'] = [[0.0, g0], [round(end - start, 4), round(g0 + (end - start) * speed, 4)]]
    s.update(kw)
    return s


SRC = json.loads((HERE / 'src_times.json').read_text())   # event times read off the contact sheets


def cuts():
    """The reel's cut points: on the beat, or on a word of the Keeper's."""
    return {
        'intro_in': 1.55,
        'reveal': beat(1),                              # 4.75: the black sun
        'peak': beat(5),                                # 8.75
        'realm': word_time('V3', 'black') - 0.10,       # on "black"
        'ranked': beat(11),                             # 12.25
        'ranked2': beat(14),                            # 14.5
        'wake': beat(18),                               # 17.5
        'fog': beat(23),                                # 21.25
        'odric_in': beat(26),                           # 23.5
        'drop': src_to_reel(147.04),                    # 25.0: the music's drop
        'odric2': beat(30),                             # 26.5
        'fights': beat(35),                             # 30.25
        'rider': beat(39),                              # 33.25: a Sovereign, the Dusk Rider
        'echo': beat(44),                               # 37.0
        'echo2': beat(47),                              # 39.25
        'shrine': beat(52),                             # 43.0
        'sovereign': beat(56),                          # 46.0: "...and one Sovereign at a time"
        'title': src_to_reel(171.04),                   # 49.0: the last hit
        'end': DURATION,
        'slam': word_time('V7', 'lands', 's'),          # Odric's Ash Slam lands on "lands"
    }


def build_shots():
    C = cuts()
    shots, t = [], 0.0
    for sh in SRC['shots']:
        end = C[sh['to']]
        extra = {k: v for k, v in sh.items() if k not in ('name', 'src', 'to', 'g0', 'g0_end', 'flash', 'shake', 'vx', 'hud',
                                                         'vx_override', 'hy_override')}
        if sh.get('hud'):   # windows that keep only whole HUD elements (boss bar, plates, hotbar), never fragments
            extra['vx'] = [[0, 1130]]
            extra['hy'] = [[0, 1010]]
        if 'hy_override' in sh:
            extra['hy'] = [[0, sh['hy_override']]]
        if 'vx_override' in sh:   # pushed in 15% to rows 175-1845, below and above every HUD element: any x is clean
            extra['vx'] = [[0, sh['vx_override']]]
        if 'flash' in sh:
            extra['flash'] = [[C[sh['flash']], 0.22, 0.35]]
        if 'shake' in sh:
            extra['shake'] = [[C[sh['shake']], 9, 0.4]]
        if 'vx' in sh:
            extra['vx'] = [[0, sh['vx']]]
        src = sh['src']
        if src and not (REEL / 'idx' / f'{src}.json').exists():
            print(f"  (placeholder: {sh['name']} -> black until {src} is captured)")
            src = None
        g0 = sh.get('g0', 0.0) if 'g0_end' not in sh else sh['g0_end'] - (end - t)
        shots.append(shot(sh['name'], src, t, end, g0, **extra))
        t = end
    return shots


# ---------------------------------------------------------------- overlays
def overlays():
    items = []
    for line, start in VO.items():
        nxt = min([v for v in VO.values() if v > start] + [DURATION])
        end = min(nxt - 0.1, start + LINES[line]['dur'] + 0.55)
        words = [dict(w) for w in LINES[line]['words']]
        script_words = LINES[line]['text'].split()
        assert len(script_words) == len(words), (line, script_words, [w['w'] for w in words])
        for w, sw in zip(words, script_words):
            w['w'] = sw
        items.append({'type': 'caption', 'line': line, 'start': start, 'end': end, 'fade_in': 0.12, 'fade_out': 0.3,
                      'words': words, 'pos': {'v': [0.5, 0.735], 'h': [0.5, 0.83]}})
    items += [
        {'type': 'tag', 'text': "BETA 9  ·  THE KEEPER'S VOICE", 'start': 17.7, 'end': 21.1,
         'pos': {'v': [0.5, 0.15], 'h': [0.5, 0.1]}, 'fade_in': 0.35, 'fade_out': 0.35},
        {'type': 'tag', 'text': 'AN OPENING TALE ON YOUR FIRST JOIN', 'start': 2.0, 'end': 4.6,
         'pos': {'v': [0.5, 0.15], 'h': [0.5, 0.1]}, 'fade_in': 0.35, 'fade_out': 0.25},
        {'type': 'scrim', 'start': 48.9, 'end': DURATION, 'a0': 0.62, 'depth': {'v': 0.42, 'h': 0.62},
         'fade_in': 0.5, 'fade_out': 0.6},
        {'type': 'title', 'start': 49.0, 'end': DURATION, 'pos': {'v': [0.5, 0.155], 'h': [0.5, 0.2]},
         'fade_in': 0.5, 'fade_out': 0.6, 'drift': 3},
        {'type': 'tag', 'text': 'BETA 9  ·  OUT NOW ON CURSEFORGE', 'start': 50.9, 'end': DURATION,
         'pos': {'v': [0.5, 0.282], 'h': [0.5, 0.415]}, 'fade_in': 0.4, 'fade_out': 0.6},
    ]
    return items


def main():
    ok, rows = fit_check()
    md = ['# Script: the Keeper\'s lines and the line timing fit check', '',
          'Every line is an existing in-game recording of the Keeper from `src/voice/raw/` (made with ElevenLabs for',
          'beta 9: voice "Arkadius - Old Storyteller", model `eleven_v4`). `source/build_vo.py` cuts the phrase out of',
          'the take at measured silences; nothing is sped up or stretched. The edit gives each line a slot at least as',
          'long as the line (generated by `source/plan.py`, which refuses a plan that does not fit).', '',
          '| Line | Take | Words | Starts | Length | Slot | Fits |', '| --- | --- | --- | --- | --- | --- | --- |']
    for a, st, du, slot, fits in rows:
        md.append(f"| {a} | `{LINES[a]['take']}` | {LINES[a]['text']} | {st:.2f} s | {du:.2f} s | {slot:.2f} s | "
                  f"{'yes' if fits else '**NO**'} |")
    md += ['', f'Total narration: {sum(LINES[a]["dur"] for a in VO):.2f} s of a {DURATION:.1f} s reel.', '',
           'Every take was word-checked: `source/wordtimes.py` transcribes each cut with faster-whisper (medium.en) and',
           '`source/verify.py` compares it with the script above, word for word.']
    (HERE.parent / 'SCRIPT.md').write_text('\n'.join(md) + '\n')
    if not ok:
        raise SystemExit('a line does not fit its slot:\n' + '\n'.join(str(r) for r in rows if not r[4]))
    C = cuts()
    shots = build_shots()
    for a, b in zip(shots, shots[1:]):
        assert abs(a['end'] - b['start']) < 1e-6, (a['name'], b['name'])
    json.dump({'fps': FPS, 'duration': DURATION, 'shots': shots, 'overlays': overlays()},
              open(OUT / 'edl.json', 'w'), indent=1)
    cues = {'duration': DURATION, 'music': {'file': 'musiclib/678.mp3', 'src0': MUSIC_SRC0, 'at': MUSIC_AT},
            'vo': [{'line': k, 'at': v} for k, v in sorted(VO.items(), key=lambda kv: kv[1])],
            'sfx': [dict(x, at=(C[x['at']] if isinstance(x['at'], str) else x['at'])) for x in SRC.get('sfx', [])],
            'mix': {'vo_db': 3.0, 'music_db': -6.0, 'sfx_db': -4.0}}
    cues['music'].update(SRC.get('music', {}))
    json.dump(cues, open(OUT / 'cues.json', 'w'), indent=1)
    for s in shots:
        print(f"{s['start']:6.2f}-{s['end']:6.2f}  {s['name']}")
    print('fit check: all lines fit')


if __name__ == '__main__':
    main()
