"""Measurements drawn from s03's actual geometry and waveform parameters.

Everything is projected with the retained shot camera. The signal at the end
is authored in screen space by the original shader, so its probe uses that same
space. This module adds no geometry and makes no model-capacity claims.
"""
import math

from PIL import ImageDraw
from common import blank, gate, project, tag, font, color, WHITE, COPPER, DIM, smooth

WINDOWS = [(30.15, 33.3), (34.6, 36.9), (38.2, 40.65),
           (41.55, 44.2), (44.45, 46.7)]


def _poly(draw, pts, tint, a, h, width=1.25):
    """Do not join through a clipped or behind-camera point."""
    run = []
    for p in pts + [None]:
        if p is None or not (-h < p[0] < 4*h and -h < p[1] < 2*h):
            if len(run) > 1:
                draw.line(run, fill=color(tint, a), width=max(1, round(width*h/1080)))
            run = []
        else:
            run.append(p)


def _ruler(draw, a, b, tint, alpha, h, arrow=False):
    if a is None or b is None:
        return
    dx, dy = b[0]-a[0], b[1]-a[1]
    length = math.hypot(dx, dy)
    if length < 20*h/1080 or length > 2.5*h:
        return
    tx, ty = dx/length, dy/length
    nx, ny = -ty, tx
    s = h/1080
    col = color(tint, alpha)
    width = max(1, round(s))
    draw.line((a, b), fill=col, width=width)
    for x, y in (a, b):
        draw.line([(x-nx*5*s, y-ny*5*s), (x+nx*5*s, y+ny*5*s)],
                  fill=col, width=width)
    if arrow:
        x, y = b
        draw.line([(x-tx*11*s+nx*4*s, y-ty*11*s+ny*4*s), b,
                   (x-tx*11*s-nx*4*s, y-ty*11*s-ny*4*s)],
                  fill=col, width=width)


def _derivative(mod, x, j, t):
    # Identical to waveD in SPRITE_VS; no derivative of the camera trajectory.
    return (.35*1.7*math.cos(1.7*x+.22*j-(t-mod.T_SIN)*1.2)
            + .12*3.3*math.cos(3.3*x-.15*j))


def _fract(x):
    return x-math.floor(x)


def _hash12(x, y):
    # Literal CPU transcription of the signal shader's h12.
    q = [_fract(x*.1031), _fract(y*.1031), _fract(x*.1031)]
    d = sum(a*(b+33.33) for a, b in zip(q, (q[1], q[2], q[0])))
    q = [v+d for v in q]
    return _fract((q[0]+q[1])*q[2])


def _signal_probe(mod, p, t, w, h):
    """Returns the exact primary waveform centreline at one shader sample."""
    x, row, g, amp = -.27, 4, .034, .011
    qx = x+t*.22
    shift = math.floor(_hash12(row, 3.)*8.)
    theta = (qx/g+shift)*math.pi/4.
    if p['u_sq'] < 1.:
        y = sum(max(0., min(1., p['u_harm']-m+1.))*math.sin(m*theta)/m
                for m in range(1, 22, 2))*amp*4./math.pi
        label = 'SIGNAL'
        count = sum(p['u_harm']-m+1. > 0 for m in range(1, 22, 2))
        detail = f'{count:02d} odd harmonic' + ('s' if count != 1 else '')
    else:
        cx = math.floor(qx/g)
        regular = 1.-((math.floor((cx+shift)/4.)) % 2.)
        bit = int(_hash12(cx, row) >= .55)
        chosen = bit if p['u_data'] >= _hash12(cx+7., row+7.) else regular
        y = (chosen*2.-1.)*amp
        label, detail = 'QUANTIZATION', 'low 0  /  high 1'
    cy = (row+.5)*g
    return (w/2+x*h, h/2-(cy+y)*h), (label, detail), (w/2+x*h, h/2-cy*h)


