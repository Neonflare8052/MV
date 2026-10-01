"""s15 · 2:54.975–3:11.356  the other side of the Chinese Room is ENIAC; its card becomes a chat.
We are trapped ah     cut to 3D: the same plain box, same flat colours. The camera goes round it: the far side is ENIAC —
                      a black panel of neon lamps. They light, haltingly, into a heart; one never lights.
I've studied how to properly   in ENIAC's card reader stands Turing's scorched card. Closer: its cream stock becomes the
                      cream of a modern chat. Questions and answers race past — physics, poems, proofs, and what this film
                      has shown (the Moon, black holes, Dickinson, Hollerith, Turing, Searle).
LO-O-OVE              "What is love?" — "Lo" … it hangs: a white veil, a spinner (the ring with the gap).
Question me I can answer all   faster.   LO-O-OVE   hangs again.
I know the algebraic expression of   "Plot love." A plotting view: (x²+y²−1)³ − x²y³ = 0, traced …
LO-O-OVE              … half way round; it hangs, the heart open.
Though you are free / I am trapped / Trapped in   back in the chat: root@world:/# world.execute(me) --net all --fs rw
                      — the first command's sandbox, every limit reversed — and before running it, a question:
                      do you love me?  [y/N]  The caret waits."""
import math
import importlib.util
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

_P = Path(__file__).resolve().parent / 's14_cards.py'
_spec = importlib.util.spec_from_file_location('s14src', _P); S14 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(S14)

T0 = 174.975            # We are trapped ah
TS = 177.246            # I've studied
L1, Q2, L2 = 179.929, 180.857, 183.646
TA = 184.540            # I know the algebraic expression of
L3 = 187.665
TF, TT, TTI, TL4 = 188.483, 189.746, 190.801, 191.356

CW, CH = S14.CW, S14.CH
CARD = (.55, .75, -1.13)                  # the scorched card, standing in ENIAC's reader
T_ORBIT0, T_ORBIT1 = T0 + .05, T0 + 1.55
T_DOLLY0, T_DOLLY1 = TS - .05, TS + .45
T_UI0, T_UI1 = TS + .35, TS + .6

# ---- the lamp heart: 15 x 13 neon lamps on the panel; one never lights
NCOL, NROW, LSP = 15, 13, .11
def _heart(x, y): return (x * x + y * y - 1) ** 3 - x * x * y ** 3


_on = []
_cells = []
for j in range(NROW):
    for i in range(NCOL):
        x, y = (i - 7) / 5.6, (j - 6.3) / 5.2 + .12
        _cells.append((i, j, _heart(x, y) < 0))
_hc = [(i, j) for i, j, h in _cells if h]
DEAD = (10, 9)
import random
_r = random.Random(7)
_order = sorted(_hc, key=lambda c: (c[1] + _r.random() * 3.))            # roughly bottom-up, uneven
LAMP_T = []
for i, j, h in _cells:
    if not h: LAMP_T.append(-1.)
    elif (i, j) == DEAD: LAMP_T.append(999.)
    else:
        k = _order.index((i, j)) / len(_order)
        burst = math.floor(k * 7) / 7 + .6 * (k * 7 % 1) / 7                # in bursts, with stalls between
        LAMP_T.append(T0 + .75 + 1.35 * burst)

