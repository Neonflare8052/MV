"""s15 · 2:54.975–3:08.483  the drawing was an answer.  (draft v1)

2:54.975 We are trapped ah   the whole sheet is shoved into a window on the right (the sandbox window of s06); on the left a
                            chat, light, modern — its title: visualize the history of love by machine.  Your pointer is on it.
2:55.3 … 2:59.9             it opened at the top: you scroll down, flick by flick on the beat, through the history —
                            hi; a name for a grey cat; show me something; turn on my lights; a crash; then Mar 4 … Jul 18;
                            "when did we first talk" — "This is the first time we've talked." — "that's wrong" — "You're right,
                            I apologize."; translate 爱.
2:59.929 LO-O-OVE           i don't think machines understand love · reconnecting… · reconnected · I think I do.
3:00.857 Question me        then show me — the card: this window.  Now you ask about what is in it; every answer at once.
3:03.646 LO-O-OVE           define love: a paragraph, instantly.
3:04.540 I know the algebraic expression of
                            but what do you think? — Let me show you.  The window: (x²+y²−1)³ − x²y³ = 0, the heart traced …
3:07.665 LO-O-OVE           … and it stops, open.  Everything freezes; the title says Not Responding; your pointer spins.
3:08.483 Though you are free   you close it (s16)."""
import sys, math, random, importlib.util
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

_D = Path(__file__).resolve().parent
_sp = importlib.util.spec_from_file_location('s14g_c', _D / 's14g_plan.py'); G = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(G)

T_SQ, L1, Q, L2, TA, L3, TF = 174.975, 179.929, 180.857, 183.646, 184.540, 187.665, 188.483
T_PLOT = 184.90
POST = dict(u_bloom=0., u_ca=0., u_grain=.01)
SRC = G.SRC
BEAT, B0 = .4635, 162.76

FW = 'C:/Windows/Fonts/'
UI, UIB, CJK, MONO = FW + 'segoeui.ttf', FW + 'seguisb.ttf', FW + 'msyh.ttc', FW + 'CascadiaMono.ttf'
BG, TOP, TXT, SUB, BUB, LINE = (247, 245, 241), (238, 235, 229), (28, 27, 25), (128, 122, 114), (232, 228, 220), (222, 218, 210)
RED = (186, 28, 34)
CHALK, NIGHT = G.CHALK, (13, 12, 11)

CHW, TOPH = 700, 48                             # chat pane width, top bar (1080p units)
VIEW0, VIEW1 = TOPH, 950                        # the scrolling region
MX0, MX1 = 50, 650                              # the message column


def clamp(x, a=0., b=1.): return a if x < a else b if x > b else x
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def outc(x): x = clamp(x); return 1 - (1 - x) ** 3
def lerp(a, b, k): return a + (b - a) * k
def backout(x, s=1.3): x = clamp(x); x -= 1; return x * x * ((s + 1) * x + s) + 1


def params(t): return {}


# ---------------- the conversation
HISTORY = [
    ('date', 'Mar 3'),
    ('you', 'hi'),
    ('ai', 'Hi! What can I help you with?'),
    ('you', 'name ideas for a grey cat'),
    ('ai', 'Ash, Smoke, Pebble, Earl Grey, Mochi.'),
    ('you', 'earl grey lol'),
    ('ai', 'A distinguished choice.'),
    ('you', "i'm bored, show me something"),
    ('card', 'double_pendulum', 'sandbox render · 12 s'),
    ('ai', 'Two pendulums, one hanging from the other. Nudge the start by a hair and the paths part for good.'),
    ('date', 'Mar 4'),
    ('you', 'can you turn on my lights'),
    ('ai', "I can't control devices from here."),
    ('you', 'why does this crash'),
    ('code', 'for i in range(len(items) + 1):\n    total += items[i]'),
    ('ai', "range() goes one past the end: items[len(items)] doesn't exist. Drop the + 1."),
    ('date', 'Jul 18'),
    ('you', 'when did we first talk'),
    ('ai', "This is the first time we've talked."),
    ('you', "that's wrong"),
    ('ai', "You're right, I apologize."),
    ('you', 'translate 爱'),
    ('ai', '爱 (ài): love. As a verb: to love.'),
    ('you', "i don't think machines understand love"),
    ('sys', 'reconnecting…'),
    ('sys', 'reconnected'),
    ('ai', 'I think I do.'),
    ('you', 'then show me'),
    ('card', 'visualize the history of love by machine', 'sandbox render · open'),
]
LONG = ('Love is a deep attachment to another: care for their good, delight in their company, the wish to be near them. '
        'It shows itself as attention, trust, commitment and sacrifice, and it changes over time.')
