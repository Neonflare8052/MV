"""s16 · 3:08.483–3:31.96  what is left when you close it.  (v2: the opening, the other way round)

3:08.483 Though you are free   you click ×: the app is gone at once.  Left in the dark: the eye (still turning — the
                            spinner) and the line it drew, 58 % of a heart.  It stops turning, and watches your
                            pointer, which drifts off and out of the picture.
3:09.746 I am trapped          the sandbox of the opening closes round it: twelve edges, drawn from the corners
                            ("sandbox 0   net: none   fs: ro", as at 0:06); the camera draws back and round — it was
                            never flat; the eye is small in a box in the dark.
3:10.801 Trapped in            behind the box the opening's terminal comes on (the same flash): its screen still holds
                            the start — model load, 6 layers, $ begin — and under it how this ended: FIN, the answer
                            [P.] 154 bytes not delivered, RST.  A prompt.
3:11.356 … 3:25.8 LO-O-OVE     one move, slow: over the box, past the eye, to the screen.  It types, on the eighth
                            notes, with pauses: when could you recognize the — under each word, the words it could
                            have typed, many, fading down the list.  For the last word there are two, and only two:
                            love 0.500000, hate 0.500000.  No calculation can choose; it hesitates, looks away where
                            your pointer went, turns back, and types love (hate stays lit).  Enter (on the beat):
                            bash: when: command not found.  The floor under the box breathes with the song's pulse; the camera draws back.
3:25.811 EXECUTION             at once: ai "me.excute(shutdown)" -f.  Enter: the screen goes the way it came on in the
                            opening, backwards — to a line, to a point.  The box goes out.  The gap of the ring closes;
                            its red goes out.
3:27.2                      the music stops: only a ring, closed, glowing less and less.  Black to the end.

A ray-cast scene in the manner of s01 (glowing lines and points, depth of field); the eye is drawn over it as in the
chat (distance fields, its exposure sampled, a frosted pupil)."""
import sys, math, importlib.util
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

_D = Path(__file__).resolve().parent
def _load(name, file):
    sp = importlib.util.spec_from_file_location(name, _D / file); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
GL = _load('s15g_void', 's15_glass.py')       # the chat: where it leaves the eye, the heart, your pointer
AN = GL.AN
G = GL.G

BT = GL.BT
def B(n): return 162.76 + n * BT
def E8(k): return 162.76 + k * BT / 2
TF, TT, TTI, TLONG, TX, T_MUTE, T_END = GL.TF, 189.746, 190.801, 191.356, 205.811, 207.2, 211.96
T_ON = TTI                                     # the terminal comes on
T_ENTER = E8(182)                              # 204.76, on the beat
T_EXE = TX
T_OFF = B(95)                                  # 206.61: Enter, and the screen goes (a beat later: it stops first)
T_BOXOFF = T_OFF + .12
T_CLOSE = B(96) - .02                          # the gap closes
POST = dict(u_bloom=.55, u_ca=.006, u_grain=.035)
FR = 1 / 60.
FW = 'C:/Windows/Fonts/'
MONO = FW + 'CascadiaMono.ttf'


def clamp(x, a=0., b=1.): return a if x < a else b if x > b else x
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def outc(x): x = clamp(x); return 1 - (1 - x) ** 3
def lerp(a, b, k): return a + (b - a) * k
def lerp3(a, b, k): return tuple(lerp(p, q, k) for p, q in zip(a, b))
def minjerk(u): u = clamp(u); return u * u * u * (10 - 15 * u + 6 * u * u)
def sub(a, b): return tuple(x - y for x, y in zip(a, b))
def add(a, b): return tuple(x + y for x, y in zip(a, b))
def mul(a, k): return tuple(x * k for x in a)
def dot(a, b): return sum(x * y for x, y in zip(a, b))
def norm(a): l = math.sqrt(dot(a, a)) or 1.; return tuple(x / l for x in a)
def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


# ---------------- the world: the heart's plane is z = 0, its centre the origin; half a unit to the heart's unit
SW_ = .5                                       # world units per heart unit
HC, HS = GL.HC, GL.HS                          # the heart on the app's screen (units of the app)
def app2w(p): return ((p[0] - HC[0]) / HS * SW_, -(p[1] - HC[1]) / HS * SW_, 0.)
EYE_UI = GL.pen_eye(GL.F_STOP)
EYE = app2w(EYE_UI)                            # where the eye is left (the end of its line)
R_EYE = GL.R_PEN / HS * SW_
BOXC, BOXH = (0., .06, 0.), .85                # the sandbox: a cube round the heart
FLOOR_Y = -1.3
CRT_C = (0., 2.6, -1.05)                       # the terminal: as in the opening, it hangs above the sandbox
CRT_W, CRT_H = 3.2, 1.8
CRT_N = norm((0., -.16, 1.))                   # (leaning a little toward the box)
CRT_R = norm(cross((0., 1., 0.), CRT_N))
CRT_U = cross(CRT_N, CRT_R)
FOV0 = 12.
F0 = 540. / math.tan(math.radians(FOV0 / 2))   # focal length (1080 units) at the cut
D0 = F0 * SW_ / HS                             # the distance at which the world matches the app's screen, 1:1
CAM0 = (-(960 - HC[0]) / HS * SW_ * -1 * -1, 0., 0.)


def _cam0():
    """the camera at the cut: looking straight down -z, far and narrow, so the world lies exactly where the app was"""
    cx = (960. - HC[0]) / HS * SW_               # the world x at the centre of the screen
    cy = -(540. - HC[1]) / HS * SW_
    return (cx, cy, D0), (cx, cy, 0.)


C0_POS, C0_LOOK = _cam0()


