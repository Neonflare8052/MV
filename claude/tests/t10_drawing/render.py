"""t10 · style test B, front side: the store of the Analytical Engine as an engineering drawing.
It was never built; it exists as drawings.  Same SDF geometry as t09, drawn instead of lit:
orthographic axonometric view, paper, ink outlines from depth / normal / part discontinuities,
shading lines along the cylinders (denser toward the silhouette), pale washes, centre lines.

python -X utf8 render.py [--w 1920 --h 1080 --sub 8 --out drawing_v1.png]
"""
import sys, argparse, importlib.util
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
T09 = HERE.parent / 't09_wheels'
sys.path.insert(0, str(HERE.parents[1] / 'engine'))
from gl import Renderer, save_png

_sp = importlib.util.spec_from_file_location('t09', T09 / 'render.py'); t09 = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(t09)

# the geometry: t09's scene up to its shading, trimmed to a drawable assembly (9 columns x 15 wheels, between two plates)
_G = (T09 / 'scene.glsl').read_text(encoding='utf-8')
_G = _G[:_G.index('vec3 normal(')]
for a, b in [('clamp(round(p.x / S), -4., 9.)', 'clamp(round(p.x / S), -2., 6.)'),
             ('clamp(round(q.y / P), -14., 14.)', 'clamp(round(q.y / P), -7., 7.)'),
             ('clamp(floor(p.x / S), -5., 9.)', 'clamp(floor(p.x / S), -3., 6.)'),
             ('clamp(round((p.y - (WY - H - .3)) / (3. * P)), -5., 5.)', 'clamp(round((p.y - (WY - H - .3)) / (3. * P)), -2., 2.)'),
             ('abs(p.x - 30.) - 90.', 'abs(p.x - 28.) - 46.'),
             ('float dA = length(q.xz) - .55;', 'float dA = max(length(q.xz) - .55, abs(p.y) - 22.2);'),
             ('float dP = max(abs(pp.x), abs(pp.z)) - .45;', 'float dP = max(max(abs(pp.x), abs(pp.z)) - .45, abs(p.y) - 19.5);'),
             ('  float d = dF; MAT = 1;', '  // top and bottom plates\n  vec3 pl = vec3(p.x - 28., abs(p.y) - 20.1, p.z - 1.);\n'
                                         '  float dL = max(max(abs(pl.x) - 63., abs(pl.y) - .6), abs(pl.z) - 7.5);\n  float d = dF; MAT = 1;\n  if(dL < d){ d = dL; MAT = 4; }')]:
    assert a in _G, a
    _G = _G.replace(a, b)

SRC = _G + (HERE / 'draw.glsl').read_text(encoding='utf-8')


def nrm(v): v = np.asarray(v, float); return v / np.linalg.norm(v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--w', type=int, default=1920); ap.add_argument('--h', type=int, default=1080)
    ap.add_argument('--sub', type=int, default=8); ap.add_argument('--out', default='drawing_v1.png')
    ap.add_argument('--scale', type=float, default=25., help='half the picture height, cm')
    a = ap.parse_args()
    f = nrm((1., -.55, 1.3)); r = nrm(np.cross(f, [0, 1, 0])); u = np.cross(r, f)
    t3 = lambda v: tuple(map(float, v))
    p = dict(u_c=(22., 1., 0.), u_fwd=t3(f), u_right=t3(r), u_up=t3(u), u_scale=a.scale)
    atlas = t09.digits_atlas()
    rr = Renderer(a.w, a.h, SRC, subframes=a.sub, shutter=1.)
    img = rr.frame(0., lambda ts: p, lambda t: {'u_dig': atlas}, post=dict(u_bloom=0., u_ca=0., u_grain=.012))
    save_png(img, a.w, a.h, HERE / a.out)
    print('saved', HERE / a.out)


if __name__ == '__main__':
    main()