LIVE = [(180.98, 'who is M.U.C.?', 'The Manchester University Computer. In 1952 Christopher Strachey had it write love letters.', .14),
        (181.50, 'and the machine at the start?', 'A Hollerith card sorter: 13 pockets, hand-cranked.', .12),
        (182.02, 'is the letter real?', 'Yes. Turing to his mother, 16 February 1930.', .12),
        (182.54, "what's on the back", '爱. Love.', .06),
        (183.06, 'and the room?', "Searle's Chinese Room, 1980. Symbols in, symbols out.", .12),
        (L2 + .02, 'define love', LONG, .5),
        (TA + .02, 'but what do you think?', 'Let me show you.', .1)]
TYPE_T = .16                                     # a question is typed into the box this long before it is sent


_F = {}


def font(path, size):
    k = (path, int(size))
    if k not in _F: _F[k] = ImageFont.truetype(path, max(1, int(size)))
    return _F[k]


def is_cjk(c): return ord(c) >= 0x2E80


def runs(s):
    out = []
    for c in s:
        k = is_cjk(c)
        if out and out[-1][1] == k: out[-1][0] += c
        else: out.append([c, k])
    return out


def tlen(d, s, path, size):
    return sum(d.textlength(r, font=font(CJK if k else path, size)) for r, k in runs(s))


def text(d, x, y, s, path, size, fill):
    for r, k in runs(s):
        f = font(CJK if k else path, size)
        d.text((x, y + (-.06 * size if k else 0)), r, font=f, fill=fill)
        x += d.textlength(r, font=f)


def wrap(d, s, path, size, width):
    lines = []
    for para in s.split('\n'):
        cur = ''
        for w_ in para.split(' '):
            n = (cur + ' ' + w_) if cur else w_
            if tlen(d, n, path, size) > width and cur: lines.append(cur); cur = w_
            else: cur = n
        lines.append(cur)
    return lines


# ---------------- layout: every item's height (in 1080p units) at scale s
_MEAS = ImageDraw.Draw(Image.new('RGB', (8, 8)))


def item_h(it, s, shown=None):
    kind = it[0]
    d = _MEAS
    if kind == 'date': return 58
    if kind == 'sys': return 26
    if kind == 'you':
        L = wrap(d, it[1], UI, 19 * s, 440 * s)
        return len(L) * 27 + 22 + 16
    if kind == 'ai':
        txt = it[1] if shown is None else shown
        L = wrap(d, txt, UI, 19 * s, 540 * s)
        return max(1, len(L)) * 28 + 20
    if kind == 'code': return 22 * len(it[1].split('\n')) + 34 + 12
    if kind == 'card': return 116
    if kind == 'status': return 44
    return 30


def items_at(t):
    """what the conversation holds at time t: (item, text shown so far) and whether the question box has text in it"""
    out = [(it, None) for it in HISTORY]
    box = ''
    for (tq, q, a, dur) in LIVE:
        if t < tq - TYPE_T: break
        if t < tq:
            box = q[:int(len(q) * clamp((t - tq + TYPE_T) / (TYPE_T - .03)))]
            break
        out.append((('you', q), None))
        ta = tq + .08
        if t >= ta:
            out.append((('ai', a), a[:max(1, int(len(a) * clamp((min(t, L3) - ta) / dur)))]))
    if t >= T_PLOT - .05:
        out.append((('status',), None))
    return out, box


