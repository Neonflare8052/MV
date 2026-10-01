"""t13 · tech ladder sample (0:59.223–1:24.268): the film's timeline with s05 / s06 swapped for the versions here.

py -3.11 -X utf8 render.py --start 58.4 --end 86.2               (video, written next to this file)
py -3.11 -X utf8 render.py --stills 60.5,64,68,72,75.5,79,83     (stills in ./stills)
"""
import sys, importlib.util
from pathlib import Path
HERE = Path(__file__).resolve().parent
FILM = HERE.parents[1] / 'film'

spec = importlib.util.spec_from_file_location('master', FILM / 'master.py')
master = importlib.util.module_from_spec(spec); spec.loader.exec_module(master)

SWAP = {'s05': HERE / 's05_tech.py', 's06': HERE / 's06_tech.py', 't02': HERE / 't02_tech.py'}
_build = master.build


def build(w, h):
    master.HERE = FILM                 # build() looks for film/shots
    S = _build(w, h)
    master.HERE = HERE
    out = []
    for t0, s in S:
        p = SWAP.get(s.NAME)
        if p and p.exists():
            m = master.load(p, s.NAME + '_tech')
            s.SRC, s.params, s.MOD = m.SRC, m.params, m
            s.textures = (lambda m: (lambda t: m.textures(t, w, h)))(m) if hasattr(m, 'textures') else None
            s.POST = getattr(m, 'POST', {})
        out.append((t0, s))
    return out


master.build = build
_frame = master.Renderer.frame


def frame(self, t, params_fn, *a, **k):
    params_fn(t)                       # let a shot set its post (POST) for this frame, not the next
    return _frame(self, t, params_fn, *a, **k)


master.Renderer.frame = frame
master.HERE = HERE                     # stills and default output land here
if __name__ == '__main__':
    if '--out' not in sys.argv and '--stills' not in sys.argv:
        a = dict(zip(sys.argv[1::2], sys.argv[2::2]))
        sys.argv += ['--out', str(HERE / f"t13_tech_{float(a.get('--start', 58.4)):06.2f}-{float(a.get('--end', 86.2)):06.2f}_{a.get('--h', '1080')}p.mp4")]
    master.main()
