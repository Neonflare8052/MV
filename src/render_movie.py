"""Deterministic GPU frame capture; native 4K60, no desktop capture or frame interpolation."""
from pathlib import Path
import argparse,sys,time,subprocess,json,math,hashlib
from canvas import Canvas
ROOT=Path(__file__).resolve().parents[1]
FFMPEG=ROOT/'tools'/'ffmpeg.exe'
FFPROBE=FFMPEG.with_name('ffprobe.exe')
SOURCE=next(ROOT.glob('*.mp3'))

def probe_duration():
    p=subprocess.run([str(FFPROBE),'-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(SOURCE)],capture_output=True,text=True)
    return float(next(x for x in p.stdout.splitlines() if x.strip().replace('.','',1).isdigit()))

def draw(c,t):
    if t<59.223:
        from act_open import draw as act
    elif t<125.708:
        from act_middle import draw as act
    else:
        from act_final import draw as act
    c.clear((0,0,0));act(c,t)

def main():
    p=argparse.ArgumentParser();p.add_argument('--width',type=int,default=3840);p.add_argument('--height',type=int,default=2160);p.add_argument('--fps',type=int,default=60);p.add_argument('--start',type=float,default=0);p.add_argument('--end',type=float);p.add_argument('--stills',type=str);p.add_argument('--output',type=str,default='output/world_execute_me_4K60.mp4');p.add_argument('--silent',action='store_true');p.add_argument('--quality',type=int,default=18);a=p.parse_args()
    c=Canvas(a.width,a.height);print('GPU:',c.ctx.info['GL_RENDERER'],flush=True)
    if a.stills:
        for t in map(float,a.stills.split(',')):
            draw(c,t);dest=ROOT/'work'/f'frame_{t:08.3f}.png';c.save(dest);print(dest,flush=True)
        return
    duration=probe_duration();end=min(a.end if a.end is not None else duration,duration);n=math.ceil((end-a.start)*a.fps)
    dest=ROOT/a.output;dest.parent.mkdir(exist_ok=True,parents=True)
    log=ROOT/'work'/f'{dest.stem}_encode.log'
    cmd=[str(FFMPEG),'-y','-hide_banner','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{a.width}x{a.height}','-framerate',str(a.fps),'-i','pipe:0']
    if not a.silent:cmd+=['-ss',str(a.start),'-i',str(SOURCE)]
    cmd+=['-map','0:v:0']
    if not a.silent:cmd+=['-map','1:a:0']
    cmd+=['-vf','vflip,scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p','-c:v','h264_nvenc','-preset','p5','-tune','hq','-rc','vbr','-cq',str(a.quality),'-b:v','32M','-maxrate','65M','-bufsize','130M','-g',str(a.fps*2),'-bf','3','-profile:v','high','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709']
    if not a.silent:cmd+=['-c:a','aac','-b:a','320k']
    cmd+=['-t',str(end-a.start),'-movflags','+faststart',str(dest)]
    start=time.monotonic()
    with log.open('w',encoding='utf-8') as lf:
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=lf,stderr=lf,bufsize=1024*1024*8)
        try:
            for frame in range(n):
                t=a.start+frame/a.fps;draw(c,t);proc.stdin.write(c.read())
                if frame%max(1,a.fps*2)==0:
                    elapsed=time.monotonic()-start;fps=(frame+1)/max(elapsed,.01)
                    print(f'{frame}/{n} t={t:.3f} rate={fps:.1f}fps remaining={(n-frame)/max(fps,.01):.0f}s',flush=True)
            proc.stdin.close();code=proc.wait()
            if code:raise RuntimeError(f'encoder exit {code}: {log}')
        except BaseException:
            try:proc.stdin.close()
            except:pass
            proc.terminate();raise
    manifest={'source':SOURCE.name,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'output':str(dest),'width':a.width,'height':a.height,'fps':a.fps,'frames':n,'duration':end-a.start,'render_seconds':time.monotonic()-start,'gpu':c.ctx.info['GL_RENDERER'],'method':'deterministic native OpenGL frame recording, instanced 3D + GPU 2D; no interpolation','audio':'original supplied MP3, AAC 320 kb/s encode; no edits'}
    (ROOT/'output'/'render_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(manifest,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
