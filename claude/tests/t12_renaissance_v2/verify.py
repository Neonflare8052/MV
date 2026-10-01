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
MOVIE=HERE/'renaissance_love_eye_v2_1080p60.mp4'
START,DURATION,FPS=122.5,1510/60,60
QA=HERE/'qa'; QA.mkdir(exist_ok=True)

def run(cmd):
    return subprocess.run([str(x) for x in cmd],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

meta=json.loads(run([PROBE,'-v','error','-show_streams','-show_format','-of','json',MOVIE]).stdout)
video=next(s for s in meta['streams'] if s['codec_type']=='video')
audio=next(s for s in meta['streams'] if s['codec_type']=='audio')
checks={
    '1920x1080':(video['width'],video['height'])==(1920,1080),
    '60fps':video['avg_frame_rate']=='60/1',
    '1510_frames':int(video['nb_frames'])==1510,
    'duration':abs(float(video['duration'])-DURATION)<.02,
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
for offset in [.5,12.3,24.0]:
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

times=[124.95,126.40,127.90,130.50,131.60,133.40,134.97,136.50,137.70,138.50,139.40,139.80,140.60,141.60,143.20,145.50]
cw,ch,cols=480,270,4
sheet=Image.new('RGB',(cw*cols,(ch+30)*4),(19,19,19));d=ImageDraw.Draw(sheet)
font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',20)
for i,t in enumerate(times):
    path=QA/f'encoded_{t:07.3f}.jpg'
    run([FF,'-y','-hide_banner','-loglevel','error','-ss',t-START,'-i',MOVIE,'-frames:v',1,'-q:v',2,path])
    x,y=i%cols*cw,i//cols*(ch+30)
    with Image.open(path) as im:sheet.paste(im.resize((cw,ch),Image.Resampling.LANCZOS),(x,y))
    d.text((x+10,y+ch+2),f'song {t:07.3f} s / clip {t-START:05.2f} s',font=font,fill=(231,224,206))
sheet.save(HERE/'encoded_contact_sheet.jpg',quality=94)
render=json.loads((HERE/'render_manifest.json').read_text(encoding='utf-8'))
manifest=[]
for entry in render['input_manifest']:
    actual=hashlib.sha256((ROOT/entry['path']).read_bytes()).hexdigest()
    manifest.append(dict(**entry,actual_sha256=actual,unchanged=entry['sha256']==actual))
checks['render_inputs_unchanged']=all(e['unchanged'] for e in manifest)
import terminal as T
audit=T.audit();responses=audit['responses']
checks['responses_are_causal_and_fifo']=all(x['returned']>x['sent'] for x in responses) and [x['id'] for x in responses]==list(range(1,len(responses)+1))
checks['latency_increases_under_load']=all(a['latency_ms']<=b['latency_ms'] for a,b in zip(responses,responses[1:])) and responses[-1]['latency_ms']>responses[0]['latency_ms']*4
checks['reply_spacing_grows']=responses[-1]['returned']-responses[-2]['returned']>1.8*(responses[3]['returned']-responses[2]['returned'])
checks['no_replies_after_stall']=all(x['returned']<audit['admission_stall'] for x in responses)
checks['pending_accounting']=audit['final']['sent']-audit['final']['replied']==audit['final']['pending']
checks['backlog_outlasts_server']=audit['final']['pending']>400 and audit['final']['age']>1.
report=dict(passed=all(checks.values()),checks=checks,audio_alignment=alignment,metadata=meta,input_manifest=manifest,terminal_timing=audit)
(HERE/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(passed=report['passed'],checks=checks,audio_alignment=alignment),indent=2),flush=True)
if not report['passed']:raise SystemExit(1)
