"""t15 · Tycho → epicycles → cogito (sample): the film's timeline with s09, s10 and s11 swapped for the versions here.
s09t starts at 111.5 (it takes over s08c's last frame); s10e from 118.333; s11c from 125.361.

py -3.11 -X utf8 render.py --start 110.4 --end 132.0 --out <file>
py -3.11 -X utf8 render.py --stills 112.5,114.0
"""
import sys, importlib.util
from pathlib import Path
HERE = Path(__file__).resolve().parent
FILM = HERE.parents[1] / 'film'
spec = importlib.util.spec_from_file_location('master', FILM / 'master.py')
master = importlib.util.module_from_spec(spec); spec.loader.exec_module(master)
_build = master.build
SWAP = {'s09': ('s09t.py', 110.221), 's11': ('s11g.py', 118.333)}
DROP = {'s10'}                         # the book (s11g) begins at 118.333


def build(w, h):
    master.HERE = FILM
    S = _build(w, h)
    master.HERE = HERE
    out = []
    for t0, s in S:
        if s.NAME in DROP: continue
        if s.NAME in SWAP and (HERE / SWAP[s.NAME][0]).exists():
            f, t_new = SWAP[s.NAME]
            m = master.load(HERE / f, s.NAME + '_t15')
            s.SRC, s.params, s.MOD, s.POST, s.DELEGATE = m.SRC, m.params, m, getattr(m, 'POST', {}), None
            s.textures = (lambda m: (lambda t: m.textures(t, w, h)))(m) if hasattr(m, 'textures') else None
            s.SPRITES = (s.NAME, m.SPRITE_VS, m.SPRITE_FS, m.SPRITE_DATA) if hasattr(m, 'SPRITE_VS') else None
            if t_new is not None: t0 = t_new
        out.append((t0, s))
    out.sort(key=lambda x: x[0])
    return out


master.build = build
_frame = master.Renderer.frame


def frame(self, t, params_fn, *a, **k):
    params_fn(t)                       # a shot's POST for this frame, not the next
    return _frame(self, t, params_fn, *a, **k)


master.Renderer.frame = frame
master.HERE = HERE
if __name__ == '__main__':
    master.main()
