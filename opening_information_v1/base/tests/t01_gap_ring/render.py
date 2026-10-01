"""t01 · gap ring prototype (0:47.0–1:00.2). Timing from LRC + onset analysis (beat ≈ 0.4635 s).

blind my vision -> dizzy -> A.D to B.C (clocks / eras through the gap)
-> the view keeps turning, the disk becomes Earth and time keeps running back:
   Moon dissolves into a debris cloud, the debris spirals back into the impact point (unite so deeply),
   Theia pulls out of the notch and flies off -> scan line turns it into a vector simulation.
"""
import sys, math, argparse, time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'engine'))
from gl import Renderer, encode, save_png

START, END = 47.0, 60.2
# beats from claude/engine/onsets.py
B = dict(c1=47.837, c2=48.290, c3=48.754, c4=49.218, dz1=49.671, dz1m=50.136, dz2=50.600, dz2m=51.064,
         travel=51.540, ad=53.386, bc=54.303, unite=55.232, conv=56.149, deep1=56.916, burst=57.067,
         deep2=58.460, chorus=59.223)
GAP_HIT = math.radians(330.)
EXIT = math.radians(345.)
PHOS = (.55, 1., .78)   # phosphor colour of the vector display


def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def ramp(t, a, b): return ease((t - a) / (b - a))
def lin(t, a, b): return clamp((t - a) / (b - a))
def outc(x): x = clamp(x); return 1 - (1 - x) ** 3


def saccade(t, t0, a, b, dur, over=.07):
    if t < t0: return a
    x = (t - t0) / dur
    if x < 1: return a + (b - a) * (1 + over) * outc(x)
    return b + (b - a) * over * (1 - ease((t - t0 - dur) / .16))


def gap_deg(t):
    g = 90.
    for t0, tgt, dur in ((B['dz1'], 160., .08), (B['dz1m'], 148., .05), (B['dz2'], 22., .11), (B['dz2m'], 34., .05)):
        g = saccade(t, t0, g, tgt, dur)
    if t >= B['travel']:                                   # deliberate counter-clockwise turn: time runs back
        g = g + (90. - g) * ease((t - B['travel']) / .46)
    g = saccade(t, B['ad'], g, 210., .12)
    g = saccade(t, B['bc'], g, 330., .12)
    g += 360. * ease((t - 54.42) / 1.05)                   # the view keeps turning while the disk becomes Earth
    fix = 1 - ramp(t, 54.4, 54.6)
    g += fix * (0.9 * math.sin(t * 7.3) + 0.5 * math.sin(t * 13.1 + 1.))   # fixational drift
    return g


def cam_for(t):
    n = 8; ax = ay = 0.
    for i in range(n):
        g = math.radians(gap_deg(t - i * .025)); ax += math.cos(g); ay += math.sin(g)
    k = .13 * ramp(t, B['dz1'], 51.3) / n
    return ax * k, ay * k


