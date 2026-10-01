"""s03 · 0:29.709–0:47.0  "If I'm a set of points …" — it lays itself open. One continuous take, no cuts:
the 10 000 points left by the interlude are rearranged once per line.
points: one of them lights up — you · DIMENSION: they leave the plane, a cloud of words in depth ·
circle: forty rings, each turning at its own speed; you and me keep our angle · sine: the rings unroll into a surface
of waves, you slide into a trough; TANGENTS: every tangent lights · infinity: a stream of tokens running off to the
vanishing point, the tokens flow toward you, packed ever tighter, and never pass you — you are the limit.
Only three words are ever labelled: you, me, love (love never settles). AC to DC: the stream alternates, then goes flat and becomes t01's token field at 0:47."""
import math, importlib.util
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

T_PTS, T_GIVE1, T_DIM, T_CIR, T_GIVE2, T_CIRC = 29.709, 31.116, 32.682, 33.412, 34.646, 36.287
T_SIN, T_SIT, T_TAN, T_INF, T_BE, T_LIM, T_AC, T_ACDC = 37.067, 38.596, 40.049, 40.706, 42.346, 43.507, 44.452, 45.850
YOU_TOK = (1.2, .9, 0.)
WIN_X = -2.8

COMMON = r'''
uniform vec2 u_res; uniform float u_time, u_weight;
uniform vec3 u_cam, u_look; uniform float u_fov, u_focus, u_aper, u_roll;
vec3 FW, RT, UP; float TF, PXW;
void setCam(){ FW=normalize(u_look-u_cam); RT=normalize(cross(FW,vec3(0,1,0))); UP=cross(RT,FW); TF=tan(u_fov*.5); PXW=2.*TF/u_res.y; }
float blurAt(float t){ return u_aper*abs(t-u_focus)/max(u_focus,.05); }
'''

