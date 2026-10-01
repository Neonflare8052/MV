"""s14c · 2:42.632–2:46.1  a person, a card, a line, a point.  (plan A; replaces s14's factory)
One 3D scene rendered flat.  The camera is its eye: no motion blur, no depth of field, straight moves.

If I can            a card, flat, seen square-on; lit from behind, its holes are a little person in red light.
                    Lit: VOLKSZÄHLUNG 1939 — the person is just holes now.
give them all the   still square-on and flat, pulling back: the card sits in the side of the wagon behind the engine; the
                    train runs.  Then the flat picture opens into depth: up and round, looking back — wagons full of cards
                    wind to the horizon; far off each card is a white point, the train a line.
                    The black mouth of the factory passes over the camera.
EXECUTION           inside, dark.  Every card: the same hole, red.  Rows and rows of red points; through the door the red
                    thread runs back to the horizon.  The doors close: only the points."""
import math
import importlib.util
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

_D = Path(__file__).resolve().parent
def _load(f, n):
    sp = importlib.util.spec_from_file_location(n, _D / f); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
S14 = _load('s14_cards.py', 's14src_c')
B = _load('s14b_train3d.py', 's14b_c')

T0, T1, T2, T3 = S14.T0, S14.T1, S14.T2, S14.T3
clamp, ease, lerp = S14.clamp, S14.ease, S14.lerp
B.TG = 165.832                        # the camera crosses the factory door at 165.02
NC, KC = B.NC, B.KC
DOOR_W, DOOR_H, HALL_H = 9., 26., 34.

_HEAD = S14.SRC.split('// ---- the factory')[0]
_MID = B.SRC[B.SRC.index('uniform vec3 u_cam'):B.SRC.index("// ---- a wagon's side")]

