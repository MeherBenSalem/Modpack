#!/bin/bash
# Downloads the reel's sound effects from Mixkit (Mixkit Sound Effects Free License: free for commercial use in
# videos, no attribution required) into $1 (default $REEL/sfxlib) as WAV, and the music bed (Mixkit Stock Music Free
# License) into $REEL/musiclib. Files served only as MP3 previews are converted to WAV. Nothing here is synthesised.
set -e
REEL=${REEL:-/home/user/reel}
D=${1:-$REEL/sfxlib}; mkdir -p "$D"
# bells, trailer impacts and whooshes, low drums, swords on armour, stomps, fire, wind, horns, heartbeat
for id in 619 623 788 2900 2901 2908 2918 1143 784 498 565 549 546 2630 561 786 632 790 1486 1492 1469 1468 \
          2762 2763 2765 2766 2794 2795 2797 2789 2160 2776 1476 2792 1506 2775 3046 3057 1327 1349 1330 1340 \
          1157 1177 2785 2289 3111 490 497 2291 1687 2902 2907 2909 551 563 557 227; do
  f="$D/$id.wav"; [ -s "$f" ] && continue
  curl -sf --max-time 60 -o "$f" "https://assets.mixkit.co/active_storage/sfx/$id/$id.wav" || rm -f "$f"
  if ! head -c 4 "$f" 2>/dev/null | grep -q RIFF; then
    rm -f "$f"
    curl -sf --max-time 60 -o "$D/$id.mp3" "https://assets.mixkit.co/active_storage/sfx/$id/$id-preview.mp3"
    ffmpeg -loglevel error -y -i "$D/$id.mp3" -c:a pcm_s16le "$f" && rm "$D/$id.mp3"
  fi
done
ls "$D" | wc -l
# The music bed: "Epical Drums 03" by Grigoriy Nuzhny (Mixkit Stock Music Free License).
M=$REEL/musiclib; mkdir -p "$M"
[ -s "$M/678.mp3" ] || curl -sf --max-time 120 -o "$M/678.mp3" "https://assets.mixkit.co/music/678/678.mp3"
