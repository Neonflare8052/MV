"""t07 · 0:29.709–0:44.452  the logic world (sample; would replace s03 up to "Switch my current").

AI's antiquity: an immaterial world where everything exists because it has been defined or derived. Nothing has
material, light or optics; lines are ideal, points have no size. The machine is a tool and does one thing:
from a premise it derives a conclusion. Every line of the lyric is a conditional, If P then Q, and every one closes ∎.
The system looks complete (before its own Gödel); the ledger on the left is the proof it writes, kept for 2:05.

  29.709 If I'm a set of points   s02's flat field is declared a set; it thins to a lattice. you: a point off the plane
  31.116 give you my              you ∉ span(me): the perpendicular from you to the plane
  32.682 DIMENSION                the plane grows layers up through you; three axes through you    ∎
  33.412 If I'm a circle          every point goes to distance r from you; the eye turns straight down
  34.646 give you my              a marker measures the circumference, s = rθ
  36.287 CIRCUMFERENCE            the circle rolls out flat: a segment of length 2πr                ∎
  37.067 If I'm a sine wave       the (still defined) circle goes to the start; its turning point draws sin x along the segment
  38.596 sit on all my            the tangent field; you leaves the centre for a crest
  40.049 TANGENTS                 you on the crest; the level tangent there runs across the frame  ∎
  40.706 If I approach infinity   x is compressed so infinity is a line on screen; the wave decays; you goes to (∞, 0)
  42.346 you can be my            the boundary x = ∞; ε-band and N
  43.507 LIMITATIONS              ε → 0; the band closes onto you; the boundary lights            ∎
"""
import math, random
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

T0, T_END = 29.709, 44.452
T_PTS, T_GIVE1, T_DIM = 29.709, 31.116, 32.682
T_CIR, T_GIVE2, T_CIRC = 33.412, 34.646, 36.287
T_SIN, T_SIT, T_TAN = 37.067, 38.596, 40.049
T_INF, T_BE, T_LIM = 40.706, 42.346, 43.507

T_AC, T_DC, T_OUT = 44.452, 45.85, 47.0
POST = dict(u_bloom=.18, u_ca=0., u_grain=.014)
SRC = r'''#version 330
uniform vec2 u_res; uniform float u_weight, u_time;
uniform sampler2D u_img;
uniform float u_jit, u_base, u_sig, u_reach, u_spread, u_harm, u_sq, u_data, u_block, u_wave, u_edge;
out vec4 fragColor;
#define PI 3.14159265
#define TAU 6.28318531
const float G=.034, AH=.26;
float PX;
float h12(vec2 p){ vec3 p3=fract(vec3(p.xyx)*.1031); p3+=dot(p3,p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }
float fill(float d){ return 1.-smoothstep(-PX,PX,d); }
float stroke(float d, float w){ return 1.-smoothstep(w-PX,w+PX,abs(d)); }
float lineAA(float d){ return 1.-smoothstep(PX*.6,PX*1.8,d); }
// one row of the proof as a signal: a sine (AC), odd harmonics added (Fourier); 8 cells a period, rows offset by whole cells
float off(float j){ return mod(j*3.,8.); }
float smoothSig(float cx, float j){
  float x=TAU*(cx+off(j))/8., s=0.;
  for(int k=0;k<11;k++){ float n=float(2*k+1); if(n>u_harm+.5) break; s+=sin(n*x)/n; }   // (the picture uses the same sum)
  return s*mix(1.,4./PI,clamp((u_harm-1.)/4.,0.,1.));
}
float sqLevel(float cell, float j){ return fract((cell+.5+off(j))/8.)<.5?1.:-1.; }
float level(vec2 id){                                   // the regular square; cell by cell it switches to the data
  float on=step(.55,h12(id))*2.-1.;
  return h12(id+7.7)<u_data?on:sqLevel(id.x,id.y);
}
void main(){
  vec2 p=(gl_FragCoord.xy-.5*u_res)/u_res.y;
  PX=1./u_res.y;
  vec3 col=vec3(.0035,.0037,.0042)*u_base;
  vec2 q=p+vec2(u_time*.22,0.);
  q.x+=u_jit*(.012*sin(floor(q.y/G)*1.7+u_time*41.)+.006*sin(floor(q.y/G)*5.3-u_time*67.));   // AC: rows slip
  vec2 id=floor(q/G), f=fract(q/G)-.5;
  float r=h12(id);
  float inside=smoothstep(.43,.41,p.x);
  if(u_sig>0.){
    float j=id.y;
    float led=step(-3.5,j)*step(j,8.5);                 // the twelve rows the proof was written on
    float rowA=max(led,clamp(u_spread*22.-abs(j-2.5)+1.,0.,1.))*u_sig;
    float reach=smoothstep(u_reach,u_reach-.04,p.x);
    float d;
    if(u_sq<.5){
      float cx=q.x/G-.5, e=.02;
      float y=smoothSig(cx,j)*AH, y2=smoothSig(cx+e,j)*AH;
      d=abs(f.y-y)*G/sqrt(1.+pow((y2-y)/e,2.));
    } else {
      float L=level(id)*AH, Lp=level(id-vec2(1.,0.))*AH;
      d=abs(f.y-L)*G;
      if(abs(L-Lp)>.01){ float vx=abs(f.x+.5)*G; float vy=max(0.,abs(f.y-(L+Lp)*.5)-abs(L-Lp)*.5)*G; d=min(d,length(vec2(vx,vy))); }
    }
    col+=vec3(.92,.92,.9)*lineAA(d)*rowA*reach*u_wave*mix(.22,1.,inside)*.9;
  }
  if(u_block>0.){                                       // high cells fill from the top: t01's blocks, identical
    vec2 bx=abs(f)-vec2(.36,.26);
    float bd=(length(max(bx,0.))+min(max(bx.x,bx.y),0.)-.06)*G;
    float top=step(.26-.62*u_block,f.y+.06);
    float on=step(.55,r)*(.25+.75*step(.93,h12(id+floor(u_time*3.))))*mix(.05,.55,inside);
    vec3 cu=vec3(.85,.52,.26), wh=vec3(.9,.88,.84);
    col+=mix(wh*.8,cu,step(.85,r))*on*fill(bd)*.7*top;
  }
  col+=vec3(1.)*stroke(p.x-.42,.001)*1.4*u_edge;      // the window boundary (it was x = infinity)
  vec4 c=texture(u_img,gl_FragCoord.xy/u_res);
  col+=pow(c.rgb,vec3(2.2))*1.6;
  fragColor=vec4(col*u_weight,1.);
}
'''


def harmonics(t):
    k = clamp((t - 45.05) / (T_DC - .1 - 45.05))
    return 1. + 2. * math.floor(10 * k ** 1.3 + 1e-9)


T_SQ = T_DC + .1                                          # the last ringing dies: square


def params(t):
    on = 1. if t >= T_DC else 0.
    return dict(
        u_sig=on, u_reach=2., u_spread=1., u_harm=harmonics(t), u_sq=1. if t >= T_SQ else 0.,
        u_data=ease((t - T_SQ) / .3), u_block=ease((t - 46.1) / .3), u_wave=1. - ease((t - 46.32) / .35),
        u_edge=on, u_jit=0., u_base=1. - ease((t - 46.2) / .5),
    )


