#!/bin/bash
# game.sh server|client [clock factor, default 0.05]
# Runs the reel's dedicated server ($REEL/server, unpacked from the real server pack) or the real client
# (client_prep.py) on a clock slowed 20x with libfaketime, so the software renderer draws far more frames per
# second of game time than the edit needs and none has to be repeated. The client opens a WxH window
# (default 1920x1920: the portrait and the landscape cut are both full-resolution crops of it) on Xvfb display :2.
F=${2:-0.05}
REEL=${REEL:-/home/user/reel}
if [ "$F" != 1 ]; then
  export FAKETIME="+0 x$F" FAKETIME_DONT_FAKE_MONOTONIC=0 LD_PRELOAD=/usr/lib/x86_64-linux-gnu/faketime/libfaketimeMT.so.1
fi
if [ "$1" = server ]; then
  cd "$REEL/server"
  exec java @user_jvm_args.txt @libraries/net/neoforged/neoforge/21.1.265/unix_args.txt nogui
else
  W=${W:-1920}; H=${H:-1920}
  mapfile -t CMD < <(python3 -c "import json;d=json.load(open('$REEL/client_cmd.json'));print('\n'.join(d['cmd']))")
  cd "$(python3 -c "import json;print(json.load(open('$REEL/client_cmd.json'))['cwd'])")"
  for i in "${!CMD[@]}"; do
    [ "${CMD[$i]}" = --width ] && CMD[$((i+1))]=$W
    [ "${CMD[$i]}" = --height ] && CMD[$((i+1))]=$H
  done
  export DISPLAY=:2 LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe MESA_GL_VERSION_OVERRIDE=4.5 MESA_GLSL_VERSION_OVERRIDE=450
  exec "${CMD[@]}"
fi
