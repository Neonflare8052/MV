"""t06 · teletype (2:24.8–2:42.2)."""
import sys, math, argparse, time
from pathlib import Path
from PIL import Image
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'engine'))
from gl import Renderer, encode, save_png

START, END = 144.8, 162.2
BANG = 145.5
EX = [147.660, 148.600, 149.520, 150.540, 151.520, 152.280, 153.160, 153.980, 155.200, 156.080, 157.040, 158.000]
COUNTS = [158.900, 159.321, 159.657, 160.244, 160.693, 161.124]
CUT = 161.584
LH, CWD, X0 = .001136, .000833, -.1              # eye field: 240 x 100 characters; EXECUTION lines at 3x pitch
YP, ZP, YB = .255, .0158, .5805
GLYPHS = Image.open(HERE / 'glyphs.png')
INSC = Image.open(HERE.parent / 't04_printer' / 'atlas.png')


def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def outc(x): x = clamp(x); return 1 - (1 - x) ** 3
def lerp(a, b, x): return tuple(p + (q - p) * x for p, q in zip(a, b))


def remap(t):
    if CUT + .05 < t < CUT + .19: return CUT + .05
    if CUT + .19 <= t < CUT + .33:
        k = int((t - CUT - .19) * 60); return CUT + .19 + (k // 3) * 3 / 60 * 1.6
    return t


def params(t):
    t = remap(t)
    # iris: looking around, then staring straight out from BANG
    if t < BANG:
        ph = t * 1.7
        iris = (.12 * math.sin(ph * 2.3) * (1 if int(ph * 3) % 2 else -1), .05 * math.sin(ph * 3.1))
        gapA = math.radians(-90 + 60 * math.sin(t * 2.))
    else:
        iris, gapA = (0., 0.), math.radians(-90.)
    # paper feed (in eye rows): eye finished at row 99; EXECUTION line i sits at rows 104+6i .. 107+6i
    F = 99 * LH
    typed = [0.] * 12
    head, strike = X0, 0.
    for i, ti in enumerate(EX):
        if t >= ti:
            prev = 99. if i == 0 else 105.5 + 6 * (i - 1)
            F = (prev + (105.5 + 6 * i - prev) * outc((t - ti) / .06)) * LH
            k = clamp((t - ti - .06) / .15) * 9
            typed[i] = k
            if k < 9:
                head = X0 + (2 + 3 * i + k) * CWD * 3
                strike = 1. - (k % 1)
    F += sum(.077 * outc((t - c) / .18) for c in COUNTS)       # each count feeds the paper towards the blade
    yb = YB + .02 * sum(1 for c in COUNTS if t >= c + .04) - .02 * sum(1 - outc((t - c - .04) / .05) for c in COUNTS if c + .04 <= t < c + .09)
    if t >= CUT: yb = YB + .12 - .12 * outc((t - CUT) / .045)
    p = dict(u_scene=0. if t < EX[0] else 1., u_bang=1. if t >= BANG else 0., u_iris=iris, u_gapA=gapA,
             u_F=F, u_typed=typed, u_headX=head, u_strike=strike, u_yb=yb,
             u_cut=1. if t >= CUT + .04 else 0., u_fall=max(t - (CUT + .33), 0.))
    # cameras: four groups, cut on the hits
    eye_y = YP + F - 49.5 * LH
    if t < EX[4]:                                   # front: the eye was on paper all along; pull back
        x = ease((t - EX[0]) / (EX[4] - EX[0]))
        cam = lerp((0., eye_y, ZP + .2), (.05, .33, ZP + .6), x)
        look = lerp((0., eye_y, ZP), (0., .31, ZP), x); fov = 30 + 10 * x
    elif t < EX[8]:                                 # macro, side: the strike, the ribbon, the fibres
        x = (t - EX[4]) / (EX[8] - EX[4])
        cam = (.13 - .03 * x, .29, .1 - .02 * x); look = (-.005, YP + .004, ZP); fov = 24
    elif t < COUNTS[0]:                             # wide: the whole machine, the paper climbing to the blade
        x = ease((t - EX[8]) / (COUNTS[0] - EX[8]))
        cam = lerp((.78, .55, 1.1), (.68, .64, .95), x); look = (0., .4, .1); fov = 36
    else:                                           # the blade, ratcheted up one notch per count
        look = (0., .64, .3); cam0 = (.32, .76, .66)
        dz = ease((t - COUNTS[5] - .02) / .42)      # dolly zoom before it falls
        k = 1 + .9 * dz
        cam = tuple(l + (c - l) * k for c, l in zip(cam0, look))
        fov = math.degrees(2 * math.atan(math.tan(math.radians(34) / 2) / k))
    p.update(u_cam=cam, u_look=look, u_fov=math.radians(fov))
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--w', type=int, default=1920); ap.add_argument('--h', type=int, default=1080)
    ap.add_argument('--sub', type=int, default=4); ap.add_argument('--stills', type=str)
    a = ap.parse_args()
    r = Renderer(a.w, a.h, (HERE / 'scene.glsl').read_text(encoding='utf-8'), subframes=a.sub)
    r.post.update(u_bloom=.4, u_ca=.005)
    tex = lambda t: {'u_glyphs': GLYPHS, 'u_insc': INSC}
    if a.stills:
        d = HERE / 'stills'; d.mkdir(exist_ok=True)
        for t in map(float, a.stills.split(',')):
            save_png(r.frame(t, params, tex), a.w, a.h, d / f'{t:07.3f}.png')
        return
    fps = 60; n = round((END - START) * fps); t0 = time.monotonic()
    out = HERE / 'preview_1080p.mp4'
    encode(out, a.w, a.h, fps, START, END - START, (r.frame(START + i / fps, params, tex) for i in range(n)))
    print('done', out, f'{time.monotonic() - t0:.0f}s')


if __name__ == '__main__':
    main()
