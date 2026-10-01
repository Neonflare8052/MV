"""A continuous recipient action across two distinct mathematical shots."""
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
T_CATCH,T_RELEASE,T_CUT,T_LAND=34.58,36.287,33.4+220/60,38.78
RADIUS,ORBIT_RADIUS=.105,1.995
THETA_START=math.radians(210.)
CAMERA_A=np.array([.8,.4,8.3])
LOOK_A=np.array([0.,0.,0.])
FOV_A,FOV_B=44.,48.
POST=dict(u_bloom=.27,u_grain=.018,u_ca=.0025,u_sat=.85,u_gain=1.12)

def ease(x):
    x=max(0.,min(1.,x));return x*x*(3.-2.*x)
def blend(a,b,x):
    return tuple(u+(v-u)*x for u,v in zip(a,b))
def field(x,z,clock,quiet,dip=0.):
    a=1.19*x+.40*z-clock;b=2.12*x-.27*z+clock*.34
    h=.68*math.sin(a)+.18*math.sin(b)
    dx=.8092*math.cos(a)+.3816*math.cos(b)
    dz=.272*math.cos(a)-.0486*math.cos(b)
    calm=quiet*math.exp(-((x-.70)/1.65)**2-(z/3.8)**4)
    cx=calm*(-2.*(x-.70)/1.65**2);cz=calm*(-4.*z**3/3.8**4)
    rest=.24+dip
    return h*(1-calm)+rest*calm,dx*(1-calm)+(rest-h)*cx,dz*(1-calm)+(rest-h)*cz

def basis(cam,look):
    forward=np.array(look)-np.array(cam);forward/=np.linalg.norm(forward)
    right=np.cross(forward,[0.,1.,0.]);right/=np.linalg.norm(right)
    up=np.cross(right,forward)
    return np.array([right,up,forward]).T

def orbit(t):
    u=max(0.,min(1.,(t-T_CATCH)/(T_RELEASE-T_CATCH)))
    phase=u+.06*(u*u-u)
    angle=THETA_START+math.pi*phase
    speed=ORBIT_RADIUS*math.pi*(.94+.12*u)/(T_RELEASE-T_CATCH)
    p=np.array([ORBIT_RADIUS*math.cos(angle),ORBIT_RADIUS*math.sin(angle),0.])
    v=np.array([-math.sin(angle),math.cos(angle),0.])*speed
    return p,v,angle

def incoming(t):
    p0=np.array([-7.4,2.6,1.3]);v0=np.array([5.9,-1.6,-.6])
    p1,v1,_=orbit(T_CATCH);duration=T_CATCH-START
    u=max(0.,min(1.,(t-START)/duration))
    return ((2*u**3-3*u*u+1)*p0+(u**3-2*u*u+u)*duration*v0
            +(-2*u**3+3*u*u)*p1+(u**3-u*u)*duration*v1)

def exit_flight(t):
    p,v,_=orbit(T_RELEASE);dt=t-T_RELEASE
    return p+v*dt+np.array([0.,-1.5*dt*dt,0.]),v+np.array([0.,-3.*dt,0.])

def matched_cut():
    """Change camera/space while retaining screen position, velocity and apparent size."""
    p,v=exit_flight(T_CUT);b1=basis(CAMERA_A,LOOK_A)
    cam=np.array([-1.5,2.7,6.2]);look=np.array([.7,.12,0.]);b2=basis(cam,look)
    # Scaling only camera-depth by this ratio preserves screen position and size.
    ratio=math.tan(math.radians(FOV_A/2))/math.tan(math.radians(FOV_B/2))
    q=b1.T@(p-CAMERA_A);velocity=b1.T@v
    q[2]*=ratio;velocity[2]*=ratio
    p2=cam+b2@q;v2=b2@velocity;remaining=T_LAND-T_CUT
    predicted=p2+v2*remaining
    shift=np.array([.70-predicted[0],0.,-predicted[2]])
    cam+=shift;look+=shift;p2+=shift
    gravity=2*(p2[1]+v2[1]*remaining-(.24+RADIUS))/remaining**2
    return cam,look,p2,v2,gravity

