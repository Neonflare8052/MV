"""Independent v2 sample; existing master, s10, s12 and v1 are read-only inputs."""
import argparse, importlib.util, json, sys, time, hashlib
from pathlib import Path
from PIL import Image

HERE=Path(__file__).resolve().parent
CL=HERE.parents[1]; ROOT=CL.parent
sys.path.insert(0,str(CL/'engine'))
from gl import Renderer,encode,save_png
import shot as S
import terminal as T

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--start',type=float,default=122.5);ap.add_argument('--end',type=float,default=147.66)
    ap.add_argument('--w',type=int,default=1920);ap.add_argument('--h',type=int,default=1080)
    ap.add_argument('--sub',type=int,default=2);ap.add_argument('--stills');ap.add_argument('--out')
    a=ap.parse_args()
    spec=importlib.util.spec_from_file_location('readonly_s10',CL/'film/shots/s10_fragments.py')
    prev=importlib.util.module_from_spec(spec);spec.loader.exec_module(prev)
    inputs=[ROOT/'Mili - world.execute (me) ;.mp3',CL/'engine/gl.py',CL/'film/shots/s10_fragments.py',
        CL/'film/shots/s12_exe.py',CL/'tests/t07_eye/render.py',HERE/'paper.py',HERE/'terminal.py',HERE/'shot.py',HERE/'render.py']
    manifest=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in inputs]
    r=Renderer(a.w,a.h,S.SRC,subframes=a.sub)
    def pp(t):
        p=prev.params(t);p['u_fadeMarks']=0.;return p
    r.use('before',prev.SRC)
    data=r.frame(S.T0-1/60,pp,lambda t:prev.textures(t,a.w,a.h),post=prev.POST)
    last=Image.frombytes('RGB',(a.w,a.h),data).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    def bare(t):
        p=pp(t);p.update(u_ringA=0.,u_polyA=1.,u_fadeMarks=1.,u_keep=1.,u_snap=0.,u_heart=0.,u_ink=0.,u_splat=0.,u_split=0.,u_blade=-2.)
        return p
    src=prev.SRC.replace('col+=cursors(uv)*u_polyA;','').replace('if(u_polyA>0.){','if(false){')
    r.use('bare',src)
    data=r.frame(S.T0-1/60,bare,lambda t:prev.textures(t,a.w,a.h),post=prev.POST)
    base=Image.frombytes('RGB',(a.w,a.h),data).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    def frame(t):
        if t<S.T0:
            r.use('before',prev.SRC)
            return r.frame(t,pp,lambda tt:prev.textures(tt,a.w,a.h),post=prev.POST)
        r.use('v2',S.SRC)
        return r.frame(t,S.params,lambda tt:S.textures(tt,a.w,a.h,last,base),post=S.POST)
    (HERE/'terminal_events.json').write_text(json.dumps(T.audit(),indent=2),encoding='utf-8')
    if a.stills:
        (HERE/'stills').mkdir(exist_ok=True)
        for t in map(float,a.stills.split(',')):
            save_png(frame(t),a.w,a.h,HERE/'stills'/f'{t:07.3f}.png');print('still',t,flush=True)
        return
    n=round((a.end-a.start)*60);out=Path(a.out) if a.out else HERE/'renaissance_love_eye_v2_1080p60.mp4'
    begin=time.monotonic()
    def frames():
        for k in range(n):
            if k%120==0:print(f'{k}/{n} {time.monotonic()-begin:.1f}s',flush=True)
            yield frame(a.start+k/60)
    encode(out,a.w,a.h,60,a.start,n/60,frames(),cq=18)
    result=dict(output=str(out),start=a.start,end=a.start+n/60,width=a.w,height=a.h,fps=60,frames=n,
                subframes=a.sub,elapsed_seconds=time.monotonic()-begin,input_manifest=manifest)
    (HERE/'render_manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print('done',out,flush=True)

if __name__=='__main__':main()