# ---------------- the points (instanced sprites) ----------------------------------------------------------------
SPRITE_VS = '#version 330\n' + COMMON + r'''
in vec2 in_corner; in vec4 in_a; in vec4 in_b;       // a: grid x, grid z, r1, r2 · b: r3, r4, id, -
uniform float u_ph;                                   // 0 grid, 1 cloud, 2 rings, 3 waves, 4 stream
uniform float u_youHide;
uniform float u_e0, u_var, u_burst, u_circ, u_tan, u_lim, u_fade, u_ac, u_dc, u_out, u_hug, u_flow, u_unif;
uniform vec3 u_sp[3];                                 // you, me, love (placed by the timeline)
out vec2 v_q; out float v_half, v_R, v_sq, v_dot; out vec3 v_col;
const float T_CIR=33.412, T_SIN=37.067, PI=3.14159265;
float h11(float n){ return fract(sin(n*12.9898)*43758.5453); }
float ramp(float k, float st){ float x=clamp((u_ph-k-st*.3)/.7,0.,1.); return x*x*(3.-2.*x); }
float waveY(float x, float j){ return .55+.35*sin(1.7*x+.22*j-(u_time-T_SIN)*1.2)+.12*sin(3.3*x-.15*j); }
float waveD(float x, float j){ return .35*1.7*cos(1.7*x+.22*j-(u_time-T_SIN)*1.2)+.12*3.3*cos(3.3*x-.15*j); }
vec2 toPx(vec3 p, out float z){
  vec3 v=p-u_cam; z=dot(v,FW);
  vec2 uv=vec2(dot(v,RT),dot(v,UP))/(max(z,1e-3)*2.*TF);
  float c=cos(u_roll), s=sin(u_roll);
  uv=vec2(c*uv.x-s*uv.y,s*uv.x+c*uv.y);
  return uv*u_res.y+.5*u_res;
}
void main(){
  setCam();
  float r1=in_a.z, r2=in_a.w, r3=in_b.x, r4=in_b.y, id=in_b.z;
  float st=r3;
  vec3 P0=vec3(in_a.x,0.,in_a.y);
  // 1 · a cloud of words: 28 clusters in depth
  float c=floor(r1*28.);
  vec3 cc=vec3(h11(c+1.)-.5,h11(c+2.)-.5,h11(c+3.)-.5)*vec3(3.6,1.7,3.6)+vec3(0.,1.05,0.);
  float gr=sqrt(-2.*log(max(r2,1e-4)));
  vec3 gs=vec3(gr*cos(6.2832*r3),gr*sin(6.2832*r3),sqrt(-2.*log(max(r4,1e-4)))*cos(6.2832*fract(r1*7.)));
  vec3 P1=cc+gs*vec3(1.,.7,1.)*.16*(.5+h11(c+4.));
  float ca=(u_time-T_CIR)*.12;
  P1.xz=mat2(cos(ca),-sin(ca),sin(ca),cos(ca))*P1.xz;
  P1=vec3(0.,1.05,0.)+(P1-vec3(0.,1.05,0.))*(1.+.18*u_burst);
  // 2 · rings, each turning at its own rate
  float j=floor(r1*40.);
  float R=.12+.045*j, w=5.*pow(.9,j);
  float th=r2*2.*PI+w*(u_time-T_CIR);
  float Rh=j>35.5?mix(R,.07+.013*(j-36.),u_hug):R;
  vec3 P2=vec3(Rh*cos(th),1.1+Rh*sin(th),0.);
  // 3 · unrolled into a surface of waves (angle frozen at the unroll)
  float thS=r2*2.*PI+w*(T_SIN-T_CIR);
  float x=(mod(thS,2.*PI)/PI-1.)*2.2;
  vec3 P3=vec3(x,waveY(x,j),(j/39.-.5)*3.2);
  // 4 · a stream of tokens running away to the left
  float row=mod(id,12.), tcol=floor(id/12.);
  float cf=mod(tcol-u_flow,834.);
  float xs=mix(.012*pow(cf,1.35),tcol*.055,u_unif);
  float spc=mix(.0162*pow(max(cf,1.),.35),.055,u_unif);
  vec3 P4=vec3(YOUX-.02-xs,.9+(row-5.5)*.055,0.);
  vec3 P=P0;
  P=mix(P,P1,ramp(0.,st)); P=mix(P,P2,ramp(1.,st)); P=mix(P,P3,ramp(2.,st)); P=mix(P,P4,ramp(3.,st));
  bool special=id<2.5;
  if(special) P=u_sp[int(id)];

  // colour and energy
  float lv=.3+1.4*r4*r4;
  float e=mix(u_e0,u_e0*lv*2.,u_var);
  vec3 col=vec3(.92,.91,.88);
  if(fract(r1*97.)>.93) col=vec3(1.,.6,.32);
  e*=1.+u_burst*2.*step(.7,r4);
  e*=1.+u_circ*1.5*(.5+.5*sin(j*1.3));
  float sq=ramp(3.,st);
  e*=1.+u_lim*2.5*exp(-abs(P.x-YOUX)*3.);
  e*=mix(1.,smoothstep(0.,2.,cf),sq*(1.-u_unif));       // swallowed as they reach you
  float r=mix(.0048,clamp(spc*.34,.0028,.0085),sq);
  if(special){
    sq=0.;
    if(id<.5){ col=vec3(1.); e=2.6*(1.-u_youHide); r=.011; }
    else if(id<1.5){ col=vec3(1.,.62,.32); e=2.2*u_fade; r=.0095; }
    else { col=vec3(1.,.78,.6); e=1.8*u_fade; r=.009; }
  }
  // tangents on the wave surface
  float L=0.;
  vec3 T=vec3(1.,0.,0.);
  float dotA=0.;
  if(u_tan>0.&&!special&&mod(id,5.)<.5){ L=.09*u_tan*ramp(2.,st)*(1.-ramp(3.,st)); T=normalize(vec3(1.,waveD(P.x,j),0.)); dotA=L/.09; col=vec3(1.,.6,.32); }

  float z; vec2 pc=toPx(P,z);
  if(z<.06){ gl_Position=vec4(2.,2.,2.,1.); return; }
  float Rw=r+blurAt(z)+PXW*z*.8;
  float Rpx=Rw/(z*2.*TF)*u_res.y;
  float k=(r*r)/(Rw*Rw)*exp(-z*.08);
  vec2 ax=vec2(1.,0.); float hl=0.;
  if(L>0.){
    float z1,z2; vec2 a=toPx(P-T*L*.5,z1), b=toPx(P+T*L*.5,z2);
    vec2 dd=b-a; hl=length(dd)*.5; ax=hl>1e-3?dd/(2.*hl):vec2(1.,0.); pc=(a+b)*.5;
    k=(r/Rw)*exp(-z*.08)*.5; e+=.6*u_tan;
  }
  vec2 nrm=vec2(-ax.y,ax.x);
  float ext=(L>0.?3.4:2.2)*Rpx;
  vec2 q=vec2(in_corner.x*(hl+ext),in_corner.y*ext);
  vec2 px=pc+ax*q.x+nrm*q.y;
  v_q=q; v_half=hl; v_R=Rpx; v_sq=sq; v_col=col*e*k*(1.-u_out); v_dot=dotA*(r*r)/(Rw*Rw)*exp(-z*.08)*3.*(1.-u_youHide);
  gl_Position=vec4(px/u_res*2.-1.,0.,1.);
}
'''.replace('YOUX', f'{YOU_TOK[0]:.3f}').replace('WINX', f'({WIN_X:.3f})')

