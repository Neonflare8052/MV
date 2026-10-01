"""Monospace glyph atlas for the ASCII eye and the typed lines. One row of cells; index = position in CHARS."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
# 0: blank, then a density ramp, then '!', then letters used by EXECUTION, then noise characters
RAMP = ' .:-=+*#%@'
CHARS = RAMP + '!' + 'EXCUTION' + '$&?/\\|<>0123456789AKMWZ'
CW, CH = 48, 80


def build():
    f = ImageFont.truetype('C:/Windows/Fonts/CascadiaMono.ttf', 64)
    img = Image.new('L', (CW * len(CHARS), CH), 0)
    d = ImageDraw.Draw(img)
    for i, ch in enumerate(CHARS):
        box = d.textbbox((0, 0), ch, font=f)
        x = i * CW + (CW - (box[2] - box[0])) / 2 - box[0]
        d.text((x, 6), ch, font=f, fill=255)
    img.save(HERE / 'glyphs.png')
    return img


if __name__ == '__main__':
    build(); print(len(CHARS), 'glyphs')