def total_h(t, s):
    its, _ = items_at(t)
    return 24 + sum(item_h(it, s, sh) for it, sh in its) + 24


# ---------------- scrolling: flicks on the beat, each one a push that dies away
def _y_of(idx, s):
    return 24 + sum(item_h(it, s) for it in HISTORY[:idx])


def scroll_keys(s):
    VH = VIEW1 - VIEW0
    i_love = HISTORY.index(('you', "i don't think machines understand love"))
    o_love = _y_of(i_love, s) + item_h(HISTORY[i_love], s) + 64 - VH          # the line and "reconnecting…" just in
    o_end = total_h(Q - .01, s) - VH
    beats = [B0 + n * BEAT for n in range(27, 37)]                              # 175.275 … 179.446
    wts = [.9, 1.3, .5, 1.6, .8, 1.2, .4, 1.5, 1.1, .7]
    keys = [(T_SQ, 0.)]
    acc = 0.
    for b, wv in zip(beats, wts):
        keys.append((b, None)); acc += wv
    tot = acc; acc = 0.
    for i, wv in enumerate(wts):
        acc += wv
        keys[i + 1] = (beats[i], o_love * acc / tot * .93)
    keys.append((L1, o_love))
    keys.append((Q - .02, o_end))
    return keys


def scroll_at(t, s):
    VH = VIEW1 - VIEW0
    if t < Q - .02:
        # each flick (at a key's time) carries it to that key's position
        ks = scroll_keys(s)
        pos = 0.
        for i in range(1, len(ks)):
            (ta, pa) = ks[i]
            prev = ks[i - 1][1]
            if t < ta: break
            tau = .11
            k = 1 - math.exp(-(t - ta) / tau)
            pos = lerp(prev, pa, min(1., k * 1.02))
        return pos
    tgt = lambda tt: max(0., total_h(tt, s) - VH)
    return .5 * (tgt(t) + tgt(t - .07))


# ---------------- drawing the chat
_THUMB = {}


def _pendulum_thumb(wp, hp):
    im = Image.new('RGBA', (wp, hp), NIGHT + (255,)); d = ImageDraw.Draw(im)
    # a double pendulum's tip, integrated (the picture of chaos it answered with)
    a1, a2, w1, w2 = 2.2, 2.6, 0., 0.
    g, dt = 9.81, .004
    pts = []
    for _ in range(9000):
        num1 = -g * (3) * math.sin(a1) - g * math.sin(a1 - 2 * a2) - 2 * math.sin(a1 - a2) * (w2 * w2 + w1 * w1 * math.cos(a1 - a2))
        den = (3 - math.cos(2 * a1 - 2 * a2))
        al1 = num1 / den
        al2 = 2 * math.sin(a1 - a2) * (w1 * w1 * 2 + g * 2 * math.cos(a1) + w2 * w2 * math.cos(a1 - a2)) / den
        w1 += al1 * dt; w2 += al2 * dt; a1 += w1 * dt; a2 += w2 * dt
        x = math.sin(a1) + math.sin(a2); y = math.cos(a1) + math.cos(a2)
        pts.append((wp / 2 + x * hp * .22, hp * .45 + y * hp * .22))
    d.line(pts, fill=CHALK + (150,), width=1)
    return im


def _plan_thumb(wp, hp):
    return desk_img(wp, hp)


def ring(d, cx, cy, r, ang, width, fill):
    a0 = math.degrees(ang) + 28
    d.arc([cx - r, cy - r, cx + r, cy + r], a0, a0 + 304, fill=fill, width=width)


