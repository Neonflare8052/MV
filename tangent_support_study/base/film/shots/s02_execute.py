"""s02 · 0:16–0:29.709  interlude, world.execute(me);
One fixed set-up turning slowly round the centre. On the left a translucent terminal: it opens the song (title, artist),
then analyses it live, loading one module per bar. Each module adds a new set of points to the same square
(same area, denser each time) and those points visualise their instrument:
envelope · kick · bass · snare · hats · spectrum. Then: new file found: LOVE — open — processing … and it lags."""
import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve()
FEAT = np.load(HERE.parents[2] / 'audio' / 'feat_14_31.npz')
FT0 = float(FEAT['t'][0])

SRC = r'''#version 330
uniform vec2 u_res; uniform float u_time, u_weight;
uniform vec3 u_cam, u_look; uniform float u_fov, u_focus, u_aper;
uniform float u_tau;                 // analysis clock (lags and stops at the end)
uniform float u_lvA[6];              // module k loaded (points of level k visible) 0..1
uniform float u_pop[6];              // flash when a module loads
uniform float u_dim, u_newest, u_flat;   // u_flat: the field settles flat and even (hand-off to s03)
uniform sampler2D u_feat, u_ui;
out vec4 fragColor;
#define PI 3.14159265
const float G=.04, HS=2.;
const float FT0=%FT0%;
const vec3 WHITE=vec3(.92,.91,.88), COP=vec3(1.,.58,.28), COOL=vec3(.75,.85,1.);
float PXW;
float h12(vec2 p){ vec3 p3=fract(vec3(p.xyx)*.1031); p3+=dot(p3,p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }
float blurAt(float t){ return u_aper*abs(t-u_focus)/max(u_focus,.05); }
// feature rows: 0 loud, 1 kick, 2 bass, 3 snare, 4 hats, 5..52 spectrum (low -> high)
float feat(float row, float tm){
  float f=(tm-FT0)*60.; float i=floor(f);
  int W=textureSize(u_feat,0).x, H=textureSize(u_feat,0).y;
  int x0=int(clamp(i,0.,float(W-1))), x1=int(clamp(i+1.,0.,float(W-1)));
  int y=H-1-int(row);
  return mix(texelFetch(u_feat,ivec2(x0,y),0).r,texelFetch(u_feat,ivec2(x1,y),0).r,fract(f));
}
float level(vec2 id){ return clamp(6.+floor(log2(max(h12(id*1.37+.5),1e-4))),0.,5.); }

// a point of the field: position, colour*energy
vec3 pointOf(vec2 id, out vec3 c){
  vec2 q=(id+.5)*G;
  float L=level(id);
  float a=L<.5?u_lvA[0]:(L<1.5?u_lvA[1]:(L<2.5?u_lvA[2]:(L<3.5?u_lvA[3]:(L<4.5?u_lvA[4]:u_lvA[5]))));
  float pop=L<.5?u_pop[0]:(L<1.5?u_pop[1]:(L<2.5?u_pop[2]:(L<3.5?u_pop[3]:(L<4.5?u_pop[4]:u_pop[5]))));
  c=vec3(0.);
  if(a<=0.) return vec3(q.x,-9.,q.y);
  float hp=h12(id+3.1);
  float y=0., e=.45+.4*hp; vec3 col=WHITE;
  float sq=max(abs(q.x),abs(q.y));
  if(L<.5){                                   // envelope: the whole song breathing
    float v=feat(0.,u_tau-sq*.12);
    y=.07*v; e=.5+1.2*v;
  } else if(L<1.5){                           // kick: square fronts thrown out from the centre
    float v=feat(1.,u_tau-sq*.22);
    y=.42*v*v; e=.45+2.2*v; col=mix(WHITE,vec3(1.,.9,.8),v);
  } else if(L<2.5){                           // bass: a swell rolling across
    float v=feat(2.,u_tau-(q.x+HS)*.28);
    y=.26*v; e=.35+1.1*v; col=mix(WHITE,COP,.55);
  } else if(L<3.5){                           // snare: a random handful flares on every hit
    float v=feat(3.,u_tau);
    float pick=step(1.-.55*min(v,1.),h12(id+floor(u_tau*8.)*.71));
    y=.05*v*pick; e=.3+5.*v*pick;
  } else if(L<4.5){                           // hats: fine glitter
    float v=feat(4.,u_tau);
    float tw=step(.72,h12(id+floor(u_tau*30.)*.37));
    e=.25+4.*v*tw; col=COOL;
  } else {                                    // spectrum: time runs toward the viewer's right, frequency into depth
    float band=clamp((q.y+HS)/(2.*HS),0.,1.)*47.;
    float tm=u_tau-(HS-q.x)*.7;
    float v=mix(feat(5.+floor(band),tm),feat(6.+min(floor(band),46.),tm),fract(band));
    y=.85*pow(v,1.5); e=.15+2.6*v*v; col=mix(vec3(.55,.5,.45),COP,smoothstep(.3,.8,v));
  }
  float focus=L>u_newest-.5?1.35:(u_newest>4.5?.3:.5);
  c=mix(col*e*a*(1.+3.*pop)*focus,WHITE*.55*a,u_flat);
  return vec3(q.x,(y+(1.-a)*.4)*(1.-u_flat),q.y);
}

vec3 field(vec3 ro, vec3 rd){
  vec3 bmin=vec3(-HS,-.05,-HS), bmax=vec3(HS,.9,HS);
  vec3 ird=1./rd;
  vec3 ta=(bmin-ro)*ird, tb=(bmax-ro)*ird, tn=min(ta,tb), tf=max(ta,tb);
  float t0=max(max(tn.x,tn.y),max(tn.z,0.)), t1=min(min(tf.x,tf.y),tf.z);
  if(t0>=t1) return vec3(0.);
  vec2 dx=rd.xz; dx=vec2(abs(dx.x)<1e-6?1e-6:dx.x,abs(dx.y)<1e-6?1e-6:dx.y);
  vec3 p=ro+rd*(t0+1e-4);
  vec2 cell=floor(p.xz/G), st=sign(dx), dl=abs(G/dx);
  vec2 nx=((cell+max(st,0.))*G-ro.xz)/dx;
  float tc=t0;
  vec3 acc=vec3(0.);
  for(int i=0;i<260;i++){
    if(tc>t1) break;
    if(abs(cell.x+.5)*G<HS&&abs(cell.y+.5)*G<HS){
      vec3 c; vec3 pos=pointOf(cell,c);
      float tt=dot(pos-ro,rd);
      if(tt>0.&&dot(c,c)>0.){
        float d=length(ro+rd*tt-pos);
        float r=.0048, R=r+blurAt(tt)+PXW*tt*.8;
        acc+=c*(r*r)/(R*R)*exp(-d*d/(R*R)*2.)*exp(-tt*.08);
        // a thin stem under raised points
        if(pos.y>.02){
          vec3 a=vec3(pos.x,0.,pos.z), ba=pos-a, w=ro-a;
          float bb=dot(ba,ba), rb=dot(rd,ba), rw=dot(rd,w), bw=dot(ba,w);
          float s=clamp((bw-rw*rb)/max(bb-rb*rb,1e-9),0.,1.);
          float t=s*rb-rw;
          float dd=length(ro+rd*t-a-ba*s);
          float rs=.0009, Rs=rs+blurAt(t)+PXW*t*.8;
          acc+=c*.18*(rs/Rs)*exp(-dd*dd/(Rs*Rs)*2.)*s*exp(-t*.08);
        }
      }
    }
    if(nx.x<nx.y){ tc=nx.x; nx.x+=dl.x; cell.x+=st.x; } else { tc=nx.y; nx.y+=dl.y; cell.y+=st.y; }
  }
  return acc;
}
// the square's outline and a faint base grid, so the area reads as fixed
vec3 base(vec3 ro, vec3 rd){
  float t=-ro.y/rd.y; if(t<=0.) return vec3(0.);
  vec3 p=ro+rd*t;
  float fp=PXW*t/max(abs(rd.y),.05)*.7+blurAt(t);
  float m=max(abs(p.x),abs(p.z));
  float e=abs(m-HS-.04);
  float edge=(.0012/(.0012+fp))*(1.-smoothstep(0.,.0012+fp,e));
  vec2 g=abs(fract(p.xz/.4+.5)-.5)*.4;
  float grid=(.0006/(.0006+fp))*(1.-smoothstep(0.,.0006+fp,min(g.x,g.y)))*step(m,HS);
  float along=abs(p.x)>abs(p.z)?p.z:p.x;
  float tk=step(abs(fract(along/.1)-.5),.06)*step(abs(m-HS-.07),.025);
  return vec3(.5,.5,.52)*(edge*.9+grid*.25+tk*.35)*exp(-t*.08);
}
void main(){
  vec2 uv=(gl_FragCoord.xy-.5*u_res)/u_res.y;
  vec3 ro=u_cam, fw=normalize(u_look-ro), rt=normalize(cross(fw,vec3(0,1,0))), up=cross(rt,fw);
  float tf=tan(u_fov*.5);
  vec3 rd=normalize(fw+(uv.x*rt+uv.y*up)*2.*tf);
  PXW=2.*tf/u_res.y;
  vec3 col=vec3(.004,.004,.005)+base(ro,rd)*(1.-u_flat)+field(ro,rd);
  col*=u_dim;
  vec4 ui=texture(u_ui,gl_FragCoord.xy/u_res);
  col=col*(1.-ui.a*.55)+ui.rgb*ui.a;
  fragColor=vec4(col*u_weight,1.);
}
'''.replace('%FT0%', f'{FT0:.6f}')
POST = dict(u_bloom=.55, u_ca=.006, u_grain=.04)

