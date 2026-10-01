import sys
sys.dont_write_bytecode=True
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'train_cel_test/_vendor'))
sys.path.insert(0,str(HERE/'base/engine'))
import argparse, importlib.util, math, json, subprocess, time
from PIL import Image
from gl import Renderer,save_png,FFMPEG,SONG
START,END,FPS=35.,40.7,60
def ease(x):
    x=max(0.,min(1.,x)); return x*x*(3.-2.*x)
def mix(a,b,x):return tuple(u+(v-u)*x for u,v in zip(a,b))
def load():
    spec=importlib.util.spec_from_file_location('support_base',HERE/'base/film/shots/s03_self.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    s=m.SRC.replace('void main(){',(HERE/'support.glsl').read_text(encoding='utf-8')+'\nvoid main(){',1)
    s=s.replace('vec3 col=vec3(.004,.004,.005);','vec3 col=supportScene(ro,rd);')
    return m,s
def state(m,t):
    p=m.params(t)
    transition=ease((t-37.1)/1.35)
    travel=ease((t-39.05)/1.5)
    x=-.85+1.65*travel
    y=m.wave_y(x,18,t)
    slope=.595*math.cos(1.7*x+3.96-(t-37.067)*1.2)+.396*math.cos(3.3*x-2.7)
    norm=math.sqrt(1.+slope*slope)
    landing=ease((t-38.60)/.43)
    radius=.072
    above=radius+.72*(1.-landing)
    target=(x-slope/norm*above,y+above/norm,-.123076923)
    recipient=mix((0.,1.1,0.),target,transition)
    cam=mix((.3,1.65,5.2),(.55,1.38,4.85),ease((t-36.9)/2.3))
    look=mix((0.,1.1,0.),(.08,.72,-.12),ease((t-37.05)/1.65))
    sp=list(p['u_sp']);sp[0]=recipient
    p.update(u_cam=cam,u_look=look,u_fov=math.radians(43),u_roll=0.,
             u_focus=math.dist(cam,recipient),u_aper=.007,u_sp=sp,u_you=recipient,u_youHide=1.,
             u_tan=0.,u_e0=.28,u_recipient=recipient,u_contactX=x,
             u_offer=ease((t-38.43)/.25),u_landed=landing,
             u_touch=math.exp(-(t-39.03)*6.) if t>=39.03 else 0.)
    return p
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stills');ap.add_argument('--sub',type=int,default=4)
    args=ap.parse_args();w,h=1920,1080;m,src=load();r=Renderer(w,h,src,subframes=args.sub)
    sprites=('points',m.SPRITE_VS,m.SPRITE_FS,m.SPRITE_DATA)
    blank=Image.new('RGBA',(w,h),(0,0,0,0))
    def frame(t):return r.frame(t,lambda tt:state(m,tt),lambda tt:{'u_ui':blank},post=m.POST,sprites=sprites)
    if args.stills:
        (HERE/'stills').mkdir(exist_ok=True)
        for t in map(float,args.stills.split(',')):
            save_png(frame(t),w,h,HERE/'stills'/f'{t:07.3f}.png');print('still',t,flush=True)
        return
    output=HERE/'tangent_support_1080p60.mp4';duration=END-START
    cmd=[str(FFMPEG),'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pixel_format','rgb24',
         '-video_size',f'{w}x{h}','-framerate',str(FPS),'-i','pipe:0','-i',str(SONG),
         '-filter_complex',f'[1:a:0]atrim=start={START}:duration={duration},asetpts=PTS-STARTPTS[a]',
         '-map','0:v:0','-map','[a]','-vf','vflip,format=yuv420p','-c:v','h264_nvenc','-preset','p5',
         '-rc','vbr','-cq','18','-b:v','20M','-c:a','aac','-b:a','320k','-t',str(duration),
         '-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','+faststart',str(output)]
    n=round(duration*FPS);start=time.monotonic()
    with (HERE/'encode.log').open('w') as log:
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=log,stderr=log)
        for i in range(n):
            if i%60==0:print(f'{i}/{n}',flush=True)
            proc.stdin.write(frame(START+i/FPS))
        proc.stdin.close()
        if proc.wait():raise RuntimeError('Encoding failed')
    (HERE/'render_manifest.json').write_text(json.dumps({'source_start':START,'source_end':END,'fps':FPS,
        'frames':n,'duration':n/FPS,'size':[w,h],'elapsed':time.monotonic()-start,
        'design':'Point-cloud AI supplies an exact local vector tangent; recipient descends to it and moves while supported.',
        'source_files':'Preserved; all study changes are local.'},indent=2),encoding='utf-8')
    print('done',output)
if __name__=='__main__':main()
