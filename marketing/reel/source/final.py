#!/usr/bin/env python3
"""Mixes and masters the reel's sound and muxes it with both picture cuts:

  $REEL/edit/mix.wav                      the master (48 kHz stereo, about -14 LUFS, true peak under -1 dBTP)
  $REEL/out/remnants-beta9-reel-9x16.mp4  1080x1920 60 fps H.264 High (CRF 17) + AAC 320k, for upload
  $REEL/out/remnants-beta9-reel-16x9.mp4  1920x1080 60 fps H.264 High (CRF 17) + AAC 320k

The voice gets the channel narration chain and nothing else (high-pass 75 Hz, +1.5 dB at 3.5 kHz, de-ess,
2.5:1 compression), then a fixed level. The music is sidechain-ducked under the voice; the effects are ducked a
little, so hits keep their punch. Loudness is set with two-pass EBU R128 normalisation (linear gain) and checked
afterwards with ffmpeg's ebur128 true-peak meter.
"""
import json
import os
import re
import subprocess
from pathlib import Path

REEL = Path(os.environ.get('REEL', '/home/user/reel'))
E = REEL / 'edit'
OUT = REEL / 'out'
OUT.mkdir(exist_ok=True)
CHAIN = 'highpass=f=75,equalizer=f=3500:t=q:w=1:g=1.5,deesser=i=0.35,acompressor=threshold=-20dB:ratio=2.5:attack=10:release=120'
mixcfg = json.loads((E / 'cues.json').read_text()).get('mix', {})
VO_DB = mixcfg.get('vo_db', 3.0)
MUS_DB = mixcfg.get('music_db', -7.0)
SFX_DB = mixcfg.get('sfx_db', -4.0)

GRAPH = (
    f'[0:a]{CHAIN},volume={VO_DB}dB,pan=stereo|c0=c0|c1=c0,asplit=3[vo][sc1][sc2];'
    f'[1:a]volume={MUS_DB}dB[mu];'
    f'[2:a]volume={SFX_DB}dB[fx];'
    '[mu][sc1]sidechaincompress=threshold=0.03:ratio=3:attack=20:release=450:knee=4[mud];'
    '[fx][sc2]sidechaincompress=threshold=0.03:ratio=2.5:attack=5:release=220:knee=3[fxd];'
    '[vo][mud][fxd]amix=inputs=3:normalize=0:duration=first[mix]'
)


def run(args):
    return subprocess.run(args, capture_output=True, text=True, check=True)


def premix():
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', E / 'vo_raw.wav', '-i', E / 'music.wav', '-i', E / 'sfx.wav',
         '-filter_complex', GRAPH, '-map', '[mix]', '-c:a', 'pcm_f32le', '-ar', '48000', E / 'premix.wav'])


def master():
    p = run(['ffmpeg', '-hide_banner', '-i', E / 'premix.wav', '-af',
             'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'])
    m = json.loads(re.search(r'\{[^{}]*"input_i"[^{}]*\}', p.stderr).group(0))
    af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:linear=true:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']},"
          "aresample=48000")
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', E / 'premix.wav', '-af', af, '-c:a', 'pcm_s24le', E / 'mix.wav'])


def measure(path):
    p = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(path), '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True)
    s = p.stderr[p.stderr.rfind('Summary:'):]
    i = float(re.search(r'I:\s+(-?[\d.]+) LUFS', s).group(1))
    tp = float(re.search(r'Peak:\s+(-?[\d.]+) dBFS', s).group(1))
    return i, tp


def mux():
    for tag, base in (('9x16', 'base_v.mp4'), ('16x9', 'base_h.mp4')):
        run(['ffmpeg', '-y', '-loglevel', 'error', '-i', E / base, '-i', E / 'mix.wav', '-map', '0:v', '-map', '1:a',
             '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-profile:v', 'high', '-pix_fmt', 'yuv420p',
             '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-g', '120',
             '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-movflags', '+faststart', '-shortest',
             OUT / f'remnants-beta9-reel-{tag}.mp4'])


if __name__ == '__main__':
    premix()
    master()
    i, tp = measure(E / 'mix.wav')
    print(f'master: {i:.1f} LUFS integrated, true peak {tp:.1f} dBTP')
    if tp > -1.0:
        raise SystemExit('true peak above -1 dBTP')
    mux()
    for f in sorted(OUT.glob('*.mp4')):
        i, tp = measure(f)
        print(f'{f.name}: {i:.1f} LUFS, true peak {tp:.1f} dBTP')