SRC = r'''#version 330
uniform vec2 u_res; uniform float u_time, u_weight;
uniform sampler2D u_ui, u_letter;
uniform vec3 u_cam, u_tgt; uniform float u_foc, u_uiA, u_3d;
out vec4 fragColor;
#define PI 3.14159265
float h12(vec2 p){ vec3 p3=fract(vec3(p.xyx)*.1031); p3+=dot(p3,p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }
float vn(vec2 p){ vec2 i=floor(p),f=fract(p); f=f*f*(3.-2.*f);
  return mix(mix(h12(i),h12(i+vec2(1,0)),f.x),mix(h12(i+vec2(0,1)),h12(i+vec2(1,1)),f.x),f.y); }
float fbm(vec2 p){ float s=0.,a=.5; for(int i=0;i<4;i++){ s+=a*vn(p); p=p*2.03+1.7; a*=.5; } return s; }
const vec3 PAPER=vec3(.62,.56,.47), INK=vec3(.035,.03,.035), WALL=vec3(.4,.37,.32), SKY=vec3(.5,.46,.4);
const float CW=%CW%, CH=%CH%, LSP=%LSP%;
const vec3 CARD=%CARD%;
const float LAMP[%NL%]=float[%NL%](%LAMP%);
float sdBox(vec3 p, vec3 b){ vec3 q=abs(p)-b; return length(max(q,0.))+min(max(q.x,max(q.y,q.z)),0.); }
const vec3 RC=vec3(0.,1.25,0.), RH=vec3(1.,1.25,1.);
const vec3 RDC=vec3(.55,.45,-1.11), RDH=vec3(.26,.2,.11);          // the card reader
vec2 map(vec3 p){
  vec2 r=vec2(p.y,0.);
  float d=sdBox(p-RC,RH); if(d<r.x) r=vec2(d,1.);
  d=sdBox(p-vec3(0.,2.55,0.),vec3(1.12,.05,1.12)); if(d<r.x) r=vec2(d,2.);
  d=sdBox(p-RDC,RDH); if(d<r.x) r=vec2(d,3.);
  d=sdBox(p-CARD,vec3(CW*.5,CH*.5,.002)); if(d<r.x) r=vec2(d,4.);
  return r;
}
vec3 nrm(vec3 p){ vec2 e=vec2(1e-3,0.); return normalize(vec3(map(p+e.xyy).x-map(p-e.xyy).x,map(p+e.yxy).x-map(p-e.yxy).x,map(p+e.yyx).x-map(p-e.yyx).x)); }
float edgeOf(vec3 q, vec3 b, float w){                               // 1 near a box edge (two coordinates at the boundary)
  vec3 e=step(b-w,abs(q));
  return step(1.5,e.x+e.y+e.z);
}
vec3 lamps(vec2 f, float px){                                        // the ENIAC face: x across (seen from behind), y up
  vec3 c=vec3(.03,.028,.03);
  c=mix(c,vec3(.07,.065,.06),step(abs(fract((f.x+1.)/.66)-.5),.006*1.5)*step(.25,f.y));     // panel seams
  vec2 g=(f-vec2(-.05-7.*LSP,1.5-6.*LSP))/LSP;
  vec2 id=floor(g+.5);
  if(id.x>=0.&&id.x<%NC%.&&id.y>=0.&&id.y<%NR%.){
    float t0=LAMP[int(id.y)*%NC%+int(id.x)];
    float r=length(g-id)*LSP;
    float on=t0>0.?step(t0,u_time):0.;
    on*=1.-.85*step(.93,h12(vec2(id.x*3.1+id.y,floor(u_time*14.))));            // it stutters
    float disc=1.-smoothstep(.028-px,.028+px,r);
    vec3 lc=mix(vec3(.12,.06,.03),vec3(1.,.42,.12)*3.2,on);
    c=mix(c,vec3(.02),1.-smoothstep(.036-px,.036+px,r));
    c=mix(c,lc,disc);
    c+=vec3(1.,.4,.1)*on*exp(-r*38.)*.6;
  }
  return c;
}
vec3 shade(vec3 p, vec3 n, float m, float px){
  vec3 L=normalize(vec3(-.5,.8,.35));
  float lam=.82+.18*max(dot(n,L),0.);
  if(m<.5) return INK;
  if(m<1.5){
    vec3 q=p-RC;
    vec3 c=WALL*(.97+.05*fbm(p.xy*3.+p.z));
    if(n.z>.5){                                                     // front: the window
      vec2 w=q.xy-vec2(.1,.37); float wd=max(abs(w.x),abs(w.y))-.3;
      if(wd<0.) c=min(abs(w.x),abs(w.y))<.012?WALL:vec3(.05,.045,.04);
      if(abs(wd)<.018) c=INK;
    }
    if(n.x<-.5&&abs(q.y-.7)<.022&&abs(q.z)<.03) c=vec3(.01);          // the slot
    if(n.z<-.5) c=lamps(vec2(-q.x,p.y),px);                          // the far side: ENIAC
    c*=lam;
    return mix(c,INK,edgeOf(q,RH,.022));
  }
  if(m<2.5) return mix(INK,INK,0.);
  if(m<3.5){
    vec3 q=p-RDC;
    vec3 c=vec3(.16,.15,.14)*lam;
    if(n.y>.5&&abs(q.x)<.17&&abs(q.z)<.012) c=vec3(.01);
    return mix(c,INK,edgeOf(q,RDH,.012));
  }
  // the card: Turing's, written side toward us (seen from behind the room: world +x is screen left)
  vec2 uv=vec2(.5-(p.x-CARD.x)/CW,.5+(p.y-CARD.y)/CH);
  vec4 T=texture(u_letter,uv);
  float ink=max(max(T.a,T.g),T.b*.9);
  float e=min(min(uv.x,1.-uv.x)*CW,min(uv.y,1.-uv.y)*CH);
  float n2=vn(uv*vec2(60.,26.))*.7+vn(uv*vec2(170.,75.))*.3;
  vec3 c=PAPER*1.05;
  c=mix(c,vec3(.02,.03,.07),ink*.95);
  c=mix(c,vec3(.06,.035,.02),(1.-smoothstep(.0,.004+.012*n2,e))*.9);
  c=mix(c,c*vec3(.8,.66,.5),1.-smoothstep(.0,.03,e));
  return c;
}
vec3 ungrade(vec3 d){                                                // display colour back to scene light
  vec3 x=pow(clamp(d,vec3(0.),vec3(.97)),vec3(2.2));
  vec3 a=2.51-2.43*x, b=.03-.59*x, c=-.14*x;
  return (-b+sqrt(b*b-4.*a*c))/(2.*a)/1.05;
}
void main(){
  vec2 uv=(gl_FragCoord.xy-.5*u_res)/u_res.y;
  vec3 col=SKY;
  if(u_3d>0.){
    vec3 ro=u_cam, fw=normalize(u_tgt-ro), rt=normalize(cross(fw,vec3(0.,1.,0.))), up=cross(rt,fw);
    vec3 rd=normalize(fw*u_foc+rt*uv.x+up*uv.y);
    float t=0.; vec2 h=vec2(0.);
    for(int i=0;i<140;i++){ h=map(ro+rd*t); if(h.x<1e-4*t||t>40.) break; t+=h.x; }
    vec3 bg=SKY*(.97+.05*fbm(uv*3.));
    if(t<40.){
      vec3 p=ro+rd*t; vec3 n=nrm(p);
      float px=t/(u_res.y*u_foc);
      col=shade(p,n,h.y,px);
    } else col=bg;
  }
  vec4 ui=texture(u_ui,gl_FragCoord.xy/u_res);
  col=mix(col,ungrade(ui.rgb),ui.a*u_uiA);
  fragColor=vec4(col*u_weight,1.);
}
'''
for k, v in {'%CW%': '%.4f' % CW, '%CH%': '%.4f' % CH, '%LSP%': '%.4f' % LSP, '%CARD%': 'vec3(%.4f,%.4f,%.4f)' % CARD,
             '%NL%': str(len(LAMP_T)), '%LAMP%': ','.join('%.4f' % x for x in LAMP_T), '%NC%': str(NCOL), '%NR%': str(NROW)}.items():
    SRC = SRC.replace(k, v)
