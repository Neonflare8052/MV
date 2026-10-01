"""s14g · 2:52.712–2:54.975  the Chinese Room, in plan: one take, the same eye as the letter's (straight down), only
orthographic pans and zooms.  The night sheet: chalk on black.  (draft v1)

2:52.712 EXECUTION            the letter (its back up: a red 爱, upright) is where it was; the view pulls out and it goes
                              through the slot in the left wall, onto the desk in front of the man.  The whole plan.
2:53.643 Though we are trapped   in on the desk.  The rule book: each row a character → a reply that means something.  His
                              finger runs down the rows; a page turns on the beat; it stops at 爱 → see shelf C, no. 3 —
                              the one line in the book he can read (Searle: the rules are in English).
2:54.348                      he reaches to the shelf by the desk and draws out file C-3; a detail opens from it:
                              M.U.C.'s love letter (Strachey, Manchester Mark 1, 1952; text as printed in Encounter, 1954).
2:54.5 … 2:54.82              a modern pointer — not drawn, not ours — comes in and double-clicks the detail while it is still
                              unfolding.  (s15: at 2:54.975 the whole sheet is shoved into a window.)

plan_frame(t, w, h) draws the sheet at any size (the chat shot shows it inside its window)."""
import sys, math, random, importlib.util
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

_D = Path(__file__).resolve().parent
sys.path.insert(0, str(_D.parents[1] / 'tests' / 't11_assembly'))
import drafting
_sp = importlib.util.spec_from_file_location('s14e_g', _D / 's14e_letter.py'); S14E = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(S14E)

T0, TZ1, TD, FLIP, T_FIND, T_REACH, T_LAY, T_SQ = 172.712, 173.35, 173.643, 173.884, 174.10, 174.348, 174.62, 174.975
CLICKS = (174.70, 174.82)
POST = dict(u_bloom=0., u_ca=0., u_grain=.012)
F = 'C:/Windows/Fonts/'
CHALK = (232, 227, 214)
NIGHT = (13, 12, 11, 255)
PAPER = (246, 241, 229)
INK = (38, 30, 24)
RED = (178, 24, 30)
BLUE = (38, 110, 230)


def clamp(x, a=0., b=1.): return a if x < a else b if x > b else x
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def outc(x): x = clamp(x); return 1 - (1 - x) ** 3
def lerp(a, b, k): return a + (b - a) * k


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


# ---------------- the room (metres; x east, y south — screen down)
RW, RD, WT = 3.6, 2.6, .24                     # inside width, depth; wall thickness
SLOT_IN = (1.1, 1.5)                           # left wall, y
SLOT_OUT = (2.9, 3.3)                          # north wall, x
DESK = (1.2, 1.1, 2.6, 1.8)
LET = (.2125, .297)                            # the letter, as big as it was in s14e at the cut
LET0, LET1 = (-.62, 1.3), (1.5, 1.46)          # outside the slot; on the desk before him
BOOK_C, PG = (2.05, 1.45), (.28, .40)          # the open rule book: centre; one page
SHELF = (2.8, .95, 3.2, 1.95)                  # C: the files, by the desk (six pigeonholes, C-1 at the top)
FOLD0, FOLD1 = (3.0, 1.37), (2.3, 1.5)         # file C-3: in its hole; on the desk
MAN = (1.9, 2.12)
S0 = 875. / LET[1]                             # px per metre (1080p units) at the cut: the letter as tall as in s14e
S1, CAM1 = 280., (2.2, 1.32)                  # the whole plan
S2, CAM2 = 1300., (2.0, 1.45)                  # the desk
S3, CAM3 = 1000., (2.35, 1.45)                 # the desk and the shelf


