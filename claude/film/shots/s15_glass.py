"""s15 · 2:54.975–3:08.483  the glass.  (v3: the eye is the one who answers)

v8 (the user: the camera moves too often; too little to look at).  Three set-ups only: the slow push into the
history; from "I think I do." one locked shot of the chat and its window; the pull back and the whip into the heart.
The window comes alive: from its first answer it is a night sheet, and for each answer it sketches in chalk
(rain over the hours, miles against km, 晚安 → Good night. as in the rule book, 17 × 24 worked long-hand, a web of
words round "tired"); after thanks it is empty — and the heart is drawn on the same sheet, unasked.

v7 (2026-10-01, the user: no tension, too much reading; the lyric says it still cannot express love).  You are free
and indifferent; it is the one in love, and it has one way to speak: answering.  After "I think I do." you do not
reply; you use it — six small questions, ping-pong, faster and faster (weather, miles, 晚安, 17 × 24, tired, thanks).
Then nothing: the box stays empty, your hand leaves it and drifts toward ×.  Unasked, it answers anyway — in the
only form it has, an equation — and draws it; the heart stops on its singular point; you close it.

v6 (2026-10-01, the user: too fast, too much, off the beat; it has learned some love and is no longer the machines of
history, but it looked like a flashy tour).  Retrieval was the old machines' way; love is remembering one person.
  history: four flicks, four lines, big: earl grey lol / This is the first time we've talked. / You're right, I
           apologize. / i don't think machines understand love.  (then: I think I do. → then prove it)
  Question me: it is asked about you, not about history: your cat (Earl Grey.), when you first talked (March 3. You
           said hi. — it got this wrong before), what you asked on March 4 (your lights; it couldn't).  It brackets
           its answer; no hunting through the picture.
  the heart: it stops on the singular point (0, 1), where both partial derivatives vanish and there is no tangent —
           half a heart, exactly; it hesitates between going on and going back, then spins.

The picture of the desk is shoved into a window of a plain, light chat — but the eye is not in the picture: it stays
where it was while the picture goes, then comes into the chat.  In your app it is the assistant; small, a ring with a
red pupil beside its words.  A camera films the screen: a new framing on every line of the song.

2:54.975 We are trapped ah     the picture stops dead and is grabbed (a jolt to 96 %); the app's bar comes down; on "are"
                              the chat comes in from the left and shoves the picture into its window — sideways, then
                              pressed down; it lands on "trapped".  The eye is not in the picture: it stays where it was
                              the whole time, watching it go; a beat later it drops into the chat, on "hi".
2:57.53 … 2:59.84             you flick down through the history, a flick a beat; on the half beat the eye goes to a
                              line and brackets it: "I can't control devices from here", the bug, "This is the first
                              time we've talked.", "You're right, I apologize.", 爱 → love …
2:59.929 LO-O-OVE              "i don't think machines understand love" <bracketed>; then, pushed in hard: the eye,
                              big, beside "I think I do."
3:00.857 Question me           cut wide: the chat and the window.  A question a beat; at each the eye leaps into the
                              picture and brackets the answer — M. U. C., the letter, 爱, the rule book — and on
                              "the room" the whole window.
3:03.646 LO-O-OVE              define love: the paragraph at once; the eye brackets word after word of it, a
                              sixteenth each: attachment, care, delight, trust, commitment, sacrifice.
3:04.540 I know the algebraic expression of
                              "but what do you think?" — "Let me show you."  The eye leaps into the window, the camera
                              with it; the picture becomes a plot; the eye draws the heart itself, a tick at a time,
                              slower and slower …
3:07.665 LO-O-OVE              … and stops at 58 %, its gap to the part not drawn.  It turns: it is the spinner.  The
                              app goes white, Not Responding; the camera pulls out; your pointer, busy, goes to ×.
3:08.483 Though you are free   (s16) you click it.

The screen is drawn with PIL for each sub-frame, at a fixed scale that only changes in steps (so the type does not
swim), through the camera; the shader places it, and draws the eye (as in s14e_desk: distance fields, its exposure
sampled, a frosted pupil).  On the light page its ring is ink; over the dark picture, chalk."""
import sys, math, importlib.util
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

_D = Path(__file__).resolve().parent
def _load(name, file):
    sp = importlib.util.spec_from_file_location(name, _D / file); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
C = _load('s15c_glass', 's15_chat.py')          # the conversation, its layout, the heart
G = C.G                                         # s14g: the system pointer
AN = _load('anim_glass', 'anim.py')

POST = dict(u_bloom=0., u_ca=0., u_grain=.01)
BT = 60 / 130.                                  # the beat here (130 bpm; the grid of s14e drifts by now)
def B(n): return 162.76 + n * BT
def E8(k): return 162.76 + k * BT / 2
def S16(k): return 162.76 + k * BT / 4
T_SQ, L1, Q, L2, TA, L3 = 174.975, 179.929, 180.857, 183.646, 184.540, 187.665
TF = 162.76 + 57 * 60 / 130.                    # 3:09.07: you click × on "free"
FR = 1 / 60.

FW = 'C:/Windows/Fonts/'
UI, UIB, UII, CJK, MONO = FW + 'segoeui.ttf', FW + 'seguisb.ttf', FW + 'segoeuii.ttf', FW + 'msyh.ttc', FW + 'CascadiaMono.ttf'
APPBG, BG, TOP, TXT, SUB, BUB, LINE = (236, 233, 227), (247, 245, 241), (238, 235, 229), (28, 27, 25), (128, 122, 114), (232, 228, 220), (222, 218, 210)
CHALK, NIGHT, INK = (232, 227, 214), (13, 12, 11), (30, 28, 26)
PEN = (206, 46, 48)                             # the pupil's red: what it draws with
CHW, TOPH, VIEW0, VIEW1, MX0, MX1 = C.CHW, C.TOPH, C.VIEW0, C.VIEW1, C.MX0, C.MX1
VH = VIEW1 - VIEW0
WT = 1920.                                      # the app is laid out 1920 x 1080 (units)
WX0, WY0, WX1, WY1 = C.win_rect(WT)
WCW, WCH = WX1 - WX0, WY1 - WY0
HC = (WX0 + .5 * WCW, WY0 + .55 * WCH)          # the heart's centre and scale in the window
HS = .3 * WCH


def clamp(x, a=0., b=1.): return a if x < a else b if x > b else x
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def outc(x): x = clamp(x); return 1 - (1 - x) ** 3
def inc(x): x = clamp(x); return x * x * x
def lerp(a, b, k): return a + (b - a) * k
def lerp3(a, b, k): return tuple(lerp(p, q, k) for p, q in zip(a, b))
def backout(x, s=1.3): x = clamp(x) - 1; return x * x * ((s + 1) * x + s) + 1
def minjerk(u): u = clamp(u); return u * u * u * (10 - 15 * u + 6 * u * u)
def whip(u):                                    # a whip pan: it goes hard, and stops hard
    u = clamp(u); return .5 - .5 * math.cos(math.pi * (u * u * (3 - 2 * u)))


# ---------------- the conversation: the history (s15_chat), and what you ask now
HISTORY = C.HISTORY[:27]                         # ends on "I think I do.": you do not answer it
LONG = C.LONG
TYPE_T, ANS_DT = .16, .065
S16_ = BT / 4                                   # a sixteenth
# you use it: ping-pong, the gaps closing (on "Question me", "Question me I can answer all"); then thanks, and nothing
PING = [(180.86, 'weather tomorrow?', 'Light rain, 14°C.', 2),
        (181.45, '5 miles in km', '8.05 km.', 2),
        (181.91, 'translate 晚安', 'Good night.', 2),
        (182.37, "what's 17 × 24", '408.', 1),
        (182.72, 'synonym for tired', 'Weary.', 1),
        (183.07, 'thanks', "You're welcome.", 1)]
EQ = '(x² + y² − 1)³ − x²y³ = 0'
LIVE = [(tq, q, a, .04, n * S16_) for tq, q, a, n in PING] + [(TA, None, EQ, .12, 0.)]   # unasked: it answers anyway
T_LAST = PING[-1][0] + PING[-1][3] * S16_       # "You're welcome."
Q1, Q2, Q3 = PING[0][0], PING[2][0], PING[4][0]
DEF_WORDS = ['attachment', 'care', 'delight', 'trust', 'commitment', 'sacrifice']

_IH = {}
def ih(it, shown=None):
    k = (it, shown)
    if k not in _IH: _IH[k] = C.item_h(it, 1., shown)
    return _IH[k]


def items_at(t):
    out = [(it, None) for it in HISTORY]
    box = ''
    for (tq, q, a, dur, adt) in LIVE:
        if t < tq - (TYPE_T if q else 0.): break
        if q and t < tq:
            box = q[:int(len(q) * clamp((t - tq + TYPE_T) / (TYPE_T - .03)))]
            break
        if q: out.append((('you', q), None))
        ta = tq + adt
        if t >= ta:
            n = max(1, int(len(a) * clamp((t - ta) / dur)))
            out.append((('ai', a), a[:n] if n < len(a) else None))
    return out, box


def content_h(t):
    its, _ = items_at(t)
    return 24 + sum(ih(it, sh) for it, sh in its) + 24


def layout(t, o):
    """[(item, shown, top y (units), height)], the text in the box"""
    its, box = items_at(t)
    y = VIEW0 + 24 - o
    L = []
    for it, sh in its:
        hh = ih(it, sh); L.append((it, sh, y, hh)); y += hh
    return L, box


