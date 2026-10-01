"""The recipient leaves the wave; its position becomes the limit of a point stream."""
from __future__ import annotations
import sys
sys.dont_write_bytecode=True
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'train_cel_test/_vendor'))
sys.path.insert(0,str(HERE/'engine'))
import argparse,importlib.util,json,math,subprocess,time
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from gl import Renderer,save_png,FFMPEG,SONG
sys.path.insert(0,str(ROOT/'circle_tangent_v5'))
import dynamics
# Extend the same contact simulation in memory to observe the actual edge release.
dynamics.END=41.4
spec=importlib.util.spec_from_file_location('previous_scene',ROOT/'circle_tangent_v5/render.py')
PREVIOUS=importlib.util.module_from_spec(spec);spec.loader.exec_module(PREVIOUS)
START,END,FPS=39.0,44.45,60
T_INF,T_BE,T_LIM=40.706,42.346,43.507
RELEASE=next(e['time'] for e in PREVIOUS.MODEL.transitions if e['time']>40.7 and e['to']==-1)
RELEASE_ROW=PREVIOUS.MODEL.sample(RELEASE)
P0,V0=RELEASE_ROW[1:4].copy(),RELEASE_ROW[4:7].copy()
FLOW_DIRECTION=V0.copy();FLOW_DIRECTION[1]=0.;FLOW_DIRECTION/=np.linalg.norm(FLOW_DIRECTION)
FLOW_SIDE=np.cross(FLOW_DIRECTION,[0.,1.,0.])
ACCELERATION=np.array([0.,-PREVIOUS.GRAVITY,0.])
CAMERA_LAG=.20
CAMERA_RELEASE,LOOK_RELEASE,FOV_RELEASE,_=PREVIOUS.camera(RELEASE,1)
VIEW_DIRECTION=(np.array(LOOK_RELEASE)-CAMERA_RELEASE)
VIEW_DIRECTION/=np.linalg.norm(VIEW_DIRECTION)
POST=PREVIOUS.POST
ease,smoother=PREVIOUS.ease,PREVIOUS.smoother

def rotation(axis,angle):
    axis=np.asarray(axis,dtype=float);axis/=np.linalg.norm(axis)
    x,y,z=axis;c=math.cos(angle);s=math.sin(angle)
    cross=np.array([[0.,-z,y],[z,0.,-x],[-y,x,0.]])
    return np.eye(3)*c+(1.-c)*np.outer(axis,axis)+s*cross

