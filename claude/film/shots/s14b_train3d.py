"""s14b · 2:42.632–2:46.6  the census cards go by train — real 3D scene, flat 2D rendering (sketch; replaces s14's factory).
Everything is simple solids (boxes, cylinders, spheres, one prism) hit analytically per pixel, shaded in two or three flat
tones by face orientation, outlined, no gradients.  Depth of field and motion blur come from jittering the lens and time
across subframes (render with --sub 12 or more).

If I can            the card, close: backlit holes, then lit — VOLKSZÄHLUNG 1939. It sits in the side of the first wagon
                    behind the locomotive; the train is running.
give them all the   the camera pulls off the wagon, rises above the engine and turns round: wagons full of cards wind back
                    across the plain to the horizon.
EXECUTION           every card, the same hole, red: a red thread down the whole train. The engine blasts smoke; it is at
                    the gate.
Then I can          the camera comes down and round to the front: the wall rushes past, out of focus; the factory ahead."""
import math
import importlib.util
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

_P = Path(__file__).resolve().parent / 's14_cards.py'
_spec = importlib.util.spec_from_file_location('s14src_b', _P); S14 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(S14)

T0, T1, T2, T3 = S14.T0, S14.T1, S14.T2, S14.T3
clamp, ease, lerp = S14.clamp, S14.ease, S14.lerp

# ---- sizes (metres, roughly); the cards are symbolic giants: 2 m wide
KC = 2.0 / S14.CW                       # s14 card units -> metres
CWm, CHm = S14.CW * KC, S14.CH * KC
LOCO_L, WAG_L, GAPm = 13., 10., .6
NC, NLP, NPO = 44, 30, 24               # cars (0 = engine), engine puffs, poles
SPEED = 12.
TG = 165.99                             # the engine's front passes the gate
CARD_X, CARD_Y = -1.1, 2.85             # our card on wagon 1, side +N


# ---- the track: straight through the gate (z = 0) and before it, winding further back
def g(z):
    u = -z - 90.
    if u <= 0: return 0.
    a = 75. * S14.ease(u / 220.)
    return a * math.sin(u / 60.) + 25. * S14.ease(u / 400.) * math.sin(u / 23. + 1.)


_Z = np.arange(-1600., 120., .5)
_X = np.array([g(z) for z in _Z])
_S = np.concatenate([[0.], np.cumsum(np.hypot(np.diff(_X), np.diff(_Z)))])
S_GATE = float(np.interp(0., _Z, _S))


def track(s):
    x = float(np.interp(s, _S, _X)); z = float(np.interp(s, _S, _Z)); return x, z


def frame(s, half=3.9):
    """position and heading of something centred at arc length s (heading from its two bogies)"""
    xa, za = track(s - half); xb, zb = track(s + half)
    x, z = track(s)
    return x, z, math.atan2(xb - xa, zb - za)


def front(t): return S_GATE + SPEED * (t - TG)


def car_s(i, t):
    f = front(t)
    if i == 0: return f - LOCO_L / 2
    return f - LOCO_L - GAPm - WAG_L / 2 - (i - 1) * (WAG_L + GAPm)


def basis(psi):
    T = np.array([math.sin(psi), 0., math.cos(psi)]); N = np.array([math.cos(psi), 0., -math.sin(psi)])
    return T, N


def to_world(i, t, local):
    x, z, psi = frame(car_s(i, t), 5.5 if i == 0 else 3.9)
    T, N = basis(psi)
    return np.array([x, 0., z]) + T * local[0] + np.array([0., local[1], 0.]) + N * local[2], T, N


