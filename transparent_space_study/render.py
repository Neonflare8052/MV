"""8-second 3D study: translucent depth slices and a delayed geometric memory."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'train_cel_test/_vendor'))
sys.path.insert(0,str(HERE/'base/engine'))
import argparse, importlib.util, hashlib, json, subprocess, time
from PIL import Image, ImageDraw, ImageFont
from gl import Renderer, save_png, FFMPEG, SONG

START,END,FPS=33.,41.,60

def load():
    path=HERE/'base/film/shots/s03_self.py'
    spec=importlib.util.spec_from_file_location('transparent_self',path)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    helper=(HERE/'background.glsl').read_text(encoding='utf-8')
    src=mod.SRC.replace('void main(){',helper+'\nvoid main(){',1)
    old='vec3 col=vec3(.004,.004,.005);'
    if src.count(old)!=1: raise RuntimeError('Unexpected snapshot shader layout')
    src=src.replace(old,'vec3 col=studyBackground(ro,rd);',1)
    return mod,src

def encode(path,w,h,frames,duration):
    # Accurate audio trimming preserves the MP3 decoder's reservoir history.
    cmd=[str(FFMPEG),'-y','-hide_banner','-loglevel','error',
         '-f','rawvideo','-pixel_format','rgb24','-video_size',f'{w}x{h}',
         '-framerate',str(FPS),'-i','pipe:0','-i',str(SONG),
         '-filter_complex',f'[1:a:0]atrim=start={START:.9f}:duration={duration:.9f},asetpts=PTS-STARTPTS[a]',
         '-map','0:v:0','-map','[a]','-vf','vflip,format=yuv420p',
         '-c:v','h264_nvenc','-preset','p5','-rc','vbr','-cq','18','-b:v','20M',
         '-c:a','aac','-b:a','320k','-t',f'{duration:.9f}',
         '-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',
         '-movflags','+faststart',str(path)]
    log=HERE/'encode.log'
    with log.open('w',encoding='utf-8') as errors:
        process=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=errors,stdout=errors)
        try:
            for frame in frames: process.stdin.write(frame)
            process.stdin.close()
            if process.wait(): raise RuntimeError('Encoding failed; see encode.log')
        except BaseException:
            if process.poll() is None: process.kill()
            process.wait()
            raise

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--w',type=int,default=1920); ap.add_argument('--h',type=int,default=1080)
    ap.add_argument('--sub',type=int,default=4); ap.add_argument('--stills')
    ap.add_argument('--background',type=float,default=1.4)
    ap.add_argument('--ghost',type=float,default=1.)
    ap.add_argument('--compare',action='store_true')
    ap.add_argument('--out',default='transparent_space_1080p60.mp4')
    a=ap.parse_args(); mod,src=load()
    r=Renderer(a.w,a.h,src,subframes=a.sub)
    sprites=('math',mod.SPRITE_VS,mod.SPRITE_FS,mod.SPRITE_DATA)
    empty=Image.new('RGBA',(a.w,a.h),(0,0,0,0))
    def render(t,background=a.background,ghost=a.ghost):
        def params(tt):
            p=mod.params(tt)
            return {**p,'u_bgStrength':background,'u_ghostStrength':ghost}
        return r.frame(t,params,lambda tt:{'u_ui':empty},post=mod.POST,sprites=sprites)
    if a.stills:
        dest=HERE/'stills'; dest.mkdir(exist_ok=True)
        for t in map(float,a.stills.split(',')):
            data=render(t)
            save_png(data,a.w,a.h,dest/f'{t:07.3f}.png')
            if a.compare:
                base=render(t,0.,0.)
                comparison=Image.new('RGB',(a.w*2,a.h+48),(15,16,16))
                for x,d in [(0,base),(a.w,data)]:
                    img=Image.frombytes('RGB',(a.w,a.h),d).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
                    comparison.paste(img,(x,48))
                draw=ImageDraw.Draw(comparison)
                f=ImageFont.truetype('C:/Windows/Fonts/CascadiaMono.ttf',26)
                draw.text((24,9),f'BASE / {t:.2f}s',font=f,fill=(220,217,207))
                draw.text((a.w+24,9),'TRANSLUCENT SPACE + DELAYED FORM',font=f,fill=(220,217,207))
                comparison.save(HERE/f'compare_{t:06.2f}.jpg',quality=94)
            print('still',t,flush=True)
        return
    n=round((END-START)*FPS); started=time.monotonic()
    def frames():
        for i in range(n):
            if i%60==0: print(f'{i}/{n} frames | {time.monotonic()-started:.1f}s',flush=True)
            yield render(START+i/FPS)
    out=Path(a.out)
    if not out.is_absolute(): out=HERE/out
    encode(out,a.w,a.h,frames(),n/FPS)
    manifest={'output':str(out),'width':a.w,'height':a.h,'fps':FPS,'frames':n,'duration':n/FPS,
              'source_start':START,'source_end':END,'subframes':a.sub,
              'background_strength':a.background,'memory_strength':a.ghost,
              'camera':'Original s03 continuous camera','annotations':'None; no lyric captions or parameter labels',
              'effects':'3D finite translucent slices, sparse geometric fragments, delayed circle-to-wave arcs',
              'elapsed_seconds':round(time.monotonic()-started,2),
              'study_sources':{name:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in ['render.py','background.glsl']}}
    (HERE/'render_manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print('done',out,flush=True)

if __name__=='__main__': main()