def top0(i):
    """item i of the history: its top with the chat scrolled to 0"""
    return VIEW0 + 24 + sum(ih(it) for it in HISTORY[:i])


O_MAX = content_h(T_SQ) - VH                    # the history, scrolled to its end


# ---------------- scrolling.  The history: a flick a beat, each lands a line the eye will read.
READ = [5, 18, 20, 23]                           # what it reads (after a long look at "hi"): four lines, no more
FLICK_T = [B(32), B(34), B(35), B(37)]
FLICK_O = []
_o = 0.
for i in READ:
    c = top0(i) + ih(HISTORY[i]) / 2
    _o = min(O_MAX, max(_o + 30, c - 430)); FLICK_O.append(_o)
TAU = .075


def _hist_scroll(t):
    pos, prev = 0., 0.
    for tk, ok in zip(FLICK_T, FLICK_O):
        if t < tk: break
        if ok - prev < 1:                                             # at the end already: the flick only bounces
            u = t - tk
            pos = ok + 16 * (u / .06) * math.exp(1 - u / .06)
        else:
            pos = ok + (pos - ok) * math.exp(-(t - tk) / TAU)
        prev = ok
    return pos


_SC = {}
def _live_table():
    """from Q the chat keeps to its bottom, a little late (sampled, then followed)"""
    if 'tab' not in _SC:
        dt = 1 / 240.
        n = int((TF + .2 - Q) / dt) + 2
        tab = []; pos = _hist_scroll(Q)
        for i in range(n):
            t = Q + i * dt
            tgt = max(0., content_h(t) - VH)
            pos = tgt + (pos - tgt) * math.exp(-dt / .06)
            tab.append(pos)
        _SC['tab'] = (dt, tab)
    return _SC['tab']


def scroll_at(t):
    if t < Q: return _hist_scroll(t)
    dt, tab = _live_table()
    x = (t - Q) / dt
    i = int(clamp(x, 0, len(tab) - 2)); f = clamp(x - i)
    return lerp(tab[i], tab[i + 1], f)


# ---------------- where things are (units)
def item_box(it, sh, y):
    """what the brackets go round: the text of an answer, your bubble, a card"""
    d = C._MEAS
    kind = it[0]
    if kind == 'ai':
        L = C.wrap(d, it[1] if sh is None else sh, UI, 19, 540)
        tw = max(C.tlen(d, l, UI, 19) for l in L)
        return (MX0 + 36, y + 3, MX0 + 40 + tw, y + 3 + len(L) * 28 - 3)
    if kind == 'you':
        L = C.wrap(d, it[1], UI, 19, 440)
        tw = max(C.tlen(d, l, UI, 19) for l in L)
        return (MX1 - tw - 32, y + 4, MX1, y + 4 + len(L) * 27 + 18)
    if kind == 'card': return (MX0 + 38, y + 4, MX1 - 40, y + 104)
    if kind == 'code': return (MX0 + 38, y + 2, MX1, y + 2 + 22 * len(it[1].split('\n')) + 26)
    return (MX0, y, MX1, y + ih(it))


def eye_spot(it, box):
    """where the eye sits to read an item: at an answer, where its avatar is; at yours, just left of the bubble"""
    if it[0] == 'you': return (box[0] - 34, (box[1] + box[3]) / 2)
    return (MX0 + 12, box[1] + 9)


def hist_item(i):
    """history item i as it lies once its flick has landed"""
    it = HISTORY[i]
    k = READ.index(i) if i in READ else 0
    y = top0(i) - (FLICK_O[k] if i in READ else 0.)
    return it, y


def live_item(tq, kind, t=None):
    """the question sent at tq, or its answer: (item, top y) — at time t, or once it has settled"""
    for (t0, q, a, dur, adt) in LIVE:
        if abs(t0 - tq) < 1e-6:
            it = ('you', q) if kind == 'q' else ('ai', a)
            tt = t0 + adt + dur + .25 if t is None else t
            tt = max(tt, t0 + adt + dur + 1e-3)
            o = scroll_at(tt)
            L, _ = layout(tt, o)
            for it2, sh, y, hh in L:
                if it2 == it:
                    return it, y + (0. if t is None else scroll_at(tt) - scroll_at(t))
    raise KeyError(tq)


def word_box(it, y, word):
    """a word inside an answer: its box"""
    d = C._MEAS
    L = C.wrap(d, it[1], UI, 19, 540)
    for j, l in enumerate(L):
        k = l.find(word)
        if k >= 0:
            x0 = MX0 + 38 + C.tlen(d, l[:k], UI, 19)
            return (x0 - 2, y + 2 + j * 28 + 3, x0 + C.tlen(d, word, UI, 19) + 2, y + 2 + j * 28 + 25)
    return None


# the desk picture in the window: where its things are (the capture is 1920 x 1080)
def desk_pt(x, y): return (WX0 + x * WCW / 1920., WY0 + y * WCH / 1080.)
def desk_box(x0, y0, x1, y1): return desk_pt(x0, y0) + desk_pt(x1, y1)
PICT = dict(muc=desk_box(512, 528, 632, 558), letter=desk_box(0, 402, 212, 706), ai=desk_box(176, 368, 444, 750),
            book=desk_box(372, 560, 962, 762), room=(WX0 + 6, WY0 + 6, WX1 - 6, WY1 - 6),
            fold=desk_box(862, 468, 975, 540), panel=desk_box(160, 104, 420, 140), cab=desk_box(1268, 74, 1626, 390))
# it is asked, and hunts for its proof: a glance, another (not there), then it finds it — only then the answer comes
_C = [(WX0 + 70, WY0 + 60), (WX1 - 70, WY0 + 60), (WX1 - 70, WY1 - 60), (WX0 + 70, WY1 - 60)]
SEARCH = [(B(40), ['ai', 'fold'], 'muc', 1), (B(41), ['panel', 'book'], 'letter', 1), (B(42), [], 'ai', 1),
          (B(43), ['cab'], 'book', 1), (B(44), _C, 'room', .5)]


def pict_spot(key, R):
    b = PICT[key]
    if key == 'room': return (WX0 + WCW * .5, WY0 + WCH * .5, R * 1.6)
    if key == 'book': return ((b[0] + b[2]) / 2, b[1] - 26, R)
    if key == 'letter': return (b[2] + 30, (b[1] + b[3]) / 2 - 40, R)
    if key == 'cab': return ((b[0] + b[2]) / 2, b[3] + 20, R)
    if key == 'panel': return (b[2] + 28, (b[1] + b[3]) / 2, R)
    return (b[2] + 26, (b[1] + b[3]) / 2 - 18, R)


def search_steps():
    """[(time, target key or corner point, is it the find)]"""
    out = []
    for tq, wrong, key, step in SEARCH:
        for i, w in enumerate(wrong): out.append((tq + .02 + i * step * S16_, w, False))
        out.append((tq + .02 + len(wrong) * step * S16_, key, True))
    return out


# ---------------- the heart it draws
CURVE = C.CURVE                                  # 721 points from the bottom tip, anticlockwise
def heart_pt(f):
    x = f * (len(CURVE) - 1); i = int(clamp(x, 0, len(CURVE) - 2)); u = x - i
    px, py = lerp(CURVE[i][0], CURVE[i + 1][0], u), lerp(CURVE[i][1], CURVE[i + 1][1], u)
    return (HC[0] + px * HS, HC[1] - py * HS)


def heart_dir(f):
    a, b = heart_pt(max(0., f - .004)), heart_pt(min(1., f + .004))
    return math.atan2(b[1] - a[1], b[0] - a[0])


T_PLOT = B(48)                                   # the eye goes into the window; it becomes a plot
T_EQ = T_PLOT + .1
TICK0 = 195                                      # the first tick of the pen (a sixteenth)


F_STOP = .5                                      # the dent: (0, 1), where the gradient vanishes (no tangent)


def _ticks():
    """(time, fraction): eighth notes at first (careful), then slower; it reaches the dent and cannot go on"""
    ks = [195, 197, 199, 201, 203, 205, 206, 208, 209]
    n = len(ks)
    inc = [1.0 * (.86 ** i) for i in range(n)]
    s = sum(inc); f = 0.; out = []
    for k, d in zip(ks, inc):
        f += F_STOP * d / s; out.append((S16(k), min(f, F_STOP)))
    out[-1] = (out[-1][0], F_STOP)
    return out


TICKS = _ticks()
T_DENT = TICKS[-1][0]                            # it is on the dent: which way?


def plot_frac(t):
    f = 0.
    for tk, fk in TICKS:
        if t >= tk: f = fk
    return f


# ---------------- the squeeze (2:54.975 We are trapped ah): the picture stops dead and is grabbed (a jolt to 96 %);
# the app's bar comes down; on "are" the chat comes in from the left and shoves the picture — sideways first, then
# pressed down — into its window; it lands on "trapped", with a little give.  The eye is not in the picture: it stays.
T_SH0, T_SH1 = B(27), 175.92
T_SQEND = T_SH1 + .15


def _grab_scale(t):
    tau = t - T_SQ
    if tau < .033: return 1 - .045 * (max(0., tau) / .033) ** 1.5
    if tau < .1: return .955 + .005 * ease((tau - .033) / .067)
    return .96