def cam(t):
    """(cx, cy, px per metre)"""
    if t < TD:
        u = (t - T0) / (TZ1 - T0)
        e = outc(u); f = ease(u)                              # zoom out at once; the eye leaves the letter more slowly
        lx, ly = letter_pos(t)[:2]
        sc = S0 * (S1 / S0) ** e
        return lerp(lx, CAM1[0], f), lerp(ly, CAM1[1], f), sc
    if t < T_REACH:
        e = ease((t - TD) / .24)
        return lerp(CAM1[0], CAM2[0], e), lerp(CAM1[1], CAM2[1], e), S1 * (S2 / S1) ** e
    e = ease((t - T_REACH) / .16)
    return lerp(CAM2[0], CAM3[0], e), lerp(CAM2[1], CAM3[1], e), S2 * (S3 / S2) ** e


def letter_pos(t):
    """centre x, y, rotation (deg): through the slot, onto the desk"""
    a = ease((t - (T0 + .08)) / .32)                     # to just inside the wall
    b = ease((t - (T0 + .40)) / .3)                      # across to the desk
    mid = (.2, 1.3)
    x = lerp(LET0[0], mid[0], a); y = LET0[1]
    x = lerp(x, LET1[0], b); y = lerp(y, LET1[1], b)
    return x, y, 3. * b


# ---------------- the rule book: a character → a reply that means something.  爱 → an instruction, in English.
SPREADS = [
    ([('你好', '你好。'), ('谢谢', '不客气。'), ('对不起', '没关系。'), ('早上好', '早上好。'), ('几点了', '请看钟。'),
      ('下雨了吗', '没有。'), ('你吃了吗', '吃了。'), ('再见', '再见。'), ('你懂中文吗', '懂。')],
     [('你叫什么', '我没有名字。'), ('你在哪里', '这里。'), ('你快乐吗', '快乐。'), ('晚安', '晚安。'), ('我不懂', '慢慢来。'),
      ('你还在吗', '在。'), ('为什么', '因为。'), ('你会写诗吗', '会。'), ('你是人吗', '请再问一次。')]),
    ([('喜欢', '我也喜欢。'), ('想你', '我也想你。'), ('永远', '多久？'), ('记得', '记得。'), ('忘记', '不会。'),
      ('家', '在这里。'), ('朋友', '你。'), ('心', '在跳。'), ('恨', '为什么？')],
     [('怕', '别怕。'), ('哭', '我在。'), ('等', '我等。'), ('信', '已收到。'), ('爱', None), ('梦', '梦见你。'),
      ('真', '真的。'), ('机器', '是我。'), ('再见', '再见。')]),
]
ROW0, ROWH = .05, .038
AI_REPLY = 'see shelf C, no. 3'                # what the book says for 爱 (s14e_desk sets its own)
MUC = ['DARLING SWEETHEART', '',
       'YOU ARE MY AVID FELLOW FEELING. MY', 'AFFECTION CURIOUSLY CLINGS TO YOUR', 'PASSIONATE WISH. MY LIKING YEARNS', 'FOR YOUR HEART. YOU ARE MY WISTFUL',
       'SYMPATHY: MY TENDER LIKING.', '', '                YOURS BEAUTIFULLY', '', '                           M. U. C.']


_FONTS = {}


