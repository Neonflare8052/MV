"""Hands, sleeves and the file cabinet, seen from straight above, lit by the desk lamp.  (for s14e_desk)

Everything is built in world metres and drawn onto a supersampled RGBA layer.  Volume comes from a height map:
each part (palm, finger segment, sleeve) is a mask whose distance-to-edge is turned into a rounded height, the parts
are merged by max (so there are grooves between fingers), normals come from its gradient and are lit from the lamp."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SKIN = np.array([200, 156, 132], float) / 255
NAIL = np.array([222, 186, 172], float) / 255
JACKET = np.array([46, 44, 46], float) / 255
SHIRT = np.array([226, 222, 212], float) / 255


def _cap(a, b, ra, rb, n=12):
    """a tapered capsule from a (radius ra) to b (radius rb)"""
    dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1e-6
    ang = math.atan2(dy, dx)
    pts = []
    for i in range(n + 1):
        th = ang - math.pi / 2 + math.pi * i / n
        pts.append((b[0] + rb * math.cos(th), b[1] + rb * math.sin(th)))
    for i in range(n + 1):
        th = ang + math.pi / 2 + math.pi * i / n
        pts.append((a[0] + ra * math.cos(th), a[1] + ra * math.sin(th)))
    return pts


# ---------------- the hand's skeleton
# per finger: knuckle (u, v·side), segment lengths, radii at base and tip
FINGERS = [((.094, .029), (.040, .025, .021), (.0098, .0080)),      # index (nearest the thumb)
           ((.097, .0095), (.046, .028, .022), (.0100, .0082)),     # middle
           ((.093, -.0095), (.043, .026, .021), (.0095, .0078)),    # ring
           ((.083, -.028), (.033, .020, .019), (.0085, .0070))]     # little
POSES = {  # joint flexion (rad) per finger (three joints), finger spread (rad), thumb (angle out, flexion)
    'flat':  ([(0.05, .05, .02)] * 4, .07, (.75, .1)),
    'point': ([(0.0, .0, .0), (1.25, 1.5, .9), (1.3, 1.5, .9), (1.3, 1.5, .9)], .03, (.35, .5)),
    'pinch': ([(.35, .35, .2), (.4, .4, .2), (.45, .45, .25), (.5, .45, .25)], .02, (.2, .9)),
    'grip':  ([(.9, 1.2, .8)] * 4, .0, (.3, 1.0)),
}


def hand_parts(wrist, ang, pose, side):
    """list of (polygons, kind, radius, extra) in world metres.  A finger is one part made of its segments' capsules."""
    f = (math.cos(ang), math.sin(ang)); r = (-math.sin(ang), math.cos(ang))
    sg = 1 if side == 'L' else -1                    # thumb's side along v
    P = lambda u, v: (wrist[0] + f[0] * u + r[0] * v, wrist[1] + f[1] * u + r[1] * v)
    flex, spread, (tha, thf) = POSES[pose]
    parts = []
    palm = [P(-.006, -sg * .026), P(.03, -sg * .039), P(.08, -sg * .037), P(.094, -sg * .02), P(.098, sg * .006),
            P(.095, sg * .028), P(.072, sg * .04), P(.045, sg * .044), P(.014, sg * .036), P(-.006, sg * .027)]
    # the thumb, joined to the palm
    ta = ang + sg * tha
    t0 = P(.022, sg * .03)
    L1, L2 = .04 * math.cos(min(thf * .5, 1.3)), .032 * math.cos(min(thf, 1.4))
    t1 = (t0[0] + math.cos(ta) * L1, t0[1] + math.sin(ta) * L1)
    t2 = (t1[0] + math.cos(ta - sg * .25) * L2, t1[1] + math.sin(ta - sg * .25) * L2)
    thumb = [_cap(t0, t1, .0145, .0118)] + ([_cap(t1, t2, .0118, .0102)] if L2 > .006 else [])
    parts.append(([palm], 'palm', .017, []))
    parts.append((thumb, 'finger', .0125, [(t1, ta, .0118)]))
    knuck = []
    for k, ((u0, v0), Ls, (ra, rb)) in enumerate(FINGERS):
        base = P(u0 - .004, sg * v0)
        knuck.append(P(u0 - .006, sg * v0))
        a = ang + sg * spread * (1.5 - k) * -1
        cum = 0.; p = base; rr = ra
        caps, joints, nail = [], [], None
        for j, L in enumerate(Ls):
            cum += flex[k][j]
            if cum > math.pi / 2 + .2: break                   # folded under: hidden
            pl = L * math.cos(min(cum, math.pi / 2))
            q = (p[0] + math.cos(a) * pl, p[1] + math.sin(a) * pl)
            r1 = ra + (rb - ra) * (j + 1) / 3
            caps.append(_cap(p, q, rr, r1))
            if j < 2: joints.append((q, a, r1))
            if j == 2 and cum < 1.0:
                nl = .0115 * math.cos(cum)
                c0 = (q[0] - math.cos(a) * (nl + .0015), q[1] - math.sin(a) * (nl + .0015))
                nail = _cap(c0, (q[0] - math.cos(a) * .0022, q[1] - math.sin(a) * .0022), r1 * .72, r1 * .7)
            p, rr = q, r1
        parts.append((caps, 'finger', ra, joints))
        if nail: parts.append(([nail], 'nail', ra * .4, []))
    return parts, knuck