def overlay(mod, t, w, h):
    img = blank(w, h)
    a = gate(t, WINDOWS)
    if a <= .001:
        return img
    draw = ImageDraw.Draw(img)
    p = mod.params(t)
    sp = mod.specials(t)
    pr = lambda v: project(v, p, w, h)
    you, me, love = (pr(v) for v in sp)

    if 30.15 <= t <= 33.3:
        # The origin moves with YOU only as the authored axes appear.
        axes = p['u_axes']
        lines = ('YOU', 'reference origin' if axes > .12 else 'selected point')
        tag(draw, you, lines, w, h, a, WHITE, (1, -1), (76, 60))
        if axes > .1:
            origin = sp[0]
            ends = [('x', (2.4*axes, 0., 0.)),
                    ('y', (0., 1.44*axes, 0.)),
                    ('z', (0., 0., 2.4*axes))]
            for name, v in ends:
                xy = pr(tuple(x+y for x, y in zip(origin, v)))
                if xy is not None and 35 < xy[0] < w-35 and 35 < xy[1] < h-35:
                    draw.text((xy[0]+7*h/1080, xy[1]-12*h/1080), name,
                              font=font(21*h/1080), fill=color(COPPER, a*.7*axes),
                              stroke_width=1, stroke_fill=(4, 5, 5, round(a*150)))

    elif 34.6 <= t <= 36.9:
        radius = .12+.045*18  # The ME circle, not an arbitrary outer ring.
        centre = (0., 1.1, 0.)
        fade = a*smooth((t-34.6)/.45)
        pts = [pr((radius*math.cos(k*2*math.pi/96),
                   1.1+radius*math.sin(k*2*math.pi/96), 0.)) for k in range(97)]
        _poly(draw, pts, COPPER, fade*.3, h)
        _ruler(draw, pr(centre), me, COPPER, fade*.65, h)
        tag(draw, you, ('YOU', 'circle center'), w, h, a, WHITE,
            (1, -1), (76, 60))
        # Numeric radius and circumference are the actual authored dimensions.
        tag(draw, me, ('ME', f'R {radius:.2f} u  /  C {2*math.pi*radius:.2f} u'),
            w, h, a, COPPER, (-1, 1), (76, 64), 'circle')

    elif 38.2 <= t <= 40.65:
        # ME and YOU occupy the same j=18 waveform, at different x positions.
        x, _, z = sp[1]
        j = 18
        slope = _derivative(mod, x, j, t)
        tangent_a = a*smooth((t-39.55)/.35)
        tag(draw, you, ('YOU', 'wave 18'), w, h, a, WHITE,
            (1, -1), (72, 58))
        if tangent_a > .01:
            y = mod.wave_y(x, j, t)
            pts = [pr((xx, mod.wave_y(xx, j, t), z))
                   for xx in [x-.42+k*.84/36 for k in range(37)]]
            _poly(draw, pts, WHITE, tangent_a*.4, h)
            L = .64/math.sqrt(1+slope*slope)
            _ruler(draw, pr((x-L/2, y-slope*L/2, z)),
                   pr((x+L/2, y+slope*L/2, z)), COPPER,
                   tangent_a*.9, h)
            detail = f'dy/dx {slope:+.2f}'
        else:
            detail = f'f(x) {sp[1][1]:.2f} u'
        tag(draw, me, ('ME', detail), w, h, a, COPPER,
            (-1, 1), (76, 60), 'circle')

    elif 41.55 <= t <= 44.2:
        # The active shader draws its boundary at YOU, not at the unused WIN_X.
        boundary = p['u_winA'] > .1
        tag(draw, you, ('YOU', 'receive boundary' if boundary else 'flow destination'),
            w, h, a, WHITE, (1, -1), (76, 64))
        dist = math.dist(sp[0], sp[2])
        flicker = .7+.3*(math.floor(t*9) % 3 != 0)
        tag(draw, love, ('LOVE', f'distance {dist:.2f} u'), w, h,
            a*flicker, COPPER, (-1, -1), (80, 74), 'cross')
        # A short arrow sits below the token rows and advances toward YOU.
        flow_a = a*smooth((t-41.85)/.3)
        _ruler(draw, pr((mod.YOU_TOK[0]-.72, .48, 0.)),
               pr((mod.YOU_TOK[0]-.18, .48, 0.)),
               DIM, flow_a*.65, h, arrow=True)
        if boundary:
            _ruler(draw, pr((mod.YOU_TOK[0], .48, 0.)),
                   pr((mod.YOU_TOK[0], 1.28, 0.)), WHITE, a*.45, h)

    elif 44.45 <= t <= 46.7:
        sample, lines, zero = _signal_probe(mod, p, t, w, h)
        signal_a = a*p['u_wave']*(1.-p['u_block']*.45)
        # The sample and zero guide are on row 4 of the real authored waveform.
        tag(draw, sample, lines, w, h, signal_a, WHITE,
            (-1, -1), (78, 79), 'circle')
        s = h/1080
        draw.line([(zero[0]-48*s, zero[1]), (zero[0]+48*s, zero[1])],
                  fill=color(DIM, signal_a*.6), width=max(1, round(s)))
        if p['u_sq'] > 0:
            x = zero[0]+56*s
            _ruler(draw, (x, zero[1]-.011*h), (x, zero[1]+.011*h),
                   COPPER, signal_a*.7, h)
            for bit, yy in ((1, zero[1]-.011*h), (0, zero[1]+.011*h)):
                draw.text((x+10*s, yy-10*s), str(bit), font=font(19*s),
                          fill=color(COPPER, signal_a), stroke_width=1,
                          stroke_fill=(4, 5, 5, round(signal_a*150)))
    return img