class V:
    """The sheet for one frame, seen through the camera: world metres -> 1080p units."""
    def __init__(self, w, h, c, seed=90):
        self.S = drafting.Sheet(w, h, seed=seed)
        self.S.fonts = _FONTS.setdefault(round(self.S.k, 4), {})
        self.Wt = w * 1080 / h
        self.cx, self.cy, self.sc = c
        self.lw = clamp((self.sc / 300) ** .35, .8, 2.6)

    def P(self, x, y): return (self.Wt / 2 + (x - self.cx) * self.sc, 540 + (y - self.cy) * self.sc)
    def Ps(self, pts): return [self.P(*p) for p in pts]

    def seen(self, x0, y0, x1, y1, m=40):
        a, b = self.P(x0, y0); c, d = self.P(x1, y1)
        return c > -m and a < self.Wt + m and d > -m and b < 1080 + m

    def fill(self, pts, col):
        k = self.S.k
        self.S.d.polygon([(a * k, b * k) for a, b in self.Ps(pts)], fill=col)

    def line(self, pts, w=1., a=235, amp=.25, col=CHALK, dash=None):
        self.S.line(self.Ps(pts), w=w * self.lw, col=col, alpha=a, amp=amp, dash=dash)

    def rect(self, x0, y0, x1, y1, fill=None, **kw):
        if not self.seen(x0, y0, x1, y1): return
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        if fill: self.fill(pts, fill)
        self.line(pts + [pts[0]], **kw)

    def circle(self, x, y, r, fill=None, n=40, **kw):
        if not self.seen(x - r, y - r, x + r, y + r): return
        pts = [(x + r * math.cos(2 * math.pi * i / n), y + r * math.sin(2 * math.pi * i / n)) for i in range(n + 1)]
        if fill: self.fill(pts, fill)
        self.line(pts, **kw)

    def text(self, x, y, s, font, size_m, col=CHALK, a=235, anchor='la'):
        sz = size_m * self.sc
        if sz < 3.5: return
        sz = round(sz * 2) / 2
        X, Y = self.P(x, y)
        if X > self.Wt + 400 or X < -900 or Y < -200 or Y > 1300: return
        self.S.text(X, Y, s, font, sz, col=col, alpha=a, anchor=anchor)

    def hatch(self, x0, y0, x1, y1, sp=.06):
        """a cut wall: dark, with section lines at 45°"""
        if not self.seen(x0, y0, x1, y1): return
        self.fill([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], (30, 29, 27, 255))
        c = x0 - y1
        while c < x1 - y0:
            # the line x - y = c, clipped to the rect
            ya, yb = max(y0, x0 - c), min(y1, x1 - c)
            if yb > ya: self.line([(ya + c, ya), (yb + c, yb)], w=.45, a=150, amp=.05)
            c += sp
        self.line([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], w=1.5, amp=.15)


def _walls(v):
    L, T, R, B = -WT, -WT, RW + WT, RD + WT
    # west wall, with the input slot
    v.hatch(L, T, 0, SLOT_IN[0]); v.hatch(L, SLOT_IN[1], 0, B)
    # north wall, with the output slot
    v.hatch(0, T, SLOT_OUT[0], 0); v.hatch(SLOT_OUT[1], T, R, 0)
    v.hatch(RW, 0, R, B); v.hatch(0, RD, RW, B)
    for (a, b) in (SLOT_IN,):                                   # slot: the sill seen below the cut
        v.line([(L, a), (0, a)], w=.8); v.line([(L, b), (0, b)], w=.8)
        v.line([(L * .5, a), (L * .5, b)], w=.5, a=160)
    a, b = SLOT_OUT
    v.line([(a, T), (a, 0)], w=.8); v.line([(b, T), (b, 0)], w=.8); v.line([(a, T * .5), (b, T * .5)], w=.5, a=160)


def _furniture(v, t):
    # floor boards, faint
    for i in range(1, 18):
        x = i * RW / 18
        if v.seen(x - .01, 0, x + .01, RD): v.line([(x, 0), (x, RD)], w=.35, a=45, amp=.05)
    # shelves of rule books on the north wall
    v.rect(.25, 0, 2.55, .34, fill=(20, 19, 18, 255), w=1.)
    if v.seen(.25, 0, 2.55, .34):
        r = random.Random(4); x = .28
        while x < 2.5:
            bw = r.uniform(.035, .07)
            v.rect(x, .03, x + bw, .03 + r.uniform(.22, .3), w=.45, a=190, amp=.02)
            x += bw + .006
    # the desk, the lamp
    v.rect(*DESK, fill=(24, 23, 21, 255), w=1.3)
    v.circle(1.3, 1.2, .07, fill=(30, 29, 27, 255), w=.9)
    v.circle(1.3, 1.2, .025, w=.6)
    # the chair, the man (from above: shoulders, head)
    mx, my = MAN
    v.rect(mx - .22, my - .05, mx + .22, my + .34, fill=(22, 21, 19, 255), w=.9)
    # the files: shelf C, six pigeonholes
    x0, y0, x1, y1 = SHELF
    v.rect(x0, y0, x1, y1, fill=(20, 19, 18, 255), w=1.2)
    for i in range(6):
        ya = y0 + i * (y1 - y0) / 6
        if i: v.line([(x0, ya), (x1, ya)], w=.8)
        if i == 2 and t >= T_REACH + .1: continue                  # C-3 has been taken out
        for j in range(5):
            xx = x0 + .06 + j * .05
            v.line([(xx, ya + .025), (xx, ya + (y1 - y0) / 6 - .025)], w=.45, a=170, amp=.02)
    for i in range(6):
        ya = y0 + (i + .5) * (y1 - y0) / 6
        v.text(x0 - .015, ya, f'C-{i + 1}', 'cour.ttf', .028, anchor='rm', a=200)