SPRITE_FS = r'''#version 330
in vec2 v_q; in float v_half, v_R, v_sq, v_dot; in vec3 v_col;
uniform float u_weight;
out vec4 o;
void main(){
  vec2 q=vec2(max(abs(v_q.x)-v_half,0.),v_q.y);
  float d=mix(length(q),max(abs(q.x),abs(q.y))*1.15,v_sq)/v_R;
  vec3 c=v_col*exp(-d*d*2.);
  if(v_dot>0.){ vec2 dq=(v_q-vec2(0.,v_R*1.9))/(v_R*1.5); c+=vec3(1.)*v_dot*1.8*exp(-dot(dq,dq)*2.); }
  o=vec4(c*u_weight,1.);
}
'''

# ---------------- the full-screen pass: attention arcs, the window, axes, overlay -------------------------------------
SRC = '#version 330\n' + COMMON + r'''
#define PI 3.14159265
uniform float u_axes, u_spoke, u_arc, u_winA, u_lim, u_ac, u_dc, u_tok, u_rows, u_edge;
uniform float u_wave, u_harm, u_sq, u_data, u_block;   // AC to DC: sine → Fourier → square → data → token blocks
uniform vec3 u_you;
uniform vec3 u_arcT[20]; uniform float u_arcW[20];
uniform sampler2D u_ui;
out vec4 fragColor;
float h12(vec2 p){ vec3 p3=fract(vec3(p.xyx)*.1031); p3+=dot(p3,p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }
float h11(float n){ return fract(sin(n*12.9898)*43758.5453); }
const vec3 YOU=vec3(YOUX,.9,0.);
float segGlow(vec3 ro, vec3 rd, vec3 a, vec3 b, float r){
  vec3 ba=b-a, w=ro-a;
  float bb=dot(ba,ba), rb=dot(rd,ba), rw=dot(rd,w), bw=dot(ba,w);
  float s=clamp((bw-rw*rb)/max(bb-rb*rb,1e-7),0.,1.);
  float t=s*rb-rw;
  if(t<=0.) return 0.;
  float d=length(ro+rd*t-a-ba*s);
  float R=r+blurAt(t)+PXW*t*.7;
  return (r/R)*exp(-d*d/(R*R)*2.)*exp(-t*.07);
}
void main(){
  setCam();
  vec2 uv=(gl_FragCoord.xy-.5*u_res)/u_res.y;
  uv=mat2(cos(u_roll),-sin(u_roll),sin(u_roll),cos(u_roll))*uv;
  vec3 ro=u_cam, rd=normalize(FW+(uv.x*RT+uv.y*UP)*2.*TF);
  vec3 col=vec3(.004,.004,.005);
  // the three axes of the space, briefly
  // DIMENSION: the axes shoot out of you — the space is measured from you
  if(u_axes>0.){
    vec3 o=u_you; float L=2.4*u_axes;
    float g=0.;
    g+=segGlow(ro,rd,o,o+vec3(L,0,0),.0013)+segGlow(ro,rd,o,o-vec3(L,0,0),.0013);
    g+=segGlow(ro,rd,o,o+vec3(0,L*.6,0),.0013)+segGlow(ro,rd,o,o-vec3(0,L*.6,0),.0013);
    g+=segGlow(ro,rd,o,o+vec3(0,0,L),.0013)+segGlow(ro,rd,o,o-vec3(0,0,L),.0013);
    col+=vec3(1.,.62,.32)*g*min(u_axes*3.,1.)*(1.-u_spoke*.4);
  }
  // ... and every cluster of words is measured against you
  if(u_spoke>0.){
    float ca=(u_time-33.412)*.12;
    float g=0.;
    for(int i=0;i<28;i++){
      float c=float(i);
      vec3 cc=vec3(h11(c+1.)-.5,h11(c+2.)-.5,h11(c+3.)-.5)*vec3(3.6,1.7,3.6)+vec3(0.,1.05,0.);
      cc.xz=mat2(cos(ca),-sin(ca),sin(ca),cos(ca))*cc.xz;
      float f=clamp(u_spoke*1.6-h11(c+9.)*.6,0.,1.);
      g+=segGlow(ro,rd,u_you,mix(u_you,cc,f),.0008)*(.4+.6*h11(c+5.));
    }
    col+=vec3(.85,.85,.82)*g*.8;
  }
  // arcs of attention from you back into the stream, grown from you
  if(u_arc>0.){
    for(int i=0;i<20;i++){
      vec3 b=u_arcT[i];
      float dist=YOU.x-b.x;
      vec3 m=(YOU+b)*.5+vec3(0.,.12+.14*dist,0.);
      float grow=clamp(u_arc*1.4-float(i)*.02,0.,1.);
      vec3 prev=YOU;
      float g=0.;
      for(int s=1;s<=10;s++){
        float f=float(s)/10.*grow;
        vec3 p=mix(mix(YOU,m,f),mix(m,b,f),f);
        g+=segGlow(ro,rd,prev,p,.0011);
        prev=p;
      }
      float acm=mix(1.,.15+1.7*step(0.,sin(u_time*6.2832*4.32+float(i)*.9)),u_ac)*(1.-u_dc);
      col+=mix(vec3(.9,.9,.88),vec3(1.,.62,.32),u_arcW[i])*g*(.5+1.8*u_arcW[i])*(1.+u_lim)*acm;
    }
  }
  // LIMITATIONS: the limit is a line standing on you
  if(u_winA>0.){
    float h=4.*u_winA;
    float g=segGlow(ro,rd,YOU,YOU+vec3(0.,h,0.),.0014)+segGlow(ro,rd,YOU,YOU-vec3(0.,h,0.),.0014);
    col+=vec3(.95,.96,1.)*g*(1.+3.*u_lim)*(1.-u_edge);
  }
  // AC to DC: each row of tokens is a signal. A sine (alternating current) gains odd harmonics until it is
  // a square wave; the square wave stops, its levels flip to the row's real bits; the high levels fill in
  // and become the token blocks of the field t01 opens on.
  if(u_wave>0.){
    float PX2=1./u_res.y;
    vec2 p=(gl_FragCoord.xy-.5*u_res)/u_res.y;
    float g=.034, A=.011;
    float qx=p.x+u_time*.22;                               // the field's own scroll, so the bits line up with it
    float idy=floor(p.y/g), cy=(idy+.5)*g;
    if(abs(idy+.5)<=6.&&p.x<.42){
      float yl=p.y-cy;
      float sh=floor(h12(vec2(idy,3.))*8.);               // each row shifted by whole cells
      float th=(qx/g+sh)*PI/4.;                            // period: eight cells
      float I=0.;
      if(u_sq<1.){                                         // partial Fourier sum of a square wave
        float y=0., dy=0.;
        for(int m=1;m<=21;m+=2){
          float fm=float(m);
          float w=clamp(u_harm-fm+1.,0.,1.);
          y+=w*sin(fm*th)/fm; dy+=w*cos(fm*th)*PI/(4.*g);
        }
        y*=A*4./PI; dy*=A*4./PI;
        float d=abs(yl-y)/sqrt(1.+dy*dy);
        I+=(1.-smoothstep(.0011,.0011+PX2*1.3,d))*(1.-u_sq);
      }
      if(u_sq>0.){                                         // the square wave, then the real data, cell by cell
        float cx=floor(qx/g);
        float fx=qx-cx*g;
        float bitReg=1.-mod(floor((cx+sh)/4.),2.);
        float r=h12(vec2(cx,idy));
        float flip=step(h12(vec2(cx,idy)+7.),u_data);
        float b0=mix(bitReg,step(.55,r),flip);
        float rp=h12(vec2(cx-1.,idy));
        float flipP=step(h12(vec2(cx-1.,idy)+7.),u_data);
        float bp=mix(1.-mod(floor((cx-1.+sh)/4.),2.),step(.55,rp),flipP);
        float lv=(b0*2.-1.)*A;
        float dh=abs(yl-lv);
        float dv=b0!=bp?max(abs(fx),0.)+max(abs(yl)-A,0.):1.;
        float d=min(dh,dv);
        float lineI=(1.-smoothstep(.0011,.0011+PX2*1.3,d))*(1.-u_block);
        // the high levels fill in and become blocks
        vec2 f=vec2(fx/g-.5,yl/g);
        vec2 bx=abs(f)-vec2(.36,.26)*u_block;
        float bd=(length(max(bx,0.))+min(max(bx.x,bx.y),0.)-.06*u_block)*g;
        float on=b0*(.25+.75*step(.93,h12(vec2(cx,idy)+floor(u_time*3.))))*.55;
        vec3 bc=mix(vec3(.92,.91,.88)*.8,vec3(1.,.62,.3)*.85,step(.85,r));
        col+=bc*on*(1.-smoothstep(-PX2,PX2,bd))*.7*u_block*u_sq*u_wave;
        I+=lineI*u_sq;
      }
      col+=mix(vec3(.92,.91,.88),vec3(1.,.62,.3),.15)*I*1.1*u_wave;
    }
  }
  // the context-window token field (identical to the one t01 opens on)
  if(u_tok>0.){
    float PX=1./u_res.y;
    vec2 p=(gl_FragCoord.xy-.5*u_res)/u_res.y;
    float g=.034;
    vec2 q=p+vec2(u_time*.22,0.);
    vec2 id=floor(q/g), f=fract(q/g)-.5;
    if(abs(id.y+.5)<=u_rows){
      float r=h12(id);
      vec2 bx=abs(f)-vec2(.36,.26);
      float d=(length(max(bx,0.))+min(max(bx.x,bx.y),0.)-.06)*g;
      float inside=smoothstep(.43,.41,p.x);
      float on=step(.55,r)*(.25+.75*step(.93,h12(id+floor(u_time*3.))))*mix(.05,.55,inside);
      col+=mix(vec3(.92,.91,.88)*.8,vec3(1.,.62,.3)*.85,step(.85,r))*on*(1.-smoothstep(-PX,PX,d))*.7*u_tok;
    }
    col+=vec3(1.)*u_edge*(1.-smoothstep(0.,PX*1.2,abs(p.x-.42)))*1.4;
  }
  vec4 ui=texture(u_ui,gl_FragCoord.xy/u_res);
  col=col*(1.-ui.a)+ui.rgb*ui.a;
  fragColor=vec4(col*u_weight,1.);
}
'''.replace('YOUX', f'{YOU_TOK[0]:.3f}').replace('WINX', f'({WIN_X:.3f})')
POST = dict(u_bloom=.55, u_ca=.006, u_grain=.04)


