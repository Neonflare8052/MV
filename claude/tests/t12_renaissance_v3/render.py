"""t12 v3 sample: s10's last seconds, the new shot (125.361–139.229), then s12 unchanged (the old eye).
python -X utf8 render.py [--start 123.5 --end 147.66] [--stills a,b]"""
import sys, argparse, time, importlib.util
from pathlib import Path
HERE = Path(__file__).resolve().parent; CL = HERE.parents[1]
sys.path.insert(0, str(CL / 'engine'))
from gl import Renderer, encode, save_png


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


ap = argparse.ArgumentParser()
ap.add_argument('--start', type=float, default=123.5); ap.add_argument('--end', type=float, default=147.66)
ap.add_argument('--w', type=int, default=1920); ap.add_argument('--h', type=int, default=1080)
ap.add_argument('--stills', type=str); ap.add_argument('--out', type=str)
a = ap.parse_args()
master = load(CL / 'film' / 'master.py', 'master')
s10 = master.shot('s10_fragments.py', 's10', a.w, a.h)
me = load(HERE / 'shot.py', 't12v3')
r = Renderer(a.w, a.h, s10.SRC, subframes=1)


def render(t):
    if t < me.T0:
        r.use('s10', s10.SRC); return r.frame(t, s10.params, s10.textures, post=s10.POST)
    if t >= me.T_END:                                   # s12, re-timed (its eye forms at 141.06), unchanged otherwise
        S = me.S12
        r.use('s12', S.SRC); return r.frame(t, me.s12_params, lambda tt: S.textures(tt, a.w, a.h), post=S.POST)
    r.use('t12', me.SRC); return r.frame(t, me.params, lambda tt: me.textures(tt, a.w, a.h), post=me.POST)


if a.stills:
    d = HERE / 'stills'; d.mkdir(exist_ok=True)
    for t in map(float, a.stills.split(',')):
        save_png(render(t), a.w, a.h, d / f'{t:07.3f}.png'); print('still', t, flush=True)
    sys.exit()
fps = 60; n = round((a.end - a.start) * fps); t0 = time.monotonic()
out = Path(a.out) if a.out else HERE / f't12_v3_{a.start:06.2f}-{a.end:06.2f}_{a.h}p.mp4'
def frames():
    for k in range(n):
        if k % 120 == 0: print(f'{k}/{n}  {time.monotonic() - t0:.0f}s', flush=True)
        yield render(a.start + k / fps)
encode(out, a.w, a.h, fps, a.start, a.end - a.start, frames())
print('done', out, f'{time.monotonic() - t0:.0f}s')