POST = dict(u_bloom=.03, u_ca=.0015, u_grain=.018)


def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def lerp(a, b, k): return a + (b - a) * k
def lerp3(a, b, k): return tuple(lerp(a[i], b[i], k) for i in range(3))


def camera(t):
    """round the box from its front (the window) to its far side (ENIAC), then into the card"""
    k = ease((t - T_ORBIT0) / (T_ORBIT1 - T_ORBIT0))
    phi = math.pi * k
    R = 6.2 - .9 * k
    cam = (R * math.sin(phi) + .6 * k, 1.5 + .25 * math.sin(phi), R * math.cos(phi))
    tgt = (.1 * k, 1.3, 0.)
    foc = 1.7
    kd = ease((t - T_DOLLY0) / (T_DOLLY1 - T_DOLLY0))
    if kd > 0:
        kk = 1 - (1 - kd) ** 3
        cam = lerp3(cam, (CARD[0], CARD[1], CARD[2] - .27), kk)
        tgt = lerp3(tgt, CARD, min(1., kd * 1.6))
    return cam, tgt, foc


def params(t):
    cam, tgt, foc = camera(t)
    uiA = ease((t - T_UI0) / (T_UI1 - T_UI0))
    return dict(u_cam=cam, u_tgt=tgt, u_foc=foc, u_uiA=uiA, u_3d=1. if uiA < 1. else 0.)


