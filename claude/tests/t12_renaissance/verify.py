"""Verify the delivered encoding and original-audio alignment."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import hashlib, json, subprocess, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
FF=ROOT/'tools/ffmpeg.exe'; PROBE=ROOT/'tools/ffprobe.exe'
SONG=ROOT/'Mili - world.execute (me) ;.mp3'
MOVIE=HERE/'t12_renaissance_v1_1080p60.mp4'
START,DURATION,FPS=122.5,19.,60
QA=HERE/'qa'; QA.mkdir(exist_ok=True)

def run(cmd):
    return subprocess.run([str(x) for x in cmd],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

meta=json.loads(run([PROBE,'-v','error','-show_streams','-show_format','-of','json',MOVIE]).stdout)
video=next(s for s in meta['streams'] if s['codec_type']=='video')
audio=next(s for s in meta['streams'] if s['codec_type']=='audio')
checks={
    '1920x1080':(video['width'],video['height'])==(1920,1080),
    '60fps':video['avg_frame_rate']=='60/1',
    '1140_frames':int(video['nb_frames'])==1140,
    '19_seconds':abs(float(video['duration'])-DURATION)<.02,
    'stereo_audio':audio['channels']==2,
    'audio_duration':abs(float(audio['duration'])-DURATION)<.04,
}
run([FF,'-hide_banner','-loglevel','error','-xerror','-i',MOVIE,'-map','0:v:0','-map','0:a:0','-f','null','NUL'])
checks['full_decode']=True

def pcm(path,start,label):
    wav=QA/f'{label}.wav'
    # Decode from the head, retaining MP3 reservoir history before trimming.
    run([FF,'-y','-hide_banner','-loglevel','error','-i',path,'-ss',start,'-t',.65,'-vn','-ac','1','-ar',16000,'-c:a','pcm_s16le',wav])
    with wave.open(str(wav),'rb') as f:
        return np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(np.float64)/32768.

alignment=[]
for offset in [.5,9.,17.8]:
    source=pcm(SONG,START+offset,f'source_{offset}')
    output=pcm(MOVIE,offset,f'output_{offset}')
    n=min(len(source),len(output));source=source[:n];output=output[:n]
    best=(-2.,0)
    for lag in range(-320,321):
        if lag>0:a,b=source[:-lag],output[lag:]
        elif lag<0:a,b=source[-lag:],output[:lag]
        else:a,b=source,output
        a=a-a.mean();b=b-b.mean()
        corr=float(np.dot(a,b)/max(np.linalg.norm(a)*np.linalg.norm(b),1e-15))
        if corr>best[0]:best=(corr,lag)
    alignment.append(dict(clip_time=offset,source_time=START+offset,correlation=best[0],lag_ms=best[1]/16.))
checks['audio_alignment']=all(x['correlation']>.98 and abs(x['lag_ms'])<=1 for x in alignment)

times=[124.95,125.75,126.20,127.50,129.30,130.50,131.55,132.30,133.25,134.65,137.3,140.8]
cw,ch,cols=640,360,3
sheet=Image.new('RGB',(cw*cols,(ch+30)*4),(19,19,19));d=ImageDraw.Draw(sheet)
font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',20)
for i,t in enumerate(times):
    path=QA/f'encoded_{t:07.3f}.jpg'
    run([FF,'-y','-hide_banner','-loglevel','error','-ss',t-START,'-i',MOVIE,'-frames:v',1,'-q:v',2,path])
    x,y=i%cols*cw,i//cols*(ch+30)
    with Image.open(path) as im:sheet.paste(im.resize((cw,ch),Image.Resampling.LANCZOS),(x,y))
    d.text((x+10,y+ch+2),f'song {t:07.3f} s / clip {t-START:05.2f} s',font=font,fill=(231,224,206))
sheet.save(HERE/'encoded_contact_sheet.jpg',quality=94)
inputs=[SONG,HERE/'shot.py',HERE/'render.py',ROOT/'claude/engine/gl.py',ROOT/'claude/film/shots/s10_fragments.py',ROOT/'claude/film/shots/s12_exe.py']
manifest=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in inputs]
report=dict(passed=all(checks.values()),checks=checks,audio_alignment=alignment,metadata=meta,input_manifest_at_verification=manifest)
(HERE/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(passed=report['passed'],checks=checks,audio_alignment=alignment),indent=2),flush=True)
if not report['passed']:raise SystemExit(1)