SRC_HEAD = S14.SRC.split('// ---- the factory')[0]
SRC = SRC_HEAD + r'''
uniform vec3 u_cam, u_fwd, u_right, u_up;
uniform float u_tanh, u_focus, u_ap, u_t2;
uniform vec4 u_car[%NC%];
uniform vec4 u_lp[%NLP%];
uniform vec3 u_pole[%NPO%];
const int NC=%NC%, NLP=%NLP%, NPO=%NPO%;
const float KC=%KC%, WAG_L=%WAGL%;
const vec3 SKY=vec3(.46,.43,.39), GRD=vec3(.15,.14,.128), GFAR=vec3(.21,.2,.185);
const vec3 LDIR=normalize(vec3(-.55,.75,-.4));
float FP;                                    // world size of one pixel per metre of distance

struct Hit { float t; vec3 n; int mat; float edge; vec3 q; float id; };
// mat: 1 ground, 2 ink solid, 3 wall, 4 wagon side (cards), 5 smoke, 6 window, 7 doorway

float h11(float x){ return fract(sin(x*127.1)*43758.5453); }

bool box(vec3 ro, vec3 rd, vec3 c, vec3 h, out float t, out vec3 n, out vec3 q){
  vec3 o=ro-c; vec3 m=1./rd; vec3 k=abs(m)*h; vec3 t1=-m*o-k, t2=-m*o+k;
  float tN=max(max(t1.x,t1.y),t1.z), tF=min(min(t2.x,t2.y),t2.z);
  if(tN>tF||tN<0.) return false;
  t=tN; n=-sign(rd)*step(t1.yzx,t1.xyz)*step(t1.zxy,t1.xyz); q=o+rd*t; return true;
}
float boxEdge(vec3 q, vec3 h, vec3 n){                    // distance to the nearest edge of the face hit
  vec3 d=h-abs(q); vec3 an=abs(n);
  return an.x>.5?min(d.y,d.z):(an.y>.5?min(d.x,d.z):min(d.x,d.y));
}
float cyl(vec3 ro, vec3 rd, vec3 a, vec3 b, float ra, out vec3 n, out float ed){
  vec3 ba=b-a, oc=ro-a;
  float baba=dot(ba,ba), bard=dot(ba,rd), baoc=dot(ba,oc);
  float k2=baba-bard*bard, k1=baba*dot(oc,rd)-baoc*bard, k0=baba*dot(oc,oc)-baoc*baoc-ra*ra*baba;
  float h=k1*k1-k2*k0;
  if(h<0.) return -1.;
  h=sqrt(h);
  float t=(-k1-h)/k2, y=baoc+t*bard;
  if(y>0.&&y<baba){ n=(oc+t*rd-ba*y/baba)/ra; float L=sqrt(baba);
    ed=min(ra*(1.-sqrt(max(0.,1.-dot(n,-rd)*dot(n,-rd))))*3., min(y,baba-y)/L); return t; }
  t=(((y<0.)?0.:baba)-baoc)/bard;
  if(abs(k1+k2*t)<h){ n=ba*sign(y)/sqrt(baba); vec3 p=oc+t*rd; ed=ra-length(p-ba*dot(p,ba)/baba); return t; }
  return -1.;
}
float sph(vec3 ro, vec3 rd, vec3 c, float r){
  vec3 oc=ro-c; float b=dot(oc,rd), cc=dot(oc,oc)-r*r, h=b*b-cc;
  if(h<0.) return -1.; return -b-sqrt(h);
}
// a sawtooth roof tooth: x0..x1, rising from (z0, yb) to (z1, yb+h), vertical at z1
bool tooth(vec3 ro, vec3 rd, float x0, float x1, float z0, float z1, float yb, float h, out float t, out vec3 n, out float ed){
  vec3 N[5]; float D[5];
  N[0]=vec3(-1,0,0); D[0]=-x0; N[1]=vec3(1,0,0); D[1]=x1; N[2]=vec3(0,-1,0); D[2]=-yb; N[3]=vec3(0,0,1); D[3]=z1;
  vec3 sn=normalize(vec3(0.,1.,-h/(z1-z0))); N[4]=sn; D[4]=dot(sn,vec3(0.,yb,z0));
  float tN=-1e9, tF=1e9; vec3 nn=vec3(0);
  for(int i=0;i<5;i++){
    float den=dot(N[i],rd), dist=dot(N[i],ro)-D[i];
    if(abs(den)<1e-8){ if(dist>0.) return false; continue; }
    float tt=-dist/den;
    if(den<0.){ if(tt>tN){ tN=tt; nn=N[i]; } } else tF=min(tF,tt);
  }
  if(tN>tF||tN<0.) return false;
  t=tN; n=nn;
  vec3 p=ro+rd*t;                                           // edge: distance to the neighbouring planes
  ed=1e3;
  for(int i=0;i<5;i++){ float dd=-(dot(N[i],p)-D[i]); if(dot(N[i],nn)<.99) ed=min(ed,dd/max(length(cross(N[i],nn)),.2)); }
  return true;
}

void take(inout Hit H, float t, vec3 n, int mat, float edge, vec3 q, float id){
  if(t>0.&&t<H.t){ H.t=t; H.n=n; H.mat=mat; H.edge=edge; H.q=q; H.id=id; }
}

// ---- one car, in its own frame: x along the track (forward), y up, z to the side (+z: the camera's side)
void traceCar(int i, vec3 ro, vec3 rd, inout Hit H){
  vec4 C=u_car[i];
  vec3 T=vec3(sin(C.z),0.,cos(C.z)), N=vec3(cos(C.z),0.,-sin(C.z));
  vec3 o=ro-vec3(C.x,0.,C.y);
  vec3 lo=vec3(dot(o,T),o.y,dot(o,N)), ld=vec3(dot(rd,T),rd.y,dot(rd,N));
  // bound
  vec3 oc=lo-vec3(0.,2.8,0.); float b=dot(oc,ld), cc=dot(oc,oc)-64.;
  if(cc>0.&&(b>0.||b*b<cc)) return;
  float t; vec3 n, q; float ed;
  #define WN(nl) (nl.x*T+vec3(0.,nl.y,0.)+nl.z*N)
  if(i==0){                                                    // the engine
    if(box(lo,ld,vec3(0.,1.35,0.),vec3(6.3,.25,1.35),t,n,q)) take(H,t,WN(n),2,boxEdge(q,vec3(6.3,.25,1.35),n),q,0.);
    t=cyl(lo,ld,vec3(-2.3,2.95,0.),vec3(6.,2.95,0.),1.3,n,ed); take(H,t,WN(n),2,ed,vec3(0),0.);
    t=cyl(lo,ld,vec3(4.6,3.8,0.),vec3(4.6,5.6,0.),.42,n,ed); take(H,t,WN(n),2,ed,vec3(0),0.);
    t=cyl(lo,ld,vec3(4.6,5.45,0.),vec3(4.6,5.8,0.),.62,n,ed); take(H,t,WN(n),2,ed,vec3(0),0.);
    t=cyl(lo,ld,vec3(1.6,3.9,0.),vec3(1.6,4.75,0.),.55,n,ed); take(H,t,WN(n),2,ed,vec3(0),0.);
    if(box(lo,ld,vec3(-4.3,3.3,0.),vec3(1.7,1.95,1.45),t,n,q)){
      int m=(abs(n.z)>.5&&abs(q.x+.1)<.75&&q.y>.35&&q.y<1.3)?6:2;
      take(H,t,WN(n),m,boxEdge(q,vec3(1.7,1.95,1.45),n),q,0.); }
    if(box(lo,ld,vec3(-4.3,5.35,0.),vec3(2.,.12,1.65),t,n,q)) take(H,t,WN(n),2,boxEdge(q,vec3(2.,.12,1.65),n),q,0.);
    if(box(lo,ld,vec3(6.45,1.3,0.),vec3(.2,.35,1.5),t,n,q)) take(H,t,WN(n),2,boxEdge(q,vec3(.2,.35,1.5),n),q,0.);
    for(int s=-1;s<=1;s+=2){
      for(int w=0;w<3;w++){ float wx=-2.2+2.15*float(w);
        t=cyl(lo,ld,vec3(wx,1.,float(s)*1.2),vec3(wx,1.,float(s)*1.42),.98,n,ed); take(H,t,WN(n),2,ed,vec3(0),0.); }
      t=cyl(lo,ld,vec3(5.2,.55,float(s)*1.1),vec3(5.2,.55,float(s)*1.3),.52,n,ed); take(H,t,WN(n),2,ed,vec3(0),0.);
    }
    return;
  }
  vec3 hb=vec3(WAG_L*.5,1.65,1.5);
  if(box(lo,ld,vec3(0.,2.75,0.),hb,t,n,q)){
    int m=abs(n.z)>.5?4:2;
    take(H,t,WN(n),m,boxEdge(q,hb,n),q+vec3(0.,2.75,0.),float(i));
  }
  if(box(lo,ld,vec3(0.,4.5,0.),vec3(WAG_L*.5+.15,.12,1.65),t,n,q)) take(H,t,WN(n),2,boxEdge(q,vec3(WAG_L*.5+.15,.12,1.65),n),q,0.);
  if(box(lo,ld,vec3(0.,.95,0.),vec3(WAG_L*.5-.4,.2,1.2),t,n,q)) take(H,t,WN(n),2,boxEdge(q,vec3(WAG_L*.5-.4,.2,1.2),n),q,0.);
  if(i<5){
    for(int s=-1;s<=1;s+=2) for(int w=0;w<4;w++){
      float wx=(w<2?-1.:1.)*(w==0||w==3?3.9:2.6);
      t=cyl(lo,ld,vec3(wx,.5,float(s)*1.1),vec3(wx,.5,float(s)*1.3),.45,n,ed); take(H,t,WN(n),2,ed,vec3(0),0.);
    }
  } else if(box(lo,ld,vec3(0.,.5,0.),vec3(4.3,.45,1.1),t,n,q)) take(H,t,WN(n),2,boxEdge(q,vec3(4.3,.45,1.1),n),q,0.);
}

// ---- a wagon's side: a rack of 4 x 3 cards in a black frame
vec3 wagonSide(vec3 q, float side, float id, float fp, out float isCard){
  isCard=0.;
  float u=side>0.?-q.x:q.x, v=q.y;
  vec3 c=vec3(.03,.028,.027);
  float col=floor((u+4.4)/2.2), row=floor((v-1.35)/1.);
  if(col<0.||col>3.||row<0.||row>2.) return c;
  vec2 cc=vec2(-4.4+2.2*(col+.5),1.35+(row+.5));
  vec2 l=(vec2(u,v)-cc)/KC;                                   // in s14 card units
  float save=PXw; PXw=fp/KC;
  vec4 cd=card(l/vec2(CW,CH)+.5,vec2(id*10.+col,row+(side>0.?0.:3.)),0.,0.);
  PXw=save;
  if(cd.a>0.) isCard=1.;
  c=mix(c,cd.rgb,cd.a);
  if(u_mark>0.&&abs(l.x)<CW*.5&&abs(l.y)<CH*.5){             // the hole: at least a clear red dot at any distance
    float dd=length(l-HOLEC)*KC;
    c=mix(c,BLOOD*(1.3+2.*u_flash),fill((dd-max(.03,fp*2.4))/KC));
    c+=BLOOD*(.4+2.5*u_flash)*exp(-dd/(fp*2.));
  }
  return c;
}

vec3 tone(vec3 n, vec3 a, vec3 b, vec3 c){
  if(n.y>.6) return a;
  return dot(n,LDIR)>0.?b:c;
}

void main(){
  // lens and pixel jitter per subframe (depth of field, antialiasing)
  float j1=h11(u_time*91.7), j2=h11(u_time*53.3+.3), j3=h11(u_time*17.1+.7), j4=h11(u_time*33.9+.1);
  vec2 uv=(gl_FragCoord.xy+vec2(j3,j4)-.5-.5*u_res)/u_res.y;
  FP=2.*u_tanh/u_res.y;
  vec3 rd0=normalize(u_fwd+2.*u_tanh*(uv.x*u_right+uv.y*u_up));
  float la=6.2832*j1, lr=sqrt(j2)*u_ap;
  vec3 ro=u_cam+(u_right*cos(la)+u_up*sin(la))*lr;
  vec3 fpnt=u_cam+rd0*u_focus/dot(rd0,u_fwd);
  vec3 rd=normalize(fpnt-ro);
  PXw=1e-3;

  Hit H; H.t=1e5; H.mat=0; H.n=vec3(0.,1.,0.); H.edge=1e3; H.q=vec3(0); H.id=0.;
  float t; vec3 n, q; float ed;
  // ground
  if(rd.y<0.){ t=-ro.y/rd.y; take(H,t,vec3(0.,1.,0.),1,1e3,ro+rd*t,0.); }
  // the train
  for(int i=0;i<NC;i++) traceCar(i,ro,rd,H);
  // the wall and the gate
  vec3 hw=vec3(150.,3.,.35);
  if(box(ro,rd,vec3(-160.5,3.,0.),hw,t,n,q)) take(H,t,n,3,boxEdge(q,hw,n),q+vec3(-160.5,3.,0.),0.);
  if(box(ro,rd,vec3(160.5,3.,0.),hw,t,n,q)) take(H,t,n,3,boxEdge(q,hw,n),q+vec3(160.5,3.,0.),0.);
  for(int s=-1;s<=1;s+=2){ vec3 hp=vec3(.8,4.5,.8), cp=vec3(float(s)*11.3,4.5,0.);
    if(box(ro,rd,cp,hp,t,n,q)) take(H,t,n,3,boxEdge(q,hp,n),q+cp,1.);
    vec3 hs=vec3(.35,3.,20.), cs=vec3(float(s)*10.6,3.,20.);
    if(box(ro,rd,cs,hs,t,n,q)){ vec3 wq=q+cs; take(H,t,n,3,boxEdge(q,hs,n),vec3(wq.z,wq.y,wq.x),0.); } }
  // the factory: a hall with a sawtooth roof, a doorway for the line, chimneys
  vec3 hh=vec3(34.,7.,25.), ch=vec3(-6.,7.,72.);
  if(box(ro,rd,ch,hh,t,n,q)){ vec3 wq=q+ch; int m=n.z<-.5?((abs(wq.x)<5.5&&wq.y<9.)?7:8):2; take(H,t,n,m,boxEdge(q,hh,n),wq,0.); }
  for(int k=0;k<5;k++){ float z0=47.+10.*float(k);
    if(tooth(ro,rd,-40.,28.,z0,z0+10.,14.,4.5,t,n,ed)) take(H,t,n,2,ed,vec3(0),0.); }
  vec3 hb2=vec3(9.,4.,11.), cb2=vec3(40.,4.,58.);
  if(box(ro,rd,cb2,hb2,t,n,q)) take(H,t,n,2,boxEdge(q,hb2,n),q,0.);
  vec3 CHM[3]; CHM[0]=vec3(-28.,40.,78.); CHM[1]=vec3(-12.,46.,92.); CHM[2]=vec3(10.,36.,66.);
  for(int k=0;k<3;k++){
    t=cyl(ro,rd,vec3(CHM[k].x,0.,CHM[k].z),CHM[k],2.1-.2*float(k),n,ed); take(H,t,n,2,ed,vec3(0),0.);
    t=cyl(ro,rd,CHM[k]-vec3(0.,1.,0.),CHM[k],2.6-.2*float(k),n,ed); take(H,t,n,2,ed,vec3(0),0.);
    for(int p=0;p<12;p++){                                     // their smoke, drifting off
      float P=.45, ph=u_time/P+float(k)*.31, id=floor(ph)-float(p), age=(float(p)+fract(ph))*P;
      vec3 c=CHM[k]+vec3(2.2*age+.8*sin(id*1.3),3.2*age,.9*age+.7*cos(id*2.1));
      float r=2.+1.1*age+.6*h11(id+float(k));
      t=sph(ro,rd,c,r); take(H,t,vec3(0.,1.,0.),5,1e3,vec3(0),0.);
    }
  }
  // poles
  for(int k=0;k<NPO;k++){
    vec3 P=u_pole[k];
    t=cyl(ro,rd,vec3(P.x,0.,P.y),vec3(P.x,8.2,P.y),.16,n,ed); take(H,t,n,2,ed,vec3(0),0.);
    vec3 ha=vec3(.1,.1,1.2); vec3 T=vec3(sin(P.z),0.,cos(P.z));
    if(box(ro,rd,vec3(P.x,8.1,P.y),vec3(1.1*abs(T.z)+.1,.1,1.1*abs(T.x)+.1),t,n,q)) take(H,t,n,2,1e3,q,0.);
  }
  // the engine's smoke
  for(int k=0;k<NLP;k++){ vec4 P=u_lp[k]; if(P.w<=0.) continue;
    t=sph(ro,rd,P.xyz,P.w); take(H,t,vec3(0.,1.,0.),5,1e3,vec3(0),0.); }

  // ---- flat shading
  float fp=FP*H.t;
  vec3 col=SKY;
  bool cardPix=false;
  if(H.mat==1){
    vec3 p=ro+rd*H.t;
    float gx=0.;
    col=GRD;
    // the line: bed, sleepers, rails (lateral distance from the track, measured across z)
    float x0=%GX%;
    float d=abs(p.x-x0)*%GC%;
    col=mix(col,vec3(.17,.16,.15),fill((d-2.3)/max(fp,1e-4)*PXw));
    float sl=abs(fract(p.z/.8)-.5)*.8;
    col=mix(col,vec3(.09,.085,.08),fill((max(d-1.35,.12-sl))/max(fp,1e-4)*PXw)*(1.-smoothstep(.05,.3,fp)));
    col=mix(col,vec3(.03),fill((abs(d-.75)-max(.05,fp*.5))/max(fp,1e-4)*PXw));
    // furrows on the plain, off the line
    float fu=abs(fract(p.x/6.)-.5)*6.;
    col*=1.-.12*fill((fu-max(.06,fp*.5))/max(fp,1e-4)*PXw)*step(3.,d)*(1.-smoothstep(.2,1.,fp));
    col=mix(col,GFAR,1.-exp(-H.t/450.));
  } else if(H.mat==2||H.mat==7||H.mat==8){
    col=H.mat==7?vec3(0.):H.mat==8?vec3(.06,.056,.052):tone(H.n,vec3(.045,.042,.04),vec3(.014,.013,.012),vec3.004,.004,.004));
  } else if(H.mat==3){
    col=tone(H.n,vec3(.3,.28,.255),vec3(.2,.188,.17),vec3(.12,.113,.103));
    if((abs(H.n.z)>.5||abs(H.n.x)>.5)&&H.id<.5){                                // brick courses
      float by=abs(fract(H.q.y/.45)-.5)*.45, bx=abs(fract(H.q.x/1.3+.5*floor(H.q.y/.45))-.5)*1.3;
      col*=1.-.25*fill((min(by,bx)-max(.02,fp*.5))/max(fp,1e-4)*PXw);
    }
  } else if(H.mat==4){
    float isc;
    col=wagonSide(H.q,sign(dot(H.n,vec3(cos(u_car[int(H.id)].z),0.,-sin(u_car[int(H.id)].z)))),H.id,fp,isc);
    cardPix=isc>0.;
  } else if(H.mat==5) col=vec3(.02,.019,.018);
  else if(H.mat==6) col=vec3(.5,.46,.4);
  // outlines
  if(H.mat>=2&&H.mat!=5) col=mix(col,vec3(.02),1.-smoothstep(.5,1.3,H.edge/max(fp,1e-5)));
  if(H.mat>=2&&H.mat!=1) col=mix(col,GFAR,(1.-exp(-H.t/650.))*.8);
  col*=cardPix?1.:mix(.03,1.,u_lit);
  col+=vec3(1.,.9,.85)*u_flash*.05;
  vec4 ui=texture(u_ui,gl_FragCoord.xy/u_res);
  col=mix(col,ui.rgb,ui.a);
  fragColor=vec4(col*u_weight,1.);
}
'''
for k, v in {'%NC%': str(NC), '%NLP%': str(NLP), '%NPO%': str(NPO), '%KC%': '%.5f' % KC, '%WAGL%': '%.3f' % WAG_L}.items():
    SRC = SRC.replace(k, v)
