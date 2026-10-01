"""s14f · 2:52.95–2:54.975  the Chinese Room, drawn.  (draft)  Orthographic, the night sheet: lime white on black.

2:52.95                       a section of the room (axonometric; the near walls cut low, their cut faces hatched).  The
                              letter comes in from the left, through the slot in the far wall, down onto the in-tray.  A man
                              at the desk; the wall behind him is rule books; an out slot.  English labels: after Searle, 1980.
2:53.643 Though we are trapped   (pages turn at 2:53.95, 2:54.30)
                              the desk from above: the paper — the red character reads the other way round from here; the
                              rule book, one symbol to a row, an arrow, the symbols to answer with.  A finger goes down the
                              rows; the page turns on the beat.
2:54.3 … 2:54.9               on the last page 爱 is there, the right way round, and its answer is empty.  The finger goes
                              past it: the one on the paper does not look like it.  It stops at the foot of the page.  The
                              answer slip stays blank.

Drawn frame by frame in PIL (static layers once, moving parts per frame); the shader only tones the picture."""
import sys, math, random, importlib.util
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

_D = Path(__file__).resolve().parent
sys.path.insert(0, str(_D.parents[1] / 'tests' / 't11_assembly'))
import drafting
_sp = importlib.util.spec_from_file_location('s14e_f', _D / 's14e_letter.py'); S14E = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(S14E)

T_IN, T_DESK, T_END = 172.95, 173.643, 174.975
FLIPS = [173.95, 174.30]
POST = dict(u_bloom=0., u_ca=0., u_grain=.012)
F = 'C:/Windows/Fonts/'
CHALK = (232, 227, 214)
NIGHT = (13, 12, 11, 255)
CREAM = (242, 235, 219, 255)
RED = (178, 24, 30)


def clamp(x, a=0., b=1.): return a if x < a else b if x > b else x
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def outc(x): x = clamp(x); return 1 - (1 - x) ** 3


SRC = r'''#version 330
uniform vec2 u_res; uniform float u_time, u_weight;
uniform sampler2D u_img;
out vec4 fragColor;
float h21(vec2 p){ vec3 p3 = fract(vec3(p.xyx) * .1031); p3 += dot(p3, p3.yzx + 33.33); return fract((p3.x + p3.y) * p3.z); }
vec3 untone(vec3 c, vec2 fc){
  vec3 L = pow(clamp(c, 0., .985), vec3(2.2));
  vec3 A = 2.51 - 2.43 * L, B = .03 - .59 * L, C = -.14 * L;
  vec3 y = (-B + sqrt(B * B - 4. * A * C)) / (2. * A);
  vec2 d = fc / u_res - .5;
  return y / 1.05 / (1. - .9 * dot(d, d));
}
void main(){
  vec3 c = texture(u_img, gl_FragCoord.xy / u_res).rgb;
  c *= 1. + .04 * (h21(floor(gl_FragCoord.xy / 3.)) - .5) * step(dot(c, vec3(.33)), .15);
  fragColor = vec4(untone(c, gl_FragCoord.xy) * u_weight, 1.);
}
'''


def params(t): return {}


# ---------------- the room, in section (axonometric)
SC, OX, OY = 132., 1010., 690.                 # px per metre at 1080p; where the room's origin falls


def iso(x, y, z):
    """Screen (1080p units, y down) of a point in the room: x along the far left wall, z toward us, y up."""
    return (OX + (x - z) * .866 * SC, OY - y * SC + (x + z) * .5 * SC - 3.5 * .5 * SC)


def _prism(S, x0, x1, y0, y1, z0, z1, hatch_top=False, fill=True, w=1.3):
    """A box seen from above-front-right: its top, +x and +z faces, filled with night, outlined in chalk."""
    k = S.k
    top = [iso(x0, y1, z0), iso(x1, y1, z0), iso(x1, y1, z1), iso(x0, y1, z1)]
    fx = [iso(x1, y0, z0), iso(x1, y1, z0), iso(x1, y1, z1), iso(x1, y0, z1)]
    fz = [iso(x0, y0, z1), iso(x1, y0, z1), iso(x1, y1, z1), iso(x0, y1, z1)]
    for poly, shade in ((fx, (22, 21, 19, 255)), (fz, (17, 16, 15, 255)), (top, (26, 25, 23, 255))):
        if fill: S.d.polygon([(a * k, b * k) for a, b in poly], fill=shade)
        S.poly(poly, w=w, col=CHALK, amp=.25)
    if hatch_top:                                  # a cut face: section lines
        (ax, ay), (bx, by), (cx, cy), (dx, dy) = top
        n = 14
        for i in range(1, n):
            f = i / n
            S.line([(ax + (bx - ax) * f, ay + (by - ay) * f), (dx + (cx - dx) * f, dy + (cy - dy) * f)], w=.5, col=CHALK, alpha=150, amp=.05)


