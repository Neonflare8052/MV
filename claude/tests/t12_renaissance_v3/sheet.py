import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
fs = sorted((Path(__file__).parent / 'stills').glob('*.png'))
if len(sys.argv) > 2: fs = [f for f in fs if float(sys.argv[2]) <= float(f.stem) <= float(sys.argv[3])]
W, H, C = 960, 540, 2
rows = (len(fs) + C - 1) // C
S = Image.new('RGB', (W * C, (H + 24) * rows), (20, 20, 20)); d = ImageDraw.Draw(S)
f = ImageFont.truetype('C:/Windows/Fonts/CascadiaMono.ttf', 18)
for i, p in enumerate(fs):
    x, y = (i % C) * W, (i // C) * (H + 24)
    S.paste(Image.open(p).resize((W, H), Image.LANCZOS), (x, y)); d.text((x + 6, y + H + 2), p.stem, font=f, fill=(200, 200, 200))
S.save(Path(__file__).parent / sys.argv[1], quality=88)
