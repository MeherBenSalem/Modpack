"""Text for the reel, drawn with Pillow in the pack's own look (art/fonts, SIL OFL; the CurseForge banner's type):
Cinzel Decorative for the name, spaced Cinzel capitals for tags, EB Garamond italic for the Keeper's words, gold
#E8D5A3 on black (regions.js, threshold.js).

Every element is rendered once as an RGBA image and composited per frame by compose.py with its own fade and
drift. Nothing here imitates the game's interface: in-game titles, plates and boss bars in the reel are the real
ones, captured."""
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONTS = Path(__file__).resolve().parents[3] / 'art' / 'fonts'
GOLD = (232, 213, 163)
GOLD_HI = (255, 241, 196)
GOLD_LO = (190, 140, 62)
PAPER = (244, 236, 222)


@lru_cache(None)
def font(name, size, wght=None):
    f = ImageFont.truetype(str(FONTS / name), size)
    if wght is not None:
        try:
            f.set_variation_by_axes([wght])
        except Exception:
            pass
    return f


def _canvas(w, h):
    return Image.new('RGBA', (w, h), (0, 0, 0, 0))


def _shadowed(layer, radius=10, alpha=0.75, spread=2):
    """A soft dark halo under light text, so it reads over bright skies without a box."""
    a = layer.split()[3]
    sh = a.filter(ImageFilter.MaxFilter(spread * 2 + 1)).filter(ImageFilter.GaussianBlur(radius))
    sh = sh.point(lambda v: int(v * alpha))
    out = Image.new('RGBA', layer.size, (0, 0, 0, 0))
    out.putalpha(sh)
    return Image.alpha_composite(out, layer)


def spaced(draw, xy, text, f, fill, tracking):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=f, fill=fill)
        x += draw.textlength(ch, font=f) + tracking
    return x


def spaced_width(text, f, tracking):
    d = ImageDraw.Draw(_canvas(1, 1))
    return sum(d.textlength(ch, font=f) for ch in text) + tracking * (len(text) - 1)


def tag(text, size=34, tracking=7, width=None):
    """◆ SPACED CAPS in gold, with a thin rule underneath: the feature callouts."""
    f = font('Cinzel-wght.ttf', size, 600)
    tw = spaced_width(text, f, tracking)
    dia = size * 0.42
    w = int(width or tw + dia * 2 + 40)
    h = int(size * 2.1)
    im = _canvas(w, h)
    d = ImageDraw.Draw(im)
    x0 = (w - (tw + dia * 2.2)) / 2
    cy = size * 0.62
    d.polygon([(x0, cy), (x0 + dia / 2, cy - dia / 2), (x0 + dia, cy), (x0 + dia / 2, cy + dia / 2)], fill=GOLD)
    spaced(d, (x0 + dia * 2.2, 0), text, f, GOLD, tracking)
    ry = int(size * 1.55)
    for x in range(int(x0), int(x0 + tw + dia * 2.2)):
        u = (x - x0) / (tw + dia * 2.2)
        a = int(200 * min(1, 4 * u, 4 * (1 - u)))
        d.point((x, ry), fill=GOLD + (a,))
        d.point((x, ry + 1), fill=GOLD + (a // 2,))
    return _shadowed(im, radius=8, alpha=0.8)


def caption_words(words, max_w, size=58):
    """Lays out the Keeper's line (EB Garamond italic) centred in up to three lines; returns the full image and,
    per word, its bounding box, so compose.py can reveal each word as it is spoken."""
    f = font('EBGaramond-Italic-wght.ttf', size, 620)
    d = ImageDraw.Draw(_canvas(1, 1))
    space = d.textlength(' ', font=f)
    lines, cur, cur_w = [], [], 0
    for i, w in enumerate(words):
        ww = d.textlength(w, font=f)
        if cur and cur_w + space + ww > max_w:
            lines.append(cur)
            cur, cur_w = [], 0
        cur.append((i, w, ww))
        cur_w += (space if cur_w else 0) + ww
    if cur:
        lines.append(cur)
    lh = int(size * 1.22)
    pad = 30
    W = int(max_w + 2 * pad)
    H = int(lh * len(lines) + 2 * pad)
    im = _canvas(W, H)
    dd = ImageDraw.Draw(im)
    boxes = [None] * len(words)
    for li, ln in enumerate(lines):
        lw = sum(x[2] for x in ln) + space * (len(ln) - 1)
        x = (W - lw) / 2
        y = pad + li * lh
        for i, w, ww in ln:
            dd.text((x, y), w, font=f, fill=PAPER)
            boxes[i] = (int(x) - 4, int(y), int(x + ww) + 6, int(y + lh))
            x += ww + space
    return _shadowed(im, radius=12, alpha=0.85, spread=3), boxes


def gradient_text(text, f, tracking=0, top=GOLD_HI, mid=GOLD, bottom=GOLD_LO):
    w = int(spaced_width(text, f, tracking)) + 20
    asc, desc = f.getmetrics()
    h = asc + desc + 20
    mask = _canvas(w, h)
    spaced(ImageDraw.Draw(mask), (10, 6), text, f, (255, 255, 255, 255), tracking)
    a = np.array(mask.split()[3], dtype=np.float32) / 255
    ys = np.linspace(0, 1, h)[:, None]
    cols = np.where((ys < 0.5)[..., None], np.array(top) + (np.array(mid) - np.array(top)) * (ys / 0.5)[..., None],
                    np.array(mid) + (np.array(bottom) - np.array(mid)) * ((ys - 0.5) / 0.5)[..., None])
    cols = np.broadcast_to(cols, (h, w, 3))
    rgba = np.dstack([cols, a[..., None] * 255]).astype(np.uint8)
    return Image.fromarray(rgba, 'RGBA')


def title_block(width):
    """REMNANTS / ASHEN LEGACY, the name in the CurseForge banner's type, with a soft golden glow."""
    big = font('CinzelDecorative-Black.ttf', int(width * 0.155))
    sub = font('Cinzel-wght.ttf', int(width * 0.052), 600)
    t1 = gradient_text('REMNANTS', big, tracking=int(width * 0.002))
    t2 = gradient_text('ASHEN LEGACY', sub, tracking=int(width * 0.03), top=GOLD_HI, mid=GOLD, bottom=GOLD)
    W = max(t1.width, t2.width) + 120
    H = t1.height + t2.height + 80
    im = _canvas(W, H)
    im.alpha_composite(t1, ((W - t1.width) // 2, 30))
    y2 = 30 + t1.height + 4
    im.alpha_composite(t2, ((W - t2.width) // 2, y2))
    glow = im.copy().filter(ImageFilter.GaussianBlur(18))
    g = np.array(glow, dtype=np.float32)
    g[..., 3] *= 0.55
    out = Image.alpha_composite(Image.fromarray(g.astype(np.uint8), 'RGBA'), im)
    return _shadowed(out, radius=16, alpha=0.7)


def to_np(im):
    """Premultiplied float32 RGB (BGR order for OpenCV frames) and alpha."""
    a = np.array(im, dtype=np.float32) / 255.0
    rgb = a[..., :3][..., ::-1] * a[..., 3:4]
    return np.ascontiguousarray(rgb), np.ascontiguousarray(a[..., 3:4])