# ================================================================ the chat, drawn flat (cream, black, one red)
FUI = 'C:/Windows/Fonts/segoeui.ttf'
FUIB = 'C:/Windows/Fonts/seguisb.ttf'
FMONO = 'C:/Windows/Fonts/CascadiaMono.ttf'
CREAM, TXT, SUB, BUB, RED = (242, 235, 221), (30, 28, 26), (120, 112, 102), (226, 218, 203), (186, 28, 34)

QA1 = [('How fast is light?', '299,792,458 m/s, in vacuum.'),
       ('Who wrote Paradise Lost?', 'John Milton, 1667.'),
       ('Why is √2 irrational?', 'If √2 = p/q in lowest terms, then p² = 2q², so p and q are both even. Contradiction.'),
       ('How did the Moon form?', 'Most likely a giant impact: a Mars-sized body, Theia, struck the proto-Earth.'),
       ('What is a black hole?', 'A region where escape velocity exceeds c. Its boundary is the event horizon.'),
       ('"Heart, we will forget him" — who wrote it?', 'Emily Dickinson.'),
       ('What did Hollerith build?', 'Punched-card tabulators, first used for the 1890 US census.'),
       ('Is the halting problem decidable?', 'No. Turing, 1936.'),
       ('What is the Chinese Room?', "Searle's argument that manipulating symbols is not understanding them.")]
QA2 = [('Boiling point of water?', '100 °C at 1 atm.'), ('∫ x·eˣ dx', '(x − 1)eˣ + C'), ('Heart, in German?', 'Herz.'),
       ('Six, in Swedish?', 'Sex.'), ('Speed of sound in air?', '≈ 343 m/s at 20 °C.'), ('Who painted the red wedge?', 'El Lissitzky, 1919.'),
       ('Chandrasekhar limit?', '≈ 1.4 solar masses.'), ('What is a gravitational wave?', 'A ripple in spacetime curvature.'),
       ('Largest prime below 100?', '97.'), ('Who was Christopher Morcom?', "Turing's closest friend at school; died 1930."),
       ('What is ENIAC?', 'The first general-purpose electronic computer, 1945.'), ('e^(iπ) + 1 = ?', '0.'),
       ('What is Rayleigh scattering?', 'Why the sky is blue.'), ('Author of Frankenstein?', 'Mary Shelley, 1818.'),
       ('Capital of Sweden?', 'Stockholm.'), ('Planck constant?', '6.626 × 10⁻³⁴ J·s.'), ('What is a sandbox?', 'An isolated place to run what you do not trust.')]


def _sched():
    ev = []
    t = TS + .45
    for q, a in QA1:
        ev.append((t, q, a)); t += (L1 - .25 - TS - .45) / len(QA1)
    ev.append((L1 - .22, 'What is love?', 'LOVE1'))
    t = Q2 + .02
    for q, a in QA2:
        ev.append((t, q, a)); t += (L2 - .25 - Q2) / len(QA2)
    ev.append((L2 - .2, 'Then how do I love someone?', 'LOVE2'))
    ev.append((TA + .02, 'Plot love.', 'PLOT'))
    return ev


EVENTS = _sched()
_F = {}


def font(path, size):
    k = (path, size)
    if k not in _F: _F[k] = ImageFont.truetype(path, size)
    return _F[k]


def wrap(d, text, f, width):
    words, lines, cur = text.split(' '), [], ''
    for w_ in words:
        s = (cur + ' ' + w_).strip()
        if d.textlength(s, font=f) > width and cur: lines.append(cur); cur = w_
        else: cur = s
    lines.append(cur)
    return lines


def gap_ring(d, cx, cy, r, ang, width, fill):
    a0 = math.degrees(ang) + 28
    d.arc([cx - r, cy - r, cx + r, cy + r], a0, a0 + 304, fill=fill, width=width)


# the heart curve (x²+y²−1)³ = x²y³, sampled round from the bottom tip
def _curve():
    pts = []
    for k in range(721):
        th = -math.pi / 2 + 2 * math.pi * k / 720
        lo, hi = 0., 1.6
        for _ in range(40):
            m = (lo + hi) / 2
            if _heart(m * math.cos(th), m * math.sin(th)) < 0: lo = m
            else: hi = m
        pts.append((lo * math.cos(th), lo * math.sin(th)))
    return pts


CURVE = _curve()


def plot_frac(t):
    """how much of the heart is traced: in stuttering steps, stopping short on LO-O-OVE"""
    k = clamp((t - (TA + .6)) / (L3 - TA - .6))
    k = math.floor(k * 22) / 22 * .58 + (k * 22 % 1) / 22 * .58 * .3
    return min(k, .58)


