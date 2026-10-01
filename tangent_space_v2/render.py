"""Recomposed point-cloud / translucent-vector study, entirely authored in 3D."""
from __future__ import annotations
import sys
sys.dont_write_bytecode = True
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'train_cel_test/_vendor'))
sys.path.insert(0,str(HERE/'engine'))
import argparse, json, math, subprocess, time
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from gl import Renderer,save_png,FFMPEG,SONG

START,END,FPS=33.4,40.7,60
POST=dict(u_bloom=.27,u_grain=.018,u_ca=.0025,u_sat=.85,u_gain=1.12)

def ease(x):
    x=max(0.,min(1.,x));return x*x*(3.-2.*x)
def blend(a,b,x):
    return tuple(u+(v-u)*x for u,v in zip(a,b))
def field(x,z,clock,quiet):
    a=1.19*x+.40*z-clock;b=2.12*x-.27*z+clock*.34
    h=.68*math.sin(a)+.18*math.sin(b)
    dx=.8092*math.cos(a)+.3816*math.cos(b)
    dz=.272*math.cos(a)-.0486*math.cos(b)
    calm=quiet*math.exp(-((x-.70)/1.65)**2-(z/3.8)**4)
    cx=calm*(-2.*(x-.70)/1.65**2);cz=calm*(-4.*z**3/3.8**4)
    return h*(1-calm)+.24*calm,dx*(1-calm)+(.24-h)*cx,dz*(1-calm)+(.24-h)*cz

KEYS=[
    (33.4,(2.9,1.45,7.3),(0.,.05,0.),42.,-7.),
    (35.4,(.55,1.65,6.3),(.1,.10,0.),44.,0.),
    (36.9,(-1.5,2.7,6.0),(.15,.0,0.),47.,5.),
    (38.30,(-2.6,2.6,5.1),(.4,.0,-.30),51.,3.),
    (39.30,(-1.3,2.25,4.65),(.70,.12,-.10),48.,0.),
    (40.7,(.6,1.85,4.0),(.7,.25,-.35),46.,0.),
]
def camera(t):
    if t<=KEYS[0][0]:return KEYS[0][1:]
    for a,b in zip(KEYS,KEYS[1:]):
        if t<=b[0]:
            k=ease((t-a[0])/(b[0]-a[0]))
            return blend(a[1],b[1],k),blend(a[2],b[2],k),a[3]+(b[3]-a[3])*k,a[4]+(b[4]-a[4])*k
    return KEYS[-1][1:]

def state(t):
    unfold=ease((t-36.86)/1.31)
    quiet=ease((t-38.60)/.73)
    clock=(t-37.067)*1.13+.35
    h,dx,dz=field(.70,0.,clock,quiet)
    n=np.array([-dx,1.,-dz]);n/=np.linalg.norm(n)
    # No dropped game-piece: it remains the same recipient through the hand-off.
    above=.105+.33*(1.-ease((t-38.53)/.7))
    target=np.array([.7,h,0.])+n*above
    orbital=.65+ease((t-34.5)/1.7)*1.35
    ring_you=(orbital,.32,0.)
    you=blend(ring_you,target,ease((t-36.75)/1.58))
    planes=[];growth=[]
    for i in range(7):
        k=i-3;z=k*1.02;x=.70+.12*math.sin(k*1.20)
        length=2.35+.18*k
        width=.57 if i==3 else .31+.032*abs(k)
        planes.append((x,z,length,width))
        onset=38.36+abs(k)*.16+(k<0)*.06
        growth.append(ease((t-onset)/.65))
    cam,look,fov,roll=camera(t)
    return dict(u_cam=cam,u_look=look,u_fov=math.radians(fov),u_roll=math.radians(roll),
                u_focus=math.dist(cam,you),u_aper=.010,u_you=you,u_unfold=unfold,u_quiet=quiet,
                u_clock=clock,u_give=ease((t-34.6)/1.52),
                u_ringFade=ease((t-34.55)/.50)*(1.-ease((t-36.92)/.80)),
                u_planes=planes,u_growth=growth)