def _params(t):
    cover = sum(.2125 * outc((t - c) / .2) for c in (B['c1'], B['c2'], B['c3'], B['c4']))
    half = math.pi * (1 - cover)
    # the gap closes as the disk becomes Earth, and reopens when Theia pulls out of it
    half *= 1 - ramp(t, 54.6, 55.35)
    # (v3) once it is Earth it stays a whole sphere: the gap never reopens
    earth = ramp(t, 54.55, 55.35)
    R = 1.25 + (.24 - 1.25) * ramp(t, B['dz1'], 51.3)
    R += (.20 - .24) * ramp(t, 54.6, 55.4)
    zoom = 1. + .32 * ramp(t, 54.6, 55.6)
    cx, cy = cam_for(t)
    cx, cy = cx * (1 - earth), cy * (1 - earth)
    dizzy = ramp(t, 49.53, 49.8) * (1 - ramp(t, 51.4, 51.7))
    focus = ramp(t, B['travel'], B['travel'] + .3)
    tr = max(t - 51.3, 0.)
    p = dict(u_R=R, u_half=half, u_gap=math.radians(gap_deg(t)), u_cam=(cx, cy), u_zoom=zoom,
             u_token=1 - ramp(t, 48.9, 49.5), u_focus=focus, u_expo=.45 + .55 * focus, u_dizzy=dizzy,
             u_planet=ramp(t, B['burst'] - .1, B['burst']), u_earth=earth,
             u_clock=12 * 60 + 47 - tr * 97., u_gear=-tr * 2.4, u_hand=math.radians(262.) - tr * math.radians(24.),
             u_shadow=math.radians(352.) - tr * math.radians(9.), u_reverse=-tr,
             u_spin=-max(t - 54.3, 0.) * 1.6, u_geo=ramp(t, 55.35, 56.3), u_stars=.25 + .75 * earth)
    # Moon: closer in the past, orbiting backwards, then torn into a ring
    mbreak = ramp(t, 55.65, 56.15)
    mdist = .62 - .22 * ramp(t, 54.9, 56.0)
    mang = math.radians(120.) - max(t - 54.9, 0.) * (1.4 + 1.2 * ramp(t, 55.2, 56.2))
    mr = .05 * ramp(t, 54.95, 55.3) * (1 - mbreak)
    p.update(u_moon=(mdist * math.cos(mang), mdist * math.sin(mang), mr), u_mbreak=mbreak, u_mang=mang, u_mdist=mdist)
    # debris spirals back into the impact point: an explosion played backwards looks like everything uniting
    p['u_dvis'] = ramp(t, 55.7, 55.95) * (1 - ramp(t, B['burst'] - .05, B['burst'] + .05))
    p['u_dphase'] = lin(t, B['conv'], B['burst'])
    hit = (math.cos(GAP_HIT) * R, math.sin(GAP_HIT) * R)
    p['u_hit'] = hit
    x = lin(t, 56.55, B['burst'])
    p['u_ring'] = .55 * (1 - x); p['u_ringA'] = (.2 + .8 * x) if 56.55 < t < B['burst'] else 0.
    k = t - B['burst']
    p['u_flash'] = .9 * math.exp(-(-k) * 7.) if k < 0 else .9 * math.exp(-k * 16.)
    if t < 55.9: p['u_flash'] = 0.
    # Theia pulls out of the notch and leaves
    rt = .075
    wall = R + rt                                          # just touching the surface, outside
    gx, gy = math.cos(GAP_HIT), math.sin(GAP_HIT)
    inx, iny = gx * R * .97, gy * R * .97                  # born at the contact point on the whole sphere
    if k < 0:
        tx, ty, trad, theat = inx, iny, 0., 0.
    else:
        trad = rt * ease(k / .55)
        s = ease((k - .5) / .35)
        tx, ty = inx + (gx * wall - inx) * s, iny + (gy * wall - iny) * s
        dist = .38 * max(k - .85, 0.) ** 1.1
        tx += math.cos(EXIT) * dist; ty += math.sin(EXIT) * dist
        theat = .3 + 1.1 * math.exp(-k * 1.8)
    p.update(u_tpos=(tx, ty), u_trad=trad, u_theat=theat, u_tvel=(math.cos(EXIT), math.sin(EXIT)),
             u_merge=math.exp(-k * 1.5) if k > 0 else 0., u_melt=1.2 * math.exp(-k * .8) if k > 0 else 0.)
    # scan line falls on the second "deeply" and redraws the world as a vector simulation
    p['u_vec'] = 1. if t >= B['deep2'] else 0.
    p['u_scan'] = .53 - 1.08 * outc(lin(t, B['deep2'], B['deep2'] + .66) * .9 + .1 * lin(t, B['deep2'], B['deep2'] + .66))
    p['u_ui_on'] = 1. if t >= B['deep2'] else 0.
    p['u_phos'] = PHOS
    return p


# timing v3 (user): B.C (lower right) holds two seconds longer; the rewound impact is cut shorter to pay for it.
# The structure runs on a warped clock; the era animations (clocks, shadow, smoke) keep real time.
T_TURN, T_BURST2 = 56.1, 57.740


def warp(t):
    if t < 54.42: return t
    if t < T_TURN: return 54.42                                            # hold on B.C
    if t < T_BURST2: return 54.42 + (t - T_TURN) * (B['burst'] - 54.42) / (T_BURST2 - T_TURN)
    if t < B['deep2']: return B['burst'] + (t - T_BURST2) * (B['deep2'] - B['burst']) / (B['deep2'] - T_BURST2)
    return t


def params(t):
    w = warp(t)
    p = _params(w)
    if 54.42 <= t < T_TURN:
        p['u_gap'] = math.radians(gap_deg(54.42) + .9 * math.sin(t * 7.3) + .5 * math.sin(t * 13.1 + 1.))   # fixational drift
    tr = max(min(t, T_TURN + .8) - 51.3, 0.)
    p.update(u_clock=12 * 60 + 47 - tr * 97., u_gear=-tr * 2.4, u_hand=math.radians(262.) - tr * math.radians(24.),
             u_shadow=math.radians(352.) - tr * math.radians(9.), u_reverse=-tr, u_day=lin(t, B['bc'], T_TURN))
    return p


FONT = 'C:/Windows/Fonts/CascadiaMono.ttf'
_blank = {}


def _vproj(P):
    """same camera as vectorView() in scene.glsl"""
    vp, vf, ro = .30, 1.6, (0., 1., -2.6)
    fw = (0., -math.sin(vp), math.cos(vp)); up = (0., math.cos(vp), math.sin(vp))
    v = tuple(a - b for a, b in zip(P, ro)); z = sum(a * b for a, b in zip(v, fw))
    return v[0] / z * vf, sum(a * b for a, b in zip(v, up)) / z * vf


def _vsun():
    vp = .30; fw = (0., -math.sin(vp), math.cos(vp)); ro = (0., 1., -2.6)
    k = -ro[1] / fw[1]; E = tuple(a + b * k for a, b in zip(ro, fw))
    return (E[0] - 2.6, 0., E[2] + 11.)


