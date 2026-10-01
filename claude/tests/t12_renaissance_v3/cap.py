import sys, importlib.util
from pathlib import Path
HERE = Path(__file__).resolve().parent; CL = HERE.parents[1]
sys.path.insert(0, str(CL / 'engine'))
spec = importlib.util.spec_from_file_location('master', CL / 'film' / 'master.py'); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
from gl import Renderer, save_png
W, H = 1920, 1080
s = M.shot('s10_fragments.py', 's10', W, H)
r = Renderer(W, H, s.SRC, subframes=1)
t = float(sys.argv[1])
p0 = s.params(t)
print({k: v for k, v in p0.items() if not isinstance(v, (list, tuple)) or len(v) < 5})
save_png(r.frame(t, s.params, s.textures, post=s.POST), W, H, HERE / 's10_with_ring.png')
noring = lambda tt: {**s.params(tt), 'u_ringA': 0., 'u_R': 0., 'u_n': 0}
save_png(r.frame(t, noring, s.textures, post=s.POST), W, H, HERE / 's10_no_ring.png')