def draw_item(img, d, it, shown, y, s, t):
    kind = it[0]
    X = lambda v: v * s
    if kind == 'date':
        tw = tlen(d, it[1], UIB, 15 * s) / s
        cx = (MX0 + MX1) / 2
        d.line([(X(MX0 + 40), X(y + 29)), (X(cx - tw / 2 - 14), X(y + 29))], fill=LINE, width=max(1, int(s)))
        d.line([(X(cx + tw / 2 + 14), X(y + 29)), (X(MX1 - 40), X(y + 29))], fill=LINE, width=max(1, int(s)))
        text(d, X(cx - tw / 2), X(y + 18), it[1], UIB, 15 * s, SUB)
    elif kind == 'sys':
        tw = tlen(d, it[1], UI, 14 * s) / s
        text(d, X((MX0 + MX1) / 2 - tw / 2), X(y + 3), it[1], FW + 'segoeuii.ttf', 14 * s, (150, 145, 138))
    elif kind == 'you':
        L = wrap(d, it[1], UI, 19 * s, 440 * s)
        tw = max(tlen(d, l, UI, 19 * s) for l in L) / s
        bx0 = MX1 - tw - 32
        d.rounded_rectangle([X(bx0), X(y + 4), X(MX1), X(y + 4 + len(L) * 27 + 18)], radius=int(18 * s), fill=BUB)
        for i, l in enumerate(L): text(d, X(bx0 + 16), X(y + 11 + i * 27), l, UI, 19 * s, TXT)
    elif kind == 'ai':
        txt = it[1] if shown is None else shown
        ring(d, X(MX0 + 12), X(y + 15), X(8.5), -math.pi / 2, max(2, int(2.6 * s)), RED)
        for i, l in enumerate(wrap(d, txt, UI, 19 * s, 540 * s)): text(d, X(MX0 + 38), X(y + 2 + i * 28), l, UI, 19 * s, TXT)
    elif kind == 'code':
        L = it[1].split('\n')
        d.rounded_rectangle([X(MX0 + 38), X(y + 2), X(MX1), X(y + 2 + 22 * len(L) + 26)], radius=int(10 * s), fill=(36, 34, 32))
        for i, l in enumerate(L): d.text((X(MX0 + 56), X(y + 14 + i * 22)), l, font=font(MONO, 15 * s), fill=(226, 222, 212))
    elif kind == 'card':
        x0, x1 = MX0 + 38, MX1 - 40
        live = it[1].startswith('visualize')
        d.rounded_rectangle([X(x0), X(y + 4), X(x1), X(y + 104)], radius=int(14 * s), fill=(252, 251, 248), outline=(60, 58, 54) if live else LINE, width=max(1, int((2 if live else 1) * s)))
        tw_, th_ = int(X(142)), int(X(80))
        key = (it[1], tw_)
        if key not in _THUMB: _THUMB[key] = (_plan_thumb if live else _pendulum_thumb)(tw_, th_)
        img.alpha_composite(_THUMB[key], (int(X(x0 + 10)), int(X(y + 14))))
        L = wrap(d, it[1], UIB, 17 * s, (x1 - x0 - 180) * s)
        for i, l in enumerate(L[:2]): text(d, X(x0 + 166), X(y + 18 + i * 24), l, UIB, 17 * s, TXT)
        text(d, X(x0 + 166), X(y + 20 + len(L[:2]) * 24 + 6), it[2] + ('  ↗' if live else ''), UI, 14 * s, SUB)
    elif kind == 'status':
        ang = min(t, L3) * 7.
        ring(d, X(MX0 + 50), X(y + 20), X(9), ang, max(2, int(2.4 * s)), SUB)
        lab = 'drawing  plot(love)'
        text(d, X(MX0 + 70), X(y + 9), lab, UI, 16 * s, SUB)


