"""t05 · the six counts as a stand-alone 2D shot (2:38.6–2:41.9).
Each count is one stage of the lift, held and drifting in slow motion; LIU ends in a dolly zoom and a blur."""
import sys, math, argparse, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'engine'))
from gl import Renderer, encode, save_png

START, END = 158.75, 161.9
COUNTS = [158.900, 159.321, 159.657, 160.244, 160.693, 161.124]
CUT = 161.584
#           body height, crouch, arms overhead
STAGES = [(.14, 1.0, 0.), (.5, .8, 0.), (.95, .5, 0.), (1.3, .2, 0.), (1.95, 0., 1.), (1.72, 0., 1.)]
F0 = 1.1


def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)


def params(t):
    k = max(i for i, c in enumerate(COUNTS) if t >= c) if t >= COUNTS[0] else -1
    if k < 0:
        return dict(u_h=.14, u_crouch=1., u_arm=0., u_walk=0., u_cz=0., u_f=F0, u_blur=0., u_black=1., u_rays=0.)
    nxt = min(k + 1, 5)
    dur = (COUNTS[k + 1] if k < 5 else CUT) - COUNTS[k]
    u = clamp((t - COUNTS[k]) / dur)
    drift = .16 * u                                   # the slow motion inside each held stage
    a, b = STAGES[k], STAGES[nxt]
    h = a[0] + (b[0] - a[0]) * drift
    crouch = a[1] + (b[1] - a[1]) * drift
    arm = a[2] if k < 4 else 1.
    walk = (t - COUNTS[5]) * .9 if k == 5 else 0.
    # dolly zoom: the camera pulls back while zooming in; the body stays the same size, the blade looms
    z = ease((t - COUNTS[5] - .02) / .44) if k == 5 else 0.
    cz = -4. * z
    f = F0 * (4.2 - cz) / 4.2
    blur = ease((t - 161.33) / .25)
    black = 1. if t >= CUT else 0.
    return dict(u_h=h, u_crouch=crouch, u_arm=arm, u_walk=walk, u_cz=cz, u_f=f, u_blur=blur, u_black=black,
                u_rays=ease((t - COUNTS[0]) / .3))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--w', type=int, default=1920); ap.add_argument('--h', type=int, default=1080)
    ap.add_argument('--sub', type=int, default=4); ap.add_argument('--stills', type=str)
    a = ap.parse_args()
    r = Renderer(a.w, a.h, (HERE / 'scene.glsl').read_text(encoding='utf-8'), subframes=a.sub)
    r.post.update(u_bloom=.35, u_ca=.004, u_grain=.045)
    if a.stills:
        d = HERE / 'stills'; d.mkdir(exist_ok=True)
        for t in map(float, a.stills.split(',')):
            save_png(r.frame(t, params), a.w, a.h, d / f'{t:07.3f}.png')
        return
    fps = 60; n = round((END - START) * fps); t0 = time.monotonic()
    out = HERE / 'preview_1080p.mp4'
    encode(out, a.w, a.h, fps, START, END - START, (r.frame(START + i / fps, params) for i in range(n)))
    print('done', out, f'{time.monotonic() - t0:.0f}s')


if __name__ == '__main__':
    main()
