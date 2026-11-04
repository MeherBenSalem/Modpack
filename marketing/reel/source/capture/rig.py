"""The capture rig: drives the real client (xdotool on display :2) and the server (RCON) on the slowed clock.

Every wait is given in game seconds and multiplied by SLOW (the clock runs SLOW times slower than real time, see
game.sh). The camera is Shoulder Surfing's decoupled over-the-shoulder camera, as the pack ships it: a teleport
points it (orient_camera_on_teleport), and the mouse moves it at 0.15 degrees per pixel (sensitivity 0.5), so the
rig keeps its own estimate of the camera's yaw and pitch to aim at things.
"""
import json
import math
import os
import re
import subprocess
import threading
import time
from pathlib import Path

from rc import Rcon

SLOW = float(os.environ.get('SLOW', '30'))
REEL = Path(os.environ.get('REEL', '/home/user/reel'))
HERE = Path(__file__).resolve().parent
P = 'Ashborn'
DEG_PER_PX = 0.15
ENV = dict(os.environ, DISPLAY=':2')


def pos_of(text):
    m = re.findall(r'(-?\d+(?:\.\d+)?(?:E-?\d+)?)d', text)
    return tuple(float(v) for v in m[:3]) if len(m) >= 3 else None


class Rig:
    def __init__(self):
        self.r = Rcon(timeout=900)
        self.lock = threading.Lock()
        self.yaw = 0.0
        self.pitch = 0.0
        self.capproc = None

    # ------------------------------------------------------------- server
    def cmd(self, *cs):
        out = ''
        with self.lock:
            for c in cs:
                out = self.r.command(c)
        return out

    def me(self, c):
        return self.cmd(f'execute as {P} at {P} run {c}')

    def pos(self, sel=P):
        return pos_of(self.cmd(f'data get entity {sel} Pos'))

    def tp(self, dim, x, y, z, yaw, pitch=0.0):
        self.cmd(f'execute in {dim} run tp {P} {x:.3f} {y:.3f} {z:.3f} {yaw:.2f} {pitch:.2f}')
        self.yaw, self.pitch = yaw, pitch
        self.want_dim = dim

    # ------------------------------------------------------------- time
    @staticmethod
    def g(game_seconds):
        time.sleep(game_seconds * SLOW)

    # ------------------------------------------------------------- input
    def x(self, *args):
        subprocess.run(['xdotool', *args], env=ENV, check=False)

    def focus(self):
        out = subprocess.run(['xdotool', 'search', '--name', 'Minecraft'], env=ENV, capture_output=True,
                             text=True).stdout.split()
        if out:
            self.x('windowfocus', '--sync', out[-1])

    def key(self, k):
        self.x('key', k)

    def hold(self, k, game_seconds):
        self.x('keydown', k)
        self.g(game_seconds)
        self.x('keyup', k)

    def click(self, button=1):
        self.x('click', str(button))

    def hud_visible(self):
        """Reads the screen: is the hotbar there? (Normalised correlation with hud_template.png, the hotbar strip of
        a HUD-on frame at GUI scale 3: about 0.4 with the HUD, under 0.1 without.)"""
        import cv2
        import numpy as np
        p = REEL / 'recon' / '_hud.png'
        subprocess.run(['import', '-window', 'root', '-crop', '560x64+680+1852', str(p)], env=ENV, check=False)
        cur = cv2.cvtColor(cv2.imread(str(p)), cv2.COLOR_BGR2GRAY).astype(np.float32)
        tpl = cv2.cvtColor(cv2.imread(str(HERE / 'hud_template.png')), cv2.COLOR_BGR2GRAY).astype(np.float32)
        return float(cv2.matchTemplate(cur, tpl, cv2.TM_CCOEFF_NORMED).max()) > 0.25

    def hud(self, visible):
        """Shows or hides the HUD (F1), checking the screen rather than trusting a remembered state."""
        for _ in range(4):
            if self.hud_visible() == visible:
                return
            self.key('F1')
            time.sleep(3)
        raise RuntimeError(f'could not set the HUD to {visible}')

    def turn(self, dyaw, dpitch, game_seconds, steps=None, ease=True):
        """Turns the camera by (dyaw, dpitch) degrees, spread over game_seconds (smoothstep)."""
        steps = steps or max(8, int(game_seconds * 40))
        dx_tot, dy_tot = dyaw / DEG_PER_PX, dpitch / DEG_PER_PX
        done_x = done_y = 0
        for i in range(1, steps + 1):
            u = i / steps
            e = u * u * (3 - 2 * u) if ease else u
            tx, ty = round(dx_tot * e), round(dy_tot * e)
            if tx != done_x or ty != done_y:
                self.x('mousemove_relative', '--', str(tx - done_x), str(ty - done_y))
            done_x, done_y = tx, ty
            time.sleep(game_seconds * SLOW / steps)
        self.yaw += done_x * DEG_PER_PX
        self.pitch += done_y * DEG_PER_PX

    def aim_delta(self, target, eye=1.62, aim_h=1.2):
        """Yaw/pitch change that points the camera from the player's eyes to the target entity (selector)."""
        me, t = self.pos(), self.pos(target)
        if not me or not t:
            return None
        dx, dy, dz = t[0] - me[0], (t[1] + aim_h) - (me[1] + eye), t[2] - me[2]
        yaw = math.degrees(math.atan2(-dx, dz))
        pitch = -math.degrees(math.atan2(dy, math.hypot(dx, dz)))
        dyaw = (yaw - self.yaw + 180) % 360 - 180
        return dyaw, pitch - self.pitch

    def track(self, target, game_seconds, gain=0.6, every=0.2, max_pitch=25):
        """Keeps the camera on a moving target for game_seconds, correcting a fraction of the error each step."""
        end = time.time() + game_seconds * SLOW
        while time.time() < end:
            d = self.aim_delta(target)
            if d:
                dp = max(-max_pitch - self.pitch, min(max_pitch - self.pitch, d[1] * gain))
                self.turn(d[0] * gain, dp, every, steps=8)
            else:
                self.g(every)

    # ------------------------------------------------------------- capture
    def cap(self, name, game_seconds):
        self.capproc = subprocess.Popen([str(HERE / 'cap.sh'), name, str(game_seconds * SLOW + 2)])
        time.sleep(1.5)

    def wait_cap(self):
        if self.capproc:
            self.capproc.wait()
            self.capproc = None

    def snap(self, name, scale=30):
        p = REEL / 'recon' / f'{name}.png'
        p.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(['import', '-window', 'root', str(p)], env=ENV, check=False)
        subprocess.run(['convert', str(p), '-resize', f'{scale}%', str(p.with_name(name + '_s.jpg'))], check=False)
        return p.with_name(name + '_s.jpg')