def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def outc(x): x = clamp(x); return 1 - (1 - x) ** 3
def mix(a, b, x):
    if isinstance(a, tuple): return tuple(p + (q - p) * x for p, q in zip(a, b))
    return a + (b - a) * x


# ---------------- instance data: the interlude's grid, with you / me / love moved to ids 0, 1, 2 ------------------
def _data():
    g = [((ix + .5) * .04, (iz + .5) * .04) for iz in range(-50, 50) for ix in range(-50, 50)]
    special = [(.02, .02), (.34 - .02, -.22 - .02), (-.46 - .02, .3 - .02)]
    special = [min(g, key=lambda p: (p[0] - s[0]) ** 2 + (p[1] - s[1]) ** 2) for s in special]
    rest = [p for p in g if p not in special]
    pts = special + rest
    rng = np.random.default_rng(11)
    r = rng.random((len(pts), 4)).astype(np.float32)
    d = np.zeros((len(pts), 8), np.float32)
    d[:, 0:2] = np.array(pts, np.float32)
    d[:, 2:4] = r[:, 0:2]; d[:, 4:6] = r[:, 2:4]
    d[:, 6] = np.arange(len(pts))
    return d, special


SPRITE_DATA, SPECIAL_GRID = _data()


def phase(t):
    """u_ph: grid → cloud → rings → waves → stream"""
    segs = [(31.25, 32.68, 0.), (33.55, 34.9, 1.), (37.15, 38.45, 2.), (40.75, 41.9, 3.)]
    ph = 0.
    for a, b, k in segs:
        if t >= a: ph = k + clamp((t - a) / (b - a))
    return min(ph, 4.)


