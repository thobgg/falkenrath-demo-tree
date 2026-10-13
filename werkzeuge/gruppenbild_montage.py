#!/usr/bin/env python3
"""Gruppenbild der Hochzeit 1924 (media/hochzeit-1924.jpg) aus den Einzelporträts montieren (Stand 2026-10-10).

Braucht rembg (pip install "rembg[cpu]" pillow numpy, am besten in einer venv; lädt beim ersten Lauf
das Modell u2net_human_seg, ~170 MB). I43 sieht mit isnet-general-use besser aus.

    python gruppenbild_montage.py freistellen <ausgabeordner> [modell]
    python gruppenbild_montage.py montieren   <ausgabeordner> <ziel.jpg>

`montieren` schreibt neben das Bild eine JSON mit geschätzten Gesichtsrahmen (x, y, w, h in Pixeln) je Person.
Ausgelassen: I272 (gleiches Foto wie I44), I65/I66/I68 (1924 in Milwaukee).
Dazu zwei Gäste ohne Datensatz im Baum (Testfälle, Bilder in werkzeuge/gruppenbild/):
  niebuhr   – Wilhelm Niebuhr, Trauzeuge (im Baum nur als `2 _WITN` an F8): bekannt, aber nicht im Stammbaum
  unbekannt – ein unbekannter Gast
"""
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAESTE = {'niebuhr': ('Wilhelm Niebuhr', 'bekannt'), 'unbekannt': (None, 'unbekannt')}


def source(i):
    if i in GAESTE:
        return f'{BASE}/werkzeuge/gruppenbild/gast-{i}.jpg'
    return f'{BASE}/media/portrait-i{i}.jpg'


if sys.argv[1] == 'freistellen':
    from rembg import remove, new_session
    from PIL import Image
    ids = '22,21,42,39,40,43,79,80,29,28,274,72,273,271,305,63,44,300,105,104,45,niebuhr,unbekannt'.split(',')
    sess = new_session(sys.argv[3] if len(sys.argv) > 3 else 'u2net_human_seg')
    for i in ids:
        im = Image.open(source(i)).convert('RGB')
        remove(im, session=sess, post_process_mask=True).save(f'{sys.argv[2]}/i{i}.png')
    sys.exit()
sys.argv = [sys.argv[0], sys.argv[2], sys.argv[3]]
import json, random
from PIL import Image, ImageDraw, ImageFilter, ImageOps
import numpy as np
S = sys.argv[1]; OUT = sys.argv[2]
random.seed(7); np.random.seed(7)
W, H = 2400, 1210

def load(i):
    im = Image.open(f'{S}/i{i}.png').convert('RGBA')
    i = int(i) if i.isdigit() else i
    a = np.array(im.getchannel('A'))
    if i == 42:  # helles Haar vor hellem Grund: Kopf-Ellipse ergänzen
        m = Image.new('L', im.size, 0)
        ImageDraw.Draw(m).ellipse((192, 112, 398, 400), fill=255)
        m = m.filter(ImageFilter.GaussianBlur(6))
        a = np.maximum(a, np.array(m))
    if i == 28:
        a[:90, 420:] = 0
    a = (a > 110).astype(np.uint8) * 255
    am = Image.fromarray(a).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(9))
    am = am.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.6))
    g = ImageOps.grayscale(Image.open(source(str(i))).convert('RGB'))
    ga = np.array(g).astype(float); mk = np.array(am) > 128
    lo, hi = np.percentile(ga[mk], [1.5, 98.5])
    ga = np.clip((ga - lo) / max(hi - lo, 1), 0, 1) ** 1.05 * 225 + 18
    g = Image.fromarray(ga.astype(np.uint8))
    return extend(g, am, CUT.get(i, 1.0))

CUT = {'unbekannt': .76, 43: .80, 29: .78, 273: .84, 72: .84, 63: .9, 44: .9, 39: .80, 40: .74, 105: .66, 45: .80, 305: .9, 300: .92, 22: .95}
EXT = 520

