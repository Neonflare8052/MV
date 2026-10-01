"""t11 · the assembled machine on the drawing sheet (still: the moment it is complete).
The parts of the Analytical Engine, put together, make a card sorter.  The margins are full of the Engine as it was meant.

python -X utf8 render.py [--w 1920 --h 1080 --sub 8 --out assembly_v1.png] [--bare]
"""
import sys, argparse
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'engine'))
from gl import Renderer, save_png
sys.path.insert(0, str(HERE))
import drafting

SRC = (HERE / 'scene.glsl').read_text(encoding='utf-8')
COUNT = '041377'


def nrm(v): v = np.asarray(v, float); return v / np.linalg.norm(v)


class Cam:
    """Orthographic camera shared by the shader and the sheet (so dimension lines land on the machine)."""
    def __init__(self, w, h, c=(-2., 7., 0.), scale=62.):
        self.w, self.h, self.c, self.scale = w, h, np.asarray(c, float), scale
        self.f = nrm((1., -.55, 1.3)); self.r = nrm(np.cross(self.f, [0, 1, 0])); self.u = np.cross(self.r, self.f)

    def px(self, P):
        d = np.asarray(P, float) - self.c
        x, y = d @ self.r / (2 * self.scale), d @ self.u / (2 * self.scale)
        return (self.w / 2 + x * self.h, self.h / 2 - y * self.h)

    def uniforms(self):
        t3 = lambda v: tuple(map(float, v))
        return dict(u_c=t3(self.c), u_fwd=t3(self.f), u_right=t3(self.r), u_up=t3(self.u), u_scale=float(self.scale))


def odo_atlas():
    """Digits stacked down a strip: the rim of a counter wheel, read across its width."""
    cw, ch = 120, 150
    img = Image.new('RGBA', (cw, ch * 10), (0, 0, 0, 255)); d = ImageDraw.Draw(img)
    font = ImageFont.truetype('C:/Windows/Fonts/BOD_R.TTF', 118)
    for k in range(10):
        x0, y0, x1, y1 = d.textbbox((0, 0), str(k), font=font)
        d.text(((cw - (x1 - x0)) / 2 - x0, k * ch + (ch - (y1 - y0)) / 2 - y0), str(k), font=font, fill=(255, 255, 255, 255))
    return img


def col_atlas():
    """0-9 side by side for the store wheels' rims (cell = a tenth of the circumference x the rim height)."""
    cw, ch = 143, 120
    img = Image.new('RGBA', (cw * 10, ch), (0, 0, 0, 255)); d = ImageDraw.Draw(img)
    font = ImageFont.truetype('C:/Windows/Fonts/BOD_R.TTF', 96)
    for k in range(10):
        x0, y0, x1, y1 = d.textbbox((0, 0), str(k), font=font)
        d.text((k * cw + (cw - (x1 - x0)) / 2 - x0, (ch - (y1 - y0)) / 2 - y0), str(k), font=font, fill=(255, 255, 255, 255))
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--w', type=int, default=1920); ap.add_argument('--h', type=int, default=1080)
    ap.add_argument('--sub', type=int, default=8); ap.add_argument('--out', default='assembly_v1.png')
    ap.add_argument('--bare', action='store_true', help='no sheet overlay')
    a = ap.parse_args()
    cam = Cam(a.w, a.h)
    ui = Image.new('RGBA', (a.w, a.h), (0, 0, 0, 0)) if a.bare else drafting.draw(cam, a.w, a.h, executed=True)
    p = dict(cam.uniforms(), u_exec=1., u_cnt=tuple(float(c) for c in COUNT))
    ODO, COL = odo_atlas(), col_atlas()
    r = Renderer(a.w, a.h, SRC, subframes=a.sub, shutter=1.)
    img = r.frame(0., lambda ts: p, lambda t: {'u_odo': ODO, 'u_col': COL, 'u_ui': ui}, post=dict(u_bloom=0., u_ca=0., u_grain=.012))
    save_png(img, a.w, a.h, HERE / a.out)
    print('saved', HERE / a.out)


if __name__ == '__main__':
    main()