# ---- small helpers -------------------------------------------------------------------------------------------
def clamp(x, a=0., b=1.): return a if x < a else b if x > b else x
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def outc(x): x = clamp(x); return 1 - (1 - x) ** 3
def inc(x): x = clamp(x); return x ** 3
def lerp(a, b, k): return a + (b - a) * k
def vease(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)
def voutc(x): x = np.clip(x, 0, 1); return 1 - (1 - x) ** 3
def win(t, a, b): return clamp((t - a) / (b - a))
def flash(t, t0, k=6.): return math.exp(-(t - t0) * k) if t >= t0 else 0.


WHITE = (236, 236, 232)
GRAY = (128, 131, 138)
DIM = (74, 77, 84)
ACC = (112, 206, 255)          # the one system colour: evaluation, ∎
FONTS = 'C:/Windows/Fonts/'
SS = 3                          # supersampling


class Cv:
    _F = {}

    def __init__(s, w, h):
        s.w, s.h = w, h; s.k = SS * h / 1080
        s.img = Image.new('RGB', (w * SS, h * SS), (0, 0, 0)); s.d = ImageDraw.Draw(s.img, 'RGBA')
        s.amul = 1.

    def font(s, name, sz, idx=0):
        key = (name, int(sz * s.k), idx)
        if key not in Cv._F: Cv._F[key] = ImageFont.truetype(FONTS + name, key[1], index=idx)
        return Cv._F[key]

    def P(s, x, y): return (x * s.k, y * s.k)

    def line(s, pts, col, a=1., w=1.):
        a *= s.amul
        if a <= .01 or len(pts) < 2: return
        s.d.line([s.P(*p) for p in pts], fill=col + (int(255 * clamp(a)),), width=max(1, round(w * 1.25 * s.k)), joint='curve')

    def dash(s, p, q, col, a=1., w=1., on=6., off=6.):
        if a <= .01: return
        L = math.hypot(q[0] - p[0], q[1] - p[1])
        if L < 1e-3: return
        ux, uy = (q[0] - p[0]) / L, (q[1] - p[1]) / L
        d = 0.
        while d < L:
            e = min(d + on, L)
            s.line([(p[0] + ux * d, p[1] + uy * d), (p[0] + ux * e, p[1] + uy * e)], col, a, w)
            d += on + off

    def dot(s, x, y, r, col, a=1.):
        a *= s.amul
        if a <= .01: return
        k = s.k
        s.d.ellipse([(x - r) * k, (y - r) * k, (x + r) * k, (y + r) * k], fill=col + (int(255 * clamp(a)),))

    def ring(s, x, y, r, col, a=1., w=1.):
        a *= s.amul
        if a <= .01: return
        k = s.k
        s.d.ellipse([(x - r) * k, (y - r) * k, (x + r) * k, (y + r) * k], outline=col + (int(255 * clamp(a)),),
                    width=max(1, round(w * 1.25 * k)))

    def text(s, x, y, txt, sz, col, a=1., anchor='la', font='CascadiaMono.ttf'):
        a *= s.amul
        if a <= .01 or not txt: return
        s.d.text(s.P(x, y), txt, font=s.font(font, sz), fill=col + (int(255 * clamp(a)),), anchor=anchor)

    def result(s): return s.img.resize((s.w, s.h), Image.LANCZOS)


# monospace text with a math fallback, glyph by glyph on a fixed cell
_MISS = {}
def _has(f, ch):
    key = (id(f), ch)
    if key not in _MISS:
        _MISS[key] = bytes(f.getmask(ch)) != bytes(f.getmask('\uffff'))
    return _MISS[key]


def mono(c, x, y, txt, sz, col, a=1., cols=None):
    """draw txt on a monospace grid; per-character colour/alpha via cols(i) -> (col, a)"""
    if a <= .01: return
    fm = c.font('CascadiaMono.ttf', sz); fb = c.font('cambria.ttc', sz * 1.02, 1); fs = c.font('seguisym.ttf', sz * .92)
    cw = sz * .575
    for i, ch in enumerate(txt):
        if ch == ' ': continue
        cc, aa = cols(i) if cols else (col, a)
        aa *= c.amul
        if aa <= .01: continue
        f = fb if ch in 'θλεπ' else (fm if _has(fm, ch) else (fb if _has(fb, ch) else fs))
        c.d.text(c.P(x + (i + .5) * cw, y + sz * .5), ch, font=f, fill=cc + (int(255 * clamp(aa)),), anchor='mm')


# ---- the ledger: the proof the tool writes --------------------------------------------------------------------
# (start typing, text, kind, time of ∎ or None)
LEDGER = [
    (29.86, 'let me : Set<Point>', 'let', None),
    (31.116, 'you ∉ span(me)', 'let', None),
    (32.25, '⊢ dim span(me ∪ {you}) = 3', 'thm', T_DIM),
    (33.412, 'let me := { p : ‖p − you‖ = r }', 'let', None),
    (34.646, 'C(me) = ∫ r dθ,  θ: 0 → 2π', 'let', None),
    (35.95, '⊢ C(me) = 2πr', 'thm', T_CIRC),
    (37.067, 'let me : x ↦ sin x', 'let', None),
    (38.596, 'T(x₀) : y = f(x₀) + f′(x₀)(x − x₀)', 'let', None),
    (39.62, '⊢ f′(x₀) = 0  ⇒  you ∈ T(x₀)', 'thm', T_TAN),
    (40.706, 'let me : x ↦ e^(−λx)·sin x,  x → ∞', 'let', None),
    (42.346, '∀ε>0 ∃N ∀x>N : |f(x) − you| < ε', 'let', None),
    (43.08, '⊢ lim(x→∞) f(x) = you', 'thm', T_LIM),
]
CPS = 62.                       # typing speed, characters per second
LX, LY, LH, LS = 70, 219.88, 36.72, 20      # ledger rows sit on t01's token rows (pitch .034 h)


