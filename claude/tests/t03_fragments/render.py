"""t03 · FRAGMENTS -> DISHEARTENED (1:57.9–2:06.2), two background variants.

python render.py --bg palimpsest|tondo
"""
import sys, math, argparse, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'engine'))
from gl import Renderer, encode, save_png

START, END = 117.9, 126.2
ERASE = [118.926, 119.158, 119.390, 119.617, 119.843, 120.307]     # one fragment per beat / half beat
FRAG_T = 120.860                                                    # FRAGMENTS: the last one goes
TRY, NEAR, SNAP = 121.677, 124.464, 124.890
FRAG_ANG = [18 + 51.4 * i for i in range(7)]
ORDER = [2, 5, 0, 4, 1, 6, 3]                                       # which fragment each beat erases
BG = 0.


def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def outc(x): x = clamp(x); return 1 - (1 - x) ** 3


def saccade(t, t0, a, b, dur=.07, over=.07):
    if t < t0: return a
    x = (t - t0) / dur
    if x < 1: return a + (b - a) * (1 + over) * outc(x)
    return b + (b - a) * over * (1 - ease((t - t0 - dur) / .14))


def frag_angle(i, t):
    drift = (t - START) * .06
    return FRAG_ANG[i] + math.degrees(drift * (.25 + .05 * (i % 3)))


def shortest(a, b):
    return a + ((b - a + 180) % 360 - 180)


def params(t):
    # the gap looks at each fragment a moment before it is erased
    g = 0.
    for k, t0 in enumerate(ERASE):
        g = saccade(t, t0 - .12, g, shortest(g, frag_angle(ORDER[k], t0)))
    g = saccade(t, FRAG_T - .1, g, shortest(g, frag_angle(ORDER[6], FRAG_T)))
    g = saccade(t, TRY - .2, g, shortest(g, -90.), .12)                # settle: gap faces down
    erase = [0.] * 7
    for k, t0 in enumerate(ERASE):
        erase[ORDER[k]] = clamp((t - t0) / .55)
    for i in range(7):
        if erase[i] == 0.: erase[i] = clamp((t - FRAG_T) / .7)
    base = math.radians(27.)
    half = base
    if t > TRY:                                                         # trying to close: effort, trembling
        x = clamp((t - TRY) / (NEAR - TRY))
        half = base * (1 - .9 * (1 - (1 - x) ** 1.6))
        half += math.radians(1.2) * math.sin(t * 47.) * x + math.radians(.8) * math.sin(t * 23.) * x
    if t > SNAP:                                                        # snaps back, a little overshoot
        y = t - SNAP
        half = base + math.radians(9.) * math.exp(-y * 7.) * math.cos(y * 26.)
    heart = 0.
    if NEAR - .35 < t < SNAP + .05:
        heart = math.exp(-((t - (NEAR - .05)) / .12) ** 2) + .5 * math.exp(-((t - (NEAR + .33)) / .1) ** 2)
    return dict(u_bg=BG, u_cursor=1 - ease((t - 118.33) / .25), u_ringA=ease((t - 118.36) / .3),
                u_R=.15 * (.3 + .7 * outc((t - 118.36) / .35)), u_gap=math.radians(g), u_half=half,
                u_erase=erase, u_fragA=ease((t - 118.5) / .35), u_drift=t - START,
                u_heart=heart, u_bgA=ease((t - 118.5) / 1.0),
                u_circle=ease((t - TRY) / (SNAP - TRY)) * (1 + .6 * math.exp(-max(t - SNAP, 0) * 2) * (t > SNAP)),
                u_ghost=1., u_scratch=clamp((t - ERASE[0]) / (SNAP - ERASE[0])),
                u_snap=math.exp(-max(t - SNAP, 0) * 6) * (t > SNAP) + .4 * clamp((t - TRY) / (NEAR - TRY)) * (t < SNAP))


def main():
    global BG
    ap = argparse.ArgumentParser()
    ap.add_argument('--bg', default='palimpsest'); ap.add_argument('--w', type=int, default=1920); ap.add_argument('--h', type=int, default=1080)
    ap.add_argument('--sub', type=int, default=4); ap.add_argument('--stills', type=str)
    a = ap.parse_args()
    BG = 0. if a.bg == 'palimpsest' else 1.
    r = Renderer(a.w, a.h, (HERE / 'scene.glsl').read_text(encoding='utf-8'), subframes=a.sub)
    r.post.update(u_bloom=.5)
    if a.stills:
        d = HERE / f'stills_{a.bg}'; d.mkdir(exist_ok=True)
        for t in map(float, a.stills.split(',')):
            save_png(r.frame(t, params), a.w, a.h, d / f'{t:07.3f}.png')
        return
    fps = 60; n = round((END - START) * fps); t0 = time.monotonic()
    out = HERE / f'preview_{a.bg}_1080p.mp4'
    encode(out, a.w, a.h, fps, START, END - START, (r.frame(START + i / fps, params) for i in range(n)))
    print('done', out, f'{time.monotonic() - t0:.0f}s')


if __name__ == '__main__':
    main()