POST = dict(u_bloom=.08, u_ca=.003)


# the track's lateral position in the shader: g(z) as a GLSL expression, and a slope correction
_G = '(( -p.z-90.)>0.?(75.*smoothstep(0.,1.,clamp((-p.z-90.)/220.,0.,1.))*sin((-p.z-90.)/60.)+25.*smoothstep(0.,1.,clamp((-p.z-90.)/400.,0.,1.))*sin((-p.z-90.)/23.+1.)):0.)'
_GC = '(1./sqrt(1.+pow((%s-%s)/.5,2.)))' % (_G, _G.replace('p.z', '(p.z+.5)'))
SRC = SRC.replace('%GX%', _G).replace('%GC%', _GC)
SRC = SRC.replace('vec3.004,.004,.004))', 'vec3(.004,.004,.004))')


# ---- the camera: keys in the frame of our card (along the train, out from the side, up) or aimed at world points
def card_world(t):
    p, T, N = to_world(1, t, (CARD_X, CARD_Y, 1.5))
    return p, T, N


def cam_keys(t):
    C, T, N = card_world(t)
    back = np.array([*track(car_s(1, t) - 170.)]); back = np.array([back[0], 0., back[1]])
    fac = np.array([6., 15., 88.])
    return [  # time, (along, out, up) from the card, target, aperture
        (T0, (0, .5, 0), C, .004),
        (T0 + .65, (0, 2.6, 0), C, .01),
        (T1 + .55, (-2., 9., 1.5), C + T * 4. + np.array([0., .5, 0.]), .01),
        (T2 - .12, (9., 16., 30.), back, .0),
        (T2 + .2, (9., 16., 30.), back, .0),
        (T3, (19., 3.6, 1.4), fac, .12),
        (T3 + .6, (19., 3.6, 1.4), fac, .12),
    ], C, T, N


