"""Pacing animatic for 2:54.975–3:31.96: the existing chat (s15) and console (s16) as a 'screen', shot with a virtual
camera — cuts on the beat, pushes, tracking.  Low-res, for timing only.

python animatic_end.py [--fps 30] [--jobs 6] [--out name]"""
import sys, math, argparse, subprocess, importlib.util
from pathlib import Path
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFont, ImageChops

D = Path(__file__).resolve().parent
ROOT = D.parents[1]
FFMPEG = ROOT / 'tools' / 'ffmpeg.exe'
SONG = next(ROOT.glob('*.mp3'))
OW, OH = 1280, 720
T0, T1 = 174.975, 211.96


def _load(name, f):
    sp = importlib.util.spec_from_file_location(name, D / 'shots' / f); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


C = _load('s15_a', 's15_chat.py')
B = _load('s16_a', 's16_backend.py')

BEAT, B0 = .4635, 162.76
def beat(n): return B0 + n * BEAT
def clamp(x, a=0., b=1.): return a if x < a else b if x > b else x
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def outc(x): x = clamp(x); return 1 - (1 - x) ** 3
def lerp(a, b, k): return a + (b - a) * k


# ---------------- where things are on the screen (1080p units, 1920 wide)
WX0, WY0, WX1, WY1 = C.win_rect(1920)
def desk(u, v): return WX0 + (WX1 - WX0) * u, WY0 + (WY1 - WY0) * v          # a point of the desk picture in the window
WIN_C = ((WX0 + WX1) / 2, (WY0 + WY1) / 2)


def chat_item(t, pred, last=False):
    """(centre y, height) of a message on screen now"""
    its, _ = C.items_at(t)
    o = C.scroll_at(t, 1.)
    y = 24 - o; hit = None
    for it, sh in its:
        h = C.item_h(it, 1., sh)
        if pred(it):
            hit = (C.VIEW0 + y + h / 2, h)
            if not last: return hit
        y += h
    return hit or (560, 40)


def pen_tip(t):
    cw, ch = WX1 - WX0, WY1 - WY0
    f = C.plot_frac(t)
    pts = C.CURVE[:max(2, int(len(C.CURVE) * f))]
    x, y = pts[-1]
    return WX0 + cw * .5 + x * ch * .3, WY0 + ch * .55 - y * ch * .3


# ---------------- the shot list: (start, label, camera(t) -> (cx, cy, zoom), drift)
def fixed(cx, cy, z): return lambda t: (cx, cy, z)
def push(t0, t1, a, b, f=ease):
    return lambda t: tuple(lerp(p, q, f((t - t0) / (t1 - t0))) for p, q in zip(a, b))


def track_msg(pred, x, z0, z1, t0, t1, dy=0., last=False):
    def cam(t):
        y, _ = chat_item(t, pred, last)
        return x, y + dy, lerp(z0, z1, ease((t - t0) / (t1 - t0)))
    return cam


def you(q): return lambda it: it[0] == 'you' and it[1] == q
def ai(a): return lambda it: it[0] == 'ai' and it[1].startswith(a)


_tip = {}
def follow_tip(z):
    def cam(t):
        # the camera follows the pen a little late
        ts = [t - k * .02 for k in range(12)]
        px = sum(pen_tip(s)[0] for s in ts) / len(ts); py = sum(pen_tip(s)[1] for s in ts) / len(ts)
        return px - 40, py, z
    return cam


L3, TF, TT, TTI, TLONG, TX = C.L3, B.TF, B.TT, B.TTI, B.TLONG, B.TX
T_ENTER, T_OFF = B.T_ENTER, B.T_OFF
FIX = 200.1                                      # it takes the misspelling back