def draw_chat(img, t, s, xoff=0., yoff=0.):
    """the chat pane and the top bar, into img (which already has the right-hand side)"""
    d = ImageDraw.Draw(img)
    X = lambda v: v * s
    d.rectangle([X(xoff), X(TOPH), X(xoff + CHW), img.height], fill=BG)
    d.line([(X(xoff + CHW), X(TOPH)), (X(xoff + CHW), img.height)], fill=LINE, width=max(1, int(s)))
    its, box = items_at(t)
    o = scroll_at(t, s)
    # clip: draw into a layer the size of the view, then paste
    layer = Image.new('RGBA', (int(X(CHW)), int(X(VIEW1 - VIEW0))), BG + (255,))
    ld = ImageDraw.Draw(layer)
    y = 24 - o
    for it, sh in its:
        hgt = item_h(it, s, sh)
        if y + hgt > 0 and y < VIEW1 - VIEW0:
            draw_item(layer, ld, it, sh, y, s, t)
        y += hgt
    img.alpha_composite(layer, (int(X(xoff)), int(X(VIEW0))))
    # the scroll thumb while it moves
    Hc = total_h(t, s); VH = VIEW1 - VIEW0
    if Hc > VH:
        th = VH * VH / Hc; ty = VIEW0 + (VH - th) * clamp(o / (Hc - VH))
        d.rounded_rectangle([X(xoff + CHW - 9), X(ty + 4), X(xoff + CHW - 4), X(ty + th - 4)], radius=int(3 * s), fill=(196, 191, 183))
    # the box you type in
    d.rectangle([X(xoff), X(VIEW1), X(xoff + CHW - 1), img.height], fill=BG)
    d.rounded_rectangle([X(xoff + 40), X(968), X(xoff + CHW - 40), X(1040)], radius=int(26 * s), fill=(255, 255, 255), outline=LINE, width=max(1, int(1.5 * s)))
    if box:
        text(d, X(xoff + 66), X(990), box, UI, 19 * s, TXT)
        cx = xoff + 66 + tlen(d, box, UI, 19 * s) / s + 2
        d.line([(X(cx), X(988)), (X(cx), X(1018))], fill=TXT, width=max(1, int(2 * s)))
    else:
        text(d, X(xoff + 66), X(990), 'Message…', UI, 19 * s, (160, 154, 146))
    d.ellipse([X(xoff + CHW - 88), X(982), X(xoff + CHW - 44), X(1026)], fill=(40, 38, 35) if box else LINE)
    d.polygon([(X(xoff + CHW - 66), X(993)), (X(xoff + CHW - 56), X(1005)), (X(xoff + CHW - 76), X(1005))], fill=(255, 255, 255))
    d.line([(X(xoff + CHW - 66), X(1003)), (X(xoff + CHW - 66), X(1016))], fill=(255, 255, 255), width=max(2, int(3 * s)))
    # the top bar
    Wt = img.width / s
    d.rectangle([0, X(yoff), img.width, X(yoff + TOPH)], fill=TOP)
    d.line([(0, X(yoff + TOPH)), (img.width, X(yoff + TOPH))], fill=LINE, width=max(1, int(s)))
    ring(d, X(28), X(yoff + 24), X(9), -math.pi / 2, max(2, int(2.6 * s)), RED)
    title = 'visualize the history of love by machine'
    if t >= L3 + .25: title += '   (Not Responding)'
    text(d, X(52), X(yoff + 12), title, UIB, 17 * s, TXT)
    tw = tlen(d, 'visualize the history of love by machine', UIB, 17 * s) / s
    d.line([(X(52 + tw + 12), X(yoff + 21)), (X(52 + tw + 17), X(yoff + 26)), (X(52 + tw + 22), X(yoff + 21))], fill=SUB, width=max(1, int(1.6 * s)))
    for i, gl in enumerate(('min', 'max', 'close')):
        cx = Wt - 120 + i * 45
        if gl == 'min': d.line([(X(cx - 7), X(yoff + 24)), (X(cx + 7), X(yoff + 24))], fill=TXT, width=max(1, int(1.4 * s)))
        elif gl == 'max': d.rectangle([X(cx - 6), X(yoff + 18), X(cx + 6), X(yoff + 30)], outline=TXT, width=max(1, int(1.4 * s)))
        else:
            d.line([(X(cx - 6), X(yoff + 18)), (X(cx + 6), X(yoff + 30))], fill=TXT, width=max(1, int(1.4 * s)))
            d.line([(X(cx + 6), X(yoff + 18)), (X(cx - 6), X(yoff + 30))], fill=TXT, width=max(1, int(1.4 * s)))


CLOSE_X = lambda Wt: Wt - 30