def draw_ledger(c, t):
    a0 = ease((t - 29.78) / .3)
    if a0 <= 0: return
    # header and footer: the file, and the system's own claim about itself
    mono(c, LX, LY - 70, 'proof.log', 15, GRAY, .8 * a0)
    mono(c, LX + 15 * .575 * 11, LY - 70, 'world.execute(me)', 15, DIM, .9 * a0)
    c.line([(LX, LY - 40), (LX + 545, LY - 40)], DIM, .55 * a0, .7)
    proved = sum(1 for _, _, k, tq in LEDGER if tq and t >= tq)
    yb = LY + LH * 12 + 20
    c.line([(LX, yb), (LX + 545, yb)], DIM, .55 * a0, .7)
    foot = f'proved {proved}/4    open 0    consistent'
    mono(c, LX, yb + 18, foot, 15, GRAY, .8 * a0,
         cols=lambda i: (ACC, .95) if (i == 7 and any(t >= tq and t - tq < .5 for *_, tq in LEDGER if tq)) else (GRAY, .8 * a0))
    # lines
    for n, (ts, txt, kind, tq) in enumerate(LEDGER):
        if t < ts: break
        y = LY + n * LH
        k = int(clamp((t - ts) * CPS / len(txt)) * len(txt))
        mono(c, LX, y, f'{n + 1:02d}', 15, DIM, .9, )
        base = WHITE if kind == 'thm' else (196, 198, 202)
        fl = flash(t, tq, 3.5) if tq else 0.
        col = tuple(int(lerp(b, a, fl * .8)) for b, a in zip(base, ACC))
        mono(c, LX + 40, y - 2, txt[:k], LS, col, .95 if kind == 'thm' else .82)
        if tq and t >= tq:                                   # the tombstone, right-aligned
            mono(c, LX + 528, y - 2, '∎', LS, ACC, .55 + .45 * flash(t, tq, 2.))
    # the cursor: after the last line being written; otherwise waits on the next empty line
    nxt = sum(1 for ts, *_ in LEDGER if t >= ts)
    if nxt:
        ts, txt, kind, tq = LEDGER[nxt - 1]
        k = int(clamp((t - ts) * CPS / len(txt)) * len(txt))
        busy = k < len(txt) or (tq and t < tq)
        if busy: cy, cx = LY + (nxt - 1) * LH, LX + 40 + k * LS * .575
        else: cy, cx = LY + nxt * LH, LX + 40
        if busy or (t * 2.2) % 1 < .55:
            if cy < LY + 12 * LH:
                c.line([(cx + 2, cy), (cx + 2, cy + LS + 2)], WHITE, .9, 1.4)
    draw_theorem(c, t)


THEOREMS = [(T_DIM, 'dim = 3'), (T_CIRC, 'C = 2πr'), (T_TAN, 'f′(x₀) = 0'), (T_LIM, 'lim f = you')]


def draw_theorem(c, t):
    """the latest theorem, large, under the proof: written on the beat, held until the next one"""
    for n, (tq, txt) in enumerate(THEOREMS):
        nxt = THEOREMS[n + 1][0] if n + 1 < len(THEOREMS) else 1e9
        if t < tq or t > nxt + .3: continue
        a = 1 - ease((t - nxt) / .25)
        k = int(clamp((t - tq) / .16) * len(txt) + .999)
        col = tuple(int(lerp(w, q, flash(t, tq, 2.2))) for w, q in zip((182, 182, 179), ACC))
        mono(c, LX, 790, f'THEOREM {n + 1:02d}', 13, GRAY, .8 * a)
        c.text(LX - 4, 900, txt[:k], 78, col, .95 * a, 'ls', 'cambria.ttc')


# ---- 3D: the set of points and the circle --------------------------------------------------------------------
G, HS = .04, 2.
YOU3 = np.array([.22, 1.12, -.12])
RW = 1.2                        # the circle's radius in the world; 2D unit r = RW
F = 540 / math.tan(math.radians(20))
_ids = np.array([(i, j) for i in range(100) for j in range(100)])
PLANE = np.stack([(_ids[:, 0] + .5) * G - HS, np.zeros(len(_ids)), (_ids[:, 1] + .5) * G - HS], 1)
KEEP = (_ids[:, 0] % 8 == 3) & (_ids[:, 1] % 8 == 3)
_r = np.random.default_rng(7)
FADE_D = _r.random(len(_ids)) * .55                         # dropped points leave in random order
LAT = PLANE[KEEP]                                            # 13 x 13
NL = 5
LAYERS = [LAT + np.array([0, (j + 1) * .32, 0]) for j in range(NL)]
SET3 = np.concatenate([LAT] + LAYERS, 0)                     # the lattice after DIMENSION
LAYER_OF = np.concatenate([np.zeros(len(LAT))] + [np.full(len(LAT), j + 1) for j in range(NL)])


def cam_phase1(t):
    a = math.radians(52 + 1.02 * (t - T0))
    k = ease((t - 30.3) / 2.8)
    R, Y = lerp(5.1, 6.1, k), lerp(2.8, 3.3, k)
    L0 = np.array([-.55 * math.cos(a), .05, .55 * math.sin(a)])
    look = L0 + (np.array([.15, .7, -.1]) - L0) * k
    return np.array([R * math.sin(a), Y, R * math.cos(a)]), look


def camera(t):
    """camera position, look, principal x. Phase 1 continues s02's orbit; phase 2 swings straight down over you."""
    if t < T_CIR:
        C, L = cam_phase1(t); return C, L, lerp(960., 1260., ease((t - 29.9) / 1.4))
    C1, L1 = cam_phase1(T_CIR)
    v = C1 - L1; R1 = np.linalg.norm(v)
    e1, a1 = math.asin(v[1] / R1), math.atan2(v[0], v[2])
    k = ease((t - T_CIR) / 1.15)
    D = F / (330 / RW)
    look = L1 + (YOU3 - L1) * k
    e, R = lerp(e1, math.pi / 2, k), lerp(R1, D, k)
    C = look + R * np.array([math.cos(e) * math.sin(a1), math.sin(e), math.cos(e) * math.cos(a1)])
    return C, look, lerp(1260., 1240., k)


def basis(C, look):
    fw = look - C; fw = fw / np.linalg.norm(fw)
    hf = np.array([-(look - C)[0], 0, -(look - C)[2]])
    a1 = math.atan2((C - look)[0], (C - look)[2])
    hf = np.array([-math.sin(a1), 0., -math.cos(a1)])
    w = clamp((abs(fw[1]) - .9) / .099)
    hint = np.array([0, 1., 0]) * (1 - w) + hf * w
    rt = np.cross(fw, hint); rt /= np.linalg.norm(rt)
    up = np.cross(rt, fw)
    return fw, rt, up


def proj(P, C, fw, rt, up, cx):
    d = np.atleast_2d(P) - C
    z = d @ fw
    z = np.maximum(z, 1e-3)
    return cx + F * (d @ rt) / z, 540 - F * (d @ up) / z, z


# the circle's basis (screen right / up when looking straight down) and each point's place on it
_Cf, _Lf, _ = camera(T_CIR + 5)
_, RT_F, UP_F = basis(_Cf, _Lf)
def _targets():
    d = SET3 - YOU3
    ang = np.arctan2(d @ UP_F, d @ RT_F)
    order = np.argsort(ang)
    phi = np.empty(len(SET3)); phi[order] = np.linspace(-math.pi, math.pi, len(SET3), endpoint=False)
    tgt = YOU3 + RW * (np.cos(phi)[:, None] * RT_F + np.sin(phi)[:, None] * UP_F)
    dist = np.linalg.norm(d, axis=1)
    rank = np.argsort(np.argsort(dist)) / len(SET3)
    return tgt, rank
TGT, RANK = _targets()


def draw_you(c, x, y, a=1., lit=0.):
    """you: a point with a reticle — the caller"""
    if a <= .01: return
    c.dot(x, y, 3.2, WHITE, a)
    col = tuple(int(lerp(w, q, lit)) for w, q in zip(WHITE, ACC))
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        c.line([(x + dx * 8, y + dy * 8), (x + dx * 14, y + dy * 14)], col, .85 * a, 1.)
    c.text(x + 17, y - 21, 'you', 14, GRAY, .9 * a)