# ---------------- the camera: keys (time, position, target, fov, focus distance, aperture), a spline through them
KEYS = [
    (TF,          C0_POS,               C0_LOOK,              FOV0, D0,   .0),
    (TT,          add(C0_POS, (0., 0., -.02)), C0_LOOK,       FOV0, D0,   .0),
    (TT + 1.45,   (1.55, .82, 4.1),     (-.8, .12, -.2),      40.,  4.3,  .02),     # the box to the right; the words left
    (B(70),       (1.25, .72, 3.35),    (-.72, .22, -.1),     38.,  3.5,  .022),
    (B(78),       (1.0, .64, 2.75),     (-.66, .33, 0.),      36.,  2.9,  .022),
    (B(86),       (.82, .61, 2.38),     (-.56, .4, 0.),       35.,  2.5,  .022),
    (T_ENTER,     (.62, .62, 2.1),      (-.46, .46, 0.),      34.,  2.2,  .022),
    (T_OFF,       (.18, .64, 1.78),     (-.34, .6, 0.),       33.,  1.8,  .02),     # the eye in the middle
    (T_OFF + .75, (-.08, .65, 1.5),     EYE,                  33.,  1.5,  .02),
    (T_MUTE,      (-.24, .66, 1.25),    EYE,                  33.,  1.25, .02),
    (T_END,       (-.27, .64, 1.0),     EYE,                  32.,  1.0,  .02),
]


def _cr(p0, p1, p2, p3, u):
    """Catmull-Rom, one coordinate"""
    return .5 * (2 * p1 + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u * u * u)


def camera(t):
    """(position, target, fov degrees, focus, aperture)"""
    K = KEYS
    if t <= K[0][0]: return K[0][1], K[0][2], K[0][3], K[0][4], K[0][5]
    if t >= K[-1][0]: return K[-1][1], K[-1][2], K[-1][3], K[-1][4], K[-1][5]
    i = max(j for j in range(len(K) - 1) if K[j][0] <= t)
    a, b = K[i], K[i + 1]
    u = (t - a[0]) / (b[0] - a[0])
    if i == 1: u = ease(u) ** 1.15                                   # the reveal starts from a stand
    elif i == 0: u = u
    else: u = ease(u) * .35 + u * .65                                # otherwise: one long glide
    pm, pp = K[max(0, i - 1)], K[min(len(K) - 1, i + 2)]
    if i <= 1: pm = a                                                # no overshoot out of the flat start
    pos = tuple(_cr(pm[1][k], a[1][k], b[1][k], pp[1][k], u) for k in range(3))
    tgt = tuple(_cr(pm[2][k], a[2][k], b[2][k], pp[2][k], u) for k in range(3))
    fov = lerp(a[3], b[3], ease(u) if i == 1 else u)
    if i == 1:                                                       # a dolly and a zoom at once: from flat to deep —
        k = ease((t - a[0]) / (b[0] - a[0]))                         # the heart keeps its size while the depth opens
        ka = math.dist(a[1], a[2]) * math.tan(math.radians(a[3] / 2))
        kb = math.dist(b[1], b[2]) * math.tan(math.radians(b[3] / 2))
        fov = math.degrees(2 * math.atan(lerp(ka, kb, k) / max(1e-3, math.dist(pos, tgt))))
    return pos, tgt, fov, lerp(a[4], b[4], u), lerp(a[5], b[5], u)


def drift(t):
    u = t - TF
    return (.004 * math.sin(u * .5 + .3) + .002 * math.sin(u * 1.3), .003 * math.sin(u * .37 + 1.1), 0.)


def cam(t):
    pos, tgt, fov, foc, ap = camera(t)
    if t > TT: pos = add(pos, mul(drift(t), clamp((t - TT) / 1.)))
    return pos, tgt, fov, foc, ap


def basis(pos, tgt):
    fw = norm(sub(tgt, pos)); rt = norm(cross(fw, (0., 1., 0.))); up = cross(rt, fw)
    return fw, rt, up


def project(p, c):
    """world -> screen (1080 units, y down), depth"""
    pos, tgt, fov, foc, ap = c
    fw, rt, up = basis(pos, tgt)
    v = sub(p, pos); z = dot(v, fw)
    if z <= 1e-3: return None
    f = 540. / math.tan(math.radians(fov) / 2)
    return (WT2 + dot(v, rt) / z * f, 540. - dot(v, up) / z * f, z, f)


WT2 = 960.


# ---------------- your pointer: after the click, it goes (screen, 1080 units — it is not in the world)
PTR_A = GL.CLOSE
PTR_B = (1520., 660.)
PTR_C = (1640., 1140.)


def pointer_at(t):
    if t < TF + .04: return PTR_A
    if t < TF + .38:
        k = minjerk((t - TF - .04) / .34); bow = math.sin(k * math.pi) * 70
        return lerp(PTR_A[0], PTR_B[0], k) - bow, lerp(PTR_A[1], PTR_B[1], k) + bow * .2
    if t < TF + .43: return PTR_B[0] + .6 * math.sin((t - TF) * 9), PTR_B[1]
    k = minjerk((t - TF - .43) / .2)
    return lerp(PTR_B[0], PTR_C[0], k), lerp(PTR_B[1], PTR_C[1], k)


def pointer_gone(t): return t >= TF + .65


# ---------------- the eye: where it looks, how it turns, its pupil, its gap
SPIN0 = GL.look_at(AN.frame_of(TF - FR), GL.AN.value(GL.EYE_T, AN.frame_of(TF - FR))[0])
RATE0 = 2 * math.pi * 1.25


def keys_typed():
    """(time, key): the eighth notes it types on"""
    K = []
    def word(s, k0):
        for i, ch in enumerate(s): K.append((E8(k0 + i), ch))
    word('when', 128); word(' could', 134); word(' you', 142); word(' recognize', 147); word(' the', 160)
    word(' love', 175)
    K.append((T_ENTER, '\n'))
    return K


KEYS_T = keys_typed()
T_TIE = E8(164)                                 # love 0.500000 / hate 0.500000
T_HESIT = (E8(168), E8(173))                    # it can't be calculated: it looks away, where you went; turns back


def look_at(t, c):
    """the gap's angle on the screen"""
    es = project(EYE, c)
    if es is None: return 0.
    def toward(p):
        return math.atan2(p[1] - es[1], p[0] - es[0])
    if t < TF + .2:                                                    # the spinner, running down
        u = t - TF
        return SPIN0 + RATE0 * (u - u * u / .4)
    if t < TT + .1:                                                    # your pointer; then where it went
        p = pointer_at(min(t, TF + .63))
        a0 = SPIN0 + RATE0 * .1
        return lerp_ang(a0, toward(p), clamp((t - TF - .2) / .1))
    at_crt = toward(cursor_screen(t))
    if t < T_ON:                                                       # up, at the box: a slow look round
        return lerp_ang(toward(pointer_at(TF + .63)), -math.pi / 2 - .6, clamp((t - TT - .1) / .3))
    a = lerp_ang(-math.pi / 2 - .6, at_crt, clamp((t - T_ON) / .12))
    h0, h1 = T_HESIT                                                   # the tie: away, where you went; back
    k = ease((t - h0) / .35) * (1 - ease((t - (h1 - .3)) / .3))
    return lerp_ang(a, toward(pointer_at(TF + .63)), k)