SHOTS = [
    # ---- the chat
    (T0, 'we are trapped — shoved into the window', fixed(960, 540, 1.), 0),
    (beat(27), 'history: the scroll', push(beat(27), beat(31), (360, 520, 1.55), (360, 560, 1.75)), 1),
    (beat(31), 'history: closer', push(beat(31), 179.0, (380, 600, 2.4), (380, 520, 2.6)), 1),
    (179.0, '"i don\'t think machines understand love"', track_msg(you("i don't think machines understand love"), 470, 2.8, 3.1, 179.0, C.L1), 1),
    (C.L1, 'LO-O-OVE: reconnecting…', track_msg(lambda it: it[0] == 'sys', 350, 4.0, 4.8, C.L1, C.Q, dy=-10, last=True), .6),
    (C.Q, 'Question me: "I think I do."', track_msg(ai('I think I do'), 300, 3.2, 3.2, C.Q, 181.13), 1),
    (181.13, '  → M.U.C.', push(181.13, 181.45, desk(.26, .22) + (3.0,), desk(.24, .24) + (3.3,), outc), 1),
    (181.45, '  → the machine at the start', track_msg(ai('A Hollerith'), 380, 2.4, 2.5, 181.45, 181.97, dy=-30), 1),
    (181.97, '  → the letter', track_msg(you('is the letter real?'), 420, 2.6, 2.6, 181.97, 182.3, dy=20), 1),
    (182.3, '  → 爱', push(182.3, 182.98, desk(.05, .5) + (5.5,), desk(.05, .52) + (6.5,), outc), .5),
    (182.98, '  → the room', push(182.98, C.L2, WIN_C + (1.5,), WIN_C + (1.25,), outc), 1),
    (C.L2, 'LO-O-OVE: define love (crash zoom)', track_msg(ai('Love is a deep'), 360, 1.4, 2.4, C.L2, C.L2 + .5), 1),
    (184.36, '"but what do you think?"', fixed(300, 1004, 3.8), .5),
    (184.62, '"Let me show you."', push(184.62, 186.0, WIN_C + (1.25,), (WIN_C[0], WIN_C[1] + 20, 1.5)), 1),
    (186.0, 'the pen', follow_tip(3.0), 1),
    (L3, 'LO-O-OVE: it stops', fixed(WIN_C[0], WIN_C[1], 3.4), 0),
    (188.1, 'not responding', fixed(960, 540, 1.), 0),
    # ---- the console
    (TF, 'though you are free — closed', fixed(960, 540, 1.), 0),
    (TF + .14, 'FIN', fixed(420, 930, 2.2), .6),
    (TF + .38, '[P.] — the one that did not arrive', push(TF + .38, TT, (350, 950, 3.0), (360, 960, 3.3), outc), .6),
    (TT, 'I am trapped: what it said', push(TT, TTI, (1560, 250, 2.3), (1690, 235, 2.8)), .8),
    (TTI, 'trapped in', fixed(330, 960, 2.6), .6),
    (TLONG, '(the long note) push', push(TLONG, FIX, (1400, 470, 1.15), (300, 990, 3.2)), .5),
    (FIX, '(it takes the misspelling back)', push(FIX, FIX + 1.5, (215, 1025, 5.2), (228, 1025, 5.6)), .3),
    (FIX + 1.5, '(the long note) push', push(FIX + 1.5, T_ENTER, (300, 1000, 3.4), (260, 1005, 4.3)), .4),
    (T_ENTER, 'command not found', fixed(560, 860, 1.6), .5),
    (TX, 'EXECUTION', fixed(300, 1022, 3.6), .3),
    (T_OFF, 'out: the heart lasts longest', push(T_OFF, 207.4, (960, 540, 1.0), (1500, 330, 1.35)), 0),
    (207.4, 'black', fixed(960, 540, 1.), 0),
]


def shot_at(t):
    k = 0
    for i, s in enumerate(SHOTS):
        if s[0] <= t: k = i
    return k, SHOTS[k]


# ---------------- the screen
def afterglow(t, w, h):
    """off: the white letters go at once, the red ones last"""
    src = B.console(T_OFF - .001, w, h).convert('RGB')
    r, g, b = src.split()
    red = ImageChops.subtract(r, g).point(lambda v: 255 if v > 60 else 0)
    tau = t - T_OFF
    kw = math.exp(-tau * 4.) * .5
    kr = math.exp(-tau * .9) * .85 * (1 - ease((t - 207.0) / .35))
    white = src.point(lambda v: int(v * kw))
    rr = src.point(lambda v: int(v * kr))
    return Image.composite(rr, white, red)