def ui(t, w, h, hide=()):
    if t < B['deep2']:
        if (w, h) not in _blank: _blank[(w, h)] = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        return {'u_ui': _blank[(w, h)]}
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0)); dr = ImageDraw.Draw(img)
    fs = int(h * .019); f = ImageFont.truetype(FONT, fs); lh = int(fs * 1.45)
    fl = ImageFont.truetype(FONT, int(h * .017))
    p = params(t)
    k = t - B['deep2']
    gyr = 4.5100 + k * .0021
    sep = (math.hypot(p['u_tpos'][0] - p['u_hit'][0], p['u_tpos'][1] - p['u_hit'][1]) / max(p['u_R'], 1e-3))
    blocks = [
        ((.04, .06), 'l', ['SIMULATION 0047', 'GIANT IMPACT   PROTO-EARTH / THEIA', 'PLAYBACK  REWIND ◀◀   x1.0e6', 'FRAME     0047 / 1200']),
        ((.96, .06), 'r', [f'T      −{gyr:.4f} Gyr', 'dt     −1.0e6 yr/s', 'FRAME  HELIOCENTRIC', 'SCALE  1 : 4.2e8']),
        ((.04, .70), 'l', ['M_EARTH    0.90 M_E', 'M_THEIA    0.10 M_E', 'V_REL      9.3 km/s', 'ANGLE      45°',
                          f'SEP        {sep:4.2f} R_E', 'STATUS     APPROACH']),
        ((.96, .21), 'r', ['ORBIT   a 1.00 AU   e 0.017', 'THEIA   L4 CO-ORBITAL', 'ROCHE   2.9 R_E', 'SOL     1.00 AU']),
    ]
    line_no = 0
    for (fx, fy), align, lines in blocks:
        for j, s_ in enumerate(lines):
            y = int(fy * h) + j * lh
            if (1 - y / h) - .5 < p['u_scan']:            # not yet reached by the scan line
                line_no += 1; continue
            line_no += 1
            txt = s_
            x = int(fx * w) - (dr.textlength(s_, font=f) if align == 'r' else 0)
            dr.text((x, y), txt, font=f, fill=(255, 255, 255, 235))
    # labels on the objects
    def to_px(uv): return uv[0] * h + w / 2, h / 2 - uv[1] * h
    cam, zm = p['u_cam'], p['u_zoom']
    R = p['u_R']
    tags = [(((0 - cam[0]) / zm - R * .72 / zm, (0 - cam[1]) / zm + R * .72 / zm), 'PROTO-EARTH', (-1, 1), .08),
            (((p['u_tpos'][0] - cam[0]) / zm, (p['u_tpos'][1] - cam[1]) / zm - p['u_trad'] / zm), 'THEIA', (1, -1), .14),
            (_vproj(_vsun()), 'SOL', (1, 1), .2)]
    for uv, txt, (sx, sy), dl in tags:
        if txt in hide: continue
        x, y = to_px(uv)
        if (1 - y / h) - .5 < p['u_scan']: continue
        a = 1.
        ex, ey = x + sx * 40 * h / 1080, y - sy * 40 * h / 1080
        col = (255, 255, 255, int(235 * a))
        dr.line([(x, y), (ex, ey), (ex + sx * 30 * h / 1080, ey)], fill=col, width=max(1, int(h / 900)))
        tw = dr.textlength(txt, font=fl)
        tx = ex + sx * 36 * h / 1080 - (tw if sx < 0 else 0)
        dr.text((tx, ey - int(h * .012)), txt, font=fl, fill=col)
    return {'u_ui': img}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--w', type=int, default=1920); ap.add_argument('--h', type=int, default=1080)
    ap.add_argument('--sub', type=int, default=4); ap.add_argument('--stills', type=str)
    ap.add_argument('--out', type=str, default=str(HERE / 'preview_1080p.mp4'))
    a = ap.parse_args()
    r = Renderer(a.w, a.h, (HERE / 'scene.glsl').read_text(encoding='utf-8'), subframes=a.sub)
    tex = lambda t: ui(t, a.w, a.h)
    if a.stills:
        (HERE / 'stills').mkdir(exist_ok=True)
        for t in map(float, a.stills.split(',')):
            save_png(r.frame(t, params, tex), a.w, a.h, HERE / 'stills' / f'{t:07.3f}.png'); print('still', t, flush=True)
        return
    fps = 60; n = round((END - START) * fps)
    t0 = time.monotonic()
    def frames():
        for i in range(n):
            if i % 120 == 0: print(f'{i}/{n}  {time.monotonic() - t0:.0f}s', flush=True)
            yield r.frame(START + i / fps, params, tex)
    encode(a.out, a.w, a.h, fps, START, END - START, frames())
    print('done', a.out, f'{time.monotonic() - t0:.0f}s')


if __name__ == '__main__':
    main()