def _book(v, t):
    bx, by = BOOK_C; pw, ph = PG
    k = 1 if t >= FLIP else 0
    v.rect(bx - pw - .012, by - ph / 2 - .012, bx + pw + .012, by + ph / 2 + .012, fill=(34, 32, 29, 255), w=.8)
    def page(side, sp, x0):
        v.rect(x0, by - ph / 2, x0 + pw, by + ph / 2, fill=PAPER + (255,), col=CHALK, w=1.)
        rows = SPREADS[sp][side]
        v.text(x0 + pw / 2, by - ph / 2 + .022, str(212 + sp * 2 + side), 'cour.ttf', .014, col=INK, anchor='mm', a=170)
        for i, (q, a) in enumerate(rows):
            y = by - ph / 2 + ROW0 + i * ROWH
            v.text(x0 + .03, y + .016, q, 'simsun.ttc', .017, col=INK, anchor='lm')
            v.text(x0 + .127, y + .016, '→', 'cour.ttf', .015, col=INK, anchor='mm', a=200)
            if a is None: v.text(x0 + .14, y + .016, AI_REPLY, 'couri.ttf', .0118, col=INK, anchor='lm')
            else: v.text(x0 + .14, y + .016, a, 'simsun.ttc', .017, col=INK, anchor='lm')
            v.line([(x0 + .012, y + .034), (x0 + pw - .012, y + .034)], w=.3, a=70, col=INK, amp=.02)
    # the page turning (right to left over the spine)
    u = (t - FLIP + .07) / .14
    if 0 <= u < 1:
        page(0, 0, bx - pw); page(1, 1, bx)
        wpg = pw * math.cos(math.pi * u)
        lift = .02 * math.sin(math.pi * u)
        pts = [(bx, by - ph / 2), (bx + wpg, by - ph / 2 - lift), (bx + wpg, by + ph / 2 + lift), (bx, by + ph / 2)]
        v.fill(pts, (232, 224, 206, 255)); v.line(pts + [pts[0]], w=1.)
    else:
        page(0, k, bx - pw); page(1, k, bx)
    v.line([(bx, by - ph / 2), (bx, by + ph / 2)], w=1., col=(90, 84, 74), a=255)


def finger_at(t):
    """where the fingertip is, and whether it is on the page"""
    bx, by = BOOK_C; pw, ph = PG
    def row(side, i): return (bx - pw + side * pw + .006, by - ph / 2 + ROW0 + i * ROWH + .022)
    segs = [(173.40, 173.60, 0, 0, 8), (173.62, 173.82, 1, 0, 8), (173.95, 174.02, 0, 0, 8), (174.03, T_FIND, 1, 0, 4)]
    if t < segs[0][0]: return row(0, 0), False
    for t0, t1, side, a, b in segs:
        if t < t0: return row(side, a), False                        # lifted between runs (the page turns)
        if t <= t1:
            i = a + (b - a) * clamp((t - t0) / (t1 - t0))
            return (row(side, 0)[0], row(side, 0)[1] + i * ROWH), True
    if t < T_REACH: return row(1, 4), True                          # it stays on 爱
    return None, False