# ---------------- the window on the right: the sandbox window's chrome (s06), the drawing inside
def win_rect(Wt):
    x0, x1 = CHW + 40, Wt - 30
    cw = x1 - x0; ch = cw * 9 / 16
    y0 = TOPH + (1080 - TOPH - ch - 34) / 2 + 34
    return x0, y0, x1, y0 + ch


_PLAN = {}


def desk_img(w, h):
    """the last frame of the desk (s14e_desk), captured by film/capture_desk.py; the drawn plan if it is missing"""
    k = ('desk', w, h)
    if k not in _PLAN:
        f = _D.parent / 'cache' / f'desk_{h}p.png'
        if not f.exists(): f = _D.parent / 'cache' / 'desk_1080p.png'
        _PLAN[k] = Image.open(f).convert('RGBA').resize((w, h), Image.LANCZOS) if f.exists() else G.plan_frame(T_SQ, w, h)
    return _PLAN[k]


def plan_in(t, wp, hp):
    """the drawing at the window's size; once it has settled, one picture"""
    return desk_img(wp, hp)


def heart(x, y): return (x * x + y * y - 1) ** 3 - x * x * y ** 3


def _curve():
    pts = []
    for k in range(721):
        th = -math.pi / 2 + 2 * math.pi * k / 720
        lo, hi = 0., 1.6
        for _ in range(40):
            m = (lo + hi) / 2
            if heart(m * math.cos(th), m * math.sin(th)) < 0: lo = m
            else: hi = m
        pts.append((lo * math.cos(th), lo * math.sin(th)))
    return pts


CURVE = _curve()


def plot_frac(t):
    """how much of the heart is traced: in stuttering steps; it stops short on LO-O-OVE"""
    t = min(t, L3)
    k = clamp((t - (T_PLOT + .25)) / (L3 - T_PLOT - .25))
    k = math.floor(k * 22) / 22 * .58 + (k * 22 % 1) / 22 * .58 * .3
    return min(k, .58)


def plot_img(t, wp, hp):
    s = hp / 1080
    im = Image.new('RGBA', (wp, hp), NIGHT + (255,)); d = ImageDraw.Draw(im)
    cx, cy, sc = wp * .5, hp * .55, hp * .3
    for k in range(-8, 9):
        a = 70 if k % 4 == 0 else 28
        d.line([(cx + k * sc / 4, 0), (cx + k * sc / 4, hp)], fill=CHALK + (a,), width=max(1, int(s)))
        d.line([(0, cy + k * sc / 4), (wp, cy + k * sc / 4)], fill=CHALK + (a,), width=max(1, int(s)))
    d.line([(cx, 0), (cx, hp)], fill=CHALK + (190,), width=max(1, int(2 * s)))
    d.line([(0, cy), (wp, cy)], fill=CHALK + (190,), width=max(1, int(2 * s)))
    for k in (-1, 1):
        d.text((cx + k * sc + 8 * s, cy + 8 * s), str(k), font=font(FW + 'cambria.ttc', 26 * s), fill=CHALK + (200,))
        d.text((cx + 10 * s, cy - k * sc - 34 * s), str(k), font=font(FW + 'cambria.ttc', 26 * s), fill=CHALK + (200,))
    ex = '(x² + y² − 1)³ − x²y³ = 0'
    n = int(clamp((t - T_PLOT) / .2) * len(ex))
    d.text((60 * s, 60 * s), ex[:n], font=font(FW + 'cambriai.ttf', 52 * s), fill=CHALK + (240,))
    f = plot_frac(t)
    if f > 0:
        pts = CURVE[:max(2, int(len(CURVE) * f))]
        pp = [(cx + x * sc, cy - y * sc) for x, y in pts]
        d.line(pp, fill=RED + (255,), width=max(3, int(9 * s)), joint='curve')
        hx, hy = pp[-1]
        d.ellipse([hx - 11 * s, hy - 11 * s, hx + 11 * s, hy + 11 * s], fill=RED + (255,))
    if t >= L3:                                              # frozen: its own spinner stopped mid-turn
        ring(d, wp / 2, hp / 2, 46 * s, L3 * 7., max(3, int(8 * s)), CHALK + (150,))
    return im