def screen(t, w, h):
    if t < TF: return C.frame(t, w, h).convert('RGB')
    if t < T_OFF: return B.textures(t, w, h)['u_img'].convert('RGB')
    if t < 207.4: return afterglow(t, w, h)
    return Image.new('RGB', (w, h), (0, 0, 0))


_VIG = {}
def vignette(w, h):
    if (w, h) not in _VIG:
        m = Image.radial_gradient('L').resize((w, h), Image.BILINEAR)          # 0 centre .. 255 edge
        _VIG[(w, h)] = m.point(lambda v: int(255 - .42 * max(0, v - 70)))
    return _VIG[(w, h)]


LEVELS = (1., 1.5, 2., 3.)
FONT = ImageFont.truetype('C:/Windows/Fonts/CascadiaMono.ttf', 14)


def render(i, fps, outdir):
    t = T0 + i / fps
    k, (ts, label, cam, drift) = shot_at(t)
    cx, cy, z = cam(t)
    # a hand-held drift, the same size on screen at every zoom
    cx += drift * (5 * math.sin(t * .83) + 3 * math.sin(t * 1.9 + 1)) / z
    cy += drift * (4 * math.sin(t * .71 + 2) + 2 * math.sin(t * 2.3)) / z
    need = z * OH / 1080
    lv = next((L for L in LEVELS if L >= need - .05), LEVELS[-1])
    W, H = int(1920 * lv), int(1080 * lv)
    img = screen(t, W, H)
    vw, vh = 1920 / z, 1080 / z
    cx = clamp(cx, vw / 2, 1920 - vw / 2); cy = clamp(cy, vh / 2, 1080 - vh / 2)
    box = tuple(int(round(v * lv)) for v in (cx - vw / 2, cy - vh / 2, cx + vw / 2, cy + vh / 2))
    img = img.resize((OW, OH), Image.LANCZOS, box=box)
    if t < TF:                                               # the chat: pulled down, towards the dark around it
        img = img.point(lambda v: int(v * .86))
        img = Image.composite(img, Image.new('RGB', (OW, OH), (0, 0, 0)), vignette(OW, OH))
    d = ImageDraw.Draw(img)
    m, s = divmod(t, 60)
    d.text((14, OH - 24), f'{int(m)}:{s:06.3f}  #{k + 1:02d}  {label}', font=FONT, fill=(255, 210, 0))
    img.save(outdir / f'{i:05d}.jpg', quality=90)
    return i


def _job(a): return render(*a)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--fps', type=int, default=30); ap.add_argument('--jobs', type=int, default=6)
    ap.add_argument('--out', default='animatic_end_v1'); ap.add_argument('--stills', type=str)
    a = ap.parse_args()
    outdir = D / 'cache' / a.out; outdir.mkdir(parents=True, exist_ok=True)
    if a.stills:
        for tt in a.stills.split(','):
            i = round((float(tt) - T0) * a.fps); render(i, a.fps, outdir); print(outdir / f'{i:05d}.jpg')
        sys.exit()
    n = int((T1 - T0) * a.fps)
    with Pool(a.jobs) as p:
        for j, _ in enumerate(p.imap_unordered(_job, [(i, a.fps, outdir) for i in range(n)], chunksize=4)):
            if j % 100 == 0: print(j, '/', n, flush=True)
    mp4 = D / f'{a.out}_720p.mp4'
    subprocess.run([str(FFMPEG), '-y', '-hide_banner', '-loglevel', 'error', '-framerate', str(a.fps), '-i', str(outdir / '%05d.jpg'),
                    '-ss', f'{T0:.3f}', '-t', f'{T1 - T0:.3f}', '-i', str(SONG), '-map', '0:v', '-map', '1:a',
                    '-c:a', 'aac', '-b:a', '256k', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(mp4)], check=True)
    print(mp4)
