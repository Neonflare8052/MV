"""s08 · 1:28.587–1:43.489  gender, time, role, trance — one continuous two-body metaphor over a sheet of spacetime.
Me = the gap ring (the black hole); you = the star. Under us, a plane of points that our masses press down.
The lensed arcs of the star (t02) close into the gap ring · Switch my gender: a cross grows out of the gap (♀), only
for that line · to F to M: it swings into an arrow (♂), only for that line · AM to PM: the arrow becomes a clock hand
and sweeps a full turn; the sheet goes through one day · switch my role, S to M: we orbit a shared centre (+), which
slides from me to you — the deepest dip moves under you; M_me : M_you flips · the trance: the orbit shrinks and speeds
up, the sheet rings with two-armed gravitational waves; the camera sinks into the plane until the sheet is a line
carrying the chirp — s09 takes the line."""
import math
from PIL import Image, ImageDraw, ImageFont

SRC = r'''#version 330
uniform vec2 u_res; uniform float u_time, u_weight;
uniform float u_el, u_D;           // camera elevation (rad) and distance; looks at the origin from +z
uniform float u_R;                 // ring radius (world)
uniform vec3  u_me, u_you;         // world positions (plane y=0)
uniform float u_youA, u_ring, u_intro;
uniform float u_cross, u_arrow, u_hand, u_handA, u_ticks;
uniform vec3  u_bary; uniform float u_baryA, u_trailA;
uniform vec3  u_trM[24], u_trY[24];
uniform float u_field, u_mMe, u_mYou, u_day, u_sun, u_well;
uniform float u_gw, u_ph, u_om, u_line, u_lineG;
uniform sampler2D u_ui;
out vec4 fragColor;
#define PI 3.14159265
float PX;
vec3 CAM, FW, RT, UP; float F;
float h12(vec2 p){ vec3 p3=fract(vec3(p.xyx)*.1031); p3+=dot(p3,p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }
float vn(vec2 p){ vec2 i=floor(p),f=fract(p); f=f*f*(3.-2.*f);
  return mix(mix(h12(i),h12(i+vec2(1,0)),f.x),mix(h12(i+vec2(0,1)),h12(i+vec2(1,1)),f.x),f.y); }
float sdSeg(vec2 p, vec2 a, vec2 b){ vec2 pa=p-a, ba=b-a; float h=clamp(dot(pa,ba)/max(dot(ba,ba),1e-9),0.,1.); return length(pa-ba*h); }
float ln(float d, float w){ return 1.-smoothstep(w-PX,w+PX,d); }
const vec3 WARM=vec3(1.,.9,.78), COP=vec3(1.,.62,.3);
vec3 proj(vec3 P){ vec3 v=P-CAM; float z=dot(v,FW); return vec3(vec2(dot(v,RT),dot(v,UP))*F/max(z,1e-3),F/max(z,1e-3)); }

// ---- the sheet of spacetime -----------------------------------------------------------------------------------------
float height(vec2 x){
  float h=0.;
  vec2 dm=x-u_me.xz, dy=x-u_you.xz;
  h-=.05*u_mMe/sqrt(dot(dm,dm)+.03)*u_well;
  h-=.05*u_mYou/sqrt(dot(dy,dy)+.03)*u_youA*u_well;
  if(u_gw>0.){                                        // two-armed waves leaving the pair, at finite speed
    vec2 b=x-u_bary.xz; float r=length(b), a=atan(b.y,b.x);
    h+=u_gw*.035/(.4+r)*cos(2.*a-2.*u_ph+2.*u_om*r/1.3)*smoothstep(.05,.25,r);
  }
  return h*u_field;
}
vec3 sheet(vec3 ro, vec3 rd){
  const float G=.045, HX=1.7;
  vec3 bmin=vec3(-HX,-.4,-HX), bmax=vec3(HX,.12,HX);
  vec3 ird=1./rd;
  vec3 ta=(bmin-ro)*ird, tb=(bmax-ro)*ird, tn=min(ta,tb), tf=max(ta,tb);
  float t0=max(max(tn.x,tn.y),max(tn.z,0.)), t1=min(min(tf.x,tf.y),tf.z);
  if(t0>=t1) return vec3(0.);
  vec2 dx=rd.xz; dx=vec2(abs(dx.x)<1e-6?1e-6:dx.x,abs(dx.y)<1e-6?1e-6:dx.y);
  vec3 p=ro+rd*(t0+1e-4);
  vec2 cell=floor(p.xz/G), st=sign(dx), dl=abs(G/dx);
  vec2 nx=((cell+max(st,0.))*G-ro.xz)/dx;
  float tc=t0; vec3 acc=vec3(0.);
  vec2 sun=vec2(cos(u_sun),sin(u_sun));
  for(int i=0;i<240;i++){
    if(tc>t1) break;
    vec2 x=(cell+.5)*G;
    if(max(abs(x.x),abs(x.y))<HX){
      float h=height(x);
      vec3 P=vec3(x.x,h,x.y);
      float tt=dot(P-ro,rd);
      if(tt>0.){
        float d=length(ro+rd*tt-P);
        float r=.0042, R=r+PX*tt*.8;
        float hp=h12(cell);
        float e=.18+.3*hp*hp;
        e*=mix(1.,.25+1.5*smoothstep(-.6,.9,dot(normalize(x+1e-4),sun)),u_day);   // one day passing over the sheet
        e+=min(-h*5.,1.2)*.35;                                                     // the dips glow
        e*=1.-smoothstep(1.2,HX,max(abs(x.x),abs(x.y)));
        vec3 c=mix(WARM,COP,clamp(-h*4.,0.,1.));
        acc+=c*e*(r*r)/(R*R)*exp(-d*d/(R*R)*2.)*exp(-tt*.12);
      }
    }
    if(nx.x<nx.y){ tc=nx.x; nx.x+=dl.x; cell.x+=st.x; } else { tc=nx.y; nx.y+=dl.y; cell.y+=st.y; }
  }
  return acc*u_field;
}

void main(){
  vec2 uv=(gl_FragCoord.xy-.5*u_res)/u_res.y; PX=1./u_res.y;
  CAM=vec3(0.,u_D*sin(u_el),u_D*cos(u_el));
  FW=normalize(-CAM); RT=vec3(1.,0.,0.); UP=cross(RT,FW); F=u_D;
  vec3 rd=normalize(FW*F+uv.x*RT+uv.y*UP);
  vec3 col=vec3(.004);
  if(u_field>0.) col+=sheet(CAM,rd)*(1.-.97*u_line);
  // the sheet, edge-on, becomes the one line s09 starts with (same place, width and colour)
  if(u_line>0.){
    float dl=abs(uv.y);
    vec3 lc=mix(WARM,vec3(.55,1.,.78),u_lineG);
    col+=lc*(ln(dl,.0022)+.25*exp(-dl*80.))*step(uv.x,.9)*u_line;
  }

  // orbit trails (recent positions)
  if(u_trailA>0.){
    float dm=1e3, dy=1e3;
    vec2 pm=proj(u_trM[0]).xy, py=proj(u_trY[0]).xy;
    for(int i=1;i<24;i++){
      vec2 a=proj(u_trM[i]).xy, b=proj(u_trY[i]).xy;
      dm=min(dm,sdSeg(uv,pm,a)); dy=min(dy,sdSeg(uv,py,b)); pm=a; py=b;
    }
    col+=WARM*.25*u_trailA*(ln(dm,.0011)+ln(dy,.0011));
  }
  // me: black disk + warm ring with a gap (a billboard); at the start it closes out of the star's two lensed arcs
  vec3 pm3=proj(u_me);
  vec2 m=uv-pm3.xy; float r=length(m), a=atan(m.y,m.x);
  float Rs=u_R*pm3.z;
  float Rin=mix(.47,Rs,u_intro);
  float gap=abs(mod(a-(-PI*.5)+PI,2.*PI)-PI);
  col=mix(col,vec3(0.),(1.-smoothstep(Rin-PX,Rin+PX,r))*u_intro*u_ring);
  float g0=radians(27.);
  vec2 e1=vec2(cos(-PI*.5+g0),sin(-PI*.5+g0))*Rin, e2=vec2(cos(-PI*.5-g0),sin(-PI*.5-g0))*Rin;
  float darc=gap>g0?abs(r-Rin):min(length(m-e1),length(m-e2));
  // the two lensed arcs of t02, fading into the ring
  float arcs=smoothstep(.9,.35,abs(mod(a-.1+PI,2.*PI)-PI))*1.+smoothstep(.55,.15,abs(mod(a-3.3+PI,2.*PI)-PI))*.45;
  float ringW=mix(arcs,gap>g0?1.:0.,u_intro);
  float dr=mix(abs(r-Rin),darc,u_intro);
  col+=WARM*1.4*ln(dr,mix(.0035,.0022,u_intro))*u_ring*max(ringW,u_intro)+WARM*.25*exp(-dr*60.)*u_ring*max(ringW,u_intro);
  // ♀ (Switch my gender) · ♂ (to F to M) · a clock hand (AM to PM)
  vec2 C=pm3.xy;
  vec2 base=C+vec2(0.,-Rs);
  float cr=min(sdSeg(uv,base,base+vec2(0.,-Rs*1.1*u_cross)),sdSeg(uv,base+vec2(-Rs*.45,-Rs*.6),base+vec2(Rs*.45,-Rs*.6))*step(.5,u_cross));
  float flow=.75+.25*sin((uv.y-uv.x)*260.-u_time*18.);                     // the stroke is a stream, not a line
  col+=WARM*1.3*ln(cr,.0022)*flow*step(.01,u_cross)*u_cross;
  vec2 d45=vec2(.7071);
  vec2 ab=C+d45*Rs, at=ab+d45*Rs*1.1;
  float ar=min(sdSeg(uv,ab,at),min(sdSeg(uv,at,at-vec2(Rs*.45,0.)),sdSeg(uv,at,at-vec2(0.,Rs*.45))));
  col+=WARM*1.3*ln(ar,.0022)*flow*u_arrow;
  vec2 hd=vec2(cos(u_handA),sin(u_handA));
  col+=WARM*1.3*ln(sdSeg(uv,C,C+hd*Rs*.85),.0028)*u_hand;
  if(u_ticks>0.){
    float tk=mod(a+PI/12.,PI/6.)-PI/12.;
    col+=WARM*.9*ln(abs(tk)*r,.002)*step(Rs*.82,r)*step(r,Rs*.94)*u_ticks;
  }
  // you: a small star with a corona
  if(u_youA>0.){
    vec3 py3=proj(u_you);
    vec2 y=uv-py3.xy; float yr=length(y); float ya=atan(y.y,y.x);
    float rs=.018*py3.z/F*u_D;
    float core=1.-smoothstep(rs-PX,rs+PX,yr);
    float cor=pow(vn(vec2(ya*5.,1.)),2.)*exp(-max(yr-rs,0.)*60.);
    col+=(WARM*1.8*core+WARM*.7*cor+WARM*.25*exp(-yr*40.))*u_youA;
  }
  // the shared centre of mass
  if(u_baryA>0.){
    vec2 b=uv-proj(u_bary).xy;
    float plus=min(sdSeg(b,vec2(-.018,0.),vec2(.018,0.)),sdSeg(b,vec2(0.,-.018),vec2(0.,.018)));
    col+=COP*1.5*ln(plus,.0018)*u_baryA;
  }
  vec4 ui=texture(u_ui,gl_FragCoord.xy/u_res);
  col=col*(1.-ui.a*.6)+ui.rgb*ui.a;
  fragColor=vec4(col*u_weight,1.);
}
'''
POST = dict(u_bloom=.55, u_ca=.006)

