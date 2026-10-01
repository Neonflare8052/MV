import sys, importlib.util
from pathlib import Path
HERE = Path(__file__).resolve().parent; CL = HERE.parents[1]
sys.path.insert(0, str(CL / 'engine'))
spec = importlib.util.spec_from_file_location('master', CL / 'film' / 'master.py'); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
from gl import Renderer, save_png
S = M.build(960, 540)
r = Renderer(960, 540, 'void main(){}'.replace('void', '#version 330\nout vec4 o;void').replace('{}', '{o=vec4(0.);}'), subframes=1)
(HERE / 'old').mkdir(exist_ok=True)
for t in map(float, sys.argv[1].split(',')):
    i, s = M.pick(S, t); r.use(f'shot{i}', s.SRC)
    save_png(r.frame(t, s.params, s.textures, post=s.POST, sprites=getattr(s, 'SPRITES', None)), 960, 540, HERE / 'old' / f'{t:07.3f}.png')
