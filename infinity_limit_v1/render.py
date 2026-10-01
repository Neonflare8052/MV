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
POST=PREVIOUS.POST
ease,smoother=PREVIOUS.ease,PREVIOUS.smoother

def recipient(t):
    if t<=RELEASE:return PREVIOUS.MODEL.sample(t)[1:4]
    dt=t-RELEASE
    # Continuous velocity at the edge; the rising tangent launches a shallow arc.
    horizontal=V0.copy();horizontal[1]=0.
    p=P0+horizontal*(-math.expm1(-.86*dt))/.86
    p[1]+=V0[1]*dt*math.exp(-2.1*dt)
    return p

def state(t):
    state=PREVIOUS.state(t,1)
    progress=max(0.,min(1.,(t-40.84)/1.36))
    you=recipient(t)
    if t>RELEASE:
        state['u_activePlane']=-1;state['u_landed']=0.
    state['u_you']=you
    state['u_growth']=[v*(1.-smoother((t-RELEASE)/.58)) for v in state['u_growth']]
    cam0,look0,fov0,_=PREVIOUS.camera(min(t,40.7),1)
    blend=smoother((t-40.82)/1.78)
    final=smoother((t-T_BE)/(T_LIM-T_BE))
    target_cam=you+np.array([4.75+.25*final,.80,4.5])
    target_look=you+np.array([-2.70,0.,0.])
    cam=np.array(cam0)*(1.-blend)+target_cam*blend
    look=np.array(look0)*(1.-blend)+target_look*blend
    state.update(u_cam=cam,u_look=look,u_fov=math.radians(fov0*(1.-blend)+43.*blend),
                 u_focus=float(np.linalg.norm(cam-you)),u_aper=.010,
                 u_stretch=progress,u_limit=smoother((t-T_BE)/(T_LIM-T_BE))**.85,
                 u_flowDir=FLOW_DIRECTION,u_flowSide=FLOW_SIDE,
                 u_planeExtent=(1.13,1.25),u_limitPulse=math.exp(-max(0.,t-T_LIM)*6.) if t>=T_LIM else 0.)
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
    output=HERE/'infinity_limit_v1_1080p60.mp4';n=round((END-START)*FPS)
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
        design='The same point waves stretch toward the horizon. The moving recipient grows a transverse plane that becomes the asymptotic limit of the approaching stream.',
        action_times=dict(infinity=T_INF,physical_edge_release=RELEASE,boundary_start=T_BE,boundary_complete=T_LIM),
        point_count=len(PREVIOUS.data()),source_method='Code-authored OpenGL only; original local audio, no lyrics or parameter overlays.'),indent=2),encoding='utf-8')
    print('done',output,flush=True)
if __name__=='__main__':main()