def _hands(v, t):
    mx, my = MAN
    # the left hand keeps the letter
    lx, ly, _ = letter_pos(t)
    lh = (lx + .1, ly + .15) if t > T0 + .75 else (1.65, 1.76)
    # the right hand: along the rows; to the shelf; back with the file
    tip, on = finger_at(t)
    if tip is None:
        if t < T_LAY:
            a = ease((t - T_REACH) / .12); b = ease((t - T_REACH - .14) / .14)
            p0 = finger_at(T_REACH - .01)[0]
            tip = (lerp(lerp(p0[0], FOLD0[0] - .05, a), FOLD1[0] + .02, b), lerp(lerp(p0[1], FOLD0[1], a), FOLD1[1] + .1, b))
        else:
            b = ease((t - T_LAY) / .2)
            tip = (lerp(FOLD1[0] + .02, 2.3, b), lerp(FOLD1[1] + .1, 1.85, b))
    rh = (tip[0] + .015, tip[1] + .09)
    for (sx, sy), (hx, hy) in (((mx - .2, my - .02), lh), ((mx + .2, my - .02), rh)):
        dx, dy = hx - sx, hy - sy; L = math.hypot(dx, dy) or 1; nx, ny = -dy / L * .035, dx / L * .035
        arm = [(sx + nx, sy + ny), (hx + nx * .8, hy + ny * .8), (hx - nx * .8, hy - ny * .8), (sx - nx, sy - ny)]
        if v.seen(min(sx, hx) - .1, min(sy, hy) - .1, max(sx, hx) + .1, max(sy, hy) + .1):
            v.fill(arm, (40, 38, 35, 255)); v.line(arm, w=1.)
    for (hx, hy), finger in ((lh, False), (rh, True)):
        pts = [(hx + .042 * math.cos(a_) , hy + .052 * math.sin(a_)) for a_ in [2 * math.pi * i / 24 for i in range(25)]]
        if v.seen(hx - .1, hy - .15, hx + .1, hy + .1):
            v.fill(pts, (48, 46, 42, 255)); v.line(pts, w=1.)
            if finger:
                fp = [(hx - .014, hy - .04), (hx - .014, hy - .095), (hx - .008, hy - .1), (hx - .002, hy - .095), (hx - .002, hy - .04)]
                v.fill(fp, (48, 46, 42, 255)); v.line(fp, w=.9)
    # shoulders and head over the arms
    sh = [(mx + .24 * math.cos(a_), my + .11 * math.sin(a_)) for a_ in [2 * math.pi * i / 40 for i in range(41)]]
    if v.seen(mx - .3, my - .2, mx + .3, my + .2):
        v.fill(sh, (36, 34, 31, 255)); v.line(sh, w=1.2)
        v.circle(mx, my - .005, .095, fill=(44, 42, 38, 255), w=1.2)


def _file(v, t):
    """C-3: a buff folder; in its hole, then drawn out onto the desk"""
    a = ease((t - T_REACH - .14) / .14)
    if t < T_REACH + .1: return
    x = lerp(FOLD0[0], FOLD1[0], a); y = lerp(FOLD0[1], FOLD1[1], a)
    hw, hh = .115, .155
    pts = [(x - hw, y - hh), (x + hw, y - hh), (x + hw, y + hh), (x - hw, y + hh)]
    v.fill(pts, (214, 196, 158, 255)); v.line(pts + [pts[0]], w=1.1)
    v.line([(x - hw, y - hh + .03), (x + hw, y - hh + .03)], w=.5, col=INK, a=150)
    v.text(x, y - hh + .06, 'C-3', 'courbd.ttf', .03, col=INK, anchor='mm')
    v.text(x, y - hh + .1, 'M.U.C.', 'cour.ttf', .024, col=INK, anchor='mm')
    v.text(x, y - hh + .13, 'love letters', 'cour.ttf', .017, col=INK, anchor='mm', a=200)