T_GEN, T_FM, T_FMhit, T_WHAT, T_AMPM, T_PM, T_ROLE, T_SM, T_ENTER, T_E1, T_E2, T_TR, T_END = \
    88.587, 90.197, 91.690, 92.015, 93.953, 95.127, 95.465, 97.739, 99.349, 99.516, 99.992, 101.474, 103.489


def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def outc(x): x = clamp(x); return 1 - (1 - x) ** 3


def omega(t): return .6 + 6.5 * ease((t - T_ENTER) / (T_END - T_ENTER)) ** 2


def phase(t):
    if t <= T_ROLE: return 0.
    n = 60; s = 0.
    for i in range(n):
        tt = T_ROLE + (t - T_ROLE) * (i + .5) / n
        s += omega(tt) * (t - T_ROLE) / n
    return s


def bodies(t):
    """world positions (x, 0, z) of me, you, the centre of mass; ring radius"""
    shrink = ease((t - T_ROLE) / .8)
    R = .22 - (.22 - .07) * shrink
    mass = ease((t - T_SM) / .9)                         # 0: I am the heavy one, 1: you are
    sep = .5 * (1 - .8 * ease((t - T_ENTER) / (T_END - T_ENTER)) ** 1.4)
    ph = phase(t)
    fm = .12 + .76 * mass
    d = (math.cos(ph), math.sin(ph))
    me = (-d[0] * sep * fm * shrink, 0., d[1] * sep * fm * shrink)
    you = (d[0] * sep * (1 - fm), 0., -d[1] * sep * (1 - fm))
    return me, you, (0., 0., 0.), R, mass, ph