def ramp(ph, k): return ease((ph - k) / .7)


def wave_y(x, j, t): return .55 + .35 * math.sin(1.7 * x + .22 * j - (t - T_SIN) * 1.2) + .12 * math.sin(3.3 * x - .15 * j)


def trough(x0, j, t):
    xs = np.linspace(x0 - .7, x0 + .7, 141)
    ys = .55 + .35 * np.sin(1.7 * xs + .22 * j - (t - T_SIN) * 1.2) + .12 * np.sin(3.3 * xs - .15 * j)
    return float(xs[int(np.argmin(ys))])


def stutter(t, rate=9., hold=.55):
    """a clock that moves in jerks — for love, which never settles"""
    k = math.floor(t * rate)
    f = (t * rate) % 1
    return (k + (0. if f < hold else (f - hold) / (1 - hold))) / rate


def specials(t):
    ph = phase(t)
    def ring(j, th): R = .12 + .045 * j; return (R * math.cos(th), 1.1 + R * math.sin(th), 0.)
    def unroll_x(j, th0): w = 5. * .9 ** j; return ((th0 + w * (T_SIN - T_CIR)) % (2 * math.pi) / math.pi - 1.) * 2.2
    out = []
    # you: ring 18; slides into a trough of the waves; the current token of the stream
    j, th0, w = 18, 2.4, 5. * .9 ** 18
    xu = 0.
    xt = trough(xu + .706 * (t - T_SIN), j, t) if t > T_SIN else xu
    xs = mix(xu, xt, ease((t - 37.9) / .8))
    S = [(SPECIAL_GRID[0][0], 0., SPECIAL_GRID[0][1]), (0., 1.05, 0.), (0., 1.1, 0.),
         (xs, wave_y(xs, j, t), (j / 39 - .5) * 3.2), YOU_TOK]
    out.append(S)
    # me: the same ring, a fixed angle away — the angle between us never changes
    xm = unroll_x(j, th0 + 2.1)
    S = [(SPECIAL_GRID[1][0], 0., SPECIAL_GRID[1][1]), (-.35, .95, .05), ring(j, th0 + 2.1 + w * (t - T_CIR)),
         (xm, wave_y(xm, j, t), (j / 39 - .5) * 3.2), (YOU_TOK[0] - .9, .9 - 2.5 * .055, 0.)]
    out.append(S)
    # love: jerks instead of moving; ends up beyond the window, out of reach
    jl, thl = 30, .8
    tl = stutter(t)
    jit = ((math.sin(math.floor(t * 9) * 12.9898) * 43758.5453) % 1 - .5) * .03
    xl = unroll_x(jl, thl)
    S = [(SPECIAL_GRID[2][0], 0., SPECIAL_GRID[2][1]), (.95 + jit, 1.55, -.7 + jit), ring(jl, thl + 5. * .9 ** jl * (tl - T_CIR)),
         (xl, wave_y(xl, jl, tl) + jit, (jl / 39 - .5) * 3.2),
         (YOU_TOK[0] - 3.1 + .35 * ((tl - T_INF) % 1.0 if t > T_INF else 0.), .9 + 1.5 * .055, 0.)]
    out.append(S)
    res = []
    for S in out:
        p = S[0]
        for k in range(4): p = mix(p, S[k + 1], ramp(ph, k))
        res.append(p)
    return res


