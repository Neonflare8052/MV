"""s01 · 0:00–0:16  boot. Abstract: light, lines, points, type — no objects.
Switch on the power line: a CRT terminal flashes on · you create a sandbox (PROTECTION) and load the model ·
the camera tilts down, the terminal leaves the frame: inside the sandbox the lattice spreads, OBJECT CREATION raises
six layers · data parameters: flying inside the lattice · INITIALIZATION: the layers are pressed into memory one by
one · the activation tree climbs · candidate words; SIMULATION. Spatial callouts ride with the camera."""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

T_PWR, T_REM, T_PROT, T_LAY, T_BEGIN, T_OBJ = .100, 1.740, 2.920, 3.873, 5.491, 6.380
T_FILL, T_INIT, T_SET, T_LETS, T_SIM = 7.446, 10.091, 11.095, 12.906, 13.891
GLYPHS = Path(__file__).resolve().parents[2] / 'tests' / 't06_teletype' / 'glyphs.png'

SRC = r'''#version 330
uniform vec2 u_res; uniform float u_time, u_weight;
uniform vec3 u_cam, u_look; uniform float u_fov, u_focus, u_aper, u_roll, u_bright;
uniform float u_power;                  // current spreading through the floor network from the centre
uniform float u_crt, u_scrA;            // seconds since the CRT was switched on; terminal visible
uniform float u_box;                    // sandbox drawn 0..1
uniform float u_press[6], u_mem[6], u_memA; // layer pressed into memory 0..1; band written (1 + flash); memory visible
uniform float u_latR;                   // lattice layer 0 revealed radius
uniform float u_rise;                   // upper layers 0..1
uniform float u_param;                  // values being written (labels) 0..1
uniform float u_fillR;                  // writing wave radius
uniform float u_act;                    // activation (layer units)
uniform float u_cand, u_pick, u_dimL;           // candidate words; one chosen
uniform vec3 u_sa[64], u_sb[64]; uniform float u_sk[64]; uniform int u_ns;   // activation tree segments
uniform sampler2D u_glyphs, u_words, u_term, u_ui;
out vec4 fragColor;
#define PI 3.14159265
const float C=.1, RL=2.4, LH=.28, NG=42.;
const float BY0=-.2, BH=.075;          // memory bands (layer 5 on top)
const float BX=2.7, BYL=-.72, BYH=2.1; // sandbox
const float SW=3.556, SH=2., SY=4.5, SZ=0.; // CRT terminal plane
const vec3 WHITE=vec3(.92,.91,.88), COP=vec3(1.,.58,.28);
vec3 RT, UP; float PXW;
float h12(vec2 p){ vec3 p3=fract(vec3(p.xyx)*.1031); p3+=dot(p3,p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }
float h13(vec3 p){ return h12(p.xy+p.z*17.13); }
float blurAt(float t){ return u_aper*abs(t-u_focus)/max(u_focus,.05); }
// a glowing point of radius r seen at depth t, ray distance d
float spot(float d, float t, float r){
  float R=r+blurAt(t)+PXW*t*.8;
  return (r*r)/(R*R)*exp(-d*d/(R*R)*2.)*exp(-t*.16);
}
// an antialiased, defocused line of half-width w at distance d on a plane seen at depth t with footprint fp
float lineM(float d, float w, float t, float fp){
  float b=blurAt(t)+fp;
  return w/(w+b)*(1.-smoothstep(0.,w+b,d));
}
float glyph(float g, vec2 f, float lod){
  if(g<.5||f.x<0.||f.x>1.||f.y<0.||f.y>1.) return 0.;
  return textureLod(u_glyphs,vec2((g+clamp(f.x,.02,.98))/NG,clamp(f.y,.02,.98)),lod).r;
}
float bandY(float k){ return BY0-BH*(5.-k); }
float layerY(float k){ return mix(k*LH*u_rise,bandY(k),u_press[int(k+.5)]); }

// ---- the network printed on a layer plane --------------------------------------------------------
vec3 plane(vec3 ro, vec3 rd, float k, float tmax){
  float y=layerY(k);
  if(k>.5&&u_rise<=0.) return vec3(0.);
  float t=(y-ro.y)/rd.y;
  if(t<=0.||t>tmax) return vec3(0.);
  vec3 p=ro+rd*t;
  float fp=PXW*t/max(abs(rd.y),.03)*.6;
  float graze=smoothstep(.015,.12,abs(rd.y))*exp(-t*.12);
  vec2 g=p.xz/C-.5;
  float r=length(p.xz);
  float inside=k<.5?1.:step(max(abs(p.x),abs(p.z)),RL);
  if(inside<=0.) return vec3(0.);
  // segments between neighbouring nodes
  vec2 id=floor(g);
  float jz=floor(g.y+.5), jx=floor(g.x+.5);
  float dz=abs(g.y-jz)*C, dx=abs(g.x-jx)*C;
  float sx=h13(vec3(id.x,jz,k*7.+1.)), sz=h13(vec3(jx,id.y,k*7.+2.));
  float base=k<.5?.35:.0;
  float mx=lineM(dz,.0009,t,fp)*(base+step(.52,sx)), mz=lineM(dx,.0009,t,fp)*(base+step(.55,sz));
  vec3 col=vec3(0.);
  vec3 dim=vec3(.05,.05,.055)*(k<.5?1.:u_rise);
  col+=dim*(mx+mz);
  // current (layer 0): manhattan front from the source, branches light up in turn
  if(k<.5){
    float md=abs(p.x)+abs(p.z)+.35*h12(floor(g));
    float lit=smoothstep(u_power,u_power-.4,md), head=exp(-pow((md-u_power)*5.,2.));
    float fade=exp(-max(r-2.,0.)*.35);
    col+=COP*((mx*step(.52,sx)+mz*step(.55,sz))*(lit*.8+head*3.))*fade;
    // nodes (vias)
    vec2 nq=(fract(g+.5)-.5)*C;
    col+=COP*lineM(abs(length(nq)-.004),.0008,t,fp)*lit*.6*step(.8,h12(floor(g+.5)+3.))*fade;
  }
  // activation along the connections
  col+=COP*(mx+mz)*exp(-pow((k-u_act)*1.3,2.))*.5*step(.6,h12(floor(g)+k));
  return col*graze*u_dimL;
}

// ---- the lattice of points (2D DDA over columns, six layers per column) --------------------------
vec3 lattice(vec3 ro, vec3 rd, float tmax){
  if(u_latR<0.) return vec3(0.);
  float ytop=5.*LH*max(u_rise,.0)+.05;
  vec3 bmin=vec3(-RL,BYL,-RL), bmax=vec3(RL,ytop,RL);
  vec3 ird=1./rd;
  vec3 ta=(bmin-ro)*ird, tb=(bmax-ro)*ird, tn=min(ta,tb), tf=max(ta,tb);
  float t0=max(max(tn.x,tn.y),max(tn.z,0.)), t1=min(min(tf.x,tf.y),min(tf.z,tmax));
  if(t0>=t1) return vec3(0.);
  vec2 rdx=rd.xz; rdx=vec2(abs(rdx.x)<1e-5?1e-5:rdx.x,abs(rdx.y)<1e-5?1e-5:rdx.y);
  vec3 p=ro+rd*(t0+1e-4);
  vec2 cell=floor(p.xz/C), st=sign(rdx), dl=abs(C/rdx);
  vec2 nx=((cell+max(st,0.))*C-ro.xz)/rdx;
  float tc=t0;
  vec3 acc=vec3(0.);
  int NL=u_rise>0.?6:1;
  for(int i=0;i<140;i++){
    if(tc>t1) break;
    float hp=h12(cell);
    vec2 cx=(cell+.5)*C;
    float rr=length(cx);
    if(hp>.3&&rr<u_latR+.3*h12(cell+5.)){
      for(int k=0;k<6;k++){
        if(k>=NL) break;
        float fk=float(k);
        vec3 pos=vec3(cx.x,layerY(fk),cx.y);
        float tt=dot(pos-ro,rd);
        if(tt<=0.||tt>tmax) continue;
        vec3 v=ro+rd*tt-pos; float d=length(v);
        float hk=h13(vec3(cell,fk));
        float e=.35+.65*hk*hk;
        vec3 c=WHITE;
        if(hk>.9) c=COP;
        // appear on reveal / rise
        float a=k==0?smoothstep(0.,.3,u_latR-rr):smoothstep(fk-1.,fk,u_rise*5.);
        // values being written: flicker; the sheet settles them
        float w=clamp((u_fillR-rr-.3*hk)/.3,0.,1.);
        float writing=w*(1.-w)*4.;
        float settled=step(.5,u_mem[k]);
        float fl=h13(vec3(cell,fk+floor(u_time*14.)*.13));
        e*=mix(1.,.4+1.2*fl,writing*(1.-settled));
        e+=writing*1.2*(1.-settled);
        e+=6.*u_press[k]*(1.-u_press[k]);
        float ac=exp(-pow((fk-u_act)*1.3,2.))*step(.9,h13(vec3(cell,fk+9.)))*.6;
        c=mix(c,COP,ac); e+=ac*2.5;
        acc+=c*e*a*spot(d,tt,.0055);
        // value labels beside the points
        if(u_param>0.&&hk<.45&&d<.06){
          vec2 q=vec2(dot(v,RT),dot(v,UP))-vec2(.012,-.007);
          float gw=.0072, gh=.012;
          if(q.x>0.&&q.x<gw*4.&&q.y>0.&&q.y<gh){
            float ci=floor(q.x/gw);
            float val=h13(vec3(cell,fk+(settled>0.?0.:floor(u_time*(8.+20.*writing))*.11)+ci*3.7));
            float gch=ci==1.?1.:27.+floor(val*10.);
            if(ci==0.) gch=27.;
            float lod=max(log2((PXW*tt+blurAt(tt))/(gw/48.)),0.);
            float m=glyph(gch,vec2(fract(q.x/gw),q.y/gh),lod);
            acc+=mix(vec3(.75,.72,.66),vec3(1.,.8,.55),writing)*m*a*u_param*(.35+writing*.8)*(1.-.5*settled);
          }
        }
      }
    }
    if(nx.x<nx.y){ tc=nx.x; nx.x+=dl.x; cell.x+=st.x; } else { tc=nx.y; nx.y+=dl.y; cell.y+=st.y; }
  }
  return acc*u_dimL;
}

// ---- candidate words on cards hanging in depth ---------------------------------------------------------
vec3 cards(vec3 ro, vec3 rd, float tmax){
  if(u_cand<=0.) return vec3(0.);
  vec3 acc=vec3(0.);
  for(int k=0;k<5;k++){
    float fk=float(k);
    vec3 c=vec3(-.15+(k==1?.6:(k==2?-.5:(k==3?1.1:(k==4?-.9:0.)))), 2.45+(k==1?.34:(k==2?-.3:(k==3?.62:(k==4?-.55:0.)))), .2-.8*fk);
    float t=(c.z-ro.z)/rd.z;
    if(t<=0.||t>tmax) continue;
    vec3 p=ro+rd*t;
    vec2 uv=vec2((p.x-c.x)/2.4+.5,(p.y-c.y)/.2+.5);
    if(uv.x<0.||uv.x>1.||uv.y<0.||uv.y>1.) continue;
    float lod=max(log2((PXW*t+blurAt(t))/(2.4/1536.)),0.);
    vec4 tx=textureLod(u_words,vec2(uv.x,(4.-fk+uv.y)/5.),lod);
    float appear=clamp(u_cand*1.6-fk*.15,0.,1.);
    float keep=k==0?1.+u_pick*.3:1.-u_pick;
    acc+=tx.rgb*tx.a*appear*keep*1.3;
  }
  return acc;
}

// ---- the activation tree: thin lines between the layers, growing upward with the activation --------------
vec3 tree(vec3 ro, vec3 rd, float tmax){
  if(u_act<-.5) return vec3(0.);
  vec3 acc=vec3(0.);
  for(int i=0;i<64;i++){
    if(i>=u_ns) break;
    float k=u_sk[i];
    float f=clamp(u_act-k,0.,1.);
    if(f<=0.) continue;
    vec3 a=u_sa[i], b=u_sb[i];
    a.y*=u_rise; if(k<4.5) b.y*=u_rise;
    vec3 ba=b-a, w=ro-a;
    float bb=dot(ba,ba), rb=dot(rd,ba), rw=dot(rd,w), bw=dot(ba,w);
    float s=clamp((bw-rw*rb)/max(bb-rb*rb,1e-7),0.,f);
    float t=s*rb-rw;
    if(t<=0.||t>tmax) continue;
    float d=length(ro+rd*t-a-ba*s);
    float r=.0016, R=r+blurAt(t)+PXW*t*.7;
    float g=(r/R)*exp(-d*d/(R*R)*2.)*exp(-t*.1);
    float head=exp(-pow((s-f)*8.,2.))*step(f,.999);
    acc+=COP*g*(2.+6.*head);
    vec3 na=a-ro, nb=b-ro;
    float ta=dot(na,rd), tb=dot(nb,rd);
    if(ta>0.) acc+=vec3(1.,.8,.55)*spot(length(na-rd*ta),ta,.009)*2.5;
    if(tb>0.&&f>=.999) acc+=vec3(1.,.8,.55)*spot(length(nb-rd*tb),tb,.009)*2.5;
  }
  return acc;
}

// ---- a glowing line segment (drawn from a toward b up to fraction f) --------------------------------------------
float segGlow(vec3 ro, vec3 rd, vec3 a, vec3 b, float f, float r){
  if(f<=0.) return 0.;
  vec3 ba=b-a, w=ro-a;
  float bb=dot(ba,ba), rb=dot(rd,ba), rw=dot(rd,w), bw=dot(ba,w);
  float s=clamp((bw-rw*rb)/max(bb-rb*rb,1e-7),0.,f);
  float t=s*rb-rw;
  if(t<=0.) return 0.;
  float d=length(ro+rd*t-a-ba*s);
  float R=r+blurAt(t)+PXW*t*.7;
  return (r/R)*exp(-d*d/(R*R)*2.)*exp(-t*.06);
}
// ---- the sandbox: a wire box round everything ---------------------------------------------------------------------
vec3 sandbox(vec3 ro, vec3 rd){
  if(u_box<=0.) return vec3(0.);
  float g=0.;
  for(int i=0;i<4;i++){
    float a=float(i)*PI*.5+PI*.25;
    vec2 c0=vec2(cos(a),sin(a))*BX*1.41421, c1=vec2(cos(a+PI*.5),sin(a+PI*.5))*BX*1.41421;
    g+=segGlow(ro,rd,vec3(c0.x,BYL,c0.y),vec3(c0.x,BYH,c0.y),u_box,.0014);
    g+=segGlow(ro,rd,vec3(c0.x,BYH,c0.y),vec3(c1.x,BYH,c1.y),u_box,.0014);
    g+=segGlow(ro,rd,vec3(c0.x,BYL,c0.y),vec3(c1.x,BYL,c1.y),u_box,.0014);
  }
  return vec3(.8,.82,.86)*g*.9;
}
// ---- memory: six bands under the floor, written as the layers are pressed in --------------------------------------
vec3 memory(vec3 ro, vec3 rd, float tmax){
  if(u_memA<=0.) return vec3(0.);
  vec3 acc=vec3(0.);
  for(int k=0;k<6;k++){
    float y=bandY(float(k));
    float t=(y-ro.y)/rd.y;
    if(t<=0.||t>tmax) continue;
    vec3 p=ro+rd*t;
    if(max(abs(p.x),abs(p.z))>RL) continue;
    float fp=PXW*t/max(abs(rd.y),.02)*.6;
    vec2 g=p.xz/.05;
    vec2 f=abs(fract(g)-.5)*.05;
    float edge=lineM(min(f.x,f.y),.0005,t,fp);
    float bit=step(.45,h13(vec3(floor(g),float(k)*3.)));
    float fill=bit*(1.-smoothstep(.013,.016+fp,max(f.x,f.y)));
    float w=u_mem[k];
    float graze=.0025/max(abs(rd.y),.05);
    acc+=vec3(.35,.36,.4)*edge*.2+mix(WHITE,COP,.5)*(fill*.045+graze*.6)*min(w,1.)*exp(-t*.15)+vec3(1.,.9,.8)*(fill*.12+graze*1.5)*max(w-1.,0.);
  }
  float g=0.;
  vec3 lo=vec3(-RL,bandY(0.)-.04,-RL), hi=vec3(RL,bandY(5.)+.04,RL);
  g+=segGlow(ro,rd,vec3(lo.x,lo.y,hi.z),vec3(hi.x,lo.y,hi.z),1.,.001)+segGlow(ro,rd,vec3(lo.x,hi.y,hi.z),vec3(hi.x,hi.y,hi.z),1.,.001);
  g+=segGlow(ro,rd,vec3(lo.x,lo.y,hi.z),vec3(lo.x,hi.y,hi.z),1.,.001)+segGlow(ro,rd,vec3(hi.x,lo.y,hi.z),vec3(hi.x,hi.y,hi.z),1.,.001);
  g+=segGlow(ro,rd,vec3(hi.x,lo.y,lo.z),vec3(hi.x,lo.y,hi.z),1.,.001)+segGlow(ro,rd,vec3(hi.x,hi.y,lo.z),vec3(hi.x,hi.y,hi.z),1.,.001);
  acc+=vec3(.6,.62,.66)*g*.7;
  return acc*u_memA;
}
// ---- the CRT terminal, a plane hanging above the sandbox ------------------------------------------------------------
vec3 screen(vec3 ro, vec3 rd){
  if(u_scrA<=0.||u_crt<0.) return vec3(0.);
  float t=(SZ-ro.z)/rd.z;
  if(t<=0.) return vec3(0.);
  vec3 p=ro+rd*t;
  vec2 c=vec2(p.x/SW,(p.y-SY)/SH);
  c*=1.+.22*dot(c,c);
  if(abs(c.x)>.5||abs(c.y)>.5) return vec3(0.);
  vec2 u=c+.5;
  float on=u_crt;
  float grow=clamp(on/.06,0.,1.);
  float open=smoothstep(.06,.26,on);
  float hh=mix(.0025,.5,open);
  float band=step(abs(c.x),grow*.5)*(1.-smoothstep(hh-.004,hh,abs(c.y)));
  float flash=(1.-open)*5.+2.2*exp(-max(on-.26,0.)*9.)*step(.26,on);
  float scan=.7+.3*sin(u.y*720.*PI);
  vec3 phos=vec3(1.,.95,.87);
  float txt=texture(u_term,u).r;
  vec3 col=phos*(txt*1.5+.007)*scan*open+phos*flash*.35;
  col*=band*(1.-1.2*dot(c,c))*(1.+.025*sin(u_time*113.));
  return col*u_scrA;
}

void main(){
  vec2 uv=(gl_FragCoord.xy-.5*u_res)/u_res.y;
  uv=mat2(cos(u_roll),-sin(u_roll),sin(u_roll),cos(u_roll))*uv;
  vec3 ro=u_cam;
  vec3 fw=normalize(u_look-ro); RT=normalize(cross(fw,vec3(0,1,0))); UP=cross(RT,fw);
  float tf=tan(u_fov*.5);
  vec3 rd=normalize(fw+(uv.x*RT+uv.y*UP)*2.*tf);
  PXW=2.*tf/u_res.y;
  float tmax=40.;
  vec3 col=vec3(.004,.004,.005);
  col+=plane(ro,rd,0.,tmax);
  for(int k=1;k<6;k++) col+=plane(ro,rd,float(k),tmax);
  col+=lattice(ro,rd,tmax);
  col+=memory(ro,rd,tmax);
  col+=sandbox(ro,rd);
  col+=cards(ro,rd,tmax);
  col+=tree(ro,rd,tmax);
  col+=screen(ro,rd);
  col*=u_bright;
  vec4 ui=texture(u_ui,gl_FragCoord.xy/u_res);
  col=col*(1.-ui.a*.4)+ui.rgb*ui.a;
  fragColor=vec4(col*u_weight,1.);
}
'''