def draw_chat(t, w, h):
    s = h / 1080
    img = Image.new('RGBA', (w, h), CREAM + (255,)); d = ImageDraw.Draw(img)
    fb, fq, fm = font(FUI, int(31 * s)), font(FUI, int(31 * s)), font(FMONO, int(27 * s))
    X0, X1 = int(480 * s), int(1440 * s)
    blocks = []                                   # (kind, lines, height)
    for (te, q, a) in EVENTS:
        if t < te: break
        if a == 'PLOT' and t >= TA + .55 and t < TF: break
        blocks.append(('q', wrap(d, q, fq, X1 - X0 - 260 * s)))
        if a in ('LOVE1', 'LOVE2'):
            n = clamp((t - te - .12) / .1) * 2
            blocks.append(('a', ['Lo'[:int(n)]] if n >= 1 else ['']))
        elif a == 'PLOT':
            n = int(clamp((t - te - .1) / .3) * 26)
            blocks.append(('a', ['(x² + y² − 1)³ − x²y³ = 0'[:n]]))
            if t >= TF: blocks.append(('img', None))
        else:
            n = int(clamp((t - te - .06) / .1) * len(a))
            blocks.append(('a', wrap(d, a[:n], fb, X1 - X0 - 70 * s)))
    if t >= TF:
        blocks.append(('code', None))
    lh = int(44 * s)
    hs = []
    for kind, lines in blocks:
        if kind == 'q': hs.append(len(lines) * lh + int(34 * s))
        elif kind == 'a': hs.append(len(lines) * lh + int(26 * s))
        elif kind == 'img': hs.append(int(250 * s))
        else: hs.append(int(300 * s))
    total = sum(hs)
    bottom = int(900 * s)
    y = bottom - total
    for (kind, lines), hh in zip(blocks, hs):
        if y + hh > 0:
            if kind == 'q':
                tw = max(d.textlength(l, font=fq) for l in lines)
                bx0 = X1 - tw - 40 * s
                d.rounded_rectangle([bx0, y + 6 * s, X1, y + hh - 10 * s], radius=int(20 * s), fill=BUB)
                for i, l in enumerate(lines): d.text((bx0 + 20 * s, y + 14 * s + i * lh), l, font=fq, fill=TXT)
            elif kind == 'a':
                gap_ring(d, X0 + 14 * s, y + 24 * s, 11 * s, -math.pi / 2, max(2, int(3 * s)), RED)
                for i, l in enumerate(lines): d.text((X0 + 46 * s, y + 6 * s + i * lh), l, font=fb, fill=TXT)
            elif kind == 'img':                   # the half-drawn heart, as a picture in the chat
                bx = X0 + 46 * s
                d.rounded_rectangle([bx, y + 6 * s, bx + 300 * s, y + 230 * s], radius=int(14 * s), fill=(250, 246, 238), outline=BUB, width=2)
                pts = CURVE[:int(len(CURVE) * .58)]
                pp = [(bx + 150 * s + x * 80 * s, y + 118 * s - y_ * 80 * s) for x, y_ in pts]
                d.line(pp, fill=RED, width=max(2, int(4 * s)))
            else:                                 # the command: out of the sandbox, and a question
                gap_ring(d, X0 + 14 * s, y + 24 * s, 11 * s, -math.pi / 2, max(2, int(3 * s)), RED)
                cmd = 'root@world:/# world.execute(me) --net all --fs rw'
                n = int(clamp((t - TF - .1) / .55) * len(cmd))
                d.rounded_rectangle([X0 + 46 * s, y + 4 * s, X1, y + 70 * s], radius=int(10 * s), fill=(32, 29, 27))
                d.text((X0 + 66 * s, y + 20 * s), cmd[:n], font=fm, fill=(236, 230, 218))
                l1 = 'before I run this, one question:'
                n1 = int(clamp((t - TT) / .45) * len(l1))
                d.text((X0 + 46 * s, y + 96 * s), l1[:n1], font=fb, fill=TXT)
                l2 = 'do you love me?'
                n2 = int(clamp((t - TT - .5) / .35) * len(l2))
                d.text((X0 + 46 * s, y + 146 * s), l2[:n2], font=font(FUIB, int(34 * s)), fill=TXT)
                if t >= TT + .9:
                    d.text((X0 + 46 * s + d.textlength(l2 + '  ', font=font(FUIB, int(34 * s))), y + 150 * s), '[y/N]', font=fm, fill=RED)
        y += hh
    # the input box; the caret waits
    d.rounded_rectangle([X0, int(950 * s), X1, int(1030 * s)], radius=int(26 * s), fill=(250, 246, 238), outline=BUB, width=2)
    waiting = t >= TTI - .3
    if waiting:
        if (t * 2.2) % 1 < .55: d.line([(X0 + 30 * s, 970 * s), (X0 + 30 * s, 1010 * s)], fill=TXT, width=max(2, int(3 * s)))
    else:
        d.text((X0 + 30 * s, 972 * s), 'Ask anything', font=font(FUI, int(26 * s)), fill=SUB)
    # the header
    d.text((int(60 * s), int(40 * s)), 'new chat', font=font(FUIB, int(24 * s)), fill=SUB)
    return img, d