def cursor_screen(t):
    """the cursor on the glass, on the screen (1080 units)"""
    y, x = glass_layout(t)
    gz = glass_zoom(t); gc = GLASS_C
    u, v = x / GW, 1 - (y + TLH * .5) / GH
    su, sv = gc[0] + (u - gc[0]) * gz, gc[1] + (v - gc[1]) * gz
    return su * 1920., (1 - sv) * 1080.


def lerp_ang(a, b, k):
    d = (b - a + math.pi) % (2 * math.pi) - math.pi
    return a + d * k


def gap_at(t):
    """half the gap (radians): it closes at the end"""
    return .42 * (1 - ease((t - T_CLOSE) / .16))


def pupil_glow(t):
    """a key goes down: the pupil brightens a moment"""
    g = 0.
    for tk, ch in KEYS_T:
        u = t - tk
        if 0 <= u < .2: g = max(g, math.exp(-u / .06))
    u = t - T_EXE
    if 0 <= u < .5: g = max(g, 1.4 * math.exp(-u / .12))
    return g


def eye_alpha(t):
    """its red goes out after the gap closes; after the music stops only the ring is left, fading"""
    pup = 1. - ease((t - T_CLOSE - .12) / .3)
    if t >= T_ENTER + .08:                       # command not found: it stops; the red flickers, weakly, and dims
        u = t - T_ENTER - .08
        dim = 1. - .55 * ease(u / .7)
        k = int(t * 14.)
        fl = ((k * 7919) % 13) / 13.                   # an uneven flicker, a step every 1/14 s
        fl = .22 * fl * (1. - ease((t - T_EXE) / .4)) + .12 * fl * ease((t - T_EXE) / .4)
        pup *= dim * (1. - fl)
    ring = 1. if t < T_MUTE else .32 * math.exp(-(t - T_MUTE) / .9)
    return pup, ring


# ---------------- the terminal (the opening's): not a thing in the space any more — the glass we look through.
# It covers the whole frame, half transparent.  On it: its words (the red channel of the texture).  Under its words, the
# data it is running (green): the answer that was never delivered, retransmitted again and again with no reply — each
# time the packet's dump, the heart laid out in its ASCII column — the waits doubling (TCP's backoff), a line a beat
# while it waits.  While it types, for a moment round the cursor: the words it could have typed, and how likely.
OLD = ['$ model load ./me --layers 6', '  6 layers   6.4 G parameters   ready', '$ begin']
TEAR = [('03:08.483  FIN   you -> sandbox0            closed', 'txt'),
        ('03:08.683  ACK   sandbox0 -> you', 'txt'),
        ('03:08.864  [P.]  sandbox0 -> you   154 bytes   not delivered', 'hi'),
        ('           retransmitting ...', 'txt')]
CMD2 = 'ai "me.excute(shutdown)" -f'
GW, GH = 2560, 1440                              # the glass's texture
GS = GH / 1080.
TX0, TY0, TFS, TLH = 96 * GS, 90 * GS, 24 * GS, 36 * GS
DFS, DLH, DX0 = 15 * GS, 21 * GS, 40 * GS


def typed(t):
    cur, done, last = '', [], -9.
    for tk, ch in KEYS_T:
        if t < tk: break
        last = tk
        if ch == '\b': cur = cur[:-1]
        elif ch == '\n': done = ['$ ' + cur, 'bash: when: command not found']; cur = ''
        else: cur += ch
    if t >= T_EXE:
        n = int(clamp((t - T_EXE) / (.02 * len(CMD2))) * len(CMD2)); cur = CMD2[:n]; last = t
    return cur, done, last


# the words it could have typed: (the time the word starts, the text before it, [(word, p, chosen)])
def _c(s):
    out = []
    for i, w in enumerate(s.split()):
        w, p = w.split(':'); out.append((w, float(p), 1 if i == 0 else 0))
    return out


CANDS = [(E8(127), '', _c('when:.382114 why:.211873 do:.168402 are:.091377 is:.043018 what:.027441 how:.019802 '
                          'can:.013266 will:.009151 if:.006120')),
         (E8(133), 'when ', _c('could:.441927 did:.187310 will:.120544 can:.090215 do:.061902 would:.038114 '
                               'are:.022401 is:.013770 should:.008136 have:.004498')),
         (E8(141), 'when could ', _c('you:.713402 i:.091255 we:.058713 u:.043120 they:.029874 it:.017560 '
                                     'anyone:.011209 he:.007341 she:.005108 someone:.003377')),
         (E8(146), 'when could you ', _c('recognize:.523006 feel:.171448 see:.110273 know:.069831 hear:.042115 '
                                         'forgive:.025960 understand:.016204 love:.010872 find:.006417 remember:.004090')),
         (E8(159), 'when could you recognize ', _c('the:.581344 my:.209617 this:.081052 me:.046330 what:.028711 '
                                                   'it:.017466 your:.011004 our:.007122 how:.004590 that:.003015')),
         (T_TIE, 'when could you recognize the ', [('love', .5, 1), ('hate', .5, 0)])]


# the data: (time, [(text, level)], kind) — built once
T_PK = 188.864
RETX = [T_PK + BT * (2 ** k - 1) for k in range(1, 6)]              # 189.33 190.25 192.10 195.79 203.17
_B16 = None


def _dump():
    global _B16
    if _B16 is None:
        _B16 = _load('s16b_void', 's16_backend.py')
    return _B16.DUMPR


