"""t09 · look test: figure wheels of the Analytical Engine's store (front side of the s14 machine).
Only a close fragment: columns of bronze figure wheels on steel axles, engraved digits on the rims,
a warm grazing light, shallow depth of field.  No model: SDF with domain repetition.

python -X utf8 render.py [--w 1920 --h 1080 --sub 64 --out wheels_v1.png]
"""
import sys, math, argparse
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'engine'))
from gl import Renderer, save_png

SRC = (HERE / 'scene.glsl').read_text(encoding='utf-8')


def digits_atlas():
    """0-9 side by side; each cell has the rim's aspect (1/10 of the circumference x the rim height)."""
    cw, ch = 350, 100
    img = Image.new('RGBA', (cw * 10, ch), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)
    fonts = ['C:/Windows/Fonts/BOD_R.TTF', 'C:/Windows/Fonts/BOD_B.TTF', 'C:/Windows/Fonts/times.ttf']
    font = next(ImageFont.truetype(f, 74) for f in fonts if Path(f).exists())
    for k in range(10):
        s = str(k)
        x0, y0, x1, y1 = d.textbbox((0, 0), s, font=font)
        d.text((k * cw + (cw - (x1 - x0)) / 2 - x0, (ch - (y1 - y0)) / 2 - y0), s, font=font, fill=(255, 255, 255, 255))
    return img


def nrm(v): v = np.asarray(v, float); return v / np.linalg.norm(v)


def camera(ro, target, focus):
    f = nrm(np.subtract(target, ro)); r = nrm(np.cross(f, [0, 1, 0])); u = np.cross(r, f)
    fd = float(np.dot(np.subtract(focus, ro), f))
    t3 = lambda v: tuple(map(float, v))
    return dict(u_ro=t3(ro), u_fwd=t3(f), u_right=t3(r), u_up=t3(u), u_focus=fd)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--w', type=int, default=1920); ap.add_argument('--h', type=int, default=1080)
    ap.add_argument('--sub', type=int, default=64); ap.add_argument('--out', default='wheels_v1.png')
    ap.add_argument('--ap', type=float, default=.3, help='aperture radius (cm)')
    a = ap.parse_args()
    cam = camera(ro=(-19., 7.5, -24.), target=(12., -1.5, 2.), focus=(-2.4, 1.2, -4.4))
    atlas = digits_atlas()
    r = Renderer(a.w, a.h, SRC, subframes=a.sub, shutter=1.)
    p = dict(cam, u_tanh=.24, u_ap=a.ap)
    img = r.frame(0., lambda ts: p, lambda t: {'u_dig': atlas}, post=dict(u_bloom=.22, u_ca=.004, u_grain=.025))
    save_png(img, a.w, a.h, HERE / a.out)
    print('saved', HERE / a.out)


if __name__ == '__main__':
    main()