def sleeve_parts(shoulder, wrist, ang):
    """jacket sleeve from the shoulder to just short of the wrist; a shirt cuff showing below it"""
    dx, dy = wrist[0] - shoulder[0], wrist[1] - shoulder[1]; L = math.hypot(dx, dy) or 1e-6
    ux, uy = dx / L, dy / L; nx, ny = -uy, ux
    cuff_end = (wrist[0] - ux * .004, wrist[1] - uy * .004)
    jk_end = (wrist[0] - ux * .03, wrist[1] - uy * .03)
    jacket = [(shoulder[0] + nx * .068, shoulder[1] + ny * .068), (jk_end[0] + nx * .047, jk_end[1] + ny * .047),
              (jk_end[0] - nx * .047, jk_end[1] - ny * .047), (shoulder[0] - nx * .068, shoulder[1] - ny * .068)]
    cuff = [(jk_end[0] + ux * .006 + nx * .036, jk_end[1] + uy * .006 + ny * .036), (cuff_end[0] + nx * .032, cuff_end[1] + ny * .032),
            (cuff_end[0] - nx * .032, cuff_end[1] - ny * .032), (jk_end[0] + ux * .006 - nx * .036, jk_end[1] + uy * .006 - ny * .036)]
    return [([cuff], 'cuff', .03, []), ([jacket], 'jacket', .05, [])], (ux, uy, nx, ny, jk_end)


def _box(a, r):
    """box blur of radius r along both axes (cumulative sums)"""
    r = int(max(1, r))
    for ax in (0, 1):
        c = np.cumsum(np.pad(a, [(r + 1, r) if i == ax else (0, 0) for i in range(2)], mode='edge'), axis=ax)
        a = (np.take(c, range(2 * r + 1, c.shape[ax]), axis=ax) - np.take(c, range(0, c.shape[ax] - 2 * r - 1), axis=ax)) / (2 * r + 1)
    return a


def blur(a, s):
    """~gaussian: three box passes"""
    r = max(1, int(round(s * .9)))
    for _ in range(3): a = _box(a, r)
    return a


def _height(mask, rpx, flat=0.):
    """rounded height from a mask: blurred mask read as a dome, radius ~ rpx at the edge"""
    b = blur(mask.astype(float), max(1., rpx * .45))
    k = np.clip((b - .5) * 2, 0, 1)
    return np.sqrt(k) * rpx