POST = dict(u_bloom=.6, u_ca=.007, u_grain=.04)


def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def outc(x): x = clamp(x); return 1 - (1 - x) ** 3
def inc(x): x = clamp(x); return x ** 3
def mix(a, b, x):
    if isinstance(a, tuple): return tuple(p + (q - p) * x for p, q in zip(a, b))
    return a + (b - a) * x


# cuts: each is a list of keys (time, cam, look, fov, focus, aperture, roll°), eased between keys; hard cuts between lists
CUTS = [
    [(0.00, (0., 4.5, 3.05), (0., 4.5, 0.), 40, 3.05, .004, 0),             # the CRT terminal, head-on, creeping in
     (5.491, (0., 4.5, 2.72), (0., 4.5, 0.), 40, 2.72, .004, 0),
     (7.446, (4.1, 1.9, 2.3), (0., .6, 0.), 40, 4.6, .01, 0)],              # tilt and crane down into the sandbox
    [(7.446, (-1.6, .7, .33), (0., .66, .28), 56, .4, .012, 0),             # inside the lattice; focus racks out at the end
     (9.0, (-.55, .7, .36), (.9, .64, .3), 56, .4, .012, 6),
     (10.091, (.1, .74, .15), (1.2, .6, -.9), 56, 1.7, .012, 12)],
    [(10.091, (0., .55, 6.6), (0., .5, 0.), 23, 6.6, .018, 0),              # INITIALIZATION side-on: pressed into memory
     (11.2, (.4, .6, 6.5), (0., .52, 0.), 23, 6.5, .018, 0),
     (12.906, (3.0, 1.7, 4.6), (0., 1.0, 0.), 30, 5.5, .014, 0)],           # ... then round to see the tree climb
    [(12.906, (1.3, 2.62, 1.7), (-.6, 2.55, -1.6), 44, 1.9, .012, 6),      # candidates in depth, swinging round to SIMULATION
     (13.8, (.1, 2.47, 2.65), (-.15, 2.45, 0.), 38, 2.45, .012, 0),
     (16.0, (-.15, 2.45, 2.4), (-.15, 2.45, 0.), 36, 2.2, .012, 0)],
]