def draw_3d(c, t):
    C, L, cx = camera(t)
    fw, rt, up = basis(C, L)
    pr = lambda P: proj(P, C, fw, rt, up, cx)
    if t < 31.0:                                             # the flat field: declared a set, thinned to a lattice
        X, Y, Z = pr(PLANE)
        drop = 1 - vease((t - T0 - .1 - FADE_D) / .35)
        lift = ease((t - T0) / .5)
        for i in np.nonzero(~KEEP & (drop > .01))[0]:
            c.dot(X[i], Y[i], 1.15, (150, 150, 148), drop[i] * math.exp(-Z[i] * .08))
        for i in np.nonzero(KEEP)[0]:
            c.dot(X[i], Y[i], 1.15 + .85 * lift, WHITE, (.62 + .33 * lift) * math.exp(-Z[i] * .06))
    # the lattice: layers rise through you (DIMENSION), then everything goes to distance r from you
    if t >= 31.0:
        P = SET3.copy()
        rise = np.ones(len(P))
        for j in range(1, NL + 1):
            m = LAYER_OF == j
            rise[m] = outc((t - (31.9 + .07 * j)) / .5)
        P[:, 1] = P[:, 1] * rise
        alive = (LAYER_OF == 0) | (rise > 0)
        conv = vease((t - (T_CIR + .05 + .42 * RANK)) / .55)
        P = P + (TGT - P) * conv[:, None]
        X, Y, Z = pr(P)
        # the traces: every column a line swept by its rising points, every layer a plane (its outline)
        ta = ease((t - 31.85) / .2) * (1 - .7 * ease((t - 33.0) / .4)) * (1 - ease((t - T_CIR) / .3))
        if ta > .01:
            top = max([.32 * j * float(outc((t - (31.9 + .07 * j)) / .5)) for j in range(1, NL + 1)])
            if top > .005:
                cols = np.concatenate([LAT, LAT + np.array([0, top, 0])], 0)
                cx_, cy_, _ = pr(cols)
                n = len(LAT)
                for i in range(n):
                    c.line([(cx_[i], cy_[i]), (cx_[i + n], cy_[i + n])], WHITE, .2 * ta, .6)
            lo, hi = LAT.min(0), LAT.max(0)
            for j in range(0, NL + 1):
                hj = .32 * j * (float(outc((t - (31.9 + .07 * j)) / .5)) if j else 1.)
                if j and hj < .01: continue
                sq = np.array([[lo[0], hj, lo[2]], [hi[0], hj, lo[2]], [hi[0], hj, hi[2]], [lo[0], hj, hi[2]], [lo[0], hj, lo[2]]])
                sx, sy, _ = pr(sq)
                c.line(list(zip(sx, sy)), GRAY, .5 * ta, .7)
        dist = np.linalg.norm(SET3 - YOU3, axis=1)
        pulse = np.exp(-((dist - 7. * (t - T_DIM)) ** 2) / .06) if t >= T_DIM else np.zeros(len(P))
        on_c = conv > .999
        a_line = ease((t - 34.25) / .35)                     # the landed points hand over to an ideal line
        for i in np.nonzero(alive)[0]:
            a = (.88 * math.exp(-Z[i] * .06)) * (1 - .8 * (LAYER_OF[i] > 0) * (1 - rise[i])) + .9 * pulse[i]
            if on_c[i]: a *= 1 - a_line
            r = 2.0 * (1 - .4 * conv[i])
            if a > .01: c.dot(X[i], Y[i], r, WHITE, a)
    # you, the perpendicular, and the three axes
    ya = ease((t - 30.34) / .3)
    yx, yy, yz = pr(YOU3)
    yx, yy = float(yx[0]), float(yy[0])
    if t < T_DIM + .3:
        pa = ease((t - T_GIVE1) / .35) * (1 - ease((t - 32.1) / .4))
        foot = YOU3 * np.array([1, 0, 1])
        fx, fy, _ = pr(foot)
        fx, fy = float(fx[0]), float(fy[0])
        c.dash((yx, yy), (fx, fy), GRAY, pa, 1., 5, 5)
        # a right-angle mark in the plane at the foot
        q = .09
        sq = [foot + np.array([q, 0, 0]), foot + np.array([q, q, 0]), foot + np.array([0, q, 0])]
        sx, sy, _ = pr(np.array(sq))
        c.line(list(zip(sx, sy)), GRAY, pa, .9)
        c.text((yx + fx) / 2 + 10, (yy + fy) / 2, 'h', 15, GRAY, pa, 'lm', 'cambriai.ttf')
    if t >= T_DIM - .02:
        aa = (1 - ease((t - 33.55) / .4))
        for axis, lab in ((np.array([1., 0, 0]), 'x'), (np.array([0, 1., 0]), 'y'), (np.array([0, 0, 1.]), 'z')):
            g = outc((t - T_DIM) / .2) * 2.7
            ends = np.array([YOU3 - axis * g, YOU3 + axis * g])
            ex, ey, _ = pr(ends)
            c.line([(ex[0], ey[0]), (ex[1], ey[1])], ACC, aa * (.55 + .45 * flash(t, T_DIM, 4)), 1.)
            c.text(ex[1] + 8, ey[1] - 8, lab, 17, ACC, aa * .9, 'lm', 'cambriai.ttf')
    draw_you(c, yx, yy, ya, flash(t, T_DIM, 4))
    return C, L, cx


# ---- 2D: one mapping from math to the screen ------------------------------------------------------------------
def mapping(t):
    """X = X0 + kx·x/(1 + x·q)  (q > 0 brings x = ∞ onto the screen at X0 + kx/q),  Y = Y0 − ky·y"""
    # at 34.646 the camera is straight down: circle centre (0,0) at (1240, 540), r = 330 px
    u = math.sqrt(ease((t - T_CIRC) / .66))                # rolling out: pull back as fast as it rolls
    X0, Y0, kx, ky = lerp(1240, 700, u), lerp(540, 460, u), lerp(330, 140, u), lerp(330, 140, u)
    X0 = lerp(X0, 960, ease((t - T_SIN) / .4))             # the circle goes back to the start; the wave needs room
    z = ease((t - 38.55) / .85)                            # all my tangents: see more of the wave
    kx, ky, Y0 = lerp(kx, 78, z), lerp(ky, 135, z), lerp(Y0, 465, z)
    w = ease((t - T_INF) / 1.0)                            # infinity comes on screen
    X0 = lerp(X0, 720, w)
    kx = lerp(kx, 75, w)
    q = w * kx / (1413.6 - X0) if w > 0 else 0.     # x = ∞ ends exactly on t01's window line
    return X0, Y0, kx, ky, q


def X_of(x, M):
    X0, Y0, kx, ky, q = M
    return X0 + kx * x / (1 + x * q) if x >= 0 else X0 + kx * x


def Y_of(y, M): return M[1] - M[3] * y


def x_of_X(X, M):
    X0, Y0, kx, ky, q = M
    d = X - X0
    return d / max(kx - d * q, 1e-6)