def draw_arm(img, P, pxm, shoulder, wrist, ang, pose, side, lamp3, seed=0):
    """draw one arm onto img (RGBA, px).  P: world -> px.  pxm: px per metre.  lamp3: (x, y, height) of the lamp, metres."""
    hparts, knuck = hand_parts(wrist, ang, pose, side)
    sparts, (ux, uy, nx, ny, jk_end) = sleeve_parts(shoulder, wrist, ang)
    allp = sparts + hparts
    pts = [P(x, y) for pls, _, _, _ in allp for pl in pls for x, y in pl]
    pad = 8
    x0 = int(max(0, min(p[0] for p in pts) - pad)); y0 = int(max(0, min(p[1] for p in pts) - pad))
    x1 = int(min(img.width, max(p[0] for p in pts) + pad)); y1 = int(min(img.height, max(p[1] for p in pts) + pad))
    if x1 - x0 < 3 or y1 - y0 < 3: return
    W, H = x1 - x0, y1 - y0
    Hmap = np.zeros((H, W)); alb = np.zeros((H, W, 3)); cover = np.zeros((H, W), bool)
    sheen = np.zeros((H, W)); flush = np.zeros((H, W))
    Q = lambda x, y: (P(x, y)[0] - x0, P(x, y)[1] - y0)
    for pls, kind, rad, extra in allp:
        m = Image.new('L', (W, H), 0); md = ImageDraw.Draw(m)
        for pl in pls: md.polygon([Q(x, y) for x, y in pl], fill=255)
        M = np.asarray(m) > 127
        if not M.any(): continue
        rpx = max(1.5, rad * pxm)
        h = _height(M, rpx)
        base = {'jacket': .06, 'cuff': .058, 'palm': .07, 'finger': .074, 'nail': 0.}[kind] * pxm
        if kind == 'nail':
            hh = Hmap + .0012 * pxm * np.sqrt(np.clip(h / rpx, 0, 1))
            Hmap = np.where(M, hh, Hmap)
        else:
            Hmap = np.where(M, h + base, Hmap)
        col = {'jacket': JACKET, 'cuff': SHIRT, 'palm': SKIN, 'finger': SKIN, 'nail': NAIL}[kind]
        alb[M] = col
        sheen[M] = {'jacket': .05, 'cuff': .04, 'palm': .07, 'finger': .08, 'nail': .35}[kind]
        cover |= M
        if kind == 'finger':                                             # creases at the joints; the tips a little redder
            for (q, a, r1) in extra:
                cx, cy = Q(*q); rr = r1 * pxm * 1.05
                ex, ey = -math.sin(a) * rr, math.cos(a) * rr
                cm = Image.new('L', (W, H), 0)
                ImageDraw.Draw(cm).line([(cx - ex, cy - ey), (cx + ex, cy + ey)], fill=255, width=max(1, int(.0012 * pxm)))
                Hmap -= (np.asarray(cm) / 255.) * .0016 * pxm
    # knuckles: small rises at the finger roots
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    for kx, ky in knuck:
        cx, cy = Q(kx, ky)
        Hmap += np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * (.006 * pxm) ** 2)) * .004 * pxm * (alb == SKIN).all(-1)
    # fabric folds on the jacket
    r = random.Random(seed)
    wx, wy = (xx + x0), (yy + y0)
    along = (wx * ux + wy * uy) / pxm; across = (wx * nx + wy * ny) / pxm
    fold = np.zeros((H, W))
    for i in range(5):
        c = r.uniform(-.4, .1); fr = r.uniform(25, 45); ph = r.uniform(0, 6)
        fold += np.exp(-((along - c - .02 * np.sin(across * 60 + ph)) * fr * 3) ** 2) * r.uniform(.4, 1.)
    jk = (alb == JACKET).all(-1)
    Hmap -= np.where(jk, fold * .006 * pxm, 0.)
    # normals and light
    gy, gx = np.gradient(blur(Hmap, max(1.2, .0012 * pxm)))
    N = np.dstack([-gx, -gy, np.ones_like(gx)])
    N /= np.linalg.norm(N, axis=-1, keepdims=True)
    L = np.array([lamp3[0] - wrist[0], lamp3[1] - wrist[1], lamp3[2]]); L /= np.linalg.norm(L)
    ndl = np.clip(N @ L, 0, 1)
    Hv = (L + np.array([0, 0, 1.])); Hv /= np.linalg.norm(Hv)
    spec = np.clip(N @ Hv, 0, 1) ** 14
    ao = np.clip(1 - (blur(Hmap, max(3, .006 * pxm)) - Hmap) / (.012 * pxm), .6, 1)
    wrap = (ndl + .35) / 1.35                                           # skin: light wraps round a little
    skin = (alb == SKIN).all(-1) | (alb == NAIL).all(-1)
    lam = np.where(skin, wrap, ndl)
    shade = (.38 + .72 * lam) * ao
    rgb = alb * shade[..., None] + (sheen * spec)[..., None] * .5
    rgb[skin] += np.array([.06, .0, -.02]) * (1 - ndl[skin])[..., None]  # a warmer, redder shadow side
    noise = blur(np.random.RandomState(seed).rand(H, W), 1.5) - .5
    rgb += noise[..., None] * np.where(jk, .05, .03)[..., None]
    rgb = np.clip(rgb, 0, 1)
    a = blur(cover.astype(float), .6)
    out = np.dstack([rgb * 255, a * 255]).astype(np.uint8)
    img.alpha_composite(Image.fromarray(out, 'RGBA'), (x0, y0))


