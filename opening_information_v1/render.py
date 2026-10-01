"""Independent 59-second information study. All original inputs remain read-only."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'train_cel_test/_vendor'))
sys.path.insert(0,str(HERE/'base/engine'))
import argparse, importlib.util, json, time
from PIL import Image
from gl import Renderer, encode, save_png
from common import gate, blank

FPS=60
FRAMES=3553
DURATION=FRAMES/FPS

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def build(w,h):
    import overlays_boot, overlays_self, overlays_gap
    boot=load(HERE/'base/film/shots/s01_boot.py','study_boot')
    exe=load(HERE/'base/film/shots/s02_execute.py','study_execute')
    self_=load(HERE/'base/film/shots/s03_self.py','study_self')
    gap=load(HERE/'base/tests/t01_gap_ring/render.py','study_gap')
    gap.SRC=(HERE/'base/tests/t01_gap_ring/scene.glsl').read_text(encoding='utf-8')
    all_windows={**overlays_boot.WINDOWS,'self':overlays_self.WINDOWS,'gap':overlays_gap.WINDOWS}
    def tex(name,mod,t):
        original=mod.ui(t,w,h) if name=='gap' else mod.textures(t,w,h)
        a=gate(t,all_windows[name])
        if name=='boot' and a>0:
            original['u_ui']=Image.blend(original['u_ui'],blank(w,h),a)
        elif name=='self' and a>0:
            original['u_ui']=Image.blend(original['u_ui'],mod.textures(t,w,h,hide=True)['u_ui'],a)
        return original
    def ov(name,mod,t):
        if name in ('boot','execute'): return overlays_boot.overlay(name,mod,t,w,h)
        if name=='self': return overlays_self.overlay(mod,t,w,h)
        return overlays_gap.overlay(mod,t,w,h)
    S=[(0.,'boot',boot),(16.,'execute',exe),(29.709,'self',self_),(47.,'gap',gap)]
    return S,all_windows,tex,ov

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--w',type=int,default=1920); ap.add_argument('--h',type=int,default=1080)
    ap.add_argument('--sub',type=int,default=4)
    ap.add_argument('--stills'); ap.add_argument('--out',default='opening_information_1080p60.mp4')
    ap.add_argument('--start',type=float,default=0.); ap.add_argument('--end',type=float,default=DURATION)
    a=ap.parse_args(); S,windows,tex,ov=build(a.w,a.h)
    r=Renderer(a.w,a.h,S[0][2].SRC,subframes=a.sub)
    def render(t):
        _,name,mod=next(s for s in reversed(S) if t>=s[0])
        r.use(name,mod.SRC)
        sprites=(name,mod.SPRITE_VS,mod.SPRITE_FS,mod.SPRITE_DATA) if hasattr(mod,'SPRITE_VS') else None
        data=r.frame(t,mod.params,lambda tt:tex(name,mod,tt),post=getattr(mod,'POST',{}),sprites=sprites)
        if gate(t,windows[name])<=0: return data
        overlay=ov(name,mod,t)
        frame=Image.frombytes('RGB',(a.w,a.h),data).transpose(Image.Transpose.FLIP_TOP_BOTTOM).convert('RGBA')
        result=Image.alpha_composite(frame,overlay).convert('RGB')
        return result.transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes()
    if a.stills:
        folder=HERE/'stills'; folder.mkdir(exist_ok=True)
        for t in map(float,a.stills.split(',')):
            save_png(render(t),a.w,a.h,folder/f'{t:07.3f}.png')
            print('still',t,flush=True)
        return
    n=round((a.end-a.start)*FPS); duration=n/FPS; started=time.monotonic()
    def frames():
        for i in range(n):
            if i%120==0: print(f'{i}/{n} frames | {time.monotonic()-started:.1f}s',flush=True)
            yield render(a.start+i/FPS)
    out=Path(a.out)
    if not out.is_absolute(): out=HERE/out
    encode(str(out),a.w,a.h,FPS,a.start,duration,frames(),cq=18)
    changed=sum(b-a for ws in windows.values() for a,b in ws)
    manifest={'output':str(out),'size':[a.w,a.h],'fps':FPS,'frames':n,'start':a.start,'duration':duration,
              'subframes':a.sub,'change_windows':windows,'annotated_seconds':round(changed,3),
              'annotated_fraction':changed/DURATION,'camera_changes':False,'geometry_changes':False,
              'lyrics_added':False,'elapsed_seconds':round(time.monotonic()-started,2),
              'method':'Copied procedural 3D/cel source; world-projected drafting annotations composited after tone mapping.'}
    (HERE/'render_manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print('done',out,flush=True)

if __name__=='__main__': main()