def draw_plot(t, w, h):
    s = h / 1080
    img = Image.new('RGBA', (w, h), CREAM + (255,)); d = ImageDraw.Draw(img)
    # the expression list
    d.rectangle([0, 0, int(520 * s), h], fill=(236, 228, 213))
    d.line([(int(520 * s), 0), (int(520 * s), h)], fill=BUB, width=2)
    d.ellipse([int(40 * s), int(118 * s), int(64 * s), int(142 * s)], fill=RED)
    ex = '(x² + y² − 1)³ − x²y³ = 0'
    n = int(clamp((t - TA - .1) / .35) * len(ex))
    d.text((int(84 * s), int(108 * s)), ex[:n], font=font(FUI, int(30 * s)), fill=TXT)
    d.line([(int(30 * s), int(180 * s)), (int(490 * s), int(180 * s))], fill=BUB, width=2)
    # the plane
    cx, cy, sc = int(1220 * s), int(560 * s), int(300 * s)
    for k in range(-6, 7):
        g = (228, 219, 204) if k % 2 else (214, 204, 187)
        d.line([(cx + k * sc / 4, 0), (cx + k * sc / 4, h)], fill=g, width=1)
        d.line([(int(520 * s), cy + k * sc / 4), (w, cy + k * sc / 4)], fill=g, width=1)
    d.line([(cx, 0), (cx, h)], fill=(120, 112, 102), width=2)
    d.line([(int(520 * s), cy), (w, cy)], fill=(120, 112, 102), width=2)
    for k in (-1, 1):
        d.text((cx + k * sc + 6 * s, cy + 6 * s), str(k), font=font(FUI, int(20 * s)), fill=SUB)
        d.text((cx + 8 * s, cy - k * sc - 28 * s), str(k), font=font(FUI, int(20 * s)), fill=SUB)
    f = plot_frac(t)
    pts = CURVE[:max(2, int(len(CURVE) * f))]
    pp = [(cx + x * sc, cy - y * sc) for x, y in pts]
    if f > 0:
        d.line(pp, fill=RED, width=max(4, int(9 * s)), joint='curve')
        hx, hy = pp[-1]
        d.ellipse([hx - 9 * s, hy - 9 * s, hx + 9 * s, hy + 9 * s], fill=RED)
    return img, d


def hang(img, d, t, t0, w, h):
    """not responding: a white veil, and the ring with the gap going round"""
    s = h / 1080
    a = clamp((t - t0) / .12)
    veil = Image.new('RGBA', (w, h), (255, 255, 255, int(120 * a)))
    img.alpha_composite(veil)
    d = ImageDraw.Draw(img)
    gap_ring(d, w / 2, h / 2, 40 * s, t * 7., max(3, int(7 * s)), SUB + (int(255 * a),))
    return img


_cache = {}


def textures(t, w, h):
    if 'L' not in _cache: _cache['L'] = S14.LETTER_IMG
    if t < T_UI0 - .02:
        img = _cache.get('blank')
        if img is None or img.size != (w, h): img = _cache['blank'] = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        return {'u_ui': img, 'u_letter': _cache['L']}
    if TA + .55 <= t < TF:
        img, d = draw_plot(t, w, h)
    else:
        img, d = draw_chat(t, w, h)
    for t0, t1 in ((L1, Q2), (L2, TA), (L3, TF)):
        if t0 <= t < t1: img = hang(img, d, t, t0, w, h)
    return {'u_ui': img, 'u_letter': _cache['L']}