_LET = {}


def _letter_img():
    if 'img' not in _LET:
        back = S14E._back(); front = S14E._front().transpose(Image.FLIP_LEFT_RIGHT)
        Wf, Hf = back.size
        img = Image.new('RGBA', (Wf, Hf), PAPER + (255,))
        d = ImageDraw.Draw(img)
        for f in (1 / 3, 2 / 3): d.line([(0, Hf * f), (Wf, Hf * f)], fill=(222, 216, 202, 255), width=5)
        sh = Image.new('RGBA', img.size, INK + (255,)); sh.putalpha(front.split()[3].point(lambda a: int(a * .07)))
        img.alpha_composite(sh)
        red = Image.new('RGBA', img.size, RED + (255,)); red.putalpha(back.split()[3].point(lambda a: int(a * .92)))
        img.alpha_composite(red)
        _LET['img'] = img
    return _LET['img']


def _letter(v, img, t):
    x, y, rot = letter_pos(t)
    wpx, hpx = LET[0] * v.sc, LET[1] * v.sc
    k = img.height / 1080
    W, H = int(wpx * k), int(hpx * k)
    if W < 2: return
    cx, cy = v.P(x, y)
    if cx < -wpx or cx > v.Wt + wpx: return
    spr = _letter_img().resize((W, H), Image.LANCZOS)
    lw = max(2, int(2.6 * k * clamp(v.sc / S0, .45, 1.)))
    ImageDraw.Draw(spr).rectangle([0, 0, W - 1, H - 1], outline=INK + (255,), width=lw)
    if abs(rot) > .05: spr = spr.rotate(-rot, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(spr, (int(cx * k - spr.width / 2), int(cy * k - spr.height / 2)))


def _overlay(w, h, alpha):
    """screen-fixed: legend, north point, scale, title block (only while the whole plan is in view)"""
    S = drafting.Sheet(w, h, seed=91); S.fonts = _FONTS.setdefault(round(S.k, 4), {})
    Wt = w * 1080 / h
    drafting.border(S)
    T = 'cour.ttf'; x = Wt - 420
    S.text(x, 80, 'THE CHINESE ROOM.', 'COPRGTL.TTF', 22, col=CHALK)
    S.text(x, 114, 'Plan, cut at 1.1 m.', T, 16, col=CHALK, alpha=200)
    for i, (l, t_) in enumerate([('A.', 'Input slot'), ('B.', 'Rule books (English)'), ('C.', 'Files'), ('D.', 'Output slot'), ('E.', 'Operator:'), ('', 'understands no Chinese')]):
        S.text(x + 4, 170 + i * 28, l, 'BASKVILL.TTF', 18, col=CHALK)
        S.text(x + 38, 173 + i * 28, t_, T, 15, col=CHALK, alpha=210)
    # north point
    nx, ny = Wt - 110, 420
    S.ellipse(nx, ny, 34, 34, w=1., col=CHALK, amp=.1)
    S.line([(nx, ny + 30), (nx, ny - 44)], w=1.2, col=CHALK, amp=.05); S.arrow(nx, ny - 20, nx, ny - 46, col=CHALK)
    S.text(nx, ny - 64, 'N', 'BASKVILL.TTF', 20, col=CHALK, anchor='mm')
    # scale (1 m = S1 units)
    sx, sy = x, 560
    S.text(sx, sy - 30, 'Scale  (m)', T, 15, col=CHALK, alpha=200)
    S.poly([(sx, sy), (sx + 2 * S1 * .5, sy), (sx + 2 * S1 * .5, sy + 8), (sx, sy + 8)], w=.9, col=CHALK, amp=.1)
    S.d.rectangle([sx * S.k, sy * S.k, (sx + S1 * .5) * S.k, (sy + 8) * S.k], fill=CHALK + (200,))
    for i, lab in enumerate(['0', '.5', '1']): S.text(sx + i * S1 * .5, sy + 24, lab, T, 13, col=CHALK, anchor='mm')
    tx, ty = Wt - 440, 888
    S.poly([(tx, ty), (tx + 380, ty), (tx + 380, ty + 150), (tx, ty + 150)], w=1.5, col=CHALK, amp=.3)
    S.line([(tx, ty + 62), (tx + 380, ty + 62)], w=.8, col=CHALK, amp=.2)
    S.text(tx + 190, ty + 33, 'THE CHINESE ROOM.', 'ENGR.TTF', 24, col=CHALK, anchor='mm')
    S.text(tx + 190, ty + 90, 'after J. R. Searle,  1980.', 'GARAIT.TTF', 21, col=CHALK, anchor='mm')
    S.text(tx + 190, ty + 124, 'Minds, Brains, and Programs', 'GARAIT.TTF', 16, col=CHALK, alpha=200, anchor='mm')
    img = S.result()
    img = Image.merge('RGBA', (*Image.new('RGB', img.size, CHALK).split(), img.split()[3].point(lambda a: int(a * alpha))))
    return img


def _labels(v):
    for pt, off, L in [((-.12, 1.3), (-.5, -.55), 'A'), ((1.4, .2), (-.35, -.45), 'B'), ((3.2, 1.2), (.4, -.5), 'C'),
                       ((3.1, -.12), (.25, -.45), 'D'), ((1.9, 2.2), (-.6, .45), 'E')]:
        x, y = v.P(*pt); tx, ty = v.P(pt[0] + off[0], pt[1] + off[1])
        if -50 < x < v.Wt + 50 and -50 < y < 1130: v.S.leader(x, y, tx, ty, L)
    # overall dimensions
    if v.sc < 500:
        v.S.dim(v.P(0, RD + WT), v.P(RW, RD + WT), 34, '3600', size=15)
        v.S.dim(v.P(-WT, 0), v.P(-WT, RD), 34, '2600', size=15)


# ---------------- the detail: M.U.C.'s letter, unrolling out of file C-3
def detail(v, img, t, sel=0.):
    if t < T_LAY: return
    k = img.height / 1080
    fx, fy = v.P(*FOLD1)
    c = ease((t - T_LAY) / .08)
    r = .2 * v.sc
    if c > 0: v.S.ellipse(fx, fy, r, r, a0=-math.pi / 2, a1=-math.pi / 2 + 2 * math.pi * c, w=1.2, col=CHALK, amp=.2)
    X0, Y0, X1, Y1 = v.Wt * .5 - 830, 70, v.Wt * .5 - 150, 600          # the panel
    ln = ease((t - T_LAY - .04) / .06)
    if ln > 0:
        ax, ay = fx - r * .7, fy - r * .7
        v.S.line([(ax, ay), (ax + (X1 - ax) * ln, ay + (Y1 - ay) * ln)], w=1., col=CHALK, amp=.2)
    u = outc((t - T_LAY - .08) / .45)                                  # unrolling, top to bottom
    if u <= 0: return
    yb = Y0 + (Y1 - Y0) * u
    v.S.text(X0, Y0 - 34, 'Detail C-3.   M.U.C. (Strachey, Manchester Mark 1, 1952)', 'cour.ttf', 15, col=CHALK, alpha=220)
    return (X0, Y0, X1, yb, u, sel)


def _panel(img, box, t):
    X0, Y0, X1, yb, u, sel = box
    k = img.height / 1080
    d = ImageDraw.Draw(img)
    d.rectangle([X0 * k, Y0 * k, X1 * k, yb * k], fill=(240, 233, 216, 255), outline=CHALK + (255,), width=max(1, int(2 * k)))
    # the teleprinter's lines, revealed as it unrolls
    f = _font('cour.ttf', int(22 * k)); fb = _font('courbd.ttf', int(22 * k))
    for i, ln in enumerate(MUC):
        y = Y0 + 40 + i * 42
        if y + 30 > yb: break
        d.text(((X0 + 40) * k, y * k), ln, font=fb if i in (0, 10) else f, fill=INK + (240,))
    # the paper's roll edge while it is still unrolling
    if u < 1: d.rectangle([(X0 - 6) * k, (yb - 6) * k, (X1 + 6) * k, (yb + 8) * k], fill=(214, 206, 188, 255), outline=CHALK + (255,), width=max(1, int(2 * k)))
    if sel > 0:                                                         # selected: the system's blue, not ours
        ov = Image.new('RGBA', img.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        od.rectangle([(X0 - 8) * k, (Y0 - 8) * k, (X1 + 8) * k, (yb + 10) * k], fill=BLUE + (int(20 * sel),), outline=BLUE + (int(255 * sel),), width=max(2, int(3 * k)))
        img.alpha_composite(ov)


def _font(name, size):
    key = (name, size)
    if key not in _FONTS: _FONTS[key] = ImageFont.truetype(F + name, max(1, size))
    return _FONTS[key]


_OV = {}


def plan_frame(t, w, h):
    c = cam(t)
    v = V(w, h, c)
    _walls(v)
    _furniture(v, t)
    _book(v, t)
    _labels(v)
    img = Image.new('RGBA', (w, h), NIGHT)
    img.alpha_composite(v.S.result())
    # moving things, drawn over the sheet
    v2 = V(w, h, c, seed=92)
    _file(v2, t)
    _hands(v2, t)
    bx = None
    if t >= T_LAY:
        bx = detail(v2, img, t, sel=1. if CLICKS[0] <= t < T_SQ else 0.)
    img.alpha_composite(v2.S.result())
    _letter(v, img, t)
    if bx: _panel(img, bx, t)
    # the whole-plan furniture of a sheet: in while the plan is all in view
    oa = clamp((600 - c[2]) / 250) * (1 - ease((t - TD) / .12))
    if oa > .01:
        if (w, h) not in _OV: _OV[(w, h)] = _overlay(w, h, 1.)
        ov = _OV[(w, h)]
        if oa < .99: ov = Image.merge('RGBA', (*ov.split()[:3], ov.split()[3].point(lambda a: int(a * oa))))
        img.alpha_composite(ov)
    return img


# ---------------- the pointer: a clean system arrow, not drawn in chalk
ARROW = [(0, 0), (0, 25), (6, 19.5), (10.5, 29), (14.5, 27.2), (10.2, 18), (18, 18)]


def pointer(img, x, y, k, busy=None):
    """x, y in 1080p units; tip at x, y.  busy: an angle -> the gapped ring spinning instead"""
    d = ImageDraw.Draw(img)
    if busy is not None:
        r = 11 * k
        cx, cy = x * k + 14 * k, y * k + 14 * k
        pointer(img, x, y, k)
        a0 = math.degrees(busy)
        d.arc([cx, cy, cx + 2 * r, cy + 2 * r], a0, a0 + 300, fill=(40, 40, 44, 255), width=max(2, int(3.4 * k)))
        return
    s = 1.1 * k
    pts = [(x * k + px * s, y * k + py * s) for px, py in ARROW]
    sh = [(a + 2 * k, b + 2 * k) for a, b in pts]
    d.polygon(sh, fill=(0, 0, 0, 90))
    d.polygon(pts, fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
    d.line(pts + [pts[0]], fill=(0, 0, 0, 255), width=max(1, int(1.3 * k)))


def pointer_path(t, Wt):
    """into the frame from the lower right, onto the unrolling detail"""
    a = ease((t - 174.50) / .17)
    x = lerp(Wt + 20, Wt * .5 - 470, a) + 40 * math.sin(a * math.pi) ** 2
    y = lerp(1100, 300, a) - 30 * math.sin(a * math.pi)
    return x, y


def textures(t, w, h):
    img = plan_frame(t, w, h)
    if t >= 174.50:
        x, y = pointer_path(t, w * 1080 / h)
        pointer(img, x, y, h / 1080)
    return {'u_img': img}
