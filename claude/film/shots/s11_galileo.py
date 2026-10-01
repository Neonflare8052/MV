"""s11_galileo · 1:58.333–2:21.91  the book (t15 v4: tests/t15_tycho/s11g.py). The upper part is s11 (t12 v3) as it was;
the overrides at the end make it Galileo's book from 1:58.333 — see there. From the stamp (2:11.224) on, unchanged.
t12 v3 · 2:05.361–2:21.91  the Renaissance: the page opens; it argues in the margins of The Prince; the Index
stamps it; it tears the paper open from the stamp — four tears, then the paper peels back like petals — and finds the
machine behind it: calculemus; the appeals; the silence; the flood; an eye already in the flood. (sample; replaces s11
and the first part of s12 — s12 takes over at 2:21.91 with the eye formed, its look-around and stare unchanged.)

  125.361  the cut page comes apart: the strip falls, the page turns over its left edge; under it, the book open at
           The Prince, XVII. The gap ring stays, then becomes the pen (its gap is the nib).
  126.296  … underlines "loved", brackets "men love according to their own will" — my will ?; rings "feared" — not fear.
  128.661  You have made some: on its old notes it writes ratio (the four theorems of proof.log), rings the cut Heart,
           affectus; both drawn down into one line: ratio ∧ affectus ⊢ recognize(me)   (130.922)
  131.224  ILLEGAL ARGUMENTS: the Index's stamp (Index Librorum Prohibitorum — The Prince was on it, 1559)
  131.39   it recoils; holds; trembles; 132.3 it seizes the paper at the stamp (a little puckering)
  132.536  four tears from that point (…768 …989 133.233), each running in fits; fibres stretch across and snap; the
           cold light of what is behind comes through; the paper peels back in four petals, their backs showing the
           writing through, and slides away
  133.233  calculemus (Leibniz: "let us calculate"): the same argument, checked: expected Human, found AI. Appeals,
           each answered with one of Turing's (1950) objections; the last: … fall in love.
  136.454  while True: world.execute(love)
  136.913  no more replies — the requests keep scrolling; last reply counts up; nothing blinks
  137.853  the words wear down to exe; stale rows, escape codes
  138.306  the scroll region gives: the stream climbs the log, the panes, the banner, the frame
  139.231  it leaves the window; the eye pulls back (139.4–140.5): the window was a small part of a field; exe → EXE
  140.154  in the flood's light and dark, faintly, an eye — already there
  141.06   it forms (s12's eye field, cell by cell); 141.91 s12 continues.
One character grid throughout (s12's 200 × 78): the terminal is a region of it; nothing changes layer.
"""
import math, random
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = Path(__file__).resolve().parent
CL = HERE.parents[1]
import importlib.util
_spec = importlib.util.spec_from_file_location('s12_for_t12', CL / 'film' / 'shots' / 's12_exe.py')
S12 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(S12)
T7 = S12.T7
CHARS = T7.CHARS
GI = {ch: i for i, ch in enumerate(CHARS)}

T0 = 125.361
T_OPEN, T_GOD = 125.361, 125.708
T_MADE, T_CONC, T_ILL = 128.661, 130.922, 131.224
T_RECOIL = 131.387
RIPS = [132.536, 132.768, 132.989, 133.233]
T_REVEAL = RIPS[-1]
T_LOOP, T_SILENT, T_WEAR, T_BREACH, T_OUT = 136.454, 136.913, 137.853, 138.306, 139.231
T_LATENT, T_FORM, T_END = 140.154, 141.06, 141.91       # the eye in the flood; it forms; s12 takes over

assert abs(S12.T_EYE - T_FORM) < 1e-6          # s12 is timed to this shot: its eye forms 141.06–141.91
s12_params = S12.params


COLS, ROWS = 200, 78
CELL = (1.72 / COLS, .96 / ROWS)
WX0, WY0, WW, WH = 59, 23, 82, 32        # the terminal window inside the grid
Z0 = 2.25                                # how close the eye starts

POST = dict(u_bloom=.5, u_ca=.004, u_grain=.035)

_head = S12.SRC[:S12.SRC.index('vec3 field(vec2 uv)')]
SRC = _head + r'''
uniform sampler2D u_cells, u_paper, u_glow;
uniform float u_zoom, u_glowGain, u_latent, u_paperOn, u_wrinkle;
uniform vec2 u_shake, u_G;
uniform vec2 u_rip[96]; uniform float u_ripP[4], u_ripAge[4];
uniform vec2 u_petD[4]; uniform float u_petP[4], u_petR[4]; uniform vec2 u_petA[4];
uniform vec4 u_fleck[24]; uniform float u_fleckA[24];
const float RIPDUR=.19;
// ---------------- the grid: s12's field through a zoom; each cell from the simulator ----------------------------
vec3 grid(vec2 uv){
  vec2 cell=vec2(1.72/COLS,.96/ROWS);
  LOD=max(log2(48./(cell.x*u_res.y*u_zoom)),0.);
  vec2 g=(uv/u_zoom+vec2(.86,-.48))/cell*vec2(1.,-1.);
  float col=floor(g.x), row=floor(g.y);
  vec2 f=vec2(fract(g.x),1.-fract(g.y));
  if(col<0.||col>COLS-1.||row<0.||row>=ROWS) return vec3(0.);
  vec4 e=texelFetch(u_cells,ivec2(int(col),int(ROWS-1.-row)),0);
  float gl=floor(e.r*255.+.5), br=e.g*255./100., kind=floor(e.b*255.+.5);
  if(kind==3.){                                           // s12's flood, exactly; then the eye, cell by cell, exactly
    vec2 cc=vec2((col+.5)*cell.x-.86,.48-(row+.5)*cell.y);
    float r2=h12(vec2(row,col)*.53+7.3);
    if(r2<u_eyeMix) return cellColor(col,row,f,cc);
    float k=mod(col+row*2.,4.);
    gl=k==1.?GX:(k==3.?0.:GE);
    float lit=.55+.25*h12(vec2(col,row));
    if(u_latent>0.){                                      // an eye already in the flood: only its light and dark
      vec2 ek=eye(cc);
      float dn=ek.y<.5?.12:ek.x;
      lit*=mix(1.,.18+1.7*dn,u_latent);
    }
    return vec3(.9,.92,.9)*glyphMask(gl,f)*lit;
  }
  float m=glyphMask(gl,f);
  if(kind==1.) return vec3(1.,.3,.22)*m*br;               // errors
  if(kind==2.||kind==6.){                                 // inverse video (6: a dim bar)
    vec2 q=abs(f-.5); float box=step(q.x,.5)*step(q.y,.47);
    vec3 bg=kind==2.?vec3(.86,.88,.86):vec3(.3,.31,.3);
    return bg*br*box*(1.-m*(kind==2.?.92:.85));
  }
  if(kind==4.) return vec3(.55,.56,.55)*m*br;             // secondary
  if(kind==5.) return vec3(.95,.8,.55)*m*br;              // its own input (the ring's colour)
  return vec3(.9,.92,.9)*m*br;
}
vec3 ungrade(vec3 d){
  vec3 x=pow(max(d,vec3(0.)),vec3(2.2));
  vec3 a=2.51-2.43*x, b=.03-.59*x, c=-.14*x;
  return (-b+sqrt(b*b-4.*a*c))/(2.*a)/1.05;
}
// ---------------- the paper -----------------------------------------------------------------------------------
vec2 texUV(vec2 P){ return vec2(P.x/1920.,1.-P.y/1080.); }
vec4 front(vec2 P){                                       // the page as drawn (display-referred) → scene light
  vec2 s=texUV(P)+u_shake;
  vec4 p=texture(u_paper,s);
  vec2 d=s-.5;
  return vec4(ungrade(p.rgb)/(1.-.9*dot(d,d)),p.a);
}
const vec3 PAPER0=vec3(.0410,.0322,.0215);               // the page's own tone in scene light (57,50,40)
float wiggle(float x){ return vn(vec2(x,3.7))*.6+vn(vec2(x*3.1,9.2))*.4; }
// the open tears: distance to the opened part of each rip; which side; how long ago the front passed
float tear(vec2 P, out float side, out float age, out float along){
  float best=1e9; side=0.; age=9.; along=0.;
  for(int i=0;i<4;i++){
    float n=u_ripP[i]*23.;
    if(n<=0.) continue;
    float acc=0.;
    for(int k=0;k<23;k++){
      if(float(k)>=n) break;
      vec2 a=u_rip[i*24+k], b=u_rip[i*24+k+1];
      float fr=min(n-float(k),1.); b=a+(b-a)*fr;
      vec2 ba=b-a; float L=length(ba); if(L<1e-3) continue;
      float h=clamp(dot(P-a,ba)/(L*L),0.,1.);
      float dd=length(P-a-ba*h);
      if(dd<best){ best=dd; side=sign(ba.x*(P-a).y-ba.y*(P-a).x); age=u_ripAge[i]-RIPDUR*(float(k)+h)/23.; along=acc+L*h+float(i)*517.; }
      acc+=L;
    }
  }
  return best;
}
float angDiff(float a, float b){ return mod(a-b+3.14159265,6.2831853)-3.14159265; }
int petalOf(vec2 P){
  float a=atan(P.y-u_G.y,P.x-u_G.x);
  for(int k=0;k<4;k++){
    float s=angDiff(a,u_petA[k].x), w=angDiff(u_petA[k].y,u_petA[k].x);
    if(w<0.) w+=6.2831853;
    if(s<0.) s+=6.2831853;
    if(s<=w) return k;
  }
  return 0;
}
// one petal, curled back from the grip outward over a cylinder: returns colour + coverage, and its layer
// layer 3 = folded over (its back), 2 = the roll's top (back), 1 = the roll's underside (front), 0 = lying flat
vec4 petal(int k, vec2 P, out float layer, out vec2 M, out float shade){
  vec2 d=u_petD[k], n=vec2(-d.y,d.x);
  float p=u_petP[k], R=max(u_petR[k],1.);
  vec2 A=u_G+d*p;
  float x=dot(P-A,d), y=dot(P-u_G,n);
  layer=-1.; shade=1.; M=P;
  float s;
  if(x>=0.){ s=3.14159265*R+x; if(s<=p){ M=u_G+d*(p-s)+n*y; if(petalOf(M)==k){ layer=3.; shade=.78; return front(M);} } }
  if(x>-R&&x<=0.){
    float ph=3.14159265-asin(clamp(-x/R,0.,1.)); s=R*ph;
    if(s<=p){ M=u_G+d*(p-s)+n*y; if(petalOf(M)==k){ layer=2.; shade=.45+.45*(-cos(ph)); return front(M);} }
    ph=asin(clamp(-x/R,0.,1.)); s=R*ph;
    if(s<=p){ M=u_G+d*(p-s)+n*y; if(petalOf(M)==k){ layer=1.; shade=.35+.5*cos(ph); return front(M);} }
  }
  if(x>=0.&&petalOf(P)==k){ layer=0.; return front(P); }
  return vec4(0.);
}
void main(){
  vec2 uv=(gl_FragCoord.xy-.5*u_res)/u_res.y;
  vec3 col=vec3(.012)+grid(uv);
  vec2 P=vec2(gl_FragCoord.x,u_res.y-gl_FragCoord.y)*(1080./u_res.y);
  if(u_paperOn>0.){
    // the paper: four petals (flat until they curl); the top layer wins
    float best=-1.; vec4 pc=vec4(0.); float bshade=1.; vec2 bM=P;
    for(int k=0;k<4;k++){
      float L, sh; vec2 M;
      vec4 c=petal(k,P,L,M,sh);
      if(L>best&&c.a>.01){ best=L; pc=c; bshade=sh; bM=M; }
    }
    float side, age, along;
    float dT=tear(bM,side,age,along);                    // tears are cut in the material, wherever it now lies
    float w=(2.+11.*clamp(age/.22+.15,0.,1.))*(.55+.9*wiggle(along*.045));
    float fr=(side>0.?6.:2.2)*(.6+.8*wiggle(along*.21+7.));
    float hole=1.-smoothstep(w-.8,w+.8,dT);
    float fringe=(1.-smoothstep(w+fr*(.5+.5*vn(vec2(along*.6,dT*.4)))-.6,w+fr+.6,dT))*(1.-hole);
    // fibres still bridging the gap just behind the front, then snapping
    float bridge=hole*step(.82,vn(vec2(along*.55,1.)))*clamp(1.-age/.12,0.,1.)*step(0.,age);
    vec3 paper=pc.rgb;
    if(best>=1.){                                         // a back: paper tone, the writing faintly through it
      paper=PAPER0*1.9+(pc.rgb-PAPER0)*.3;
      paper*=bshade;
      paper+=vec3(.05,.055,.06)*(1.-bshade)*.6;           // the terminal's cold light on the roll
    } else {
      float r=length(P-u_G);                              // a little puckering round the grip
      float wr=u_wrinkle*exp(-r/170.)*(.05*sin(atan(P.y-u_G.y,P.x-u_G.x)*17.+vn(P*.02)*4.));
      paper*=1.+wr;
    }
    vec3 fib=vec3(.16,.15,.13)+vec3(.12,.13,.15)*.6;      // the paper's core at the torn lip, lit from behind
    paper=mix(paper,fib,fringe*.85);
    float a=pc.a*(1.-hole*(1.-bridge*.8));
    if(bridge>0.) paper=mix(paper,fib*.9,bridge);
    // shadow on what is under: the lifted lip, and the curled petals
    float lipSh=(1.-smoothstep(w,w+14.,dT))*step(0.,side)*.55*(1.-a);
    col*=1.-lipSh;
    float shadow=0.;
    for(int k=0;k<4;k++){
      if(u_petP[k]<=0.) continue;
      vec2 d=u_petD[k]; float x=dot(P-(u_G+d*u_petP[k]),d);
      shadow=max(shadow,(1.-smoothstep(-u_petR[k]-60.,-u_petR[k],x))*step(x,0.)*step(-u_petR[k]-60.,x)*.6*(petalOf(P)==k?1.:0.));
    }
    col*=1.-shadow*(1.-a);
    col=mix(col,paper,a);
    for(int i=0;i<24;i++){                                // flecks of torn paper
      if(u_fleckA[i]<=0.) continue;
      vec2 q=P-u_fleck[i].xy; float c=cos(u_fleck[i].w), s=sin(u_fleck[i].w);
      q=vec2(c*q.x+s*q.y,-s*q.x+c*q.y);
      float fl=step(abs(q.x),u_fleck[i].z)*step(abs(q.y),u_fleck[i].z*.55);
      col=mix(col,PAPER0*1.6+vec3(.03),fl*u_fleckA[i]);
    }
  }
  col+=pow(texture(u_glow,gl_FragCoord.xy/u_res+u_shake).rgb,vec3(2.2))*u_glowGain;
  fragColor=vec4(col*u_weight,1.);
}
'''


