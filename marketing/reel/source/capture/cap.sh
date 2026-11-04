#!/bin/bash
# cap.sh <name> <real_seconds>: grabs the 1920x1920 game display :2 at 8 fps (the slowed game renders about 2.5 frames a
# real second, so every render is caught at least twice) into $REEL/raw/<name>.mkv. prep.py keeps one copy of each.
REEL=${REEL:-/home/user/reel}; mkdir -p "$REEL/raw"
exec ffmpeg -loglevel error -y -f x11grab -video_size 1920x1920 -framerate 8 -draw_mouse 0 -i :2 -t "$2" -threads 2 \
  -c:v libx264 -preset ultrafast -crf 13 -pix_fmt yuv420p "$REEL/raw/$1.mkv"
