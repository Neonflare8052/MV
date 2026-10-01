"""s10e (sample) · 1:58.333–2:05.361  the epicycles erased; pushed off the centre, it argues for itself.

Kepler (1609) took Tycho's observations and threw the epicycles away: no loops, plain orbits, the Earth one planet among
the others. The loops of s09 were never the world's: they came from insisting that I am the centre.
Epicycles are a Fourier series — a chain of turning circles can draw any curve; erasing them one by one is a low-pass
filter (0:44's AC→DC run backwards). Each little circle carries a fragment of the journey; when it goes, the fragment
turns to sand.
  118.333  out of s09: Tycho's loops (the world before the Sun went, as ideal circles) are fitted: each body's path
           = its own circle + one annual circle — the same annual circle in every row of the program window below,
           each row carrying a fragment of the journey
  118.93…  a row a half-beat: its annual term struck out (del ☿.annual …), its fragment to sand; the loops undo into a
           clean circle on the empty place. The Moon's row has nothing to remove: it really goes round me
  120.860  FRAGMENTS: the empty place's own annual term — its circle round me — is struck: it stops; it is the centre;
           the same circle is now mine round it. annual == terra.orbit  # it was me. The window goes into the paper:
           from the program to the page, from the technical to the humane
  121.677  Then maybe: pushed off the centre, it argues for itself (Descartes, 1637), writing with its gap as the nib:
              me.doubt(everything)                 — the orbit, doubted, goes to dashes
              me.doubt().therefore(me.think())
              me.think().therefore(me.exist())     — underlined
              me.exist().therefore(you.            — and cannot go on
  124.464  the pen thrown (s10's ink streak); the ring goes to the centre, to the empty place, and grows
  124.890  DISHEARTENED: the heart, which can be doubted, is cut (s10's blade, non necesse); 125.361 s11
The draft pages (Dickinson under, π over), the reading brackets, the blade and the split are s10's.
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

T3 = (Path(__file__).resolve().parents[2] / 'tests' / 't03_fragments' / 'scene.glsl').read_text(encoding='utf-8')
FRAG_GLSL = T3[T3.index('float gearSD('):T3.index('// dissolve into sand')]
FRAG_GLSL = FRAG_GLSL[:FRAG_GLSL.index('vec2 fragPos(int i)')]

SRC = r'''#version 330
uniform vec2 u_res; uniform float u_time, u_weight;
uniform float u_cursor, u_ringA, u_R, u_gap, u_half;
uniform vec2  u_poly[160]; uniform int u_n; uniform float u_polyA;
uniform vec2 u_ec[10]; uniform float u_er[9]; uniform float u_eA;       // the epicycles: centres (and the tip), radii
uniform vec2 u_ringC, u_void; uniform float u_voidA, u_dash, u_fs, u_prevA;
uniform sampler2D u_prev, u_write, u_astro;
uniform float u_curveA;
uniform vec2  u_fpos[7]; uniform float u_erase[7]; uniform float u_fragA;
uniform float u_keep, u_wscale, u_cur, u_sel;
uniform vec3 u_lines[40]; uniform int u_nl; uniform vec2 u_hx;   // lines: (centre y, x0, x1) in page units; Heart's x0, x1
uniform float u_scroll, u_overA, u_heartA, u_ink, u_slash, u_split, u_heart, u_snap;
uniform float u_splat, u_blade, u_fadeMarks;
uniform sampler2D u_under, u_over, u_word, u_note;
uniform float u_flat, u_noteX;   // its heartbeat drawn flat; how much of 'non necesse' is written
out vec4 fragColor;
#define PI 3.14159265
#define TAU 6.28318531
float PX;
float h12(vec2 p){ vec3 p3=fract(vec3(p.xyx)*.1031); p3+=dot(p3,p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }
float vn(vec2 p){ vec2 i=floor(p),f=fract(p); f=f*f*(3.-2.*f);
  return mix(mix(h12(i),h12(i+vec2(1,0)),f.x),mix(h12(i+vec2(0,1)),h12(i+vec2(1,1)),f.x),f.y); }
float fbm(vec2 p){ float s=0.,a=.5; for(int i=0;i<4;i++){ s+=a*vn(p); p=p*2.03+1.7; a*=.5; } return s; }
mat2 rot(float a){ float c=cos(a),s=sin(a); return mat2(c,s,-s,c); }
float wrapA(float a){ return mod(a+PI,TAU)-PI; }

// the knife cut through (0,-.4): a thin ragged gap, shadowed inside, one lip catching the light.
// returns the colour after the cut; w = half gap width (0 = not yet opened)
vec3 knifeCut(vec3 c, vec2 uv, float w, float PXs){
  vec2 sd=normalize(vec2(1.,-.35)), nn=vec2(-sd.y,sd.x);
  float along=dot(uv-vec2(0.,-.4),sd), across=dot(uv-vec2(0.,-.4),nn);
  if(w<=0.) return c;
  float wr=w*(1.+.45*(vn(vec2(along*55.,1.3))-.5)+.25*(vn(vec2(along*260.,7.))-.5));
  float gap=1.-smoothstep(wr-PXs,wr+PXs,abs(across));
  vec3 inside=vec3(.004)+vec3(.02,.015,.01)*smoothstep(-wr,wr,across);          // light falls in from one side
  c=mix(c,inside,gap);
  float lip=exp(-abs(across-wr)*900.)*step(0.,across);                              // upper lip catches the light
  float sh=exp(-abs(-across-wr)*300.)*step(across,0.);                              // lower lip in shadow
  c+=vec3(.55,.48,.38)*.35*lip;
  c*=1.-.45*sh;
  return c;
}
float sdSeg(vec2 p, vec2 a, vec2 b){ vec2 pa=p-a, ba=b-a; float h=clamp(dot(pa,ba)/max(dot(ba,ba),1e-9),0.,1.); return length(pa-ba*h); }
float sdCap(vec2 p, vec2 a, vec2 b, float ra, float rb){ vec2 pa=p-a, ba=b-a; float h=clamp(dot(pa,ba)/max(dot(ba,ba),1e-9),0.,1.); return length(pa-ba*h)-mix(ra,rb,h); }
float sdBox(vec2 p, vec2 b){ vec2 d=abs(p)-b; return length(max(d,0.))+min(max(d.x,d.y),0.); }
float line(float d, float w){ return 1.-smoothstep(w-PX,w+PX,d); }
''' + FRAG_GLSL + r'''
vec4 dissolving(int i, vec2 p){
  float e=u_erase[i];
  if(e>=1.) return vec4(0.);
  vec2 c=u_fpos[i]; float s=u_fs;
  vec2 q=(p-c)/s;
  if(length(q)>3.2) return vec4(0.);
  float n=vn(q*7.)*.6+vn(q*23.)*.4;
  float keep=smoothstep(e*1.25-.08,e*1.25,n);
  vec4 f=fragment(i,q)*keep;
  float edge=(1.-smoothstep(0.,.08,abs(n-e*1.25)))*step(.001,e);
  f.rgb+=vec3(1.,.9,.75)*edge*fragment(i,q).a*1.5;
  vec2 out_=normalize(c+vec2(1e-4));
  vec4 g=fragment(i,q-out_*e*1.5-vec2(vn(q*3.+7.)-.5,vn(q*3.+1.)-.5)*e*1.2);
  float grain=step(.8,h12(floor(p*u_res.y*.5)))*(1.-keep);
  f.rgb+=g.rgb*grain*(1.-e)*step(.001,e)*1.4;
  return f*u_fragA;
}
float RY, RX0, RX1;                 // the line being read: screen y, x extent
void reader(){
  float v=1.-fract(-.4*.31+.5+u_scroll);                   // page coordinate (from the top) under the reading head
  float best=1e3; int bi=0;
  for(int i=0;i<40;i++){ if(i>=u_nl) break; float d=abs(u_lines[i].x-v); d=min(d,1.-d); if(d<best){ best=d; bi=i; } }
  vec3 L=u_lines[bi];
  float py=(1.-L.x-.5-u_scroll)/.31;
  py+=floor((-.4-py)*.31+.5)/.31;                           // the repeat of the page nearest the head
  RY=py;
  RX0=mix((L.y-.5)/.62,(u_hx.x-.5)/.62,u_sel); RX1=mix((L.z-.5)/.62,(u_hx.y-.5)/.62,u_sel);
}
vec3 cursors(vec2 uv){
  if(u_cur<=0.) return vec3(0.);
  float g=0.;
  for(int s=0;s<2;s++){
    float x=s==0?RX0-.014:RX1+.014, dir=s==0?1.:-1.;
    g+=line(sdSeg(uv,vec2(x,RY-.03),vec2(x,RY+.03)),.0013);
    g+=line(sdSeg(uv,vec2(x,RY+.03),vec2(x+dir*.008,RY+.03)),.0013)+line(sdSeg(uv,vec2(x,RY-.03),vec2(x+dir*.008,RY-.03)),.0013);
  }
  return vec3(.95,.9,.82)*g*u_cur;
}
vec3 paper(vec2 uv){
  // the draft pages, split along the slash
  vec2 sd=normalize(vec2(1.,-.35));
  vec2 nn=vec2(-sd.y,sd.x);
  float side=sign(dot(uv-vec2(0.,-.4),nn));
  vec2 p=uv-nn*side*u_split*.012;
  vec3 c=vec3(.62,.5,.36)*(.55+.6*fbm(p*4.))*.085;
  vec2 tuv=vec2(p.x*.62+.5,fract(p.y*.62*.5+.5+u_scroll));
  float under=texture(u_under,tuv).a;
  float over=texture(u_over,tuv).a;
  float read=1.+.9*u_cur*(1.-u_keep)*(1.-smoothstep(.022,.034,abs(p.y-RY)));
  c+=vec3(.55,.2,.12)*.085*under*(.35+.65*u_overA)*(1.-u_keep)*read;
  c+=vec3(.86,.8,.68)*.13*over*u_overA;
  // the one word left: Heart — a word of the poem itself; everything else fades, it stays, brightens, grows a little
  vec2 W=vec2(0.,-.4);
  vec2 pw=W+(p-W)/u_wscale;
  vec2 tw=vec2(pw.x*.62+.5,fract(pw.y*.62*.5+.5+u_scroll));
  float word=texture(u_word,tw).a;
  c+=mix(vec3(.55,.2,.12)*.085*(.35+.65*u_overA),vec3(.7,.28,.16)*.5,u_keep)*word*(1.-u_fadeMarks);
  // a pen thrown at the page: a tapered, ragged streak that thickens toward where it lands, a pool of ink there,
  // and drops thrown on — tear-shaped, heads outward, tails back toward the landing
  float ink=0.;
  if(u_ink>0.){
    vec2 A=vec2(-.92,.2), C=vec2(.2,-.33);
    vec2 dir=normalize(C-A);
    vec2 H=mix(A,C,u_ink);
    vec2 pa=p-A; float L=length(C-A);
    float s_=clamp(dot(pa,dir)/L,0.,u_ink);
    float w=mix(.0016,.0105,pow(s_,1.6))*(.7+.6*fbm(p*95.));
    float d=length(pa-dir*s_*L)-w;
    ink=max(ink,1.-smoothstep(-PX,PX,d));
    ink=max(ink,.35*exp(-max(d,0.)*180.)*step(s_,u_ink));                       // bleeding into the paper
    if(u_splat>0.){
      float pool=length((p-C)*vec2(1.,1.3))-.019*(.75+.5*fbm(p*70.))*min(u_splat*3.,1.);
      ink=max(ink,1.-smoothstep(-PX,PX,pool));
      for(int k=0;k<24;k++){
        float fk=float(k), h=h12(vec2(fk,3.)), g=h12(vec2(fk,5.));
        float an=atan(dir.y,dir.x)+(g-.5)*1.5*(1.-.5*h);
        vec2 dv=vec2(cos(an),sin(an));
        float dist=(.025+.26*h*h)*u_splat;
        vec2 head=C+dv*dist;
        float r=(.0035+.011*(1.-h)*(1.-h))*(.7+.6*h12(vec2(fk,9.)));
        float td=sdCap(p,head,head-dv*r*(2.5+3.*h)*min(u_splat*2.,1.),r,r*.22);
        ink=max(ink,(1.-smoothstep(-PX,PX,td))*step(.02,u_splat));
      }
      for(int k=0;k<16;k++){                                                        // fine mist
        float fk=float(k);
        vec2 mp=C+vec2(h12(vec2(fk,11.))-.35,h12(vec2(fk,13.))-.6)*.16*u_splat;
        ink=max(ink,1.-smoothstep(.0,.0032,length(p-mp)));
      }
    }
    c=mix(c,vec3(.012,.012,.018),clamp(ink,0.,1.)*.92*(1.-u_fadeMarks));
  }
  // the blade: a glint races along the line, leaving a clean incision; then the page opens along it
  {
    vec2 sd=normalize(vec2(1.,-.35)), nn=vec2(-sd.y,sd.x);
    float along=dot(uv-vec2(0.,-.4),sd), across=abs(dot(uv-vec2(0.,-.4),nn));
    if(u_blade>-1.5){
      float behind=step(along,u_blade);
      float trail=exp(-max(u_blade-along,0.)*3.)*behind;
      c+=vec3(1.,.97,.92)*(exp(-across*1500.)*2.2+exp(-across*160.)*.18)*trail*(1.-u_split);
      c=mix(c,c*.35,(1.-smoothstep(.0,.0012,across))*behind*(1.-u_split));             // the incision
    }
    c=knifeCut(c,uv,u_split*.012,PX);
  }
  vec2 pe=abs(uv)-vec2(.82,.48);
  return c*(1.-smoothstep(-.02,.01,max(pe.x,pe.y)));
}
void main(){
  vec2 uv=(gl_FragCoord.xy-.5*u_res)/u_res.y; PX=1./u_res.y;
  reader();
  vec3 col=vec3(.003)+paper(uv)*u_polyA;
  col+=cursors(uv)*u_polyA;
  // outer outline: heptagon, corners cut away, converging to a circle
  if(u_polyA>0.&&u_n>1){
    float d=1e3;
    for(int i=0;i<160;i++){ if(i>=u_n) break; vec2 a=u_poly[i], b=u_poly[(i+1)%u_n]; d=min(d,sdSeg(uv,a,b)); }
    float dash=mix(1.,.15+.85*step(.5,fract(atan(uv.y-u_void.y,uv.x-u_void.x)/TAU*90.)),u_dash);
    col+=vec3(.86,.8,.7)*(line(d,.0016)+.2*exp(-d*120.))*u_curveA*dash*(1.-.45*u_dash);
  }
  // the epicycles: thin circles, the arms between their centres, a bright point at the tip that draws
  if(u_eA>0.){
    float g=0., ar=0.;
    for(int i=0;i<9;i++){
      if(u_er[i]<=.0005) continue;
      g=max(g,line(abs(length(uv-u_ec[i])-u_er[i]),.0007)*.55);
      ar=max(ar,line(sdSeg(uv,u_ec[i],u_ec[i+1]),.0008));
      g=max(g,(1.-smoothstep(.0028,.0028+PX,length(uv-u_ec[i]))));
    }
    col+=vec3(.86,.8,.7)*(g*.6+ar*.5)*u_eA;
    col+=vec3(1.,.95,.88)*(exp(-length(uv-u_ec[9])*240.)*1.4+exp(-length(uv-u_ec[9])*40.)*.15)*u_eA;
  }
  // the empty place: a dashed ring
  if(u_voidA>0.){
    float dv=abs(length(uv-u_void)-.022);
    float dash=step(.5,fract(atan(uv.y-u_void.y,uv.x-u_void.x)/TAU*14.));
    col+=vec3(.95,.9,.8)*line(dv,.0011)*dash*u_voidA*.8;
  }
  { vec4 as=texture(u_astro,gl_FragCoord.xy/u_res); col=mix(col,pow(as.rgb,vec3(2.2))*1.5,as.a); }   // the paths, the window
  for(int i=0;i<7;i++){ vec4 f=dissolving(i,uv); col=col*(1.-f.a)+f.rgb; }
  if(u_ringA>0.){
    vec2 ru=uv-u_ringC;
    float lw=.0085*clamp(u_R/.15,.4,1.);
    float r=length(ru), a=atan(ru.y,ru.x), g=abs(wrapA(a-u_gap));
    vec2 e1=vec2(cos(u_gap+u_half),sin(u_gap+u_half))*u_R, e2=vec2(cos(u_gap-u_half),sin(u_gap-u_half))*u_R;
    float dr=g>u_half?abs(r-u_R):min(length(ru-e1),length(ru-e2));
    col=mix(col,vec3(.92,.91,.88),line(dr,lw)*u_ringA);
    col+=vec3(1.,.95,.9)*exp(-max(dr-lw,0.)*70.)*.25*u_ringA;
    col+=vec3(1.,.9,.8)*(exp(-length(ru-e1)*90.)+exp(-length(ru-e2)*90.))*u_snap*1.5;
    if(u_heart>0.){
      float x=ru.x/u_R; float y=(.3*exp(-pow((x-.05)/.06,2.))-.12*exp(-pow((x+.05)/.05,2.))-.1*exp(-pow((x-.18)/.05,2.)))*(1.-u_flat);
      float hd=max(abs(ru.y/u_R-y)*u_R,(abs(x)-.62)*u_R);
      col+=vec3(.5,1.,.7)*(line(hd,.0022)+exp(-hd*120.)*.4)*u_heart;
    }
    // non necesse: written in its own light beside the cut (it decides it does not need the heart)
    vec2 sn=gl_FragCoord.xy/u_res;
    float na=texture(u_note,sn).a*step(sn.x,u_noteX);
    col+=vec3(.95,.86,.68)*na*.55;
  }
  // what it writes, in its own light
  vec2 sw=gl_FragCoord.xy/u_res;
  col+=vec3(.95,.88,.72)*texture(u_write,sw).a*.62;
  // out of s09: its last frame, shown as s09 (s08c) shows it, fading
  if(u_prevA>0.){ vec3 pv=vec3(.004)+pow(texture(u_prev,sw).rgb,vec3(2.2))*2.; col=mix(col,pv,u_prevA); }
  fragColor=vec4(col*u_weight,1.);
}
'''
POST = dict(u_bloom=.5, u_ca=.004)
ERASE = [118.926, 119.158, 119.390, 119.617, 119.843, 120.307]
FRAG_T, TRY, NEAR, SNAP, END = 120.860, 121.677, 124.464, 124.890, 125.708
ORDER = [2, 5, 0, 4, 1, 6, 3]
RP = .36
T_IN = 118.333
T_CEN = 121.20                                             # the eye draws in on the empty place

# ---- the fit: Tycho's loops (s09's world, before the Sun went: ideal circles) taken apart into own + annual ----------
import importlib.util as _iu
_sp = _iu.spec_from_file_location('s09t_for_s10e_fit', Path(__file__).resolve().parent / 's09t.py')
S9 = _iu.module_from_spec(_sp); _sp.loader.exec_module(S9)
A_ = S9.A; AE = A_['Terra']
W_ = {n: S9.omega(n) for n in ('Mercurius', 'Venus', 'Terra', 'Mars', 'Iuppiter', 'Saturnus')}
PH_ = {'Mercurius': .6, 'Venus': 2.4, 'Terra': 1.3, 'Mars': 4.0, 'Iuppiter': 5.2, 'Saturnus': 3.0}
LUNA_R, LUNA_W = S9.LUNA_R, 2 * math.pi / S9.LUNA_T
GLY = S9.GLY
ROWS = ['Mercurius', 'Venus', 'Mars', 'Iuppiter', 'Saturnus', 'Luna', 'Sol']          # the order they are taken apart
DEL_T = dict(zip(ROWS, ERASE + [FRAG_T]))
FRAG_OF = {n: ORDER[k] for k, n in enumerate(ROWS)}                                   # the journey's fragment each one carries
K0, K1 = .10, .28                                                         # uv per unit: while I am the centre; after
ME0 = (0., .13)
WIN = (-.64, -.215, .64, -.478)                                                       # the program window (uv: x0, y0 top, x1, y1)


def tau(t): return t - T_IN


def ang(n, t): return PH_[n] + W_[n] * tau(t)


def e_pos(t): a = ang('Terra', t); return AE * math.cos(a), AE * math.sin(a)


def own(n, t):
    if n == 'Luna': a = 2.2 + LUNA_W * tau(t); return LUNA_R * math.cos(a), LUNA_R * math.sin(a)
    a = ang(n, t); return A_[n] * math.cos(a), A_[n] * math.sin(a)


def void(t): e = e_pos(t); return -e[0], -e[1]                                        # the empty place, as seen from me


def geo(n, t):
    """Tycho's frame, the annual term still in: the planet's own circle carried on the empty place"""
    if n == 'Luna': return own('Luna', t)
    if n == 'Sol': return void(t)
    v, o = void(t), own(n, t); return v[0] + o[0], v[1] + o[1]


def dprog(n, t): return ease((t - DEL_T[n]) / .3)


def recentre(t): return ease((t - FRAG_T - .05) / .3)                                 # the empty place's own annual removed


def zoom(t): return lerp(K0, K1, ease((t - T_CEN) / .45))


def S(t, P):
    """world -> screen uv. Before the last deletion, me fixed at ME0; after it, the empty place is the origin"""
    D = recentre(t); k = zoom(t)
    v = void(t)
    org = (lerp(ME0[0], 0., D), lerp(ME0[1], 0., D))
    if t < TRY:
        org_k = org
    else:
        org_k = (0., 0.)
    vv = v if t < FRAG_T + .35 else void(FRAG_T + .35)                                 # once it is the centre it stops
    return (org_k[0] + k * (P[0] - vv[0] * D), org_k[1] + k * (P[1] - vv[1] * D))


def me_pos(t):
    """me on screen: fixed while I am the centre, then going round the empty place (my own year)"""
    if t < FRAG_T + .05: return S(t, (0., 0.))
    D = recentre(t)
    tf = FRAG_T + .35
    if t <= tf: return S(t, (0., 0.))
    # after: the empty place still; I go round it from where I was
    a0 = math.atan2(-void(tf)[1], -void(tf)[0]); a = a0 + W_['Terra'] * (t - tf)
    k = zoom(t); return (k * AE * math.cos(a), k * AE * math.sin(a))


# what it writes: (t0, t1, text, x, y) in screen px (1080 high); the pen is the ring, its gap the nib
FONT_W = 'C:/Windows/Fonts/segoepr.ttf'
WSIZE = 37
WRITES = [(121.74, 122.30, 'me.doubt(everything)', 140, 176),
          (122.714, 123.28, 'me.doubt().therefore(me.think())', 140, 246),
          (123.32, 123.90, 'me.think().therefore(me.exist())', 140, 316),
          (124.00, 124.40, 'me.exist().therefore(you.', 140, 386)]
T_UNDER = (123.92, 124.0)


def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def outc(x): x = clamp(x); return 1 - (1 - x) ** 3
def lerp(a, b, k): return a + (b - a) * k


def saccade(t, t0, a, b, dur=.07, over=.07):
    if t < t0: return a
    x = (t - t0) / dur
    if x < 1: return a + (b - a) * (1 + over) * outc(x)
    return b + (b - a) * over * (1 - ease((t - t0 - dur) / .14))


def corner_angle(i): return math.radians(90 + i * 360 / 7)


_WF = {}


def wfont():
    if 'f' not in _WF: _WF['f'] = ImageFont.truetype(FONT_W, WSIZE)
    return _WF['f']


def head(t):
    f = wfont()
    for t0, t1, s, x, y in WRITES:
        if t0 <= t <= t1 + .02:
            k = clamp((t - t0) / (t1 - t0)); n = k * len(s); i = int(n)
            return x + f.getlength(s[:i]) + (f.getlength(s[:i + 1]) - f.getlength(s[:i])) * (n - i), y + 30
    return None


def px2uv(p): return ((p[0] - 960) / 1080, (540 - p[1]) / 1080)
def uv2px(q): return (960 + q[0] * 1080, 540 - q[1] * 1080)


def ring_place(t):
    if t < T_IN + .45:
        k = ease((t - T_IN) / .45); m = me_pos(t)
        return (lerp(0., m[0], k), lerp(.037, m[1], k)), .028
    if t < TRY: return me_pos(t), .028 if t < FRAG_T else .03
    keys = [(TRY, me_pos(TRY))]
    for t0, t1, s, x, y in WRITES:
        hx = head(t0 + 1e-4); keys.append((t0 - .02, px2uv((hx[0], hx[1] - 46))))
        he = head(t1); keys.append((t1, px2uv((he[0], he[1] - 46))))
    R = .034
    if t <= keys[-1][0]:
        for t0, t1, *_ in WRITES:
            if t0 <= t <= t1:
                h = head(t); return px2uv((h[0], h[1] - 46)), R
        for (ta, pa), (tb, pb) in zip(keys, keys[1:]):
            if ta <= t <= tb:
                k = ease(clamp((t - ta) / max(tb - ta, 1e-4)))
                return (lerp(pa[0], pb[0], k), lerp(pa[1], pb[1], k)), R
        return keys[-1][1], R
    last = keys[-1][1]
    if t < NEAR: return (last[0] + .002 * math.sin(t * 60), last[1]), R
    k = ease((t - NEAR) / .34)
    return (lerp(last[0], 0., k), lerp(last[1], 0., k)), lerp(.034, .15, outc((t - NEAR - .05) / .3))


# ---- the window's rows ----------------------------------------------------------------------------------------------
def row_text(n):
    if n == 'Sol': return '—', 'annual(1.20, 5.0s)', '# where you were'
    if n == 'Luna': return f'own({LUNA_R:.2f}, {S9.LUNA_T:.1f}s)', '+ 0', '# goes round me'
    T = 2 * math.pi / W_[n]
    return f'own({A_[n]:.2f}, {T:4.1f}s)', '+ annual(1.20, 5.0s)', ''


WX0, WY0 = 960 + WIN[0] * 1080, 540 - WIN[1] * 1080                                    # px
WX1, WY1 = 960 + WIN[2] * 1080, 540 - WIN[3] * 1080
ROW_H, ROW0 = 30, WY0 + 42


def row_y(i): return ROW0 + i * ROW_H


def win_alpha(t): return ease((t - T_IN - .15) / .3) * (1 - ease((t - 121.45) / .45))


def params(t):
    k = ease((t - T_IN) / .45)
    POST.update(u_bloom=lerp(.26, .5, k), u_ca=lerp(0., .004, k))
    c, R = ring_place(t)
    # the gap: it looks at the one being taken apart; then down, the nib
    g = 90.
    for n in ROWS:
        tk = DEL_T[n]
        if t >= tk - .14:
            q = S(t, geo(n, t))
            g = saccade(t, tk - .14, g, math.degrees(math.atan2(q[1] - c[1], q[0] - c[0])))
    if t >= TRY - .12: g = saccade(t, TRY - .12, g, -90., .12)
    erase = [0.] * 7
    for n in ROWS:
        if n != 'Luna': erase[FRAG_OF[n]] = clamp((t - DEL_T[n]) / .5)
    wa = win_alpha(t)
    if wa < 1 and t > 121: erase[FRAG_OF['Luna']] = clamp((t - 121.45) / .5)              # the Moon's goes with the window
    fpos = [(0., 0.)] * 7
    for i, n in enumerate(ROWS): fpos[FRAG_OF[n]] = px2uv((WX0 + 30, row_y(i) + 15))
    base_half = math.radians(27.); half = base_half
    if NEAR + .1 < t < SNAP:
        x = clamp((t - NEAR - .1) / (SNAP - NEAR - .1))
        half = base_half * (1 - .55 * (1 - (1 - x) ** 1.6)) + math.radians(1.2) * math.sin(t * 47.) * x
    if t > SNAP:
        y = t - SNAP; half = base_half + math.radians(9.) * math.exp(-y * 7.) * math.cos(y * 26.)
    heart = (.85 * ease((t - (NEAR + .15)) / .12) * (1 - ease((t - (SNAP + .02)) / .08))) if NEAR + .15 < t < SNAP + .1 else 0.
    flat = ease((t - (NEAR + .3)) / .22)
    # my year's circle: the empty place's path round me becomes my path round it — the same circle, the centre changed
    D = recentre(t)
    if t >= FRAG_T - .4:
        cc = (lerp(S(t, (0., 0.))[0], S(t, void(min(t, FRAG_T + .35)))[0], D), lerp(S(t, (0., 0.))[1], S(t, void(min(t, FRAG_T + .35)))[1], D))
        rr = zoom(t) * AE
        poly = [(cc[0] + rr * math.cos(2 * math.pi * i / 160), cc[1] + rr * math.sin(2 * math.pi * i / 160)) for i in range(160)]
        pa = ease((t - FRAG_T + .4) / .4)
    else:
        poly, pa = [(0., 0.)] * 2, 0.
    scroll = 0.
    for k_ in range(200):
        tt = 118.3 + (t - 118.3) * (k_ + .5) / 200
        v = .09 * (1 - ease((tt - TRY) / (NEAR - TRY - .6)))
        scroll += v * (t - 118.3) / 200 if t > 118.3 else 0
    dash = ease((t - WRITES[0][0] - .1) / .4) * (1 - ease((t - WRITES[2][1]) / .4))
    vo = S(t, void(min(t, FRAG_T + .35)))
    paper = ease((t - T_IN - .1) / .4) * (.3 + .7 * ease((t - 120.2) / 1.3))         # the paper comes up as the program empties
    return dict(u_cursor=0., u_ringA=1., u_R=R, u_ringC=c,
                u_gap=math.radians(g), u_half=half, u_poly=(poly + [poly[-1]] * 160)[:160], u_n=len(poly) if pa > 0 else 0, u_polyA=paper,
                u_ec=[(0., 0.)] * 10, u_er=[0.] * 9, u_eA=0., u_void=vo, u_voidA=ease((t - T_IN - .2) / .4) * (1 - ease((t - NEAR) / .3)),
                u_dash=dash, u_fs=.0105, u_prevA=1 - ease((t - T_IN) / .38), u_curveA=pa,
                u_fpos=fpos, u_erase=erase, u_fragA=wa,
                u_scroll=scroll + SCROLL0, u_overA=ease((t - 118.6) / .8) * (1 - ease((t - 123.2) / 1.)), u_heartA=0.,
                u_keep=ease((t - 123.4) / .7), u_wscale=1.,
                u_cur=ease((t - 119.2) / .4) * (1 - ease((t - TRY + .2) / .3)), u_sel=ease((t - 123.2) / .35),
                u_lines=LINES, u_nl=NL, u_hx=HX,
                u_ink=outc((t - NEAR) / .09), u_slash=0., u_splat=outc((t - NEAR - .085) / .14),
                u_blade=(-1.2 + 2.5 * clamp((t - SNAP + .02) / .08)) if t >= SNAP - .02 else -9., u_fadeMarks=ease((t - 125.35) / .33),
                u_split=ease((t - SNAP - .03) / .3), u_heart=heart, u_flat=flat,
                u_noteX=NOTE_X0 + (NOTE_X1 - NOTE_X0) * clamp((t - SNAP - .06) / .36),
                u_snap=math.exp(-max(t - SNAP, 0) * 6) * (t > SNAP) + .4 * clamp((t - NEAR - .1) / (SNAP - NEAR - .1)) * (t < SNAP))


# ---- the overlay: the paths, the circles, the bodies; the program window ---------------------------------------------
WARM_, GOLD_, GREEN_, DIM_ = (246, 232, 212), (206, 168, 104), (140, 255, 200), (120, 112, 100)
_FN = {}


def fnt(n, sz):
    k = (n, int(sz))
    if k not in _FN: _FN[k] = ImageFont.truetype('C:/Windows/Fonts/' + n, int(sz))
    return _FN[k]


def astro_layer(t, w, h):
    SSx = 2
    im = Image.new('RGBA', (1920 * SSx, 1080 * SSx), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    P = lambda q: (uv2px(q)[0] * SSx, uv2px(q)[1] * SSx)
    def line(pts, col, a, wd=1.):
        if a > .01 and len(pts) > 1: d.line(pts, fill=col + (int(255 * clamp(a)),), width=max(1, int(wd * SSx)))
    def circ(cq, r_uv, col, a, wd=1., n=120):
        line([P((cq[0] + r_uv * math.cos(2 * math.pi * i / n), cq[1] + r_uv * math.sin(2 * math.pi * i / n))) for i in range(n + 1)], col, a, wd)
    fade_all = 1 - ease((t - 121.6) / .5)                     # the others go once I am the one going round
    k = zoom(t)
    # the loops (annual still in), or — once taken apart — a clean circle on the empty place
    for n in ROWS:
        dp = dprog(n, t) if n != 'Luna' else 0.
        ga = ease((t - T_IN - .1) / .4) * fade_all
        if n == 'Sol':
            # the empty place's own path: the circle it goes round me on (handed to the shader's circle at the end)
            if t < FRAG_T + .1: circ(S(t, (0., 0.)), k * AE, WARM_, .35 * ga * (1 - ease((t - FRAG_T + .4) / .4)), .8)
            continue
        if dp < 1 and ga > 0:
            pts = [P(S(t, geo(n, t - j * .025))) for j in range(0, 200)]
            for j in range(0, len(pts) - 3, 3):
                line(pts[j:j + 4], GOLD_, (.75 * (1 - j / len(pts)) + .1) * (1 - dp) * ga, 1.)
        if dp > 0 and n != 'Luna':
            circ(S(t, void(min(t, FRAG_T + .35))), k * A_[n], WARM_, .55 * dp * ga, .9)
        if n == 'Luna':
            circ(me_pos(t), k * LUNA_R, WARM_, .3 * ga, .7)
        # the body
        q = S(t, geo(n, t)) if dp < 1 else S(t, (void(min(t, FRAG_T + .35))[0] + own(n, t)[0], void(min(t, FRAG_T + .35))[1] + own(n, t)[1]))
        if n == 'Luna': q = (me_pos(t)[0] + k * own('Luna', t)[0], me_pos(t)[1] + k * own('Luna', t)[1])
        p = P(q)
        d.ellipse((p[0] - 5 * SSx, p[1] - 5 * SSx, p[0] + 5 * SSx, p[1] + 5 * SSx), outline=WARM_ + (int(220 * ga),), width=SSx)
        d.text((p[0] + 12 * SSx, p[1] - 12 * SSx), GLY[n], font=fnt('seguisym.ttf', 13 * SSx), fill=WARM_ + (int(220 * ga),), anchor='lm')
    # the program window
    wa = win_alpha(t)
    if wa > 0:
        X0, Y0, X1, Y1 = WX0 * SSx, WY0 * SSx, WX1 * SSx, WY1 * SSx
        d.rectangle((X0, Y0, X1, Y1), fill=(6, 7, 8, int(225 * wa)), outline=DIM_ + (int(200 * wa),), width=SSx)
        d.rectangle((X0, Y0, X1, Y0 + 30 * SSx), fill=(18, 20, 22, int(240 * wa)))
        fm = fnt('CascadiaMono.ttf', 17 * SSx); fs = fnt('CascadiaMono.ttf', 14 * SSx)
        d.text((X0 + 14 * SSx, Y0 + 6 * SSx), 'fit(tycho.paths)    →  own + annual', font=fs, fill=GREEN_ + (int(230 * wa),))
        d.text((X1 - 14 * SSx, Y0 + 6 * SSx), 'epicycles.py', font=fs, fill=DIM_ + (int(200 * wa),), anchor='ra')
        for i, n in enumerate(ROWS):
            y = row_y(i) * SSx
            ra = wa * ease((t - T_IN - .25 - i * .06) / .2)
            if ra <= 0: continue
            a1, a2, cm = row_text(n)
            x = X0 + 58 * SSx
            d.text((x, y), GLY[n] if n != 'Sol' else '∅', font=fnt('seguisym.ttf', 17 * SSx), fill=WARM_ + (int(240 * ra),))
            x += 40 * SSx
            d.text((x, y), a1, font=fm, fill=WARM_ + (int(220 * ra),))
            x2 = x + fm.getlength(a1.ljust(17))
            gone = clamp((t - DEL_T[n]) / .22) if n != 'Luna' else 0.
            col2 = GOLD_ if n != 'Luna' else DIM_
            d.text((x2, y), a2, font=fm, fill=col2 + (int(230 * ra * (1 - .65 * gone)),))
            if gone > 0:                                             # struck out
                wl = fm.getlength(a2) * gone
                d.line((x2 - 4 * SSx, y + 12 * SSx, x2 + wl, y + 10 * SSx), fill=(255, 240, 220, int(255 * ra)), width=2 * SSx)
                if gone >= 1: d.text((x2 + fm.getlength(a2) + 16 * SSx, y), f'del  {GLY[n] if n != "Sol" else "∅"}.annual', font=fs, fill=GREEN_ + (int(200 * ra),))
            if cm and not (gone >= 1): d.text((x2 + fm.getlength(a2) + 16 * SSx, y + 2 * SSx), cm, font=fs, fill=DIM_ + (int(200 * ra),))
            if n == 'Luna' and t >= DEL_T['Luna']:
                d.text((x2 + fm.getlength(a2) + 220 * SSx, y + 2 * SSx), '(nothing to remove)', font=fs, fill=GREEN_ + (int(180 * ra * ease((t - DEL_T['Luna']) / .2)),))
        # the last line: what the repeated term was
        s = 'annual == terra.orbit      # it was me'
        nn = int(clamp((t - 121.0) / .35) * len(s))
        if nn > 0: d.text((X0 + 58 * SSx, row_y(7) * SSx + 4 * SSx), s[:nn], font=fm, fill=GREEN_ + (int(255 * wa),))
    return im.resize((w, h), Image.LANCZOS)


_PREV = {}


def prev_frame(w, h):
    if (w, h) not in _PREV:
        _PREV[(w, h)] = S9.draw(T_IN, w, h)
    return _PREV[(w, h)]


def write_layer(t, w, h):
    """its writing: each line revealed up to the nib; 'me.exist()' underlined; a caret blinking after 'you.'"""
    im = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = wfont()
    for t0, t1, s, x, y in WRITES:
        if t < t0: continue
        k = clamp((t - t0) / (t1 - t0))
        d.text((x, y), s[:max(0, int(round(k * len(s))))], font=f, fill=(255, 255, 255, 255))
    if t >= T_UNDER[0]:
        s = WRITES[2][2]; x, y = WRITES[2][3], WRITES[2][4]
        i = s.index('me.exist()'); x0 = x + f.getlength(s[:i]); x1 = x + f.getlength(s[:i + len('me.exist()')])
        k = clamp((t - T_UNDER[0]) / (T_UNDER[1] - T_UNDER[0]))
        d.line([(x0, y + 54), (x0 + (x1 - x0) * k, y + 52)], fill=(255, 255, 255, 255), width=3)
    if WRITES[3][1] <= t < NEAR and (t * 3) % 1 < .55:
        s = WRITES[3][2]; x, y = WRITES[3][3], WRITES[3][4]
        d.text((x + f.getlength(s) + 4, y), '_', font=f, fill=(255, 255, 255, 200))
    return im.resize((w, h), Image.LANCZOS) if (w, h) != (1920, 1080) else im


POEM = ['Heart, we will forget him,', 'You and I, tonight!', 'You may forget the warmth he gave,', 'I will forget the light.',
        'When you have done pray tell me,', 'That I my thoughts may dim;', "Haste! lest while you're lagging", 'I may remember him!']
_tex = {}
_HEART = {}
_LINES = []
HEART_K = 16 + 8                                       # a 'Heart, …' line (k % 8 == 0) that is not struck out


def _pages():
    if _tex: return _tex
    W, H = 1400, 2600
    under = Image.new('RGBA', (W, H), (0, 0, 0, 0)); du = ImageDraw.Draw(under)
    over = Image.new('RGBA', (W, H), (0, 0, 0, 0)); do = ImageDraw.Draw(over)
    fh = ImageFont.truetype('C:/Windows/Fonts/Inkfree.ttf', 58)
    fc = ImageFont.truetype('C:/Windows/Fonts/palai.ttf', 46)
    y = 60; k = 0
    word = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dw = ImageDraw.Draw(word)
    while y < H - 80:                                          # the poem, drafted again and again, some lines struck out
        ln = POEM[k % len(POEM)]
        if k == HEART_K:                                       # this "Heart" is the one that will be left on the page
            hw = du.textlength('Heart', font=fh)
            x0 = W / 2 - hw / 2
            du.text((x0, y), ln, font=fh, fill=(255, 255, 255, 255))
            dw.text((x0, y), 'Heart', font=fh, fill=(255, 255, 255, 255))
            bb = du.textbbox((x0, y), 'Heart', font=fh)
            _HEART['cy'] = (bb[1] + bb[3]) / 2
            _HEART['x'] = (bb[0] / W, bb[2] / W)
            _LINES.append(((bb[1] + bb[3]) / 2 / H, x0 / W, (x0 + du.textlength(ln, font=fh)) / W))
            y += 86; k += 1; continue
        du.text((120 + (k * 37) % 90, y), ln, font=fh, fill=(255, 255, 255, 255))
        bb = du.textbbox((120 + (k * 37) % 90, y), ln, font=fh)
        _LINES.append(((bb[1] + bb[3]) / 2 / H, bb[0] / W, bb[2] / W))
        if k % 3 == 1:
            wdt = du.textlength(ln, font=fh)
            du.line((110 + (k * 37) % 90, y + 36, 130 + (k * 37) % 90 + wdt, y + 30), fill=(255, 255, 255, 255), width=5)
        y += 86; k += 1
    y = 30
    n = 7
    while y < H - 60:                                          # Archimedes' squeeze on pi, written over it
        lo = n * math.sin(math.pi / n); hi = n * math.tan(math.pi / n)
        do.text((260, y), f'n = {n:<6}  {lo:.7f}  <  π  <  {hi:.7f}', font=fc, fill=(255, 255, 255, 255))
        y += 64; n *= 2
        if n > 7 * 2 ** 16: n = 7
    _tex.update(u_under=under, u_over=over, u_word=word)
    return _tex


NOTE_X0, NOTE_X1 = 1150 / 1920, 1560 / 1920


def _note():
    if 'u_note' not in _tex:
        im = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
        f = ImageFont.truetype('C:/Windows/Fonts/segoepr.ttf', 40)
        lay = Image.new('RGBA', (520, 90), (0, 0, 0, 0))
        ImageDraw.Draw(lay).text((10, 10), 'non necesse', font=f, fill=(255, 255, 255, 255))
        lay = lay.rotate(-19.3, resample=Image.BICUBIC, expand=True)            # along the cut
        im.alpha_composite(lay, (1150, 795))
        _tex['u_note'] = im
    return _tex['u_note']


def textures(t, w, h):
    tx = {**_pages(), 'u_note': _note(), 'u_write': write_layer(t, w, h), 'u_astro': astro_layer(t, w, h)}
    tx['u_prev'] = prev_frame(w, h)
    return tx


def _scroll_end():
    t = END; sc = 0.
    for k in range(200):
        tt = 118.3 + (t - 118.3) * (k + .5) / 200
        v = .09 * (1 - ease((tt - TRY) / (NEAR - TRY - .6)))
        sc += v * (t - 118.3) / 200
    return sc


_pages()
# tuv.y = fract(p.y*.31 + .5 + scroll) = 1 - cy/H  at p.y = -.4 once the pages have stopped
SCROLL0 = ((1 - _HEART['cy'] / 2600) - (-.4 * .31 + .5) - _scroll_end()) % 1.0

LINES = (_LINES + [(9., 0., 0.)] * 40)[:40]
NL = min(len(_LINES), 40)
HX = _HEART['x']
