"""Validate the encoded movie, including decoded source-audio alignment."""
from pathlib import Path
import json
import subprocess
import wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FF = ROOT/'tools/ffmpeg.exe'
PROBE = ROOT/'tools/ffprobe.exe'
MOVIE = HERE/'train_cel_study_1080p60.mp4'
SONG = next(ROOT.glob('*.mp3'))
START = 162.632


def run(cmd):
    return subprocess.run([str(x) for x in cmd], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def pcm(path, start, duration=.7):
    wav = HERE/f'qa_{Path(path).suffix[1:]}_{start:.3f}.wav'
    run([FF, '-y', '-hide_banner', '-loglevel', 'error', '-ss', start, '-i', path, '-t', duration, '-vn', '-ac', 1, '-ar', 16000, '-c:a', 'pcm_s16le', wav])
    with wave.open(str(wav), 'rb') as f:
        assert f.getnchannels() == 1 and f.getsampwidth() == 2 and f.getframerate() == 16000
        data = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16).astype(float)/32768
    assert len(data) >= 16000*duration*.95 and data.std() > .0001
    return data


meta = json.loads(run([PROBE, '-v', 'error', '-show_streams', '-show_format', '-of', 'json', MOVIE]).stdout)
video = next(s for s in meta['streams'] if s['codec_type'] == 'video')
audio = next(s for s in meta['streams'] if s['codec_type'] == 'audio')
checks = {'1920x1080': video['width'] == 1920 and video['height'] == 1080,
          '60fps': video['avg_frame_rate'] == '60/1',
          '360_frames': int(video['nb_frames']) == 360,
          '6_seconds': abs(float(meta['format']['duration'])-6.) < .02,
          'stereo_audio': audio['channels'] == 2}
run([FF, '-hide_banner', '-loglevel', 'error', '-xerror', '-i', MOVIE, '-map', '0:v:0', '-map', '0:a:0', '-f', 'null', 'NUL'])
checks['full_decode'] = True
alignment = []
for offset in [.4, 2.8, 5.1]:
    reference, encoded = pcm(SONG, START+offset), pcm(MOVIE, offset)
    n = min(len(reference), len(encoded)); reference, encoded = reference[:n], encoded[:n]
    best = (-2, None)
    for lag in range(-320, 321):
        if lag > 0: a, b = reference[:-lag], encoded[lag:]
        elif lag < 0: a, b = reference[-lag:], encoded[:lag]
        else: a, b = reference, encoded
        a, b = a-a.mean(), b-b.mean()
        corr = float(np.dot(a, b)/(np.linalg.norm(a)*np.linalg.norm(b)+1e-15))
        if corr > best[0]: best = (corr, lag)
    alignment.append({'window_start': offset, 'correlation': best[0], 'lag_ms': best[1]/16})
checks['audio_sync'] = all(x['correlation'] > .98 and abs(x['lag_ms']) <= 1. for x in alignment)
sheet = Image.new('RGB', (1920, 1176), (20,19,18)); draw = ImageDraw.Draw(sheet)
font = ImageFont.truetype('C:/Windows/Fonts/cour.ttf', 23)
for i, t in enumerate([.2,.8,1.3,2.,2.7,3.5,4.2,5.,5.8]):
    name = HERE/f'encoded_{t:04.1f}.jpg'
    run([FF, '-y', '-hide_banner', '-loglevel', 'error', '-ss', t, '-i', MOVIE, '-frames:v', 1, '-q:v', 2, name])
    x, y = i%3*640, i//3*392
    with Image.open(name) as frame: sheet.paste(frame.resize((640,360), Image.Resampling.LANCZOS), (x,y))
    draw.text((x+12,y+363), f'{t:04.2f}s / {START+t:07.3f}', fill=(225,218,198), font=font)
sheet.save(HERE/'encoded_contact_sheet.jpg', quality=95)
report = {'passed': all(checks.values()), 'checks': checks, 'audio_alignment': alignment, 'metadata': meta}
(HERE/'verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({'passed': report['passed'], 'checks': checks, 'audio_alignment': alignment}, indent=2), flush=True)
if not report['passed']: raise SystemExit(1)