def _shove(u):
    """it accelerates the whole way, and brakes hard at the end"""
    u = clamp(u); a, b = .8, .84
    if u < a: return b * (u / a) ** 1.75
    return b + (1 - b) * outc((u - a) / (1 - a))


def squeeze_state(t):
    """(the picture's rect, the chat's x offset, the bar's y offset)"""
    yoff = lerp(-TOPH, 0., outc((t - T_SQ - .015) / .18))
    sc = _grab_scale(t)
    g = (960 - 960 * sc, 540 - 540 * sc, 960 + 960 * sc, 540 + 540 * sc)
    if t < T_SH0: return g, -CHW - 10., yoff
    u = (t - T_SH0) / (T_SH1 - T_SH0)
    cx, cy = _shove(u), _shove((u - .2) / .8)
    xoff = lerp(-CHW - 10., 0., cx)
    r = [max(g[0], xoff + CHW + 40), lerp(g[1], WY0, cy), lerp(g[2], WX1, cx), lerp(g[3], WY1, cy)]
    tau = t - T_SH1
    if 0 <= tau < .14:                                               # it lands with a little give
        k = .012 * math.sin(math.pi * tau / .14) * (1 - tau / .14)
        mx, my = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
        r = [mx + (r[0] - mx) * (1 - k), my + (r[1] - my) * (1 - k), mx + (r[2] - mx) * (1 - k), my + (r[3] - my) * (1 - k)]
    return tuple(r), xoff, yoff


# ---------------- the eye: (x, y, R) in units of the app, keyframed (anim.py); what it brackets; where it looks
E0 = (918.15, 525.38, 34.)                      # where s14e_desk leaves it (the camera there is 1:1 with the app)
LOOK0 = -2.66
R_CHAT, R_PICT, R_PEN = 12., 20., 20.


def _eye_track():
    sac = lambda t0, to, n=3: AN.move(t0, to, 'sac', n)
    tick = lambda t0, to: AN.move(t0, to, 'tick', 1)
    tr = [AN.move(0., E0, 'set')]
    # into the chat, onto "hi"
    it, y = HISTORY[1], top0(1)
    bx = item_box(it, None, y); sx, sy = eye_spot(it, bx)
    tr.append(sac(B(29), (sx, sy, R_CHAT), 5))
    # the history: on each half beat, the line just flicked in
    for tk, i in zip(FLICK_T, READ):
        it, y = hist_item(i)
        sx, sy = eye_spot(it, item_box(it, None, y))
        tr.append(sac(tk + (.1 if i == READ[-1] else BT / 2), (sx, sy, R_CHAT), 2))
    # I think I do.
    it = HISTORY[26]; y = top0(26) - O_MAX
    tr.append(sac(B(38), (MX0 + 12, y + 12, R_CHAT), 2))
    # the answers: it is at each before it is finished being asked
    for (tq, q, a, dur, adt) in LIVE[:-1]:
        it, y = live_item(tq, 'a')
        tr.append(sac(tq + adt - 3 * FR, (MX0 + 12, y + 12, R_CHAT), 2))
    # unasked: its equation
    it, y = live_item(TA, 'a')
    tr.append(sac(TA - 2 * FR, (MX0 + 12, y + 12, R_CHAT), 3))
    # into the window: the pen
    tr.append(sac(T_PLOT, pen_eye(0.) + (R_PEN,), 5))
    for tk, fk in TICKS:
        tr.append(tick(tk, pen_eye(fk) + (R_PEN,)))
    return tr


def pen_eye(f):
    """the eye's centre such that its pupil (a little ahead of the centre, along its look) is on the line's end"""
    x, y = heart_pt(f); a = heart_dir(f)
    return (x - math.cos(a) * R_PEN * .22, y - math.sin(a) * R_PEN * .22)


EYE_T = _eye_track()


def brackets_at(t):
    """what it is comparing now (a box in units), and since when"""
    # the history
    if B(29) + .12 <= t < FLICK_T[0]:
        it = HISTORY[1]; return item_box(it, None, top0(1)), t - (B(29) + .12)
    for k, (tk, i) in enumerate(zip(FLICK_T, READ)):
        t_on = tk + (.1 if i == READ[-1] else BT / 2) + .07
        t_off = FLICK_T[k + 1] if k + 1 < len(FLICK_T) else B(38) - .02
        if t_on <= t < t_off:
            it, _ = hist_item(i)
            y = top0(i) - scroll_at(t)
            return item_box(it, None, y), t - t_on
    # its answers
    for j, (tq, q, a, dur, adt) in enumerate(LIVE[:-1]):
        t_on = tq + adt + 4 * FR
        t_off = LIVE[j + 1][0] - (TYPE_T if j + 1 < len(LIVE) - 1 else 0.) - .02
        if j == len(LIVE) - 2: t_off = T_LAST + .45                    # "You're welcome.", then it lets go
        if t_on <= t < t_off:
            it, y = live_item(tq, 'a', t)
            return item_box(it, None, y), t - t_on
    if TA + 4 * FR <= t < T_PLOT - .02:                                # the equation it was not asked for
        it, y = live_item(TA, 'a', t)
        return item_box(it, None, y), t - TA - 4 * FR
    return None, 9.


def _snap(age):
    """the brackets arrive: from wide, fast, a frame's smear, then held steps (as in s14e_desk)"""
    A, S_ = 2 * FR, 1 * FR
    if age < A: return 2.2 - .2 * (age / A) ** 2, False
    if age < A + S_: return lerp(2.0, 1.15, (age - A) / S_), False
    return (1.06, 1.)[min(1, int((age - A - S_) / (AN.HOLD * FR)))], True


def spin_at(t):
    """the stall: from a little after LO-O-OVE it turns in place (radians turned)"""
    u = t - (L3 + .14)
    if u <= 0: return 0.
    rate = 2 * math.pi * 1.25
    return rate * (u * u / .6 if u < .3 else .15 + (u - .3))


def look_at(t, pos):
    """where its gap points: at what it brackets; at the next place just before it goes; along the way while it
    goes; at rest, at its words (to the right); as the pen, along the line"""
    if t < B(29) - .07:                                              # it watches its picture being shoved away
        if t < T_SH0: return LOOK0
        r = squeeze_state(min(t, T_SH1))[0]
        a_pic = math.atan2((r[1] + r[3]) / 2 - E0[1], (r[0] + r[2]) / 2 - E0[0])
        return lerp_ang(LOOK0, a_pic, ease((t - T_SH0) / .2))
    if t >= T_PLOT + .12:
        f = plot_frac(t)
        if T_DENT + 3 * FR <= t < L3 + .14:                           # on the dent: on, or back?  a sixteenth each
            j = int((t - T_DENT - 3 * FR) / S16_)
            return heart_dir(F_STOP + .01) if j % 2 == 0 else heart_dir(F_STOP - .01) + math.pi
        return heart_dir(f if f > 0 else .001) + spin_at(t)
    b, _ = brackets_at(t)
    if b is not None:
        cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        if abs(cx - pos[0]) + abs(cy - pos[1]) > 4: return math.atan2(cy - pos[1], cx - pos[0])
    nm = AN.next_move(EYE_T, t, .07)
    if nm:
        dx, dy = nm['to'][0] - pos[0], nm['to'][1] - pos[1]
        if math.hypot(dx, dy) > 2: return math.atan2(dy, dx)
    m, a = AN._active(EYE_T, t)
    if m['kind'] == 'sac' and t - m['t0'] < (3 + m['smear'] + 2) * FR:
        dx, dy = m['to'][0] - a[0], m['to'][1] - a[1]
        if math.hypot(dx, dy) > 2: return math.atan2(dy, dx)
    if T_LAST + .5 <= t < TA:                                        # nothing more: the empty box; then your hand, going
        if t < 184.15: return math.atan2(1004. - pos[1], 300. - pos[0])
        px, py, _ = pointer_at(t)
        return math.atan2(py - pos[1], px - pos[0])
    return 0.


def lerp_ang(a, b, k):
    d = (b - a + math.pi) % (2 * math.pi) - math.pi
    return a + d * k


# ---------------- the camera: (cx, cy, zoom) in units of the app
V_FULL = (960., 540., 1.)
V_HIST = (430., 430., 2.0)
V_QA = (711., 640., 1.35)
V_Q = (420., 712., 1.9)
V_WIN = ((WX0 + WX1) / 2, (WY0 + WY1) / 2, 1080. / WCH)
Y_THINK = top0(26) - O_MAX + 22


V_FIX = (962., 556., 1.04)                      # the chat and its window, locked
T_FIX1 = B(38) + .55
V_PULL = (920., 548., 1.02)                     # the empty box, the chat, the window, ×
V_THINK = (122., Y_THINK - 6, 4.4)


def _eye_y_smooth(t):
    return AN.smooth(EYE_T, t, lag=.1, dur=.35)[1]