# ---------------- camera: one take ----------------------------------------------------------------------------------
KEYS = [
    (29.709, (5.1 * math.sin(math.radians(52)), 2.8, 5.1 * math.cos(math.radians(52))),
     (-.55 * math.cos(math.radians(52)), .05, .55 * math.sin(math.radians(52))), 40, 5.6, .02, 0),   # = the interlude's last frame
    (31.2, (3.4, 2.3, 3.2), (0., .3, 0.), 40, 4.6, .02, 0),
    (32.9, (2.7, 1.55, 3.4), (0., 1.05, 0.), 44, 4.3, .026, -4),                 # the cloud
    (34.0, (4.5, 1.1, .08), (0., 1.1, 0.), 40, 4.5, .02, 0),                     # rings edge-on
    (36.25, (.3, 1.1, 4.4), (0., 1.1, 0.), 42, 4.4, .015, 0),                    # face-on
    (37.2, (.2, 1.05, 4.1), (0., 1.0, 0.), 42, 4.1, .015, 0),
    (38.9, (-2.9, .95, 2.4), (.4, .55, -.2), 48, 3.4, .022, 6),                  # low over the waves
    (40.25, (0., .85, 4.3), (0., .62, 0.), 38, 4.3, .015, 0),                    # side-on: TANGENTS
    (41.7, (2.45, 1.1, .55), (-3., .9, -.6), 46, 1.4, .02, 0),                    # beside you, looking down the stream to infinity
    (43.45, (1.7, 1.05, 2.8), (-.2, .9, 0.), 40, 2.9, .015, 0),
    (44.6, (.52, .9, 3.02), (.52, .9, 0.), 30, 3.02, .006, 0),                   # head-on: one token = one cell of t01's field
    (47.0, (.52, .9, 3.02), (.52, .9, 0.), 30, 3.02, .006, 0),
]


