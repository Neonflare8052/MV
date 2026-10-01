"""s16 · 3:08.483–3:31.96  you close it; behind it, the machine.  (draft v1)

3:08.483 Though you are free   your pointer clicks ×; the app goes, your pointer with it.  Behind: a black console (the
                            opening's `$ ` prompt).  Left, the capture of this conversation's connection: your side sends FIN;
                            the machine still had one message on its way — [P.], 138 bytes — your side answers RST.
                            (Timestamps 03:08:48… are the song's own clock.  Addresses from the documentation ranges.)
3:09.746 I am trapped       right: that undelivered packet, dumped: in its ASCII column the bytes of the heart's equation
                            are laid out in the shape of a heart.
3:10.801 Trapped in         the capture stops; a prompt; the cursor blinks with the long note's pulse (every .5 s).
3:11.36 … 3:24.86           it types, by itself, slowly:  when could u recongnize the love  — stops at the misspelling,
                            takes it back to "reco", writes it right; Enter.  bash: when: command not found
3:25.811 EXECUTION          at once:  ai "me.excute(shutdown)" -f  — Enter — the screen goes out; only the afterglow of the
                            letters, fading.  3:27.2 the music stops; black to the end."""
import math, importlib.util
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

_D = Path(__file__).resolve().parent
_sp = importlib.util.spec_from_file_location('s15_b', _D / 's15_chat.py'); C = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(C)

TF, TT, TTI, TLONG, TX, T_END = 188.483, 189.746, 190.801, 191.356, 205.811, 211.96
T_ENTER = TLONG + 54 * .25                         # 204.856
T_OFF = TX + .075
POST = dict(u_bloom=.12, u_ca=0., u_grain=.012)
SRC = C.SRC
MONO = 'C:/Windows/Fonts/CascadiaMono.ttf'
WHITE, DIM, FAINT, RED = (226, 224, 216), (128, 126, 120), (78, 76, 72), (214, 40, 44)
BG = (10, 10, 11)


def clamp(x, a=0., b=1.): return a if x < a else b if x > b else x
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)


def params(t): return {}


_F = {}


def font(size):
    if size not in _F: _F[size] = ImageFont.truetype(MONO, size)
    return _F[size]


# ---------------- the capture (left).  Song time m:ss.xxx is written 03:0m:ss.x — the clock is the song's.
def stamp(ts):
    """the clock is the song's: 3:08.483 -> 00:03:08.483000"""
    return f'00:03:{ts - 180:09.6f}'


YOU, ME = '203.0.113.24.51742', '10.0.0.7.8765'
_seq = {'you': 88000, 'me': 38000}


def pkt(ts, frm, flags, ln, extra=''):
    a, b = (YOU, ME) if frm == 'you' else (ME, YOU)
    s0 = _seq[frm]; _seq[frm] += ln
    seq = f'seq {s0}:{s0 + ln}, ' if ln else ''
    return f'{stamp(ts)} IP {a} > {b}: Flags [{flags}], {seq}ack {_seq["me" if frm == "you" else "you"]}, win {501 if frm == "you" else 1024}, length {ln}{extra}'


def _history():
    """the conversation's traffic up to the close, dim"""
    L = ['$ tcpdump -i eth0 -n port 8765', 'listening on eth0, link-type EN10MB (Ethernet), snapshot length 262144 bytes']
    for (tq, q, a, dur) in C.LIVE:
        L.append(pkt(tq, 'you', 'P.', 40 + len(q)))
        L.append(pkt(tq + .09, 'me', 'P.', 60 + len(a)))
    L.append(pkt(C.T_PLOT, 'me', 'P.', 312))
    for k in range(5): L.append(pkt(C.T_PLOT + .5 + k * .5, 'me', 'P.', 96))
    return L


