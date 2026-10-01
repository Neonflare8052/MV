"""The star-chart of rings (s09, 1:43.489–1:52.22): classical celestial-atlas structure, drawn flat — rings, ticks,
glyphs, Latin legends; no gears, no metal, no figures.

1:43.489 If I can            the flat line from s08 stands up into rings (ellipses opening from a line).
1:44.197 feel your           the two bodies spiral in at the centre, leaving a precessing rosette; every ring, the lattice and
                             the stars breathe with the wave (plus polarisation), faster and harder; the instrument strip
                             (ME / YOU, a few ms apart), the time–frequency chirp, the readouts.
1:46.293 VIBRATIONS          merger: a flash; the rings are knocked off centre; ringdown.
1:47.22 … 1:50.221 COMPLETION   the ringdown becomes a heartbeat; on each beat the rings pulse and one more comes back to
                             round and concentric, from the outside in; the gap of the centre ring closes.
1:50.900 Though you have left   the heartbeat goes flat; every ring cracks open at the bottom."""
import math, random
from PIL import Image, ImageDraw, ImageFont

F = 'C:/Windows/Fonts/'
WARM, GOLD, GREEN, DIM = (246, 232, 212), (206, 168, 104), (140, 255, 200), (120, 112, 100)
T0, T_FEEL, T_VIB, T_THEN, T_FIN, T_COMP, T_LEFT, T_OUT = 103.489, 104.197, 106.293, 107.220, 107.903, 110.221, 110.900, 112.220
BEATS = [107.14 + i * .927 for i in range(5)]                 # the heartbeat: every other beat of the song
SC = 1.18                                                     # the design (mock) in px at 1080 -> the film
LW, FS = 1.7, 1.4                                             # line and type scale (after the second mock)
GLYPH = ['☉', '☽', '☿', '♀', '♂', '♃', '♄']
LATIN = ['Sol', 'Luna', 'Mercurius', 'Venus', 'Mars', 'Iuppiter', 'Saturnus']
ROMAN = ['XII', 'I', 'II', 'III', 'IIII', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI']
_F = {}


def clamp(x, a=0., b=1.): return a if x < a else b if x > b else x
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def outc(x): x = clamp(x); return 1 - (1 - x) ** 3


# ---------------- the wave
def tau(t): return max(T_VIB - t, 0.)


def gw_phase(t):
    """phase of the strain (rad): frequency climbs as (tau)^-1/2 into the merger, then rings down at a fixed pitch"""
    if t <= T_VIB: return 2 * math.pi * -5. * math.sqrt(tau(t) + .03)
    return 2 * math.pi * (-5. * math.sqrt(.03) + 11. * (t - T_VIB))


def gw_amp(t):
    if t < T_FEEL - .4: return 0.
    a = (.012 + .12 / (1 + 2.2 * tau(t)) ** 1.6) * ease((t - T_FEEL + .4) / .6)
    if t > T_VIB: a = .13 * math.exp(-(t - T_VIB) / .32)
    return a


def gw_freq(t):
    if t <= T_VIB: return 2.5 / math.sqrt(tau(t) + .03)
    return 11.


# ---------------- the drawing
class Canvas:
    def __init__(s, w, h):
        s.w, s.h = w, h
        s.k = 2 * h / 1080                                    # 1080 units -> supersampled px
        s.img = Image.new('RGBA', (int(w * 2), int(h * 2)), (0, 0, 0, 0)); s.d = ImageDraw.Draw(s.img)
        s.Wt = w * 1080 / h
        s.cx, s.cy = s.Wt / 2, 540.

    def font(s, n, sz):
        key = (n, int(sz * s.k))
        if key not in _F: _F[key] = ImageFont.truetype(F + n, max(1, int(sz * s.k)))
        return _F[key]

    def line(s, pts, col, a=255, w=1.):
        k = s.k
        s.d.line([(x * k, y * k) for x, y in pts], fill=col + (int(clamp(a * 1.25, 0, 255)),), width=max(1, int(w * LW * k / 2 * 1.2)))

    def dot(s, x, y, r, col, a=255):
        k = s.k
        s.d.ellipse([(x - r) * k, (y - r) * k, (x + r) * k, (y + r) * k], fill=col + (int(clamp(a, 0, 255)),))

    def text(s, x, y, t, fn, sz, col, a=255, anchor='mm', angle=0.):
        f = s.font(fn, sz * FS); k = s.k
        if not angle: s.d.text((x * k, y * k), t, font=f, fill=col + (int(a),), anchor=anchor); return
        bb = s.d.textbbox((0, 0), t, font=f, anchor='mm')
        lay = Image.new('RGBA', (int(bb[2] - bb[0]) + 16, int(bb[3] - bb[1]) + 16), (0, 0, 0, 0))
        ImageDraw.Draw(lay).text((lay.width / 2, lay.height / 2), t, font=f, fill=col + (int(a),), anchor='mm')
        lay = lay.rotate(angle, resample=Image.BICUBIC, expand=True)
        s.img.alpha_composite(lay, (int(x * k - lay.width / 2), int(y * k - lay.height / 2)))

    def result(s):
        return s.img.resize((s.w, s.h), Image.LANCZOS)


class Ring:
    """one ring's state at a moment: deformation, offset, rotation, gap, standing (0 flat .. 1 round)"""
    def __init__(s, st, R):
        s.st, s.R = st, R

    def rxy(s):
        st = s.st
        h = st['amp'] * math.cos(st['phase'] - s.R / 36.)                    # the wave goes outward
        pulse = 1 + st['pulse'] * .025
        return s.R * SC * (1 + h) * pulse, s.R * SC * (1 - h) * pulse * st['stand']

    def centre(s):
        o = s.st['off'].get(s.R, (0., 0.))
        return s.st['c'][0] + o[0], s.st['c'][1] + o[1]

    def at(s, R, ang):
        """a point on the (deformed) circle of radius R (design units) at angle ang (deg, 0 = top, clockwise)"""
        h = s.st['amp'] * math.cos(s.st['phase'] - s.R / 36.)
        pulse = 1 + s.st['pulse'] * .025
        cx, cy = s.centre(); t = math.radians(ang - 90)
        return cx + R * SC * (1 + h) * pulse * math.cos(t), cy + R * SC * (1 - h) * pulse * s.st['stand'] * math.sin(t)


def ell(c, ring, R, col, a, w=1., dots=0, gap=0., n=None):
    """the circle R of this ring's group; gap: half-angle (deg) left open at the bottom"""
    n = n or max(40, int(R * 1.3))
    pts = []
    for i in range(n + 1):
        ang = 180 + gap + (360 - 2 * gap) * i / n
        pts.append(ring.at(R, ang))
    if dots:
        for p in pts[::dots]: c.dot(*p, 1.3, col, a * 1.3)
    else: c.line(pts, col, a, w)


def draw(t, w, h):
    c = Canvas(w, h)
    stand = ease((t - T0) / .7) * .98 + .02
    amp = gw_amp(t); ph = gw_phase(t)
    # the rings after the merger: knocked off centre, then back to round and concentric one by one (outside in) on the beats
    radii = [447, 412, 355, 284, 225, 161]
    off = {}
    for i, R in enumerate(radii):
        if t > T_VIB:
            r = random.Random(R)
            home = BEATS[min(i, len(BEATS) - 1)] if i < 5 else T_COMP
            k = math.exp(-(t - T_VIB) / .5) * .4 + .6 * (1 - ease((t - home + .25) / .35))
            k *= clamp((t - T_VIB) / .05)
            off[R] = (r.uniform(-26, 26) * k, r.uniform(-20, 20) * k)
    pulse = sum(math.exp(-(t - b) / .12) for b in BEATS if t >= b) + (math.exp(-(t - T_COMP) / .2) * 2 if t >= T_COMP else 0)
    if t >= T_LEFT: amp = 0.
    st = dict(amp=amp, phase=ph, stand=stand, off=off, c=(c.cx, c.cy), pulse=pulse)
    cracked = ease((t - T_LEFT - .1) / .3) * 16 if t >= T_LEFT else 0.       # every ring opens at the bottom
    fade = 1 - .45 * ease((t - T_LEFT) / .6)
    gapped = lambda a: cracked > 0 and abs(((a % 360) + 360) % 360 - 180) < cracked

    def deform_pt(x, y):
        dx, dy = x - c.cx, y - c.cy
        R = math.hypot(dx, dy) / SC + 1e-6
        hh = amp * math.cos(ph - R / 36.)
        return c.cx + dx * (1 + hh), c.cy + dy * (1 - hh) * (.2 + .8 * stand)

    # ---- the ground: stars, the lattice (they breathe too)
    r = random.Random(3)
    for i in range(700):
        x, y = r.uniform(0, c.Wt), r.uniform(0, 1080)
        c.dot(*deform_pt(x, y), r.choice([.5, .6, .8, 1.1]), WARM, r.randint(30, 110) * fade)
    for gx in range(-22, 23):
        for gy in range(-12, 13):
            c.dot(*deform_pt(c.cx + gx * 48, c.cy + gy * 48), .9, WARM, 38 * fade)
    # frame
    W_ = c.Wt
    c.line([(40, 40), (W_ - 40, 40), (W_ - 40, 1040), (40, 1040), (40, 40)], DIM, 70, 1)
    for x, y in ((40, 40), (W_ - 40, 40), (40, 1040), (W_ - 40, 1040)):
        c.line([(x - 14, y), (x + 14, y)], WARM, 140); c.line([(x, y - 14), (x, y + 14)], WARM, 140)

    G = {R: Ring(st, R) for R in radii + [110]}
    # particle rings beyond the chart: moiré while the wave passes
    pr = Ring(st, 470)
    for k in range(34):
        R = 470 + k * 13
        pr.R = R
        ell(c, pr, R, WARM, (40 + 30 * min(1., amp * 8)) * fade, dots=4, n=int(R * 1.2))
    rot = (t - T0) * 6.
    # 1 · the degree ring
    g = G[161]
    ell(c, g, 150, GOLD, 120 * fade, gap=cracked); ell(c, g, 172, GOLD, 120 * fade, gap=cracked)
    for i in range(0, 360, 1 if stand > .5 else 5):
        a = i - rot * .5
        if gapped(a): continue
        L = 18 if i % 30 == 0 else (11 if i % 5 == 0 else 6)
        c.line([g.at(150, a), g.at(150 + L, a)], GOLD, (150 if i % 5 == 0 else 80) * fade, .8)
    # 2 · the planets
    g = G[225]
    ell(c, g, 205, WARM, 90 * fade, gap=cracked); ell(c, g, 245, WARM, 90 * fade, gap=cracked)
    for i, gl in enumerate(GLYPH):
        a = rot * 1.3 + i * 360 / 7
        if gapped(a): continue
        x, y = g.at(225, a)
        if stand > .3:
            cc = Ring(st, 225); cc.st = dict(st, off={}, c=(x, y), amp=0, stand=1)
            ell(c, cc, 19 / SC, WARM, 110 * fade * stand)
            c.text(x, y, gl, 'seguisym.ttf', 17, WARM, 230 * fade * stand)
    # 3 · the hours
    g = G[284]
    ell(c, g, 268, GOLD, 90 * fade, gap=cracked); ell(c, g, 300, GOLD, 90 * fade, gap=cracked)
    for i in range(24):
        a = -rot * .8 + i * 15
        if gapped(a) or gapped(a + 7.5): continue
        if stand > .3: c.text(*g.at(284, a), ROMAN[i % 12], 'GARA.TTF', 12, WARM, 190 * fade * stand, angle=-a)
        c.line([g.at(268, a + 7.5), g.at(300, a + 7.5)], GOLD, 70 * fade, .6)
    # 4 · the eccentric curves (fade while the wave is strong: they would only tangle)
    ea = (1 - clamp(amp * 9)) * (1 - ease((t - T_THEN) / .6)) * fade
    if ea > .02:
        for k, o in enumerate([-60, -36, -18, 0, 18]):
            q = Ring(st, 120 + k * 34); q.st = dict(st, c=(c.cx, c.cy + o * SC * stand))
            ell(c, q, 120 + k * 34, GOLD, 45 * ea, .7)
        q = Ring(st, 236); q.st = dict(st, c=(c.cx, c.cy - 44 * SC * stand)); ell(c, q, 236, GOLD, 90 * ea, .9)
    # 5 · the band of twelve
    g = G[355]
    ell(c, g, 330, WARM, 80 * fade, gap=cracked); ell(c, g, 380, WARM, 80 * fade, gap=cracked)
    ba = 1 - clamp(amp * 7)                                                      # its dividers go quiet in the strong wave
    for s_ in range(12):
        a0 = rot * .6 + s_ * 30
        if not gapped(a0): c.line([g.at(330, a0), g.at(380, a0)], WARM, 120 * fade * ba, .8)
        for j in range(1, 9):
            fa = a0 + j * 30 / 9
            if gapped(fa): continue
            ty = (j + s_) % 3
            if ty == 0: c.line([g.at(334, fa), g.at(376, fa)], GOLD, 60 * fade, .5)
            elif ty == 1: c.dot(*g.at(355, fa), 1.2, GOLD, 120 * fade)
            else: c.line([g.at(340, fa), g.at(352, fa)], GOLD, 70 * fade, .5); c.line([g.at(358, fa), g.at(370, fa)], GOLD, 70 * fade, .5)
    # 6 · the outer
    g = G[412]; ell(c, g, 412, WARM, 120 * fade, dots=3, gap=cracked)
    g = G[447]; ell(c, g, 440, WARM, 110 * fade, gap=cracked); ell(c, g, 447, WARM, 70 * fade, .6, gap=cracked)
    for i in range(0, 360, 6):
        a = i - rot * .3
        if gapped(a): continue
        c.line([g.at(447, a), g.at(447 + (14 if i % 30 == 0 else 6), a)], WARM, 110 * fade, .7)

    # ---- the centre: the two, before; the ring, after
    g = G[110]
    if t < T_VIB:
        sep = 70 * SC * (tau(t) / (T_VIB - T_FEEL)) ** .5 * stand
        oa = ph / 2
        # the rosette they have drawn
        n = int(clamp((t - T_FEEL + .3) / 2.4) * 900)
        for k in range(0, n, 2):
            u = k / 900
            tt = T_FEEL + u * (t - T_FEEL)
            sp = 70 * SC * (tau(tt) / (T_VIB - T_FEEL)) ** .5
            th = gw_phase(tt) / 2
            pr_ = th * .93
            x = c.cx + sp * math.cos(th) * (1 + .3 * math.cos(pr_)); y = c.cy + sp * math.sin(th) * (1 + .3 * math.cos(pr_)) * .8
            c.dot(x, y, .8, GOLD, 70 * u)
        mx, my = c.cx + sep * .4 * math.cos(oa), c.cy + sep * .4 * math.sin(oa) * .8
        yx, yy = c.cx - sep * .6 * math.cos(oa), c.cy - sep * .6 * math.sin(oa) * .8
        c.dot(yx, yy, 6, WARM, 255 * stand)
        pts = [(mx + 14 * math.cos(math.radians(a)), my + 14 * math.sin(math.radians(a))) for a in range(90 + 40, 90 + 360 - 40, 6)]
        c.line(pts, WARM, 255 * stand, 2.4)
    else:
        # the flash, a shell going out
        fl = t - T_VIB
        if fl < .5: ell(c, Ring(dict(st, amp=0, off={}), 0), 110 + fl * 900, WARM, 255 * (1 - fl / .5), 2.2)
        gap = 27 * (1 - ease((t - T_FIN) / (T_COMP - T_FIN)))
        if t >= T_LEFT: gap = 27 * ease((t - T_LEFT - .1) / .3)
        ga = ease((t - T_VIB) / .25)
        ell(c, g, 110, WARM, 255 * ga, 4.5 / LW * 1.6, gap=gap, n=260)
        ell(c, g, 110, WARM, 60 * ga, 11 / LW, gap=gap, n=260)                 # a soft halo line under it
        # inside: ringdown, then the heartbeat, swept in like a monitor; flat after you have left
        pts = []
        R = 110 * SC * .86
        for i in range(161):
            x = -1 + i / 80
            if t < BEATS[0]:
                y = .5 * math.exp(-(t - T_VIB) * 2.5) * math.exp(-abs(x) * 1.5) * math.sin(x * 18 - (t - T_VIB) * 30)
            else:
                e = .55 * math.exp(-((x - .02) / .03) ** 2) - .18 * math.exp(-((x + .05) / .03) ** 2) - .22 * math.exp(-((x - .15) / .04) ** 2) + .1 * math.exp(-((x + .3) / .07) ** 2)
                y = e * (1 - ease((t - T_LEFT) / .15))
            pts.append((c.cx + x * R, c.cy - y * R * .9))
        last = max([b for b in BEATS if b <= t], default=None)
        sweep = 1. if last is None else clamp((t - last) / .35)
        n = max(2, int(len(pts) * (sweep if t >= BEATS[0] else 1)))
        c.line(pts[:n], GREEN, 240 * ga, 2)

    # ---- the instrument: strip, spectrogram, readouts, keys
    ia = ease((t - T_FEEL) / .4) * fade
    if ia > 0:
        y0 = 965
        c.line([(120, y0 - 70), (W_ - 120, y0 - 70)], DIM, 80 * ia, .6)
        span = 3.4
        for j, (col, dl, lab) in enumerate(((WARM, 0., 'ME'), (GREEN, .007, 'YOU'))):
            pts = []
            for i in range(700):
                u = i / 699
                tt = t - span + u * span
                x = 180 + u * (W_ - 560)
                if tt < T_FEEL - .3: v = 0.
                elif tt <= T_VIB + .8 and tt < BEATS[0]: v = gw_amp(tt) / .13 * math.sin(gw_phase(tt - dl * (1 - ease((tt - T_VIB + .6) / .6))))
                else:
                    x_ = ((tt - BEATS[0]) % .927) / .927 - .3
                    v = (.55 * math.exp(-((x_ - .02) / .02) ** 2) - .2 * math.exp(-((x_ + .04) / .02) ** 2) - .25 * math.exp(-((x_ - .09) / .025) ** 2) + .12 * math.exp(-((x_ - .3) / .06) ** 2)) * 1.6
                    if tt >= T_LEFT: v = 0.
                yo = (-7 if j == 0 else 7) * (1 - ease((tt - T_VIB + .3) / .3))    # two lines become one at the merger
                pts.append((x, y0 - 30 + yo - 24 * v))
            c.line(pts, col, 220 * ia * (1 if j == 0 or t < T_THEN + .5 else 1 - ease((t - T_THEN - .5) / .3)), 1.3)
            lab_ = lab if t < T_THEN else ('II' if j == 0 else '')
            if lab_: c.text(150, y0 - 30 + (-7 if j == 0 else 7), lab_, 'CascadiaMono.ttf', 11, col, 200 * ia, anchor='rm')
        # the time-frequency chirp
        sx0, sx1, sy0, sy1 = W_ - 330, W_ - 120, 862, 1010
        sa = ia * (1 - ease((t - T_THEN) / .5))
        if sa > 0:
            c.line([(sx0, sy1), (sx1, sy1)], DIM, 120 * sa, .6); c.line([(sx0, sy0), (sx0, sy1)], DIM, 120 * sa, .6)
            for i in range(40):
                tt = T_FEEL - .2 + i / 39 * (T_VIB + .3 - T_FEEL + .2)
                for j in range(18):
                    fy = 1 - j / 18
                    curve = clamp(gw_freq(tt) / 16.) if tt <= T_VIB else .7
                    v = math.exp(-((fy - curve) / .07) ** 2) * (tt <= t) * (gw_amp(tt) / .13 + .15)
                    c.dot(sx0 + 5 + i * 5, sy0 + 5 + j * 7.8, 1.7, GREEN, (25 + 220 * clamp(v)) * sa)
            c.text(sx0, sy0 - 16, 'f  [Hz]', 'CascadiaMono.ttf', 10, GREEN, 170 * sa, anchor='lm')
        # readouts
        if t < T_THEN:
            f_hz = 30 + 220 * clamp(gw_freq(t) / 16.) if t < T_VIB else 250
            rows = [('f_GW', f'{f_hz:5.0f} Hz'), ('h(t)', f'{max(gw_amp(t), .002) * 8e-21:.1e}'), ('sep', f'{max(10, 2000 * (tau(t) / 2.1) ** .6):5.0f} km'), ('pol', '+')]
        else:
            rows = [('HR', ' 65 bpm' if t < T_LEFT else '  0 bpm'), ('RR', '0.927 s' if t < T_LEFT else '    — s'), ('rhythm', 'sinus' if t < T_LEFT else '—'), ('lead', 'II')]
        for i, (k, v) in enumerate(rows):
            c.text(W_ - 90, 120 + i * 26, f'{k:<7}{v:>10}', 'CascadiaMono.ttf', 13, GREEN, 200 * ia, anchor='rm')
        # the textbook key: a ring of particles under the wave, four phases
        c.text(90, 108, 'POLARISATIO  +', 'GARA.TTF', 13, GOLD, 170 * ia, anchor='lm')
        for i in range(4):
            hh = .3 * math.cos(ph + i * math.pi / 2) * clamp(amp * 10)
            pts = [(120 + i * 60 + 20 * (1 + hh) * math.cos(a / 20 * math.pi), 160 + 20 * (1 - hh) * math.sin(a / 20 * math.pi)) for a in range(0, 40, 2)]
            for p in pts: c.dot(*p, 1.2, WARM, 170 * ia)
    # the legend (always), a caption under the chart
    la = ease((t - T0 - .3) / .5) * fade
    x, y = 90, 380
    c.text(x, y - 40, 'TABULA  PLANETARUM', 'GARA.TTF', 14, GOLD, 200 * la, anchor='lm')
    for i, (gl, l) in enumerate(zip(GLYPH, LATIN)):
        c.text(x + 10, y + i * 28, gl, 'seguisym.ttf', 16, WARM, 220 * la)
        c.text(x + 36, y + i * 28, l, 'GARAIT.TTF', 16, WARM, 170 * la, anchor='lm')
    cap = 'VIBRATIONES' if t < T_THEN else ('COMPLETIO' if t < T_LEFT else '')
    if cap: c.text(W_ / 2, 1010, cap, 'GARA.TTF', 13, GOLD, 150 * la)
    return c.result()