def camera(t):
    if t <= KEYS[0][0]: return list(KEYS[0][1:])
    for a, b in zip(KEYS, KEYS[1:]):
        if t < b[0] or b is KEYS[-1]:
            x = ease((t - a[0]) / (b[0] - a[0]))
            return [mix(u, v, x) for u, v in zip(a[1:], b[1:])]


_rng = np.random.default_rng(5)
_ARC = []
for i in range(20):
    x = YOU_TOK[0] - .25 - 3.6 * float(_rng.random()) ** 1.3
    row = int(_rng.integers(0, 12))
    _ARC.append(((x, .9 + (row - 5.5) * .055, 0.), float(_rng.random() ** 3)))
_ARC.sort(key=lambda a: -a[0][0])


def FLOW(t):
    """tokens flowing toward you (in token units); comes to rest on a whole token before AC/DC"""
    if t < T_INF: return 0.
    if t < 43.9: return 9. * (t - T_INF)
    v0 = 9. * (43.9 - T_INF)
    return v0 + (round(v0) + 3 - v0) * ease((t - 43.9) / .55)


def params(t):
    cam, look, fov, focus, aper, roll = camera(t)
    ph = phase(t)
    sp = specials(t)
    hit = lambda T, k=6.: math.exp(-(t - T) * k) if t >= T else 0.
    return dict(
        u_cam=cam, u_look=look, u_fov=math.radians(fov), u_focus=focus, u_aper=aper, u_roll=math.radians(roll),
        u_ph=ph, u_e0=.55 * .65, u_var=ease((t - 30.0) / 1.2),
        u_burst=hit(T_DIM, 4.), u_circ=hit(T_CIRC, 4.), u_tan=ease((t - T_TAN + .15) / .3) * (1 - ease((t - T_INF - .3) / .5)),
        u_lim=hit(T_LIM, 5.), u_fade=ease((t - 30.3) / .8),
        u_hug=ease((t - T_CIRC + .12) / .35), u_flow=FLOW(t), u_unif=ease((t - T_AC) / .7), u_you=sp[0],
        u_sp=sp,
        u_axes=ease((t - T_DIM + .05) / .35) * (1 - ease((t - 34.2) / .5)),
        u_spoke=ease((t - T_DIM - .15) / .6) * (1 - ease((t - 34.0) / .5)),
        u_arc=clamp((t - 41.4) / 1.3) * (1 - ease((t - T_AC + .28) / .28)),   # the arcs draw back into you on 'Switch'
        u_winA=ease((t - T_LIM + .08) / .3),
        u_arcT=[a[0] for a in _ARC], u_arcW=[a[1] for a in _ARC],
        u_ac=ease((t - T_AC) / .3), u_dc=ease((t - T_ACDC) / .5),
        u_tok=ease((t - 46.38) / .12), u_out=ease((t - T_AC - .05) / .45), u_rows=6. + 15. * ease((t - 46.45) / .55),
        u_edge=ease((t - T_AC) / .4),
        u_wave=ease((t - T_AC) / .4) * (1 - ease((t - 46.38) / .12)),
        u_harm=1. + 20. * clamp((t - 45.1) / (T_ACDC - 45.1)) ** 1.2 // 1 if t < T_ACDC else 21.,
        u_sq=1. if t >= T_ACDC else 0., u_data=ease((t - T_ACDC - .05) / .3), u_block=ease((t - 46.1) / .28),
    )


