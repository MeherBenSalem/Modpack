#!/usr/bin/env python3
"""Renders both cuts of the reel (picture only) from $REEL/edit/edl.json:

  $REEL/edit/base_v.mp4   1080x1920, 60 fps (Shorts, Reels, TikTok)
  $REEL/edit/base_h.mp4   1920x1080, 60 fps (the 16:9 cut, re-framed from the same renders, not letterboxed)

The footage was captured at 1920x1920 with the game's clock slowed 30x, so about 119 real renders exist for every
second of game time. Each output frame asks its shot for a game time (never advancing slower than real time), and
averages the renders that fall inside half a frame interval around it (a 180 degree shutter), cross-fading
between the two nearest renders when the window holds none. No frame is repeated and none is invented. The
vertical and horizontal cuts are crops of the same graded square: a portrait window that may slide sideways, a
landscape window that may slide up and down, so camera moves cost no resolution.

  compose.py                 # both cuts, whole reel
  compose.py 20 31           # only reel seconds 20-31 (for checks): base_v_part.mp4, base_h_part.mp4
"""
import bisect
import json
import math
import os
import subprocess
import sys

import cv2
import numpy as np

import overlay as ov

REEL = os.environ.get('REEL', '/home/user/reel')
E = f'{REEL}/edit'
EDL = json.load(open(f'{E}/edl.json'))
FPS = EDL['fps']
DUR = EDL['duration']
NF = int(round(DUR * FPS))
SQ = 1920
SHUTTER = 0.5
VW, VH = 1080, 1920
HW, HH = 1920, 1080