def params(t):
    me, you, bary, R, mass, ph = bodies(t)
    youA = ease((t - T_ROLE - .2) / .5) * (1 - ease((t - T_END + .38) / .3))
    if youA <= 0: you = (3., 0., 3.)
    trM, trY = [], []
    for i in range(24):
        tt = max(t - i * .06, T_ROLE)
        m2, y2, *_ = bodies(tt); trM.append(m2); trY.append(y2)
    # ♀ only for "Switch my gender", ♂ only for "To F to M", then the hand
    cross = outc((t - T_GEN - .25) / .8) * (1 - ease((t - T_FM) / .3))
    arrow = ease((t - T_FM) / .3) * (1 - ease((t - T_WHAT) / .35))
    a0 = math.radians(45.)
    sweep = ease((t - T_AMPM) / (T_PM - T_AMPM))
    hand = ease((t - T_WHAT) / .35) * (1 - ease((t - T_ROLE) / .35))
    k = ease((t - T_ENTER - .3) / (T_END - T_ENTER - .45))
    el = math.radians(90 - 89.85 * k ** 1.3)          # sink into the plane until it is a line
    D = 1. + 4.5 * k ** 1.6                           # ... pulling back as we go (the scale at the centre is kept)
    return dict(
        u_el=el, u_D=D, u_R=R, u_me=me, u_you=you, u_bary=bary, u_youA=youA,
        u_ring=1. - ease((t - T_END + .38) / .3), u_intro=ease((t - T_GEN) / .45),
        u_cross=cross, u_arrow=arrow, u_hand=hand, u_handA=a0 - 2 * math.pi * sweep,
        u_ticks=ease((t - T_AMPM + .3) / .4) * (1 - ease((t - T_ROLE) / .4)),
        u_baryA=ease((t - T_ROLE - .4) / .4) * (1 - ease((t - T_TR) / .6)),
        u_trailA=ease((t - T_ROLE - .5) / .6) * (1 - ease((t - T_END + .6) / .5)), u_trM=trM, u_trY=trY,
        u_line=ease((t - 102.95) / .45), u_lineG=ease((t - 103.12) / .32),
        u_field=ease((t - T_GEN - .3) / 1.2), u_well=1. - .9 * ease((t - 102.3) / 1.), u_mMe=1.1 - .8 * mass, u_mYou=.3 + .8 * mass,
        u_day=ease((t - T_AMPM + .2) / .4) * (1 - ease((t - T_ROLE) / .5)), u_sun=a0 - 2 * math.pi * sweep,
        u_gw=ease((t - T_ENTER) / 1.5) * (1 + 1.2 * ease((t - T_TR) / 2.)), u_ph=ph, u_om=omega(t),
    )


