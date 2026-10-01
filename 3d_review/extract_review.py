from pathlib import Path
import subprocess
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FF = ROOT/'tools/ffmpeg.exe'
MOVIE = ROOT/'claude/film/film_full_v1_1080p.mp4'
TIMES = [8.0,11.5,14.5,31.8,35.5,39.5,43.6,56.8,85.9,87.7,95.0,98.2,101.4,105.0,108.8,110.5,174.9,175.5,176.2,177.3,193.0,194.5,197.4,201.0]
font = ImageFont.truetype('C:/Windows/Fonts/cour.ttf',21)
sheet = Image.new('RGB',(1920,6*302),(16,16,16))
d = ImageDraw.Draw(sheet)
for i,t in enumerate(TIMES):
    name = HERE/f'{t:07.3f}.jpg'
    subprocess.run([str(FF),'-y','-hide_banner','-loglevel','error','-ss',str(t),'-i',str(MOVIE),'-frames:v','1','-q:v','2',str(name)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    x,y=i%4*480,i//4*302
    with Image.open(name) as im: sheet.paste(im.resize((480,270),Image.Resampling.LANCZOS),(x,y))
    d.text((x+12,y+275),f'{int(t)//60}:{t%60:06.3f}',font=font,fill=(220,220,220))
sheet.save(HERE/'3d_review_sheet.jpg',quality=95)
print('24 encoded frames extracted from film_full_v1_1080p.mp4')