def smooth(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


class Source:
    """The unique renders of one capture, decoded sequentially (with a small cache around the read head)."""

    def __init__(self, name):
        j = json.load(open(f'{REEL}/idx/{name}.json'))
        self.name, self.idx, self.t = name, j['idx'], j['t']
        self.k_of = {c: k for k, c in enumerate(self.idx)}
        self.cap, self.pos, self.cache = None, 0, {}

    def frame(self, k):
        k = max(0, min(len(self.idx) - 1, k))
        if k in self.cache:
            return self.cache[k]
        want = self.idx[k]
        if self.cap is None or want < self.pos:
            self.cap = cv2.VideoCapture(f'{REEL}/raw/{self.name}.mkv')
            self.pos = 0
        while self.pos <= want:
            if self.k_of.get(self.pos, -99) >= k - 2:
                ok, f = self.cap.read()
                if not ok:
                    raise RuntimeError(f'{self.name}: ran out of frames at {self.pos}')
                self.cache[self.k_of[self.pos]] = f.astype(np.float32)
            else:
                if not self.cap.grab():
                    raise RuntimeError(f'{self.name}: ran out of frames at {self.pos}')
            self.pos += 1
        for kk in [x for x in self.cache if x < k - 2 or x > k + 6]:
            del self.cache[kk]
        return self.cache[k]

    def at(self, g):
        """The picture at game time g: cross-fade between the renders on either side."""
        t = self.t
        if g <= t[0]:
            return self.frame(0)
        i = bisect.bisect_right(t, g) - 1
        if i >= len(t) - 1:
            return self.frame(len(t) - 1)
        w = (g - t[i]) / (t[i + 1] - t[i])
        if w < 0.02:
            return self.frame(i)
        if w > 0.98:
            return self.frame(i + 1)
        return self.frame(i) * (1 - w) + self.frame(i + 1) * w

    def exposure(self, g, span):
        """Averages the scene over [g - span/2, g + span/2] (a 180 degree shutter at the shot's speed)."""
        n = max(1, int(math.ceil(span / 0.0042)))
        if n == 1:
            return self.at(g)
        acc = None
        for k in range(n):
            s = self.at(g + span * ((k + 0.5) / n - 0.5))
            acc = s.copy() if acc is None else acc + s
        return acc / n


def game_time(shot, local):
    """Game time for a local shot time from the shot's map: [[local, game], ...], piecewise linear. plan.py
    guarantees every segment's slope is at least 1 (never slower than real time)."""
    keys = shot['map']
    if local <= keys[0][0]:
        return keys[0][1] + (local - keys[0][0])
    for a, b in zip(keys, keys[1:]):
        if a[0] <= local <= b[0]:
            u = (local - a[0]) / (b[0] - a[0])
            return a[1] + (b[1] - a[1]) * u
    return keys[-1][1] + (local - keys[-1][0])


def keyed(keys, local, default):
    """A value animated by [[local, value], ...] keys (smoothstep between keys)."""
    if not keys:
        return default
    if local <= keys[0][0]:
        return keys[0][1]
    for a, b in zip(keys, keys[1:]):
        if a[0] <= local <= b[0]:
            return a[1] + (b[1] - a[1]) * smooth((local - a[0]) / (b[0] - a[0]))
    return keys[-1][1]


def grade(img, g):
    """A restrained film grade on the square: a touch of contrast, deeper blacks, warm highlights, cooler shadows,
    and a soft vignette. Values come from the shot (EDL) so night and dusk shots can differ."""
    c = g.get('contrast', 1.06)
    sat = g.get('sat', 1.06)
    lift = g.get('lift', -4.0)
    f = (img - 128.0) * c + 128.0 + lift
    grey = f.mean(axis=2, keepdims=True)
    f = grey + (f - grey) * sat
    warm = g.get('warm', 0.035)
    lum = np.clip(grey / 255.0, 0, 1)
    f[..., 2] *= 1 + warm * lum[..., 0]          # R up in highlights
    f[..., 0] *= 1 + warm * 0.6 * (1 - lum[..., 0])  # B up in shadows
    if g.get('exposure'):
        f *= g['exposure']
    return f


VIG = None


def vignette(f, strength):
    global VIG
    if VIG is None:
        y, x = np.mgrid[0:SQ, 0:SQ].astype(np.float32)
        r = np.hypot((x - SQ / 2) / (SQ / 2), (y - SQ / 2) / (SQ / 2))
        VIG = np.clip(1 - 0.5 * np.clip(r - 0.55, 0, None) ** 1.6, 0, 1)[..., None]
    return f * (1 - strength + strength * VIG)


# ---------------------------------------------------------------------------- overlays
class Overlays:
    def __init__(self, items):
        self.items = items
        self.cache = {}

    def layer(self, it, view):
        key = (id(it), view)
        if key in self.cache:
            return self.cache[key]
        w = VW if view == 'v' else HW
        if it['type'] == 'caption':
            im, boxes = ov.caption_words([x['w'] for x in it['words']], max_w=(940 if view == 'v' else 1300),
                                         size=(66 if view == 'v' else 62))
            res = (ov.to_np(im), boxes)
        elif it['type'] == 'tag':
            res = (ov.to_np(ov.tag(it['text'], size=(34 if view == 'v' else 30))), None)
        elif it['type'] == 'scrim':   # a soft top-down darkening behind the title (alpha a0 at the top -> 0 at depth)
            H_, W_ = (VH, VW) if view == 'v' else (HH, HW)
            depth = it['depth'][view]
            y = np.linspace(0, 1, H_, dtype=np.float32)[:, None, None]
            a = it['a0'] * np.clip(1 - y / depth, 0, 1) ** 1.6
            a = np.broadcast_to(a, (H_, W_, 1)).copy()
            res = ((np.zeros((H_, W_, 3), np.float32), a), 'full')
            self.cache[key] = res
            return res
        elif it['type'] == 'title':
            res = (ov.to_np(ov.title_block(980 if view == 'v' else 1100)), None)
        else:
            raise ValueError(it['type'])
        self.cache[key] = res
        return res

    def apply(self, img, t, view):
        H, W = img.shape[:2]
        for it in self.items:
            if not (it['start'] - 0.01 <= t <= it['end'] + 0.01):
                continue
            (rgb, a), boxes = self.layer(it, view)
            if boxes == 'full':
                fi, fo = it.get('fade_in', 0.25), it.get('fade_out', 0.3)
                k = min(smooth((t - it['start']) / fi) if fi else 1, smooth((it['end'] - t) / fo) if fo else 1)
                img *= 1 - a * k
                continue
            fi, fo = it.get('fade_in', 0.25), it.get('fade_out', 0.3)
            alpha = min(smooth((t - it['start']) / fi) if fi else 1, smooth((it['end'] - t) / fo) if fo else 1)
            if alpha <= 0:
                continue
            pos = it['pos'][view]
            drift = it.get('drift', 0) * (t - it['start'])
            cx, cy = pos[0] * W, pos[1] * H - drift
            h, w = a.shape[:2]
            x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
            aa = a * alpha
            if boxes is not None:   # reveal the Keeper's words as he speaks them
                mask = np.zeros_like(aa)
                for word, box in zip(it['words'], boxes):
                    u = smooth((t - it['start'] - word['s'] + 0.05) / 0.16)
                    if u > 0:     # the word's box, padded so its soft shadow comes with it
                        bx0, by0, bx1, by1 = box
                        sl = np.s_[max(0, by0 - 10):by1 + 10, max(0, bx0 - 10):bx1 + 10]
                        mask[sl] = np.maximum(mask[sl], u)
                aa = aa * mask
                rr = rgb * (aa / np.maximum(a, 1e-6))
            else:
                rr = rgb * alpha
            sx0, sy0 = max(0, -x0), max(0, -y0)
            sx1, sy1 = min(w, W - x0), min(h, H - y0)
            if sx1 <= sx0 or sy1 <= sy0:
                continue
            reg = img[y0 + sy0:y0 + sy1, x0 + sx0:x0 + sx1]
            reg *= 1 - aa[sy0:sy1, sx0:sx1]
            reg += rr[sy0:sy1, sx0:sx1] * 255.0
        return img


def ffmpeg_out(path, w, h):
    return subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24',
                             '-s', f'{w}x{h}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'slow',
                             '-crf', '13', '-pix_fmt', 'yuv420p', '-color_primaries', 'bt709', '-color_trc', 'bt709',
                             '-colorspace', 'bt709', path], stdin=subprocess.PIPE)