def camera(t):
    K, C, T, N = cam_keys(t)
    if t <= K[0][0]: k0, k1, x = K[0], K[0], 0.
    elif t >= K[-1][0]: k0, k1, x = K[-1], K[-1], 0.
    else:
        for j in range(len(K) - 1):
            if K[j][0] <= t < K[j + 1][0]: k0, k1 = K[j], K[j + 1]; break
        x = (t - k0[0]) / (k1[0] - k0[0])
    a = ease(x)
    if k0[0] == T2 + .2:                    # down first, on the outside; in to the line last
        ab, ac = ease((x - .1) / .55), ease(x / .6)
    else: ab = ac = a
    o = [lerp(k0[1][0], k1[1][0], a), lerp(k0[1][1], k1[1][1], ab), lerp(k0[1][2], k1[1][2], ac)]
    pos = C + T * o[0] + N * o[1] + np.array([0., o[2], 0.])
    tgt = k0[2] + (k1[2] - k0[2]) * a
    return pos, tgt, lerp(k0[3], k1[3], a)


def puffs(t):
    out = []
    P = .1
    for k in range(NLP):
        te = (math.floor(t / P) - k) * P
        age = t - te
        if age < 0: continue
        chim, T, N = to_world(0, te, (4.6, 5.9, 0.))
        boost = math.exp(-((te - T2 - .08) / .12) ** 2) if te >= T2 - .1 else 0.
        c = chim + np.array([.6, 3.2 + 7. * boost, -.8]) * age
        r = (.5 + 1.25 * age) * (1. + 1.8 * boost)
        out.append((float(c[0]), float(c[1]), float(c[2]), float(r)))
    while len(out) < NLP: out.append((0., 0., 0., 0.))
    return out