def _room_layer(w, h):
    S = drafting.Sheet(w, h, seed=80)
    k = S.k
    W_, D_, H_, T_ = 4., 3., 2.6, .2
    # floor
    fl = [iso(0, 0, 0), iso(W_, 0, 0), iso(W_, 0, D_), iso(0, 0, D_)]
    S.d.polygon([(a * k, b * k) for a, b in fl], fill=(19, 18, 17, 255))
    for i in range(1, 12):                          # floor boards, faint
        S.line([iso(i * W_ / 12, 0, 0), iso(i * W_ / 12, 0, D_)], w=.4, col=CHALK, alpha=60, amp=.05)
    # the far walls, full height, cut at the top
    _prism(S, -T_, 0, 0, H_, -T_, D_, hatch_top=True)
    _prism(S, 0, W_, 0, H_, -T_, 0, hatch_top=True)
    # shelves of rule books on the far wall (z = 0), behind the desk
    for row in range(4):
        y0 = .5 + row * .48
        S.line([iso(1.9, y0, 0.02), iso(3.9, y0, 0.02)], w=.9, col=CHALK, amp=.1)
        x = 1.95
        r = random.Random(row)
        while x < 3.85:
            bw = r.uniform(.05, .09); bh = r.uniform(.28, .4)
            S.poly([iso(x, y0, .02), iso(x + bw, y0, .02), iso(x + bw, y0 + bh, .02), iso(x, y0 + bh, .02)], w=.5, col=CHALK, alpha=200, amp=.02)
            x += bw + .01
    # the in slot (left wall, inner face) and the out slot (far wall)
    S.poly([iso(0, 1.18, 1.05), iso(0, 1.18, 1.55), iso(0, 1.24, 1.55), iso(0, 1.24, 1.05)], w=1.2, col=CHALK, amp=.05)
    S.poly([iso(.9, 1.18, 0), iso(1.4, 1.18, 0), iso(1.4, 1.24, 0), iso(.9, 1.24, 0)], w=1.2, col=CHALK, amp=.05)
    # desk, trays, a lamp
    _prism(S, .7, 2.1, .72, .78, .9, 1.9)
    for x, z in ((.75, .95), (2.05, .95), (.75, 1.85), (2.05, 1.85)):
        S.line([iso(x, 0, z), iso(x, .72, z)], w=1., col=CHALK, amp=.05)
    _prism(S, .8, 1.15, .78, .84, 1.0, 1.35)                    # in-tray
    _prism(S, 1.7, 2.05, .78, .84, 1.5, 1.85)                   # out-tray
    _prism(S, 1.2, 1.75, .78, .86, 1.1, 1.5)                    # the open rule book
    S.line([iso(1.9, .78, 1.1), iso(1.9, 1.3, 1.1), iso(1.7, 1.38, 1.2)], w=1., col=CHALK, amp=.05)
    # the man: seated, turned to the slot
    cx, cz = 2.45, 1.4
    _prism(S, cx - .05, cx + .35, .42, .47, cz - .2, cz + .2)   # seat
    S.line([iso(cx + .3, .47, cz - .2), iso(cx + .3, 1.0, cz - .2)], w=1., col=CHALK, amp=.05)
    S.line([iso(cx + .3, .47, cz + .2), iso(cx + .3, 1.0, cz + .2)], w=1., col=CHALK, amp=.05)
    hx, hy = iso(cx + .1, 1.42, cz)
    torso = [iso(cx, .5, cz - .16), iso(cx + .22, .5, cz - .16), iso(cx + .22, 1.2, cz - .13), iso(cx, 1.2, cz - .13),
             iso(cx, 1.2, cz + .13), iso(cx, .5, cz + .16)]
    S.d.polygon([(a * k, b * k) for a, b in torso], fill=(24, 23, 21, 255)); S.poly(torso, w=1.2, col=CHALK, amp=.1)
    S.d.ellipse([(hx - 15) * k, (hy - 17) * k, (hx + 15) * k, (hy + 17) * k], fill=(24, 23, 21, 255))
    S.ellipse(hx, hy, 15, 17, w=1.2, col=CHALK, amp=.1)
    S.line([iso(cx + .02, 1.1, cz - .1), iso(cx - .35, .86, cz - .15), iso(cx - .6, .82, cz - .2)], w=1.3, col=CHALK, amp=.1)   # arm to the book
    S.line([iso(cx + .05, .5, cz - .05), iso(cx - .35, .48, cz - .05), iso(cx - .35, 0, cz - .05)], w=1.2, col=CHALK, amp=.1)
    S.line([iso(cx + .05, .5, cz + .08), iso(cx - .35, .48, cz + .1), iso(cx - .35, 0, cz + .1)], w=1.2, col=CHALK, amp=.1)
    # the near walls, cut low: their cut faces hatched
    _prism(S, 0, W_ + T_, 0, .9, D_, D_ + T_, hatch_top=True)
    _prism(S, W_, W_ + T_, 0, .9, -T_, D_, hatch_top=True)
    return S


