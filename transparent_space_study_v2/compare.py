from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
HERE=Path(__file__).resolve().parent
previous=HERE.parent/'transparent_space_study'
font=ImageFont.truetype('C:/Windows/Fonts/CascadiaMono.ttf',28)
for index,t in [(2,35.8),(5,38.8)]:
    name=f'encoded_{index:02d}_source_{t:04.1f}.jpg'
    result=Image.new('RGB',(3840,1136),(15,16,16))
    for x,folder in [(0,previous),(1920,HERE)]:
        with Image.open(folder/'qa'/name) as frame:
            result.paste(frame,(x,56))
    draw=ImageDraw.Draw(result)
    draw.text((28,12),f'V1 / {t:.1f}s',font=font,fill=(220,217,207))
    draw.text((1948,12),f'V2 / {t:.1f}s',font=font,fill=(220,217,207))
    result.save(HERE/f'v1_vs_v2_{t:.1f}.jpg',quality=95)