def cam_base(t):
    if t < 176.30: return V_FULL
    if t < 177.0:
        return lerp3(V_FULL, V_HIST, ease((t - 176.30) / .7))
    if t < B(38):                                                      # the history: one slow push, following the eye down
        cx, cy, z = V_HIST
        ey = _eye_y_smooth(t)
        cy += max(0., ey - 470.) * .85
        z *= 1 + .06 * ease((t - 177.0) / 3.)
        return (cx, cy, z)
    if t < T_FIX1:                                                     # one move out to the locked shot
        a = cam_base(B(38) - 1e-4)
        e = ease((t - B(38)) / (T_FIX1 - B(38)))
        return (lerp(a[0], V_FIX[0], e), lerp(a[1], V_FIX[1], e), math.exp(lerp(math.log(a[2]), math.log(V_FIX[2]), e)))
    if t < T_LAST + .3:                                                # locked: the ping-pong plays in the picture
        return V_FIX
    if t < T_PLOT - .07:                                               # nothing more: back, slowly
        e = ease((t - (T_LAST + .3)) / 1.1)
        z = math.exp(lerp(math.log(V_FIX[2]), math.log(V_PULL[2]), e))
        return (lerp(V_FIX[0], V_PULL[0], e), lerp(V_FIX[1], V_PULL[1], e), z)
    if t < L3 + .45:
        a = (V_PULL[0], V_PULL[1], V_PULL[2] * 1.02)
        e = whip((t - (T_PLOT - .07)) / .42)
        z = math.exp(lerp(math.log(a[2]), math.log(V_WIN[2]), e))
        c = (lerp(a[0], V_WIN[0], e), lerp(a[1], V_WIN[1], e))
        k = ease((t - (T_PLOT + .35)) / (L3 - T_PLOT - .35))          # then a slow push on the heart
        zz = z * (1 + .045 * k)
        return (lerp(c[0], HC[0], k * .3), lerp(c[1], HC[1] - 20, k * .3), zz)
    a = cam_base(L3 + .45 - 1e-4)
    e = ease((t - (L3 + .45)) / .6)
    return (lerp(a[0], V_FULL[0], e), lerp(a[1], V_FULL[1], e), math.exp(lerp(math.log(a[2]), 0., e)))


def punch(t):
    """(v8: none)"""
    return 0.
    k = 0.
    for tq, q, a, n in PING:
        u = t - tq - n * S16_
        if 0 <= u < .3: k += .02 * math.exp(-u / .07)
    return k


def cam(t):
    cx, cy, z = cam_base(t)
    z *= 1 + punch(t)
    u = t - T_SQ
    d = 2.2 / z ** .5
    cx += d * math.sin(u * .63 + .4) + .6 * d * math.sin(u * 1.7)
    cy += d * .7 * math.sin(u * .47 + 1.3)
    # keep inside the screen
    hw, hh = WT / 2 / z, 540. / z
    cx = clamp(cx, hw - 160, WT - hw) if hw < WT / 2 else WT / 2
    cy = clamp(cy, hh, 1080. - hh) if hh < 540 else 540.
    return cx, cy, z


# ---------------- your pointer (units of the app) — a person's hand
PTR0 = (1440., 250.)                            # where it clicked the M.U.C. sheet in s14e_desk
PTR_REST = (470., 660.)
PTR_IN0, PTR_ENTER = (760., 1140.), 175.80
PTR_BOX = (400., 1004.)
CLOSE = (WT - 30, 21.)
PTR_DRIFT = (WT - 300., 190.)                   # where the hand has drifted to by the stall


def pointer_at(t):
    """(x, y, busy angle or None)"""
    if t < 175.98: return PTR0[0] + .8 * math.sin((t - T_SQ) * 2.3), PTR0[1] + .6 * math.sin((t - T_SQ) * 1.7), None
    if t < 176.58:
        k = minjerk((t - 175.98) / .6); bow = math.sin(k * math.pi) * 30
        return lerp(PTR0[0], PTR_REST[0], k) - bow * .4, lerp(PTR0[1], PTR_REST[1], k) + bow * .2, None
    if t < Q + .05:
        u = t - 176.58
        x, y = PTR_REST[0] + 2.5 * math.sin(u * 2.1) + 1.2 * math.sin(u * 6.3), PTR_REST[1] + 1.8 * math.sin(u * 1.6 + 1)
        for tk in FLICK_T:                                            # the wheel flicked: the hand shifts a hair
            v = t - tk
            if 0 <= v < .2: y += 2.2 * math.sin(v / .2 * math.pi)
        return x, y, None
    if t < T_LAST + .35:
        k = minjerk((t - Q - .05) / .3)
        return lerp(PTR_REST[0], PTR_BOX[0], k), lerp(PTR_REST[1], PTR_BOX[1], k), None
    busy = (t - L3) * 8. if t >= L3 + .2 else None
    if t < 188.483:                                                   # done with it: the hand drifts off, toward ×
        k = minjerk((t - T_LAST - .35) / 4.2); bow = math.sin(k * math.pi) * 50
        return lerp(PTR_BOX[0], PTR_DRIFT[0], k) + bow * .4, lerp(PTR_BOX[1], PTR_DRIFT[1], k) - bow * .2, busy
    t0, t1 = 188.483, TF - .27
    k = minjerk((t - t0) / (t1 - t0)); bow = math.sin(k * math.pi) * 20
    x = lerp(PTR_DRIFT[0], CLOSE[0] + 16, k) + bow * .3
    y = lerp(PTR_DRIFT[1], CLOSE[1] + 10, k) + bow
    c = minjerk((t - t1 + .01) / .07)
    return x - 16 * c, y - 10 * c, busy


# ---------------- drawing the screen through the camera
_F = {}
def font(path, size):
    k = (path, round(size * 4) / 4)
    if k not in _F: _F[k] = ImageFont.truetype(path, max(1., k[1]))
    return _F[k]


class Pen:
    """UI units -> image pixels: px = u * k - org"""
    def __init__(self, img, k, ox, oy):
        self.img, self.d, self.k, self.ox, self.oy = img, ImageDraw.Draw(img, 'RGBA'), k, ox, oy
        self.w, self.h = img.size
    def X(self, x): return x * self.k - self.ox
    def Y(self, y): return y * self.k - self.oy
    def P(self, x, y): return (self.X(x), self.Y(y))
    def R(self, x0, y0, x1, y1): return [self.X(x0), self.Y(y0), self.X(x1), self.Y(y1)]
    def S(self, v): return v * self.k
    def W(self, v): return max(1, int(round(v * self.k)))
    def seen(self, x0, y0, x1, y1, m=4):
        return self.X(x1) > -m and self.X(x0) < self.w + m and self.Y(y1) > -m and self.Y(y0) < self.h + m
    def text(self, x, y, s, path, size, fill):
        for r, cj in C.runs(s):
            f = font(CJK if cj else path, size * self.k)
            self.d.text((self.X(x), self.Y(y + (-.06 * size if cj else 0))), r, font=f, fill=fill)
            x += self.d.textlength(r, font=f) / self.k
    def tlen(self, s, path, size):
        return sum(self.d.textlength(r, font=font(CJK if cj else path, size * self.k)) for r, cj in C.runs(s)) / self.k


def ring_icon(p, cx, cy, r, ang, width, fill, pupil=None):
    a0 = math.degrees(ang) + 28
    p.d.arc(p.R(cx - r, cy - r, cx + r, cy + r), a0, a0 + 304, fill=fill, width=p.W(width))
    if pupil:
        pr = r * .38; px, py = cx + math.cos(ang) * r * .22, cy + math.sin(ang) * r * .22
        p.d.ellipse(p.R(px - pr, py - pr, px + pr, py + pr), fill=pupil)


_THUMB = {}


def draw_item(p, it, shown, y, t):
    kind = it[0]
    if kind == 'date':
        tw = p.tlen(it[1], UIB, 15); cx = (MX0 + MX1) / 2
        p.d.line([p.P(MX0 + 40, y + 29), p.P(cx - tw / 2 - 14, y + 29)], fill=LINE, width=p.W(1))
        p.d.line([p.P(cx + tw / 2 + 14, y + 29), p.P(MX1 - 40, y + 29)], fill=LINE, width=p.W(1))
        p.text(cx - tw / 2, y + 18, it[1], UIB, 15, SUB)
    elif kind == 'sys':
        tw = p.tlen(it[1], UII, 14)
        p.text((MX0 + MX1) / 2 - tw / 2, y + 3, it[1], UII, 14, (150, 145, 138))
    elif kind == 'you':
        L = C.wrap(C._MEAS, it[1], UI, 19, 440)
        tw = max(C.tlen(C._MEAS, l, UI, 19) for l in L)
        bx0 = MX1 - tw - 32
        p.d.rounded_rectangle(p.R(bx0, y + 4, MX1, y + 4 + len(L) * 27 + 18), radius=p.S(18), fill=BUB)
        for i, l in enumerate(L): p.text(bx0 + 16, y + 11 + i * 27, l, UI, 19, TXT)
    elif kind == 'ai':
        txt = it[1] if shown is None else shown
        ep = AN.value(EYE_T, AN.frame_of(t))[0]
        if math.hypot(ep[0] - (MX0 + 12), ep[1] - (y + 12)) > 15:
            ring_icon(p, MX0 + 12, y + 12, 8.5, 0., 2.2, (190, 184, 175))
        for i, l in enumerate(C.wrap(C._MEAS, txt, UI, 19, 540)): p.text(MX0 + 38, y + 2 + i * 28, l, UI, 19, TXT)
    elif kind == 'code':
        L = it[1].split('\n')
        p.d.rounded_rectangle(p.R(MX0 + 38, y + 2, MX1, y + 2 + 22 * len(L) + 26), radius=p.S(10), fill=(36, 34, 32))
        for i, l in enumerate(L): p.text(MX0 + 56, y + 14 + i * 22, l, MONO, 15, (226, 222, 212))
    elif kind == 'card':
        x0, x1 = MX0 + 38, MX1 - 40
        live = it[1].startswith('visualize')
        p.d.rounded_rectangle(p.R(x0, y + 4, x1, y + 104), radius=p.S(14), fill=(252, 251, 248),
                              outline=(60, 58, 54) if live else LINE, width=p.W(2 if live else 1))
        tw_, th_ = max(2, int(p.S(142))), max(2, int(p.S(80)))
        key = (it[1], tw_)
        if key not in _THUMB:
            src = desk_img() if live else C._pendulum_thumb(284, 160)
            _THUMB[key] = src.resize((tw_, th_), Image.LANCZOS)
        th = _THUMB[key]; p.img.paste(th, (int(round(p.X(x0 + 10))), int(round(p.Y(y + 14)))), th)
        L = C.wrap(C._MEAS, it[1], UIB, 17, x1 - x0 - 180)
        for i, l in enumerate(L[:2]): p.text(x0 + 166, y + 18 + i * 24, l, UIB, 17, TXT)
        p.text(x0 + 166, y + 20 + len(L[:2]) * 24 + 6, it[2] + ('  ↗' if live else ''), UI, 14, SUB)