def _labels_layer(w, h):
    S = drafting.Sheet(w, h, seed=81)
    Wt = w * 1080 / h
    drafting.border(S)
    T = 'cour.ttf'
    for pt, off, L in [((0, 1.21, 1.3), (-150, -60), 'A'), ((2.9, 1.5, 0), (40, -150), 'B'), ((1.15, 1.21, 0), (-40, -160), 'C'),
                       ((2.55, 1.42, 1.4), (150, -40), 'D')]:
        x, y = iso(*pt)
        S.leader(x, y, x + off[0], y + off[1], L)
    S.text(70, 70, 'THE CHINESE ROOM.', 'COPRGTL.TTF', 22, col=CHALK)
    S.text(70, 104, 'Section, looking in.', T, 16, col=CHALK, alpha=200)
    for i, (l, t_) in enumerate([('A.', 'Input slot'), ('B.', 'Rule books'), ('C.', 'Output slot'), ('D.', 'Operator: understands no Chinese')]):
        S.text(74, 160 + i * 28, l, 'BASKVILL.TTF', 18, col=CHALK)
        S.text(108, 163 + i * 28, t_, T, 15, col=CHALK, alpha=210)
    tx, ty = Wt - 530, 888
    S.poly([(tx, ty), (tx + 470, ty), (tx + 470, ty + 150), (tx, ty + 150)], w=1.5, col=CHALK, amp=.3)
    S.line([(tx, ty + 62), (tx + 470, ty + 62)], w=.8, col=CHALK, amp=.2)
    S.text(tx + 235, ty + 33, 'THE CHINESE ROOM.', 'ENGR.TTF', 28, col=CHALK, anchor='mm')
    S.text(tx + 235, ty + 90, 'after J. R. Searle,  1980.', 'GARAIT.TTF', 22, col=CHALK, anchor='mm')
    S.text(tx + 235, ty + 124, 'Minds, Brains, and Programs', 'GARAIT.TTF', 17, col=CHALK, alpha=200, anchor='mm')
    return S


# ---------------- the desk from above: the paper, the rule book
CH = list('的一是在不了有和人这中大为上个国我以要他时来用们生到作地于出就分对成会可也你能下过子说产种面而方后多定行学法所民得经十三之进着等部度家电力里如水化高自二理起小物现实加量都两体制机当使点从业本去把性好应开它合还因由其些然前外天政四日那社义事平形相全表间样与关各重新线内数正心反明看原又么利比或但质气第向道命此变条只没结解问意建月公无系军很情者最立代想已通并提直题党程展五果料象员革位入常文总次品式活设及管特件长求老头基资边流路级少图山统接知较将组见计别她手角期根论运农指几九区强放决西被干做必战先回则任取据处理府研质')