def camera(t):
    keys = [c for c in CUTS if t >= c[0][0]][-1] if t >= 0 else CUTS[0]
    if t <= keys[0][0]: return list(keys[0][1:])
    for a, b in zip(keys, keys[1:]):
        if t < b[0] or b is keys[-1]:
            x = ease((t - a[0]) / (b[0] - a[0]))
            return [mix(u, v, x) for u, v in zip(a[1:], b[1:])]


# ---- the activation tree: from the laid prompt up through the layers to one node, then to the chosen word ----
LHp, Cp = .28, .1


def _tree():
    import random
    rnd = random.Random(7)
    dots = []
    while len(dots) < 14:
        d = ((rnd.randint(-11, 10) + .5) * Cp, 0., (rnd.randint(-5, 4) + .5) * Cp)
        if d not in dots: dots.append(d)
    layers = [dots]
    for k, n in zip(range(1, 6), (10, 7, 5, 3, 1)):
        rad = 1.5 - .28 * k
        pts = []
        while len(pts) < n:
            x, z = (rnd.randint(-int(rad / Cp), int(rad / Cp)) + .5) * Cp, (rnd.randint(-int(rad / Cp * .7), int(rad / Cp * .7)) + .5) * Cp
            if n == 1: x, z = .05, .05
            if (x, z) not in pts: pts.append((x, z))
        layers.append([(x, k * LHp, z) for x, z in pts])
    segs = []
    for k in range(5):
        up = layers[k + 1]
        for p in layers[k]:
            d = sorted(up, key=lambda q: (q[0] - p[0]) ** 2 + (q[2] - p[2]) ** 2)
            segs.append((p, d[0], k))
            if len(d) > 1 and rnd.random() < .35: segs.append((p, d[1], k))
    segs.append((layers[5][0], (-.7, 2.38, .2), 5))            # up into the chosen word
    return segs