_DESK = {}
def desk_img():
    """s14e_desk's last frame without the eye (film/capture_desk.py)"""
    if 'img' not in _DESK:
        f = _D.parent / 'cache' / 'desk_noeye_1080p.png'
        if not f.exists(): f = _D.parent / 'cache' / 'desk_1080p.png'
        _DESK['img'] = Image.open(f).convert('RGBA')
    return _DESK['img']


def paste_region(p, src, x0, y0, x1, y1):
    """src stretched over the units rect, only the part that is seen"""
    X0, Y0, X1, Y1 = p.R(x0, y0, x1, y1)
    if X1 - X0 < 1 or Y1 - Y0 < 1: return
    ix0, iy0 = int(math.floor(max(0, X0))), int(math.floor(max(0, Y0)))
    ix1, iy1 = int(math.ceil(min(p.w, X1))), int(math.ceil(min(p.h, Y1)))
    if ix1 <= ix0 or iy1 <= iy0: return
    sw, sh = src.size
    fx, fy = sw / (X1 - X0), sh / (Y1 - Y0)
    part = src.transform((ix1 - ix0, iy1 - iy0), Image.EXTENT,
                         ((ix0 - X0) * fx, (iy0 - Y0) * fy, (ix1 - X0) * fx, (iy1 - Y0) * fy), Image.BILINEAR)
    p.img.paste(part, (ix0, iy0), part)


def draw_sheet(p):
    """the night sheet: black, a faint grid"""
    p.d.rectangle(p.R(WX0, WY0, WX1, WY1), fill=NIGHT)
    k = HS / 4
    for j in range(-12, 13):
        a = 46 if j % 4 == 0 else 18
        x = HC[0] + j * k
        if WX0 < x < WX1: p.d.line([p.P(x, WY0), p.P(x, WY1)], fill=CHALK + (a,), width=p.W(1))
        y = HC[1] + j * k
        if WY0 < y < WY1: p.d.line([p.P(WX0, y), p.P(WX1, y)], fill=CHALK + (a,), width=p.W(1))


T_SKETCH0 = PING[0][0] + PING[0][3] * S16_      # its first answer: the window becomes its sheet
CH_ = CHALK + (235,)


def _pl(p, pts, k, w=2.4, col=CH_):
    """a polyline drawn up to fraction k of its length"""
    if k <= 0 or len(pts) < 2: return
    L = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:])]
    tot = sum(L) * k; out = [pts[0]]
    for (a, b), l in zip(zip(pts, pts[1:]), L):
        if tot <= 0: break
        f = min(1., tot / l) if l else 1.
        out.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)); tot -= l
    p.d.line([p.P(*q) for q in out], fill=col, width=p.W(w), joint='curve')


def _tx(p, x, y, s_, size, k, font_=None, col=CHALK):
    if k <= 0: return
    p.text(x, y, s_, font_ or (FW + 'cambriai.ttf'), size, col + (int(235 * min(1., k)),))


def sketch(p, i, k):
    """answer i, drawn in chalk; k: 0 .. 1 drawn"""
    cx, cy, S = HC[0], HC[1] - 20, HS
    if i == 0:                                                       # tomorrow: the temperature over the hours; rain
        xs = [cx - 1.9 * S + j * 3.8 * S / 24 for j in range(25)]
        pts = [(x, cy - .25 * S - .35 * S * math.sin((j - 6) / 24 * 2 * math.pi)) for j, x in enumerate(xs)]
        _pl(p, [(cx - 1.95 * S, cy + .9 * S), (cx + 1.95 * S, cy + .9 * S)], min(1., k * 3), 1.6)
        _pl(p, pts, k * 1.3)
        for j in range(14):
            x = cx - 1.7 * S + j * .26 * S; y = cy + .25 * S + (j * 37 % 5) * .08 * S
            if k > .3 + j * .03: _pl(p, [(x, y), (x - .06 * S, y + .22 * S)], 1., 1.8, CHALK + (150,))
        _tx(p, cx + 1.25 * S, cy - .95 * S, '14°C', 30, k * 2 - 1)
    elif i == 1:                                                     # 5 miles = 8.05 km: two scales
        x0, x1 = cx - 1.8 * S, cx + 1.8 * S
        for row, (n, lab) in enumerate(((10, 'mi'), (16, 'km'))):
            y = cy - .3 * S + row * .7 * S
            _pl(p, [(x0, y), (x1, y)], min(1., k * 2.5), 2.)
            for j in range(n + 1):
                x = x0 + (x1 - x0) * j / n * (1. if row else 16 / 10 / 1.6)
                x = x0 + (x1 - x0) * (j / 16 if row else j * 1.609 / 16)
                if x <= x1 + 1 and k > .2 + j * .02: _pl(p, [(x, y - .07 * S), (x, y + .07 * S)], 1., 1.6)
            _tx(p, x1 + .08 * S, y - .12 * S, lab, 24, k * 2 - .4)
        xm = x0 + (x1 - x0) * 5 * 1.609 / 16
        _pl(p, [(xm, cy - .3 * S), (xm, cy + .4 * S)], (k - .5) * 3, 2.6, PEN + (255,))
        _tx(p, xm - .1 * S, cy - .75 * S, '5', 30, k * 2 - 1); _tx(p, xm - .25 * S, cy + .55 * S, '8.05', 30, k * 2 - 1.1)
    elif i == 2:                                                     # 晚安 → Good night. — a row of the rule book
        w, h = 2.8 * S, .7 * S
        _pl(p, [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2), (cx - w / 2, cy - h / 2)], k * 1.6, 2.)
        _tx(p, cx - w / 2 + .2 * S, cy - .2 * S, '晚安', 40, k * 2 - .6, CJK)
        _tx(p, cx - .35 * S, cy - .18 * S, '→', 36, k * 2 - .8, FW + 'cambria.ttc')
        _tx(p, cx + .05 * S, cy - .18 * S, 'Good night.', 34, k * 2 - 1.)
    elif i == 3:                                                     # 17 × 24, long-hand
        rows = [('  17', 0), ('× 24', 0), ('—', 1), ('  68', 0), (' 34 ', 0), ('—', 1), (' 408', 0)]
        for j, (r_, rule) in enumerate(rows):
            y = cy - 1.05 * S + j * .32 * S
            if rule: _pl(p, [(cx - .45 * S, y + .2 * S), (cx + .45 * S, y + .2 * S)], (k * 7 - j) * 1., 2.)
            else: _tx(p, cx - .42 * S, y, r_, 40, k * 7 - j, MONO, PEN[:3] if j == 6 else CHALK)
    elif i == 4:                                                     # tired: a web of words
        words = ['weary', 'exhausted', 'drained', 'spent', 'worn out', 'sleepy']
        _tx(p, cx - .3 * S, cy - .14 * S, 'tired', 34, k * 4)
        for j, wd in enumerate(words):
            a = -math.pi / 2 + j * 2 * math.pi / len(words)
            ex, ey = cx + math.cos(a) * 1.3 * S, cy + math.sin(a) * .95 * S
            _pl(p, [(cx + math.cos(a) * .45 * S, cy + math.sin(a) * .3 * S), (ex - math.cos(a) * .2 * S, ey - math.sin(a) * .15 * S)], (k * 1.8 - j * .12) * 1.4, 1.6)
            _tx(p, ex - .3 * S, ey - .14 * S, wd, 28, k * 2.2 - j * .15 - .3, None, PEN[:3] if wd == 'weary' else CHALK)


def sketch_now(t):
    """which answer's sketch, and how far drawn"""
    for i, (tq, q, a, n) in enumerate(PING[:5]):
        t0 = tq + n * S16_
        t1 = PING[i + 1][0] + PING[i + 1][3] * S16_
        if t0 <= t < t1: return i, clamp((t - t0) / min(.32, (t1 - t0) * .7))
    return None, 0.