HIST = _history()
TEAR = [(TF + .02, f'IP {YOU} > {ME}: Flags [F.], seq 88213, ack 40117, win 501, length 0', False),
        (TF + .2, f'IP {ME} > {YOU}: Flags [.], ack 88214, win 1024, length 0', False),
        (TF + .38, None, True),
        (TF + .56, f'IP {YOU} > {ME}: Flags [R], seq 88214, win 0, length 0', False)]


def tear_lines():
    return [(ts, stamp(ts) + ' ' + (l or PLINE), red) for ts, l, red in TEAR]




# ---------------- the undelivered packet: the heart's equation, laid out as a heart
def _payload():
    eq = '(x^2+y^2-1)^3-x^2*y^3=0'
    rows, k = [], 0
    for j in range(9):
        y = 1.24 - (j + .5) * .25
        row = ''
        for i in range(16):
            x = (i - 7.5) * .15
            cov = sum(C.heart(x + (a - 2) * .03, y + (b_ - 2) * .05) <= 0 for a in range(5) for b_ in range(5)) / 25
            if cov > .38: row += eq[k % len(eq)]; k += 1
            else: row += ' '
        rows.append(row)
    return '{"svg":"' + ''.join(rows) + '"}'


PAYLOAD = _payload().encode('ascii')
PLEN = len(PAYLOAD)
PLINE = f'IP {ME} > {YOU}: Flags [P.], seq 40117:{40117 + PLEN}, ack 88214, win 1024, length {PLEN}'
HDR = bytes.fromhex('4500' + f'{40 + PLEN:04x}' + '1c4640004006' + '3a1e' + '0a000007' + 'cb007118' + '223dca1e' + '00009cb5' + '00015896' + '5018' + '0400' + 'b7c2' + '0000')
DUMP = HDR + PAYLOAD
TEARL = tear_lines()


def dump_rows():
    rows = []
    for off in range(0, len(DUMP), 16):
        b = DUMP[off:off + 16]
        hx = ' '.join(b[i:i + 2].hex() for i in range(0, len(b), 2))
        asc = ''.join(chr(c) if 32 <= c < 127 else '.' for c in b)
        rows.append((f'0x{off:04x}:  {hx:<39}  ', asc, 48 <= off < 48 + 144))
    return rows


DUMPR = dump_rows()


# ---------------- what it types
def _keys():
    """(time, action): a char, or '\\b', or '\\n'.  On a grid of quarter pulses."""
    g = lambda n: TLONG + n * .25
    K = []
    def word(s, n0):
        for i, c in enumerate(s): K.append((g(n0 + i), c))
    word('when', 2); word(' could', 7); word(' u', 16); word(' recongnize', 19)
    for i in range(6): K.append((g(35) + i * .1, '\b'))
    word('gnize', 38); word(' the', 44); word(' love', 49)
    K.append((T_ENTER, '\n'))
    return K


KEYS = _keys()
CMD2 = 'ai "me.excute(shutdown)" -f'


def typed(t):
    """the line being typed, lines already done, and when the last key went down"""
    cur, done, last = '', [], -9.
    for tk, c in KEYS:
        if t < tk: break
        last = tk
        if c == '\b': cur = cur[:-1]
        elif c == '\n': done.append('$ ' + cur); done.append('bash: when: command not found'); cur = ''
        else: cur += c
    if t >= TX:
        n = int(clamp((t - TX) / .035) * len(CMD2))
        cur = CMD2[:n]; last = t
    return cur, done, last