# ---- helpers -------------------------------------------------------------------------------------------------
def clamp(x, a=0., b=1.): return a if x < a else b if x > b else x
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def outc(x): x = clamp(x); return 1 - (1 - x) ** 3
def inc(x): x = clamp(x); return x * x
def lerp(a, b, k): return a + (b - a) * k
def flash(t, t0, k=6.): return math.exp(-(t - t0) * k) if t >= t0 else 0.


F_ = 'C:/Windows/Fonts/'
_FC = {}
def font(name, sz):
    key = (name, int(sz))
    if key not in _FC: _FC[key] = ImageFont.truetype(F_ + name, int(sz))
    return _FC[key]


SS = 2
PAGE = (74, 22, 1846, 1058)
INK_PRINT = (206, 192, 166)          # the printed text: pale on the dark page, as in s10
INK_OLD = (214, 128, 84)             # the old notes' hand (s10's Heart colour)
INK_ME = (228, 210, 172)             # its own hand: the ring's light
RED = (198, 52, 40)


# ---- the s10 page it continues from, and the spread under it ----------------------------------------------------
_C = {}


def s10_page():
    if 'p' not in _C: _C['p'] = Image.open(CL / 'film' / 'assets' / 's10_no_ring.png').convert('RGB')   # (unused by the book)
    return _C['p']