def data():
    rng=np.random.default_rng(229)
    # Regular strands preserve legible mathematical topology; tiny jitter avoids moire.
    nx,nz=320,56;x,z=np.meshgrid(np.linspace(-5.4,5.4,nx),np.linspace(-3.3,3.3,nz))
    n=x.size;result=rng.random((n,8),dtype=np.float32)
    result[:,0]=x.ravel();result[:,1]=z.ravel();result[:,2]=np.repeat(np.linspace(0,1,nz),nx)
    return result

def compile_sources():
    common=(HERE/'common.glsl').read_text(encoding='utf-8')
    return '#version 330\n'+common+(HERE/'scene.glsl').read_text(encoding='utf-8'),(
        'recomposed','#version 330\n'+common+(HERE/'points.vert').read_text(encoding='utf-8'),
        (HERE/'points.frag').read_text(encoding='utf-8'),data())

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stills');ap.add_argument('--sub',type=int,default=4)
    ap.add_argument('--w',type=int,default=1920);ap.add_argument('--h',type=int,default=1080)
    args=ap.parse_args();src,sprites=compile_sources();w,h=args.w,args.h
    r=Renderer(w,h,src,subframes=args.sub)
    def frame(t):return r.frame(t,state,post=POST,sprites=sprites)
    if args.stills:
        out=HERE/'stills';out.mkdir(exist_ok=True);times=list(map(float,args.stills.split(',')))
        sheet=Image.new('RGB',(1280,384*math.ceil(len(times)/2)),(15,16,18));draw=ImageDraw.Draw(sheet)
        font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',19)
        for i,t in enumerate(times):
            pixels=frame(t);save_png(pixels,w,h,out/f'{t:07.3f}.png')
            im=Image.frombytes('RGB',(w,h),pixels).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            sheet.paste(im.resize((640,360),Image.Resampling.LANCZOS),(i%2*640,i//2*384))
            draw.text((i%2*640+12,i//2*384+361),f'{t:.2f}s',font=font,fill=(222,217,204))
            print('still',t,flush=True)
        sheet.save(HERE/'design_contact_sheet.jpg',quality=94);return
    output=HERE/'tangent_space_v2_1080p60.mp4';duration=END-START;n=round(duration*FPS)
    cmd=[str(FFMPEG),'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pixel_format','rgb24',
         '-video_size',f'{w}x{h}','-framerate',str(FPS),'-i','pipe:0','-i',str(SONG),
         '-filter_complex',f'[1:a:0]atrim=start={START}:duration={duration},asetpts=PTS-STARTPTS[a]',
         '-map','0:v:0','-map','[a]','-vf','vflip,format=yuv420p','-c:v','h264_nvenc','-preset','p5',
         '-rc','vbr','-cq','18','-b:v','25M','-c:a','aac','-b:a','320k','-t',str(duration),
         '-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','+faststart',str(output)]
    start=time.monotonic()
    with (HERE/'encode.log').open('w') as log:
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=log,stderr=log)
        try:
            for i in range(n):
                if i%60==0:print(f'{i}/{n} frames | {time.monotonic()-start:.1f}s',flush=True)
                proc.stdin.write(frame(START+i/FPS))
            proc.stdin.close()
            if proc.wait():raise RuntimeError('Encoding failed; see encode.log')
        except BaseException:
            if proc.poll() is None:proc.kill()
            proc.wait();raise
    (HERE/'render_manifest.json').write_text(json.dumps(dict(source_start=START,source_end=END,fps=FPS,
        frames=n,duration=n/FPS,size=[w,h],elapsed=time.monotonic()-start,subframes=args.sub,
        design='Recomposed point body, circumferential hand-off, unfolding wave landscape and seven translucent tangent planes; camera moves into recipient space.',
        implementation='New scene, point topology, camera and choreography; original engine reused as an independent snapshot.'),indent=2),encoding='utf-8')
    print('done',output,flush=True)
if __name__=='__main__':main()