SEGS = _tree()
SEG_A = [s[0] for s in SEGS] + [(0., 0., 0.)] * (64 - len(SEGS))
SEG_B = [s[1] for s in SEGS] + [(0., 0., 0.)] * (64 - len(SEGS))
SEG_K = [float(s[2]) for s in SEGS] + [99.] * (64 - len(SEGS))


PRESS = [T_INIT + .23175 * i for i in range(6)]      # eighth notes; layer 5 first


def press(t, k):
    ti = PRESS[5 - k]
    if t < ti: return 0.
    if t < ti + .08: return outc((t - ti) / .08)
    return 1. - ease((t - ti - .1) / .13)


def params(t):
    cam, look, fov, focus, aper, roll = camera(t)
    mem = []
    for k in range(6):
        tw = PRESS[5 - k] + .07
        mem.append(0. if t < tw else 1. + 1.5 * math.exp(-(t - tw) * 7))
    return dict(
        u_cam=cam, u_look=look, u_fov=math.radians(fov), u_focus=focus, u_aper=aper, u_roll=math.radians(roll),
        u_bright=1. - ease((t - 15.55) / .45),
        u_crt=t - T_PWR, u_scrA=1. - ease((t - 7.0) / .4),
        u_box=1. if t >= T_PROT else 0.,
        u_power=3.2 * (t - 5.3) if t >= 5.3 else -1.,
        u_latR=-.5 + 5. * ease((t - 5.3) / 1.4) if t >= 5.3 else -1.,
        u_rise=outc((t - T_OBJ + .03) / .4) * (1 + .08 * math.sin((t - T_OBJ) * 18) * math.exp(-(t - T_OBJ) * 5)) if t >= T_OBJ - .03 else 0.,
        u_param=ease((t - T_FILL) / .5) * (1 - ease((t - T_SET) / .6)),
        u_fillR=-.5 + 3.8 * clamp((t - T_FILL) / 2.4) if t >= T_FILL else -1.,
        u_press=[press(t, k) for k in range(6)], u_mem=mem, u_memA=ease((t - 5.4) / .8),
        u_act=-1. + 7. * clamp((t - T_SET) / (T_LETS - T_SET)) if t >= T_SET else -9.,
        u_dimL=1. - .45 * ease((t - T_SET) / .6) - .3 * ease((t - T_LETS) / .5),
        u_cand=ease((t - T_LETS + .05) / .5), u_pick=outc((t - T_SIM) / .4),
        u_sa=SEG_A, u_sb=SEG_B, u_sk=SEG_K, u_ns=len(SEGS),
    )


