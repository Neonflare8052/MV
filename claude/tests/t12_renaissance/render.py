"""Isolated original-audio sample. Never writes to film/shots or master.py."""
import argparse, importlib.util, sys, time, json
from pathlib import Path
from PIL import Image

HERE=Path(__file__).resolve().parent
CL=HERE.parents[1]
sys.path.insert(0,str(CL/'engine'))
from gl import Renderer,encode,save_png

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--start',type=float,default=122.5);ap.add_argument('--end',type=float,default=141.5)
    ap.add_argument('--w',type=int,default=1920);ap.add_argument('--h',type=int,default=1080)
    ap.add_argument('--stills');ap.add_argument('--out');ap.add_argument('--sub',type=int,default=2)
    a=ap.parse_args()
    prev=load(CL/'film/shots/s10_fragments.py','s10_readonly')
    nxt=load(CL/'film/shots/s12_exe.py','s12_readonly')
    me=load(HERE/'shot.py','renaissance')
    renderer=Renderer(a.w,a.h,me.SRC,subframes=a.sub)
    def pp(t):
        p=prev.params(t);p['u_fadeMarks']=0.
        return p
    renderer.use('before',prev.SRC)
    data=renderer.frame(me.T0-1/60,pp,lambda t:prev.textures(t,a.w,a.h),post=prev.POST)
    last=Image.frombytes('RGB',(a.w,a.h),data).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    def bare(t):
        p=pp(t);p.update(u_ringA=0.,u_polyA=1.,u_fadeMarks=1.,u_keep=1.,u_snap=0.,u_heart=0.,u_ink=0.,u_splat=0.,u_split=0.,u_blade=-2.)
        return p
    bare_src=prev.SRC.replace('col+=cursors(uv)*u_polyA;', '').replace('if(u_polyA>0.){', 'if(false){')
    renderer.use('bare',bare_src)
    base=renderer.frame(me.T0-1/60,bare,lambda t:prev.textures(t,a.w,a.h),post=prev.POST)
    lastbase=Image.frombytes('RGB',(a.w,a.h),base).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    # Composite a display-referred overlay AFTER the shared HDR renderer, preserving
    # its precise placement and red throughout the typography-to-terminal transition.
    def overlay(data,t):
        base=Image.frombytes('RGB',(a.w,a.h),data).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        ui=me.terminal_overlay(t,a.w,a.h)
        return Image.alpha_composite(base.convert('RGBA'),ui).convert('RGB').transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes()
    def render(t):
        if t<me.T0:
            renderer.use('before',prev.SRC)
            return renderer.frame(t,pp,lambda tt:prev.textures(tt,a.w,a.h),post=prev.POST)
        if t<me.T_TERM:
            renderer.use('study',me.SRC)
            data=renderer.frame(t,me.params,lambda tt:me.textures(tt,a.w,a.h,last,lastbase),post=me.POST)
            return overlay(data,t) if t>=132.88 else data
        renderer.use('after',nxt.SRC)
        def nt(tt):
            tex=nxt.textures(tt,a.w,a.h)
            tex['u_ui']=Image.new('RGBA',(a.w,a.h),(0,0,0,0))
            return tex
        data=renderer.frame(t,nxt.params,nt,post=nxt.POST)
        return overlay(data,t) if t<138.5 else data
    if a.stills:
        (HERE/'stills').mkdir(exist_ok=True)
        for t in map(float,a.stills.split(',')):
            save_png(render(t),a.w,a.h,HERE/'stills'/f'{t:07.3f}.png');print('still',t,flush=True)
        return
    start=time.monotonic();fps=60;n=round((a.end-a.start)*fps)
    out=Path(a.out) if a.out else HERE/'t12_renaissance_v1_1080p60.mp4'
    def frames():
        for k in range(n):
            if k%120==0:print(f'{k}/{n} {time.monotonic()-start:.1f}s',flush=True)
            yield render(a.start+k/fps)
    encode(out,a.w,a.h,fps,a.start,a.end-a.start,frames(),cq=18)
    (HERE/'render_manifest.json').write_text(json.dumps(dict(output=str(out),start=a.start,end=a.end,width=a.w,height=a.h,fps=fps,frames=n,subframes=a.sub,elapsed_seconds=time.monotonic()-start,original_audio=True),indent=2),encoding='utf-8')
    print('done',out,flush=True)

if __name__=='__main__':main()
