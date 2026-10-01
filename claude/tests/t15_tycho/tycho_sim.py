"""Sun removed at t0; the news (light and gravity) spreads from where it was at c. Each body keeps its circular orbit
round the vanished Sun until the front reaches it, then goes straight (inertia). Earth is one of those bodies.
Tycho's frame: Earth fixed at the origin, axes fixed to the stars -> every position minus Earth's."""
import math
from PIL import Image, ImageDraw, ImageFont

T0 = 112.22
BEATS = {'Mercurius': 113.10, 'Venus': 114.18, 'Mars': 114.92, 'Iuppiter': 115.78, 'Saturnus': 117.274}
C = .39 / (BEATS['Mercurius'] - T0)                      # the front reaches Mercury on its beat (AU / s, compressed)
A = {k: C * (v - T0) for k, v in BEATS.items()}           # orbit radii chosen so each is released on its beat
A['Terra'] = 1.0
TE = 3.0                                                  # Earth's year, compressed (s)
PH = {'Mercurius': 1.0, 'Venus': 2.6, 'Terra': 4.2, 'Mars': .3, 'Iuppiter': 3.5, 'Saturnus': 5.4}


def body(name, t):
    a = A[name]; w = 2 * math.pi / (TE * a ** 1.5)       # Kepler's third law
    tr = T0 + a / C                                        # when the news arrives
    def circ(tt): return a * math.cos(PH[name] + w * (tt - T0)), a * math.sin(PH[name] + w * (tt - T0))
    if t <= tr: return circ(t)
    x, y = circ(tr); vx, vy = -a * w * math.sin(PH[name] + w * (tr - T0)), a * w * math.cos(PH[name] + w * (tr - T0))
    return x + vx * (t - tr), y + vy * (t - tr)


def geo(name, t):
    e = body('Terra', t); p = (0., 0.) if name == 'Sol' else body(name, t)
    return p[0] - e[0], p[1] - e[1]


if __name__ == '__main__':
    W, H = 1800, 900
    img = Image.new('RGB', (W, H), (14, 14, 16)); d = ImageDraw.Draw(img)
    f = ImageFont.truetype('C:/Windows/Fonts/GARA.TTF', 22)
    cols = {'Sol': (255, 210, 120), 'Mercurius': (180, 180, 190), 'Venus': (240, 220, 170), 'Mars': (230, 110, 80),
            'Iuppiter': (220, 180, 130), 'Saturnus': (200, 190, 140), 'Terra': (120, 170, 255)}
    for panel, (fn, title, cx) in enumerate([(lambda n, t: (0., 0.) if n == 'Sol' else body(n, t), 'heliocentric (what really happens)', 450),
                                              (geo, "Tycho's frame: Earth fixed", 1350)]):
        cy, sc = 450, 150
        d.text((cx - 200, 30), title, font=f, fill=(230, 220, 200))
        for n in ['Sol', 'Terra', 'Mercurius', 'Venus', 'Mars', 'Iuppiter', 'Saturnus']:
            if panel == 1 and n == 'Terra': continue
            pts_before, pts_after = [], []
            for k in range(0, 801):
                t = T0 - 1.2 + k * (6.6 / 800)
                if n == 'Sol' and t > T0 and panel == 0: break
                x, y = fn(n, t)
                q = (cx + x * sc, cy - y * sc)
                (pts_before if t <= T0 else pts_after).append(q)
            if len(pts_before) > 1: d.line(pts_before, fill=tuple(int(c * .45) for c in cols[n]), width=1)
            if len(pts_after) > 1: d.line(pts_after, fill=cols[n], width=2)
            x, y = fn(n, T0); d.ellipse((cx + x * sc - 5, cy - y * sc - 5, cx + x * sc + 5, cy - y * sc + 5), fill=cols[n])
            d.text((cx + x * sc + 8, cy - y * sc - 10), n, font=f, fill=cols[n])
        if panel == 1: d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=cols['Terra']); d.text((cx + 10, cy + 4), 'Terra (me)', font=f, fill=cols['Terra'])
    d.text((40, H - 40), 'dim: before the Sun goes (1.2 s) · bright: after, until 117.6 · Sun\'s place in Tycho\'s frame = the empty spot it left', font=f, fill=(160, 150, 140))
    img.save('tycho_paths.png')
    print({k: round(v, 3) for k, v in A.items()}, 'Earth news at', round(T0 + 1 / C, 3))
