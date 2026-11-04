#!/usr/bin/env python3
"""wordtimes.py <out.json> <audio>...: word-level timestamps (faster-whisper, medium.en, CPU) for each take, used to
cut the Keeper's existing recordings at their natural pauses and to word-check every take against the script."""
import json
import sys
from pathlib import Path

import librosa
from faster_whisper import WhisperModel

model = WhisperModel('medium.en', device='cpu', compute_type='int8')
out = {}
for f in sys.argv[2:]:
    audio = librosa.load(f, sr=16000, mono=True)[0]
    segs, _ = model.transcribe(audio, word_timestamps=True, beam_size=5, language='en', vad_filter=False)
    words = [{'w': w.word.strip(), 's': round(w.start, 3), 'e': round(w.end, 3), 'p': round(w.probability, 3)}
             for s in segs for w in s.words]
    out[Path(f).stem] = words
    print(Path(f).stem, ' '.join(w['w'] for w in words), flush=True)
Path(sys.argv[1]).write_text(json.dumps(out, indent=1))