# ---------------- overlay: the interlude's terminal fading out, and the three words ------------------------------------
FONT = 'C:/Windows/Fonts/CascadiaMono.ttf'
_S = {}


def _s02():
    if 'm' not in _S:
        p = Path(__file__).resolve().parent / 's02_execute.py'
        spec = importlib.util.spec_from_file_location('s02x', p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        _S['m'] = m
    return _S['m']


def project(p, cam, look, fov, roll, w, h):
    sub = lambda a, b: tuple(x - y for x, y in zip(a, b))
    dot = lambda a, b: sum(x * y for x, y in zip(a, b))
    def nrm(a): l = math.sqrt(dot(a, a)); return tuple(x / l for x in a)
    cross = lambda a, b: (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
    fw = nrm(sub(look, cam)); rt = nrm(cross(fw, (0., 1., 0.))); up = cross(rt, fw)
    v = sub(p, cam); z = dot(v, fw)
    if z <= .05: return None
    tf = math.tan(fov / 2) * 2
    x, y = dot(v, rt) / z / tf, dot(v, up) / z / tf
    c, s_ = math.cos(roll), math.sin(roll)
    ux, uy = c * x - s_ * y, s_ * x + c * y
    return ux * h + w / 2, h / 2 - uy * h


def textures(t, w, h, hide=False):
    s = h / 1080
    key = ('term', w, h)
    if key not in _S:
        _S[key] = _s02().textures(29.70, w, h)['u_ui']
    a = 1 - ease((t - T_PTS) / 1.3)
    if a > 0:
        img = _S[key].copy()
        img.putalpha(img.getchannel('A').point(lambda v: int(v * a)))
    else:
        img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fk = ('f', s)
    if fk not in _S: _S[fk] = ImageFont.truetype(FONT, int(19 * s))
    f = _S[fk]
    cam, look, fov, focus, aper, roll = camera(t)
    sp = specials(t)
    words = [('you', 30.25, 45.9, (1, 1)), ('me', 32.9, 40.3, (-1, 1)), ('love', 32.9, 44.2, (1, -1))]
    for (txt, t0, t1, (sx, sy)), p in zip(words, sp):
        if hide: break
        if not t0 <= t < t1: continue
        al = min(1., (t - t0) / .3, (t1 - t) / .3)
        if txt == 'love': al *= .55 + .45 * (math.floor(t * 9) % 3 != 0)
        pr = project(p, cam, look, math.radians(fov), math.radians(roll), w, h)
        if pr is None: continue
        x, y = pr
        if not (-40 < x < w + 40 and -40 < y < h + 40): continue
        ex, ey = x + sx * 34 * s, y - sy * 34 * s
        col = (236, 232, 222, int(235 * al)) if txt != 'love' else (240, 200, 160, int(235 * al))
        d.line([(x + sx * 8 * s, y - sy * 8 * s), (ex, ey)], fill=col, width=max(1, int(1.3 * s)))
        tw = d.textlength(txt, font=f)
        d.text((ex + 6 * s if sx > 0 else ex - 6 * s - tw, ey - 12 * s), txt, font=f, fill=col)
    return {'u_ui': img}
