"""Contact sheet of PNG stills: python sheet.py <dir> <out.jpg> [cols]"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

d, out = Path(sys.argv[1]), sys.argv[2]
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 3
files = sorted(d.glob('*.png'))
ims = [Image.open(f).convert('RGB') for f in files]
w, h = ims[0].size
lab = 22
sheet = Image.new('RGB', (w * cols, (h + lab) * ((len(ims) + cols - 1) // cols)), (20, 20, 20))
dr = ImageDraw.Draw(sheet)
for i, (f, im) in enumerate(zip(files, ims)):
    x, y = (i % cols) * w, (i // cols) * (h + lab)
    sheet.paste(im, (x, y)); dr.text((x + 6, y + h + 4), f.stem, fill=(220, 220, 220))
sheet.save(out, quality=90)
print(out)