def row_activation(row):
    transverse=((row%7-3)*.20,(row//7-3.5)*.19)
    extent=max(abs(transverse[0])/.72,abs(transverse[1])/.80)+.012
    low,high=T_BE,T_LIM
    for _ in range(40):
        mid=(low+high)*.5
        if smoother((mid-T_BE)/(T_LIM-T_BE))**.85<extent:low=mid
        else:high=mid
    return high

ROW_ACTIVATION=[row_activation(i) for i in range(56)]

def recipient(t):
    if t<=RELEASE:return PREVIOUS.MODEL.sample(t)[1:4]
    dt=t-RELEASE
    # Continue the actual release velocity under the SAME gravity as the waves.
    return P0+V0*dt+.5*ACCELERATION*dt*dt

def tracking_camera(t):
    if t<=RELEASE:return PREVIOUS.camera(t,1)[:3]
    dt=t-RELEASE
    # Velocity-following camera. Its speed approaches the ball's speed from below;
    # it never overtakes the ball to force it back into a preset screen position.
    tracked_time=dt-CAMERA_LAG*(-math.expm1(-dt/CAMERA_LAG))
    translation=V0*tracked_time+.5*ACCELERATION*dt*dt
    cam=np.array(CAMERA_RELEASE)+translation
    look=np.array(LOOK_RELEASE)+translation
    # Lift the viewing angle around the recipient, preserving its projection.
    # The camera must not use its orbit as a reason to drag the ball backwards.
    amount=smoother(dt/1.65)
    right=PREVIOUS.basis(CAMERA_RELEASE,LOOK_RELEASE)[:,0]
    orbit=rotation([0.,1.,0.],.52*amount)@rotation(right,.34*amount)
    you=recipient(t)
    cam=you+orbit@(cam-you);look=you+orbit@(look-you)
    return cam,look,FOV_RELEASE

def state(t):
    state=PREVIOUS.state(t,1)
    progress=max(0.,min(1.,(t-40.84)/1.36))
    you=recipient(t)
    if t>RELEASE:
        state['u_activePlane']=-1;state['u_landed']=0.
    state['u_you']=you
    state['u_growth']=[v*(1.-smoother((t-RELEASE)/.58)) for v in state['u_growth']]
    cam,look,fov=tracking_camera(t)
    dt=max(0.,t-RELEASE)
    free_fall=.5*ACCELERATION*dt*dt
    # World-space advection has its own constant launch velocity. The distant
    # cloud is never repositioned from the current recipient position.
    stream_origin=P0+(V0+3.*FLOW_DIRECTION)*dt+free_fall
    state.update(u_cam=cam,u_look=look,u_fov=math.radians(fov),
                 u_focus=float(np.linalg.norm(cam-you)),u_aper=.010,
                 u_stretch=progress,u_limit=smoother((t-T_BE)/(T_LIM-T_BE))**.85,
                 u_flowDir=FLOW_DIRECTION,u_flowSide=FLOW_SIDE,
                 u_streamOrigin=stream_origin,u_freeFall=free_fall,
                 u_releasePoint=P0,u_releaseTime=RELEASE,u_rowActivation=ROW_ACTIVATION,
                 u_planeExtent=(.72,.80),u_limitPulse=math.exp(-max(0.,t-T_LIM)*6.) if t>=T_LIM else 0.)
    return state

def compile_sources():
    common=(HERE/'common.glsl').read_text(encoding='utf-8')
    return '#version 330\n'+common+(HERE/'scene.glsl').read_text(encoding='utf-8'),(
        'infinity','#version 330\n'+common+(HERE/'points.vert').read_text(encoding='utf-8'),
        (HERE/'points.frag').read_text(encoding='utf-8'),PREVIOUS.data())

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stills');ap.add_argument('--sub',type=int,default=4)
    ap.add_argument('--w',type=int,default=1920);ap.add_argument('--h',type=int,default=1080)
    args=ap.parse_args();src,sprites=compile_sources();w,h=args.w,args.h
    renderer=Renderer(w,h,src,subframes=args.sub)
    def frame(t):return renderer.frame(t,state,post=POST,sprites=sprites)
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
    output=HERE/'infinity_limit_v2_1080p60.mp4';n=round((END-START)*FPS)
    cmd=[str(FFMPEG),'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pixel_format','rgb24',
         '-video_size',f'{w}x{h}','-framerate',str(FPS),'-i','pipe:0','-i',str(SONG),
         '-filter_complex',f'[1:a:0]atrim=start={START}:duration={n/FPS},asetpts=PTS-STARTPTS[a]',
         '-map','0:v:0','-map','[a]','-vf','vflip,format=yuv420p','-c:v','h264_nvenc','-preset','p5',
         '-rc','vbr','-cq','18','-b:v','25M','-c:a','aac','-b:a','320k','-t',str(n/FPS),
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
        design='Ballistic recipient with conserved horizontal momentum; velocity-following camera; independently advected point field decelerating only at the moving boundary.',
        action_times=dict(infinity=T_INF,physical_edge_release=RELEASE,boundary_start=T_BE,boundary_complete=T_LIM),
        point_count=len(PREVIOUS.data()),source_method='Code-authored OpenGL only; original local audio, no lyrics or parameter overlays.'),indent=2),encoding='utf-8')
    print('done',output,flush=True)
if __name__=='__main__':main()
