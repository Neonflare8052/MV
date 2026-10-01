from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import render as scene

views=[((-70,82,-45),(0,7,53)),((-85,95,-30),(0,9,56)),((-115,104,18),(0,8,48)),
       ((-100,100,25),(0,10,48)),((-45,58,-35),(5,9,53)),((-70,67,-30),(0,8,50))]
sheet=Image.new('RGB',(1920,784),(20,20,20));d=ImageDraw.Draw(sheet);font=ImageFont.truetype(scene.FONT,20)
for i,(eye,look) in enumerate(views):
    scene.FAR_POS=np.array(eye,dtype=float);scene.FAR_LOOK=np.array(look,dtype=float)
    im=scene.render(2.8,1280,720,2)
    im.save(scene.HERE/f'camera_{i}.png')
    x=(i%3)*640;y=(i//3)*392
    sheet.paste(im.resize((640,360)),(x,y));d.text((x+8,y+363),f'{i}: {eye}',font=font,fill='white')
sheet.save(scene.HERE/'camera_study.jpg',quality=95)