T0, T_END = 16.0, 29.709
MOD_T = [17.0, 17.854, 19.708, 21.562, 23.416, 25.270]          # envelope, kick, bass, snare, hats, spectrum
MOD_N = ['envelope', 'kick', 'bass', 'snare', 'hats', 'spectrum']
T_SCAN, T_FOUND, T_OPEN, T_PROC, T_LAG = 27.124, 27.40, 27.78, 28.05, 28.444


def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def outc(x): x = clamp(x); return 1 - (1 - x) ** 3


def tau(t):
    """analysis clock: real time, then from T_LAG it stutters — advances in jerks, each shorter — and stops"""
    if t < T_LAG: return t
    x, k, step = T_LAG, T_LAG, .09
    while True:
        if t < k + step: return x + (t - k)
        x += step
        hold = .12 + .05 * ((k * 7.3) % 1)
        k += step + hold; step *= .55
        if step < .01 or t < k: return x


def params(t):
    a = math.radians(38 + 14 * clamp((t - T0) / (T_END - T0)))       # a slow turn round the centre
    cam = (5.1 * math.sin(a), 2.8, 5.1 * math.cos(a))
    return dict(
        u_cam=cam, u_look=(-.55 * math.cos(a), .05, .55 * math.sin(a)), u_fov=math.radians(40), u_focus=5.6, u_aper=.02,
        u_tau=tau(t),
        u_lvA=[outc((t - m) / .35) for m in MOD_T],
        u_pop=[math.exp(-(t - m) * 5) if t >= m else 0. for m in MOD_T],
        u_newest=float(sum(1 for m in MOD_T if t >= m) - 1) if t < T_SCAN else -1.,
        u_flat=ease((t - 29.05) / .6),
        u_dim=1. - .35 * ease((t - T_LAG) / 1.),
    )


