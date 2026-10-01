"""t04 · out of the sandbox (2:37.5–2:42.8): the box is cut open from inside (12th EXECUTION);
EIN..LIU: a dot-matrix printer in a dark room prints the procession; EXECUTION: a paper guillotine falls."""
import sys, math, argparse, time
from pathlib import Path
from PIL import Image
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'engine'))
from gl import Renderer, encode, save_png

START, END = 157.5, 162.8
EX12, EIN = 158.000, 158.900
COUNTS = [158.900, 159.321, 159.657, 160.244, 160.693, 161.124]
CUT = 161.584
L, LEAD = .27, .04
ATLAS = Image.open(HERE / 'atlas.png')


def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def outc(x): x = clamp(x); return 1 - (1 - x) ** 3


def remap(t):
    """Freeze and dropped frames right after the blade lands."""
    if CUT + .05 < t < CUT + .19: return CUT + .05                      # freeze
    if CUT + .19 <= t < CUT + .33:                                       # stutter: hold every other 3 frames
        k = int((t - CUT - .19) * 60)
        return CUT + .19 + (k // 3) * 3 / 60 * 1.6
    return t


def params(t):
    t = remap(t)
    if t < EIN:
        k = t - EX12
        return dict(u_scene=0., u_cam=(.3 - .06 * clamp((t - START) / 1.4), .3, .72 - .14 * clamp((t - START) / 1.4)),
                    u_look=(0., .12, 0.), u_fov=math.radians(34.),
                    u_slit=outc(k / .07) if k > 0 else 0., u_slit2=outc((k - .42) / .07) if k > .42 else 0.,
                    u_open=ease((k - .55) / .3), u_leak=ease((k - .5) / .35) + .25 * (k > 0))
    F = LEAD + L * sum(outc((t - c) / .26) for c in COUNTS) + .005
    feeding = any(0 < t - c < .26 for c in COUNTS)
    head = .16 * math.sin(t * 55.) if feeding else -.19
    yb = .22 if t < CUT else .22 - .2185 * outc((t - CUT) / .05)
    push = ease((t - EIN) / (CUT - EIN))
    cam = (.03 - .03 * push, .44 - .06 * push, .56 - .12 * push)
    look = (0., .07, -.15)
    return dict(u_scene=1., u_cam=cam, u_look=look, u_fov=math.radians(42. - 6 * push),
                u_F=F, u_head=head, u_led=1. if (feeding or (t * 4) % 1 < .5) else .3,
                u_yb=yb, u_cut=1. if t >= CUT + .045 else 0., u_fall=max(t - (CUT + .33), 0.))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--w', type=int, default=1920); ap.add_argument('--h', type=int, default=1080)
    ap.add_argument('--sub', type=int, default=4); ap.add_argument('--stills', type=str)
    a = ap.parse_args()
    r = Renderer(a.w, a.h, (HERE / 'scene.glsl').read_text(encoding='utf-8'), subframes=a.sub)
    r.post.update(u_bloom=.5, u_ca=.006)
    tex = lambda t: {'u_atlas': ATLAS}
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
