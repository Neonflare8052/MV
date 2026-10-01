"""Complete 16 s audio visualization through a continuous AC to DC handoff."""
from __future__ import annotations
import sys
sys.dont_write_bytecode=True
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'train_cel_test/_vendor'))
sys.path.insert(0,str(HERE/'engine'))
import argparse,importlib.util,json,math,subprocess,time
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from gl import Renderer,save_png,FFMPEG,SONG

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

INFINITY=load(ROOT/'infinity_limit_v2/render.py','accepted_infinity')
CIRCLE=INFINITY.PREVIOUS
SELF=load(ROOT/'claude/film/shots/s03_self.py','source_self')
SOURCE_MOVIE=ROOT/'claude/film/film_full_v1_1080p.mp4'
START,END,FPS=16.,47.+40/60,60
PREFIX_END=29.7
BRIDGE_START,BRIDGE_END=32.70,33.40
T_SWITCH,T_DC,DC_DURATION=44.452,46.50,.36
smoother=INFINITY.smoother

# Integrate the actual signed current. AC reversals retain continuous position;
# a driven transition changes its velocity to positive DC, rather than stopping it.
CURRENT_T=np.arange(T_SWITCH,END+.05,1/2400.)
DC_BLEND=np.array([smoother((t-T_DC)/DC_DURATION) for t in CURRENT_T])
CURRENT_SPEED=(1.-DC_BLEND)*1.65*np.sin(2.*math.pi*2.0*(CURRENT_T-44.72))+DC_BLEND*1.65
CURRENT_S=np.zeros(len(CURRENT_T))
CURRENT_S[1:]=np.cumsum((CURRENT_SPEED[1:]+CURRENT_SPEED[:-1])*.5/2400.)

def ac_state(t):
    s=INFINITY.state(t)
    unfold=smoother((t-T_SWITCH)/.94)
    dc=smoother((t-T_DC)/DC_DURATION)
    travel=float(np.interp(t,CURRENT_T,CURRENT_S))
    speed=float(np.interp(t,CURRENT_T,CURRENT_SPEED))
    if unfold>0.:
        you=s['u_you'];right=CIRCLE.basis(s['u_cam'],s['u_look'])[:,0]
        orbit=INFINITY.rotation(right,-.30*unfold)
        s['u_cam']=you+orbit@(s['u_cam']-you)
        s['u_look']=you+orbit@(s['u_look']-you)
        s['u_focus']=float(np.linalg.norm(s['u_cam']-you))
    s.update(u_switch=unfold,u_dc=dc,u_currentTravel=travel,u_currentSpeed=speed,
             u_signalClock=(t-44.72)*2.*math.pi*2.)
    return s

def bridge_state(t):
    p=SELF.params(t);u=smoother((t-BRIDGE_START)/(BRIDGE_END-BRIDGE_START))
    target=CIRCLE.state(BRIDGE_END,0)
    for key in ('u_cam','u_look'):
        p[key]=tuple(np.asarray(p[key])*(1.-u)+np.asarray(target[key])*u)
    for key in ('u_fov','u_roll','u_focus','u_aper'):
        p[key]=p.get(key,0.)*(1.-u)+target[key]*u
    p['u_bridge']=u;p['u_axes']*=1.-u;p['u_spoke']*=1.-u
    return p

def bridge_post(t):
    base=dict(u_bloom=.6,u_grain=.035,u_ca=.012,u_sat=1.,u_gain=1.,**{})
    base.update(SELF.POST)
    u=smoother((t-BRIDGE_START)/(BRIDGE_END-BRIDGE_START))
    return {k:base[k]*(1.-u)+CIRCLE.POST.get(k,base[k])*u for k in base}

def bridge_sources():
    # Duplicate only in the transition, compensating radiance per old point.
    # Every instance then moves to one of the exact accepted ring coordinates.
    new=CIRCLE.data();old=SELF.SPRITE_DATA[np.arange(len(new))%len(SELF.SPRITE_DATA)]
    data=np.concatenate([old,new],axis=1).astype('f4')
    src=SELF.SRC.replace('uniform vec2 u_res;','uniform float u_bridge;\nuniform vec2 u_res;')
    src=src.replace('vec3 col=vec3(.004,.004,.005);',
        'vec3 bg=vec3(.0026,.0031,.0040)+vec3(.002,.0023,.003)*exp(-dot(uv-vec2(.14,-.04),uv-vec2(.14,-.04))*4.);\n  vec3 col=mix(vec3(.004,.004,.005),bg,u_bridge);')
    return src,('cloud_to_circle',(HERE/'bridge.vert').read_text(),(HERE/'points.frag').read_text(),data)

def compile_sources():
    common=(HERE/'common.glsl').read_text(encoding='utf-8')
    return '#version 330\n'+common+(HERE/'scene.glsl').read_text(encoding='utf-8'),(
        'current','#version 330\n'+common+(HERE/'points.vert').read_text(encoding='utf-8'),
        (HERE/'points.frag').read_text(encoding='utf-8'),CIRCLE.data())