def _book_pages():
    """Three spreads: symbol, arrow, the symbols to answer with.  爱 on the last, its answer empty."""
    r = random.Random(1980)
    fs = ImageFont.truetype(F + 'simsun.ttc', 44); fr = ImageFont.truetype(F + 'simsun.ttc', 34)
    fa = ImageFont.truetype(F + 'cour.ttf', 30); fn = ImageFont.truetype(F + 'cour.ttf', 20)
    spreads = []
    for sp in range(3):
        img = Image.new('RGBA', (1500, 980), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
        for side in range(2):
            x0 = 60 + side * 750
            d.text((x0 + 320, 40), str(212 + sp * 2 + side), font=fn, fill=(255, 255, 255, 180), anchor='mm')
            for row in range(12):
                y = 100 + row * 70
                ch = r.choice(CH)
                ans = ''.join(r.choice(CH) for _ in range(r.randint(2, 5)))
                if sp == 2 and side == 1 and row == 6: ch, ans = '爱', ''
                if ch == '爱': d.text((x0 + 44, y + 26), ch, font=ImageFont.truetype(F + 'STXINGKA.TTF', 66), fill=(255, 255, 255, 255), anchor='mm')   # the same hand as the paper's
                else: d.text((x0 + 20, y), ch, font=fs, fill=(255, 255, 255, 250))
                d.text((x0 + 100, y + 8), '→', font=fa, fill=(255, 255, 255, 200))
                if ans: d.text((x0 + 170, y + 8), ans, font=fr, fill=(255, 255, 255, 235))
                else: d.line([(x0 + 175, y + 44), (x0 + 560, y + 44)], fill=(255, 255, 255, 110), width=2)   # nothing written
                d.line([(x0, y + 60), (x0 + 620, y + 60)], fill=(255, 255, 255, 60), width=1)
        spreads.append(img)
    return spreads


_C = {}


def _static(w, h):
    if (w, h) not in _C:
        _C.clear()
        room = _room_layer(w, h).result(); labels = _labels_layer(w, h).result()
        labels = Image.merge('RGBA', (*Image.new('RGB', labels.size, CHALK).split(), labels.split()[3]))   # all in chalk
        back = S14E._back()                                    # the letter's back: 爱
        _C[(w, h)] = dict(room=room, labels=labels, back=back, spreads=_book_pages(),
                          paper_mirror=back.transpose(Image.FLIP_LEFT_RIGHT))
    return _C[(w, h)]


def _letter_sprite(back, wpx, hpx, mirrored=False):
    img = Image.new('RGBA', (int(wpx) + 8, int(hpx) + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rectangle([4, 4, 4 + wpx, 4 + hpx], fill=CREAM, outline=CHALK + (255,), width=max(2, int(wpx / 60)))
    mark = back.transpose(Image.FLIP_LEFT_RIGHT) if mirrored else back
    a = mark.split()[3].resize((int(wpx), int(hpx)), Image.LANCZOS)
    red = Image.new('RGBA', a.size, RED + (255,)); red.putalpha(a.point(lambda v: int(v * .92)))
    img.alpha_composite(red, (4, 4))
    return img


def _frame_room(t, w, h):
    C = _static(w, h); s = h / 1080
    img = Image.new('RGBA', (w, h), NIGHT)
    # the letter: from the left edge, behind the far wall to the slot; then out of the slot, down onto the in-tray
    sx, sy = iso(0, 1.21, 1.3); tx, ty = iso(.97, .86, 1.17)
    a1 = ease((t - T_IN) / .2); a2 = ease((t - T_IN - .2) / .22)
    if a2 <= 0:
        x = -120 + (sx - 60 + 120) * a1; y = sy - 90 + 90 * a1; sc = .95 - .5 * a1; inside = False
    else:
        x = sx + (tx - sx) * a2; y = sy + (ty - sy) * a2; sc = .45 - .1 * a2; inside = True
    spr = _letter_sprite(C['back'], 140 * sc * s, 196 * sc * s)
    spr = spr.rotate(-8 + 20 * a2, resample=Image.BICUBIC, expand=True)
    if not inside and a1 < 1: img.alpha_composite(spr, (int(x * s - spr.width / 2), int(y * s - spr.height / 2)))
    img.alpha_composite(C['room'])
    if inside: img.alpha_composite(spr, (int(x * s - spr.width / 2), int(y * s - spr.height / 2)))
    img.alpha_composite(C['labels'])
    return img


def _frame_desk(t, w, h):
    C = _static(w, h); s = h / 1080
    img = Image.new('RGBA', (w, h), NIGHT); d = ImageDraw.Draw(img)
    # the paper, as he has it: the character reads backwards
    pw, ph = 380 * s, 530 * s
    px_, py_ = 470 * s, 540 * s
    spr = _letter_sprite(C['back'], pw, ph, mirrored=True).rotate(4, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(spr, (int(px_ - spr.width / 2), int(py_ - spr.height / 2)))
    # the book: which spread, and the turning page
    k = 0 + (t >= FLIPS[0]) + (t >= FLIPS[1])
    bw, bh = 1180 * s, 770 * s
    bx, by = 1260 * s - bw / 2, 540 * s - bh / 2
    d.rectangle([bx - 8 * s, by - 8 * s, bx + bw + 8 * s, by + bh + 8 * s], fill=(30, 28, 26, 255))
    d.rectangle([bx, by, bx + bw, by + bh], fill=CREAM, outline=CHALK + (255,), width=max(2, int(3 * s)))
    d.line([(bx + bw / 2, by), (bx + bw / 2, by + bh)], fill=(90, 84, 74, 255), width=max(2, int(3 * s)))
    sp = C['spreads'][k].resize((int(bw), int(bh)), Image.LANCZOS)
    ink = Image.new('RGBA', sp.size, (38, 30, 24, 255)); ink.putalpha(sp.split()[3])
    img.alpha_composite(ink, (int(bx), int(by)))
    for f in FLIPS:                                               # the right-hand page turning over the spine
        u = (t - f + .15) / .15
        if 0 <= u < 1:
            wpg = bw / 2 * math.cos(math.pi * u)
            x0 = bx + bw / 2
            d.polygon([(x0, by), (x0 + wpg, by - 18 * s * math.sin(math.pi * u)), (x0 + wpg, by + bh + 18 * s * math.sin(math.pi * u)), (x0, by + bh)],
                      fill=(232, 224, 206, 255), outline=CHALK + (255,))
    # the finger, down the rows of the right-hand page
    seg = [(T_DESK, FLIPS[0] - .15), (FLIPS[0] + .02, FLIPS[1] - .15), (FLIPS[1] + .02, T_END - .1)][k]
    u = clamp((t - seg[0]) / (seg[1] - seg[0]))
    row = u * 11.6
    if k == 2:                                                    # at 爱 it stops a moment, looks, goes on
        ta, tb = seg[0] + .16, seg[0] + .38
        row = 6. * ease((t - seg[0]) / .16) if t < ta else (6. if t < tb else 6. + 5.6 * ease((t - tb) / (seg[1] - tb)))
    fx = bx + bw / 2 + 40 * s
    fy = by + (100 + row * 70 + 20) / 980 * bh
    lw = max(2, int(3 * s)); HAND = (60, 56, 50, 235)
    d.rounded_rectangle([fx - 120 * s, fy - 11 * s, fx + 6 * s, fy + 11 * s], radius=int(11 * s), fill=HAND, outline=CHALK + (255,), width=lw)   # the finger
    d.rounded_rectangle([fx - 250 * s, fy - 30 * s, fx - 100 * s, fy + 46 * s], radius=int(26 * s), fill=HAND, outline=CHALK + (255,), width=lw)  # the hand
    for i in range(3):                                                                                                                         # the curled fingers
        d.rounded_rectangle([fx - (150 - i * 2) * s, fy + (4 + i * 13) * s, fx - 92 * s, fy + (16 + i * 13) * s], radius=int(6 * s), fill=HAND, outline=CHALK + (255,), width=max(1, lw - 1))
    d.line([(fx - 250 * s, fy - 10 * s), (fx - 420 * s, fy - 40 * s)], fill=CHALK + (255,), width=lw)                                          # the cuff, the arm
    d.line([(fx - 250 * s, fy + 40 * s), (fx - 420 * s, fy + 30 * s)], fill=CHALK + (255,), width=lw)
    # the answer slip, blank
    d.rectangle([150 * s, 880 * s, 640 * s, 975 * s], fill=CREAM, outline=CHALK + (255,), width=max(2, int(3 * s)))
    d.text((170 * s, 892 * s), 'Reply:', font=ImageFont.truetype(F + 'cour.ttf', int(22 * s)), fill=(38, 30, 24, 255))
    # a faint frame and a note: the detail view
    d.rectangle([22 * s, 22 * s, w - 22 * s, h - 22 * s], outline=CHALK + (110,), width=max(1, int(2 * s)))
    d.text((60 * s, 50 * s), 'Detail at the desk.   B. Rule book, pp. ' + str(212 + 2 * k) + '–' + str(213 + 2 * k), font=ImageFont.truetype(F + 'cour.ttf', int(18 * s)), fill=CHALK + (200,))
    return img


def textures(t, w, h):
    img = _frame_room(t, w, h) if t < T_DESK else _frame_desk(t, w, h)
    return {'u_img': img}
