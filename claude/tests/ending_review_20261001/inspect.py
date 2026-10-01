from pathlib import Path
import subprocess
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
movie=ROOT/'claude/film/film_0172-0212_ending_v4_1080p.mp4'
times=[174.98,176.3,178.8,180.25,181.6,183.8,185.9,187.85,188.8,189.4,190.35,191.8,193.3,195.6,198.2,200.5,202.7,204.5,205.85,207.1,208.5,209.5,210.5,211.5]
sheet=Image.new('RGB',(1920,6*300),(16,16,16));d=ImageDraw.Draw(sheet)
f=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',20)
for i,t in enumerate(times):
    path=HERE/f'{t:.2f}.jpg'
    subprocess.run([str(ROOT/'tools/ffmpeg.exe'),'-y','-hide_banner','-loglevel','error','-ss',str(t-172),'-i',str(movie),'-frames:v','1','-q:v','2',str(path)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    x,y=i%4*480,i//4*300
    with Image.open(path) as im:sheet.paste(im.resize((480,270),Image.Resampling.LANCZOS),(x,y))
    d.text((x+10,y+273),f'{int(t//60):02d}:{t%60:05.2f}',font=f,fill='white')
sheet.save(HERE/'contact.jpg',quality=95)
print(HERE/'contact.jpg')