class Film:
    def __init__(self,w,h,sub=4):
        self.w,self.h=w,h
        self.acsrc,self.acsprites=compile_sources()
        self.circlesrc,self.circlesprites=CIRCLE.compile_sources()
        self.bridgesrc,self.bridgesprites=bridge_sources()
        self.oldsprites=('source_points',SELF.SPRITE_VS,SELF.SPRITE_FS,SELF.SPRITE_DATA)
        self.renderer=Renderer(w,h,self.acsrc,subframes=sub)

    def frame(self,t):
        r=self.renderer
        if t<BRIDGE_START:
            r.use('points',SELF.SRC)
            return r.frame(t,SELF.params,lambda tt:SELF.textures(tt,self.w,self.h,hide=True),post=SELF.POST,sprites=self.oldsprites)
        if t<BRIDGE_END:
            r.use('bridge',self.bridgesrc)
            return r.frame(t,bridge_state,lambda tt:SELF.textures(tt,self.w,self.h,hide=True),post=bridge_post(t),sprites=self.bridgesprites)
        if t<40.70:
            r.use('circle',self.circlesrc)
            return r.frame(t,lambda tt:CIRCLE.state(tt,int(t>=CIRCLE.T_CUT)),post=CIRCLE.POST,sprites=self.circlesprites)
        r.use('current',self.acsrc)
        return r.frame(t,ac_state,post=INFINITY.POST,sprites=self.acsprites)

def source_frames(w,h,count,log):
    cmd=[str(FFMPEG),'-hide_banner','-loglevel','error','-ss',str(START),'-i',str(SOURCE_MOVIE),
         '-map','0:v:0','-an','-frames:v',str(count),'-vf',f'scale={w}:{h}:flags=lanczos,vflip',
         '-pix_fmt','rgb24','-f','rawvideo','pipe:1']
    process=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=log)
    try:
        size=w*h*3
        for _ in range(count):
            pixels=process.stdout.read(size)
            if len(pixels)!=size:raise RuntimeError('Incomplete source visualization frame')
            yield pixels
        process.stdout.close()
        if process.wait():raise RuntimeError('Source visualization decode failed')
    finally:
        if process.poll() is None:process.kill();process.wait()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stills');ap.add_argument('--sub',type=int,default=4)
    ap.add_argument('--w',type=int,default=1920);ap.add_argument('--h',type=int,default=1080)
    args=ap.parse_args();w,h=args.w,args.h;film=Film(w,h,args.sub)
    if args.stills:
        times=list(map(float,args.stills.split(',')));out=HERE/'stills';out.mkdir(exist_ok=True)
        sheet=Image.new('RGB',(1280,384*math.ceil(len(times)/2)),(15,16,18));draw=ImageDraw.Draw(sheet)
        font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',19)
        for i,t in enumerate(times):
            pixels=film.frame(t);save_png(pixels,w,h,out/f'{t:07.3f}.png')
            im=Image.frombytes('RGB',(w,h),pixels).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            sheet.paste(im.resize((640,360),Image.Resampling.LANCZOS),(i%2*640,i//2*384))
            draw.text((i%2*640+12,i//2*384+361),f'{t:.2f}s',font=font,fill=(222,217,204))
            print('still',t,flush=True)
        sheet.save(HERE/'design_contact_sheet.jpg',quality=94);return
    output=HERE/'audio_to_acdc_v1_1080p60.mp4';n=round((END-START)*FPS);prefix=round((PREFIX_END-START)*FPS)
    cmd=[str(FFMPEG),'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pixel_format','rgb24',
         '-video_size',f'{w}x{h}','-framerate',str(FPS),'-i','pipe:0','-i',str(SONG),
         '-filter_complex',f'[1:a:0]atrim=start={START}:duration={n/FPS},asetpts=PTS-STARTPTS[a]',
         '-map','0:v:0','-map','[a]','-vf','vflip,format=yuv420p','-c:v','h264_nvenc','-preset','p5',
         '-rc','vbr','-cq','18','-b:v','25M','-c:a','aac','-b:a','320k','-t',str(n/FPS),
         '-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','+faststart',str(output)]
    start=time.monotonic()
    with (HERE/'encode.log').open('w') as log:
        process=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=log,stderr=log)
        try:
            for i,pixels in enumerate(source_frames(w,h,prefix,log)):
                if i%300==0:print(f'{i}/{n} | preserved audio visualization',flush=True)
                process.stdin.write(pixels)
            for i in range(prefix,n):
                if i%180==0:print(f'{i}/{n} | {time.monotonic()-start:.1f}s',flush=True)
                process.stdin.write(film.frame(START+i/FPS))
            process.stdin.close()
            if process.wait():raise RuntimeError('Encoding failed; see encode.log')
        except BaseException:
            if process.poll() is None:process.kill()
            process.wait();raise
    (HERE/'render_manifest.json').write_text(json.dumps(dict(source_start=START,source_end=END,fps=FPS,
        frames=n,duration=n/FPS,size=[w,h],elapsed=time.monotonic()-start,subframes=args.sub,
        segments=[['original sound visualization',START,PREFIX_END],['point dimensions and cloud-to-ring transition',PREFIX_END,BRIDGE_END],
                  ['accepted circle and tangent actions',BRIDGE_END,40.7],['accepted inertia and limitations',40.7,T_SWITCH],
                  ['hinged boundary becomes AC then DC channel',T_SWITCH,END]],
        ac_dc=dict(switch=T_SWITCH,dc_begin=T_DC,dc_settled=T_DC+DC_DURATION),
        method='Local original audio and code-authored geometry. Original visualization retained. No lyrics or numerical parameter overlays added.'),indent=2),encoding='utf-8')
    print('done',output,flush=True)
if __name__=='__main__':main()
