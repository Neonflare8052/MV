"""Extract review contact sheet from the encoded delivery (not source renders)."""
from pathlib import Path
import subprocess,concurrent.futures
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
TIMES=[1.3,10.5,27,32.8,39.8,54.5,56.8,60,65,72.4,82.8,87.99,96.6,102.5,110.5,116.1,132,156,164,176.8,180.9,190.5,197,210]

def extract(t):
    p=ROOT/'work'/'encoded_review'/f'{t:08.3f}.jpg'
    subprocess.run([str(ROOT/'tools'/'ffmpeg.exe'),'-v','error','-y','-ss',str(t),'-i',str(ROOT/'output'/'world_execute_me_4K60.mp4'),'-frames:v','1','-vf','scale=640:360','-q:v','2',str(p)],check=True,capture_output=True)
    return p

def main():
    (ROOT/'work'/'encoded_review').mkdir(exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:paths=list(pool.map(extract,TIMES))
    out=Image.new('RGB',(1920,6*390),'#141414');d=ImageDraw.Draw(out);font=ImageFont.truetype('C:/Windows/Fonts/CascadiaMono.ttf',17)
    for i,(p,t) in enumerate(zip(paths,TIMES)):
        x=i%3*640;y=i//3*390
        # 24 frames use eight rows.
        if y+390>out.height:
            larger=Image.new('RGB',(1920,y+390),'#141414');larger.paste(out,(0,0));out=larger;d=ImageDraw.Draw(out)
        out.paste(Image.open(p),(x,y));d.text((x+16,y+365),f'{int(t//60):02}:{t%60:06.3f}',font=font,fill='#F2EBDD')
    out.save(ROOT/'output'/'contact_sheet.jpg',quality=91)
    Image.open(paths[17]).save(ROOT/'output'/'preview.jpg',quality=95)
    print('Encoded-frame contact sheet written.')
if __name__=='__main__':main()
