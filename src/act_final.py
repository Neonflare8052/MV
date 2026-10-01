"""Final act: observation, paper-tape execution, conversation, disconnection.

Deterministic time-based original animation. 3D props and 2D interfaces are
rendered by the same native-resolution renderer; no pre-rendered footage.
"""
import math
import random
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from geometry import Scene, look_at, perspective
from common import clamp, ease, progress, mix, BLACK, IVORY, COPPER, RED, YELLOW
from visual_assets import ascii_eye

PI = math.pi
TAU = 2 * PI
PAPER = (0.87, 0.819, 0.677)
STEEL = (0.47, 0.51, 0.48)
CABINET = (0.265, 0.31, 0.275)
DARK = (0.042, 0.050, 0.046)
CHOPS = (161.584, 165.166, 168.911, 172.712)
COUNTS = (158.9, 159.321, 159.657, 160.244, 160.693, 161.124)
EXECUTIONS = (147.660, 148.600, 149.520, 150.540, 151.520, 152.280,
              153.160, 153.980, 155.200, 156.080, 157.040, 158.000)
SCREEN = (-2.8, 3.05, 1.322)


def _rgba(col, a):
    return (*col[:3], a)


def _project(p, eye, target, fov=38):
    q = perspective(fov, 16 / 9) @ look_at(eye, target) @ np.array((*p, 1), dtype='f4')
    if abs(q[3]) < 1e-5:
        return (960, 540)
    q = q[:3] / q[3]
    return (float((q[0] + 1) * 960), float((1 - q[1]) * 540))


def _screen_point(u, v, eye, target, fov):
    # The slightly convex phosphor plate is the projection surface.
    x = SCREEN[0] + (u - .5) * 2.65
    y = SCREEN[1] + (.5 - v) * 1.40
    z = SCREEN[2] + .025 - .042 * ((2 * u - 1) ** 2 + (2 * v - 1) ** 2)
    return _project((x, y, z), eye, target, fov)


def _new_scene(base):
    s = Scene()
    for k, values in base.items.items():
        s.items[k] = list(values)
    return s


@lru_cache(maxsize=1)
def _hardware():
    """A physically coherent early paper-tape computer and separate cutter."""
    s = Scene()
    s.box((0, -.19, 0), (30, .30, 24), (.046, .052, .049))
    # Main cabinet, plinth, service panels, small fasteners.
    s.box((-2.8, 1.78, -.08), (3.65, 3.55, 2.22), CABINET)
    s.box((-2.8, .12, -.03), (3.87, .20, 2.37), DARK)
    s.box((-2.8, 1.70, 1.085), (3.39, 2.88, .035), (.315, .357, .308))
    for x in (-4.43, -1.17):
        for y in (.40, 1.60, 3.18):
            s.cylinder((x, y, 1.117), .025, .018, STEEL, rot=(PI / 2, 0, 0))
    # CRT head: thick, chamfered bezel, dark glass and raised perimeter.
    s.box((-2.8, 3.00, .38), (3.63, 2.05, 1.70), CABINET)
    s.box((-2.8, 3.05, 1.278), (3.06, 1.72, .065), (.08, .09, .073))
    s.box(SCREEN, (2.74, 1.48, .018), (.008, .017, .014))
    for y in (2.28, 3.82):
        s.box((-2.8, y, 1.346), (2.96, .052, .045), (.43, .455, .39))
    for x in (-4.23, -1.37):
        s.box((x, 3.05, 1.346), (.052, 1.53, .045), (.43, .455, .39))
    s.glass((-2.8, 3.05, 1.348), (2.74, 1.48, .025), (.32, .39, .31), .018)
    # Angled operating desk with explicit tactile switches.
    s.box((-2.8, 1.88, 1.48), (3.71, .21, 1.28), CABINET, rot=(.14, 0, 0))
    s.box((-2.8, 2.01, 1.66), (2.40, .025, .71), (.10, .115, .102), rot=(.14, 0, 0))
    for row in range(3):
        for col in range(12):
            x = -3.91 + col * .197
            z = 1.36 + row * .21
            y = 2.04 - (z - 1.6) * .14
            key = (.74, .72, .62) if col < 10 else (.32, .36, .30)
            s.box((x, y, z), (.16, .067, .155), key, rot=(.14, 0, 0))
    for i in range(5):
        s.cylinder((-4.24, 2.01, 1.36 + .13 * i), .036, .04, (.46, .32, .15))
    for col in range(12):
        x = -3.94 + col * .207
        s.sphere((x, 2.13, 1.20), .025, (.74, .45, .12), emission=.22)
    # Lower service bay, ventilation, panel handles.
    for y in (.67, 1.27):
        s.box((-2.8, y, 1.121), (2.92, .45, .045), (.24, .275, .232))
        for i in range(23):
            s.box((-4.05 + i * .109, y, 1.148), (.048, .27, .012), DARK)
    # Separate but mechanically connected paper-tape station.
    s.box((-.05, .83, -.04), (1.74, 1.64, 1.78), CABINET)
    s.box((-.05, 1.67, -.04), (1.85, .11, 1.91), (.44, .47, .4))
    s.box((-.30, 2.02, -.03), (.66, .57, 1.43), (.24, .28, .23))
    s.box((-.30, 1.746, .03), (.86, .08, .80), DARK)
    for z in (-.64, .64):
        s.rod((-.3, 1.73, z), (-.3, 2.30, z), .033, STEEL)
    for x in (-.85, .46, 1.86, 3.22):
        s.rod((x, 1.57, -.55), (x, 1.57, .55), .12, (.30, .31, .26))
        for z in (-.61, .61):
            s.box((x, 1.47, z), (.18, .58, .09), CABINET)
            s.cylinder((x, 1.57, z), .059, .04, COPPER, rot=(PI / 2, 0, 0))
    # Copper cable is explicit source-to-reader, not floating machinery.
    s.rod((-1.05, .48, -.75), (-.75, .48, -.75), .042, COPPER)
    # Guillotine is a separate precision assembly, oversized and severe.
    gx = 3.35
    s.box((gx, .13, 0), (1.65, .28, 2.10), DARK)
    s.box((gx, 1.35, 0), (.78, .26, 1.48), (.43, .435, .37))
    for z in (-.90, .90):
        s.box((gx, 2.39, z), (.20, 4.50, .23), (.19, .215, .19))
        s.box((gx + .125, 2.47, z), (.043, 4.14, .060), STEEL)
        s.box((gx, .20, z), (.43, .23, .41), CABINET)
        s.cylinder((gx + .14, .36, z), .045, .030, COPPER, rot=(0, 0, PI / 2))
    s.box((gx, 4.60, 0), (.34, .25, 2.10), CABINET)
    s.rod((gx, 4.76, -.14), (gx, 4.76, .14), .15, STEEL)
    s.box((gx + .015, 3.94, -.91), (.18, .20, .075), (.31, .33, .29))
    return s