def poles():
    out = []
    s_end = S_GATE - 12.
    for k in range(NPO):
        s = s_end - k * 26.
        x, z, psi = frame(s)
        T, N = basis(psi)
        out.append((x - N[0] * 6.5, z - N[2] * 6.5, psi))
    return out


POLES = poles()


def params(t):
    pos, tgt, ap = camera(t)
    f = tgt - pos; f /= np.linalg.norm(f)
    r = np.cross(f, [0., 1., 0.]); r /= np.linalg.norm(r)
    u = np.cross(r, f)
    sh = .004 * math.exp(-(t - T2) * 18) if 0 <= t - T2 < .35 else 0.
    f = f + r * sh * math.sin(t * 97) + u * sh * math.cos(t * 83); f /= np.linalg.norm(f)
    cars = []
    for i in range(NC):
        x, z, psi = frame(car_s(i, t), 5.5 if i == 0 else 3.9)
        cars.append((x, z, psi, 0.))
    return dict(u_cam=tuple(map(float,pos)), u_fwd=tuple(map(float,f)), u_right=tuple(map(float,r)), u_up=tuple(map(float,u)), u_tanh=math.tan(math.radians(21)),
                u_focus=float(np.linalg.norm(tgt - pos)), u_ap=ap, u_car=cars, u_lp=puffs(t), u_pole=POLES,
                u_lit=ease((t - T0 - .3) / .35), u_backRed=1. - ease((t - T0 - .1) / .5),
                u_mark=1. if t >= T2 else 0., u_flash=math.exp(-(t - T2) * 14) if t >= T2 else 0., u_t2=T2)


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
    return {'u_face': S14.FACE, 'u_ui': _UI[key]}
