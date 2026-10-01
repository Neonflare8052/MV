"""Check encoded output, extract encoded frames and compare the actual soundtrack."""
from pathlib import Path
import json
import subprocess
import wave
import numpy as np
from PIL import Image,ImageDraw,ImageFont

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
FF=ROOT/'tools/ffmpeg.exe';PROBE=ROOT/'tools/ffprobe.exe'
SONG=next(ROOT.glob('*.mp3'))
MOVIE=HERE/'census_train_study_1080p60.mp4'
START=162.632

def run(cmd):
    return subprocess.run([str(x) for x in cmd],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

meta=json.loads(run([PROBE,'-v','error','-show_streams','-show_format','-of','json',MOVIE]).stdout)
video=next(s for s in meta['streams'] if s['codec_type']=='video')
audio=next(s for s in meta['streams'] if s['codec_type']=='audio')
duration=float(meta['format']['duration'])
checks={
    '1920x1080':video['width']==1920 and video['height']==1080,
    '60fps':video['avg_frame_rate']=='60/1',
    '323_frames':int(video['nb_frames'])==323,
    'duration':abs(duration-323/60)<.02,
    'stereo_audio':audio['channels']==2,
}
run([FF,'-hide_banner','-loglevel','error','-xerror','-i',MOVIE,'-map','0:v:0','-map','0:a:0','-f','null','NUL'])
checks['full_decode']=True

def pcm(path,start,seconds):
    wav=HERE/f'qa_{Path(path).suffix[1:]}_{start:.3f}.wav'
    run([FF,'-y','-hide_banner','-loglevel','error','-ss',str(start),'-i',path,'-t',str(seconds),'-vn','-ac','1','-ar','16000','-c:a','pcm_s16le',wav])
    with wave.open(str(wav),'rb') as file:
        assert file.getnchannels()==1 and file.getframerate()==16000 and file.getsampwidth()==2
        samples=np.frombuffer(file.readframes(file.getnframes()),dtype=np.int16).astype(np.float64)/32768
    assert len(samples)>seconds*16000*.95 and np.std(samples)>.0001
    return samples

alignment=[]
for offset in [.40,2.25,4.30]:
    reference=pcm(SONG,START+offset,.70)
    encoded=pcm(MOVIE,offset,.70)
    n=min(len(reference),len(encoded));reference=reference[:n];encoded=encoded[:n]
    # Lags are bounded to a meaningful edit/sync error, 20 ms.
    best=(-2,None)
    for lag in range(-320,321):
        if lag>0:a,b=reference[:-lag],encoded[lag:]
        elif lag<0:a,b=reference[-lag:],encoded[:lag]
        else:a,b=reference,encoded
        a=a-a.mean();b=b-b.mean()
        corr=float(np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b)+1e-15))
        if corr>best[0]:best=(corr,lag)
    alignment.append({'window_start':offset,'correlation':best[0],'lag_ms':best[1]/16})
checks['audio_sync']=all(x['correlation']>.98 and abs(x['lag_ms'])<=1.0 for x in alignment)

frames=[]
for t in [.3,.8,1.3,1.85,2.5,2.8,3.38,4.3,5.3]:
    name=HERE/f'encoded_{t:04.1f}.jpg'
    run([FF,'-hide_banner','-loglevel','error','-ss',str(t),'-i',MOVIE,'-frames:v','1','-q:v','2','-y',name])
    frames.append((t,name))
cw,ch,cols=640,360,3
sheet=Image.new('RGB',(1920,1176),(20,20,20));draw=ImageDraw.Draw(sheet)
font=ImageFont.truetype('C:/Windows/Fonts/cour.ttf',24)
for i,(t,name) in enumerate(frames):
    x,y=(i%cols)*cw,(i//cols)*(ch+32)
    with Image.open(name) as frame:sheet.paste(frame.resize((cw,ch),Image.Resampling.LANCZOS),(x,y))
    draw.text((x+12,y+ch+3),f'{t:04.1f}s  /  {START+t:07.3f}',fill='white',font=font)
sheet.save(HERE/'encoded_contact_sheet.jpg',quality=95)
report={'passed':all(checks.values()),'checks':checks,'audio_alignment':alignment,'metadata':meta}
(HERE/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':report['passed'],'checks':checks,'audio_alignment':alignment},indent=2),flush=True)
if not report['passed']:raise SystemExit(1)
