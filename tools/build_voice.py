#!/usr/bin/env python3
"""Turn the narration script (src/voice/lines.yaml) into the pack's voice files.

  python3 tools/build_voice.py                       # use recordings in src/voice/raw/ only
  python3 tools/build_voice.py --kokoro MODEL_DIR    # synthesise missing lines with Kokoro (open TTS, Apache-2.0)

For each line: a recording in src/voice/raw/<line>.(wav|mp3|ogg|flac) wins (drop in human or ElevenLabs takes there
any time); otherwise, with --kokoro, the line is synthesised (kokoro-onnx, model files kokoro-v1.0.onnx and
voices-v1.0.bin in MODEL_DIR) into .cache/voice/<line>.wav. Then every line gets its speaker's treatment with
ffmpeg and is written as pack/kubejs/assets/remnants/sounds/vo/<line>.ogg (stereo, so Minecraft plays it like music
rather than placing it in the world), and sounds.json + the subtitle lang keys are regenerated.

Speakers: keeper (an old voice by the fire: deeper, slower, a little room) and whisper (the voice from nowhere).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "src" / "voice" / "lines.yaml"
RAW = ROOT / "src" / "voice" / "raw"
CACHE = ROOT / ".cache" / "voice"
ASSETS = ROOT / "pack" / "kubejs" / "assets" / "remnants"
OUT = ASSETS / "sounds" / "vo"

KOKORO_VOICE = {"keeper": "bm_george", "whisper": "am_onyx"}
KOKORO_SPEED = {"keeper": 0.86, "whisper": 0.8}

# ffmpeg filter chains. asetrate lowers pitch and tempo together; atempo puts some of the speed back.
FILTERS = {
    "keeper": "asetrate=24000*0.92,aresample=44100,atempo=1.04,"
              "highpass=f=70,lowpass=f=9000,"
              "aecho=0.8:0.7:45|90:0.18|0.10,"
              "loudnorm=I=-17:TP=-1.5:LRA=9",
    "whisper": "asetrate=24000*0.84,aresample=44100,"
               "afftfilt=real='hypot(re,im)*cos((random(0)*2-1)*2*3.14)':"
               "imag='hypot(re,im)*sin((random(1)*2-1)*2*3.14)':win_size=512:overlap=0.75,"
               "highpass=f=180,aecho=0.8:0.85:120|260:0.35|0.22,"
               "loudnorm=I=-20:TP=-2:LRA=7",
}
SUBTITLES = {"keeper": "The Keeper speaks", "whisper": "Something whispers"}


def kokoro_synth(model_dir, line, speaker, text):
    """Synthesise paragraph by paragraph with a pause between them; write .cache/voice/<line>.wav."""
    import numpy as np
    import soundfile as sf
    from kokoro_onnx import Kokoro
    global _kokoro
    try:
        _kokoro
    except NameError:
        _kokoro = Kokoro(str(Path(model_dir) / "kokoro-v1.0.onnx"), str(Path(model_dir) / "voices-v1.0.bin"))
    chunks, rate = [], 24000
    for para in [p for p in text.split("\n\n") if p.strip()]:
        samples, rate = _kokoro.create(para, voice=KOKORO_VOICE[speaker], speed=KOKORO_SPEED[speaker], lang="en-gb")
        chunks += [samples, np.zeros(int(rate * 0.7), dtype=samples.dtype)]
    CACHE.mkdir(parents=True, exist_ok=True)
    out = CACHE / f"{line}.wav"
    sf.write(out, np.concatenate(chunks), rate)
    return out


def source_for(line):
    for ext in ("wav", "mp3", "ogg", "flac"):
        if (RAW / f"{line}.{ext}").exists():
            return RAW / f"{line}.{ext}", True
    if (CACHE / f"{line}.wav").exists():
        return CACHE / f"{line}.wav", False
    return None, False


def master(src, speaker, recorded, dest):
    # Real recordings keep their own voice: only levels and the room, no pitch change.
    chain = FILTERS[speaker] if not recorded else FILTERS[speaker].split("aresample=44100,", 1)[-1]
    if recorded:
        chain = "aresample=44100," + chain
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-af", chain, "-ac", "2", "-ar", "44100",
                    "-c:a", "libvorbis", "-q:a", "4", str(dest)], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kokoro", help="directory with kokoro-v1.0.onnx and voices-v1.0.bin")
    ap.add_argument("--only", nargs="*", help="only these line ids")
    ap.add_argument("--resynth", action="store_true", help="re-synthesise lines already in .cache/voice")
    args = ap.parse_args()
    script = yaml.safe_load(SCRIPT.read_text())
    sounds, missing = {}, []
    for line, entry in script.items():
        speaker = entry["speaker"]
        if not args.only or line in args.only:
            src, recorded = source_for(line)
            if args.kokoro and not recorded and (src is None or args.resynth):
                src = kokoro_synth(args.kokoro, line, speaker, entry["text"])
            if src is None:
                missing.append(line)
            else:
                master(src, speaker, recorded, OUT / f"{line}.ogg")
                print(f"{'recorded' if recorded else 'kokoro  '} {line}")
        if (OUT / f"{line}.ogg").exists():
            sounds[f"vo.{line}"] = {"subtitle": f"subtitles.remnants.vo.{speaker}",
                                    "sounds": [{"name": f"remnants:vo/{line}", "stream": True}]}
    (ASSETS / "sounds.json").write_text(json.dumps(sounds, indent=2) + "\n")
    lang = ASSETS / "lang" / "en_us.json"
    data = json.loads(lang.read_text()) if lang.exists() else {}
    for speaker, text in SUBTITLES.items():
        data[f"subtitles.remnants.vo.{speaker}"] = text
    lang.parent.mkdir(parents=True, exist_ok=True)
    lang.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"{len(sounds)} lines in sounds.json" + (f"; no audio yet: {', '.join(missing)}" if missing else ""))
    if missing:
        sys.exit(1)


if __name__ == "__main__":
    main()
