"""t02 · only god / proof of my existence (1:24.9–1:28.8).

Pure black. On "you're the proof" a star sweeps past the camera from behind, curves away and dives
behind an unseen black hole; lensing wraps its light into arcs / an Einstein ring and the shadow appears.
"""
import sys, math, argparse, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'engine'))
from gl import Renderer, encode, save_png

START, END = 84.9, 88.8
T_YOU, T_EXIST, T_NEXT = 86.538, 87.922, 88.587


def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)


def bez(p0, p1, p2, p3, s):
    u = 1 - s
    return tuple(u**3 * a + 3 * u * u * s * b + 3 * u * s * s * c + s**3 * d for a, b, c, d in zip(p0, p1, p2, p3))


def star_at(t):
    """the star: in from the right as soon as the shot begins ("If I"); across the near field; then slowly in behind the hole"""
    P0, P1, P2, P3 = (3.4, .5, 8.4), (1.9, .35, 5.2), (6.2, .25, -7.), (.0, -.525 + .75, -15.)
    u = clamp((t - 84.266) / 5.14)                              # already under way when the shot begins; at 88.587 exactly where the old path was (s08 picks up its arcs)
    s = .26 * ease(u / .4) if u < .4 else .26 + .74 * (1 - (1 - (u - .4) / .6) ** 1.6)
    return bez(P0, P1, P2, P3, s)


def params(t):
    cam = (0., .35, 10.2 - .5 * ease((t - 86.8) / 2.))       # a slow push-in: we are closer than we thought
    star = star_at(t)
    vis = ease((t - 85.5) / .12)
    trail = [star_at(t - .35 * (k + 1)) for k in range(4)]
    return dict(u_cam=cam, u_look=(0., 0., 0.), u_fov=math.radians(52.), u_star=star, u_rstar=.3,
                u_glow=.05 * vis, u_bright=.95 * vis, u_corona=.3 * vis,
                u_sky=1., u_grid=0., u_trail=trail, u_rev=.25 + .55 * ease((t - 86.0) / 2.3),
                u_gather=ease((t - 88.1) / .48), u_ringC=(960. * RES[0] / 1920, 530. * RES[1] / 1080), u_ringR=500. * RES[1] / 1080,
                u_shadowR=305. * RES[1] / 1080)


RES = [1920, 1080]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--w', type=int, default=1920); ap.add_argument('--h', type=int, default=1080)
    ap.add_argument('--sub', type=int, default=4); ap.add_argument('--stills', type=str)
    ap.add_argument('--out', type=str, default=str(HERE / 'preview_1080p.mp4'))
    a = ap.parse_args()
    r = Renderer(a.w, a.h, (HERE / 'scene.glsl').read_text(encoding='utf-8'), subframes=a.sub)
    r.post.update(u_bloom=.45, u_ca=.008)
    if a.stills:
        (HERE / 'stills').mkdir(exist_ok=True)
        for t in map(float, a.stills.split(',')):
            save_png(r.frame(t, params), a.w, a.h, HERE / 'stills' / f'{t:07.3f}.png'); print('still', t, flush=True)
        return
    fps = 60; n = round((END - START) * fps); t0 = time.monotonic()
    encode(a.out, a.w, a.h, fps, START, END - START, (r.frame(START + i / fps, params) for i in range(n)))
    print('done', a.out, f'{time.monotonic() - t0:.0f}s')


if __name__ == '__main__':
    main()
