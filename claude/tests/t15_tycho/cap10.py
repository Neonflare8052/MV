"""The page s11 opens from: s10e at 125.361 without the ring, the outline, the epicycles (as tests/t12_renaissance_v3/cap.py
does for s10). Writes s10_no_ring.png here; s11c reads it."""
import sys, importlib.util
from pathlib import Path
HERE = Path(__file__).resolve().parent; CL = HERE.parents[1]
sys.path.insert(0, str(CL / 'engine'))
spec = importlib.util.spec_from_file_location('master', CL / 'film' / 'master.py'); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
from gl import Renderer, save_png
W, H = 1920, 1080
m = M.load(HERE / 's10e.py', 's10e_cap')
r = Renderer(W, H, m.SRC, subframes=1)
t = 125.361
noring = lambda tt: {**m.params(tt), 'u_ringA': 0., 'u_R': 0., 'u_n': 0, 'u_eA': 0., 'u_voidA': 0., 'u_prevA': 0.}
m.params(t)
save_png(r.frame(t, noring, lambda tt: m.textures(tt, W, H), post=m.POST), W, H, HERE / 's10_no_ring.png')
print('saved', HERE / 's10_no_ring.png')
