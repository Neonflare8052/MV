from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE=Path(__file__).resolve().parent
paths=sorted((HERE/'stills').glob('*.png'))
sheet=Image.new('RGB',(1920,294*((len(paths)+3)//4)),(18,19,19))
draw=ImageDraw.Draw(sheet)
f=ImageFont.truetype('C:/Windows/Fonts/CascadiaMono.ttf',17)
for i,path in enumerate(paths):
    x=(i%4)*480; y=(i//4)*294
    with Image.open(path) as img: sheet.paste(img.resize((480,270)),(x,y+24))
    draw.text((x+10,y+1),f'{float(path.stem):05.2f} s',font=f,fill=(224,220,211))
sheet.save(HERE/'preview_sheet.jpg',quality=92)