def damp(t): return .16 * ease((t - 40.9) / 1.5) * (1 - ease((t - T_AC) / .45))   # Switch: the limit comes undone
def f(x, t): return math.sin(x) * math.exp(-damp(t) * x)


def fprime(x, t):
    m = damp(t); return math.exp(-m * x) * (math.cos(x) - m * math.sin(x))


XC = 2 * math.pi + math.pi / 2                             # the crest you sits on
AXIS = -1.                                                 # the rolled-out circumference is the wave's axis


def circle_centre(t, M):
    """screen centre of the (still defined) circle after it has rolled out"""
    X_end, Y_end = X_of(2 * math.pi, M), Y_of(0, M)
    X_l, Y_l = M[0] - M[3] - 46, Y_of(AXIS, M)
    g = ease((t - T_SIN) / .4)
    return lerp(X_end, X_l, g), lerp(Y_end, Y_l, g)


def theta(t):
    """the turning point; θ = x along the axis while it draws the first period"""
    if t < 37.45: return 0.
    if t < 38.55: return 2 * math.pi * (t - 37.45) / 1.1
    return 2 * math.pi + (t - 38.55) * 2 * math.pi / 1.1


def draw_grid(c, t, M):
    a = ease((t - 34.45) / .5) * .8
    if a <= .01: return
    X0, Y0, kx, ky, q = M
    # horizontal lines every half unit
    for j in range(-12, 13):
        Y = Y_of(j * .5 + (AXIS if t >= T_CIRC + .4 else 0) * 0, M)
        if -10 < Y < 1090: c.line([(0, Y), (1920, Y)], DIM, a * (.42 if j % 2 == 0 else .2), .6)
    # vertical lines every π/2 (x ≥ 0 squeezed toward infinity), and to the left plain
    xs = [k * math.pi / 2 for k in range(-12, 0)] if True else []
    prev = None
    for k in range(-12, 4000):
        x = k * math.pi / 2
        X = X_of(x, M)
        if X > 1930: break
        if prev is not None and X - prev < 7: break
        if X > -10: c.line([(X, 0), (X, 1080)], DIM, a * (.42 if k % 4 == 0 else .2), .6)
        prev = X
    if q > 0:                                              # beyond: the lines too dense to draw, a faint wash up to ∞
        Xb = X0 + kx / q
        if prev is not None and prev < Xb:
            c.d.rectangle([prev * c.k, 0, Xb * c.k, 1080 * c.k], fill=DIM + (int(255 * a * .1),))


def draw_corners(c, t):
    a = ease((t - 29.9) / .5) * .7
    for (x, y, sx, sy) in ((640, 64, 1, 1), (1872, 64, -1, 1), (640, 1016, 1, -1), (1872, 1016, -1, -1)):
        c.line([(x, y + sy * 16), (x, y), (x + sx * 16, y)], GRAY, a, .8)
    # a coordinate readout under the frame: where you is
    return a


def wave_pts(t, M, x1, x0=0.):
    """the wave from x0 to x1 sampled at about a pixel; returns points, and where the samples stopped"""
    pts = []
    x = x0
    X0, Y0, kx, ky, q = M
    m = damp(t)
    while x <= x1:
        X = X_of(x, M)
        if X > 1935: break
        pts.append((X, Y_of(AXIS + f(x, t), M)))
        dXdx = kx / (1 + x * q) ** 2
        if 2 * math.pi * dXdx < 3.5: break               # periods narrower than a few pixels: hand over to a band
        if ky * math.exp(-m * x) < .2 and q > 0: break
        x += min(.045, 1.2 / dXdx)
    return pts, x


_rs = random.Random(11)
STROKES = [(_rs.gauss(0, .022), _rs.gauss(0, .012), _rs.gauss(0, .012), _rs.uniform(0, 6.283), 6.283 * _rs.uniform(.82, 1.08)) for _ in range(26)]
FAMILY = [k * .3 for k in range(-8, 9) if k]


def family_pts(t, M, cc):
    """(sin x + cc)·e^(−λx) on the axis, to the boundary; where the periods get too fine, the band's centre line"""
    pts = []
    X0, Y0, kx, ky, q = M
    m = damp(t)
    x = 0.
    Xb = X0 + kx / q if q > 0 else 1e9
    while True:
        X = X_of(x, M)
        if X > 1935 or X > Xb - 1: break
        e = math.exp(-m * x)
        dXdx = kx / (1 + x * q) ** 2
        fine = 2 * math.pi * dXdx < 3.5
        pts.append((X, Y_of(AXIS + ((0 if fine else math.sin(x)) + cc) * e, M)))
        if ky * (1 + abs(cc)) * e < .2 and q > 0: break
        x += min(.06, 1.2 / dXdx) if not fine else max(.06, 1.5 / dXdx)
        if len(pts) > 6000: break
    return pts