_T = {}


def _words():
    W, H = 1536, 128
    img = Image.new('RGBA', (W, H * 5), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    fw = ImageFont.truetype('C:/Windows/Fonts/CascadiaMono.ttf', 100)
    fn = ImageFont.truetype('C:/Windows/Fonts/CascadiaMono.ttf', 40)
    cands = [('SIMULATION', .83), ('STIMULATION', .07), ('SIMULACRUM', .04), ('SIMILAR', .03), ('SILENCE', .01)]
    for k, (wd, pr) in enumerate(cands):
        y = k * H
        d.text((30, y + 6), wd, font=fw, fill=(236, 232, 222, 255))
        d.text((1080, y + 40), f'{pr:.2f}', font=fn, fill=(230, 150, 80, 255))
        d.line([(1080, y + 100), (1080 + int(420 * pr), y + 100)], fill=(230, 150, 80, 255), width=6)
        d.line([(1080, y + 100), (1500, y + 100)], fill=(120, 116, 110, 140), width=2)
    return img


# ---- the terminal on the CRT ------------------------------------------------------------------------------------
FONT = 'C:/Windows/Fonts/CascadiaMono.ttf'
TERM = [  # (time, text, kind, typing speed s/char; 0 = printed at once)
    (0.34, 'BOOT   rom 0.1   mem 65536 M ......... ok', 'dim', 0),
    (0.42, 'power line ................ 1.20 V   ok', 'dim', 0),
    (0.58, '$ ', 'cmd', 0),
    (1.74, '$ sandbox create --net none --fs readonly', 'cmd', .02),
    (T_PROT, '  [ PROTECTION ]  sandbox 0 created   isolated', 'hi', 0),
    (3.30, '$ ', 'cmd', 0),
    (T_LAY, '$ model load ./me --layers 6', 'cmd', .022),
] + [(4.62 + .135 * k, f'  layer {k}   4096 x 4096   ' + '#' * 16 + f'   0x{k * 0x4000000:08X}   ok', 'dim', 0) for k in range(6)] + [
    (5.30, '  6 layers   6.4 G parameters   ready', 'sys', 0),
    (T_BEGIN, '$ begin', 'cmd', .04),
]
TCOL = dict(dim=150, sys=190, cmd=235, hi=255)
_TF = {}


def term(t):
    W, H = 1280, 720
    if 'f' not in _TF: _TF['f'] = ImageFont.truetype(FONT, 25)
    f = _TF['f']
    img = Image.new('L', (W, H), 0); d = ImageDraw.Draw(img)
    lines = []
    for k, (tt, txt, kind, sp) in enumerate(TERM):
        if t < tt: break
        n = len(txt) if sp == 0 else 2 + int((t - tt) / sp)
        nxt = TERM[k + 1][0] if k + 1 < len(TERM) else 99.
        if txt == '$ ' and t >= nxt: continue                      # an empty prompt replaced by the command typed on it
        if lines and lines[-1][0] == '$ ' and txt.startswith('$ '): lines.pop()
        lines.append((txt[:n], kind, n < len(txt) or (k + 1 == len(TERM)) or txt == '$ '))
    y = 60
    for i, (txt, kind, live) in enumerate(lines):
        v = TCOL[kind]
        if kind == 'hi':
            tw = d.textlength(txt, font=f)
            d.rectangle((60 + 26, y - 4, 60 + tw + 12, y + 34), fill=235)
            d.text((60, y), txt, font=f, fill=10)
        else:
            d.text((60, y), txt, font=f, fill=v)
        if live and i == len(lines) - 1 and (t * 2.5) % 1 < .6:
            cx = 60 + d.textlength(txt, font=f) + 4
            d.rectangle((cx, y + 2, cx + 13, y + 30), fill=230)
        y += 38
    return img


# ---- spatial callouts: anchored to world points, projected with the shader's camera ---------------------------------
CALLOUTS = [  # (t_in, t_out, anchor, text, side)
    (6.00, 7.40, (2.7, 2.1, 2.7), 'sandbox 0   net: none   fs: ro', (1, -1)),
    (6.55, 7.40, (-2.4, 5 * .28, -2.4), 'layer 05   4096 x 4096', (-1, -1)),
    (6.70, 7.40, (2.4, 0., -2.4), 'layer 00   embedding', (1, -1)),
    (6.10, 7.40, (-2.4, -.575, 2.4), 'memory   6 x 32 MiB   empty', (-1, 1)),
    (7.70, 9.60, (.35, .56, .25), 'w[2][1187]', (1, -1)),
    (8.30, 10.0, (1.25, .84, .45), 'w[3][0042]', (1, 1)),
    (10.15, 11.05, (-2.4, -.2, 0.), 'memory   0x00000000', (-1, 1)),
    (10.15, 11.05, (2.4, 5 * .28, 0.), 'load  L5 -> L0', (1, -1)),
    (11.35, 12.85, (.05, 1.4, .05), 'logits', (1, -1)),
    (11.25, 12.85, (-1.05, 0., .05), 'input   14 tokens', (-1, 1)),
]


def project(p, cam, look, fov, roll, w, h):
    def sub(a, b): return tuple(x - y for x, y in zip(a, b))
    def dot(a, b): return sum(x * y for x, y in zip(a, b))
    def nrm(a): l = math.sqrt(dot(a, a)); return tuple(x / l for x in a)
    def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
    fw = nrm(sub(look, cam)); rt = nrm(cross(fw, (0., 1., 0.))); up = cross(rt, fw)
    v = sub(p, cam); z = dot(v, fw)
    if z <= .05: return None
    tf = math.tan(fov / 2) * 2
    x, y = dot(v, rt) / z / tf, dot(v, up) / z / tf
    c, s_ = math.cos(roll), math.sin(roll)
    ux, uy = c * x - s_ * y, s_ * x + c * y
    return ux * h + w / 2, h / 2 - uy * h


def callouts(t, w, h):
    cam, look, fov, focus, aper, roll = camera(t)
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    s = h / 1080
    if 'c' not in _TF: _TF['c'] = {}
    if s not in _TF['c']: _TF['c'][s] = ImageFont.truetype(FONT, int(17 * s))
    f = _TF['c'][s]
    for t0, t1, anc, txt, (sx, sy) in CALLOUTS:
        if not t0 <= t < t1: continue
        a = min(1., (t - t0) / .2, (t1 - t) / .2)
        if txt.startswith('memory   0x'):
            n = sum(1 for k in range(6) if t >= PRESS[k] + .07)
            txt = f'memory   0x00000000   {n}/6 written'
        pr = project(anc, cam, look, math.radians(fov), math.radians(roll), w, h)
        if pr is None: continue
        x, y = pr
        if not (-50 < x < w + 50 and -50 < y < h + 50): continue
        k = min(1., (t - t0) / .25)
        ex, ey = x + sx * 60 * s * k, y + sy * 60 * s * k
        col = (225, 220, 210, int(230 * a))
        d.ellipse((x - 3 * s, y - 3 * s, x + 3 * s, y + 3 * s), outline=col, width=max(1, int(1.5 * s)))
        d.line([(x, y), (ex, ey)], fill=col, width=max(1, int(1.2 * s)))
        tw = d.textlength(txt, font=f)
        lx = ex + sx * 110 * s * k
        d.line([(ex, ey), (lx, ey)], fill=col, width=max(1, int(1.2 * s)))
        n = int(len(txt) * min(1., (t - t0) / .3))
        tx = lx + 8 * s if sx > 0 else lx - 8 * s - tw
        d.text((tx, ey - 12 * s), txt[:n], font=f, fill=col)
    return img


def textures(t, w, h):
    if 'g' not in _T:
        _T['g'] = Image.open(GLYPHS); _T['w'] = _words()
    out = {'u_glyphs': _T['g'], 'u_words': _T['w']}
    if t < 7.5: out['u_term'] = term(t)
    elif 'term_end' not in _T: _T['term_end'] = term(7.5); out['u_term'] = _T['term_end']
    else: out['u_term'] = _T['term_end']
    out['u_ui'] = callouts(t, w, h)
    return out
