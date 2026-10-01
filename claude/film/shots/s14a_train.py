"""s14a · 2:42.632–2:46.3  the census cards go by train (standalone sketch; replaces the factory of s14's first shot).
Flat 2D design: grey paper, black shapes, red only for the hole.  The depth is a drawing trick — every car is a flat
side panel whose two ends are placed by a perspective map of a winding track; nothing is modelled.

If I can            the red glow of the last shot is the light behind a card; lit: VOLKSZÄHLUNG 1939.
give them all the   it sits in a rack in the side of a wagon; the rack fills; pulling back and up: the wagon is the last
                    of a long train winding across the plain to the horizon, a locomotive's black smoke over it all.
EXECUTION           every card in every wagon: the same hole, red — a red dotted thread down the whole train.
                    The smoke bursts; the train starts.
Then I can          it runs off into the distance."""
import math
import importlib.util
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

_P = Path(__file__).resolve().parent / 's14_cards.py'
_spec = importlib.util.spec_from_file_location('s14src_a', _P); S14 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(S14)

T0, T1, T2, T3 = S14.T0, S14.T1, S14.T2, S14.T3
CW, CH = S14.CW, S14.CH

# ---- the track: a heading function integrated on the ground plane (x across, z into the picture)
LC, GAP, HB = 1.5, .1, .68          # car length, gap, body height (at depth 1)
Y0, YH = -.507, 2.35                 # the rails at depth 1; the horizon
X0 = .915                            # rear of the last car: puts our card at (0, 0)
NC, NT, NP = 44, 120, 34             # cars, track points, poles
WC = .5                              # car width (seen on the ends)


def _sm(a, b, x):
    c = max(0., min(1., (x - a) / (b - a))); return c * c * (3 - 2 * c)


def phi(s):
    if s < 1.8: return 0.
    u, n, L = s - 1.8, 0, 10.
    while u > L and n < 12: u -= L; n += 1; L *= 1.55
    k = n + _sm(.62, 1., u / L)
    lo = math.radians(7)
    return (math.pi / 2 - (math.pi / 2 - lo) * math.cos(math.pi * k)) * (_sm(0, 1.2, s - 1.8) if n == 0 else 1.)


def _path(s0=-6., s1=120., ds=.01):
    S = np.arange(s0, s1, ds)
    F = np.array([phi(s) for s in S])
    dx, dz = -np.cos(F) * ds, np.sin(F) * ds
    i0 = int(round(-s0 / ds))
    X = np.cumsum(dx); Z = np.cumsum(dz)
    X += X0 - X[i0]; Z += 1. - Z[i0]
    return S, X, Z, F


PS, PX, PZ, PF = _path()


def at(s):
    return (float(np.interp(s, PS, PX)), float(np.interp(s, PS, PZ)), float(np.interp(s, PS, PF)))


def proj(x, z):
    g = 1. / z
    return (x * g, YH - (YH - Y0) * g, g)


def _v(p): return 'vec2(%.7f,%.7f)' % tuple(p)