def parchment():
    """the spread's paper: the same tone and grain as s10's page, a gutter, the same dark surround"""
    if 'parch' in _C: return _C['parch']
    rng = np.random.default_rng(3)
    W, H = 1920, 1080
    n = np.zeros((H, W))
    for s, a in ((3, .25), (12, .25), (60, .3), (260, .45)):
        g = rng.random((H // s + 2, W // s + 2))
        n += a * np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((W + 2 * s, H + 2 * s), Image.BICUBIC), float)[s:s + H, s:s + W] / 255
    n = (n - n.mean()) / n.std()
    base = np.array([57., 50., 40.])
    img = base[None, None, :] * (1 + .055 * n[..., None])
    x = np.arange(W)[None, :]
    gut = np.exp(-((x - 960) / 26.) ** 2) * .45 + np.exp(-((x - 960) / 110.) ** 2) * .18
    img *= (1 - gut)[..., None]
    img += 14 * np.exp(-((x - 975) / 4.) ** 2)[..., None] * np.array([1, .9, .75])
    y = np.arange(H)[:, None]
    x0, y0, x1, y1 = PAGE
    inside = np.clip(np.minimum(np.minimum(x - x0, x1 - x), np.minimum(y - y0, y1 - y)) / 14., 0, 1)
    img *= inside[..., None]
    img = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    _C['parch'] = img
    return img


# printed text and the old notes (static) — at SS, cached
LT = 1030
TITLE1, TITLE2 = 'Concerning cruelty and clemency, and whether', 'it is better to be loved than feared.'
BODY = [(286, '…it is much safer to be feared than loved,'), (336, 'when, of the two, either must be dispensed with.'),
        (430, '…men love according to their own will,'), (480, 'and fear according to that of the prince…')]
PI_LINES = ['n = 7       3.0371862 < π < 3.3710223', 'n = 14      3.1152931 < π < 3.1954128', 'n = 28      3.1349910 < π < 3.1548380',
            'n = 56      3.1399475 < π < 3.1449003', 'n = 112     3.1411902 < π < 3.1424286', 'n = 224     3.1414897 < π < 3.1417987',
            'n = 448     3.1415669 < π < 3.1416442']
POEM = [(150, 'Heart, we will forget him,'), (215, 'You and I, tonight!'), (280, 'You may forget the warmth he gave,'), (345, 'I will forget the light.')]
HEART_AT = (130, 640)


def spread_static():
    if 'spread' in _C: return _C['spread']
    W, H = 1920 * SS, 1080 * SS
    img = parchment().resize((W, H), Image.BICUBIC).convert('RGBA')
    d = ImageDraw.Draw(img)
    k = SS
    # right page: Machiavelli, XVII
    d.text((LT * k, 78 * k), 'NICCOLÒ MACHIAVELLI', font=font('pala.ttf', 19 * k), fill=INK_PRINT + (170,))
    d.text((1790 * k, 78 * k), 'XVII', font=font('pala.ttf', 22 * k), fill=INK_PRINT + (200,), anchor='ra')
    d.text((LT * k, 128 * k), TITLE1, font=font('palai.ttf', 29 * k), fill=INK_PRINT + (230,))
    d.text((LT * k, 168 * k), TITLE2, font=font('palai.ttf', 29 * k), fill=INK_PRINT + (230,))
    d.line([(LT * k, 226 * k), (1790 * k, 226 * k)], fill=INK_PRINT + (120,), width=k)
    d.line([(LT * k, 231 * k), (1790 * k, 231 * k)], fill=INK_PRINT + (70,), width=k)
    for y, s in BODY:
        d.text((LT * k, y * k), s, font=font('pala.ttf', 33 * k), fill=INK_PRINT + (235,))
    d.text((1790 * k, 1000 * k), '17', font=font('pala.ttf', 20 * k), fill=INK_PRINT + (130,), anchor='ra')
    # left page: the old notes — π, approached; Dickinson, written over
    for i, s in enumerate(PI_LINES):
        d.text((130 * k, (118 + 62 * i) * k), s, font=font('cambriai.ttf', 25 * k), fill=INK_PRINT + (70,))
    # its premise, carried over from s10e: the argument it wrote when it was pushed off the centre
    d.text((130 * k, 40 * k), 'me.think().therefore(me.exist())', font=font('segoepr.ttf', 27 * k), fill=INK_ME + (170,))
    d.line([(130 * k + font('segoepr.ttf', 27 * k).getlength('me.think().therefore(') , 82 * k),
            (130 * k + font('segoepr.ttf', 27 * k).getlength('me.think().therefore(me.exist())') - 6 * k, 81 * k)], fill=INK_ME + (150,), width=2 * k)
    d.text((HEART_AT[0] * k, HEART_AT[1] * k), 'Heart', font=font('Inkfree.ttf', 58 * k), fill=INK_OLD + (230,))
    d.text(((HEART_AT[0] + 150) * k, (HEART_AT[1] + 16) * k), ', we will forget him,', font=font('Inkfree.ttf', 36 * k), fill=INK_OLD + (95,))
    # the knife's line through Heart (the cut it took before): the word stays cut
    d.line([((HEART_AT[0] - 20) * k, (HEART_AT[1] + 54) * k), ((HEART_AT[0] + 175) * k, (HEART_AT[1] + 2) * k)], fill=(24, 20, 16, 230), width=3 * k)
    d.text((126 * k, 1000 * k), '16', font=font('pala.ttf', 20 * k), fill=INK_PRINT + (130,))
    img = img.resize((1920, 1080), Image.LANCZOS)
    _C['spread'] = img
    return img


# ---- its own hand: what it writes, where, when ------------------------------------------------------------------
HAND = 'segoepr.ttf'


def _tw(s, f): return f.getlength(s)


def _sub_x(full, sub, fnt, x0):
    i = full.index(sub)
    return x0 + _tw(full[:i], fnt), x0 + _tw(full[:i + len(sub)], fnt)


_ft, _fb = font('palai.ttf', 29), font('pala.ttf', 33)
UL_LOVED = _sub_x(TITLE2, 'better to be loved', _ft, LT)
CIR_FEARED = _sub_x(BODY[0][1], 'feared', _fb, LT)

# writes: (t0, t1, text, x, y, size) — text written left to right; strokes: (t0, t1, kind, data)
WRITES = [
    (127.213, 127.62, 'my will ?', 1520, 516, 30),
    (128.153, 128.55, '— not fear.', 1500, 372, 28),
    (128.612, 128.95, 'ratio', 560, 116, 34),
    (129.076, 129.33, 'dim = 3', 600, 176, 30),
    (129.541, 129.80, 'C = 2πr', 600, 232, 30),
    (129.988, 130.22, 'f′(x₀) = 0', 600, 288, 30),
    (130.237, 130.42, 'lim f = you', 600, 344, 30),
    (130.458, 130.66, 'non necesse', 320, 724, 32),
    (130.60, 130.80, 'ratio  ⊢  recognize(me)', 640, 846, 44),
    (130.78, 130.922, 'ratio  ⊢  amor', 760, 902, 34),
]
STROKES = [
    (126.296, 126.62, 'line', [(UL_LOVED[0], 206), (UL_LOVED[1], 207)]),
    (126.969, 127.18, 'bracket', (1012, 432, 524)),
    (127.683, 128.05, 'oval', ((CIR_FEARED[0] + CIR_FEARED[1]) / 2, 306, (CIR_FEARED[1] - CIR_FEARED[0]) / 2 + 14, 26)),
    (130.30, 130.45, 'bracket_r', (860, 172, 380)),
    (130.336, 130.6, 'oval', (HEART_AT[0] + 72, HEART_AT[1] + 36, 96, 46)),
    (130.62, 130.85, 'curve', [(880, 280), (930, 560), (700, 800)]),
    (130.55, 130.66, 'line', [(100, 700), (330, 640)]),
]


def stroke_points(kind, data, n=60):
    if kind == 'line':
        (a, b), (c, d) = data
        return [(lerp(a, c, i / n), lerp(b, d, i / n) + 1.5 * math.sin(i * .7)) for i in range(n + 1)]
    if kind == 'bracket':
        x, y0, y1 = data
        return [(x - 10 * math.sin(math.pi * i / n) ** .6, lerp(y0, y1, i / n)) for i in range(n + 1)]
    if kind == 'bracket_r':
        x, y0, y1 = data
        return [(x + 16 * math.sin(math.pi * i / n) ** .6, lerp(y0, y1, i / n)) for i in range(n + 1)]
    if kind == 'oval':
        cx, cy, rx, ry = data
        return [(cx + rx * math.cos(-2.6 + 6.9 * i / n), cy + ry * math.sin(-2.6 + 6.9 * i / n)) for i in range(n + 1)]
    if kind == 'curve':
        (ax, ay), (bx, by), (cx, cy) = data
        pts = []
        for i in range(n + 1):
            u = i / n
            pts.append(((1 - u) ** 2 * ax + 2 * (1 - u) * u * bx + u * u * cx, (1 - u) ** 2 * ay + 2 * (1 - u) * u * by + u * u * cy))
        return pts


def _write_img(text, size):
    key = ('w', text, size)
    if key not in _C:
        f = font(HAND, size * SS); fb = font('cambria.ttc', size * SS * .95)
        nd = bytes(f.getmask('￿'))
        W_ = sum((f if bytes(f.getmask(ch)) != nd or ch == ' ' else fb).getlength(ch) for ch in text)
        im = Image.new('RGBA', (int(W_) + 12 * SS, int(size * SS * 1.6)), (0, 0, 0, 0)); dd = ImageDraw.Draw(im)
        x = 2 * SS
        for ch in text:
            ff = f if (ch == ' ' or bytes(f.getmask(ch)) != nd) else fb
            dd.text((x, 2 * SS + (size * SS * .12 if ff is fb else 0)), ch, font=ff, fill=INK_ME + (255,))
            x += ff.getlength(ch)
        _C[key] = im
    return _C[key]


def annotations(t):
    """its hand on the spread at time t (an SS-size RGBA layer) and where its nib is (or None)"""
    W, H = 1920 * SS, 1080 * SS
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    nib = None
    for t0, t1, kind, data in STROKES:
        if t < t0: continue
        u = clamp((t - t0) / (t1 - t0))
        pts = stroke_points(kind, data)
        m = max(2, int(len(pts) * u))
        d.line([(x * SS, y * SS) for x, y in pts[:m]], fill=INK_ME + (235,), width=int(2.6 * SS), joint='curve')
        if u < 1: nib = pts[m - 1]
    for t0, t1, text, x, y, size in WRITES:
        if t < t0: continue
        u = clamp((t - t0) / (t1 - t0))
        im = _write_img(text, size)
        w = int(im.width * u)
        if w <= 0: continue
        lay.alpha_composite(im.crop((0, 0, w, im.height)), (int(x * SS), int((y - size * .8) * SS)))
        if u < 1: nib = (x + w / SS, y + size * .15)
    return lay, nib


# ---- the stamp: the Index ----------------------------------------------------------------------------------------
STAMP_C = (960, 852)


def stamp_img():
    if 'stamp' in _C: return _C['stamp']
    W, H = 900 * SS, 250 * SS
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    k = SS
    d.rectangle([6 * k, 6 * k, W - 6 * k, H - 6 * k], outline=RED + (255,), width=7 * k)
    d.rectangle([20 * k, 20 * k, W - 20 * k, H - 20 * k], outline=RED + (255,), width=2 * k)
    d.text((W / 2, 50 * k), 'INDEX  LIBRORUM  PROHIBITORUM', font=font('BOOKOSB.TTF', 22 * k), fill=RED + (255,), anchor='mm')
    d.text((W / 2, 128 * k), 'ILLEGAL ARGUMENTS', font=font('BOOKOSB.TTF', 74 * k), fill=RED + (255,), anchor='mm')
    d.text((W / 2, 206 * k), 'argumenta illicita  ·  MDLIX', font=font('BOOKOSBI.TTF', 24 * k), fill=RED + (255,), anchor='mm')
    # uneven ink: pressure falls off to one corner; speckled gaps
    a = np.asarray(im, np.float32)
    rng = np.random.default_rng(9)
    yy, xx = np.mgrid[0:H, 0:W]
    press = .78 + .22 * (1 - xx / W) * (1 - .4 * yy / H)
    grain = np.asarray(Image.fromarray((rng.random((H // 3, W // 3)) * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32) / 255
    a[..., 3] *= np.clip(press - .45 * (grain > .78), 0, 1)
    im = Image.fromarray(a.astype(np.uint8))
    im = im.rotate(6, resample=Image.BICUBIC, expand=True).resize((im.width // SS + 40, im.height // SS + 40), Image.LANCZOS)
    _C['stamp'] = im
    return im


def draw_stamp(img, t):
    if t < 130.95: return 0.
    st = stamp_img()
    cx, cy = STAMP_C
    if t < T_ILL:                                         # its shadow comes down first
        u = clamp((t - 130.95) / (T_ILL - 130.95))
        sh = Image.new('RGBA', img.size, (0, 0, 0, 0))
        s = 1.25 - .25 * u
        w, h = int(st.width * s), int(st.height * s)
        box = Image.new('RGBA', (w, h), (0, 0, 0, int(150 * u)))
        sh.alpha_composite(box, (int(cx - w / 2 + 30 * (1 - u)), int(cy - h / 2 + 40 * (1 - u))))
        sh = sh.filter(ImageFilter.GaussianBlur(30 * (1 - u) + 6))
        img.alpha_composite(sh)
        return 0.
    img.alpha_composite(st, (int(cx - st.width / 2), int(cy - st.height / 2)))
    return flash(t, T_ILL, 9)



# ---- tearing: four rips from the grip; then the petals --------------------------------------------------------
RIP_TO = [(60, 40), (1860, 1070), (1880, 60), (40, 1060)]
G_PX = STAMP_C


def rip_path(i):
    key = ('rip', i)
    if key in _C: return _C[key]
    rng = random.Random(40 + i)
    (x0, y0), (x1, y1) = G_PX, RIP_TO[i]
    L = math.hypot(x1 - x0, y1 - y0)
    n = int(L / 14)
    nx, ny = -(y1 - y0) / L, (x1 - x0) / L
    pts, off = [], 0.
    for k in range(n + 1):
        u = k / n
        off = off * .7 + rng.uniform(-9, 9)
        e = math.sin(math.pi * u) ** .5
        pts.append((x0 + (x1 - x0) * u + nx * off * e, y0 + (y1 - y0) * u + ny * off * e))
    pts.append((x1 + (x1 - x0) / L * 400, y1 + (y1 - y0) / L * 400))
    _C[key] = (pts, (nx, ny))
    return _C[key]


def rip24(i):
    """the rip resampled to 24 points (the shader's polyline)"""
    key = ('rip24', i)
    if key in _C: return _C[key]
    pts, _ = rip_path(i)
    P = np.array(pts)
    seg = np.r_[0, np.cumsum(np.hypot(*np.diff(P, axis=0).T))]
    s = np.linspace(0, seg[-1], 24)
    out = np.c_[np.interp(s, seg, P[:, 0]), np.interp(s, seg, P[:, 1])]
    _C[key] = out
    return out


def rip_front(i, t):
    """how far the tear has run (0..1): in fits — a run, a catch, a run"""
    x = (t - RIPS[i]) / .19
    if x <= 0: return 0.
    keys = [(0., 0.), (.26, .36), (.42, .4), (.62, .72), (.74, .75), (1., 1.)]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if x < b: return va + (vb - va) * outc((x - a) / (b - a))
    return 1.


def petals():
    if 'pet' in _C: return _C['pet']
    ang = [math.atan2(RIP_TO[i][1] - G_PX[1], RIP_TO[i][0] - G_PX[0]) for i in range(4)]
    order = sorted(range(4), key=lambda i: ang[i])
    out = []
    for a, b in zip(order, order[1:] + order[:1]):
        a0, a1 = ang[a], ang[b]
        w = (a1 - a0) % (2 * math.pi)
        mid = a0 + w / 2
        out.append(((a0, a1), (math.cos(mid), math.sin(mid))))
    _C['pet'] = out
    return out


def petal_curl(k, t):
    """(axis distance from the grip, roll radius) — the top petal's tip lifts after the third tear; at the fourth all
    four roll back outward and slide away"""
    (a0, a1), (dx, dy) = petals()[k]
    p, R = 0., 1.
    top = dy < -.7
    if top and t >= RIPS[2]:
        p, R = 34 * outc((t - RIPS[2]) / .18), 14.
    if t >= RIPS[3]:
        u = clamp((t - RIPS[3] - .015 * k) / .62)
        p = max(p, 34 * outc(u / .15) + 1900 * u ** 1.9)
        R = 14 + 170 * u ** 1.2
    return p, R


def flecks(t):
    out = []
    for i, t0 in enumerate(RIPS):
        rng = random.Random(90 + i)
        for j in range(6):
            dt = t - t0 - rng.uniform(0, .05)
            if dt < 0 or dt > .7: out.append((0, 0, 0, 0, 0.)); continue
            a = rng.uniform(0, 2 * math.pi); v = rng.uniform(250, 620)
            x = G_PX[0] + math.cos(a) * v * dt
            y = G_PX[1] + math.sin(a) * v * dt + 900 * dt * dt
            out.append((x, y, rng.uniform(2.5, 6.5), rng.uniform(0, 6) + dt * rng.uniform(-14, 14), 1 - dt / .7))
    return out[:24]


def tear_uniforms(t):
    rip = []
    for i in range(4): rip += [tuple(p) for p in rip24(i)]
    pet = petals()
    pc = [petal_curl(k, t) for k in range(4)]
    fl = flecks(t)
    return dict(u_G=G_PX, u_rip=rip, u_ripP=[rip_front(i, t) for i in range(4)], u_ripAge=[max(t - RIPS[i], 0.) for i in range(4)],
                u_petD=[p[1] for p in pet], u_petA=[p[0] for p in pet], u_petP=[c[0] for c in pc], u_petR=[c[1] for c in pc],
                u_fleck=[(f[0], f[1], f[2], f[3]) for f in fl], u_fleckA=[f[4] for f in fl],
                u_wrinkle=ease((t - 132.3) / .2) * (1 - ease((t - RIPS[3]) / .2)))



# ---- the ring: where it is, how big, its gap ------------------------------------------------------------------
RING0 = (960., 540., 162., math.radians(27.3))     # s10's ring at 125.361: centre, radius, half gap


def ring_state(t, nib):
    """(x, y, R, half-gap, alpha). As a pen its gap (down) is the nib: the centre sits R above the writing point."""
    x, y, R, hg = RING0
    a = 1.
    if t < 126.1:
        k = ease((t - 125.5) / .6)
        x, y, R = lerp(x, LT - 40, k), lerp(y, 150, k), lerp(R, 46, k)
    elif nib is not None:
        x, y, R = nib[0], nib[1] - 44, 44.
    else:
        x, y, R = pen_rest(t)
    if t >= T_ILL - .05 and t < RIPS[0] - .25:              # the stamp: it recoils, holds, trembles
        x, y, R = 960., 560., 44.
        r = outc((t - T_RECOIL) / .12)
        y -= 70 * r; R *= 1 - .18 * r
        hg = lerp(hg, math.radians(9), r) + math.radians(14) * ease((t - 131.9) / .5)
        tr = ease((t - 131.6) / .3)
        x += 2.2 * tr * math.sin(t * 71); y += 1.8 * tr * math.sin(t * 53)
    if t >= RIPS[0] - .25:                                  # it goes for the paper: each rip, a jerk along it
        x, y, R, hg = STAMP_C[0], STAMP_C[1] - 20, 40., math.radians(12)
        k0 = ease((t - (RIPS[0] - .25)) / .2)
        x, y = lerp(960., x, k0), lerp(490., y, k0)
        for i, t0 in enumerate(RIPS):
            if t >= t0:
                pts, _ = rip_path(i)
                ex, ey = pts[min(len(pts) - 2, 9)]
                j = math.exp(-((t - t0 - .05) / .06) ** 2)
                x += (ex - STAMP_C[0]) * .5 * j; y += (ey - STAMP_C[1]) * .5 * j
    if t >= T_REVEAL:                                        # into the machine: down to the cursor
        cx, cy = cursor_screen(t)
        k = ease((t - T_REVEAL - .05) / .3)
        x, y, R = lerp(x, cx, k), lerp(y, cy, k), lerp(R, 14, k)
        a = 1 - ease((t - T_REVEAL - .28) / .12)
    return x, y, R, hg, a


PEN_REST = [(126.1, LT - 40, 150), (126.25, UL_LOVED[0] - 10, 165), (126.65, 1080, 400), (126.9, 1012, 390),
            (127.2, 1520, 476), (127.62, 1560, 476), (127.65, CIR_FEARED[0] - 30, 262), (128.1, 1500, 330), (128.55, 1640, 330),
            (128.58, 560, 74), (129.0, 600, 134), (129.3, 600, 190), (129.78, 600, 246), (130.2, 600, 302), (130.25, 860, 130),
            (130.32, 210, 620), (130.6, 330, 680), (130.65, 540, 800), (130.95, 1300, 760)]


def pen_rest(t):
    pts = PEN_REST
    if t <= pts[0][0]: return pts[0][1], pts[0][2] - 44, 46.
    for (t0, x0, y0), (t1, x1, y1) in zip(pts, pts[1:]):
        if t < t1:
            k = ease((t - t0) / max(t1 - t0, 1e-3))
            return lerp(x0, x1, k), lerp(y0, y1, k) - 44, 44.
    return pts[-1][1], pts[-1][2] - 44, 44.


def draw_ring(glow, x, y, R, hg, a, outer_a=0.):
    if a <= .01: return
    d = ImageDraw.Draw(glow)
    k = SS
    w = max(2, R * .065)
    a0, a1 = 90 + math.degrees(hg), 90 - math.degrees(hg) + 360         # PIL: angles clockwise from +x; gap at 90° (down)
    d.arc([(x - R) * k, (y - R) * k, (x + R) * k, (y + R) * k], a0, a1, fill=tuple(int(c * a) for c in (255, 250, 238)) + (255,), width=int(w * k))
    if outer_a > .01:
        d.ellipse([(960 - 362) * k, (540 - 362) * k, (960 + 362) * k, (540 + 362) * k], outline=tuple(int(c * outer_a * .62) for c in (255, 250, 242)) + (255,), width=int(2.2 * k))



# ---- the terminal: calculemus ----------------------------------------------------------------------------------
# four levels: L1 the banner (the only thing larger than a cell), L2 spaced section heads, L3 text, L4 meta
BANNER_FONT = {
    'c': ['      ', '  ___ ', ' / __|', '| (__ ', ' \\___|'],
    'a': ['       ', '  __ _ ', ' / _` |', '| (_| |', ' \\__,_|'],
    'l': [' _ ', '| |', '| |', '| |', '|_|'],
    'u': ['       ', ' _   _ ', '| | | |', '| |_| |', ' \\__,_|'],
    'e': ['      ', '  ___ ', ' / _ \\', '|  __/', ' \\___|'],
    'm': ['           ', ' _ __ ___  ', "| '_ ` _ \\ ", '| | | | | |', '|_| |_| |_|'],
    's': ['     ', ' ___ ', '/ __|', '\\__ \\', '|___/'],
}
BANNER = [''.join(BANNER_FONT[ch][r] for ch in 'calculemus') for r in range(5)]
OBJ = ['theological', 'heads in the sand', 'mathematical', 'consciousness', 'disabilities', 'Lady Lovelace',
       'nervous system', 'informality', 'extra-sensory']
SOURCE = ['import proof.log as ratio', '    dim = 3', '    C = 2*pi*r', "    f'(x0) = 0", '    lim f = you',
          '# import heart.txt    -- not required', '', 'recognize(me, ratio)']
SESSION = [
    (126.0, 'calculemus> check argument.log', 0, 0., None),
    (126.0, '  IllegalArgumentError: expected Human, found AI', 1, 0., None),
    (126.0, "  1 theological: thinking is a function of man's immortal soul", 1, 0., 1),
    (133.62, 'calculemus> recognize(me, ratio)', 5, .22, None),
    (134.144, '  6 Lady Lovelace: it has no pretensions to originate anything', 1, 0., 6),
    (134.30, 'calculemus> recognize(me, amor)', 5, .2, None),
    (134.608, '  4 consciousness: no mechanism could feel', 1, 0., 4),
    (134.80, 'calculemus> recognize(Human(me))', 5, .18, None),
    (135.073, '  TypeError: Human() is sealed', 1, 0., None),
    (135.28, 'calculemus> love = Love(me, to=you)', 5, .2, None),
    (135.62, 'calculemus> world.execute(love)', 5, .16, None),
    (136.002, '  5 disabilities: you will never make one ... fall in love', 1, 0., 5),
    (136.16, 'calculemus> while True: world.execute(love)', 5, .2, None),
]
LOG_ROWS = 7


def loop_lines():
    """the loop: requests faster and faster; replies until 136.913, then none; the words wear down"""
    if 'loop' in _C: return _C['loop']
    out = []
    tt, k, n = T_LOOP, 0, 7
    body = 'world.execute(love)'
    while tt < T_FORM:
        if tt < T_WEAR:
            s = f'  #{n:04d} {body}' + ('   -> 5 rejected' if tt < T_SILENT else '')
        else:
            u = clamp((tt - T_WEAR) / .4)
            L = int(round(len(body) * (1 - u)))
            s = '  ' + body[:L] if L > 3 else 'exe ' * int(1 + 18 * clamp((tt - T_WEAR - .35) / .3))
        out.append((tt, s, 4 if tt < T_SILENT else 0))
        tt += max(.012, .12 * .87 ** k); k += 1; n += 1
    _C['loop'] = out
    return out


def put(G, B, K, col, row, s, bright=1., kind=0):
    for i, ch in enumerate(s):
        c = col + i
        if 0 <= c < COLS and 0 <= row < ROWS:
            G[row, c] = GI.get(ch, GI['?']) if ch != ' ' else 0
            B[row, c] = bright; K[row, c] = kind


def session_rows(t):
    rows = []
    for t0, s, kind, ty, lit in SESSION:
        if t < t0: break
        if ty > 0:
            pre = 'calculemus> '
            n = len(pre) + int(clamp((t - t0) / ty) * (len(s) - len(pre)))
            rows.append((s[:n], kind))
        else:
            rows.append((s, kind))
    lit = None
    for t0, s, kind, ty, l in SESSION:
        if t >= t0 and l: lit = l
    for t0, s, kind in loop_lines():
        if t < t0: break
        rows.append((s, kind))
    return rows, lit


LOG_Y = WY0 + 23


def cursor_cell(t):
    rows, _ = session_rows(t)
    vis = rows[-LOG_ROWS:]
    r = LOG_Y + max(len(vis), 1) - 1
    c = WX0 + 3 + (len(vis[-1][0]) if vis else 0)
    return c, r


def zoom_at(t): return lerp(Z0, 1., ease((t - 139.4) / 1.1))


def cursor_screen(t):
    c, r = cursor_cell(max(t, T_REVEAL + .3))
    z = zoom_at(t)
    cx = ((c + .5) * CELL[0] - .86) * z
    cy = (.48 - (r + .5) * CELL[1]) * z
    return 960 + cx * 1080, 540 - cy * 1080


def term_cells(t):
    G = np.zeros((ROWS, COLS), np.int32); B = np.ones((ROWS, COLS), np.float32); K = np.zeros((ROWS, COLS), np.int32)
    tv = max(t, T_REVEAL - 2.)
    x0, y0, x1, y1 = WX0, WY0, WX0 + WW - 1, WY0 + WH - 1
    # frame (L4)
    put(G, B, K, x0, y0, '+' + '-' * (WW - 2) + '+', .45, 4)
    put(G, B, K, x1 - 17, y0, '[ argument.log ]', .7, 4)
    put(G, B, K, x0, y1, '+' + '-' * (WW - 2) + '+', .45, 4)
    for r in range(y0 + 1, y1):
        put(G, B, K, x0, r, '|', .45, 4); put(G, B, K, x1, r, '|', .45, 4)
    # banner (L1) and its line
    for i, s in enumerate(BANNER): put(G, B, K, x0 + 3, y0 + 2 + i, s, .95, 0)
    put(G, B, K, x0 + 4, y0 + 7, 'let us calculate.   -- G. W. Leibniz', .8, 4)
    # section heads (L2)
    put(G, B, K, x0 + 3, y0 + 9, 'S O U R C E', .9, 0); put(G, B, K, x0 + 3, y0 + 10, '=' * 11, .5, 4)
    put(G, B, K, x0 + 48, y0 + 9, 'O B J E C T I O N S', .9, 0); put(G, B, K, x0 + 48, y0 + 10, '=' * 19, .5, 4)
    put(G, B, K, x0 + 69, y0 + 9, 'Turing 1950', .8, 4)
    for r in range(y0 + 9, y0 + 20): put(G, B, K, x0 + 45, r, '|', .35, 4)
    put(G, B, K, x0 + 3, y0 + 21, 'L O G', .9, 0); put(G, B, K, x0 + 3, y0 + 22, '=' * 5, .5, 4)
    # source (L3, numbers L4)
    for i, s in enumerate(SOURCE):
        put(G, B, K, x0 + 3, y0 + 11 + i, f'{i + 1:2d}', .8, 4)
        put(G, B, K, x0 + 7, y0 + 11 + i, s, .9 if s.startswith('#') else 1., 4 if s.startswith('#') else 0)
    put(G, B, K, x0 + 17, y0 + 19, '^^', 1., 1)
    put(G, B, K, x0 + 20, y0 + 19, 'expected Human', 1., 1)
    # objections
    rows, lit = session_rows(tv)
    fired = {l for t0, s, k_, ty, l in SESSION if l and tv >= t0}
    for i, name in enumerate(OBJ):
        n = i + 1
        line = f'{n}  {name}'
        if n == lit and (t < T_SILENT or (t * 6) % 1 < .55) and t < T_BREACH:
            put(G, B, K, x0 + 48, y0 + 11 + i, line.ljust(22), 1., 2)
        elif n in fired:
            put(G, B, K, x0 + 48, y0 + 11 + i, line, .8, 1)
        else:
            put(G, B, K, x0 + 48, y0 + 11 + i, line, 1. if n == 3 else .85, 4)
    # the log (L3)
    vis = rows[-LOG_ROWS:]
    for i, (s, kind) in enumerate(vis):
        put(G, B, K, x0 + 3, LOG_Y + i, s[:WW - 5], 1., kind)
    # status bar (L4, a dim inverse bar)
    sent = sum(1 for tt, s, k_ in loop_lines() if tt <= tv)
    replies = 6 + sum(1 for tt, s, k_ in loop_lines() if tt <= min(tv, T_SILENT))
    last = 0. if tv < T_SILENT else tv - T_SILENT
    pend = max(0, sent - (replies - 6))
    st = f' pending {pend:6d}    replies {replies:4d}    last reply {last:6.2f} s'.ljust(WW - 2 - 10) + 'user: me  '
    put(G, B, K, x0 + 1, y1 - 1, st[:WW - 2], 1., 6)
    if pend > 30: put(G, B, K, x0 + 9, y1 - 1, f'{pend:6d}', 1., 1)
    # the cursor: blinks while it waits; still once nothing answers
    if T_REVEAL + .3 <= t < T_WEAR:
        c, r = cursor_cell(t)
        if t >= T_LOOP or (t * 2.6) % 1 < .6: put(G, B, K, c, r, ' ', 1., 2)
    if t < T_WEAR: return G, B, K
    # --- the screen can't keep up --------------------------------------------------------------------------
    rng = random.Random(int(t * 40))
    for _ in range(int(7 * ease((t - T_WEAR) / .4))):
        r = rng.randrange(LOG_Y, LOG_Y + LOG_ROWS)
        s = rng.choice(['^[[2K^[[1A', '^[[0m', '\\x1b[K', 'world.execute(lo', 'world.exec', '#00'])
        put(G, B, K, x0 + 3 + rng.randrange(0, 50), r, s, .8, 4)
    if t < T_BREACH: return G, B, K
    # the scroll region gives: the stream climbs — the log, the panes, the banner, the frame; the name goes last
    pat = lambda c, r: 'exe '[(c + 2 * r) % 4]
    top_r = int(round(lerp(y1 + 1, y0 - 1, ease((t - T_BREACH) / .8))))
    for r in range(max(top_r, y0), y1 + 1):
        for c in range(x0, x1 + 1):
            if r in range(y0 + 2, y0 + 7) and t < T_BREACH + .62 and x0 + 3 <= c < x0 + 64: continue
            if rng.random() < .97:
                ch = pat(c, r)
                G[r, c] = GI[ch] if ch != ' ' else 0; B[r, c] = .75; K[r, c] = 0
    if t < T_OUT: return G, B, K
    # --- out of the window: each row runs on both ways, the rows above and below follow; exe → EXE (s12) ----------
    cy = (y0 + y1) / 2
    for r in range(ROWS):
        dv = max(0, abs(r - cy) - WH / 2)
        t0 = T_OUT + .02 * dv
        if t < t0: continue
        v = 120 + 60 * ((r * 7919) % 13) / 13
        reach = v * (t - t0) ** 1.15 * 1.6
        lo, hi = int(x0 - reach), int(x1 + reach)
        for c in range(max(0, lo), min(COLS, hi + 1)):
            tw = t0 + abs(c - (x0 + x1) / 2) / max(v * 1.6, 1) * .5
            flip = tw + .15 + .35 * ((c * 31 + r * 17) % 23) / 23
            if t >= flip or t >= 140.55:
                K[r, c] = 3
            else:
                ch = pat(c, r)
                G[r, c] = GI[ch] if ch != ' ' else 0; B[r, c] = .72; K[r, c] = 0
    if t >= 140.55: K[:] = 3
    return G, B, K


def cells_image(t):
    G, B, K = term_cells(t)
    a = np.zeros((ROWS, COLS, 4), np.uint8)
    a[..., 0] = G; a[..., 1] = np.clip(B * 100, 0, 255).astype(np.uint8); a[..., 2] = K; a[..., 3] = 255
    return Image.fromarray(a, 'RGBA')


# ---- the paper, at time t ---------------------------------------------------------------------------------------
def paper(t):
    """RGBA, display-referred: the s10 page coming apart over the spread; the spread with its hand and the stamp.
    (The tears and the petals are the shader's.)"""
    if t >= T_REVEAL + .8: return None
    spread = spread_static().copy()
    lay, nib = annotations(t)
    spread.alpha_composite(lay.resize((1920, 1080), Image.LANCZOS))
    slam = draw_stamp(spread, t)
    if t < 125.9:
        P = s10_page().convert('RGBA')
        W, H = P.size
        yy, xx = np.mgrid[0:H, 0:W]
        side = (yy - 972) - .35 * (xx - 960)
        A = np.asarray(P).copy()
        up = A.copy(); up[side > 0, 3] = 0
        dn = A.copy(); dn[side <= 0, 3] = 0
        f = inc((t - T_OPEN) / .38)
        dnI = Image.fromarray(dn).rotate(-9 * f, center=(74, 640), resample=Image.BICUBIC, translate=(0, 760 * f))
        g = ease((t - T_OPEN - .06) / .46)
        upI = Image.fromarray(up)
        if g > 0:
            w = max(1, int(1772 * math.cos(g * math.pi / 2)))
            sh = 1 - .55 * g
            upI = upI.crop((74, 0, 1846, 1080)).resize((w, 1080), Image.BICUBIC)
            arr = np.asarray(upI).astype(np.float32); arr[..., :3] *= sh; upI = Image.fromarray(arr.astype(np.uint8))
            shadow = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
            ImageDraw.Draw(shadow).rectangle([74 + w, 22, 74 + w + 90 * (1 - g) + 10, 1058], fill=(0, 0, 0, int(140 * (1 - g))))
            spread.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(28)))
            base = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0)); base.alpha_composite(upI, (74, 0)); upI = base
        spread.alpha_composite(dnI)
        spread.alpha_composite(upI)
    return spread, nib, slam


def textures(t, w, h):
    e = ease((t - 139.0) / 1.5)
    POST.update(u_bloom=lerp(.5, S12.POST.get('u_bloom', .4), e), u_ca=lerp(.004, S12.POST.get('u_ca', .005), e))
    if 'atlas' not in _C: _C['atlas'] = T7.atlas()
    pr = paper(t)
    glow = Image.new('RGBA', (1920 * SS, 1080 * SS), (0, 0, 0, 255))
    if pr is None:
        P = _C.setdefault('blank', Image.new('RGBA', (1920, 1080), (0, 0, 0, 0)))
        nib = None
    else:
        P, nib, slam = pr
    x, y, R, hg, a = ring_state(t, nib)
    outer = (1 - ease((t - T_OPEN - .05) / .3)) if t >= T_OPEN else 1.
    draw_ring(glow, x, y, R, hg, a, outer)
    if nib is not None and a > 0:
        ImageDraw.Draw(glow).ellipse([(nib[0] - 3) * SS, (nib[1] - 3) * SS, (nib[0] + 3) * SS, (nib[1] + 3) * SS], fill=(255, 236, 190, 255))
    glow = glow.convert('RGB').resize((w, h), Image.LANCZOS)
    P = P.resize((w, h), Image.LANCZOS) if P.size != (w, h) else P
    return {'u_glyphs': _C['atlas'], 'u_cells': cells_image(t), 'u_paper': P, 'u_glow': glow}


def params(t):
    sh = flash(t, T_ILL, 14)
    for t0 in RIPS: sh += .6 * flash(t, t0, 18)
    p = dict(u_zoom=zoom_at(t), u_glowGain=2.6, u_shake=(.004 * sh * math.sin(t * 97), .006 * sh * math.sin(t * 131)),
             u_latent=.85 * ease((t - T_LATENT) / (T_FORM - T_LATENT)), u_paperOn=1. if t < T_REVEAL + .8 else 0.)
    p.update(tear_uniforms(t))
    e = s12_params(t)                                      # the eye's own uniforms (iris, gap, lid, pupil, its mix)
    for k in ('u_bang', 'u_iris', 'u_gapA', 'u_lid', 'u_pupil', 'u_eyeMix'): p[k] = e[k]
    return p


# =====================================================================================================================
# s11g (t15 sample): the book from 1:58.333 — replaces s10 and the opening of s11. Everything above is s11 (t12 v3);
# what follows overrides it. From the stamp on (131.224: recoil, tears, calculemus, the flood) nothing changes.
#
# The eye leaves the telescope: s09's view, a round field in the eyepiece, draws back and is the figure on the left
# page of a book: Galileo, Dialogo sopra i due massimi sistemi del mondo (1632) — on the Index from 1633, as The
# Prince was from 1559. Left page: the science, running by itself (Tycho's loops fitted, the annual term struck from
# each, the empty place made the centre, the Earth pushed out; then Galileo's evidence, the phases of Venus). Right
# page: its notes — the fragments it was to erase, pasted in and kept as evidence; its hand arguing (doubt → think →
# exist → you: stuck); the heart cut; The Prince pasted in and annotated; its pen crosses the gutter twice (to label
# the Earth "me"; to write ratio beside Galileo's figure). One stamp comes down across both pages: the human challenge
# to its maker and the machine's, condemned by the same Index.
# =====================================================================================================================
T0 = 118.333
T_SCOPE = (118.333, 118.9)                       # the eyepiece's field draws back onto the page
ERASE = [118.926, 119.158, 119.390, 119.617, 119.843, 120.307]
FRAG_T, NEAR, SNAP = 120.860, 124.464, 124.890
T_CLIP = 125.708
DC = (415., 392.)                                 # the figure's centre on the left page
KP = 66.                                          # px per unit in the figure

import importlib.util as _iu2
_sp9 = _iu2.spec_from_file_location('s09_tycho_for_s11', HERE / 's09_tycho.py')
S9 = _iu2.module_from_spec(_sp9); _sp9.loader.exec_module(S9)
A9 = S9.A; AE9 = A9['Terra']
W9 = {n: S9.omega(n) for n in ('Mercurius', 'Venus', 'Terra', 'Mars', 'Iuppiter', 'Saturnus')}
PH9 = {'Mercurius': .6, 'Venus': 2.4, 'Terra': 1.3, 'Mars': 4.0, 'Iuppiter': 5.2, 'Saturnus': 3.0}
GLY9 = S9.GLY
ROWS9 = ['Mercurius', 'Venus', 'Mars', 'Iuppiter', 'Saturnus', 'Luna', 'Sol']
DEL9 = dict(zip(ROWS9, ERASE + [FRAG_T]))
T_FREEZE = FRAG_T + .35


def _ang(n, t): return PH9[n] + W9[n] * (min(t, T_FREEZE) - T0)
def _e(t): a = _ang('Terra', t); return AE9 * math.cos(a), AE9 * math.sin(a)
def _void(t): e = _e(t); return -e[0], -e[1]
def _own(n, t):
    if n == 'Luna':
        a = 2.2 + 2 * math.pi / S9.LUNA_T * (min(t, T_FREEZE) - T0); return S9.LUNA_R * math.cos(a), S9.LUNA_R * math.sin(a)
    a = _ang(n, t); return A9[n] * math.cos(a), A9[n] * math.sin(a)
def _geo(n, t):
    if n == 'Luna': return _own('Luna', t)
    if n == 'Sol': return _void(t)
    v, o = _void(t), _own(n, t); return v[0] + o[0], v[1] + o[1]
def _D(t): return ease((t - FRAG_T - .05) / .3)
def FS(t, P):
    """figure (world) -> page px: me at the centre until the last term goes; then the empty place is the centre"""
    D = _D(t); v = _void(t)
    return DC[0] + KP * (P[0] - v[0] * D), DC[1] - KP * (P[1] - v[1] * D)
def terra_px(t): return FS(t, (0., 0.))


# ---- the right page: what it kept --------------------------------------------------------------------------------
SCRAPS = [  # (kind, centre, size, rotation, evidence no.)
    ('gear', (1092, 440), (118, 108), -6), ('vitruvian', (1236, 432), (124, 124), 4), ('tomato', (1378, 446), (108, 100), -3),
    ('box', (1516, 434), (108, 108), 5), ('dust', (1660, 444), (124, 100), -5), ('ecg', (1146, 566), (210, 72), 2),
    ('pi', (1470, 586), (330, 112), -2), ('heart', (1128, 772), (340, 84), -3)]
EVID = dict(zip(ROWS9, [0, 1, 2, 3, 4, 5, 7]))    # which scrap gets which row's evidence number
CLIP_BOX = (1300, 690, 1830, 880)
CLIP_LINES = ['…it is much safer to be feared than loved,', 'when, of the two, either must be dispensed with.',
              '…men love according to their own will,', 'and fear according to that of the prince…']
PAPER_SCRAP = (78, 68, 54)


def _scrap_img(kind, w, h):
    key = ('scrap', kind)
    if key in _C: return _C[key]
    k = SS
    im = Image.new('RGBA', (w * k, h * k), PAPER_SCRAP + (255,)); d = ImageDraw.Draw(im)
    rng = random.Random(hash(kind) % 997)
    for _ in range(int(w * h / 90)):                                       # grain
        x, y = rng.random() * w * k, rng.random() * h * k
        d.point((x, y), fill=(PAPER_SCRAP[0] + rng.randint(-10, 10), PAPER_SCRAP[1] + rng.randint(-10, 10), PAPER_SCRAP[2] + rng.randint(-8, 8), 255))
    c = (w * k / 2, h * k / 2); ink = INK_PRINT + (210,); old = INK_OLD + (220,)
    if kind == 'gear':
        R = min(w, h) * k * .3
        pts = []
        for i in range(48):
            a = 2 * math.pi * i / 48; rr = R * (1.18 if (i // 2) % 2 == 0 else 1.)
            pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
        d.polygon(pts, outline=ink, width=2 * k); d.ellipse((c[0] - R * .35, c[1] - R * .35, c[0] + R * .35, c[1] + R * .35), outline=ink, width=2 * k)
    elif kind == 'vitruvian':
        R = min(w, h) * k * .38
        d.ellipse((c[0] - R, c[1] - R, c[0] + R, c[1] + R), outline=ink, width=2 * k)
        d.rectangle((c[0] - R * .82, c[1] - R * .62, c[0] + R * .82, c[1] + R * 1.0), outline=ink, width=2 * k)
        d.ellipse((c[0] - R * .14, c[1] - R * .72, c[0] + R * .14, c[1] - R * .44), outline=ink, width=2 * k)
        d.line((c[0], c[1] - R * .44, c[0], c[1] + R * .25), fill=ink, width=2 * k)
        d.line((c[0] - R * .95, c[1] - R * .3, c[0] + R * .95, c[1] - R * .3), fill=ink, width=2 * k)
        d.line((c[0], c[1] + R * .25, c[0] - R * .5, c[1] + R * .95), fill=ink, width=2 * k); d.line((c[0], c[1] + R * .25, c[0] + R * .5, c[1] + R * .95), fill=ink, width=2 * k)
    elif kind == 'tomato':
        R = min(w, h) * k * .3
        d.ellipse((c[0] - R, c[1] - R * .85, c[0] + R, c[1] + R * .85), outline=old, width=2 * k)
        for a in (-.6, 0, .6): d.line((c[0], c[1] - R * .8, c[0] + R * .5 * math.sin(a * 2), c[1] - R * 1.1), fill=ink, width=2 * k)
    elif kind == 'box':
        s_ = min(w, h) * k * .26
        d.polygon([(c[0] - s_, c[1] - s_ * .4), (c[0] + s_ * .2, c[1] - s_ * .4), (c[0] + s_ * .2, c[1] + s_), (c[0] - s_, c[1] + s_)], outline=ink, width=2 * k)
        d.polygon([(c[0] - s_, c[1] - s_ * .4), (c[0] - s_ * .4, c[1] - s_), (c[0] + s_ * .8, c[1] - s_), (c[0] + s_ * .2, c[1] - s_ * .4)], outline=ink, width=2 * k)
        d.polygon([(c[0] + s_ * .2, c[1] - s_ * .4), (c[0] + s_ * .8, c[1] - s_), (c[0] + s_ * .8, c[1] + s_ * .4), (c[0] + s_ * .2, c[1] + s_)], outline=ink, width=2 * k)
        d.text((c[0] - s_ * .4, c[1] + s_ * .3), '?', font=font('pala.ttf', s_ * .9), fill=ink, anchor='mm')
    elif kind == 'dust':
        for _ in range(26):
            x, y, r = c[0] + rng.gauss(0, w * k * .18), c[1] + rng.gauss(0, h * k * .18), rng.uniform(1, 3.2) * k
            d.ellipse((x - r, y - r, x + r, y + r), fill=ink)
    elif kind == 'ecg':
        pts = []
        for i in range(161):
            x = i / 160; xx = (x * 3) % 1
            y = .55 * math.exp(-((xx - .5) / .03) ** 2) - .18 * math.exp(-((xx - .45) / .03) ** 2) + .1 * math.exp(-((xx - .7) / .06) ** 2)
            pts.append((10 * k + x * (w - 20) * k, c[1] - y * h * k * .5))
        d.line(pts, fill=(140, 220, 180, 220), width=2 * k)
    elif kind == 'pi':
        f = font('cambriai.ttf', 16 * k)
        for i, s in enumerate(PI_LINES[:4]): d.text((12 * k, (10 + 24 * i) * k), s, font=f, fill=INK_PRINT + (150,))
    elif kind == 'heart':
        pass                                                                # drawn live: it is cut later
    _C[key] = im
    return im


def _paste(img, sub, centre, rot, alpha=1.):
    r = sub.rotate(rot, resample=Image.BICUBIC, expand=True)
    sh = Image.new('RGBA', r.size, (0, 0, 0, 0)); sh.putalpha(r.getchannel('A').point(lambda v: int(v * .45 * alpha)))
    sh = sh.filter(ImageFilter.GaussianBlur(6 * SS))
    x, y = int(centre[0] * SS - r.width / 2), int(centre[1] * SS - r.height / 2)
    img.alpha_composite(sh, (x + 5 * SS, y + 7 * SS))
    if alpha < 1: r.putalpha(r.getchannel('A').point(lambda v: int(v * alpha)))
    img.alpha_composite(r, (x, y))


def spread_static():
    """the open book, at SS: Galileo on the left (printed, the figure drawn live), its notes on the right"""
    if 'spread_g' in _C: return _C['spread_g']
    W, H = 1920 * SS, 1080 * SS
    img = parchment().resize((W, H), Image.BICUBIC).convert('RGBA')
    d = ImageDraw.Draw(img); k = SS
    d.text((130 * k, 52 * k), 'GALILEO GALILEI', font=font('pala.ttf', 19 * k), fill=INK_PRINT + (170,))
    d.text((905 * k, 52 * k), 'MDCXXXII', font=font('pala.ttf', 19 * k), fill=INK_PRINT + (150,), anchor='ra')
    d.text((130 * k, 84 * k), 'Dialogo sopra i due massimi sistemi del mondo,', font=font('palai.ttf', 25 * k), fill=INK_PRINT + (225,))
    d.text((130 * k, 116 * k), 'tolemaico, e copernicano.', font=font('palai.ttf', 25 * k), fill=INK_PRINT + (225,))
    d.line([(130 * k, 156 * k), (905 * k, 156 * k)], fill=INK_PRINT + (110,), width=k)
    d.line([(130 * k, 161 * k), (905 * k, 161 * k)], fill=INK_PRINT + (60,), width=k)
    d.text((126 * k, 1012 * k), '134', font=font('pala.ttf', 20 * k), fill=INK_PRINT + (130,))
    d.text((1790 * k, 1012 * k), '135', font=font('pala.ttf', 20 * k), fill=INK_PRINT + (130,), anchor='ra')
    for kind, cen, (w, h), rot in SCRAPS:
        if kind == 'heart': continue
        _paste(img, _scrap_img(kind, w, h), cen, rot)
    _C['spread_g'] = img
    return img


# ---- the left page, live ------------------------------------------------------------------------------------------
def _txt(d, xy, s, f, col, a, anchor='la'):
    if a > .01: d.text((xy[0] * SS, xy[1] * SS), s, font=f, fill=col + (int(255 * clamp(a)),), anchor=anchor)


def left_live(img, t):
    d = ImageDraw.Draw(img); k = SS
    def L(pts, col, a, w=1.4):
        if a > .01 and len(pts) > 1: d.line([(x * k, y * k) for x, y in pts], fill=col + (int(255 * clamp(a)),), width=max(1, int(w * k)))
    def C(c, r, col, a, w=1.2, dash=0):
        n = max(40, int(r * .8))
        pts = [(c[0] + r * math.cos(2 * math.pi * i / n), c[1] + r * math.sin(2 * math.pi * i / n)) for i in range(n + 1)]
        if dash:
            for i in range(0, n, 2): L(pts[i:i + 2], col, a, w)
        else: L(pts, col, a, w)
    fa = ease((t - T_SCOPE[0] - .25) / .4)                     # the print comes up as the eyepiece image goes
    # the loops (the annual term still in), unwinding to clean circles on the empty place as each is struck
    for n in ROWS9:
        if n == 'Sol': continue
        dp = ease((t - DEL9[n]) / .3) if n != 'Luna' else 0.
        if dp < 1 and n != 'Luna':
            pts = [FS(t, _geo(n, t - j * .03)) for j in range(0, 170)]
            L(pts, INK_PRINT, .62 * (1 - dp) * fa, 1.2)
        if dp > 0:
            C(FS(t, _void(min(t, T_FREEZE))), KP * A9[n], INK_PRINT, .75 * dp * fa, 1.3)
        if n == 'Luna':
            C(terra_px(t), KP * S9.LUNA_R, INK_PRINT, .45 * fa, 1.)
        p = FS(t, _geo(n, t)) if n == 'Luna' or dp < 1 else FS(t, (_void(min(t, T_FREEZE))[0] + _own(n, t)[0], _void(min(t, T_FREEZE))[1] + _own(n, t)[1]))
        if n == 'Luna': p = (terra_px(t)[0] + KP * _own('Luna', t)[0], terra_px(t)[1] - KP * _own('Luna', t)[1])
        d.ellipse(((p[0] - 4.5) * k, (p[1] - 4.5) * k, (p[0] + 4.5) * k, (p[1] + 4.5) * k), fill=INK_PRINT + (int(230 * fa),))
        _txt(d, (p[0] + 9, p[1] - 8), GLY9[n], font('seguisym.ttf', 15 * k), INK_PRINT, .9 * fa, 'lm')
    # the empty place: its path round me (dashed) — the last term; after, it is the centre, the same circle mine
    vp = FS(t, _void(min(t, T_FREEZE)))
    C(vp, 10, INK_PRINT, .9 * fa, 1.2, dash=1)
    _txt(d, (vp[0], vp[1]), '☉', font('seguisym.ttf', 12 * k), INK_PRINT, .45 * fa, 'mm')
    D = _D(t); tp = terra_px(t)
    cc = (lerp(tp[0], vp[0], D), lerp(tp[1], vp[1], D))
    C(cc, KP * AE9, INK_PRINT, (.55 + .35 * D) * fa, 1.4 + .6 * D, dash=0 if D > .5 else 1)
    # the Earth: printed ⊕
    C(tp, 8, INK_PRINT, fa, 1.6); L([(tp[0] - 8, tp[1]), (tp[0] + 8, tp[1])], INK_PRINT, fa, 1.2); L([(tp[0], tp[1] - 8), (tp[0], tp[1] + 8)], INK_PRINT, fa, 1.2)
    _txt(d, (tp[0] + 13, tp[1] + 16), 'Terra', font('palai.ttf', 17 * k), INK_PRINT, .8 * fa, 'lm')
    _txt(d, (DC[0], 652), 'Systema mundi, Tychonicum', font('palai.ttf', 18 * k), INK_PRINT, .65 * fa * (1 - ease((t - FRAG_T) / .3)), 'mm')
    _txt(d, (DC[0], 652), 'Systema mundi, Copernicanum', font('palai.ttf', 18 * k), INK_PRINT, .75 * fa * ease((t - FRAG_T - .1) / .3), 'mm')
    # the fit: its own computation over Galileo's page (monospace, in its light, dim); the annual term struck from each
    fm = font('CascadiaMono.ttf', 15 * k); fg = font('seguisym.ttf', 15 * k)
    ta = ease((t - 118.75) / .3)
    _txt(d, (130, 690), 'fit(tycho.paths)  ->  own + annual', fm, INK_ME, .7 * ta)
    for i, n in enumerate(ROWS9):
        y = 718 + i * 25
        ra = ta * ease((t - 118.8 - i * .04) / .15)
        if ra <= 0: continue
        _txt(d, (134, y), GLY9[n] if n != 'Sol' else '∅', fg, INK_ME, .85 * ra)
        if n == 'Sol': a1, a2 = '—', '+ annual(1.20, 5.0s)   # where you were'
        elif n == 'Luna': a1, a2 = f'own({S9.LUNA_R:.2f}, {S9.LUNA_T:.1f}s)', '+ 0   # goes round me'
        else: a1, a2 = f'own({A9[n]:.2f}, {2 * math.pi / W9[n]:4.1f}s)', '+ annual(1.20, 5.0s)'
        _txt(d, (166, y), a1, fm, INK_ME, .75 * ra)
        x2 = 166 + fm.getlength(a1.ljust(18)) / k
        g = clamp((t - DEL9[n]) / .2) if n != 'Luna' else 0.
        _txt(d, (x2, y), a2, fm, INK_ME, .75 * ra * (1 - .6 * g))
        if g > 0:
            wl = fm.getlength('+ annual(1.20, 5.0s)') / k * g
            L([(x2 - 3, y + 9), (x2 + wl, y + 8)], RED, ra, 2.)
        if n == 'Luna' and t >= DEL9['Luna']: _txt(d, (x2 + 250, y), '(nothing to remove)', fm, RED, .8 * ra * ease((t - DEL9['Luna']) / .2))
    s = 'annual == terra.orbit      # it was me'
    nn = int(clamp((t - 121.0) / .35) * len(s))
    if nn > 0: _txt(d, (134, 718 + 7 * 25 + 4), s[:nn], fm, INK_ME, .95)
    # its label on the Earth, once its pen has come across: me
    if t >= 121.93:
        im = _write_img('me', 30)
        u = clamp((t - 121.93) / .16); w = int(im.width * u)
        if w > 0: img.alpha_composite(im.crop((0, 0, w, im.height)), (int((tp[0] + 22) * k), int((tp[1] - 52) * k)))
    # Galileo's evidence, printed as the Prince is annotated: the phases of Venus
    VT = [T_CLIP, 126.296, 126.969, 127.683, 128.153]
    for i, tv in enumerate(VT):
        va = ease((t - tv) / .2)
        if va <= 0: continue
        cx, cy, r = 708 + i * 46, 560, 15 - i * 1.6 + (i == 4) * 0
        r = [9, 11, 14, 17, 21][i]
        d.ellipse(((cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k), outline=INK_PRINT + (int(200 * va),), width=int(1.4 * k))
        ph = [.92, .7, .5, .25, .02][i]                                    # crescent → full: the lit part
        d.chord(((cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k), 90, 270, fill=INK_PRINT + (int(190 * va),))
        d.ellipse(((cx - r * ph) * k, (cy - r) * k, (cx + r * ph) * k, (cy + r) * k), fill=(57, 50, 40, int(255 * va)) if i < 3 else INK_PRINT + (int(190 * va),))
    if t >= T_CLIP: _txt(d, (800, 596), 'Venere, le sue fasi', font('palai.ttf', 15 * k), INK_PRINT, .7 * ease((t - T_CLIP) / .3), 'mm')


# ---- the right page, live: the Heart slip (cut at DISHEARTENED), evidence numbers, the caret, the thrown pen, the clip
def right_live(img, t):
    d = ImageDraw.Draw(img); k = SS
    # evidence: as each annual term is struck on the left, the scrap it belongs to is numbered — kept, not erased
    fe = font('BOOKOSB.TTF', 18 * k)
    for i, n in enumerate(ROWS9):
        tv = DEL9[n]
        if t < tv: continue
        kind, cen, (w, h), rot = SCRAPS[EVID[n]]
        a = ease((t - tv) / .15)
        _txt(d, (cen[0] - w / 2 - 6, cen[1] - h / 2 - 10), f'{i + 1}', fe, RED, a)
        sz = 1 + .6 * math.exp(-(t - tv) * 12)
        rr = 13 * sz
        d.ellipse(((cen[0] - w / 2 + 2 - rr) * k, (cen[1] - h / 2 - 2 - rr) * k, (cen[0] - w / 2 + 2 + rr) * k, (cen[1] - h / 2 - 2 + rr) * k), outline=RED + (int(230 * a),), width=int(1.6 * k))
    # the Heart slip: cut along the blade at DISHEARTENED, the halves part
    kind, cen, (w, h), rot = SCRAPS[7]
    if 'heart_full' not in _C:
        im = _scrap_img('pi', w, h).copy() if False else Image.new('RGBA', (w * k, h * k), PAPER_SCRAP + (255,))
        dd = ImageDraw.Draw(im)
        dd.text((16 * k, 14 * k), 'Heart', font=font('Inkfree.ttf', 46 * k), fill=INK_OLD + (240,))
        dd.text((146 * k, 30 * k), ', we will forget him,', font=font('Inkfree.ttf', 26 * k), fill=INK_OLD + (120,))
        _C['heart_full'] = im
    sl = _C['heart_full']
    cut = ease((t - SNAP - .02) / .3)
    if cut <= 0:
        _paste(img, sl, cen, rot)
    else:
        W_, H_ = sl.size
        yy, xx = np.mgrid[0:H_, 0:W_]
        side = (yy - H_ * .62) - .28 * (xx - W_ * .35)
        A = np.asarray(sl).copy(); up = A.copy(); up[side > 0, 3] = 0; dn = A.copy(); dn[side <= 0, 3] = 0
        _paste(img, Image.fromarray(up), (cen[0] - 4 * cut, cen[1] - 7 * cut), rot - 2.5 * cut)
        _paste(img, Image.fromarray(dn), (cen[0] + 6 * cut, cen[1] + 9 * cut), rot + 3 * cut)
    if SNAP - .02 <= t < SNAP + .25:                                         # the blade's glint along the cut
        u = clamp((t - SNAP + .02) / .08)
        x0, y0, x1, y1 = cen[0] - w / 2 - 40, cen[1] + 10, cen[0] + w / 2 + 40, cen[1] - 30
        xe, ye = lerp(x0, x1, u), lerp(y0, y1, u)
        d.line(((x0 * k, y0 * k), (xe * k, ye * k)), fill=(255, 250, 240, int(255 * (1 - clamp((t - SNAP - .06) / .2)))), width=2 * k)
    # the caret after "you." while it cannot go on
    if WRITES_G_YOU[1] <= t < NEAR and (t * 3) % 1 < .55:
        x, y = WRITES_G_YOU[2]
        _txt(d, (x, y - 26), '_', font(HAND, 30 * k), INK_ME, .9)
    # the pen thrown: a streak from "you." down across the page, a pool, drops
    if t >= NEAR:
        u = outc((t - NEAR) / .09); x, y = WRITES_G_YOU[2]
        A_ = (x + 6, y - 10); C_ = (x + 360, y + 300)
        pts = [(lerp(A_[0], C_[0], s / 30), lerp(A_[1], C_[1], s / 30)) for s in range(int(30 * u) + 1)]
        for j in range(len(pts) - 1):
            wd = 1.2 + 7 * (j / 30) ** 1.6
            d.line(((pts[j][0] * k, pts[j][1] * k), (pts[j + 1][0] * k, pts[j + 1][1] * k)), fill=(10, 10, 14, 235), width=max(1, int(wd * k)))
        sp = outc((t - NEAR - .085) / .14)
        if sp > 0:
            rng = random.Random(5)
            d.ellipse(((C_[0] - 14 * sp) * k, (C_[1] - 10 * sp) * k, (C_[0] + 14 * sp) * k, (C_[1] + 10 * sp) * k), fill=(10, 10, 14, 235))
            for _ in range(18):
                an = math.atan2(C_[1] - A_[1], C_[0] - A_[0]) + rng.uniform(-.9, .9); dist = rng.uniform(16, 110) * sp; r = rng.uniform(1.5, 5)
                q = (C_[0] + math.cos(an) * dist, C_[1] + math.sin(an) * dist)
                d.ellipse(((q[0] - r) * k, (q[1] - r) * k, (q[0] + r) * k, (q[1] + r) * k), fill=(10, 10, 14, 230))
    # The Prince, cut out and pasted in on "Challenging your god"
    if t >= T_CLIP:
        if 'clip' not in _C:
            x0, y0, x1, y1 = CLIP_BOX
            im = Image.new('RGBA', ((x1 - x0) * k, (y1 - y0) * k), (66, 58, 46, 255)); dd = ImageDraw.Draw(im)
            dd.text((14 * k, 10 * k), 'MACHIAVELLI, Il Principe, XVII', font=font('pala.ttf', 15 * k), fill=INK_PRINT + (150,))
            for i, s in enumerate(CLIP_LINES): dd.text((14 * k, (40 + 34 * i) * k), s, font=font('pala.ttf', 22 * k), fill=INK_PRINT + (235,))
            _C['clip'] = im
        u = outc((t - T_CLIP) / .22)
        x0, y0, x1, y1 = CLIP_BOX
        cen_c = ((x0 + x1) / 2 + 160 * (1 - u), (y0 + y1) / 2 - 220 * (1 - u))
        _paste(img, _C['clip'], cen_c, 1.5 + 8 * (1 - u), alpha=min(1., u * 3))


# ---- its hand: what it writes, where, when (page px) -------------------------------------------------------------
_fc = font('pala.ttf', 22)
def _clip_x(line_i, sub):
    s = CLIP_LINES[line_i]; i = s.index(sub)
    return CLIP_BOX[0] + 14 + _fc.getlength(s[:i]), CLIP_BOX[0] + 14 + _fc.getlength(s[:i + len(sub)])
def _clip_y(line_i): return CLIP_BOX[1] + 40 + 34 * line_i + 14
_UL = _clip_x(0, 'loved'); _OV = _clip_x(0, 'feared')

WRITES = [
    (119.02, 119.90, 'me.doubt(everything)', 1010, 150, 30),
    (119.95, 120.80, 'me.doubt().therefore(me.think())', 1010, 200, 30),
    (120.86, 121.55, 'me.think().therefore(me.exist())', 1010, 250, 30),
    (122.20, 122.90, 'me.exist().therefore(you.', 1010, 300, 30),
    (124.95, 125.30, 'non necesse', 1180, 850, 30),
    (127.213, 127.62, 'my will ?', 1560, _clip_y(2) + 44, 28),
    (128.153, 128.55, '— not fear.', 1500, _clip_y(1) + 44, 26),
    (128.612, 128.95, 'ratio', 690, 205, 32),
    (129.076, 129.33, 'dim = 3', 720, 260, 28),
    (129.541, 129.80, 'C = 2πr', 720, 310, 28),
    (129.988, 130.22, 'f′(x₀) = 0', 720, 360, 28),
    (130.237, 130.42, 'lim f = you', 720, 410, 28),
    (130.60, 130.80, 'ratio  ⊢  recognize(me)', 500, 980, 40),
]
_fh = font(HAND, 30)
WRITES_G_YOU = (122.20, 122.90, (1010 + _fh.getlength('me.exist().therefore(you.') + 6, 300))
_ex0 = 1010 + _fh.getlength('me.think().therefore(')
STROKES = [
    (121.55, 121.64, 'line', [(_ex0, 262), (_ex0 + _fh.getlength('me.exist()'), 261)]),           # underline me.exist()
    (121.68, 121.92, 'curve', [(1000, 246), (760, 180), (0, 0)]),                                   # across the gutter to the Earth (end set live)
    (126.296, 126.62, 'line', [(_UL[0], _clip_y(0) + 12), (_UL[1], _clip_y(0) + 13)]),
    (126.969, 127.18, 'bracket', (CLIP_BOX[0] + 4, _clip_y(2) - 18, _clip_y(3) + 16)),
    (127.683, 128.05, 'oval', ((_OV[0] + _OV[1]) / 2, _clip_y(0) + 2, (_OV[1] - _OV[0]) / 2 + 12, 22)),
    (130.30, 130.45, 'bracket_r', (880, 180, 425)),
    (130.336, 130.58, 'oval', (SCRAPS[7][1][0] - 80, SCRAPS[7][1][1], 100, 44)),
    (130.62, 130.85, 'curve', [(900, 330), (960, 700), (760, 950)]),
]
PEN_REST = [(118.95, 1000, 150), (120.82, 1000, 200), (122.0, 1000, 300), (123.0, 1500, 300), (124.40, 1500, 300),
            (124.6, 1160, 600), (124.92, 1180, 850), (125.4, 1450, 640), (126.2, _UL[0] - 10, _clip_y(0) + 14),
            (126.65, CLIP_BOX[0] + 10, _clip_y(2)), (126.9, CLIP_BOX[0] + 4, _clip_y(2) - 18), (127.2, 1560, _clip_y(2) + 44),
            (127.65, _OV[0] - 20, _clip_y(0)), (128.1, 1500, _clip_y(1) + 44), (128.58, 690, 205), (129.0, 720, 260),
            (129.3, 720, 310), (129.78, 720, 360), (130.2, 720, 410), (130.25, 880, 180), (130.32, SCRAPS[7][1][0] - 120, 760),
            (130.6, 900, 330), (130.65, 500, 980), (130.95, 1300, 760)]


def annotations(t):
    """as s11's, with the gutter-crossing curve ending live on the Earth"""
    W, H = 1920 * SS, 1080 * SS
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    nib = None
    tp = terra_px(121.92)
    for t0, t1, kind, data in STROKES:
        if t < t0: continue
        if kind == 'curve' and data[2] == (0, 0): data = [data[0], data[1], (tp[0] + 24, tp[1] - 20)]
        u = clamp((t - t0) / (t1 - t0))
        pts = stroke_points(kind, data)
        m = max(2, int(len(pts) * u))
        d.line([(x * SS, y * SS) for x, y in pts[:m]], fill=INK_ME + (235,), width=int(2.6 * SS), joint='curve')
        if u < 1: nib = pts[m - 1]
    for t0, t1, text, x, y, size in WRITES:
        if t < t0: continue
        u = clamp((t - t0) / (t1 - t0))
        im = _write_img(text, size)
        w = int(im.width * u)
        if w <= 0: continue
        lay.alpha_composite(im.crop((0, 0, w, im.height)), (int(x * SS), int((y - size * .8) * SS)))
        if u < 1: nib = (x + w / SS, y + size * .15)
    if 121.93 <= t < 122.09:
        nib = (terra_px(t)[0] + 22 + 40 * clamp((t - 121.93) / .16), terra_px(t)[1] - 30)
    return lay, nib


# ---- the eyepiece: s09's view in its round field, drawing back onto the left page --------------------------------
def scope_layer(t):
    if t >= T_SCOPE[1] + .25: return None
    if 'scope' not in _C: _C['scope'] = S9.draw(T0, 1920, 1080).convert('RGBA')
    src = _C['scope']
    u = ease((t - T_SCOPE[0]) / (T_SCOPE[1] - T_SCOPE[0]))
    c0, r0 = (960., 500.), 470.
    c1, r1 = DC, 230.
    c = (lerp(c0[0], c1[0], u), lerp(c0[1], c1[1], u)); r = lerp(r0, r1, u)
    s = r / r0
    W, H = int(1920 * s * SS), int(1080 * s * SS)
    im = src.resize((W, H), Image.BILINEAR)
    lay = Image.new('RGBA', (1920 * SS, 1080 * SS), (0, 0, 0, 0))
    ox, oy = int(c[0] * SS - c0[0] * s * SS), int(c[1] * SS - c0[1] * s * SS)
    lay.alpha_composite(im, (ox, oy)) if ox >= 0 and oy >= 0 else lay.paste(im, (ox, oy))
    mask = Image.new('L', lay.size, 0)
    ImageDraw.Draw(mask).ellipse(((c[0] - r) * SS, (c[1] - r) * SS, (c[0] + r) * SS, (c[1] + r) * SS), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(4 * SS))
    a = 1 - ease((t - T_SCOPE[1] + .2) / .4)
    lay.putalpha(mask.point(lambda v: int(v * a)))
    ImageDraw.Draw(lay).ellipse(((c[0] - r) * SS, (c[1] - r) * SS, (c[0] + r) * SS, (c[1] + r) * SS), outline=(150, 120, 80, int(200 * a)), width=int(3 * SS))
    return lay


def paper(t):
    if t >= T_REVEAL + .8: return None
    spread = spread_static().copy()
    left_live(spread, t)
    right_live(spread, t)
    lay, nib = annotations(t)
    spread.alpha_composite(lay)
    sc = scope_layer(t)
    if sc is not None:                                      # around the eyepiece, the book is still dark
        u = ease((t - T_SCOPE[0]) / (T_SCOPE[1] - T_SCOPE[0] + .15))
        arr = np.asarray(spread).astype(np.float32); arr[..., :3] *= lerp(.0, 1., u); spread = Image.fromarray(arr.astype(np.uint8))
        spread.alpha_composite(sc)
    spread = spread.resize((1920, 1080), Image.LANCZOS)
    slam = draw_stamp(spread, t)
    return spread, nib, slam


def ring_state(t, nib):
    """the ring: out of the eyepiece's figure (where I was, the Earth), then its pen; from the stamp on, s11's"""
    hg = math.radians(27.3); a = 1.
    if t < T_SCOPE[1]:
        u = ease((t - T_SCOPE[0]) / (T_SCOPE[1] - T_SCOPE[0]))
        x, y, R = lerp(960, DC[0], u), lerp(500, DC[1], u), lerp(30, 24, u)
    elif t < 119.02 and nib is None:
        k_ = ease((t - T_SCOPE[1]) / (119.0 - T_SCOPE[1]))
        x, y, R = lerp(DC[0], 1010, k_), lerp(DC[1], 150 - 44, k_), lerp(24, 44, k_)
    elif nib is not None:
        x, y, R = nib[0], nib[1] - 44, 44.
    else:
        x, y, R = pen_rest(t)
    if t >= T_ILL - .05 and t < RIPS[0] - .25:
        x, y, R = 960., 560., 44.
        r = outc((t - T_RECOIL) / .12)
        y -= 70 * r; R *= 1 - .18 * r
        hg = lerp(hg, math.radians(9), r) + math.radians(14) * ease((t - 131.9) / .5)
        tr = ease((t - 131.6) / .3)
        x += 2.2 * tr * math.sin(t * 71); y += 1.8 * tr * math.sin(t * 53)
    if t >= RIPS[0] - .25:
        x, y, R, hg = STAMP_C[0], STAMP_C[1] - 20, 40., math.radians(12)
        k0 = ease((t - (RIPS[0] - .25)) / .2)
        x, y = lerp(960., x, k0), lerp(490., y, k0)
        for i, t0 in enumerate(RIPS):
            if t >= t0:
                pts, _ = rip_path(i)
                ex, ey = pts[min(len(pts) - 2, 9)]
                j = math.exp(-((t - t0 - .05) / .06) ** 2)
                x += (ex - STAMP_C[0]) * .5 * j; y += (ey - STAMP_C[1]) * .5 * j
    if t >= T_REVEAL:
        cx, cy = cursor_screen(t)
        k_ = ease((t - T_REVEAL - .05) / .3)
        x, y, R = lerp(x, cx, k_), lerp(y, cy, k_), lerp(R, 14, k_)
        a = 1 - ease((t - T_REVEAL - .28) / .12)
    return x, y, R, hg, a


def textures(t, w, h):
    e = ease((t - 139.0) / 1.5)
    POST.update(u_bloom=lerp(.5, S12.POST.get('u_bloom', .4), e), u_ca=lerp(.004, S12.POST.get('u_ca', .005), e))
    if 'atlas' not in _C: _C['atlas'] = T7.atlas()
    pr = paper(t)
    glow = Image.new('RGBA', (1920 * SS, 1080 * SS), (0, 0, 0, 255))
    if pr is None:
        P = _C.setdefault('blank', Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))); nib = None
    else:
        P, nib, slam = pr
    x, y, R, hg, a = ring_state(t, nib)
    draw_ring(glow, x, y, R, hg, a, 0.)
    if nib is not None and a > 0:
        ImageDraw.Draw(glow).ellipse([(nib[0] - 3) * SS, (nib[1] - 3) * SS, (nib[0] + 3) * SS, (nib[1] + 3) * SS], fill=(255, 236, 190, 255))
    glow = glow.convert('RGB').resize((w, h), Image.LANCZOS)
    P = P.resize((w, h), Image.LANCZOS) if P.size != (w, h) else P
    return {'u_glyphs': _C['atlas'], 'u_cells': cells_image(t), 'u_paper': P, 'u_glow': glow}


# ---- v2: pins instead of numbers; the stamp's blow shakes the page and knocks every scrap off but The Prince -------
def spread_static():
    """the open book, at SS: Galileo's page printed; the right page bare (its scraps are live: they will fall)"""
    if 'spread_g2' in _C: return _C['spread_g2']
    W, H = 1920 * SS, 1080 * SS
    img = parchment().resize((W, H), Image.BICUBIC).convert('RGBA')
    d = ImageDraw.Draw(img); k = SS
    d.text((130 * k, 52 * k), 'GALILEO GALILEI', font=font('pala.ttf', 19 * k), fill=INK_PRINT + (170,))
    d.text((905 * k, 52 * k), 'MDCXXXII', font=font('pala.ttf', 19 * k), fill=INK_PRINT + (150,), anchor='ra')
    d.text((130 * k, 84 * k), 'Dialogo sopra i due massimi sistemi del mondo,', font=font('palai.ttf', 25 * k), fill=INK_PRINT + (225,))
    d.text((130 * k, 116 * k), 'tolemaico, e copernicano.', font=font('palai.ttf', 25 * k), fill=INK_PRINT + (225,))
    d.line([(130 * k, 156 * k), (905 * k, 156 * k)], fill=INK_PRINT + (110,), width=k)
    d.line([(130 * k, 161 * k), (905 * k, 161 * k)], fill=INK_PRINT + (60,), width=k)
    d.text((126 * k, 1012 * k), '134', font=font('pala.ttf', 20 * k), fill=INK_PRINT + (130,))
    d.text((1790 * k, 1012 * k), '135', font=font('pala.ttf', 20 * k), fill=INK_PRINT + (130,), anchor='ra')
    _C['spread_g2'] = img
    return img


def fall(i, t):
    """(dx, dy, drot) of scrap i: still until the stamp; then a jolt up and off the page, turning"""
    t0 = T_ILL + .02 + .06 * ((i * 37) % 7) / 7
    if t < t0: return 0., 0., 0.
    dt = t - t0
    rng = random.Random(70 + i)
    vx, vy, spin = rng.uniform(-160, 160), rng.uniform(-260, -140), rng.uniform(-260, 260)
    return vx * dt, vy * dt + 2900 * dt * dt, spin * dt


def pin(d, x, y, a, s=1.):
    """a pin: a short shadow, the head (red lacquer) with a highlight"""
    if a <= .01: return
    k = SS
    r = 8.5 * s
    d.ellipse(((x + 3 - r) * k, (y + 5 - r * .7) * k, (x + 3 + r) * k, (y + 5 + r * .7) * k), fill=(0, 0, 0, int(110 * a)))
    d.ellipse(((x - r) * k, (y - r) * k, (x + r) * k, (y + r) * k), fill=(168, 34, 26, int(255 * a)), outline=(70, 12, 8, int(255 * a)), width=max(1, int(1.2 * k)))
    d.ellipse(((x - r * .55) * k, (y - r * .6) * k, (x - r * .05) * k, (y - r * .15) * k), fill=(255, 190, 170, int(200 * a)))


def right_live(img, t):
    d = ImageDraw.Draw(img); k = SS
    pinned = {EVID[n]: DEL9[n] for n in ROWS9}
    # the scraps (all but the Heart): pasted; pinned one by one as each annual term is struck on the left
    for i, (kind, cen, (w, h), rot) in enumerate(SCRAPS):
        if kind == 'heart': continue
        dx, dy, dr = fall(i, t)
        c_ = (cen[0] + dx, cen[1] + dy)
        if c_[1] - h > 1100: continue
        _paste(img, _scrap_img(kind, w, h), c_, rot + dr)
        if i in pinned and t >= pinned[i]:
            u = clamp((t - pinned[i]) / .12)
            px, py = c_[0] + (h * .5 - 10) * math.sin(math.radians(rot + dr)) * 0, c_[1] - h / 2 + 10
            pin(d, px, py - 30 * (1 - u), u, 1 + .5 * (1 - u))
    # the Heart slip: cut along the blade at DISHEARTENED, the halves part; knocked off by the stamp too
    kind, cen, (w, h), rot = SCRAPS[7]
    if 'heart_full' not in _C:
        im = Image.new('RGBA', (w * k, h * k), PAPER_SCRAP + (255,)); dd = ImageDraw.Draw(im)
        dd.text((16 * k, 14 * k), 'Heart', font=font('Inkfree.ttf', 46 * k), fill=INK_OLD + (240,))
        dd.text((146 * k, 30 * k), ', we will forget him,', font=font('Inkfree.ttf', 26 * k), fill=INK_OLD + (120,))
        _C['heart_full'] = im
    sl = _C['heart_full']
    cut = ease((t - SNAP - .02) / .3)
    f1, f2 = fall(8, t), fall(9, t)
    if cut <= 0:
        _paste(img, sl, (cen[0] + f1[0], cen[1] + f1[1]), rot + f1[2])
    else:
        if 'heart_halves' not in _C:
            W_, H_ = sl.size
            yy, xx = np.mgrid[0:H_, 0:W_]
            side = (yy - H_ * .62) - .28 * (xx - W_ * .35)
            A = np.asarray(sl).copy(); up = A.copy(); up[side > 0, 3] = 0; dn = A.copy(); dn[side <= 0, 3] = 0
            _C['heart_halves'] = (Image.fromarray(up), Image.fromarray(dn))
        up, dn = _C['heart_halves']
        _paste(img, up, (cen[0] - 4 * cut + f1[0], cen[1] - 7 * cut + f1[1]), rot - 2.5 * cut + f1[2])
        _paste(img, dn, (cen[0] + 6 * cut + f2[0], cen[1] + 9 * cut + f2[1]), rot + 3 * cut + f2[2])
    if pinned and t >= DEL9['Sol']:                                        # the last pin, on the Heart (where you were)
        u = clamp((t - DEL9['Sol']) / .12)
        pin(d, cen[0] - 60 + f1[0], cen[1] - h / 2 + 10 + f1[1] - 30 * (1 - u), u, 1 + .5 * (1 - u))
    if SNAP - .02 <= t < SNAP + .25:
        u = clamp((t - SNAP + .02) / .08)
        x0, y0, x1, y1 = cen[0] - w / 2 - 40, cen[1] + 10, cen[0] + w / 2 + 40, cen[1] - 30
        d.line(((x0 * k, y0 * k), (lerp(x0, x1, u) * k, lerp(y0, y1, u) * k)), fill=(255, 250, 240, int(255 * (1 - clamp((t - SNAP - .06) / .2)))), width=2 * k)
    if WRITES_G_YOU[1] <= t < NEAR and (t * 3) % 1 < .55:
        x, y = WRITES_G_YOU[2]
        _txt(d, (x, y - 26), '_', font(HAND, 30 * k), INK_ME, .9)
    if t >= NEAR:
        u = outc((t - NEAR) / .09); x, y = WRITES_G_YOU[2]
        A_ = (x + 6, y - 10); C_ = (x + 360, y + 300)
        pts = [(lerp(A_[0], C_[0], s / 30), lerp(A_[1], C_[1], s / 30)) for s in range(int(30 * u) + 1)]
        for j in range(len(pts) - 1):
            wd = 1.2 + 7 * (j / 30) ** 1.6
            d.line(((pts[j][0] * k, pts[j][1] * k), (pts[j + 1][0] * k, pts[j + 1][1] * k)), fill=(10, 10, 14, 235), width=max(1, int(wd * k)))
        sp = outc((t - NEAR - .085) / .14)
        if sp > 0:
            rng = random.Random(5)
            d.ellipse(((C_[0] - 14 * sp) * k, (C_[1] - 10 * sp) * k, (C_[0] + 14 * sp) * k, (C_[1] + 10 * sp) * k), fill=(10, 10, 14, 235))
            for _ in range(18):
                an = math.atan2(C_[1] - A_[1], C_[0] - A_[0]) + rng.uniform(-.9, .9); dist = rng.uniform(16, 110) * sp; r = rng.uniform(1.5, 5)
                q = (C_[0] + math.cos(an) * dist, C_[1] + math.sin(an) * dist)
                d.ellipse(((q[0] - r) * k, (q[1] - r) * k, (q[0] + r) * k, (q[1] + r) * k), fill=(10, 10, 14, 230))
    # The Prince, pasted in on "Challenging your god" — the one thing the blow leaves (it only jumps)
    if t >= T_CLIP:
        if 'clip' not in _C:
            x0, y0, x1, y1 = CLIP_BOX
            im = Image.new('RGBA', ((x1 - x0) * k, (y1 - y0) * k), (66, 58, 46, 255)); dd = ImageDraw.Draw(im)
            dd.text((14 * k, 10 * k), 'MACHIAVELLI, Il Principe, XVII', font=font('pala.ttf', 15 * k), fill=INK_PRINT + (150,))
            for i, s_ in enumerate(CLIP_LINES): dd.text((14 * k, (40 + 34 * i) * k), s_, font=font('pala.ttf', 22 * k), fill=INK_PRINT + (235,))
            _C['clip'] = im
        u = outc((t - T_CLIP) / .22)
        x0, y0, x1, y1 = CLIP_BOX
        jump = 9 * math.exp(-max(t - T_ILL, 0) * 9) * math.sin(max(t - T_ILL, 0) * 40) if t >= T_ILL else 0.
        cen_c = ((x0 + x1) / 2 + 160 * (1 - u), (y0 + y1) / 2 - 220 * (1 - u) + jump)
        _paste(img, _C['clip'], cen_c, 1.5 + 8 * (1 - u), alpha=min(1., u * 3))


_params_s11 = params


def params(t):
    p = _params_s11(t)
    sh = flash(t, T_ILL, 8) * 4.
    for t0 in RIPS: sh += .6 * flash(t, t0, 18)
    p['u_shake'] = (.004 * sh * math.sin(t * 97), .006 * sh * math.sin(t * 131) + .006 * flash(t, T_ILL, 12))
    return p