# ---- a few numbers, small, bottom-left ------------------------------------------------------------------------------------
FONT = 'C:/Windows/Fonts/CascadiaMono.ttf'
_F = {}


def textures(t, w, h):
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    if t < T_ROLE + .3: return {'u_ui': img}
    d = ImageDraw.Draw(img); s = h / 1080
    if s not in _F: _F[s] = ImageFont.truetype(FONT, int(18 * s))
    f = _F[s]
    me, you, bary, R, mass, ph = bodies(t)
    a = int(210 * ease((t - T_ROLE - .3) / .4) * (1 - ease((t - T_END + .5) / .4)))
    mm, my = 1.1 - .8 * mass, .3 + .8 * mass
    tot = mm + my
    om = omega(t)
    lines = [f'M_me : M_you   {mm / tot:.2f} : {my / tot:.2f}',
             f'P_orb          {2 * math.pi / om:5.2f} s',
             f'f_GW           {om / math.pi:5.2f} Hz']
    if t > T_ENTER: lines.append('h(t)           ' + '▁▂▃▄▅▆▇█'[min(7, int(ease((t - T_ENTER) / (T_END - T_ENTER)) * 8))] * 6)
    for i, ln in enumerate(lines):
        d.text((70 * s, h - (70 + (len(lines) - i) * 26) * s), ln, font=f, fill=(226, 222, 214, a))
    return {'u_ui': img}
