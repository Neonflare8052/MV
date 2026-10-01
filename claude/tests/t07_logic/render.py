"""t07 sample: s02's last seconds, then the logic world.  python -X utf8 render.py [--start 28 --end 44.452] [--stills 30,33]"""
import sys, argparse, time, importlib.util
from pathlib import Path
HERE = Path(__file__).resolve().parent; CL = HERE.parents[1]
sys.path.insert(0, str(CL / 'engine'))
from gl import Renderer, encode, save_png


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


ap = argparse.ArgumentParser()
ap.add_argument('--start', type=float, default=28.0); ap.add_argument('--end', type=float, default=48.0)
ap.add_argument('--w', type=int, default=1920); ap.add_argument('--h', type=int, default=1080)
ap.add_argument('--stills', type=str); ap.add_argument('--out', type=str)
a = ap.parse_args()
master = load(CL / 'film' / 'master.py', 'master')
s02 = master.shot('s02_execute.py', 's02', a.w, a.h)
me = load(HERE / 'shot.py', 't07')
t01 = master.proto('t01_gap_ring', 't01', a.w, a.h, textures=lambda m, t, W, H: m.ui(t, W, H))
r = Renderer(a.w, a.h, s02.SRC, subframes=1)


def render(t):
    if t < me.T0:
        r.use('s02', s02.SRC); return r.frame(t, s02.params, s02.textures, post=s02.POST)
    if t >= me.T_OUT:
        r.use('t01', t01.SRC); return r.frame(t, t01.params, t01.textures, post=t01.POST)
    r.use('t07', me.SRC); return r.frame(t, me.params, lambda tt: me.textures(tt, a.w, a.h), post=me.POST)


if a.stills:
    d = HERE / 'stills'; d.mkdir(exist_ok=True)
    for t in map(float, a.stills.split(',')):
        save_png(render(t), a.w, a.h, d / f'{t:07.3f}.png'); print('still', t, flush=True)
    sys.exit()
fps = 60; n = round((a.end - a.start) * fps); t0 = time.monotonic()
out = Path(a.out) if a.out else HERE / f't07_logic_{a.start:06.2f}-{a.end:06.2f}_{a.h}p.mp4'
def frames():
    for k in range(n):
        if k % 120 == 0: print(f'{k}/{n}  {time.monotonic() - t0:.0f}s', flush=True)
        yield render(a.start + k / fps)
encode(out, a.w, a.h, fps, a.start, a.end - a.start, frames())
print('done', out, f'{time.monotonic() - t0:.0f}s')