def draw_plot(p, t):
    """the window's picture once it is asked what it thinks: a night sheet, axes, the equation, the red line"""
    draw_sheet(p)
    p.d.line([p.P(HC[0], WY0), p.P(HC[0], WY1)], fill=CHALK + (170,), width=p.W(1.6))
    p.d.line([p.P(WX0, HC[1]), p.P(WX1, HC[1])], fill=CHALK + (170,), width=p.W(1.6))
    for s_ in (-1, 1):
        p.text(HC[0] + s_ * HS + 5, HC[1] + 5, str(s_), FW + 'cambria.ttc', 16, CHALK + (190,))
        p.text(HC[0] - 16, HC[1] - s_ * HS - 9, str(s_) if s_ < 0 else ' 1', FW + 'cambria.ttc', 16, CHALK + (190,))
    ex = '(x² + y² − 1)³ − x²y³ = 0'
    n = int(clamp((t - T_EQ) / .22) * len(ex))
    if n: p.text(WX0 + 70, WY0 + 52, ex[:n], FW + 'cambriai.ttf', 32, CHALK + (245,))
    f = pen_frac(t)
    na = ease((t - T_DENT - .35) / .25)
    if na > 0:                                                        # why it stops: there is no tangent here
        nx, ny = HC[0] + 34, HC[1] - HS * .62                          # inside the half drawn, below the dent
        p.text(nx, ny + 2, '∇', FW + 'seguisym.ttf', 24, CHALK + (int(220 * na),))
        p.text(nx + p.tlen('∇', FW + 'seguisym.ttf', 24) + 2, ny, 'F = 0', FW + 'cambriai.ttf', 26, CHALK + (int(220 * na),))
        p.d.line([p.P(nx + 10, ny - 4), p.P(HC[0] + 6, HC[1] - HS + 22)], fill=CHALK + (int(170 * na),), width=p.W(1.4))
    if f > 0:
        m = max(2, int(len(CURVE) * f))
        pts = [heart_pt(i / (len(CURVE) - 1)) for i in range(m)] + [heart_pt(f)]
        p.d.line([p.P(*q) for q in pts], fill=PEN, width=p.W(5.5), joint='curve')
        x, y = pts[0]; r = 2.75
        p.d.ellipse(p.R(x - r, y - r, x + r, y + r), fill=PEN)


def pen_frac(t):
    """the line's end: where the eye's pupil is (also between ticks, while it smears)"""
    tf = AN.frame_of(t)
    f = plot_frac(tf)
    for tk, fk in TICKS:
        if tk <= tf < tk + FR:
            prev = 0.
            for tk2, fk2 in TICKS:
                if tk2 < tk: prev = fk2
            return lerp(prev, fk, (tf - tk) / FR * .5 + .5)
    return f


def draw_window(p, t, rect=None):
    x0, y0, x1, y1 = rect or (WX0, WY0, WX1, WY1)
    for j in range(5):                                                # a soft shadow, cheaply
        e = 2 + j * 3
        p.d.rounded_rectangle(p.R(x0 + 4 - e * .3, y0 - 30 - e * .3, x1 + 8 + e, y1 + 10 + e), radius=p.S(e), fill=(0, 0, 0, 9))
    if rect is None and t >= T_PLOT + .03: draw_plot(p, t)
    elif rect is None and t >= T_SKETCH0:                             # its sheet: a sketch for each answer
        draw_sheet(p)
        i, k = sketch_now(t)
        if i is not None: sketch(p, i, k)
    else: paste_region(p, desk_img(), x0, y0, x1, y1)
    p.d.rectangle(p.R(x0 - 3, y0 - 34, x1 + 3, y1 + 3), outline=(226, 222, 214), width=p.W(2))
    p.d.rectangle(p.R(x0 - 3, y0 - 34, x1 + 3, y0), fill=(22, 22, 24))
    title = ('render://sandbox/0212   visualize(history, love)' if t < T_SKETCH0 else 'render://sandbox/0213   visualize(answer)') if t < T_PLOT + .03 else 'render://sandbox/0213   plot(love)'
    p.text(x0 + 10, y0 - 29, title, MONO, 19, (200, 196, 188))


def draw_chat(p, t, o, xoff=0., yoff=0.):
    d = p.d
    d.rectangle(p.R(xoff - (400 if not xoff else 0), TOPH, xoff + CHW, 1080), fill=BG)
    d.line([p.P(xoff + CHW, TOPH), p.P(xoff + CHW, 1080)], fill=LINE, width=p.W(1))
    L, box = layout(t, o)
    for it, sh, y, hh in L:
        if y + hh > VIEW0 - 4 and y < VIEW1 + 4 and p.seen(xoff, y, xoff + CHW, y + hh):
            if xoff: draw_item_off(p, it, sh, y, t, xoff)
            else: draw_item(p, it, sh, y, t)
    # the scroll thumb
    Hc = content_h(t)
    if Hc > VH:
        th = VH * VH / Hc; ty = VIEW0 + (VH - th) * clamp(o / (Hc - VH))
        d.rounded_rectangle(p.R(xoff + CHW - 9, ty + 4, xoff + CHW - 4, ty + th - 4), radius=p.S(3), fill=(196, 191, 183))
    # the box you type in (covers what scrolled below the view)
    d.rectangle(p.R(xoff - (400 if not xoff else 0), VIEW1, xoff + CHW - 1, 1080), fill=BG)
    d.rounded_rectangle(p.R(xoff + 40, 968, xoff + CHW - 40, 1040), radius=p.S(26), fill=(255, 255, 255), outline=LINE, width=p.W(1.5))
    if box:
        p.text(xoff + 66, 990, box, UI, 19, TXT)
        cx = xoff + 66 + p.tlen(box, UI, 19) + 2
        d.line([p.P(cx, 988), p.P(cx, 1018)], fill=TXT, width=p.W(2))
    else:
        p.text(xoff + 66, 990, 'Message…', UI, 19, (160, 154, 146))
    d.ellipse(p.R(xoff + CHW - 88, 982, xoff + CHW - 44, 1026), fill=(40, 38, 35) if box else LINE)
    d.polygon([p.P(xoff + CHW - 66, 993), p.P(xoff + CHW - 56, 1005), p.P(xoff + CHW - 76, 1005)], fill=(255, 255, 255))
    d.line([p.P(xoff + CHW - 66, 1003), p.P(xoff + CHW - 66, 1016)], fill=(255, 255, 255), width=p.W(3))
    # the top bar (covers what scrolled above)
    d.rectangle(p.R(-400, yoff - 60, WT, yoff + TOPH), fill=TOP)
    d.line([p.P(-400, yoff + TOPH), p.P(WT, yoff + TOPH)], fill=LINE, width=p.W(1))
    ring_icon(p, 28, yoff + 24, 9, -math.pi / 2, 2.6, (186, 28, 34))
    title = 'visualize the history of love by machine'
    tw = p.tlen(title, UIB, 17)
    if t >= L3 + .25: title += '   (Not Responding)'
    p.text(52, yoff + 12, title, UIB, 17, TXT)
    d.line([p.P(52 + tw + 12, yoff + 21), p.P(52 + tw + 17, yoff + 26), p.P(52 + tw + 22, yoff + 21)], fill=SUB, width=p.W(1.6))
    hover = t >= TF - .24
    for i, gl in enumerate(('min', 'max', 'close')):
        cx = WT - 120 + i * 45
        col = TXT
        if gl == 'close' and hover:
            d.rectangle(p.R(cx - 22, yoff, cx + 23, yoff + TOPH - 1), fill=(196, 43, 28)); col = (255, 255, 255)
        if gl == 'min': d.line([p.P(cx - 7, yoff + 24), p.P(cx + 7, yoff + 24)], fill=col, width=p.W(1.4))
        elif gl == 'max': d.rectangle(p.R(cx - 6, yoff + 18, cx + 6, yoff + 30), outline=col, width=p.W(1.4))
        else:
            d.line([p.P(cx - 6, yoff + 18), p.P(cx + 6, yoff + 30)], fill=col, width=p.W(1.4))
            d.line([p.P(cx + 6, yoff + 18), p.P(cx - 6, yoff + 30)], fill=col, width=p.W(1.4))


def draw_item_off(p, it, sh, y, t, xoff):
    """an item of the chat while it slides in (the squeeze)"""
    q = Pen.__new__(Pen); q.__dict__.update(p.__dict__); q.ox = p.ox - xoff * p.k
    draw_item(q, it, sh, y, t)


def pointer_sprite():
    """your pointer, drawn once, large: sampled by the shader along its path (it blurs when it moves fast)"""
    if 'spr' not in _SPR:
        img = Image.new('RGBA', (SPR_W * SPR_K, SPR_H * SPR_K), (0, 0, 0, 0))
        G.pointer(img, SPR_TIP[0], SPR_TIP[1], SPR_K)
        _SPR['spr'] = img
    return _SPR['spr']


_SPR = {}
SPR_W, SPR_H, SPR_K, SPR_TIP = 40, 48, 8, (4, 4)


def screen(t, pen):
    """the whole screen at t, into pen's image (your pointer is drawn by the shader, over the eye)"""
    p = pen
    p.d.rectangle([0, 0, p.w, p.h], fill=APPBG)
    if t < T_SQEND:
        r, xoff, yoff = squeeze_state(t)
        draw_window(p, t, r)
        draw_chat(p, t, 0., xoff=xoff, yoff=yoff)
        return
    draw_window(p, t)
    draw_chat(p, t, scroll_at(t))
    v = .55 * ease((t - L3 - .3) / .35) + .45 * ease((t - L3 - .65) / (TF - L3 - .75))
    if v > 0:
        p.d.rectangle([0, 0, p.w, p.h], fill=(255, 255, 255, int(115 * v)))