# ---- the terminal ---------------------------------------------------------------------------------------------
FONT = 'C:/Windows/Fonts/CascadiaMono.ttf'
LOG = [
    (16.00, '$ world.execute(me);', 'cmd'),
    (16.18, '> open audio stream', 'sys'),
    (16.36, '  title    world.execute (me) ;', 'meta'),
    (16.50, '  artist   Mili', 'meta'),
    (16.64, '  length   03:31.96   44.1 kHz   stereo', 'dim'),
    (16.78, '  tempo    129.5 bpm   4/4', 'dim'),
    (16.92, '> analyse --live', 'sys'),
] + [(m, f'  + module {n:<10}{"." * 10} ok', 'mod') for m, n in zip(MOD_T, MOD_N)] + [
    (T_SCAN, '> scan complete   6 streams   10000 points', 'sys'),
    (T_FOUND, '! new file found:  LOVE', 'love'),
    (T_OPEN, '> open LOVE', 'cmd'),
]
COLS = dict(cmd=(236, 232, 222), sys=(170, 168, 160), meta=(236, 232, 222), dim=(140, 138, 132), mod=(214, 150, 90),
            love=(240, 200, 150))
BLK = ' ▁▂▃▄▅▆▇█'
_F = {}


def _fonts(s):
    if s not in _F:
        _F[s] = (ImageFont.truetype(FONT, int(21 * s)), ImageFont.truetype(FONT, int(15 * s)))
    return _F[s]