def main():
    part = (float(sys.argv[1]), float(sys.argv[2])) if len(sys.argv) > 2 else None
    suffix = '_part' if part else ''
    outs = {'v': ffmpeg_out(f'{E}/base_v{suffix}.mp4', VW, VH), 'h': ffmpeg_out(f'{E}/base_h{suffix}.mp4', HW, HH)}
    sources = {}
    ovl = Overlays(EDL['overlays'])
    shots = EDL['shots']
    black = np.zeros((SQ, SQ, 3), np.float32)
    for fno in range(NF):
        t = fno / FPS
        if part and not (part[0] <= t < part[1]):
            continue
        shot = next((s for s in shots if s['start'] <= t < s['end']), shots[-1])
        local = t - shot['start']
        if shot.get('src'):
            src = sources.setdefault(shot['src'], Source(shot['src']))
            g = game_time(shot, local)
            speed = (game_time(shot, local + 0.01) - game_time(shot, local - 0.01)) / 0.02
            img = src.exposure(g, SHUTTER * speed / FPS)
            img = grade(img, shot.get('grade', {}))
            img = vignette(img, shot.get('vignette', 0.35))
        else:
            img = black.copy()
        # fades to and from black
        k = 1.0
        if shot.get('fade_in'):
            k = min(k, smooth(local / shot['fade_in']))
        if shot.get('fade_out'):
            k = min(k, smooth((shot['end'] - t) / shot['fade_out']))
        if k < 1:
            img = img * k
        # a short lift of exposure on hits (fx: [[time, strength, duration]])
        for at, st, du in shot.get('flash', []):
            if at <= t < at + du:
                img = img * (1 + st * (1 - (t - at) / du) ** 2)
        # framing: the portrait window's centre x and the landscape window's centre y, animated; optional
        # push-in (zoom >= 1) and a decaying shake on impacts
        zoom0 = keyed(shot.get('zoom'), local, 1.0)
        shake_zoom = 1.0
        dx = dy = 0.0
        for at, amp, du in shot.get('shake', []):
            if at <= t < at + du:
                q = (1 - (t - at) / du) ** 2
                dx += amp * q * math.sin(t * 97.0)
                dy += amp * q * math.cos(t * 83.0)
                shake_zoom = max(shake_zoom, 1 + abs(amp) / 900)
        # a light, per-frame film grain (luminance only), so even held black and title frames are distinct frames
        rng = np.random.default_rng(fno)
        grain = cv2.resize(rng.normal(0, EDL.get('grain', 2.2), (SQ // 2, SQ // 2)).astype(np.float32), (SQ, SQ),
                           interpolation=cv2.INTER_LINEAR)
        img = img + grain[..., None]
        views = {}
        for view, (w, h) in (('v', (VW, VH)), ('h', (HW, HH))):
            zoom = max(keyed(shot.get(f'zoom_{view}'), local, zoom0), shake_zoom)
            if view == 'v':
                cx = keyed(shot.get('vx'), local, SQ / 2) + dx
                cy = keyed(shot.get('vy'), local, SQ / 2) + dy
            else:
                cx = SQ / 2 + dx
                cy = keyed(shot.get('hy'), local, SQ / 2) + dy
            sw, sh = w / zoom, h / zoom
            cx = min(max(cx, sw / 2), SQ - sw / 2)
            cy = min(max(cy, sh / 2), SQ - sh / 2)
            if zoom > 1.0005 or abs(cx - round(cx)) > 1e-3 or abs(cy - round(cy)) > 1e-3:
                m = np.array([[zoom, 0, w / 2 - zoom * cx], [0, zoom, h / 2 - zoom * cy]], np.float32)
                crop = cv2.warpAffine(img, m, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            else:
                x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
                crop = img[y0:y0 + h, x0:x0 + w].copy()
            crop = ovl.apply(crop, t, view)
            views[view] = crop
        for view in ('v', 'h'):
            out = np.clip(views[view], 0, 255).astype(np.uint8)
            outs[view].stdin.write(out.tobytes())
        if fno % 120 == 0:
            print(f'{t:6.2f} s  {shot["name"]}', flush=True)
    for p in outs.values():
        p.stdin.close()
        p.wait()


if __name__ == '__main__':
    main()