SRC = _HEAD + _MID + r'''
uniform float u_clk, u_door, u_fogOff, u_skip;
const float DW=%DW%, DH=%DH%, HH=%HH%;

// the punched person: a pictogram on the 80 x 12 grid (x in row heights, y up from the bottom row)
float person(vec2 p, float v){
  float d=length(p-vec2(0.,10.3))-.8;
  d=min(d,sdRBox(p-vec2(0.,7.4),vec2(.85,1.75),.3));
  float sw=(v-.5)*1.2;
  d=min(d,sdCap(p,vec2(-.42,5.6),vec2(-.6-sw*.5,.6),.38));
  d=min(d,sdCap(p,vec2(.42,5.6),vec2(.6+sw*.5,.6),.38));
  d=min(d,sdCap(p,vec2(-1.05,8.8),vec2(-1.45-sw,5.9),.32));
  d=min(d,sdCap(p,vec2(1.05,8.8),vec2(1.45+sw*.3,5.9),.32));
  return d;
}

// a card: paper, printed face, holes (the person + a little data), the mark
vec4 cardP(vec2 uv, vec2 id, float fp){
  if(uv.x<0.||uv.x>1.||uv.y<0.||uv.y>1.) return vec4(0.);
  if(uv.x*CW/CH+(1.-uv.y)<.11) return vec4(0.);
  float edge=min(min(uv.x,1.-uv.x)*CW,min(uv.y,1.-uv.y)*CH);
  vec3 paper=PAPER*(.985+.03*vn(uv*vec2(300.,130.)));
  float ink=texture(u_face,uv).a;
  vec3 c=mix(paper,INK,ink*.9)*mix(.03,1.,u_lit);
  float pxc=fp/KC;                                             // a pixel in s14 card units
  c*=mix(.25,1.,smoothstep(pxc*.6,pxc*1.8,edge));
  float cx=(uv.x-.035)/COLW, ry=(.80-uv.y)/ROWH;
  float col=floor(cx), row=floor(ry);
  if(col>=0.&&col<80.&&row>=0.&&row<12.){
    float cellPx=COLW*CW/pxc;
    float vis=smoothstep(.7,1.8,cellPx);                        // too far to see a hole: no hole
    vec2 f=vec2(fract(cx)-.5,fract(ry)-.5)*vec2(COLW*CW/CH,ROWH);
    float dh=sdRBox(f,vec2(.2*COLW*CW/CH,.3*ROWH),.07*COLW*CW/CH);
    float hole=(1.-smoothstep(-pxc/CH,pxc/CH,dh))*vis;
    float ox=22.+floor(h12(id*3.1)*30.);
    vec2 pp=vec2((col+.5-ox)*COLW*CW/(ROWH*CH),11.5-(row+.5));
    float punched=step(person(pp,h12(id*7.7)),0.);
    punched=max(punched,step(h12(id*1.37+vec2(col*.71,row*1.9)),.025));
    bool mark=abs(col-%MC%.)<.1&&abs(row-%MR%.)<.1&&u_mark>0.;
    vec3 backL=mix(vec3(1.,.82,.62),BLOOD,u_backRed)*2.2*(1.-u_lit);
    if(mark) return vec4(mix(c,BLOOD*(1.6+2.*u_flash),max(hole,.0)),1.);
    if(punched>0.) return vec4(mix(c,backL,hole),1.-hole*(1.-step(.001,length(backL))));
  }
  return vec4(c,1.);
}

vec3 wagonSide2(vec3 q, float side, float id, float fp){
  float u=side>0.?-q.x:q.x, v=q.y;
  vec3 c=vec3(.03,.028,.027);
  float col=floor((u+4.4)/2.2), row=floor((v-1.35)/1.);
  if(col<0.||col>3.||row<0.||row>2.) return c;
  vec2 cc=vec2(-4.4+2.2*(col+.5),1.35+(row+.5));
  vec2 l=(vec2(u,v)-cc)/KC;
  float save=PXw; PXw=fp/KC;
  vec4 cd=cardP(l/vec2(CW,CH)+.5,vec2(id*10.+col,row+(side>0.?0.:3.)),fp);
  PXw=save;
  c=mix(c,cd.rgb,cd.a);
  if(u_mark>0.&&abs(l.x)<CW*.5&&abs(l.y)<CH*.5){               // the mark: at least a clear red point at any distance
    float dd=length(l-HOLEC)*KC;
    c=mix(c,BLOOD*(1.5+2.5*u_flash),fill((dd-max(.03,fp*2.))/KC));
    c+=BLOOD*(.35+2.*u_flash)*exp(-dd/(fp*1.6));
  }
  return c;
}

vec3 tone(vec3 n, vec3 a, vec3 b, vec3 c){ if(n.y>.6) return a; return dot(n,LDIR)>0.?b:c; }
bool inHall(vec3 p){ return abs(p.x)<70.&&p.y<HH&&p.z>.5&&p.z<160.; }

void main(){
  float j3=h11(u_time*17.1+.7), j4=h11(u_time*33.9+.1);
  vec2 uv=(gl_FragCoord.xy+vec2(j3,j4)-.5-.5*u_res)/u_res.y;
  FP=2.*u_tanh/u_res.y;
  vec3 rd=normalize(u_fwd+2.*u_tanh*(uv.x*u_right+uv.y*u_up));
  vec3 ro=u_cam+rd*u_skip; vec3 hp0=vec3(0);
  PXw=1e-3;

  Hit H; H.t=1e7; H.mat=0; H.n=vec3(0.,1.,0.); H.edge=1e3; H.q=vec3(0); H.id=0.;
  float t; vec3 n, q; float ed;
  if(rd.y<0.){ t=-ro.y/rd.y; take(H,t,vec3(0.,1.,0.),1,1e3,ro+rd*t,0.); }
  for(int i=0;i<NC;i++) traceCar(i,ro,rd,H);
  // the factory's face: a black wall with a huge door; the doors; chimneys on the roof
  vec3 hf=vec3((70.-DW)*.5,HH*.5,.5);
  for(int s=-1;s<=1;s+=2){ vec3 c=vec3(float(s)*(DW+70.)*.5,HH*.5,0.);
    if(box(ro,rd,c,hf,t,n,q)) take(H,t,n,2,boxEdge(q,hf,n),q+c,0.);
    vec3 hd=vec3(DW*.5,DH*.5,.3), cd=vec3(float(s)*(DW*1.5-DW*u_door),DH*.5,1.2);
    if(u_door>0.&&box(ro,rd,cd,hd,t,n,q)) take(H,t,n,9,boxEdge(q,hd,n),q+cd,0.); }
  vec3 hl=vec3(DW,(HH-DH)*.5,.5), cl=vec3(0.,(HH+DH)*.5,0.);
  if(box(ro,rd,cl,hl,t,n,q)) take(H,t,n,2,boxEdge(q,hl,n),q+cl,0.);
  vec3 hr=vec3(70.,.5,80.), cr=vec3(0.,HH,80.);
  if(box(ro,rd,cr,hr,t,n,q)) take(H,t,n,2,boxEdge(q,hr,n),q+cr,0.);
  vec3 CHM[3]; CHM[0]=vec3(-34.,70.,50.); CHM[1]=vec3(-8.,78.,80.); CHM[2]=vec3(26.,66.,40.);
  for(int k=0;k<3;k++){
    t=cyl(ro,rd,vec3(CHM[k].x,HH,CHM[k].z),CHM[k],2.6,n,ed); take(H,t,n,2,ed,vec3(0),0.);
    for(int p=0;p<10;p++){
      float P=.5, ph=u_clk/P+float(k)*.31, id=floor(ph)-float(p), age=(float(p)+fract(ph))*P;
      vec3 c=CHM[k]+vec3(2.5*age+.8*sin(id*1.3),3.5*age,.9*age);
      t=sph(ro,rd,c,2.4+1.3*age+.6*h11(id+float(k))); take(H,t,vec3(0.,1.,0.),5,1e3,vec3(0),0.);
    }
  }
  for(int k=0;k<NPO;k++){
    vec3 P=u_pole[k];
    t=cyl(ro,rd,vec3(P.x,0.,P.y),vec3(P.x,8.2,P.y),.16,n,ed); take(H,t,n,2,ed,vec3(0),0.);
    vec3 T=vec3(sin(P.z),0.,cos(P.z));
    if(box(ro,rd,vec3(P.x,8.1,P.y),vec3(1.1*abs(T.z)+.1,.1,1.1*abs(T.x)+.1),t,n,q)) take(H,t,n,2,1e3,q,0.);
  }
  for(int k=0;k<NLP;k++){ vec4 P=u_lp[k]; if(P.w<=0.) continue;
    t=sph(ro,rd,P.xyz,P.w); take(H,t,vec3(0.,1.,0.),5,1e3,vec3(0),0.); }

  // the wagons standing in the dark hall, row on row
  for(int k=0;k<8;k++){
    float xr=(k<4?-1.:1.)*12.*float(k%4+1);
    vec3 hr2=vec3(1.5,1.65,73.5), cr2=vec3(xr,2.75,81.5);
    if(box(ro,rd,cr2,hr2,t,n,q)){
      vec3 w=q+cr2; float a=w.z-8., idx=floor(a/10.6), u=a-idx*10.6-5.3;
      int m=(abs(n.x)>.5&&abs(u)<5.)?4:2;
      take(H,t,n,m,1e3,vec3(u,w.y,0.),-1.-(float(k)*20.+idx));
    }
  }
  // ---- flat shading
  H.t+=u_skip;
  float fp=FP*H.t;
  vec3 col=SKY, hp=u_cam+rd*min(H.t,1e5);
  bool glow=false;
  if(H.mat==1){
    col=GRD;
    vec3 p=hp;
    float x0=%GX%;
    float d=abs(p.x-x0)*%GC%;
    col=mix(col,vec3(.12,.113,.103),fill((d-2.3)/max(fp,1e-4)*PXw));
    float sl=abs(fract(p.z/.8)-.5)*.8;
    col=mix(col,vec3(.07,.066,.06),fill((max(d-1.35,.12-sl))/max(fp,1e-4)*PXw)*(1.-smoothstep(.05,.3,fp)));
    col=mix(col,vec3(.02),fill((abs(d-.75)-max(.05,fp*.5))/max(fp,1e-4)*PXw));
    float fu=abs(fract(p.x/6.)-.5)*6.;
    col*=1.-.12*fill((fu-max(.06,fp*.5))/max(fp,1e-4)*PXw)*step(3.,d)*(1.-smoothstep(.2,1.,fp));
    col=mix(col,GFAR,1.-exp(-max(H.t-u_fogOff,0.)/450.));
  } else if(H.mat==2||H.mat==9){
    col=tone(H.n,vec3(.045,.042,.04),vec3(.014,.013,.012),vec3(.004));
  } else if(H.mat==4){
    if(H.id<0.) col=wagonSide2(H.q,sign(H.n.x),-H.id+50.,fp);
    else col=wagonSide2(H.q,sign(dot(H.n,vec3(cos(u_car[int(H.id)].z),0.,-sin(u_car[int(H.id)].z)))),H.id,fp);
    glow=true;
  } else if(H.mat==5) col=vec3(.02,.019,.018);
  else if(H.mat==6) col=vec3(.5,.46,.4);
  if(H.mat>=2&&H.mat!=5&&H.mat!=4) col=mix(col,vec3(.004),1.-smoothstep(.5,1.3,H.edge/max(fp,1e-5)));
  if(H.mat>=2) col=mix(col,GFAR,(1.-exp(-max(H.t-u_fogOff,0.)/650.))*.8);
  // inside the factory: dark; the red points still burn
  bool camIn=inHall(u_cam);
  if(camIn){
    vec3 m=1./rd, o=u_cam-vec3(0.,HH*.5,80.5); vec3 k=abs(m)*vec3(70.,HH*.5,80.);
    float tx=min(min((-m*o+k).x,(-m*o+k).y),(-m*o+k).z);
    vec3 ex=ro+rd*tx;
    if(H.t>tx&&ex.z>1.) { col=vec3(.004); H.mat=0; }
  }
  if(H.mat!=0&&inHall(hp)){
    vec3 red=vec3(max(col.r-max(col.g,col.b)*1.6,0.)*1.6,0.,0.);
    col=col*(H.mat==4?.028:.012)+(H.mat==4?red*1.8:vec3(0.));
  }
  col*=H.mat==4?1.:mix(.03,1.,u_lit);
  col+=vec3(1.,.9,.85)*u_flash*.03*(camIn?0.:1.);
  vec4 ui=texture(u_ui,gl_FragCoord.xy/u_res);
  col=mix(col,ui.rgb,ui.a);
  fragColor=vec4(col*u_weight,1.);
}
'''
SRC = (SRC.replace('%DW%', '%.3f' % DOOR_W).replace('%DH%', '%.3f' % DOOR_H).replace('%HH%', '%.3f' % HALL_H)
       .replace('%MC%', str(S14.MARK[0])).replace('%MR%', str(S14.MARK[1])).replace('%GX%', B._G).replace('%GC%', B._GC))