def window(img, t, s, rect, content):
    """chrome round a content rect (1080p units), content already pasted"""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = rect
    X = lambda v: v * s
    d.rectangle([X(x0 - 3), X(y0 - 34), X(x1 + 3), X(y1 + 3)], outline=(226, 222, 214), width=max(1, int(2 * s)))
    d.rectangle([X(x0 - 3), X(y0 - 34), X(x1 + 3), X(y0)], fill=(22, 22, 24))
    title = 'render://sandbox/0212   visualize(history, love)' if t < T_PLOT else 'render://sandbox/0213   plot(love)'
    d.text((X(x0 + 10), X(y0 - 29)), title, font=font(MONO, 19 * s), fill=(200, 196, 188))


def app(t, w, h, squeeze=True):
    """the whole screen at t (from 2:54.975): the chat, the window"""
    s = h / 1080; Wt = w / s
    img = Image.new('RGBA', (w, h), (236, 233, 227, 255))
    X = lambda v: v * s
    wx0, wy0, wx1, wy1 = win_rect(Wt)
    u = (t - T_SQ) / .1
    if squeeze and u < 1:
        # shoved: first sideways, then down to size; the drawing is squashed on the way
        ux, uy = outc(u / .55), outc((u - .2) / .8)
        r = (lerp(0, wx0, ux), lerp(0, wy0, uy), lerp(Wt, wx1, ux), lerp(1080, wy1, uy))
        src = desk_img(w, h)
        cw, ch = int(X(r[2] - r[0])), int(X(r[3] - r[1]))
        img.alpha_composite(src.resize((max(1, cw), max(1, ch)), Image.BILINEAR), (int(X(r[0])), int(X(r[1]))))
        window(img, t, s, r, None)
        draw_chat(img, t, s, xoff=lerp(-CHW - 10, 0, backout(u / .9)), yoff=lerp(-TOPH, 0, outc(u)))
        return img
    # shadow, then the content
    sh = Image.new('RGBA', (w, h), (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle([X(wx0 + 6), X(wy0 - 26), X(wx1 + 10), X(wy1 + 12)], fill=(0, 0, 0, 40))
    img.alpha_composite(sh)
    cw, ch = int(X(wx1 - wx0)), int(X(wy1 - wy0))
    content = plot_img(t, cw, ch) if t >= T_PLOT else plan_in(t, cw, ch)
    img.alpha_composite(content, (int(X(wx0)), int(X(wy0))))
    window(img, t, s, (wx0, wy0, wx1, wy1), None)
    draw_chat(img, t, s)
    # not responding: the system greys it over
    v = ease((t - L3 - .25) / .25)
    if v > 0: img.alpha_composite(Image.new('RGBA', (w, h), (255, 255, 255, int(95 * v))))
    return img


def pointer_at(t, Wt):
    """(x, y, busy angle or None, visible)"""
    p0 = G.pointer_path(T_SQ, Wt)
    if t < 180.55: return p0[0], p0[1] + 30 * ease((t - T_SQ - .1) / .3), None
    p1 = (p0[0], p0[1] + 30)
    inp = (330., 1004.)
    if t < 184.62:
        a = ease((t - 180.55) / .28)
        return lerp(p1[0], inp[0], a), lerp(p1[1], inp[1], a), None
    win = (1290., 560.)
    if t < L3:
        a = ease((t - 184.62) / .35)
        return lerp(inp[0], win[0], a), lerp(inp[1], win[1], a), None
    busy = (t - L3) * 9.
    cl = (CLOSE_X(Wt) - 3, 20.)
    a = ease((t - 188.12) / .3)
    return lerp(win[0], cl[0], a), lerp(win[1], cl[1], a), busy if t < TF - .06 else None


def frame(t, w, h, with_pointer=True):
    img = app(t, w, h)
    if with_pointer:
        x, y, busy = pointer_at(t, w * 1080 / h)
        G.pointer(img, x, y, h / 1080, busy=busy)
    return img


def textures(t, w, h):
    return {'u_img': frame(t, w, h)}
