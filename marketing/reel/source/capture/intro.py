#!/usr/bin/env python3
"""Records the real first-join opening tale (beta 9): the Keeper's intro over a black screen with its title cards.

The Ashborn must be a brand-new player for threshold.js to run it, so this closes the client, deletes the player's
save, stats and advancements on the server (offline UUID of 'Ashborn'), restarts the server, relaunches the client (game.sh, slowed
clock), waits on Runeborn's origin screen until the join toasts have gone, presses RISE (Knight-Errant), and
records the intro as it plays: $REEL/raw/intro.mkv.
"""
import hashlib
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
REEL = Path(os.environ.get('REEL', '/home/user/reel'))
sys.path.insert(0, str(HERE.parents[3] / 'tools'))
import test_client  # noqa: E402

sys.path.insert(0, str(HERE))
from rig import Rig  # noqa: E402


def offline_uuid(name):
    h = bytearray(hashlib.md5(f'OfflinePlayer:{name}'.encode()).digest())
    h[6] = h[6] & 0x0F | 0x30
    h[8] = h[8] & 0x3F | 0x80
    return str(uuid.UUID(bytes=bytes(h)))


def main():
    u = offline_uuid('Ashborn')
    test_client.close_game_window(':2')
    for _ in range(90):
        if subprocess.run(['pgrep', '-f', 'Djava.library.path=.*run/client'], capture_output=True).returncode:
            break
        time.sleep(2)
    time.sleep(20)                                  # the server saves the player on disconnect
    # stop the server too: it keeps every player's stats cached after they log out, and threshold.js skips the
    # Threshold for anyone with more than five minutes of play time
    from rc import Rcon
    try:
        Rcon().command('stop')
    except OSError:
        pass                                        # already down
    while not subprocess.run(['pgrep', '-f', 'unix_args.txt nogui'], capture_output=True).returncode:
        time.sleep(3)
    world = REEL / 'server' / 'world'
    for p in (world / 'playerdata' / f'{u}.dat', world / 'playerdata' / f'{u}.dat_old',
              world / 'stats' / f'{u}.json', world / 'advancements' / f'{u}.json'):
        if p.exists():
            p.unlink()
            print('removed', p.relative_to(REEL))
    slog = REEL / 'server_slow.log'
    slog.write_text('')                             # start from an empty log: no stale 'Done' or 'joined'
    subprocess.Popen(f'nohup {HERE}/game.sh server 0.0333 > {slog} 2>&1 &', shell=True)
    time.sleep(10)
    while 'Done (' not in slog.read_text(errors='replace'):
        time.sleep(5)
    join_and_record()


def join_and_record():
    slog = REEL / 'server_slow.log'
    log = REEL / 'client_slow.log'
    subprocess.Popen(f'nohup {HERE}/game.sh client 0.0333 > {log} 2>&1 &', shell=True)
    joined = REEL / 'server_slow.log'
    while 'Ashborn joined the game' not in joined.read_text(errors='replace'):
        time.sleep(10)
    # Record from the moment of joining: if Runeborn already knows this Ashborn's origin, there is no origin
    # screen and the tale starts at once. Otherwise wait out the join toasts on the origin screen and press RISE.
    r = Rig()
    r.cap('intro', 60.0)
    print('joined; recording', flush=True)
    time.sleep(480)
    r.focus()
    r.snap('origin_screen', 25)
    st = r.cmd('data get entity Ashborn KubeJSPersistentData.remnants_threshold')
    print('threshold state:', st, flush=True)
    if 'pending' in st:
        r.x('mousemove', '1507', '1237')           # RISE (Knight-Errant is preselected)
        time.sleep(1)
        r.click(1)
        print('pressed RISE', flush=True)
    r.wait_cap()
    print('intro captured')


if __name__ == '__main__':
    join_and_record() if '--join' in sys.argv else main()