def extend(g, am, cut):
    # Oberkörper nach unten verlängern: unterste saubere Zeilen fortsetzen, zu dunkler Kleidung abdunkeln
    ga = np.array(g).astype(float); aa = np.array(am).astype(float)
    hh = int(g.height * cut); ga, aa = ga[:hh], aa[:hh]
    band = slice(hh - 22, hh - 4)
    col = np.median(ga[band], axis=0)
    col = np.array(Image.fromarray(np.tile(col, (3, 1)).astype(np.uint8)).filter(ImageFilter.GaussianBlur(25)))[1].astype(float)
    body = aa[band].max(axis=0) > 128
    dark = np.percentile(ga[:hh][aa > 200][-20000:], 30) if (aa > 200).any() else 60
    dark = min(dark, 70)
    col = np.minimum(col, dark + 45)
    newg = np.zeros((EXT, g.width)); newa = np.zeros((EXT, g.width))
    xs = np.where(body)[0]
    for r in range(EXT):
        t = min(r / 28, 1)
        widen = int(r * .18)
        lo, hi = max(xs.min() - widen, 0), min(xs.max() + widen, g.width - 1) if len(xs) else (0, -1)
        m = np.zeros(g.width, bool); m[body] = True; m[lo:hi + 1] |= True
        newa[r] = m * 255
        newg[r] = col * (1 - t) + dark * t
    newg = np.array(Image.fromarray(newg.astype(np.uint8)).filter(ImageFilter.GaussianBlur(3))).astype(float)
    newg += np.random.normal(0, 4, newg.shape)
    G = np.vstack([ga, newg]); A = np.vstack([aa, newa])
    ramp = np.clip(np.arange(g.width) / 60, 0, 1); ramp = np.minimum(ramp, ramp[::-1])
    A = A * ramp[None, :]
    # Körper zur Mitte hin etwas heller, zu den Seiten dunkler (Volumen)
    shade = 1 - .25 * (np.linspace(-1, 1, g.width) ** 2)
    G[hh:] = G[hh:] * shade[None, :]
    Am = Image.fromarray(A.astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.6))
    Gi = Image.fromarray(np.clip(G, 0, 255).astype(np.uint8))
    return Image.merge('RGBA', (Gi, Gi, Gi, Am))

# (id, Reihe, Skalenkorrektur) – Reihenfolge links→rechts
ROWS = {
  'hinten': ['unbekannt', '79', '80', '28', '29', '72', '274', '105'],
  'mitte':  ['305', '63', '45', '44', 'niebuhr', '273', '271', '104'],
  'vorn':   ['300', '39', '40', '21', '22', '42', '43'],
}
SCALE = {'niebuhr': .86, 'unbekannt': 1.04, '21': .86, '28': .84, '22': 1.0, '80': .98, '42': .95, '271': .92, '79': 1.0, '29': .95, '305': .95}
ROWCFG = {'hinten': (0.84, 230), 'mitte': (0.90, 480), 'vorn': (0.98, 770)}  # Basisskala, Kopf-Oberkante y
SLOT = {7: 318, 8: 290}

def backdrop():
    y = np.linspace(0, 1, H)[:, None]; x = np.linspace(-1, 1, W)[None, :]
    base = 150 - 40 * y + 25 * np.exp(-((x + .2) ** 2) / .5 - ((y - .35) ** 2) / .2)
    n = np.random.rand(H // 40, W // 40)
    n = np.array(Image.fromarray((n * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(30))) / 255.
    base = base + (n - .5) * 40
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert('RGBA')

canvas = backdrop()
boxes = []
for row in ['hinten', 'mitte', 'vorn']:
    base, ytop = ROWCFG[row]
    ids = ROWS[row]
    slot = SLOT[len(ids)]
    off = (W - slot * (len(ids) - 1)) / 2
    for k, i in enumerate(ids):
        im = load(i)
        s = base * SCALE.get(i, 0.93)
        im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
        a = np.array(im.getchannel('A')) > 128
        rows_ = np.where(a.any(1))[0]; y0 = rows_[0]
        top = a[y0:y0 + int(.3 * im.height)]
        cx = int(np.nonzero(top)[1].mean())
        jitter = random.randint(-14, 14)
        X = int(off + k * slot - cx + random.randint(-12, 12)); Y = int(ytop - y0 + jitter)
        sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); sh.putalpha(im.getchannel('A').point(lambda v: v * .45))
        sh = sh.filter(ImageFilter.GaussianBlur(14))
        canvas.alpha_composite(sh, (X + 10, Y + 8))
        canvas.alpha_composite(im, (X, Y))
        hw = int(.34 * 480 * s)
        name, art = GAESTE.get(i, (None, 'baum'))
        boxes.append({'id': f'I{i}' if art == 'baum' else None, 'name': name, 'art': art, 'reihe': row, 'x': X + cx - hw // 2, 'y': Y + y0, 'w': hw, 'h': int(.40 * 600 * s)})

img = canvas.convert('L')
# Gesamt-Look: leichte Unschärfe, Korn, Vignette, Sepia
img = img.filter(ImageFilter.GaussianBlur(.9))
arr = np.array(img).astype(float)
arr += np.random.normal(0, 7, arr.shape)
yy, xx = np.mgrid[0:H, 0:W]
v = 1 - .38 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) ** 1.4
arr = np.clip(arr * v, 0, 255)
g = Image.fromarray(arr.astype(np.uint8))
sep = ImageOps.colorize(g, black=(38, 26, 16), mid=(150, 118, 84), white=(240, 226, 198))
# Karton
M = 110
card = Image.new('RGB', (W + 2 * M, H + 2 * M), (226, 214, 190))
card.paste(sep, (M, M))
d = ImageDraw.Draw(card); d.rectangle((M - 2, M - 2, M + W + 1, M + H + 1), outline=(120, 100, 75), width=2)
card = card.resize((card.width // 2, card.height // 2), Image.LANCZOS)
card.save(OUT, quality=88)
for b in boxes:
    for k in 'xywh': b[k] = int(b[k] + (M if k in 'xy' else 0)) // 2
json.dump(boxes, open(OUT.replace('.jpg', '.json'), 'w'), indent=1)
print(card.size)