# ---------------- the file cabinet: an open box of six compartments; folders leaning back like shingles
def _wood(W, H, seed, base=(112, 80, 54)):
    rs = np.random.RandomState(seed)
    n = blur(rs.rand(H, W), 1.) - .5
    g = blur(rs.rand(H, 1) * np.ones((1, W)), 1.)                  # grain: streaks along the boards
    g = g + .25 * (blur(rs.rand(H, W // 30 + 2), 1.)[:, (np.arange(W) // 30)] - .5)
    return np.array(base, float)[None, None, :] * (.8 + .35 * g[..., None] + .12 * n[..., None])


def cabinet(img, P, pxm, box, t_pull, lamp3, taken=2, font=None, labels=None):
    """drawn, not modelled: flat tones, chalk outlines.  Six wells; folders leaning back, each a strip of its face with a tab."""
    x0, y0, x1, y1 = box
    m = lambda v: v * pxm
    CH = (232, 227, 214, 255)
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    (X0, Y0), (X1, Y1) = P(x0, y0), P(x1, y1)
    lw = max(1, int(m(.0022)))
    d.rectangle([X0 + m(.02), Y0 + m(.03), X1 + m(.03), Y1 + m(.04)], fill=(0, 0, 0, 90))              # a flat shadow
    d.rectangle([X0, Y0, X1, Y1], fill=(88, 64, 46, 255), outline=CH, width=lw)
    rim, div = .022, .012
    n = 6; hh = (y1 - y0 - rim) / n
    r = random.Random(3)
    comps = []
    for i in range(n):
        cy0 = y0 + rim + i * hh; cy1 = cy0 + hh - div
        comps.append((cy0, cy1))
        (a0, b0), (a1, b1) = P(x0 + rim, cy0), P(x1 - rim, cy1)
        d.rectangle([a0, b0, a1, b1], fill=(30, 24, 20, 255), outline=CH, width=max(1, lw - 1))
        k = r.randint(7, 10)
        base = [b1 - 3 - j * (b1 - b0 - m(.03)) / (k - 1) for j in range(k)][::-1]
        for j, by in enumerate(base):
            if i == taken and j == k // 2 and t_pull > 0: continue
            top = max(b0 + 2, by - m(r.uniform(.035, .055)))
            tone = r.choice([1., .92, .86])
            xl, xr = a0 + m(.006), a1 - m(.006 + r.uniform(0, .008))
            d.rectangle([xl, top, xr, by], fill=tuple(int(c * tone) for c in (200, 178, 134)) + (255,))
            d.line([(xl, top), (xr, top)], fill=CH, width=max(1, lw - 1))
            tw = m(.06); tx = xl + r.choice([.05, .38, .7]) * (xr - xl - tw)
            d.rectangle([tx, top - m(.011), tx + tw, top], fill=(214, 192, 146, 255), outline=CH, width=1)
            if font and labels and m(.0065) >= 5:
                lab = labels(i, j, k)
                if lab: d.text((tx + tw / 2, top - m(.0055)), lab, font=font(int(m(.0065))), fill=(40, 34, 28, 255), anchor='mm')
        # the label holder facing the desk
        lx, ly = P(x0 + .002, (cy0 + cy1) / 2)
        d.rectangle([lx, ly - m(.026), lx + m(.018), ly + m(.026)], fill=(236, 230, 214, 255), outline=CH, width=1)
    img.alpha_composite(lay)
    if font and m(.012) >= 6:
        for i, (cy0, cy1) in enumerate(comps):
            lx, ly = P(x0 + .002, (cy0 + cy1) / 2)
            lab = Image.new('RGBA', (int(m(.052)), int(m(.018))), (0, 0, 0, 0))
            ImageDraw.Draw(lab).text((m(.026), m(.009)), 'C-%d' % (i + 1), font=font(int(m(.011))), fill=(30, 26, 22, 255), anchor='mm')
            lab = lab.rotate(90, expand=True)
            img.alpha_composite(lab, (int(lx), int(ly - lab.height / 2)))
    return comps


def folder_out(img, P, pxm, c, tilt, font, label=('C-3', 'M.U.C.', 'love letters')):
    """the folder: seen edge-on (tilt 0) to face-up (tilt 1); c its centre (world)"""
    d = ImageDraw.Draw(img)
    w2, h2 = .115, .155 * max(.03, tilt)
    (a, b), (cc, e) = P(c[0] - w2, c[1] - h2), P(c[0] + w2, c[1] + h2)
    sh = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([a + .02 * pxm, b + .03 * pxm, cc + .02 * pxm, e + .03 * pxm], fill=(0, 0, 0, 120))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(max(2, .015 * pxm))))
    d.rectangle([a, b, cc, e], fill=(212, 190, 146, 255), outline=(150, 128, 92, 255), width=max(1, int(.0015 * pxm)))
    if tilt > .6:
        tb = b - .018 * pxm
        d.rectangle([a + .02 * pxm, tb, a + .09 * pxm, b + 1], fill=(218, 196, 152, 255), outline=(150, 128, 92, 255))
        f1, f2, f3 = font(int(.028 * pxm)), font(int(.02 * pxm)), font(int(.015 * pxm))
        d.text(((a + cc) / 2, b + .045 * pxm), label[0], font=f1, fill=(52, 40, 30, 255), anchor='mm')
        d.text(((a + cc) / 2, b + .085 * pxm), label[1], font=f2, fill=(52, 40, 30, 255), anchor='mm')
        d.text(((a + cc) / 2, b + .112 * pxm), label[2], font=f3, fill=(70, 56, 42, 230), anchor='mm')