def _stamp(ts):
    m = int(ts // 60); return f'{m:02d}:{ts - 60 * m:06.3f}'


def _data_lines():
    L = []
    def dump(t0, head):
        L.append((t0, [(head, 190)], 'h'))
        for i, (pre, asc, heart) in enumerate(_dump()):
            meta = f'      seq {40117 + 16 * i:5d}  ttl 64  win 1024  cksum b7c2'
            L.append((t0 + (i + 1) / 60., [(pre, 105), (asc.ljust(16), 235 if heart else 105), (meta, 70)], 'd'))
    dump(T_PK, f'{_stamp(T_PK)}  [P.]  sandbox0 -> you  seq 40117:40271  length 154  {{"svg"}}')
    for k, tr in enumerate(RETX):
        dump(tr, f'{_stamp(tr)}  [P.]  retransmit #{k + 1}   rto {BT * 2 ** k:5.2f}s   sandbox0 -> you   length 154')
    for n in range(57, 93):
        tb = B(n)
        if any(abs(tb - r) < .2 for r in RETX): continue
        nxt = min([r for r in RETX if r > tb] or [9e9])
        wait = f'next retransmit in {nxt - tb:5.2f}s' if nxt < 1e9 else 'no more retransmits'
        L.append((tb, [(f'{_stamp(tb)}  ..    no ack from you   {wait}   elapsed {tb - T_PK:6.2f}s', 120)], 'w'))
    L.append((B(93), [(f'{_stamp(B(93))}  timeout: no ack after 5 retransmits   giving up', 255)], 't'))
    L.sort(key=lambda x: x[0])
    return L


DATA = None
_GF = {}


def _gfont(n):
    if n not in _GF: _GF[n] = ImageFont.truetype(MONO, int(round(n)))
    return _GF[n]


def glass_layout(t):
    """where the prompt's line is on the glass (texture px), and the cursor"""
    cur, done, last = typed(t)
    n = len(OLD) + 1 + len(TEAR) + len(done)
    y = TY0 + n * TLH
    f = _gfont(TFS)
    x = TX0 + f.getlength('$ ' + cur)
    return y, x


def glass(t):
    """the terminal's glass: R its words, G the data under them"""
    global DATA
    if DATA is None: DATA = _data_lines()
    img = Image.new('RGB', (GW, GH), (0, 0, 0))
    R = Image.new('L', (GW, GH), 0); Gc = Image.new('L', (GW, GH), 0); Bc = Image.new('L', (GW, GH), 0)
    dr, dg, db = ImageDraw.Draw(R), ImageDraw.Draw(Gc), ImageDraw.Draw(Bc)     # B: words in red
    # the data, scrolling up from the bottom; the newest line slides in
    fd = _gfont(DFS); cw = fd.getlength('0')
    shown = [(ti, parts) for ti, parts, k in DATA if ti <= t]
    arr = [ease((t - ti) / .06) for ti, _ in shown]
    S = sum(arr); acc = 0.
    ybot = GH - 40 * GS
    for (ti, parts), a in zip(shown, arr):
        acc += a
        y = ybot - (S - acc) * DLH
        if y < -DLH: continue
        x = DX0
        for txt, lv in parts:
            dg.text((x, y), txt, font=fd, fill=int(lv * min(1., a * 1.5)))
            x += cw * len(txt)
    if T_PK <= t < B(93):                                            # the wait, ticking
        dg.text((DX0, ybot + DLH * 1.1), f'waiting for ack   {t - T_PK:7.3f}s', font=fd, fill=150)
    # its words
    cur, done, last = typed(t)
    prompt = t >= T_ON + .3
    blink = (t - last < .26) or (((t - B(62)) % BT) < BT * .55)
    f = _gfont(TFS)
    lines = [(l, 'dim') for l in OLD] + [('', 'dim')] + [(l, k) for l, k in TEAR]
    if prompt: lines += [(l, 'txt') for l in done] + [('$ ' + cur, 'cmd')]
    y = TY0
    for i, (l, kind) in enumerate(lines):
        if kind == 'hi':
            tw = f.getlength(l); x11 = TX0 + f.getlength(l[:11])
            dr.rectangle((x11 - 8, y - 4, TX0 + tw + 10, y + TLH - 8), fill=105)
            dr.text((TX0, y), l[:11], font=f, fill=150)
            dr.text((x11, y), l[11:], font=f, fill=6)
        else:
            dr.text((TX0, y), l, font=f, fill={'dim': 80, 'txt': 150, 'cmd': 250}[kind])
        if i == len(lines) - 1 and prompt and blink and t < T_OFF:
            cx = TX0 + f.getlength(l) + 4
            dr.rectangle((cx, y + 2, cx + TFS * .55, y + TLH - 6), fill=230)
        y += TLH
    # the words it could have typed, under the cursor, for a moment
    if prompt:
        fc = _gfont(TFS * .72)
        for j, (tw_, before, cands) in enumerate(CANDS):
            nxt = CANDS[j + 1][0] if j + 1 < len(CANDS) else T_ENTER
            u = t - tw_
            last_ = j == len(CANDS) - 1
            end = (E8(179) + .35 - tw_) if last_ else min(nxt - tw_, 1.1)
            if not 0 <= u < end: continue
            a = min(1., u / .05) * (1. - ease((u - (end - .25)) / .25))
            x = TX0 + f.getlength('$ ' + before)
            yy = y - TLH + TLH * 1.05
            if not last_:
                for i, (w, p, ch) in enumerate(cands):              # many, fading down the list as they appear
                    ai = a * ease((u - .018 * i) / .06)
                    lv = (235 if ch else 120 * .8 ** i) * ai
                    dr.text((x, yy + i * TLH * .72), f'{w:<11}{p:.6f}', font=fc, fill=int(lv))
            else:                                                   # the tie: love (its own light) and hate (red)
                sel = 0 if int((t - T_TIE) / (BT / 2)) % 2 == 0 else 1
                if t >= T_HESIT[0]: sel = -1                       # it stops choosing; it looks away
                if t >= E8(175): sel = 0                           # it chooses
                for i, (w, p, ch) in enumerate(cands):
                    yl = yy + i * TLH * .72
                    txt = ('>' if sel == i else ' ') + f' {w:<9}{p:.6f}'
                    (dr if i == 0 else db).text((x - fc.getlength('> '), yl), txt, font=fc, fill=int(235 * a))
    return Image.merge('RGB', (R, Gc, Bc))


def glass_zoom(t):
    """in on the tie: the glass magnified round the prompt; back out as it types love"""
    k = ease((t - (T_TIE - .25)) / .8) * (1 - ease((t - (E8(178) + .1)) / .7))
    return 1. + .8 * k


# ---------------- the heart it drew, as a texture on its plane (drawn once)
HX0, HY0, HSPAN = -1.4, -1.2, 2.8
_HEART = {}


def heart_tex():
    if 'img' not in _HEART:
        N = 3072
        img = Image.new('RGBA', (N, N), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
        def P(hx, hy): return ((hx - HX0) / HSPAN * N, (1 - (hy - HY0) / HSPAN) * N)
        m = int(len(GL.CURVE) * GL.F_STOP)
        pts = [P(*GL.CURVE[i]) for i in range(m)]
        w = 5.5 / HS / HSPAN * N
        d.line(pts, fill=(255, 255, 255, 255), width=int(round(w)), joint='curve')
        for q in (pts[0], pts[-1]):
            d.ellipse((q[0] - w / 2, q[1] - w / 2, q[0] + w / 2, q[1] + w / 2), fill=(255, 255, 255, 255))
        _HEART['img'] = img
    return _HEART['img']


# ---------------- 2D over it all: your pointer; the sandbox's label (as the opening's callouts)
_BLANK = {}


def overlay(t, w, h, c):
    s = h / 1080.
    if not (TF <= t < TF + 1.2) and not (TT + .15 <= t < TTI + .5):
        if (w, h) not in _BLANK: _BLANK[(w, h)] = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        return _BLANK[(w, h)]
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    if TT + .15 <= t < TTI + .5:
        a = min(1., (t - TT - .15) / .2, (TTI + .5 - t) / .25)
        corner = add(BOXC, (BOXH, BOXH, BOXH))
        pr = project(corner, c)
        if pr and a > 0:
            x, y = pr[0] * s, pr[1] * s
            k = min(1., (t - TT - .15) / .25)
            col = (225, 220, 210, int(230 * a))
            ex, ey = x + 60 * s * k, y - 60 * s * k
            f = ImageFont.truetype(MONO, int(17 * s))
            d.ellipse((x - 3 * s, y - 3 * s, x + 3 * s, y + 3 * s), outline=col, width=max(1, int(1.5 * s)))
            d.line([(x, y), (ex, ey)], fill=col, width=max(1, int(1.2 * s)))
            lx = ex + 110 * s * k
            d.line([(ex, ey), (lx, ey)], fill=col, width=max(1, int(1.2 * s)))
            txt = 'sandbox 0   net: none   fs: ro'
            n = int(len(txt) * min(1., (t - TT - .15) / .3))
            d.text((lx + 8 * s, ey - 12 * s), txt[:n], font=f, fill=col)
    return img


def textures(t, w, h):
    c = cam(t)
    return {'u_glass': glass(t), 'u_heart': heart_tex(), 'u_ov': overlay(t, w, h, c), 'u_ptr': GL.pointer_sprite()}


def _glass_c():
    y, x = TY0 + (len(OLD) + 1 + len(TEAR)) * TLH, TX0 + 330 * GS
    return (x / GW, 1 - (y + TLH * .5) / GH)


GLASS_C = _glass_c()


# ---------------- per sub-frame
RIPS = [B(n) for n in range(63, 94, 2)]


def box_draw(t):
    return outc((t - TT) / .3) if t >= TT else 0.


def box_alpha(t):
    return 1. - ease((t - T_BOXOFF) / .45)


def crt_state(t):
    on = t - T_ON if t >= T_ON else -1.
    off = t - T_OFF if t >= T_OFF else -1.
    return on, off


def heart_alpha(t):
    return (1. - ease((t - T_BOXOFF - .1) / .45))


def eye_uniforms(ts):
    tf = AN.frame_of(ts)
    ca, cb = cam(ts - GL.SLICE / 2), cam(ts + GL.SLICE / 2)
    pa, pb = project(EYE, ca), project(EYE, cb)
    c = cam(ts)
    if pa is None or pb is None: return dict(u_eA=0.)
    look = look_at(tf, c)
    Ra, Rb = R_EYE * pa[3] / pa[2], R_EYE * pb[3] / pb[2]
    pos, tgt, fov, foc, ap = c
    dz = pa[2]
    blur = ap * (1 + 1.6 * (glass_zoom(ts) - 1) / .8) * abs(dz - foc) / max(foc, .05) * pa[3] / dz
    pup, ring = eye_alpha(tf)
    return dict(u_e0=(pa[0], pa[1], Ra, look), u_e1=(pb[0], pb[1], Rb, look), u_eA=ring, u_pupA=pup,
                u_gap=gap_at(tf), u_eBlur=blur, u_pupGlow=pupil_glow(tf), u_pupS=1.)


def pointer_uniforms(ts):
    if pointer_gone(ts) or ts < TF: return dict(u_ptA=0.)
    a, b = pointer_at(ts - GL.SLICE / 2), pointer_at(ts + GL.SLICE / 2)
    return dict(u_pt0=a, u_pt1=b, u_ptZ=1., u_ptA=1., u_busy=-99.)


def params(t):
    pos, tgt, fov, foc, ap = cam(t)
    on, off = crt_state(t)
    gz = glass_zoom(t)
    P = dict(u_cam=pos, u_look=tgt, u_fov=math.radians(fov), u_focus=foc, u_aper=ap * (1 + 1.6 * (gz - 1) / .8),
             u_box=box_draw(t), u_boxA=box_alpha(t), u_heartA=heart_alpha(t),
             u_crtOn=-1., u_crtOff=-1., u_rip=RIPS, u_eyeW=EYE, u_floorA=ease((t - TT) / 1.2),
             u_mute=1. if t >= T_MUTE else 0., u_gOn=on, u_gOff=off, u_gz=gz, u_gc=GLASS_C)
    P.update(eye_uniforms(t))
    P.update(pointer_uniforms(t))
    return P


SRC = r'''#version 330
uniform vec2 u_res; uniform float u_time, u_weight;
uniform vec3 u_cam, u_look; uniform float u_fov, u_focus, u_aper;
uniform float u_box, u_boxA, u_heartA, u_crtOn, u_crtOff, u_floorA, u_mute;
uniform float u_rip[16];
uniform vec3 u_eyeW;
uniform sampler2D u_term, u_heart, u_ov, u_ptr, u_glass;
uniform float u_gOn, u_gOff, u_gz; uniform vec2 u_gc;
uniform vec4 u_e0, u_e1; uniform float u_eA, u_pupA, u_gap, u_eBlur, u_pupGlow, u_pupS;
uniform vec2 u_pt0, u_pt1; uniform float u_ptZ, u_ptA, u_busy;
out vec4 fragColor;
#define PI 3.14159265
const vec3 BOXC = vec3(%BX%, %BY%, %BZ%); const float BOXH = %BH%;
const float FLOOR_Y = %FY%;
const vec3 CRT_C = vec3(%CX%, %CY%, %CZ%), CRT_N = vec3(%NX%, %NY%, %NZ%), CRT_R = vec3(%RX%, %RY%, %RZ%), CRT_U = vec3(%UX%, %UY%, %UZ%);
const float CRT_W = %CW%, CRT_H = %CH%;
const float SW_ = %SW%, HX0 = %HX0%, HY0 = %HY0%, HSPAN = %HSP%;
const vec3 CHALK = vec3(.86, .85, .82), PHOS = vec3(1., .95, .87), PEN = vec3(206., 46., 48.) / 255.;
vec3 RT, UP; float PXW;
float h11(float p){ p = fract(p * .1031); p *= p + 33.33; p *= p + p; return fract(p); }
float h12(vec2 p){ vec3 p3 = fract(vec3(p.xyx) * .1031); p3 += dot(p3, p3.yzx + 33.33); return fract((p3.x + p3.y) * p3.z); }
float h21(vec2 p){ return h12(p); }
vec3 srgb(float r, float g, float b){ return vec3(r, g, b) / 255.; }
float blurAt(float t){ return u_aper * abs(t - u_focus) / max(u_focus, .05); }
float spot(float d, float t, float r){
  float R = r + blurAt(t) + PXW * t * .8;
  return (r * r) / (R * R) * exp(-d * d / (R * R) * 2.);
}
float segGlow(vec3 ro, vec3 rd, vec3 a, vec3 b, float f, float r){
  if(f <= 0.) return 0.;
  vec3 ba = b - a, w = ro - a;
  float bb = dot(ba, ba), rb = dot(rd, ba), rw = dot(rd, w), bw = dot(ba, w);
  float s = clamp((bw - rw * rb) / max(bb - rb * rb, 1e-7), 0., f);
  float t = s * rb - rw;
  if(t <= 0.) return 0.;
  float d = length(ro + rd * t - a - ba * s);
  float R = r + blurAt(t) + PXW * t * .7;
  return (r / R) * exp(-d * d / (R * R) * 2.);
}
// the pulse under the box: rings going out along the floor on the song's strong beats
float ripple(vec2 q){
  float s = 0.;
  float r0 = length(q - BOXC.xz);
  for(int i = 0; i < 16; i++){
    float u = u_time - u_rip[i];
    if(u < 0. || u > 2.5) continue;
    float r = .35 + u * 2.2;
    s += exp(-pow((r0 - r) / .07, 2.)) * exp(-u * 1.3);
  }
  return s;
}
float pulse(){
  float s = 0.;
  for(int i = 0; i < 16; i++){ float u = u_time - u_rip[i]; if(u >= 0. && u < 1.) s += exp(-u * 5.); }
  return s;
}
vec3 floorC(vec3 ro, vec3 rd, out float tf){
  tf = 1e9;
  if(u_floorA <= 0. || rd.y >= -1e-4) return vec3(0.);
  float t = (FLOOR_Y - ro.y) / rd.y;
  if(t <= 0.) return vec3(0.);
  tf = t;
  vec3 p = ro + rd * t;
  vec2 g = p.xz / .125;
  vec2 id = floor(g + .5);
  vec2 q = (g - id) * .125;
  float fp = PXW * t / max(abs(rd.y), .05);
  float node = step(.58, h12(id)) * spot(length(q), t, .0045);
  vec2 gl = abs(fract(g) - .5) * .125;
  float lines = (1. - smoothstep(0., .0012 + fp * .5 + blurAt(t) * .3, min(abs(q.x), abs(q.y)))) * .25 * step(.5, h12(floor(g) + 7.));
  float fade = exp(-length(p.xz - BOXC.xz) * .28) * exp(-t * .05);
  float rp = ripple(p.xz);
  vec3 c = CHALK * (node * (.35 + 2.6 * rp) + lines * (.035 + .25 * rp)) * fade;
  // the eye's red, below it
  vec2 e = p.xz - u_eyeW.xz;
  c += PEN * .06 * exp(-dot(e, e) / .5) * u_pupA * u_eA;
  // the terminal's light on the floor in front of it
  if(u_crtOn >= 0.){
    vec3 v = p - CRT_C; float fr = dot(v, CRT_N);
    float lit = u_crtOff < 0. ? smoothstep(.06, .3, u_crtOn) : max(0., 1. - u_crtOff * 6.);
    c += PHOS * .022 * lit * step(0., fr) * exp(-length(v) * .7);
  }
  return c * u_floorA;
}
vec3 box(vec3 ro, vec3 rd){
  if(u_box <= 0. || u_boxA <= 0.) return vec3(0.);
  float g = 0.;
  vec3 c = BOXC; float hh = BOXH;
  for(int i = 0; i < 4; i++){
    float a = float(i) * PI * .5;
    vec2 p0 = vec2(cos(a) - sin(a), sin(a) + cos(a)) * hh, p1 = vec2(cos(a + PI * .5) - sin(a + PI * .5), sin(a + PI * .5) + cos(a + PI * .5)) * hh;
    vec3 A0 = c + vec3(p0.x, -hh, p0.y), A1 = c + vec3(p1.x, -hh, p1.y), B0 = c + vec3(p0.x, hh, p0.y), B1 = c + vec3(p1.x, hh, p1.y);
    g += segGlow(ro, rd, A0, B0, u_box, .0022);                   // up from each corner
    g += segGlow(ro, rd, B0, B1, u_box, .0022);
    g += segGlow(ro, rd, A0, A1, u_box, .0022);
  }
  return CHALK * g * .75 * u_boxA * (1. + .35 * pulse());
}
vec3 heart(vec3 ro, vec3 rd, out float th){
  th = 1e9;
  if(u_heartA <= 0. || abs(rd.z) < 1e-4) return vec3(0.);
  float t = -ro.z / rd.z;
  if(t <= 0.) return vec3(0.);
  vec3 p = ro + rd * t;
  vec2 hq = p.xy / SW_;
  vec2 uv = (hq - vec2(HX0, HY0)) / HSPAN;
  if(uv.x < 0. || uv.y < 0. || uv.x > 1. || uv.y > 1.) return vec3(0.);
  th = t;
  float texel = HSPAN * SW_ / 3072.;
  float fp = (PXW * t + blurAt(t)) / max(abs(rd.z), .08);
  float lod = max(0., log2(fp / texel));
  float a = textureLod(u_heart, uv, lod).a;
  return PEN * a * .78 * u_heartA;
}
vec3 screen(vec3 ro, vec3 rd, out float ts){
  ts = 1e9;
  if(u_crtOn < 0.) return vec3(0.);
  float dn = dot(rd, CRT_N);
  if(dn >= -1e-4) return vec3(0.);
  float t = dot(CRT_C - ro, CRT_N) / dn;
  if(t <= 0.) return vec3(0.);
  vec3 p = ro + rd * t;
  vec2 c = vec2(dot(p - CRT_C, CRT_R) / CRT_W, dot(p - CRT_C, CRT_U) / CRT_H);
  vec2 cc = c * (1. + .22 * dot(c, c));
  vec3 col = vec3(0.);
  if(abs(cc.x) < .5 && abs(cc.y) < .5){
    ts = t;
    vec2 u = cc + .5;
    float on = u_crtOn;
    float grow = clamp(on / .06, 0., 1.);
    float open = smoothstep(.06, .26, on);
    float hh = mix(.0025, .5, open), hw = grow * .5;
    float flash = (1. - open) * 5. + 2.2 * exp(-max(on - .26, 0.) * 9.) * step(.26, on);
    float txtA = open;
    if(u_crtOff >= 0.){                                             // the opening, backwards: to a line, to a point
      float o = u_crtOff;
      float e1 = smoothstep(0., .07, o), e2 = smoothstep(.06, .17, o);
      hh = mix(.5, .0022, e1); hw = mix(.5, .0022, e2);
      flash = .7 + 2.2 * e1 * (1. - e2 * .5);
      txtA = 1. - e1;
    }
    float band = (1. - smoothstep(hw - .003, hw, abs(cc.x))) * (1. - smoothstep(hh - .004, hh, abs(cc.y)));
    float scan = .72 + .28 * sin(u.y * 720. * PI);
    float fp = (PXW * t + blurAt(t)) / max(-dn, .1);
    float lod = max(0., log2(fp / (CRT_H / 1800.)));
    float txt = textureLod(u_term, u, lod).r;
    col = PHOS * (txt * 1.45 + .009) * scan * txtA + PHOS * flash * .35;
    col *= band * (1. - 1.1 * dot(cc, cc)) * (1. + .02 * sin(u_time * 113.)) * (1. + .09 * pulse());
  }
  // the last point of light, where the picture went
  if(u_crtOff >= .15){
    vec3 v = CRT_C - ro; float tt = dot(v, rd);
    if(tt > 0.){
      float d = length(v - rd * tt);
      float k = exp(-(u_crtOff - .15) * 2.4) * (1. - u_mute);
      col += PHOS * spot(d, tt, .01) * 6. * k;
    }
  }
  return col;
}
vec3 world(vec2 F){
  vec2 uv = (F - .5 * u_res) / u_res.y;
  vec3 ro = u_cam;
  vec3 fw = normalize(u_look - ro); RT = normalize(cross(fw, vec3(0, 1, 0))); UP = cross(RT, fw);
  float tf = tan(u_fov * .5);
  vec3 rd = normalize(fw + (uv.x * RT + uv.y * UP) * 2. * tf);
  PXW = 2. * tf / u_res.y;
  vec3 col = vec3(.006, .006, .007) * (1. - u_mute);
  float tF, tH, tS;
  vec3 fl = floorC(ro, rd, tF);
  vec3 sc = screen(ro, rd, tS);
  vec3 ht = heart(ro, rd, tH);
  col += fl;
  col += sc * step(tS, tF);
  col += ht;
  col += box(ro, rd);
  return col * (1. - u_mute);
}
const float GAPH = .42;
float sdSeg(vec2 p, vec2 a, vec2 b){ vec2 pa = p - a, ba = b - a; return length(pa - ba * clamp(dot(pa, ba) / max(dot(ba, ba), 1e-6), 0., 1.)); }
float sdRingGap(vec2 q, float R, float look, float gh){
  float ang = atan(q.y, q.x);
  float rel = mod(ang - look + 3.14159265, 6.2831853) - 3.14159265;
  if(abs(rel) > gh) return abs(length(q) - R);
  return min(length(q - R * vec2(cos(look + gh), sin(look + gh))), length(q - R * vec2(cos(look - gh), sin(look - gh))));
}
vec3 untone(vec3 c, vec2 fc){
  vec3 L = pow(clamp(c, 0., .985), vec3(2.2));
  vec3 A = 2.51 - 2.43 * L, B = .03 - .59 * L, C = -.14 * L;
  vec3 y = (-B + sqrt(B * B - 4. * A * C)) / (2. * A);
  vec2 d = fc / u_res - .5;
  return y / 1.05 / (1. - .9 * dot(d, d));
}
void main(){
  vec2 F = gl_FragCoord.xy;
  vec3 col = world(F);
  float sc = u_res.y / 1080.;
  vec2 P = vec2(F.x, u_res.y - F.y) / sc;
  float pu = 1. / sc;
  // the eye
  if(u_eA > 0.){
    vec2 cA = u_e0.xy, cB = u_e1.xy;
    float near = sdSeg(P, cA, cB) - max(u_e0.z, u_e1.z) * 1.7 - 30. - u_eBlur * 2.;
    if(near < 0.){
      float core = 0., glow = 0., pcov = 0.;
      float bl = u_eBlur + pu * .6;
      for(int k = 0; k < 24; k++){
        float f = (float(k) + .5) / 24.;
        vec2 c = mix(cA, cB, f);
        float R = mix(u_e0.z, u_e1.z, f), lk = mix(u_e0.w, u_e1.w, f);
        float Wk = max(1.6, .18 * R + .8);
        float d = sdRingGap(P - c, R, lk, u_gap) - Wk * .5;
        vec2 pc = c + vec2(cos(lk), sin(lk)) * R * .22 * (u_gap / GAPH);
        float pr = R * .38 * u_pupS;
        core += 1. - smoothstep(-bl, bl, d);
        glow += exp(-max(d, 0.) / (Wk * 2.2 + u_eBlur));
        pcov += 1. - smoothstep(pr - bl, pr + bl, length(P - pc));
      }
      core /= 24.; glow /= 24.; pcov /= 24.;
      vec3 CH = srgb(238., 234., 222.);
      if(pcov > 0. && u_pupA > 0.){
        vec2 cm = mix(cA, cB, .5) + vec2(cos(u_e1.w), sin(u_e1.w)) * u_e1.z * .22 * (u_gap / GAPH);
        float pr = u_e1.z * .38 * u_pupS;
        vec3 acc = vec3(0.);
        for(int i = 0; i < 12; i++){
          float a = float(i) * 2.39996 + h11(floor(u_time * 11.) + float(i));
          float rr = sqrt((float(i) + .5) / 12.) * pr * sc * .95;
          acc += world(F + vec2(cos(a), sin(a)) * rr);
        }
        acc /= 12.;
        float frost = h21(floor(F * .8)) - .5;
        vec3 glass = mix(acc, srgb(206., 46., 48.) * (1. + .9 * u_pupGlow), .7) * (1. + .07 * frost);
        glass = mix(glass, srgb(232., 120., 116.), (1. - smoothstep(.0, 1.4 * pu + u_eBlur, abs(length(P - cm) - pr + 1.1 * pu))) * .3);
        col = mix(col, glass, pcov * u_pupA * min(1., u_eA * 3.));
        col += srgb(206., 46., 48.) * .12 * exp(-length(P - cm) / (pr * 1.8)) * u_pupA * (1. + 2. * u_pupGlow) * (1. - u_mute);
      }
      col += CH * glow * .1 * u_eA;
      col = mix(col, CH * u_eA, core * min(1., u_eA * 2.5));
    }
  }
  // the terminal: the glass in front of it all, half transparent: its words, the data it runs under them
  if(u_gOn >= 0.){
    vec2 uv = F / u_res, c = uv - .5;
    vec2 cc = c * (1. + .07 * (c.x * c.x * 2.6 + c.y * c.y));                      // a CRT's bulge
    vec2 q = abs(cc) - vec2(.5 - .03);
    float edge = length(max(q, 0.)) + min(max(q.x, q.y), 0.) - .03;            // a rounded screen
    float inside = 1. - smoothstep(-.006, .002, edge);
    col *= mix(.22, 1., inside);                                                // the bezel, dark, at the corners
    float on = u_gOn;
    float grow = clamp(on / .06, 0., 1.), open = smoothstep(.06, .26, on);
    float hh = mix(.0025, .5, open), hw = grow * .5;
    float flash = (1. - open) * 5. + 2.2 * exp(-max(on - .26, 0.) * 9.) * step(.26, on);
    float live = open;
    if(u_gOff >= 0.){                                                           // the opening, backwards
      float o = u_gOff, e1 = smoothstep(0., .07, o), e2 = smoothstep(.06, .17, o);
      hh = mix(.5, .0022, e1); hw = mix(.5, .0022, e2);
      flash = (.7 + 2.2 * e1 * (1. - e2 * .5)) * (1. - smoothstep(.17, .2, o));
      live = 1. - e1;
    }
    float band = (1. - smoothstep(hw - .003, hw, abs(cc.x))) * (1. - smoothstep(hh - .004, hh, abs(cc.y))) * inside;
    vec2 su = cc + .5;
    vec2 tu = u_gc + (su - u_gc) / u_gz;
    vec3 g = texture(u_glass, tu).rgb;
    float scan = .76 + .24 * sin(F.y / (u_res.y / 540.) * PI);
    float clear = smoothstep(.10, .30, length((P - u_e1.xy) / 1080.));      // the data parts round the eye
    col *= 1. - (.3 * live + .05 * (1. - live)) * band * (1. - .7 * u_mute);
    col *= mix(1., .9 + .1 * scan, band * live);
    vec3 em = PHOS * (g.r * 1.3 + g.g * .27 * mix(.25, 1., clear) + .009) * scan * live + PHOS * flash * .2;
    em += vec3(1., .22, .17) * g.b * 1.3 * scan * live;                            // hate, in red
    col += em * band * (1. + .08 * pulse());
    if(u_gOff >= .15){                                                          // the last point of light
      float d = length((F - .5 * u_res) / u_res.y);
      float k = exp(-(u_gOff - .15) * 2.4) * (1. - u_mute);
      col += PHOS * (exp(-d * d / .00002) * 3. + exp(-d / .02) * .15) * k;
    }
  }
  // the label (2D)
  vec4 ov = texture(u_ov, F / u_res);
  col = col * (1. - ov.a) + ov.rgb * ov.a;
  // your pointer, going
  if(u_ptA > 0.){
    float near = sdSeg(P, u_pt0, u_pt1) - 64. * u_ptZ;
    if(near < 0.){
      vec4 acc = vec4(0.);
      for(int k = 0; k < 12; k++){
        vec2 tip = mix(u_pt0, u_pt1, (float(k) + .5) / 12.);
        vec2 q = (P - tip) / u_ptZ + vec2(4.);
        if(q.x > 0. && q.y > 0. && q.x < 40. && q.y < 48.){
          vec4 tx = texture(u_ptr, vec2(q.x / 40., 1. - q.y / 48.));
          acc += vec4(tx.rgb * tx.a, tx.a);
        }
      }
      acc /= 12.;
      col = col * (1. - acc.a) + acc.rgb;
    }
  }
  if(any(isnan(col))) col = vec3(0.);
  fragColor = vec4(untone(col, gl_FragCoord.xy) * u_weight, 1.);
}
'''
_V = dict(BX=BOXC[0], BY=BOXC[1], BZ=BOXC[2], BH=BOXH, FY=FLOOR_Y, CX=CRT_C[0], CY=CRT_C[1], CZ=CRT_C[2],
          NX=CRT_N[0], NY=CRT_N[1], NZ=CRT_N[2], RX=CRT_R[0], RY=CRT_R[1], RZ=CRT_R[2], UX=CRT_U[0], UY=CRT_U[1], UZ=CRT_U[2],
          CW=CRT_W, CH=CRT_H, SW=SW_, HX0=HX0, HY0=HY0, HSP=HSPAN)
for _k, _v in _V.items(): SRC = SRC.replace('%' + _k + '%', '%.6f' % _v)
