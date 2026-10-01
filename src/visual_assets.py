"""Shared deterministic ASCII identity used in first and final simulation views."""
import math
import random
from PIL import Image, ImageDraw, ImageFont
_assets={}

def ascii_eye():
    if 'eye' in _assets:
        return _assets['eye']
    w,h=3840,2160
    im=Image.new('RGB',(w,h),(4,6,8)); d=ImageDraw.Draw(im)
    try:
        font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',27)
    except OSError:
        font=ImageFont.load_default()
    rng=random.Random(4891)
    for row in range(65):
        for col in range(120):
            px=col*32;py=row*34
            x=(px-w/2)/(w*.44);y=(py-h/2)/(h*.36)
            radius=math.sqrt(x*x*3.0+y*y)
            lid=abs(y)/(max(.02,1-x*x)**.66)
            iris=.0
            if abs(x)<.96 and lid<.96:
                iris=.20
                if .43<radius<.96:
                    iris=.44+.34*abs(math.sin(math.atan2(y,x*1.73)*27))
                if radius<.42: iris=.025
            if .94<lid<1.03 and abs(x)<1: iris=.72
            base=.06+iris
            # The eye is made exclusively from the failed execution prefix.
            txt='exe'[col%3]
            v=int(255*min(.9,base+rng.uniform(-.03,.025)))
            d.text((px,py),txt,font=font,fill=(v,int(v*.97),int(v*.90)))
    _assets['eye']=im
    return im