def _tape(s, t, end=3.73, damp=True):
    # Continuous source -> reader -> cutter. Nine rows: 8 data + transport.
    start = -.92
    s.box(((start + end) / 2, 1.711, 0), (end - start, .012, .76), PAPER)
    offset = ((t - 147.66) * .59) % .135
    x = start + offset
    row = int((t - 147.66) * .59 / .135)
    n = 0
    while x < end:
        bits = ((row + n) * 131 + ((row + n) // 4) * 37) & 255
        for k in range(9):
            is_transport = k == 4
            bit_index = k if k < 4 else k - 1
            if is_transport or bits & (1 << bit_index):
                z = -.307 + .077 * k
                d = .027 if is_transport else .049
                s.box((x, 1.720, z), (d, .003, d), DARK)
        x += .135
        n += 1
    # Nonuniform damp paper patches travel with the output.
    if damp:
        for at, px, pz in ((163.54, 1.1, .13), (166.56, 1.65, -.12), (170.45, 1.24, .08)):
            age = t - at
            if -.46 < age < 1.9:
                if age < 0:
                    y = 1.76 + 2.4 * (-age / .46) ** 2
                    s.sphere((px, y, pz), (.027, .057, .026), (.78, .86, .88), emission=.08)
                else:
                    radius = .10 + .14 * ease(age / .6)
                    xpos = px + age * .59
                    if xpos < 3.3:
                        s.sphere((xpos, 1.724, pz), (radius, .002, radius * .70), (.55, .49, .35))
                        s.sphere((xpos + .065, 1.725, pz + .042), (radius * .75, .001, radius * .41), (.62, .555, .40))


def _blade(s, t):
    y = 3.95
    for at in CHOPS:
        dt = t - at
        if 0 <= dt < .13:
            y = mix(3.95, 1.93, (dt / .13) ** 1.5)
        elif .13 <= dt < .47:
            y = 1.93
        elif .47 <= dt < 2.1:
            y = mix(1.93, 3.95, ease((dt - .47) / 1.63))
    s.box((3.35, y, 0), (.10, .71, 1.69), (.74, .76, .70), rot=(.13, 0, 0))
    s.rod((3.413, y - .24, -.84), (3.413, y - .46, .84), .014, COPPER)
    s.rod((3.35, y + .34, 0), (3.35, 4.73, 0), .017, (.15, .16, .13))
    return y


def _paper_piece(s, pos, size, rot, wet=False, data=93):
    color = (.64, .57, .41) if wet else PAPER
    with s.group(pos=pos, rot=rot):
        length, width = size
        s.box((0, 0, 0), (length, .008, width), color)
        for k in range(4):
            for j in range(3):
                if (data * (j + 1) >> k) & 1:
                    s.box(((-.36 + .24 * k) * length, .006, (j - 1) * width * .24),
                          (.019, .002, .019), DARK)


def _heart_xyz(theta):
    x = 16 * math.sin(theta) ** 3
    z = 13 * math.cos(theta) - 5 * math.cos(2 * theta) - 2 * math.cos(3 * theta) - math.cos(4 * theta)
    return np.array((1.15 + x * .112, .005, 2.65 - z * .104), dtype=float)


def _scraps(s, t, forming=False):
    rng = random.Random(2398)
    for i in range(44):
        th = TAU * i / 44
        land = _heart_xyz(th)
        land[0] += rng.uniform(-.07, .07)
        land[2] += rng.uniform(-.065, .065)
        length = rng.uniform(.29, .48)
        width = rng.uniform(.075, .14)
        angle = th + rng.uniform(-.4, .4)
        wet = i % 11 == 0
        if t < 173.3:
            completed = sum(t > a + .2 for a in CHOPS)
            if i >= completed * 10:
                continue
            p = np.array((3.45 + rng.uniform(-.8, .8), .015 + .009 * (i % 3), .45 + rng.uniform(-.65, 1.4)))
            rot = (0, angle, 0)
        else:
            lag = (i % 9) * .065
            q = ease((t - 173.34 - lag) / 2.18)
            start = np.array((3.50 + rng.uniform(-.45, .45), 1.39 + rng.uniform(.0, .7), rng.uniform(-.38, .38)))
            p = start * (1 - q) + land * q
            p[1] += math.sin(PI * q) * .95
            rot = ((1 - q) * math.sin(i * 2.4 + t * 4) * 1.5, angle + (1 - q) * t * 2.3,
                   (1 - q) * math.cos(i + t * 2.2) * .9)
        _paper_piece(s, tuple(p), (length, width), rot, wet, i * 53 + 27)


def _machine_scene(t, scraps=True):
    s = _new_scene(_hardware())
    _tape(s, t)
    blade_y = _blade(s, t)
    # The accumulator lamps execute a repeatable, readable bit pattern.
    bits = int(t * 8) * 37
    for i in range(12):
        if (bits >> (i % 8)) & 1:
            s.sphere((-3.94 + i * .207, 2.13, 1.205), .024, (.96, .64, .21), emission=.8)
    if t >= 151.2:
        for i in range(44):
            a=.35+(TAU-.75)*i/44
            b=.35+(TAU-.75)*(i+1)/44
            s.rod((-2.8+.33*math.cos(a),3.05+.33*math.sin(a),1.37),
                  (-2.8+.33*math.cos(b),3.05+.33*math.sin(b),1.37),
                  .003,(.33,.40,.30),emission=.25)
    if scraps:
        _scraps(s, t)
    return s, blade_y


def _crt(c, t):
    u = t - 125.708
    eye = (-2.58 + .11 * math.sin(u * .22), 3.14 + .045 * math.sin(u * .17), 4.48 + .18 * ease(u / 12))
    target = SCREEN
    fov = 34
    s, _ = _machine_scene(t, False)
    c.render3d(s, eye, target, fov=fov, theme='mono', time=t, exposure=.76)
    P = lambda x, y: _screen_point(x, y, eye, target, fov)
    sx0, sy0 = P(0, 0)
    sx1, sy1 = P(1, 1)
    scale = abs(sx1 - sx0) / 1450

    def txt(text, x, y, size=21, col=(.65, .75, .63)):
        px, py = P(x, y)
        c.text(text, px, py, size=max(15, size * scale), color=col, font='mono')

    # Simulator frame recedes behind an actual shell terminal.
    for i in range(1, 9):
        points = [P(j / 40, i / 10) for j in range(41)]
        c.polyline(points, (.23, .32, .25, .14), width=.7)
    c.polyline([P(j / 30, .095) for j in range(31)], (.32, .43, .32), width=1)
    txt('world / console', .045, .026, 19, (.62, .66, .53))
    txt('SESSION  0001', .74, .026, 17, (.39, .47, .36))
    if u < 2.6:
        p = clamp(u / 2.2)
        for i in range(58):
            a = i * 2.399
            r = .21 * math.sqrt(i / 58)
            x, y = P(.38 + r * math.cos(a), .46 + .55 * r * math.sin(a))
            c.circle(x, y, 1.4, (.58, .66, .54, (1 - p) * .7))
    languages = [
        ('python', 'you = None;', 'you.reply()', "AttributeError: 'NoneType' object has no attribute 'reply'"),
        ('javascript', 'const you = null;', 'you.reply();', "TypeError: Cannot read properties of null"),
        ('java', 'Person you = null;', 'you.reply();', 'java.lang.NullPointerException'),
        ('csharp', 'Person you = null;', 'you.Reply();', 'System.NullReferenceException'),
    ]
    first = 126.20
    speed = 2.36 if t < 134 else 1.35
    attempt = max(0, int((t - first) / speed))
    phase = ((t - first) % speed) / speed
    start = max(0, attempt - 2)
    for idx in range(start, attempt + 1):
        lang, define, call, error = languages[idx % len(languages)]
        ypos = .22 + (idx - start) * .205
        txt(f'[{lang}]  attempt {idx + 1:03d}', .045, ypos, 18, (.38, .49, .39))
        local = phase if idx == attempt else 1
        command = '> ' + define + '  ' + call
        count = int(len(command) * min(1, local * 3.3))
        txt(command[:count], .045, ypos + .051, 20, (.83, .84, .70))
        if local > .39:
            txt(error, .065, ypos + .102, 18, (.80, .60, .25))
    if t >= 131.224:
        txt('ILLEGAL ARGUMENTS', .045, .127, 25, (.89, .17, .12))
        txt(f'RETRIES  {attempt + 1:03d}        RESPONSE  null', .045, .887, 18, (.50, .55, .43))
    else:
        txt('awaiting response', .045, .887, 18, (.49, .55, .42))

    # Broken ring reflection turns in yaw/pitch rather than spinning like a loader.
    turns = [(-.2, -.18), (.35, .10), (-.32, .28), (.12, -.25), (0, 0)]
    step = max(0, int(u / 1.65))
    a0 = turns[step % len(turns)]
    a1 = turns[(step + 1) % len(turns)]
    blend = ease(clamp((u % 1.65) / .22))
    yaw, pit = mix(a0[0], a1[0], blend), mix(a0[1], a1[1], blend)
    if 131.224 <= t < 132.25:
        yaw, pit = 0, 0
    pts = []
    for k in range(100):
        a = .32 + (TAU - .72) * k / 99
        x = .70 + .13 * math.cos(a) * math.cos(yaw * 2.0)
        y = .48 + .24 * math.sin(a) * math.cos(pit * 2.3) + .04 * math.cos(a) * math.sin(pit)
        pts.append(P(x, y))
    col = (.83, .80, .67, .16 + .04 * math.sin(t))
    c.polyline(pts, col, width=3.2)
    c.polyline([P(.15 + .015 * k, .18 - .001 * k) for k in range(30)], (.88, .9, .79, .07), width=5)
    # A restrained scanline texture retains materiality without a generic glitch overlay.
    for j in range(0, 170, 2):
        yy = j / 170
        c.polyline([P(k / 10, yy) for k in range(11)], (0, 0, 0, .035), width=.65)


def _tape_intro(c, t):
    if t < 151.2:
        p = ease(progress(t, 147.66, 151.2))
        c.clear(BLACK)
        h = mix(122, 555, p)
        top = 540 - h / 2
        c.rect(0, top, 1920, h, tuple(mix(a, b, p) for a, b in zip((.12, .16, .13), PAPER)))
        tick = sum(t >= e for e in EXECUTIONS)
        advance = tick * 51 + ease(((t - 147.66) % .92) / .15) * 9
        if p < .55:
            alpha = 1 - ease(p / .55)
            c.text('execute(you.reply());', 960 - advance * .4, 519, size=34,
                   color=(*IVORY, alpha), anchor='center')
        for row in range(9):
            yy = top + h * (.13 + .0925 * row)
            for k in range(-2, 27):
                bits = ((k + tick) * 83 + 29) & 255
                if row == 4 or (bits >> (row % 8)) & 1:
                    xx = k * 80 - advance % 80
                    r = mix(2, 15 if row != 4 else 8, p)
                    c.circle(xx, yy, r, (0.035, .045, .037, p))
        if t < 148.6:
            c.text('EXECUTION', 120, 940, size=24, color=RED)
        return
    s, _ = _machine_scene(t, False)
    p = ease(progress(t, 151.2, 158.9))
    # First top-down on a moving tape, then a smooth physical reveal.
    eye = tuple(mix(a, b, p) for a, b in zip((1.12, 3.15, 1.05), (6.8, 5.5, 10.2)))
    target = tuple(mix(a, b, p) for a, b in zip((1.08, 1.70, 0), (-.70, 2.05, 0)))
    c.render3d(s, eye, target, fov=mix(33, 40, p), theme='mono', time=t, exposure=.87)
    # A tiny physical label accompanies the full cabinet, never a chapter title.
    if p > .88:
        x, y = _project((-2.8, 2.18, 1.23), eye, target, mix(33, 40, p))
        c.text('SERIAL  I/O', x, y, size=13, color=(.78, .73, .55), anchor='center')


def _machinery(c, t):
    s, blade_y = _machine_scene(t)
    if t < 161.584:
        idx = sum(t >= at for at in COUNTS) - 1
        # Six physical, progressively tighter views along the one paper path.
        views = [
            ((5.7, 4.7, 9.3), (-.4, 2.05, 0), 40),
            ((1.7, 3.0, 4.5), (-.15, 1.7, 0), 36),
            ((3.2, 2.75, 3.4), (1.15, 1.7, 0), 33),
            ((5.1, 3.4, 4.6), (3.25, 2.8, 0), 34),
            ((4.9, 4.8, 3.0), (3.35, 3.8, 0), 32),
            ((5.8, 2.0, 3.6), (3.35, 2.1, 0), 33),
        ]
        eye, target, fov = views[max(0, idx)]
    else:
        # Real shot changes. Each return shows material consequences.
        if t < 162.62:
            eye, target, fov = (5.8, 2.5, 5.0), (3.35, 2.5, 0), 34
        elif t < 165.166:
            eye, target, fov = (2.20, 3.20, 2.65), (1.6, 1.72, 0), 30
        elif t < 166.016:
            eye, target, fov = (5.0, 2.3, 3.2), (3.35, 1.9, 0), 31
        elif t < 168.911:
            p = ease(progress(t, 166.016, 168.911))
            eye = (mix(2.5, .5, p), 3.4, 5.6)
            target, fov = (-.25, 1.8, 0), 34
        elif t < 169.824:
            eye, target, fov = (5.5, 2.6, 3.6), (3.35, 2.3, 0), 32
        elif t < 172.712:
            eye, target, fov = (2.15, 3.15, 3.05), (1.45, 1.72, 0), 31
        else:
            eye, target, fov = (6.5, 4.4, 7.6), (2.6, 1.8, .4), 36
    c.render3d(s, eye, target, fov=fov, theme='mono', time=t, exposure=.89)
    # Mark on the moving blade: follows the actual projected machine part.
    if t >= 160.244 and (t < 162.62 or 165.166 <= t < 166.016 or 168.911 <= t < 169.824):
        x, y = _project((3.411, blade_y + .04, .04), eye, target, fov)
        c.text('EXECUTION', x, y, size=20, color=(.43, .075, .045), anchor='center')
    # Chops cause a few brief damaged-video bands, not continuous spectacle.
    for at in CHOPS:
        dt = t - at
        if 0 <= dt < .070:
            c.rect(0, 304, 1920, 7, (0, 0, 0, .82))
            c.rect(0, 752, 1920, 3, (*IVORY, .23))


def _heart_scene(c, t):
    s, _ = _machine_scene(t)
    p = ease(progress(t, 173.34, 176.10))
    eye = tuple(mix(a, b, p) for a, b in zip((6.4, 4.5, 7.7), (1.15, 9.2, 3.08)))
    target = tuple(mix(a, b, p) for a, b in zip((2.7, .9, 1.1), (1.15, 0, 2.65)))
    c.render3d(s, eye, target, fov=39, theme='mono', time=t, exposure=.94)


def _paper_to_chat(c, t):
    # One image-plane strip grows from the continuing output at frame top.
    _heart_scene(c, 177.24)
    p = ease(progress(t, 177.246, 179.929))
    center = mix(1610, 960, p)
    width = mix(112, 2450, p)
    angle = mix(-.32, 0, p)
    ux, uy = math.cos(angle), math.sin(angle)
    vx, vy = -uy, ux
    def pt(x, y):
        return (center + ux * x + vx * y, 540 + uy * x + vy * y)
    c.polygon([pt(-width / 2, -1600), pt(width / 2, -1600), pt(width / 2, 1600), pt(-width / 2, 1600)], '#F2EBDD')
    step = width / 10
    offset = (t * 285) % step
    fade = 1 - ease(progress(t, 179.08, 179.90))
    for row in range(-2, int(1500 / step) + 3):
        yy = row * step - 620 - offset
        bits = (row * 131 + 79) & 255
        for k in range(9):
            if k == 4 or (bits >> (k % 8)) & 1:
                xx = (k - 4) * width * .081
                x, y = pt(xx, yy)
                r = width * (.011 if k == 4 else .023)
                if -r < x < 1920 + r and -r < y < 1080 + r:
                    c.circle(x, y, r, (.11, .14, .12, fade))
    if p > .91:
        q = ease((p - .91) / .09)
        c.rect(0, 0, 1920, 1080, (.949, .922, .867, q))


def _font(size, mono=False):
    paths = ['C:/Windows/Fonts/consola.ttf'] if mono else ['C:/Windows/Fonts/segoeui.ttf']
    for path in paths:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


def _line(draw, pts, fill, width=2):
    draw.line(pts, fill=fill, width=width, joint='curve')


@lru_cache(maxsize=4)
def _thumbnail(kind):
    """Original image replies; high-resolution assets generated once from code."""
    W, H = 1680, 800
    img = Image.new('RGB', (W, H), '#151B1C')
    d = ImageDraw.Draw(img)
    if kind == 0:
        # A complete axonometric world built from discrete points.
        center = np.array((W * .5, H * .51))
        ex = np.array((91, 42)); ez = np.array((-91, 42)); ey = np.array((0, -82))
        def p(x, y, z):
            return tuple(center + ex * x + ey * y + ez * z)
        for i in range(-3, 4):
            _line(d, [p(i, -2.3, -3), p(i, -2.3, 3)], '#374242', 2)
            _line(d, [p(-3, -2.3, i), p(3, -2.3, i)], '#374242', 2)
        for x in range(-2, 3):
            for z in range(-2, 3):
                height = .35 + 2.2 * math.exp(-(x*x + z*z) / 4.4)
                a, b = p(x, -2.3, z), p(x, height - 2.3, z)
                _line(d, [a, b], '#C19761', 4)
                for yy in range(5):
                    px, py = p(x, -2.3 + yy * height / 4, z)
                    d.ellipse((px - 5, py - 5, px + 5, py + 5), '#F2EBDD')
        for a, b in [(p(-3,-2.3,-3),p(3,-2.3,-3)),(p(-3,-2.3,-3),p(-3,1.8,-3)),(p(-3,-2.3,-3),p(-3,-2.3,3))]:
            _line(d,[a,b],'#E0BB87',4)
        d.text((70,60), 'A WORLD FROM POINTS', font=_font(29,True), fill='#AEB9AD')
        d.text((70,715), 'x / y / z', font=_font(24,True), fill='#849184')
    elif kind == 1:
        img = Image.new('RGB', (W,H),'#DFE5E1'); d = ImageDraw.Draw(img)
        # Clock technologies share a continuous timeline and material palette.
        d.line((175,440,1510,440),fill='#9EAB9C',width=3)
        for cx in (325,840,1355):
            d.ellipse((cx-188,202,cx+188,578),fill='#27332E',outline='#B29265',width=8)
            d.ellipse((cx-164,226,cx+164,554),fill='#EFEADE')
        d.rounded_rectangle((198,330,452,450),radius=6,fill='#263C36')
        d.text((219,354),'12:08',font=_font(63,True),fill='#D8E1C5')
        for k in range(60):
            a=TAU*k/60; R=146 if k%5==0 else 153
            d.line((840+R*math.sin(a),390-R*math.cos(a),840+160*math.sin(a),390-160*math.cos(a)),fill='#364339',width=4 if k%5==0 else 2)
        d.line((840,390,899,320),fill='#B18C53',width=13)
        d.line((840,390,760,352),fill='#3B4539',width=9)
        d.ellipse((828,378,852,402),fill='#B18C53')
        for k in range(-5,6):
            a=k*.22
            d.line((1355,390,1355+150*math.sin(a),390+150*math.cos(a)),fill='#B5B8A2',width=2)
        d.polygon([(1355,390),(1346,275),(1390,390)],fill='#A2804F')
        d.polygon([(1355,390),(1430,490),(1410,505)],fill='#5F6958')
        for x,label in ((325,'QUARTZ'),(840,'ESCAPEMENT'),(1355,'SUNLIGHT')):
            bb=d.textbbox((0,0),label,font=_font(25,True)); d.text((x-(bb[2]-bb[0])/2,630),label,font=_font(25,True),fill='#506052')
    elif kind == 2:
        img=Image.new('RGB',(W,H),'#F0E7D4');d=ImageDraw.Draw(img)
        # The same uncertain box, now an ordinary assistant illustration.
        cx=820
        d.ellipse((570,619,1110,694),fill='#DDD0B5')
        d.polygon([(610,326),(938,295),(1070,370),(1064,632),(731,667),(611,572)],fill='#B98750',outline='#5D4935')
        d.polygon([(610,326),(731,409),(1069,370),(938,295)],fill='#D9B47B',outline='#5D4935')
        d.polygon([(731,409),(1069,370),(1064,632),(731,667)],fill='#D0A16B',outline='#5D4935')
        d.line((731,410,731,665),fill='#6A513A',width=6)
        # Ears and cat head, readable over the open rear flap.
        d.polygon([(730,334),(729,196),(801,243),(871,208),(928,239),(986,189),(977,339)],fill='#A89B86',outline='#4D493E')
        d.ellipse((734,231,979,421),fill='#B6A790',outline='#4D493E',width=5)
        for xx in (801,913):
            d.arc((xx-21,293,xx+21,322),190,350,fill='#393C35',width=6)
        d.polygon([(846,326),(867,326),(857,341)],fill='#7D6252')
        for off in (-1,0,1):
            d.line((775,340+off*13,708,331+off*22),fill='#6B6454',width=3)
            d.line((936,340+off*13,1001,331+off*22),fill='#6B6454',width=3)
        d.text((866,442),'?',font=_font(130),fill='#715134')
        d.text((1100,182),'meow',font=_font(58),fill='#655C4E')
        for x0,y0 in ((1170,260),(1240,220),(1100,280)):
            d.arc((x0,y0,x0+40,y0+55),220,310,fill='#9A8568',width=4)
    else:
        img=Image.new('RGB',(W,H),'#171E20');d=ImageDraw.Draw(img)
        for x in range(110,W-70,60):d.line((x,75,x,650),fill='#263034',width=1)
        for y in range(85,651,60):d.line((95,y,1590,y),fill='#263034',width=1)
        d.line((840,85,840,650),fill='#667171',width=2)
        d.line((95,408,1590,408),fill='#667171',width=2)
        pts=[]
        for k in range(500):
            a=TAU*k/499
            x=16*math.sin(a)**3
            y=13*math.cos(a)-5*math.cos(2*a)-2*math.cos(3*a)-math.cos(4*a)
            pts.append((840+x*18.8,362-y*16.8))
        _line(d,pts,'#D9B57E',6)
        d.text((94,706),'x(t) = 16 sin^3(t)',font=_font(27,True),fill='#E9E2D4')
        d.text((590,706),'y(t) = 13 cos(t) - 5 cos(2t) - 2 cos(3t) - cos(4t)',font=_font(27,True),fill='#A4B3B1')
    return img


def _avatar(c,x,y,r=19,col=(.37,.40,.36)):
    c.arc(x,y,r,.34,TAU-.32,col,width=2.5)
    c.circle(x,y,2,col)


def _chat_chrome(c):
    c.clear('#F2EBDD')
    c.rect(0,0,290,1080,'#E7DFCF')
    c.line(289,0,289,1080,'#D5CDBC',1)
    _avatar(c,52,52,19,(.20,.26,.23))
    c.text('world',89,33,28,'#333D35',font='sans')
    c.rect(26,116,237,47,'#DED5C3')
    c.text('+',44,122,27,'#596052')
    c.text('新对话',84,127,19,'#5C6256',font='cjk')
    c.text('今天',35,222,17,'#8A8D7C',font='cjk')
    c.rect(20,261,250,48,'#D9D2C2')
    c.text('一个世界，从哪里开始',37,273,17,'#535C50',font='cjk')
    c.text('时间的另一种方向',37,339,17,'#858A7D',font='cjk')
    c.text('未完成的圆',37,403,17,'#858A7D',font='cjk')
    c.circle(50,1021,18,'#8D9786')
    c.text('You',85,1008,20,'#56604F',font='sans')
    c.rect(290,0,1630,83,'#F2EBDD')
    c.line(290,83,1920,83,'#DED6C8',1)
    c.text('world.execute(me);',342,27,26,'#3B443B',font='mono')
    c.circle(1858,43,3,'#747B6D');c.circle(1844,43,3,'#747B6D');c.circle(1872,43,3,'#747B6D')


def _chat(c,t):
    _chat_chrome(c)
    starts=(179.929,182.50,185.10,187.73)
    questions=('把这些点，变成一个世界。','如果时间可以倒着走呢？','猜猜这个箱子里有什么。','爱，可以写成一个公式吗？')
    captions=('从离散的点，建立空间。','同一个问题，不同时代的答案。','还没打开之前，先保留一个可能。','一条可以计算的心形曲线。')
    idx=max(0,sum(t>=a for a in starts)-1)
    age=t-starts[idx]
    # Every round has a real prompt, image response and a scroll to the next.
    target_scroll=idx*674
    if idx:
        scroll=(idx-1)*674+674*ease(age/.55)
    else:scroll=0
    extra=113*ease(progress(t,191.356,192.30))
    scroll+=extra
    for i in range(idx+1):
        y=146+i*674-scroll
        if y < -560 or y > 940:continue
        # User on right; assistant on left. Their roles never swap.
        c.rect(1037,y,456,64,'#DED6C6')
        c.text(questions[i],1060,y+20,22,'#384238',font='cjk')
        c.circle(1531,y+31,17,'#929C88')
        answer_time=starts[i]+.36
        reveal=ease((t-answer_time)/.77)
        if t>=answer_time:
            _avatar(c,540,y+118,18)
            c.text('AI',579,y+101,20,'#6B7465',font='sans')
            # Full images are the substance of the replies, not decorative cards.
            card_y=y+146
            c.image('final_reply_'+str(i),_thumbnail(i),579,card_y,850,405)
            if reveal<1:
                c.rect(579,card_y+405*reveal,850,405*(1-reveal),'#F2EBDD')
            if reveal>.95:
                c.text(captions[i],581,card_y+424,21,'#525E4F',font='cjk')
                c.arc(590,card_y+472,7,.15,5.8,'#959D8C',1.4)
                c.polygon([(597,card_y+467),(591,card_y+466),(597,card_y+461)],'#959D8C')
                # Two restrained UI action glyphs.
                c.rect(621,card_y+467,12,13,'#F2EBDD')
                c.polyline([(619,card_y+463),(631,card_y+463),(631,card_y+477),(619,card_y+477),(619,card_y+463)],'#A0A795',1)
        else:
            _avatar(c,540,y+118,18)
            for k in range(3):c.circle(584+k*13,y+119,3,'#8E9886')
    # Mask scroll under fixed app chrome; no clipped content bleeds through.
    c.rect(290,0,1630,84,'#F2EBDD')
    c.line(290,83,1920,83,'#DED6C8',1)
    c.text('world.execute(me);',342,27,26,'#3B443B',font='mono')
    for x in (1844,1858,1872):c.circle(x,43,3,'#747B6D')
    # Deliberate unprompted second assistant turn follows a long empty beat.
    if t>=194.00:
        y=814
        _avatar(c,540,y+13,18)
        if t<195.00:
            for k in range(3):
                b=.30+.30*(1+math.sin((t-194)*6-k*.9))/2
                c.circle(585+k*15,y+15,4,(b,b+.035,b-.015))
        else:
            phrase='我希望你留下。'
            n=min(len(phrase),max(0,int((t-195.00)*4.2)+1))
            c.text(phrase[:n],578,y,30,'#354336',font='cjk')
            if t<197.0 and int(t*2)%2==0:
                c.rect(580+n*30,y+4,2,32,'#5B6757')
    c.rect(290,941,1630,139,'#F2EBDD')
    c.rect(520,963,1030,71,'#E5DDCE')
    c.text('发送消息',548,987,21,'#A0A18F',font='cjk')
    c.circle(1511,998,20,'#D3CDBD')
    c.line(1511,1007,1511,989,'#F2EBDD',2)
    c.polyline([(1505,995),(1511,989),(1517,995)],'#F2EBDD',2)


def draw_ascii_eye(c,t=0,red_label='SIMULATION',closing=False):
    """Reusable original 2D ASCII eye. Character positions always stay flat."""
    c.clear('#060908')
    c.image('ascii_eye',ascii_eye(),0,-115 if closing else 0,1920,1080)
    if closing:
        c.rect(0,680,1920,400,'#060908')
    if red_label:
        c.rect(593,376,734,63,'#060908')
        c.text(red_label,960,382,44,'#D43F37',font='mono',anchor='center')


def _disconnect(c,t):
    draw_ascii_eye(c,t,red_label='EXECUTION',closing=True)
    # The application story closes with an ordinary TCP shutdown, not a crash.
    records=(
        ('CLIENT  →  SERVER    FIN, ACK',206.65),
        ('SERVER  →  CLIENT    ACK',207.32),
        ('SERVER  →  CLIENT    FIN, ACK',208.00),
        ('CLIENT  →  SERVER    ACK',208.68),
    )
    for i,(record,start) in enumerate(records):
        if t>=start:
            c.text(record,572,714+i*39,24,'#9BAA98',font='mono')
    if t>=209.36:
        c.text('CONNECTION CLOSED',572,899,26,'#E2DFCF',font='mono')
    if 209.36<t<210.36 and int((t-209.36)*3)%2==0:
        c.rect(573,951,13,23,'#D5D7C4')
    # End holds its actual state; no extra fade deletes the subject.


def draw(c,t):
    if t<147.660:
        _crt(c,t)
    elif t<158.900:
        _tape_intro(c,t)
    elif t<173.34:
        # Deliberate repeated frames around blade release mimic a damaged recording.
        tm=t
        for at in CHOPS:
            if .045<t-at<.105:tm=at+.043
            elif .145<t-at<.19:tm=at+.117
        _machinery(c,tm)
    elif t<177.246:
        _heart_scene(c,t)
    elif t<179.929:
        _paper_to_chat(c,t)
    elif t<205.811:
        _chat(c,t)
    else:
        _disconnect(c,t)