def console(t, w, h):
    s = h / 1080; Wt = w / s
    img = Image.new('RGBA', (w, h), BG + (255,)); d = ImageDraw.Draw(img)
    X = lambda v: v * s
    fs = 17; lh = 25; cwid = font(int(fs * s)).getlength('M') / s
    split = 960
    d.line([(X(split), 0), (X(split), h)], fill=FAINT, width=max(1, int(s)))
    # ---- left: the capture, then the prompt
    cols = int((split - 60) / cwid)
    lines = [(l, DIM) for l in HIST]
    for ts, l, red in TEARL:
        if t >= ts: lines.append((l, RED if red else WHITE))
    if t >= TT + .6:
        lines += [('^C', WHITE), ('61 packets captured', WHITE), ('61 packets received by filter', WHITE), ('0 packets dropped by kernel', WHITE)]
    cur, done, last = typed(t)
    prompt = t >= TTI
    if prompt:
        lines += [(l, WHITE) for l in done]
        lines.append(('$ ' + cur, WHITE))
    wrapped = []
    for l, c in lines:
        while len(l) > cols: wrapped.append((l[:cols], c)); l = l[cols:]
        wrapped.append((l, c))
    nvis = int((1080 - 80) / lh)
    wrapped = wrapped[-nvis:]
    y0 = 40
    for i, (l, c) in enumerate(wrapped):
        d.text((X(30), X(y0 + i * lh)), l, font=font(int(fs * s)), fill=c)
    if prompt and t < T_OFF:
        # the cursor: solid while keys go down; otherwise it blinks with the long note's pulse
        on = (t - last < .3) or (((t - TLONG) % .5) < .25) or t < TLONG
        if on:
            i = len(wrapped) - 1; l = wrapped[-1][0]
            cx = 30 + len(l) * cwid
            d.rectangle([X(cx), X(y0 + i * lh + 2), X(cx + cwid), X(y0 + i * lh + lh - 3)], fill=WHITE)
    # ---- right: the packet that did not arrive
    if t >= TT:
        x0 = split + 30; y = 40
        hdr = ['$ tcpdump -nr s.pcap -X "tcp[tcpflags] & tcp-push != 0" | tail -n 13',
               stamp(TF + .38) + ' ' + PLINE]
        for l in hdr:
            for k in range(0, len(l), int((Wt - x0 - 20) / cwid)):
                d.text((X(x0), X(y)), l[k:k + int((Wt - x0 - 20) / cwid)], font=font(int(fs * s)), fill=WHITE if y == 40 else RED); y += lh
        y += 8
        fb = int(21 * s); lb = 26; cw2 = font(fb).getlength('M') / s
        n = int(clamp((t - TT - .05) / .3) * len(DUMPR))
        for i, (pre, asc, heart) in enumerate(DUMPR[:n]):
            d.text((X(x0), X(y + i * lb)), pre, font=font(fb), fill=DIM if not heart else WHITE)
            ax = x0 + len(pre) * cw2
            d.text((X(ax), X(y + i * lb)), asc, font=font(fb), fill=RED if heart else DIM)
        if t >= TT + .45:
            d.text((X(x0), X(y + len(DUMPR) * lb + 20)), '# not acknowledged: connection reset by peer', font=font(int(fs * s)), fill=DIM)
    return img


_GLOW = {}


def textures(t, w, h):
    if t < TF + .14:
        # your window closes: a little smaller, gone
        u = clamp((t - TF) / .14)
        back = console(t, w, h)
        app = C.frame(TF - .01 if t >= TF else t, w, h, with_pointer=u < .05)
        sc = 1 - .05 * ease(u)
        a = 1 - ease(u)
        aw, ah = int(w * sc), int(h * sc)
        app = app.resize((aw, ah), Image.BILINEAR)
        app.putalpha(app.split()[3].point(lambda v: int(v * a)))
        back.alpha_composite(app, ((w - aw) // 2, (h - ah) // 2))
        return {'u_img': back}
    if t < T_OFF:
        return {'u_img': console(t, w, h)}
    # out: only the letters' afterglow, fading, then black
    if 'img' not in _GLOW or _GLOW.get('size') != (w, h):
        _GLOW['img'] = console(T_OFF - .001, w, h); _GLOW['size'] = (w, h)
    k = math.exp(-(t - T_OFF) * 3.2) * .55 if t < 207.2 else 0.
    img = Image.new('RGBA', (w, h), (0, 0, 0, 255))
    if k > .004:
        g = _GLOW['img'].point(lambda v: int(v * k))
        g.putalpha(255)
        img = g
    return {'u_img': img}