# ---------------- per frame: four sub-frames, each drawn at its own camera, in one atlas.  Within a sub-frame's
# slice of the exposure the shader follows the camera and the scroll (taps along the way), so fast moves blur.
SUB = 4
SHUTTER = .5
SLICE = SHUTTER / 60 / SUB                      # each sub-frame stands for this much time
MCAP = 120                                      # the most margin (px) drawn round the view for those taps
_FRAME = {}


def _zq(z):
    """the drawing scale: the zoom rounded up to a step of 1.25 (so type is not redrawn at every size)"""
    return 1.25 ** math.ceil(math.log(z) / math.log(1.25) - 1e-6)


def _sub_times(t):
    return [t + ((i + .5) / SUB - .5) * SHUTTER / 60 for i in range(SUB)]


def _motion(ts, w, h):
    """the cameras at the ends of the sub-frame's slice, the scroll there (relative to the drawn one), and how far a
    point of the screen travels within the slice (px of the drawing)"""
    c0, cm, c1 = cam(ts - SLICE / 2), cam(ts), cam(ts + SLICE / 2)
    o = scroll_at(ts)
    do = (scroll_at(ts - SLICE / 2) - o, scroll_at(ts + SLICE / 2) - o)
    sc = h / 1080.
    Wt = w / sc
    k = max(1., _zq(cm[2])) * sc
    disp = 0.
    for P in ((0, 0), (Wt, 0), (0, 1080), (Wt, 1080)):
        u0 = (c0[0] + (P[0] - Wt / 2) / c0[2], c0[1] + (P[1] - 540) / c0[2])
        u1 = (c1[0] + (P[0] - Wt / 2) / c1[2], c1[1] + (P[1] - 540) / c1[2])
        disp = max(disp, math.hypot(u1[0] - u0[0], u1[1] - u0[1]))
    disp = disp * k + abs(do[1] - do[0]) * k
    return c0, cm, c1, do, disp


def _draw(ts, w, h):
    sc = h / 1080.
    c0, (cx, cy, z), c1, do, disp = _motion(ts, w, h)
    zq = max(1., _zq(z))
    k = zq * sc
    Wt = w / sc
    M = int(min(MCAP, math.ceil(disp * .6) + 6))
    ox = math.floor((cx - Wt / 2 / z) * k) - M
    oy = math.floor((cy - 540. / z) * k) - M
    iw = int(math.ceil(w * zq / z)) + 2 * M + 1
    ih_ = int(math.ceil(h * zq / z)) + 2 * M + 1
    if T_SQ <= ts < T_SQEND:                                         # the squeeze: too fast for four; sixteen, averaged
        import numpy as np
        acc = None
        for j in range(4):
            img = Image.new('RGB', (iw, ih_), APPBG)
            screen(ts + (j - 1.5) / 4 * SLICE, Pen(img, k, ox, oy))
            a = np.asarray(img, dtype=np.float32)
            acc = a if acc is None else acc + a
        img = Image.fromarray((acc / 4 + .5).clip(0, 255).astype('uint8'), 'RGB')
    else:
        img = Image.new('RGB', (iw, ih_), APPBG)
        screen(ts, Pen(img, k, ox, oy))
    return img, (ox, oy, k), (c0, (cx, cy, z), c1, do)


