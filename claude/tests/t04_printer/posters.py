"""Six constructivist frames (EIN..LIU): first-person, lying on your back, carried towards the blade.
Only black / red / cream — the colours a dot-matrix printer with a two-colour ribbon can print.
Also renders the blade inscription strip. Output: atlas.png (6 frames stacked + strip)."""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
W, H = 1200, 900
CREAM, BLACK, RED = (242, 235, 221), (20, 18, 16), (200, 30, 28)
WORDS = ['EIN', 'DOS', 'TROIS', 'NE', 'FEM', 'LIU']
ANG = [120, 300, 200, 20, 250, 70]          # where each bearer leans in (degrees, screen space)
INSCRIPTION = 'IF I CANNOT INSPIRE LOVE, I WILL CAUSE FEAR'


def font(size):
    f = ImageFont.truetype('C:/Windows/Fonts/bahnschrift.ttf', size)
    try: f.set_variation_by_name('Bold')
    except Exception: pass
    return f


def rotated_text(img, text, size, fill, center, angle):
    f = font(size)
    box = ImageDraw.Draw(img).textbbox((0, 0), text, font=f)
    tw, th = box[2] - box[0] + 20, box[3] - box[1] + 20
    layer = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((10 - box[0], 10 - box[1]), text, font=f, fill=fill)
    layer = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(layer, (int(center[0] - layer.width / 2), int(center[1] - layer.height / 2)))


def bearer(d, cx, cy, ang, scale, colour):
    """A Schlemmer-like figure seen from below: cone body reaching in from the frame edge, sphere head."""
    a = math.radians(ang)
    ux, uy = math.cos(a), -math.sin(a)                    # outward direction (screen y down)
    hx, hy = cx + ux * 300 * scale, cy + uy * 300 * scale  # head
    far = 900
    px, py = -uy, ux
    body = [(hx + ux * 60 * scale + px * 90 * scale, hy + uy * 60 * scale + py * 90 * scale),
            (hx + ux * 60 * scale - px * 90 * scale, hy + uy * 60 * scale - py * 90 * scale),
            (hx + ux * far - px * 330, hy + uy * far - py * 330),
            (hx + ux * far + px * 330, hy + uy * far + py * 330)]
    d.polygon(body, fill=colour)
    r = 78 * scale
    d.ellipse((hx - r, hy - r, hx + r, hy + r), fill=BLACK)
    d.pieslice((hx - r * .8, hy - r * .8, hx + r * .8, hy + r * .8), ang + 150, ang + 210, fill=CREAM)   # a sliver of light


def frame(k):
    img = Image.new('RGBA', (W, H), CREAM + (255,))
    d = ImageDraw.Draw(img)
    cx, cy = W / 2, H / 2 + 20
    closeness = (k + 1) / 6
    # the sky between them: a cream disc framed by a black ring that tightens as they close in
    ring = 520 - 150 * closeness
    d.ellipse((cx - ring - 40, cy - ring - 40, cx + ring + 40, cy + ring + 40), outline=BLACK, width=int(10 + 30 * closeness))
    # guillotine uprights converge overhead from frame 3 on
    if k >= 2:
        for sgn in (-1, 1):
            d.polygon([(cx + sgn * 330, H + 40), (cx + sgn * 400, H + 40), (cx + sgn * 150, cy - 150), (cx + sgn * 120, cy - 150)], fill=BLACK)
        d.rectangle((cx - 170, cy - 185, cx + 170, cy - 145), fill=BLACK)
    for i in range(k + 1):
        bearer(d, cx, cy, ANG[i], .75 + .35 * closeness, RED if i % 2 else BLACK)
    # the red wedge (Lissitzky): the blade, nearer every count
    s = .35 + .65 * closeness
    top = cy - 145
    wedge = [(cx - 150 * s, top), (cx + 150 * s, top), (cx + 150 * s, top + 110 * s), (cx - 150 * s, top + 220 * s)]
    d.polygon(wedge, fill=RED)
    if k >= 4:                                               # the inscription becomes legible
        rotated_text(img, INSCRIPTION, int(13 * s), CREAM, (cx, top + 125 * s), math.degrees(math.atan2(110, 300)))
    # a constructivist bar
    d.polygon([(0, H * .78), (W * .42, H * .98), (W * .42, H), (0, H)], fill=RED if k % 2 == 0 else BLACK)
    tx, ty, ta = (W * .2 if k % 2 == 0 else W * .8), H * .15, (10 if k % 2 == 0 else -10)
    band = Image.new('RGBA', (560, 230), CREAM + (255,)).rotate(ta, expand=True, fillcolor=(0, 0, 0, 0))
    img.alpha_composite(band, (int(tx - band.width / 2), int(ty - band.height / 2)))
    rotated_text(img, WORDS[k], 230, RED if k % 2 else BLACK, (tx, ty), ta)
    rotated_text(img, f'{k + 1}/6', 46, BLACK, (W * .9, H * .92), 0)
    return img.convert('RGB')


def strip():
    img = Image.new('RGBA', (W, 150), (0, 0, 0, 255))
    rotated_text(img, INSCRIPTION, 50, (255, 255, 255, 255), (W / 2, 75), 0)
    return img.convert('RGB')


def atlas():
    frames = [frame(k) for k in range(6)] + [strip()]
    out = Image.new('RGB', (W, H * 6 + 150))
    y = 0
    for f in frames:
        out.paste(f, (0, y)); y += f.height
    return out


if __name__ == '__main__':
    a = atlas(); a.save(HERE / 'atlas.png')
    prev = Image.new('RGB', (W * 3, H * 2))
    for k in range(6):
        prev.paste(a.crop((0, H * k, W, H * (k + 1))), ((k % 3) * W, (k // 3) * H))
    prev.resize((W * 3 // 3, H * 2 // 3)).save(HERE / 'posters_preview.jpg', quality=88)
    print('ok')
