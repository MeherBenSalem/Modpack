#!/usr/bin/env python3
"""Record the narration script (src/voice/lines.yaml) with ElevenLabs into src/voice/raw/<line>.mp3.

  ELEVENLABS_API_KEY=... python3 tools/eleven_voice.py                 # every line without a recording yet
  ELEVENLABS_API_KEY=... python3 tools/eleven_voice.py --only a b      # just these lines (re-records them)
  ELEVENLABS_API_KEY=... python3 tools/eleven_voice.py --take 2 ...    # another take: a different seed
  python3 tools/eleven_voice.py --dry-run                              # list what would be recorded and the cost

Then run tools/build_voice.py, which masters src/voice/raw/ into the pack. The key is read from the environment
only; it is never written anywhere. Each request costs one credit per character on the models below.

Voices (added to the account from the voice library):
  keeper   "Arkadius - Old Storyteller" (O4uxPTtvgxrA0QCLHI1J): an old storyteller by the fire.
  whisper  "Glenn - SleepStory, Whisper & Gravely" (80POrI92mU3QZbdwHl4r): the voice from nowhere.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "src" / "voice" / "lines.yaml"
RAW = ROOT / "src" / "voice" / "raw"
MODEL = "eleven_v4"
VOICES = {"keeper": "O4uxPTtvgxrA0QCLHI1J", "whisper": "80POrI92mU3QZbdwHl4r"}
SETTINGS = {
    "keeper": {"stability": 0.5, "similarity_boost": 0.8, "style": 0.0, "use_speaker_boost": True},
    "whisper": {"stability": 0.5, "similarity_boost": 0.75, "style": 0.0, "use_speaker_boost": True},
}


def spoken(text):
    """The script's paragraphs, joined the way they're read aloud."""
    return " ".join(p.strip() for p in text.split("\n\n") if p.strip()).replace("\n", " ")


def record(key, line, entry, take):
    body = {
        "text": spoken(entry["text"]),
        "model_id": MODEL,
        "voice_settings": SETTINGS[entry["speaker"]],
        "seed": 1000 * take + sum(map(ord, line)) % 1000,
    }
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICES[entry['speaker']]}?output_format=mp3_44100_128",
        data=json.dumps(body).encode(), method="POST",
        headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:300]
            if e.code in (429, 500, 502, 503) and attempt < 3:
                time.sleep(5 * (attempt + 1))
                continue
            sys.exit(f"{line}: HTTP {e.code} {msg}")
        except urllib.error.URLError:
            if attempt == 3:
                raise
            time.sleep(5)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", help="these lines (re-records them)")
    ap.add_argument("--take", type=int, default=1, help="take number (changes the seed)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    lines = yaml.safe_load(SCRIPT.read_text())
    if args.only:
        missing = [l for l in args.only if l not in lines]
        if missing:
            sys.exit(f"not in the script: {missing}")
        todo = args.only
    else:
        todo = [l for l in lines if not any((RAW / f"{l}.{ext}").exists() for ext in ("mp3", "wav", "ogg", "flac"))]
    chars = sum(len(spoken(lines[l]["text"])) for l in todo)
    print(f"{len(todo)} lines, {chars} characters ({MODEL}, 1 credit per character)")
    if args.dry_run or not todo:
        return
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        sys.exit("set ELEVENLABS_API_KEY")
    RAW.mkdir(parents=True, exist_ok=True)
    for i, line in enumerate(todo, 1):
        audio = record(key, line, lines[line], args.take)
        (RAW / f"{line}.mp3").write_bytes(audio)
        print(f"[{i}/{len(todo)}] {line}: {len(audio) // 1024} KB")


if __name__ == "__main__":
    main()