def _fv(row, tm):
    i = int(clamp((tm - FT0) * 60, 0, FEAT['F'].shape[1] - 1))
    return float(FEAT['F'][row, i]) if row < 5 else FEAT['S'][:, i]


_PANEL = {}


def textures(t, w, h):
    s = h / 1080
    f, fs = _fonts(s)
    if (w, h) not in _PANEL:
        pw = int(700 * s)
        panel = Image.new('RGBA', (w, h), (0, 0, 0, 0)); pd = ImageDraw.Draw(panel)
        for x in range(pw):
            pd.line([(x, 0), (x, h)], fill=(6, 6, 7, int(130 * (1 - x / pw) ** 1.5)))
        _PANEL[(w, h)] = panel
    img = _PANEL[(w, h)].copy(); d = ImageDraw.Draw(img)
    x0, y0, lh = 70 * s, 70 * s, 30 * s
    y = y0
    for tt, txt, kind in LOG:
        if t < tt: break
        k = int(clamp((t - tt) / max(.05, len(txt) * .006)) * len(txt))
        a = 215 if kind != 'dim' else 170
        if kind == 'love': a = 255 if (t - tt) > .25 or int((t - tt) * 16) % 2 else 60
        d.text((x0, y), txt[:k], font=f, fill=COLS[kind] + (a,))
        y += lh
    # processing … a progress bar that stutters with the clock, then hangs
    if t >= T_PROC:
        tc = tau(t)
        pr = clamp((tc - T_PROC) / .9) * .47
        n = 22
        bar = '█' * int(pr * n) + '░' * (n - int(pr * n))
        cur = '▌' if (t * 2.4) % 1 < .55 else ' '
        d.text((x0, y), f'  processing  {bar}  {int(pr * 100):3d}%  {cur}', font=f, fill=(236, 232, 222, 225))
        y += lh
    # live data stream under the log: only the loaded modules, newest at the bottom
    loaded = [n for m, n in zip(MOD_T, MOD_N) if t >= m]
    if loaded:
        yb = h - 70 * s
        rows = []
        step = 1 / 12
        k_now = int(tau(t) / step)
        for k in range(k_now - 30, k_now + 1):
            tm = k * step
            if tm < MOD_T[0]: continue
            parts = [f'{tm:7.3f}']
            for row in range(5):
                if tm >= MOD_T[row]: parts.append(f'{MOD_N[row][:4]} {_fv(row, tm):.2f}')
            if tm >= MOD_T[5]:
                sp = _fv(5, tm); parts.append(''.join(BLK[int(clamp(float(v)) * 8)] for v in sp[::3]))
            rows.append('  '.join(parts))
        room = int((yb - y - 30 * s) / (19 * s))
        rows = rows[-room:] if room > 0 else []
        for i, r in enumerate(reversed(rows)):
            a = int(130 * (1 - i / max(len(rows), 1)) + 30)
            d.text((x0, yb - i * 19 * s), r, font=fs, fill=(200, 196, 188, a))
    return {'u_ui': img, 'u_feat': FEATIMG}


_rows = np.concatenate([FEAT['F'], FEAT['S']], 0)
FEATIMG = Image.fromarray((np.clip(_rows, 0, 1) * 255).astype(np.uint8), 'L')
