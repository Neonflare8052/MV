import sys, importlib.util
from pathlib import Path
HERE = Path(__file__).resolve().parent; CL = HERE.parents[1]
sys.path.insert(0, str(CL / 'engine'))
spec = importlib.util.spec_from_file_location('master', CL / 'film' / 'master.py'); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
from gl import Renderer, save_png
s = M.shot('s02_execute.py', 's02', 960, 540)
r = Renderer(960, 540, s.SRC, subframes=1)
for t in map(float, sys.argv[1].split(',')):
    save_png(r.frame(t, s.params, s.textures, post=s.POST), 960, 540, HERE / f'peek_{t:.2f}.png')