POST = dict(u_bloom=.1, u_ca=.002)


# ---- the camera: keys as (focus point, direction, view height at the focus, tan of half the field of view);
#      a telephoto square-on view is the flat picture; it opens into depth by widening the lens as it comes in
TAN_FLAT = math.tan(math.radians(.3))
TAN_WIDE = math.tan(math.radians(23))


def _nrm(v): return v / np.linalg.norm(v)


def keys(t):
    C, T, N = B.card_world(t)
    Y = np.array([0., 1., 0.])
    def flat(F, hv): return (F, -N, hv, TAN_FLAT, None)
    def look(P, F): d = F - P; return (F, _nrm(d), 2 * np.linalg.norm(d) * TAN_WIDE, TAN_WIDE, P)
    bx, bz = B.track(B.car_s(1, t) - 150.); back = np.array([bx, 0., bz])
    bx2, bz2 = B.track(B.car_s(1, t) - 70.); back2 = np.array([bx2, 3., bz2])
    # the camera never turns round: it keeps looking back at the train and backs in through the door (|x| < DW/2)
    return [
        (T0, flat(C, .42)),
        (T0 + .62, flat(C, 1.3)),
        (T1 + .1, flat(C, 1.45)),
        (T1 + .5, flat(C + T * 8. + Y * 1.3, 11.)),
        (T1 + .85, flat(C + T * 8. + Y * 1.3, 11.5)),
        (164.5, look(C + T * 25. + N * 12. + Y * 17., back)),
        (164.86, look(C + T * 27. + N * .6 + Y * 15., back)),
        (T2, look(np.array([.6, 12.5, 5.]), back2)),
        (T3 + .2, look(np.array([.2, 11., 30.]), back2)),
    ]