# ---- stencilled numbers on the wagons
def _labels():
    W, H = 1024, 96
    img = Image.new('RGBA', (W, H * NC), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    f = ImageFont.truetype(S14.FONTB, 70)
    for i in range(NC):
        n = NC - i                                       # counted from the locomotive
        txt = 'Nr %04d   VZ 39' % (n * 7 + 3) if i < NC - 1 else ''
        d.text((6, i * H + H / 2), txt, font=f, fill=(255, 255, 255, 255), anchor='lm')
    return img


LABELS = _labels()

# the header of s14 (uniforms, noise, the card) + the train
_HEAD = S14.SRC.split('// ---- the factory')[0]
SRC = _HEAD + r'''
uniform vec4 u_A[%NC%], u_B[%NC%];
uniform vec3 u_trk[%NT%], u_pole[%NP%];
uniform vec3 u_chim; uniform float u_m, u_t2;
uniform float u_load0;
uniform sampler2D u_lab;
const int NC=%NC%, NT=%NT%, NP=%NP%;
const float LC=%LC%, HB=%HB%, YH=%YH%, Y0=%Y0%;
const vec3 SKY=vec3(.4,.37,.33), GROUND=vec3(.22,.205,.185), END=vec3(.11,.1,.095);
float PX0;

// when a slot of the last wagon gets its card (the rest of the train is loaded already)
float loadT(float col, float row){
  if(abs(col-1.)<.1&&abs(row-1.)<.1) return -1.;              // ours
  float k=h12(vec2(col*3.1+1.,row*7.7+2.));
  return u_load0+.06+.5*k;
}

vec3 wagon(vec2 p, vec3 c, float lx, float ly, float s, int i){
  if(ly<-.01) return c;
  float PL=PX0/s;
  for(int w=0;w<4;w++){
    float wx=w==0?.2:(w==1?.46:(w==2?LC-.46:LC-.2));
    float d=length(vec2(lx-wx,ly-.075))-.075;
    c=mix(c,INK,fill(d*s));
    c=mix(c,SKY*.6,fill((length(vec2(lx-wx,ly-.075))-.018)*s));
  }
  if(lx>.05&&lx<LC-.05&&ly>.1&&ly<.15) c=INK;
  if(lx>-.035&&lx<LC+.035&&ly>.82&&ly<.865) c=INK;               // the roof
  if(lx<0.||lx>LC||ly<.14||ly>.82) return c;
  c=INK;
  // the stencil
  if(ly>.765&&ly<.812&&lx>.09&&lx<.6){
    vec2 luv=vec2((lx-.09)/.51,(float(i)+1.-(ly-.765)/.047)/float(NC));
    c=mix(c,vec3(.72,.7,.66),texture(u_lab,vec2(luv.x,1.-luv.y)).a*.85);
  }
  // the rack: 4 x 3 cards
  float col=floor((lx-.09)/.33), row=floor((ly-.14-HB*.18)/(HB*.24));
  if(col<0.||col>3.||row<0.||row>2.) return c;
  vec2 cc=vec2(.09+.33*(col+.5),.14+HB*(.18+.24*(row+.5)));
  float dy=0.;
  if(i==0){
    float tl=loadT(col,row);
    if(u_time<tl) { c=mix(c,vec3(.02),fill(sdBox(vec2(lx,ly),cc,vec2(CW*.52,CH*.56))*s)); return c; }
    dy=.3*(1.-smoothstep(0.,.14,u_time-tl));
  }
  vec2 l=vec2(lx,ly)-cc-vec2(0.,dy);
  c=mix(c,vec3(.02),fill(sdBox(vec2(lx,ly),cc,vec2(CW*.52,CH*.56))*s));
  if(ly-dy>.82) return c;
  float save=PXw; PXw=PL;
  vec4 cd=card(l/vec2(CW,CH)+.5,vec2(float(i)*10.+col,row),0.,0.);
  PXw=save;
  c=mix(c,cd.rgb,cd.a);
  if(abs(l.x)<CW*.5&&abs(l.y)<CH*.5&&u_mark>0.){                // the hole: at least a clear red dot at any distance
    float dd=length(l-HOLEC)*s;
    c=mix(c,BLOOD*(1.3+2.*u_flash),fill(dd-max(.006*s,PX0*3.2)));
    c+=BLOOD*(.5+3.*u_flash)*exp(-dd/(PX0*2.2));
  }
  return c;
}

vec3 loco(vec2 p, vec3 c, float lf, float ly, float s){
  if(ly<-.01) return c;
  float d=1e3;
  d=min(d,sdRBox(vec2(lf,ly)-vec2(.66,.44),vec2(.54,.2),.12));      // boiler
  d=min(d,sdBox(vec2(lf,ly),vec2(.21,.68),vec2(.065,.16)));           // chimney
  d=min(d,sdBox(vec2(lf,ly),vec2(.21,.85),vec2(.1,.025)));
  d=min(d,length(vec2(lf,ly)-vec2(.66,.66))-.075);                    // dome
  d=min(d,sdBox(vec2(lf,ly),vec2(1.33,.56),vec2(.19,.36)));           // cab
  d=min(d,sdBox(vec2(lf,ly),vec2(1.33,.93),vec2(.24,.025)));
  d=min(d,sdBox(vec2(lf,ly),vec2(.72,.2),vec2(.76,.04)));             // frame
  d=min(d,sdBox(vec2(lf,ly),vec2(.0,.2),vec2(.05,.06)));              // buffer beam
  for(int w=0;w<3;w++) d=min(d,length(vec2(lf,ly)-vec2(.52+.31*float(w),.13))-.13);
  d=min(d,length(vec2(lf,ly)-vec2(.2,.07))-.07);
  c=mix(c,INK,fill(d*s));
  c=mix(c,SKY*.8,fill(sdBox(vec2(lf,ly),vec2(1.33,.72),vec2(.1,.09))*s));   // cab window
  float a=u_m/.13;                                                            // the coupling rod
  vec2 o=.065*vec2(cos(a),sin(a));
  c=mix(c,SKY*.6,fill(sdCap(vec2(lf,ly),vec2(.52,.13)+o,vec2(1.14,.13)+o,.012)*s));
  return c;
}

vec3 car(vec2 p, vec3 c, int i){
  vec4 A=u_A[i], B=u_B[i];
  float sm=max(A.z,B.z);
  float x0=min(A.x,B.x)-abs(A.w)-.1*sm, x1=max(A.x,B.x)+abs(A.w)+.1*sm;
  float y0=min(A.y,B.y)-.03*sm, y1=max(A.y,B.y)+1.*sm;
  if(p.x<x0||p.x>x1||p.y<y0||p.y>y1) return c;
  bool isLoco=i==NC-1;
  vec4 N=B.w>.5?A:B;
  if(abs(A.w)>1e-5){                                              // the near end, seen when the track turns away
    float e0=min(N.x,N.x+A.w), e1=max(N.x,N.x+A.w);
    float ly=(p.y-N.y)/N.z;
    if(p.x>e0&&p.x<e1&&ly>.1&&ly<(isLoco?.95:.865)){
      float ex=(p.x-e0)/(e1-e0);
      c=isLoco?INK:END;
      if(!isLoco){
        float br=min(abs(ex*.73-(ly-.14)),abs((1.-ex)*.73-(ly-.14)));
        c=mix(c,INK,fill((br-.02)*N.z));
        c=mix(c,INK,fill((min(ex,1.-ex)*(e1-e0)-.012*N.z)));
      }
    }
  }
  float dx=B.x-A.x;
  if(abs(dx)>1e-6){
    float u=(p.x-A.x)/dx;
    float over=.04*LC/max(abs(dx)/sm,1e-3);
    if(u>-over&&u<1.+over){
      float s=mix(A.z,B.z,clamp(u,0.,1.)), by=mix(A.y,B.y,u);
      float ly=(p.y-by)/s;
      float lx=dx<0.?(1.-u)*LC:u*LC;
      float lf=(1.-u)*LC;
      c=isLoco?loco(p,c,lf,ly,s):wagon(p,c,lx,ly,s,i);
    }
  }
  return c;
}

float smoke(vec2 p){
  float m=0.;
  float P=.2, ph=u_time/P;
  for(int k=0;k<26;k++){
    float id=floor(ph)-float(k), age=(float(k)+fract(ph))*P;
    vec2 cp=u_chim.xy+vec2(.2*age+.04*sin(id*1.7)+.035*age*age,.44*age-.025*age*age+.04*sin(id*2.3));
    float tb=u_time-age, boost=exp(-(tb-u_t2-.12)*(tb-u_t2-.12)/.035)*step(u_t2,tb+.1);   // EXECUTION: a violent puff
    cp+=vec2(.25,1.1)*boost*age;
    float r=(u_chim.z*.1+.075*age+.035*h12(vec2(id,4.))*age)*(1.+3.*boost)*(1.-smoothstep(3.6,5.2,age));
    float d=length(p-cp)-r*(1.+.12*(vn((p-cp)*9./(.3+age)+id)-.5));
    m=max(m,fill(d));
  }
  return m;
}

void main(){
  vec2 uv=(gl_FragCoord.xy-.5*u_res)/u_res.y;
  PXw=1./(u_res.y*u_zoom); PX0=PXw;
  vec2 p=u_ctr+(uv+u_shake)/u_zoom;
  float lit=mix(.03,1.,u_lit);
  vec3 col;
  // sky, the plain (furrows at equal depth), the horizon
  if(p.y>YH) col=SKY*(.97+.05*fbm(p*1.5));
  else {
    float Z=(YH-Y0)/max(YH-p.y,1e-4);
    float f=Z*1.3, w=fwidth(f);
    float g=min(fract(f),1.-fract(f));
    col=GROUND*(.97+.05*fbm(p*2.));
    col*=1.-.28*(1.-smoothstep(0.,w*1.4,g))*(1.-smoothstep(.15,.45,w));
  }
  col=mix(col,INK,fill(abs(p.y-YH)-.004));
  col*=lit;
  // the track bed and the rail
  for(int k=0;k<NT-1;k++){
    vec3 a=u_trk[k], b=u_trk[k+1];
    float r=.09*max(a.z,b.z);
    if(p.x<min(a.x,b.x)-r||p.x>max(a.x,b.x)+r||p.y<min(a.y,b.y)-r||p.y>max(a.y,b.y)+r) continue;
    float sb=sdCap(p,a.xy-vec2(0.,.02*a.z),b.xy-vec2(0.,.02*b.z),.06*mix(a.z,b.z,.5));
    col=mix(col,vec3(.13,.12,.11)*lit,fill(sb));
    col=mix(col,INK,fill(sdCap(p,a.xy,b.xy,max(.012*mix(a.z,b.z,.5),PXw*.6))));
  }
  // telegraph poles and the wire
  for(int k=0;k<NP;k++){
    vec3 a=u_pole[k];
    float h=1.2*a.z, wd=max(.014*a.z,PXw*.6);
    col=mix(col,INK,fill(sdBox(p,vec2(a.x,a.y+h*.5),vec2(wd,h*.5))));
    col=mix(col,INK,fill(sdBox(p,vec2(a.x,a.y+h*.93),vec2(.11*a.z,wd*.8))));
    if(k<NP-1){
      vec3 b=u_pole[k+1];
      for(int q=-1;q<=1;q+=2){
        vec2 pa=a.xy+vec2(float(q)*.08*a.z,h*.93), pb=b.xy+vec2(float(q)*.08*b.z,1.2*b.z*.93);
        float t=clamp((p.x-pa.x)/(pb.x-pa.x+1e-6),0.,1.);
        vec2 on=mix(pa,pb,t)-vec2(0.,.06*mix(a.z,b.z,t)*4.*t*(1.-t));
        if(p.x>min(pa.x,pb.x)&&p.x<max(pa.x,pb.x)) col=mix(col,INK,fill(abs(p.y-on.y)-max(.0035*mix(a.z,b.z,t),PXw*.35)));
      }
    }
  }
  // the train, far to near
  for(int i=NC-1;i>=0;i--) col=car(p,col,i);
  col=mix(col,INK,smoke(p));
  col+=vec3(1.,.9,.85)*u_flash*.06;
  vec4 ui=texture(u_ui,gl_FragCoord.xy/u_res);
  col=mix(col,ui.rgb,ui.a);
  fragColor=vec4(col*u_weight,1.);
}
'''
for k, v in {'%NC%': str(NC), '%NT%': str(NT), '%NP%': str(NP), '%LC%': '%.4f' % LC, '%HB%': '%.4f' % HB,
             '%YH%': '%.4f' % YH, '%Y0%': '(%.4f)' % Y0}.items():
    SRC = SRC.replace(k, v)
POST = dict(u_bloom=.3, u_ca=.004)

clamp, ease, outc, lerp, lerp2, lz = S14.clamp, S14.ease, S14.outc, S14.lerp, S14.lerp2, S14.lz


def travel(t):
    """how far the train has run: it starts on EXECUTION, heavily; after 'Then I can' it is rushed off"""
    a = t - (T2 + .25)
    if a <= 0: return 0.
    return .45 * a * a + (5. * (t - T3) ** 2 if t > T3 else 0.)


def layout(m):
    A, B = [], []
    chim = (0., 0., 0.)
    for i in range(NC):
        sr = i * (LC + GAP) + m; sf = sr + LC
        xr, zr, fr = at(sr); xf, zf, ff = at(sf)
        pa, pb = proj(xr, zr), proj(xf, zf)
        nearA = pa[2] >= pb[2]
        pn, pfar, fn = (pa, pb, fr) if nearA else (pb, pa, ff)
        ew = WC * pn[2] * abs(math.sin(fn)) * (1. if pn[0] >= pfar[0] else -1.)
        A.append((pa[0], pa[1], pa[2], ew)); B.append((pb[0], pb[1], pb[2], 1. if nearA else 0.))
        if i == NC - 1:
            u = 1 - .21 / LC
            chim = (lerp(pa[0], pb[0], u), lerp(pa[1], pb[1], u) + .87 * lerp(pa[2], pb[2], u), lerp(pa[2], pb[2], u))
    return A, B, chim


def _static():
    s_end = (NC - 1) * (LC + GAP) + LC + 12.
    trk = []
    for k in range(NT):                                   # denser near, sparser far
        s = -5. + (s_end + 5.) * (k / (NT - 1)) ** 1.25
        x, z, f = at(s); trk.append(proj(x, z))
    poles = []
    for k in range(NP):
        s = -1.2 + k * 2.2
        x, z, f = at(s)
        x += math.sin(f) * .75; z += math.cos(f) * .75       # on the far side of the line
        poles.append(proj(x, z))
    return trk, poles


TRK, POLES = _static()


def camera(t):
    if t < T1: return lz(14., 5.4, outc((t - T0) / .6)), (0., 0.)
    end = (-1.2, 1.22)
    if t < T2:
        k = ease((t - T1) / (T2 - .05 - T1))
        return lz(5.4, .205, k), (lerp(0., end[0], k), lerp(0., end[1], k * k))
    return .205 * (1 - .025 * ease((t - T2) / (T3 - T2 + .5))), end


def params(t):
    z, ctr = camera(t)
    sh = .008 * math.exp(-(t - T2) * 20) if 0 <= t - T2 < .3 else 0.
    m = travel(t)
    A, B, chim = layout(m)
    return dict(u_zoom=z, u_ctr=ctr, u_shake=(sh * math.sin(t * 97), sh * math.cos(t * 83)),
                u_lit=ease((t - T0 - .3) / .35), u_backRed=1. - ease((t - T0 - .1) / .5),
                u_mark=1. if t >= T2 else 0., u_flash=math.exp(-(t - T2) * 14) if t >= T2 else 0.,
                u_A=A, u_B=B, u_trk=TRK, u_pole=POLES, u_chim=chim, u_m=m,
                u_t2=T2, u_load0=T1 - .05)


_UI = {}


def textures(t, w, h):
    s = h / 1080
    txt = S14.typed('17. V. 1939', T0 + .7, t) if t >= T0 + .7 else ''
    key = (w, h, txt)
    if key not in _UI:
        _UI.clear()
        img = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
        if txt: d.text((70 * s, 60 * s), txt, font=ImageFont.truetype(S14.FONT, int(30 * s)), fill=(226, 222, 212, 255))
        _UI[key] = img
    return {'u_face': S14.FACE, 'u_ui': _UI[key], 'u_lab': LABELS}