CAMERA_B,LOOK_B,CUT_POSITION,CUT_VELOCITY,GRAVITY=matched_cut()

def camera(t,shot):
    if shot==0:return CAMERA_A,LOOK_A,FOV_A,0.
    keys=[(T_CUT,CAMERA_B,LOOK_B,FOV_B),
          (37.35,CAMERA_B,LOOK_B,FOV_B),
          (38.78,np.array([.3,2.35,6.2]),np.array([.7,.40,.1]),48.),
          (40.7,np.array([.45,1.85,4.0]),np.array([.7,.30,-.35]),46.)]
    if t<=keys[0][0]:return keys[0][1],keys[0][2],keys[0][3],0.
    for a,b in zip(keys,keys[1:]):
        if t<=b[0]:
            k=ease((t-a[0])/(b[0]-a[0]))
            return blend(a[1],b[1],k),blend(a[2],b[2],k),a[3]+(b[3]-a[3])*k,0.
    return keys[-1][1],keys[-1][2],keys[-1][3],0.

def impact_dip(t):
    dt=t-T_LAND
    return -.095*(dt/.09)*math.exp(1.-dt/.09) if dt>=0. else 0.

def state(t,shot=None):
    if shot is None:shot=int(t>=T_CUT)
    unfold=float(shot)
    quiet=ease((t-38.04)/.62)
    clock=(t-37.067)*1.13+.35
    dip=impact_dip(t)
    if shot==0:
        if t<T_CATCH:you=incoming(t)
        elif t<=T_RELEASE:you=orbit(t)[0]
        else:you=exit_flight(t)[0]
    elif t<T_LAND:
        dt=t-T_CUT
        you=CUT_POSITION+CUT_VELOCITY*dt+np.array([0.,-.5*GRAVITY*dt*dt,0.])
    else:
        you=np.array([.7,.24+RADIUS+dip,0.])
    planes=[];growth=[]
    for i in range(7):
        k=i-3;z=k*1.34;x=.70+.12*math.sin(k*1.20)
        length=2.40+.20*k
        width=.62 if i==3 else .46
        planes.append((x,z,length,width))
        onset={3:38.20,2:39.00,4:39.22}.get(i,999.)
        growth.append(ease((t-onset)/.52) if shot else 0.)
    cam,look,fov,roll=camera(t,shot)
    _,_,angle=orbit(t)
    ring_contact=(ease((t-T_CATCH)/.055)*(1.-ease((t-T_RELEASE)/.23))) if shot==0 else 0.
    return dict(u_cam=cam,u_look=look,u_fov=math.radians(fov),u_roll=math.radians(roll),
                u_focus=math.dist(cam,you),u_aper=.010,u_you=you,u_unfold=unfold,u_quiet=quiet,
                u_clock=clock,u_give=ease((t-33.64)/.86),
                u_ringFade=ease((t-33.55)/.70) if shot==0 else 0.,
                u_planes=planes,u_growth=growth,u_dip=dip,u_contactAngle=angle,
                u_ringContact=ring_contact,u_catchPulse=math.exp(-(t-T_CATCH)*10.) if t>=T_CATCH else 0.,
                u_landed=ease((t-T_LAND)/.045),u_impact=math.exp(-(t-T_LAND)*4.) if t>=T_LAND else 0.)

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
    # A shutter must never sample the other shot: the cut has no dissolving circle.
    def frame(t):return r.frame(t,lambda tt:state(tt,int(t>=T_CUT)),post=POST,sprites=sprites)
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
    output=HERE/'circle_tangent_v3_1080p60.mp4';duration=END-START;n=round(duration*FPS)
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
        design='External approach, circumference capture, exact half orbit, tangential release, motion-matched hard cut, airborne descent and softly yielding tangent support.',
        action_times=dict(catch=T_CATCH,release=T_RELEASE,cut=T_CUT,landing=T_LAND),
        implementation='Independent copy of the previous renderer; new two-shot motion and camera choreography. Four motion-blur samples stay within each shot.'),indent=2),encoding='utf-8')
    print('done',output,flush=True)
if __name__=='__main__':main()
