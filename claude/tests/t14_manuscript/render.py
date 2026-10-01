"""t14 · you have left, the manuscript (sample): the film's timeline with s09 swapped for s09m (from 1:52.22).

py -3.11 -X utf8 render.py --start 110.4 --end 119.6 --out <file>
py -3.11 -X utf8 render.py --stills 112.5,113.6,114.5
"""
import sys, importlib.util
from pathlib import Path
HERE = Path(__file__).resolve().parent
FILM = HERE.parents[1] / 'film'
spec = importlib.util.spec_from_file_location('master', FILM / 'master.py')
master = importlib.util.module_from_spec(spec); spec.loader.exec_module(master)
_build = master.build


def build(w, h):
    master.HERE = FILM
    S = _build(w, h)
    master.HERE = HERE
    for t0, s in S:
        if s.NAME == 's09':
            m = master.load(HERE / 's09m.py', 's09m')
            s.SRC, s.params, s.MOD, s.POST, s.DELEGATE = m.SRC, m.params, m, m.POST, None
            s.textures = (lambda m: (lambda t: m.textures(t, w, h)))(m)
    return S


master.build = build
_frame = master.Renderer.frame


def frame(self, t, params_fn, *a, **k):
    params_fn(t)                       # a shot's POST for this frame, not the next
    return _frame(self, t, params_fn, *a, **k)


master.Renderer.frame = frame
master.HERE = HERE
if __name__ == '__main__':
    master.main()