def camera(t):
    K = keys(t)
    if t <= K[0][0]: k0 = k1 = K[0]; a = 0.
    elif t >= K[-1][0]: k0 = k1 = K[-1]; a = 0.
    else:
        for j in range(len(K) - 1):
            if K[j][0] <= t < K[j + 1][0]: k0, k1 = K[j], K[j + 1]; break
        a = ease((t - k0[0]) / (k1[0] - k0[0]))
    (F0, d0, h0, n0, P0), (F1, d1, h1, n1, P1) = k0[1], k1[1]
    if P0 is not None and P1 is not None:                     # two ordinary views: move the camera, swing the aim
        pos = P0 + (P1 - P0) * a
        d = _nrm(_nrm(d0) * (1 - a) + _nrm(d1) * a)
        return pos, d, n0, float(np.linalg.norm(F0 - P0))
    if P0 is None and P1 is not None:                         # flat -> depth: come straight in along the line of sight
        D0, D1 = h0 / (2 * n0), float(np.linalg.norm(F1 - P1))
        pos0 = F0 - _nrm(d0) * D0
        D = math.exp(lerp(math.log(D0), math.log(D1), a))
        pos = P1 + (pos0 - P1) * ((D - D1) / (D0 - D1))       # a straight path: it never sweeps through the factory
        F = F0 + (F1 - F0) * ease(clamp((a - .25) / .75))
        tn = math.exp(lerp(math.log(n0), math.log(n1), a))
        return pos, _nrm(F - pos), tn, D
    F = F0 + (F1 - F0) * a
    d = _nrm(d0 + (d1 - d0) * a)
    hv = math.exp(lerp(math.log(h0), math.log(h1), a))
    tn = math.exp(lerp(math.log(n0), math.log(n1), a))
    pos = F - d * hv / (2 * tn)
    return pos, d, tn, hv / (2 * tn)