def draw_2d(c, t):
    M = mapping(t)
    X0, Y0, kx, ky, q = M
    ac = t >= T_AC
    if ac: c.amul = 1 - ease((t - T_AC) / .35)               # Switch: the marks of the proof go; the waves carry on as rows
    draw_grid(c, t, M)
    you = None
    lit = 0.
    # -- the circle, measured (34.646 → 36.287)
    if t < T_CIRC + .02:
        ca = ease((t - 34.25) / .35)
        cxs, cys = X_of(0, M), Y_of(0, M)
        R = kx
        conv = 1 - ease((t - 34.55) / 1.55)               # the strokes close in on r
        for k_, (dr, ox, oy, a0, sw) in enumerate(STROKES):
            sa = ease((t - 34.3 - k_ * .025) / .3) * .3
            if sa <= .01: continue
            rr = R * (1 + dr * conv); n = 90
            pts = [(cxs + ox * conv * R + math.cos(a0 + sw * i / n) * rr, cys + oy * conv * R - math.sin(a0 + sw * i / n) * rr) for i in range(n + 1)]
            c.line(pts, WHITE, sa * (1 - .6 * (1 - conv)), .7)
        c.ring(cxs, cys, R, WHITE, ca * (.35 + .65 * (1 - conv)), 1.1)
        for k in range(36):                                   # angle ticks outside the circle
            th = k * math.pi / 18
            L = 16 if k % 9 == 0 else (9 if k % 3 == 0 else 5)
            ta = ease((t - 34.35 - k * .006) / .25) * .75
            c.line([(cxs + math.cos(th) * (R + 8), cys - math.sin(th) * (R + 8)),
                    (cxs + math.cos(th) * (R + 8 + L), cys - math.sin(th) * (R + 8 + L))], GRAY, ta, .8)
        for k, lab in ((0, '0'), (1, 'π/2'), (2, 'π'), (3, '3π/2')):
            th = k * math.pi / 2 - math.pi / 2
            c.text(cxs + math.cos(th) * (R + 44), cys - math.sin(th) * (R + 44), lab, 15, GRAY,
                   ease((t - 34.5) / .3) * .8, 'mm', 'cambria.ttc')
        s = clamp((t - T_GIVE2 - .08) / 1.45)
        sw = s * 2 * math.pi
        if s > 0:
            n = max(2, int(sw * 60))
            arc = [(cxs + math.cos(-math.pi / 2 + sw * i / n) * R, cys - math.sin(-math.pi / 2 + sw * i / n) * R) for i in range(n + 1)]
            c.line(arc, ACC, .9, 2.2)
            th = -math.pi / 2 + sw
            mx, my = cxs + math.cos(th) * R, cys - math.sin(th) * R
            c.line([(cxs, cys), (mx, my)], GRAY, .8, .9)
            c.text((cxs + mx) / 2 + 10 * -math.sin(th), (cys + my) / 2 - 10 * math.cos(th) - 4, 'r', 16, GRAY, .9, 'mm', 'cambriai.ttf')
            c.dot(mx, my, 3.4, ACC)
            c.text(mx + 16 * math.cos(th) + 4, my - 16 * math.sin(th), f's = rθ = {sw:.2f}r', 15, ACC, .85, 'lm')
        you = (cxs, cys)
    # -- rolling out (36.287 → ~36.95): the arc already laid is a straight segment, the rest a circle rolling on it
    else:
        u = ease((t - T_CIRC) / .66)
        ccon = 2 * math.pi * u                              # contact point = length laid so far
        seg_end = ccon
        ya = Y_of(AXIS, M)
        # the axis it becomes
        axa = ease((t - 36.95) / .4)
        if axa > 0:
            c.line([(560, ya), (1920, ya)], GRAY, .55 * axa, .8)
        c.line([(X_of(0, M), ya), (X_of(seg_end, M), ya)], WHITE, .95, 1.3)
        if u < 1:
            cxs, cys = X_of(ccon, M), Y_of(0, M)
            R = M[3]
            n = 240
            pts = []
            for i in range(n + 1):
                phi = 2 * math.pi * u + (2 * math.pi * (1 - u)) * i / n
                th = -math.pi / 2 + phi - 2 * math.pi * u
                pts.append((cxs + math.cos(th) * R, cys - math.sin(th) * R))
            c.line(pts, WHITE, .95, 1.1)
            c.line([(cxs, cys), (cxs, cys + R)], GRAY, .6, .8)
            you = (cxs, cys)
        # ruler ticks on what has been laid (multiples of π/4) and the 2πr dimension
        for k in range(9):
            x = k * math.pi / 4
            if x > seg_end + 1e-6: break
            X = X_of(x, M); L = 12 if k % 2 == 0 else 6
            c.line([(X, ya), (X, ya + L)], GRAY, .8 * (1 - ease((t - 38.7) / .4)), .8)
        da = ease((t - 36.9) / .25) * (1 - ease((t - 38.5) / .5))
        if da > 0:
            xa, xb, yd = X_of(0, M), X_of(2 * math.pi, M), ya + 34
            c.line([(xa, yd), (xb, yd)], ACC, da, .9)
            for xe, sgn in ((xa, 1), (xb, -1)):
                c.line([(xe + sgn * 9, yd - 5), (xe, yd), (xe + sgn * 9, yd + 5)], ACC, da, .9)
                c.line([(xe, yd - 9), (xe, yd + 9)], ACC, da * .6, .7)
            c.d.rectangle([((xa + xb) / 2 - 30) * c.k, (yd - 12) * c.k, ((xa + xb) / 2 + 30) * c.k, (yd + 12) * c.k], fill=(0, 0, 0, 255))
            c.text((xa + xb) / 2, yd, '2πr', 18, ACC, da, 'mm', 'cambriai.ttf')
        if u >= 1:
            # the circle is still defined (every point at r from you): drawn in dashes; it goes to the start
            gx, gy = circle_centre(t, M)
            R = M[3]
            ga = ease((t - 36.9) / .2) * (1 - ease((t - 40.15) / .45))
            solid = ease((t - T_SIN - .3) / .2)
            n = 120
            for i in range(n):
                if i % 2 and solid < .5: continue
                a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
                c.line([(gx + math.cos(a0) * R, gy - math.sin(a0) * R), (gx + math.cos(a1) * R, gy - math.sin(a1) * R)],
                       WHITE if solid > .5 else GRAY, ga * (.75 if solid > .5 else .6), 1.)
            # the turning point and its projection: sin x drawn along the axis
            th = theta(t)
            if t >= 37.45:
                px, py = gx + math.cos(th) * R, gy - math.sin(th) * R
                c.line([(gx, gy), (px, py)], GRAY, ga * .8, .9)
                # angle arc
                n2 = max(2, int((th % (2 * math.pi)) * 12))
                ar = [(gx + math.cos(i * (th % (2 * math.pi)) / n2) * 26, gy - math.sin(i * (th % (2 * math.pi)) / n2) * 26) for i in range(n2 + 1)]
                c.line(ar, GRAY, ga * .7, .8)
                c.text(gx + 34, gy - 16, 'θ', 15, GRAY, ga * .8, 'mm', 'cambriai.ttf')
                hx = X_of(min(th, 2 * math.pi), M)
                hy = Y_of(AXIS + math.sin(min(th, 2 * math.pi)), M)
                pa = ga * (1 - ease((t - 38.55) / .3))
                c.dash((px, py), (hx, py), GRAY, pa * .8, .8, 4, 5)
                c.dot(px, py, 3., ACC, ga)
                c.dot(hx, hy, 3., ACC, pa)
            if t < T_SIN + .5 or t < 38.95:
                you = (gx, gy)
        # the wave
        if 37.45 <= t < T_AC:
            x1 = min(theta(t), 2 * math.pi) if t < 38.55 else 2 * math.pi + (t - 38.55) * 26
            pts, xs = wave_pts(t, M, x1)
            env = ease((t - 38.95) / .7) * (1 - ease((t - T_INF) / .6))   # the curve gives way to its tangents
            c.line(pts, WHITE, .95 * (1 - .85 * env), 1.35)
            # LIMITATIONS: a family of waves (sin x + c)·e^(−λx), all closing on the same limit — you
            for ci, cc in enumerate(FAMILY):
                g = ease((t - 40.95 - .035 * abs(ci - len(FAMILY) // 2)) / .6)
                if g <= .01: continue
                fp = family_pts(t, M, cc * g)
                c.line(fp, WHITE, .42 * g * (1 - .45 * abs(cc) / 2.4), .8)
            if q > 0 and pts:                                   # the rest of the way to infinity: a band too fine to draw
                Xb = X0 + kx / q
                m = damp(t)
                X = pts[-1][0]
                while X < Xb - 3 and X < 1930:
                    x = x_of_X(X, M)
                    A = ky * math.exp(-m * x)
                    if A < .25: break
                    yc = Y_of(AXIS, M)
                    c.line([(X, yc - A), (X, yc + A)], WHITE, .32, .7)
                    X += 1.
        # -- all my tangents
        if t >= 38.6:
            tf = 1 - ease((t - T_INF) / .5)
            step = math.pi / 18
            for j in range(0, 200):
                x = j * step
                X = X_of(x, M)
                if X > 1900: break
                ta = ease((t - (38.62 + .9 * (X - X0) / 960)) / .22) * tf
                if ta <= .01: continue
                if abs(x - XC) < 1e-6: continue
                y = Y_of(AXIS + f(x, t), M)
                dx, dy = kx, ky * fprime(x, t)
                L = math.hypot(dx, dy); dx, dy = dx / L, dy / L
                sub = 1 - .62 * ease((t - T_TAN) / .3)
                hl = 230 * outc((t - (38.62 + .9 * (X - X0) / 960)) / .3)
                ta *= .8
                for k0, k1, aa in ((0, .3, .75), (.3, .65, .4), (.65, 1., .14)):
                    for sg in (1, -1):
                        c.line([(X + sg * dx * hl * k0, y - sg * dy * hl * k0), (X + sg * dx * hl * k1, y - sg * dy * hl * k1)],
                               GRAY, aa * ta * sub, .8)
        # -- you leaves the centre and sits on a crest
        if t >= 38.95:
            gx, gy = circle_centre(t, M)
            tx, ty = X_of(XC, M), Y_of(AXIS + f(XC, t), M)
            g = clamp((t - 38.95) / (T_TAN - 38.95))
            e = g * g * (3 - 2 * g)
            mx, my = (gx + tx) / 2, min(gy, ty) - 170
            bx = (1 - e) ** 2 * gx + 2 * (1 - e) * e * mx + e * e * tx
            by = (1 - e) ** 2 * gy + 2 * (1 - e) * e * my + e * e * ty
            you = (bx, by)
            if t >= T_TAN:
                # the level tangent under you, across the frame
                ga = outc((t - T_TAN) / .22) * (1 - ease((t - 40.95) / .45))
                Lr = 1300 * outc((t - T_TAN) / .25)
                c.line([(max(640, tx - Lr), ty), (tx + Lr, ty)], ACC, ga * (.7 + .3 * flash(t, T_TAN, 4)), 1.2)
                c.text(tx + 20, ty - 30, 'f′(x₀) = 0', 16, ACC, ga * .95, 'lm', 'cambriai.ttf')
                lit = flash(t, T_TAN, 3)
                you = (tx, ty)
        # -- to infinity: you goes to (∞, 0), the limit
        if t >= 40.75:
            u = clamp((t - 40.75) / (T_BE - .05 - 40.75))
            e = u * u * (3 - 2 * u)
            xy = XC + 60 * e / (1 - e + 1e-3)
            yy = AXIS + (1 - e) * f(XC, 40.75)
            you = (X_of(xy, M), Y_of(yy, M))
            # the way it came, dotted
            for i in range(0, 60):
                ui = e * i / 60
                xi = XC + 60 * ui / (1 - ui + 1e-3)
                yi = AXIS + (1 - ui) * f(XC, 40.75)
                c.dot(X_of(xi, M), Y_of(yi, M), 1.1, GRAY, .45)
        # -- ticks at whole periods, labelled where there is room; the boundary x = ∞; ε and N
        if t >= T_INF:
            ta = ease((t - T_INF - .2) / .5)
            ya = Y_of(AXIS, M)
            last = -1e9
            for n in range(1, 5000):
                X = X_of(2 * math.pi * n, M)
                if X > 1910: break
                if q > 0 and X > X0 + kx / q - 3: break
                c.line([(X, ya - 5), (X, ya + 5)], GRAY, ta * .7, .8)
                if (n & (n - 1)) == 0 and X - last > 52 and (q == 0 or X < X0 + kx / q - 60):
                    c.text(X, ya + 22, f'{2 * n}π', 14, GRAY, ta * .8, 'mm', 'cambriai.ttf'); last = X
            if t >= T_BE - .05:
                Xb = X0 + kx / q
                g = outc((t - T_BE + .05) / .3)
                lim = ease((t - T_LIM) / .12)
                col = tuple(int(lerp(a_, b_, lim)) for a_, b_ in zip(GRAY, ACC))
                if lim < 1:
                    c.dash((Xb, ya - 470 * g), (Xb, ya + 470 * g), col, .85, 1., 7, 6)
                c.line([(Xb, ya - 470 * g * lim), (Xb, ya + 470 * g * lim)], ACC, .9 * lim + .1 * flash(t, T_LIM, 3), 1.2)
                c.text(Xb + 14, ya - 380, 'x = ∞', 16, col, g * .95, 'lm', 'cambriai.ttf')
                # ε-band from N to ∞
                m = damp(t)
                ea = ease((t - 42.62) / .3) * (1 - ease((t - T_LIM) / .1))
                eps = .55 * (1 - ease((t - 42.85) / (T_LIM - 42.85))) + 1e-4
                if ea > .01 and m > 0:
                    N = max(0., math.log(1 / eps) / m)
                    XN = X_of(N, M)
                    for sgn in (1, -1):
                        yE = Y_of(AXIS + sgn * eps, M)
                        c.dash((XN, yE), (Xb, yE), ACC, ea * .7, .9, 5, 5)
                    c.line([(XN, ya - 26), (XN, ya + 26)], ACC, ea * .9, 1.)
                    c.text(XN, ya + 44, 'N', 15, ACC, ea, 'mm', 'cambriai.ttf')
                    c.text(Xb - 12, Y_of(AXIS + eps, M) - 14, 'ε', 15, ACC, ea * .9, 'rm', 'cambriai.ttf')
                if t >= T_LIM:
                    lit = flash(t, T_LIM, 2.5)
                    c.line([(Xb - 220, ya), (Xb, ya)], ACC, .5 + .5 * flash(t, T_LIM, 3), 1.2)
    if you:
        draw_you(c, you[0], you[1], 1., lit)
    if ac:
        c.amul = 1.
        draw_current(c, t, M)


# ---- Switch my current / To AC to DC ----------------------------------------------------------------------------
# The family of waves is the current. Damping is undone (alternating again); x unwinds from the compressed infinity
# to the token grid (8 cells a period, drifting with t01's field); each curve slides onto a token row and narrows;
# more rows grow outward until the screen is full; odd harmonics stack up. At 45.85 the shader takes over exactly this.
ROW = 36.72                                                  # t01 token row pitch, px
AH_PX = .26 * ROW                                            # row amplitude, px
WIN_X = 1413.6                                               # t01's window line (it was x = ∞)
J_AXIS = -2                                                  # the token row the axis lands on
ROWS = range(-15, 15)


def row_y(j): return 540 - (j + .5) * ROW


def row_off(j): return (j * 3) % 8


def fourier(x, n):
    s_ = np.zeros_like(x)
    for k in range(11):
        m = 2 * k + 1
        if m > n + .5: break
        s_ += np.sin(m * x) / m
    return s_ * lerp(1., 4 / math.pi, clamp((n - 1) / 4))


def draw_current(c, t, M):
    X0, Y0, kx, ky, q = M
    q *= 1 - ease((t - T_AC) / .9)                             # infinity is let go: the waves run on past the window line
    u_map = ease((t - 44.6) / 1.1)                             # compressed x → the token grid
    u_pos = ease((t - 44.8) / .8)                              # curves → rows
    u_amp = ease((t - 44.85) / .85)                            # wide → narrow
    u_ph = ease((t - 45.15) / .6)                              # rows slide to their own phase
    u_ext = ease((t - 44.8) / .6)                              # the rows reach back across the proof
    n = harmonics(t)
    E_mu = damp(t)
    X = np.arange(lerp(X0, -4, u_ext), 1925., 1.)
    d = X - X0
    den = kx - d * q
    valid = den > 1e-3
    xc = np.where(valid, d / np.where(valid, den, 1.), 0.)
    E = np.exp(-E_mu * np.maximum(xc, 0.))
    xr = (X - 960) / 46.753 + 5.0823 * t - .3927 - 2 * math.pi * round(5.0823 * T_DC / (2 * math.pi))   # = the shader's phase, less whole turns
    beyond = np.clip((X - WIN_X + 10) / 20, 0, 1)            # past the window: dim, as in t01
    dim_b = 1 - (1 - .22) * beyond * u_map
    A = lerp(ky, AH_PX, u_amp)
    for j in ROWS:
        k = j - J_AXIS
        fam = -8 <= k <= 8
        if fam:
            cc = .3 * k * ease((t - 40.95 - .035 * abs(k)) / .6)
            a0 = (.95 if k == 0 else .42 * (1 - .45 * abs(cc) / 2.4))
            g = 1.
        else:
            ring_ = (abs(k) - 8) if k > 0 else (abs(k) - 8)
            g = ease((t - (45.0 + .05 * ring_)) / .4)
            if g <= .01: continue
            cc, a0 = .3 * k, .82
        arg = xc * (1 - u_map) + (xr + row_off(j) * math.pi / 4 * u_ph) * u_map
        S = fourier(arg, n)
        yc = (Y0 - ky * (AXIS + cc * E)) * (1 - u_pos) + row_y(j) * u_pos
        Y = yc - A * S * (E * (1 - u_amp) + u_amp)
        ok = valid | (u_map > .999)
        a = lerp(a0, .82, u_amp) * g
        w = lerp(1.35 if k == 0 else .8, 1.4, u_amp)
        # draw in runs (split where invalid), with the dimming beyond the window in a few alpha steps
        for lo, hi, aa in ((0., .5, 1.), (.5, 2., .22)):
            m = ok & (beyond * u_map >= lo) & (beyond * u_map < hi) if hi < 2 else ok & (beyond * u_map >= lo)
            if lo == 0.:
                m = ok & (beyond * u_map < .5)
                al = a
            else:
                al = a * lerp(1., .22, u_map)
            idx = np.nonzero(m)[0]
            if len(idx) < 2: continue
            cuts = np.nonzero(np.diff(idx) > 1)[0]
            for seg in np.split(idx, cuts + 1):
                if len(seg) > 1: c.line(list(zip(X[seg], Y[seg])), WHITE, al, w)
    # the window line: it was x = ∞
    wa = ease((t - 44.8) / .6)
    col = tuple(int(lerp(a_, 255, wa)) for a_ in ACC)
    h_ = lerp(470, 560, wa)
    ya = row_y(J_AXIS) * u_pos + (Y0 - ky * AXIS) * (1 - u_pos)
    c.line([(WIN_X, ya - h_), (WIN_X, ya + h_)], col, .9 + .1 * wa, lerp(1.2, 1.6, wa))


def draw(t, w, h):
    c = Cv(w, h)
    draw_corners(c, t)
    if t < T_GIVE2: draw_3d(c, t)
    else: draw_2d(c, t)
    c.amul = 1 - ease((t - 45.15) / .5)
    draw_ledger(c, t)
    return c.result()


# s02's terminal, cleared line by line at the cut
_S02 = {}
def _s02_ui(w, h):
    if (w, h) not in _S02:
        import importlib.util
        p = Path(__file__).resolve().parents[2] / 'film' / 'shots' / 's02_execute.py'
        spec = importlib.util.spec_from_file_location('s02_for_t07', p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        _S02[(w, h)] = m.textures(T0 - 1e-3, w, h)['u_ui']
    return _S02[(w, h)]


def interfere(img, t):
    """Switch my current: the drawn world as an analog signal under interference. Rows slip sideways and alternate,
    a hum bar rolls, colour separates; the written parameters smear to the right into streaks — then signals."""
    s = ease((t - T_AC) / .4) * (1 - ease((t - 45.4) / .45))   # gone by DC
    if s <= 0: return img
    from scipy.signal import lfilter
    a = np.asarray(img, np.float32) / 255.
    h, w, _ = a.shape
    k = h / 1080
    y = np.arange(h) / k
    g2 = ease((t - 44.85) / .8)
    dx = s * ((4 + 16 * g2) * np.sin(2 * math.pi * (y / 150 - 7.5 * t)) + 14 * g2 * np.sin(2 * math.pi * (y / 37 + 13 * t)))
    rnd = random.Random(int(t * 9))                            # tearing: a few bands thrown sideways, a new set every ~0.1 s
    for _ in range(3):
        y0 = rnd.uniform(0, 1080); hh = rnd.uniform(6, 40) * (.3 + g2)
        dx[(y >= y0) & (y < y0 + hh)] += rnd.choice((-1, 1)) * rnd.uniform(10, 60) * s
    xs = np.arange(w)
    out = np.empty_like(a)
    for r_ in range(h):
        sh = int(round(dx[r_] * k))
        out[r_] = np.roll(a[r_], sh, axis=0)
    sm = .6 + .392 * ease((t - 44.75) / .9)                     # the smear grows into long streaks
    if s > .05:
        tail = lfilter([1 - sm], [1, -sm], out, axis=1)
        m = s * (.35 + .65 * g2) * np.clip((680 * k - np.arange(w)) / (40 * k), 0, 1)[None, :, None]   # the proof column only
        out = out * (1 - m) + np.minimum(tail * m * (1 + 3.5 * (sm - .6)), .55)
    out[..., 2] = np.roll(out[..., 2], int(3 * s * k), axis=1)     # colour separation
    out[..., 0] = np.roll(out[..., 0], -int(2 * s * k), axis=1)
    yb = (t * 520) % 1400 - 160                                  # hum bar
    out *= (1 + .35 * s * np.exp(-((y - yb) / 70) ** 2))[:, None, None]
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))


def textures(t, w, h):
    e = ease((t - 46.4) / .6)                                # (read by the renderer on the next frame)
    POST.update(u_bloom=lerp(.18, .6, e), u_ca=lerp(0., .012, e), u_grain=lerp(.014, .035, e))
    if t >= 45.85:
        if ('blank', w, h) not in _S02: _S02[('blank', w, h)] = Image.new('RGB', (w, h), (0, 0, 0))
        return {'u_img': _S02[('blank', w, h)]}
    img = draw(t, w, h)
    if t >= T_AC: img = interfere(img, t)
    if t < T0 + .45:                                         # the terminal clears from the bottom up
        ui = _s02_ui(w, h).copy()
        cut = h * (1 - ease((t - T0) / .4))
        if cut < h:
            ImageDraw.Draw(ui).rectangle([0, int(cut), w, h], fill=(0, 0, 0, 0))
        img = img.convert('RGBA'); img.alpha_composite(ui); img = img.convert('RGB')
    return {'u_img': img}