def textures(t, w, h):
    ts = _sub_times(t)
    QW, QH = int(math.ceil(w * 1.25)) + 2 * MCAP + 8, int(math.ceil(h * 1.25)) + 2 * MCAP + 8
    atlas = Image.new('RGB', (QW * 2, QH * 2), (0, 0, 0))
    AW, AH = atlas.size
    quads = []
    for i, s in enumerate(ts):
        img, org, mot = _draw(s, w, h)
        qx, qy = (i % 2) * QW, (i // 2) * QH
        atlas.paste(img, (qx, qy))
        quads.append(((qx / AW, (AH - qy) / AH, 1 / AW, 1 / AH), (float(img.size[0]), float(img.size[1])), org, mot))
    _FRAME.update(t=t, ts=ts, quads=quads, w=w, h=h)
    return {'u_ui': atlas, 'u_ptr': pointer_sprite()}


def _sub_index(ts):
    if not _FRAME: return 0, None
    best = min(range(SUB), key=lambda i: abs(_FRAME['ts'][i] - ts))
    return best, _FRAME['quads'][best]


def _to_screen(p, c, Wt):
    return ((p[0] - c[0]) * c[2] + Wt / 2, (p[1] - c[1]) * c[2] + 540.)


def eye_uniforms(ts, c0, c1):
    tf = AN.frame_of(ts)
    Wt = (_FRAME.get('w', 1920) / (_FRAME.get('h', 1080) / 1080.))
    p0, p1 = AN.sample(EYE_T, ts)
    look = look_at(tf, AN.value(EYE_T, tf)[0])
    s0, s1 = _to_screen(p0, c0, Wt), _to_screen(p1, c1, Wt)
    b, age = brackets_at(tf)
    if b is not None:
        a0_, a1_ = _to_screen(b[:2], c0, Wt), _to_screen(b[2:], c0, Wt)
        b0_, b1_ = _to_screen(b[:2], c1, Wt), _to_screen(b[2:], c1, Wt)
        bx0, bx1 = (a0_[0], a0_[1], a1_[0], a1_[1]), (b0_[0], b0_[1], b1_[0], b1_[1])
        sn, held = _snap(max(0., age))
        if held: sn0 = sn1 = sn
        else:
            u = (ts - tf) / (.5 * FR) + .5; i = min(3, max(0, int(u * 4)))
            e0 = tf - .5 * FR + i * FR / 4
            sn0, sn1 = _snap(max(0., age - (tf - e0)))[0], _snap(max(0., age - (tf - e0 - FR / 4)))[0]
    else:
        bx0 = bx1 = (0., 0., 0., 0.); sn0 = sn1 = 1.
    pup = 1. + .12 * ease((tf - B(38) - .2) / .3) * (1 - ease((tf - Q + .1) / .1))
    return dict(u_e0=(s0[0], s0[1], p0[2] * c0[2], look), u_e1=(s1[0], s1[1], p1[2] * c1[2], look), u_eA=1.,
                u_ink=0. if tf < B(29) else 1.,                          # over the picture, still the desk's chalk
                u_bA=1. if b is not None else 0., u_bx0=bx0, u_bx1=bx1, u_bSn0=sn0, u_bSn1=sn1, u_pupS=pup)


def pointer_uniforms(ts, c0, c1):
    Wt = (_FRAME.get('w', 1920) / (_FRAME.get('h', 1080) / 1080.))
    x0, y0, busy = pointer_at(ts - SLICE / 2)
    x1, y1, _ = pointer_at(ts + SLICE / 2)
    a, b = _to_screen((x0, y0), c0, Wt), _to_screen((x1, y1), c1, Wt)
    return dict(u_pt0=a, u_pt1=b, u_ptZ=(c0[2] + c1[2]) / 2, u_ptA=1., u_busy=busy if busy is not None else -99.)


def params(ts):
    i, q = _sub_index(ts)
    if q is None:
        cm = cam(ts); c0 = c1 = cm
        P = dict(u_cam=cm)
    else:
        (qv, qs, org, (c0, cm, c1, do)) = q
        P = dict(u_q=qv, u_qs=qs, u_org=(float(org[0]), float(org[1]), float(org[2])), u_cam=cm, u_c0=c0, u_c1=c1, u_do=do,
                 u_chat=(-400., VIEW0, CHW, VIEW1) if ts >= T_SQEND else (0., 0., 0., 0.))
    P.update(eye_uniforms(ts, c0, c1))
    P.update(pointer_uniforms(ts, c0, c1))
    return P


SRC = r'''#version 330
uniform vec2 u_res; uniform float u_time, u_weight;
uniform sampler2D u_ui, u_ptr;
uniform vec4 u_q; uniform vec2 u_qs;              // this sub-frame's image in the atlas: uv of its top-left, 1/size; its size (px)
uniform vec3 u_cam, u_c0, u_c1;                   // the camera (centre in units, zoom): drawn with; at the ends of the slice
uniform vec2 u_do;                                // the scroll at the ends of the slice, less the drawn one (units)
uniform vec4 u_chat;                              // where the chat scrolls (units)
uniform vec3 u_org;                               // image px = units * org.z - org.xy
uniform vec4 u_e0, u_e1;                          // the eye at both ends of its exposure: x, y (1080 units, y down), R, look
uniform float u_eA, u_pupS, u_bA, u_bSn0, u_bSn1, u_ink;
uniform vec4 u_bx0, u_bx1;
uniform vec2 u_pt0, u_pt1; uniform float u_ptZ, u_ptA, u_busy;   // your pointer: its tip at both ends; its scale
out vec4 fragColor;
float h11(float p){ p = fract(p * .1031); p *= p + 33.33; p *= p + p; return fract(p); }
float h21(vec2 p){ vec3 p3 = fract(vec3(p.xyx) * .1031); p3 += dot(p3, p3.yzx + 33.33); return fract((p3.x + p3.y) * p3.z); }
vec3 srgb(float r, float g, float b){ return vec3(r, g, b) / 255.; }
vec3 untone(vec3 c, vec2 fc){
  vec3 L = pow(clamp(c, 0., .985), vec3(2.2));
  vec3 A = 2.51 - 2.43 * L, B = .03 - .59 * L, C = -.14 * L;
  vec3 y = (-B + sqrt(B * B - 4. * A * C)) / (2. * A);
  vec2 d = fc / u_res - .5;
  return y / 1.05 / (1. - .9 * dot(d, d));
}
vec3 tapUI(vec2 U){
  vec2 px = U * u_org.z - u_org.xy;
  px = clamp(px, vec2(.5), u_qs - .5);
  return textureLod(u_ui, vec2(u_q.x + px.x * u_q.z, u_q.y - px.y * u_q.w), 0.).rgb;
}
vec2 screenP(vec2 F){ float sc = u_res.y / 1080.; return vec2(F.x, u_res.y - F.y) / sc; }
vec2 toUI(vec2 P, vec3 c){ float sc = u_res.y / 1080.; return c.xy + (P - vec2(.5 * u_res.x / sc, 540.)) / c.z; }
vec3 scene(vec2 F){ return tapUI(toUI(screenP(F), u_cam)); }
vec3 sceneBlur(vec2 F){
  vec2 P = screenP(F);
  vec2 Um = toUI(P, u_cam), U0 = toUI(P, u_c0), U1 = toUI(P, u_c1);
  if(Um.x > u_chat.x && Um.x < u_chat.z && Um.y > u_chat.y && Um.y < u_chat.w){ U0.y += u_do.x; U1.y += u_do.y; }
  float len = length(U1 - U0) * u_org.z;
  if(len < 1.2) return tapUI(Um);
  int n = int(clamp(ceil(len / 1.1), 2., 20.));
  vec3 acc = vec3(0.);
  for(int i = 0; i < 20; i++){
    if(i >= n) break;
    acc += tapUI(mix(U0, U1, (float(i) + .5) / float(n)));
  }
  return acc / float(n);
}
const float GAPH = .42;
float sdSeg(vec2 p, vec2 a, vec2 b){ vec2 pa = p - a, ba = b - a; return length(pa - ba * clamp(dot(pa, ba) / max(dot(ba, ba), 1e-6), 0., 1.)); }
float sdRingGap(vec2 q, float R, float look, float gh){
  float ang = atan(q.y, q.x);
  float rel = mod(ang - look + 3.14159265, 6.2831853) - 3.14159265;
  if(abs(rel) > gh) return abs(length(q) - R);
  return min(length(q - R * vec2(cos(look + gh), sin(look + gh))), length(q - R * vec2(cos(look - gh), sin(look - gh))));
}
float sdRing(vec2 q, float R, float look){ return sdRingGap(q, R, look, GAPH); }
float sdBrackets(vec2 p, vec4 b, float sn, float pad){
  vec2 c = (b.xy + b.zw) * .5;
  float hw = (b.z - b.x) * .5 * sn + pad, hh = (b.w - b.y) * .5 * sn + pad * .7;
  float bw = max(pad * 1.1, min(hh * .5, 40.));
  float d = min(sdSeg(p, c + vec2(-hw, -hh), c + vec2(-hw - bw, 0.)), sdSeg(p, c + vec2(-hw - bw, 0.), c + vec2(-hw, hh)));
  d = min(d, min(sdSeg(p, c + vec2(hw, -hh), c + vec2(hw + bw, 0.)), sdSeg(p, c + vec2(hw + bw, 0.), c + vec2(hw, hh))));
  return d;
}
float lum(vec3 c){ return dot(c, vec3(.3, .55, .15)); }
void main(){
  vec2 F = gl_FragCoord.xy;
  vec3 col = sceneBlur(F);
  float sc = u_res.y / 1080.;
  vec2 P = vec2(F.x, u_res.y - F.y) / sc;
  float pu = 1. / sc;
  if(u_eA > 0.){
    float W = max(.2 * u_e1.z + 1., min(12., .35 * u_e1.z));
    vec2 cA = u_e0.xy, cB = u_e1.xy;
    float near = sdSeg(P, cA, cB) - max(u_e0.z, u_e1.z) * 1.6 - 30.;
    float nearB = u_bA > 0. ? (max(max(min(min(u_bx0.x, u_bx1.x), min(u_bx0.z, u_bx1.z)) - P.x, P.x - max(max(u_bx0.z, u_bx1.z), max(u_bx0.x, u_bx1.x))),
                                   max(min(u_bx0.y, u_bx1.y) - P.y, P.y - max(u_bx0.w, u_bx1.w))) - 200.) : 1e5;
    if(near < 0. || nearB < 0.){
      float core = 0., shad = 0., glow = 0., pcov = 0.;
      vec2 so = vec2(.08, .13) * u_e1.z + vec2(1., 1.6);
      float bpad = max(6., u_e1.z * .45), bW = max(2.2, W * .8);
      for(int k = 0; k < 24; k++){
        float f = (float(k) + .5) / 24.;
        vec2 c = mix(cA, cB, f);
        float R = mix(u_e0.z, u_e1.z, f), lk = mix(u_e0.w, u_e1.w, f);
        float Wk = max(.2 * R + 1., min(12., .35 * R));
        float d = sdRing(P - c, R, lk) - Wk * .5;
        vec4 bxk = mix(u_bx0, u_bx1, f); float snk = mix(u_bSn0, u_bSn1, f);
        float db = u_bA > 0. ? sdBrackets(P, bxk, snk, bpad) - bW * .5 : 1e5;
        vec2 pc = c + vec2(cos(lk), sin(lk)) * R * .22;
        float pr = R * .38 * u_pupS;
        float ds = sdRing(P - so - c, R, lk) - Wk * .5;
        if(u_bA > 0.) ds = min(ds, sdBrackets(P - so * .6, bxk, snk, bpad) - bW * .5);
        ds = min(ds, length(P - so - pc) - pr);
        core += 1. - smoothstep(-pu * .6, pu * .6, min(d, db));
        shad += 1. - smoothstep(-Wk * .3, Wk * 1.6 + 2., ds);
        glow += exp(-max(d, 0.) / (Wk * 1.8));
        pcov += 1. - smoothstep(pr - pu * .7, pr + pu * .7, length(P - pc));
      }
      core /= 24.; shad /= 24.; glow /= 24.; pcov /= 24.;
      vec3 bg = col;
      float light = smoothstep(.3, .62, lum(bg)) * u_ink;             // on the light page: ink; over the picture: chalk
      vec3 CH = mix(srgb(238., 234., 222.), srgb(30., 28., 26.), light);
      col *= 1. - mix(.5, .16, light) * shad * u_eA;
      if(pcov > 0.){
        vec2 cm = mix(cA, cB, .5) + vec2(cos(u_e1.w), sin(u_e1.w)) * u_e1.z * .22;
        float pr = u_e1.z * .38 * u_pupS;
        vec3 acc = vec3(0.);
        for(int i = 0; i < 12; i++){
          float a = float(i) * 2.39996 + h11(floor(u_time * 11.) + float(i));
          float rr = sqrt((float(i) + .5) / 12.) * pr * sc * .95;
          acc += scene(F + vec2(cos(a), sin(a)) * rr);
        }
        acc /= 12.;
        float frost = h21(floor(F * .8)) - .5;
        vec3 glass = mix(acc, srgb(206., 46., 48.), mix(.66, .74, light)) * (1. + .07 * frost);
        float still = 1. / (1. + 3. * length(cB - cA) / max(pr, 1.));
        glass = mix(glass, srgb(232., 120., 116.), (1. - smoothstep(.0, 1.4 * pu, abs(length(P - cm) - pr + 1.1 * pu))) * .35 * still);
        col = mix(col, glass, pcov * u_eA);
      }
      col += CH * glow * .08 * (1. - light) * u_eA;
      col = mix(col, CH, core * u_eA);
    }
  }
  // your pointer, over everything: the arrow (and, when the app hangs, the system's busy ring beside it)
  if(u_ptA > 0.){
    float near = sdSeg(P, u_pt0, u_pt1) - 64. * u_ptZ;
    if(near < 0.){
      vec4 acc = vec4(0.);
      for(int k = 0; k < 12; k++){
        vec2 tip = mix(u_pt0, u_pt1, (float(k) + .5) / 12.);
        vec2 q = (P - tip) / u_ptZ + vec2(4.);
        vec4 s = vec4(0.);
        if(q.x > 0. && q.y > 0. && q.x < 40. && q.y < 48.){
          vec4 tx = texture(u_ptr, vec2(q.x / 40., 1. - q.y / 48.));
          s = vec4(tx.rgb * tx.a, tx.a);
        }
        if(u_busy > -50.){
          vec2 bq = (P - tip) / u_ptZ - vec2(25.);
          float d = sdRingGap(bq, 11., u_busy + 5.7596, .5236) - 1.7;
          float a = 1. - smoothstep(-.6 * pu / u_ptZ, .6 * pu / u_ptZ, d);
          s = s * (1. - a) + vec4(srgb(40., 40., 44.) * a, a);
        }
        acc += s;
      }
      acc /= 12.;
      col = col * (1. - acc.a) + acc.rgb;
    }
  }
  if(any(isnan(col))) col = vec3(0.);
  fragColor = vec4(untone(col, gl_FragCoord.xy) * u_weight, 1.);
}
'''