def params(ts):
    t = round(ts * 60) / 60                      # its eye: no motion blur
    pos, f, tn, dist = camera(t)
    r = _nrm(np.cross(f, [0., 1., 0.])); u = np.cross(r, f)
    cars = []
    for i in range(NC):
        x, z, psi = B.frame(B.car_s(i, t), 5.5 if i == 0 else 3.9)
        cars.append((x, z, psi, 0.))
    return dict(u_cam=tuple(map(float, pos)), u_fwd=tuple(map(float, f)), u_right=tuple(map(float, r)), u_up=tuple(map(float, u)),
                u_tanh=tn, u_car=cars, u_lp=puffs(t), u_pole=POLES, u_clk=t,
                u_lit=ease((t - T0 - .3) / .35), u_backRed=1. - ease((t - T0 - .1) / .5),
                u_mark=1. if t >= T2 else 0., u_flash=math.exp(-(t - T2) * 14) if t >= T2 else 0.,
                u_door=0., u_fogOff=max(0., dist - 60.), u_skip=max(0., dist - 90.) if tn < .05 else 0.)


def puffs(t):
    # separate puffs, as in the flat side view: spaced wider than they grow, each its own size and drift
    out = []
    P = .2
    for k in range(B.NLP):
        n = math.floor(t / P) - k
        te = n * P
        age = t - te
        if age < 0 or age > 2.6: continue
        r1, r2, r3 = (math.sin(n * 12.9898 + j * 78.233) * 43758.5453 % 1. for j in range(3))
        chim, T, N = B.to_world(0, te, (4.6, 5.9, 0.))
        boost = math.exp(-((te - T2 - .08) / .12) ** 2) if te >= T2 - .1 else 0.
        rise = (3.2 + 1.4 * r1 + 6. * boost) * age - .25 * age * age
        c = chim + np.array([(.6 + 1.2 * (r2 - .5)) * age, rise, (-.4 + 1.2 * (r3 - .5)) * age])
        out.append((float(c[0]), float(c[1]), float(c[2]), float((.5 + .55 * age) * (.8 + .4 * r2) * (1. + 1.5 * boost))))
    while len(out) < B.NLP: out.append((0., 0., 0., 0.))
    return out


def _poles():
    out = []
    for k in range(B.NPO):
        s = B.S_GATE - 18. - k * 26.
        x, z, psi = B.frame(s)
        T, N = B.basis(psi)
        out.append((x - N[0] * 6.5, z - N[2] * 6.5, psi))
    return out


POLES = _poles()
_UI = {}


def textures(t, w, h):
    s = h / 1080
    txt = S14.typed('17. V. 1939', T0 + .7, t) if T0 + .7 <= t < T2 else ''
    key = (w, h, txt)
    if key not in _UI:
        _UI.clear()
        img = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
        if txt: d.text((70 * s, 60 * s), txt, font=ImageFont.truetype(S14.FONT, int(30 * s)), fill=(226, 222, 212, 255))
        _UI[key] = img
    return {'u_face': S14.FACE, 'u_ui': _UI[key]}
