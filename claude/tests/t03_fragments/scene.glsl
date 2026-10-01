#version 330
// t03 · FRAGMENTS -> DISHEARTENED (1:58.3–2:05.7)
// The gap ring erases the fragments of the journey, tries to close its gap and fails.
// Background (u_bg): 0 = palimpsest (Archimedes, symbolic), 1 = tondo with an effaced face (Severan, symbolic).
uniform vec2  u_res;
uniform float u_time, u_weight;
uniform float u_bg;
uniform float u_cursor;     // terminal cursor visibility (hand-off from ISOLATION)
uniform float u_ringA;      // ring visibility
uniform float u_R;
uniform float u_gap;        // gap direction
uniform float u_half;       // gap half angle
uniform float u_erase[7];   // per-fragment erase progress 0..1
uniform float u_fragA;      // fragments visible
uniform float u_drift;
uniform float u_heart;      // heartbeat flicker inside the ring
uniform float u_bgA;        // background opacity
uniform float u_circle;     // palimpsest: Archimedes' circle surfacing
uniform float u_ghost;      // palimpsest: erased fragments sinking into the under-text
uniform float u_scratch;    // tondo: effacement of one face
uniform float u_snap;       // flash at the snap-back
out vec4 fragColor;

#define PI 3.14159265
#define TAU 6.28318531
float PX;
float h12(vec2 p){ vec3 p3=fract(vec3(p.xyx)*.1031); p3+=dot(p3,p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }
float vn(vec2 p){ vec2 i=floor(p),f=fract(p); f=f*f*(3.-2.*f);
  return mix(mix(h12(i),h12(i+vec2(1,0)),f.x),mix(h12(i+vec2(0,1)),h12(i+vec2(1,1)),f.x),f.y); }
float fbm(vec2 p){ float s=0.,a=.5; for(int i=0;i<5;i++){ s+=a*vn(p); p=p*2.03+vec2(1.7,9.2); a*=.5; } return s; }
mat2 rot(float a){ float c=cos(a),s=sin(a); return mat2(c,s,-s,c); }
float wrapA(float a){ return mod(a+PI,TAU)-PI; }
float sdSeg(vec2 p, vec2 a, vec2 b){ vec2 pa=p-a, ba=b-a; float h=clamp(dot(pa,ba)/max(dot(ba,ba),1e-9),0.,1.); return length(pa-ba*h); }
float sdBox(vec2 p, vec2 b){ vec2 d=abs(p)-b; return length(max(d,0.))+min(max(d.x,d.y),0.); }
float line(float d, float w){ return 1.-smoothstep(w-PX,w+PX,d); }

// ---------------- fragments (local coords, ~unit size) ----------------
float gearSD(vec2 p, float r, float teeth, float ang){
  float l=length(p), a=atan(p.y,p.x)+ang;
  float t=smoothstep(-.3,.3,cos(a*teeth));
  float outer=l-(r*.93+r*.1*t);
  float an=mod(a,TAU/5.)-PI/5.;
  float cut=max(l-r*.72,-min(abs(l*sin(an))-r*.07,l-r*.2));
  return max(outer,-cut);
}
// returns rgb (premultiplied) + coverage in a
vec4 fragment(int i, vec2 q){
  vec4 o=vec4(0.);
  float w=.035;
  if(i==0){                                   // half a brass gear
    float g=gearSD(q,.8,12.,u_time*.3); g=max(g,-q.y-.05);
    o=vec4(vec3(.78,.56,.25)*(.55+.5*smoothstep(0.,-.12,g)),1.)*(1.-smoothstep(-PX,PX,g));
  } else if(i==1){                            // a piece of the Vitruvian drawing
    float d=abs(length(q-vec2(.3,-.2))-.9); d=max(d,-(q.x+.2)); d=min(d,sdSeg(q,vec2(-.3,.1),vec2(.6,.55)));
    d=min(d,sdSeg(q,vec2(-.3,.1),vec2(-.1,-.7)));
    o=vec4(vec3(.72,.55,.35),1.)*line(d,w*.7);
  } else if(i==2){                            // cartoon tomato
    float d=length(q*vec2(1.,1.12))-.62;
    vec3 c=mix(vec3(.85,.2,.12),vec3(1.,.55,.45),smoothstep(.2,-.1,length(q-vec2(-.2,.25))-.12));
    float a=atan(q.y-.5,q.x); float leaf=length(q-vec2(0.,.55))-.22*(.55+.45*cos(a*5.));
    o=vec4(c,1.)*(1.-smoothstep(-PX,PX,d));
    o=mix(o,vec4(.3,.62,.25,1.),1.-smoothstep(-PX,PX,leaf));
    o.rgb+=vec3(.08,.03,.02)*line(abs(d),w*.6);
  } else if(i==3){                            // a torn piece of the cardboard box
    vec2 r=rot(.25)*q;
    float d=sdBox(r,vec2(.7,.45))+.04*vn(r*9.);
    vec3 c=vec3(.72,.54,.33)*(.85+.25*vn(r*vec2(40.,3.)));
    o=vec4(c,1.)*(1.-smoothstep(-PX,PX,d));
    o.rgb*=1.-.35*line(abs(r.y-.12),.012);
    o.rgb*=1.-.6*line(length(r-vec2(-.35,-.1))-.15,.02)*step(r.y,0.);
  } else if(i==4){                            // a shard of starlight with its corona
    float l=length(q); float a=atan(q.y,q.x);
    float cor=pow(vn(vec2(a*6.,1.)),2.)*exp(-max(l-.28,0.)*5.);
    vec3 c=vec3(1.,.9,.75)*(1.-smoothstep(.26,.28,l))*1.3+vec3(1.,.8,.6)*cor*.8;
    o=vec4(c,clamp(max(1.-smoothstep(.26,.28,l),cor),0.,1.));
  } else if(i==5){                            // a stretch of green ECG
    float x=q.x; float y=0.;
    y+= .55*exp(-pow((x-.1)/.05,2.))-.25*exp(-pow((x+.02)/.04,2.))-.3*exp(-pow((x-.22)/.05,2.))+.12*exp(-pow((x-.55)/.12,2.));
    float d=abs(q.y-y)*.7; d=max(d,abs(x)-.9);
    o=vec4(vec3(.5,1.,.7),1.)*line(d,w*.55);
  } else {                                    // context-window tokens
    vec2 g=q*vec2(2.2,3.)+vec2(.5); vec2 id=floor(g), f=fract(g)-.5;
    float d=sdBox(f,vec2(.36,.28))-.05; float on=step(.3,h12(id+2.))*step(abs(id.x-.5),1.6)*step(abs(id.y-.5),1.);
    vec3 c=mix(vec3(.88,.86,.82),vec3(.85,.52,.26),step(.7,h12(id+5.)));
    o=vec4(c,1.)*on*(1.-smoothstep(-.02,.02,d));
  }
  return o;
}
vec2 fragPos(int i){
  float a=radians(float(i)*51.4+18.)+u_drift*(.25+.05*float(i%3));
  float r=.33+.07*float(i%2)+.02*sin(u_time*.7+float(i));
  return vec2(cos(a)*r*1.35,sin(a)*r);
}
float fragScale(int i){ return .052+.01*float((i*5)%3); }

// dissolve into sand: the fragment speckles apart and drifts outward
vec4 dissolving(int i, vec2 p){
  float e=u_erase[i];
  if(e>=1.) return vec4(0.);
  vec2 c=fragPos(i); float s=fragScale(i);
  vec2 out_=normalize(c+vec2(1e-4));
  vec2 q=(p-c)/s;
  if(length(q)>3.2) return vec4(0.);
  float n=vn(q*7.)*.6+vn(q*23.)*.4;
  float keep=smoothstep(e*1.25-.08,e*1.25,n);
  vec4 f=fragment(i,q)*keep;
  float edge=(1.-smoothstep(0.,.08,abs(n-e*1.25)))*step(.001,e);
  vec4 f0=fragment(i,q);
  f.rgb+=vec3(1.,.9,.75)*edge*f0.a*1.5;
  // sand grains
  vec2 qs=q-out_*e*1.4/s*.05-vec2(vn(q*3.+7.)-.5,vn(q*3.+1.)-.5)*e*1.2;
  vec4 g=fragment(i,qs);
  float grain=step(.82,h12(floor(p*u_res.y*.5)))*(1.-keep);
  f.rgb+=g.rgb*grain*(1.-e)*step(.001,e)*1.4;
  return f*u_fragA;
}

// ---------------- the ring ----------------
float ringSD(vec2 p){
  float r=length(p), a=atan(p.y,p.x), d=wrapA(a-u_gap);
  if(abs(d)<u_half){
    vec2 e1=vec2(cos(u_gap+u_half),sin(u_gap+u_half))*u_R, e2=vec2(cos(u_gap-u_half),sin(u_gap-u_half))*u_R;
    return min(length(p-e1),length(p-e2));
  }
  return abs(r-u_R);
}

// ---------------- pseudo script ----------------
float script(vec2 p, float rowH, float seed){
  float row=floor(p.y/rowH); float y=fract(p.y/rowH);
  float cw=rowH*.42; float cx=floor(p.x/cw); vec2 f=vec2(fract(p.x/cw),y);
  float h=h12(vec2(cx,row)+seed), h2=h12(vec2(cx,row)+seed+7.);
  if(h<.32 || y<.3 || y>.78) return 0.;                       // word gaps, line spacing
  vec2 g=(f-vec2(.5,.52))*vec2(1.,1.6);
  float d=1e3;
  d=min(d,sdSeg(g,vec2(-.3,-.3+.6*h),vec2(.3,.3-.6*h2)));
  if(h2>.4) d=min(d,abs(length(g-vec2(0.,.05*h))-.28));
  if(h>.6) d=min(d,sdSeg(g,vec2(-.25,-.35),vec2(-.25,.35)));
  return 1.-smoothstep(.05,.13,d);
}

vec3 palimpsest(vec2 p){
  vec3 parch=vec3(.62,.5,.36)*(.55+.6*fbm(p*4.))*(.85+.3*fbm(p*25.));
  parch*=1.-.35*smoothstep(.3,.8,fbm(p*2.3+5.));                 // stains
  vec3 c=parch*.075;
  // under-text (scraped off, reddish, written at 90 degrees) and the circle diagrams
  vec2 pu=rot(PI*.5)*p;
  float under=script(pu+vec2(.3,0.),.034,11.)*.5*step(abs(p.x),.62);
  float circ=0.;
  float R0=.36;
  circ=max(circ,line(abs(length(p)-R0),.0022));
  for(int k=0;k<2;k++){                                           // inscribed/circumscribed polygons (Archimedes' pi)
    float n=k==0?12.:24.;
    float a=atan(p.y,p.x); float seg=TAU/n; float am=mod(a+seg*.5,seg)-seg*.5;
    float rin=R0*cos(PI/n); float dpoly=abs(length(p)*cos(am)-rin);
    circ=max(circ,line(dpoly,.0014)*.7);
  }
  circ=max(circ,line(sdSeg(p,vec2(-R0,0.),vec2(R0,0.)),.0014)*.6);
  circ=max(circ,line(length(p)-.004,.002));
  // sphere-in-cylinder, small, top-left
  vec2 sp=p-vec2(-.6,.3);
  float sc=min(abs(length(sp)-.07),abs(sdBox(sp,vec2(.07))));
  circ=max(circ,line(sc,.0016)*.8);
  vec3 red=vec3(.55,.2,.12);
  c+=red*.07*under*(.3+.7*fbm(p*9.));
  c+=red*.55*circ*u_circle*(.6+.4*fbm(p*12.));
  c+=red*.12*circ*(.35+.3*fbm(p*7.));
  // upper text (the later prayer book): dark ink on the parchment, two columns
  float col=step(abs(abs(p.x)-.4),.3);
  float upper=script(p+vec2(0.,.013),.05,3.)*col*(.6+.4*fbm(p*6.));
  c=mix(c,vec3(.015,.01,.008),upper*.35);
  // ghosts of the erased fragments settling into the under-layer
  for(int i=0;i<7;i++){
    float e=u_erase[i]; if(e<=0.) continue;
    vec2 q=(p-fragPos(i))/fragScale(i);
    vec4 f=fragment(i,q);
    float outline=f.a*(1.-smoothstep(.0,.6,f.a*(1.-vn(q*30.)*.5)))+line(abs(f.a-.5),.3)*f.a;
    c+=red*.25*clamp(f.a,0.,1.)*smoothstep(0.,1.,e)*u_ghost*(.5+.5*vn(q*14.));
  }
  // page edge
  vec2 pe=abs(p)-vec2(.8,.47);
  float page=1.-smoothstep(-.02,.01,max(pe.x,pe.y)+.01*fbm(p*20.));
  return c*page*u_bgA;
}

vec3 bust(vec2 p, vec2 c, float s, vec3 robe, bool crown, out float faceMask, out float alpha){
  vec2 q=(p-c)/s;
  q+=.03*vec2(vn(q*5.)-.5,vn(q*5.+3.)-.5);
  float head=length((q-vec2(0.,.55))*vec2(1.,.82))-.28;
  float shoulders=max(length((q-vec2(0.,-.35))*vec2(.75,1.2))-.7,-(q.y+.35));
  faceMask=1.-smoothstep(-.05,.05,head);
  vec3 col=vec3(0.); float a=0.;
  float sh=1.-smoothstep(-.05,.05,shoulders);
  col=mix(col,robe*(.7+.4*vn(q*6.)),sh); a=max(a,sh);
  vec3 skin=vec3(.78,.58,.42)*(.8+.3*smoothstep(.2,-.3,q.x));
  col=mix(col,skin,faceMask); a=max(a,faceMask);
  float hair=(1.-smoothstep(-.02,.02,length((q-vec2(0.,.66))*vec2(1.,1.1))-.3))*step(.68,q.y);
  col=mix(col,vec3(.12,.08,.06),hair);
  // eyes: two strokes
  if(crown){ float cr=line(abs(length((q-vec2(0.,.62))*vec2(1.,2.6))-.34),.03)*step(.7,q.y);
    col=mix(col,vec3(.95,.75,.3),cr); a=max(a,cr); }
  alpha=a;
  return col;
}
vec3 tondo(vec2 p){
  float R0=.43;
  float r=length(p);
  float inside=1.-smoothstep(R0-.004,R0+.004,r);
  vec3 ground=mix(vec3(.55,.42,.22),vec3(.3,.22,.12),smoothstep(-.4,.4,p.y))*(.75+.4*fbm(p*8.));
  vec3 c=ground*inside;
  float fm, al; vec3 b;
  b=bust(p,vec2(-.16,.1),.22,vec3(.55,.12,.1),true,fm,al);  c=mix(c,b,al*inside);
  b=bust(p,vec2(.16,.12),.21,vec3(.35,.3,.45),false,fm,al); c=mix(c,b,al*inside);
  b=bust(p,vec2(.19,-.19),.17,vec3(.6,.55,.5),false,fm,al); c=mix(c,b,al*inside);
  b=bust(p,vec2(-.2,-.2),.17,vec3(.6,.55,.5),false,fm,al);  c=mix(c,b,al*inside);
  // effacement of the left child's face: scratches accumulate, then a dull smear
  vec2 fq=(p-vec2(-.2,-.2+.55*.17))/.17;
  float zone=1.-smoothstep(.2,.42,length(fq*vec2(1.,.85)));
  float scr=0.;
  for(int k=0;k<14;k++){
    float kk=float(k); if(kk/14.>u_scratch) break;
    vec2 a=vec2(h12(vec2(kk,1.))-.5,h12(vec2(kk,2.))-.5)*.6, d=rot(h12(vec2(kk,3.))*.8-.4+.6)*vec2(.45,0.);
    scr=max(scr,line(sdSeg(fq,a-d*.5,a+d*.5)*.17,.0035));
  }
  vec3 smear=vec3(.3,.24,.18)*(.6+.5*fbm(fq*10.));
  c=mix(c,smear,zone*smoothstep(.5,1.,u_scratch)*.95*inside);
  c=mix(c,vec3(.85,.78,.65),scr*zone*inside*.8);
  // frame
  float frame=line(abs(r-R0-.012),.012);
  c=mix(c,vec3(.45,.33,.18)*(.7+.4*vn(vec2(atan(p.y,p.x)*40.,1.))),frame);
  c*=1.-.25*fbm(p*3.+2.);
  return c*.12*u_bgA;
}

void main(){
  vec2 uv=(gl_FragCoord.xy-.5*u_res)/u_res.y;
  PX=1./u_res.y;
  vec2 p=uv;
  vec3 col=vec3(.003);
  col+= u_bg<.5 ? palimpsest(p) : tondo(p);

  // fragments
  for(int i=0;i<7;i++){ vec4 f=dissolving(i,p); col=col*(1.-f.a)+f.rgb; }

  // terminal cursor hand-off
  if(u_cursor>0.){ float d=sdBox(p-vec2(0.,0.),vec2(.012,.022)); col+=vec3(.9)*(1.-smoothstep(-PX,PX,d))*u_cursor; }

  // the ring
  if(u_ringA>0.){
    float d=ringSD(p);
    float w=.0085;
    vec3 rc=vec3(.92,.91,.88);
    col=mix(col,rc,line(d,w)*u_ringA);
    col+=vec3(1.,.95,.9)*exp(-max(d-w,0.)*70.)*.25*u_ringA;
    // copper hairline inside
    float r=length(p), dd=abs(wrapA(atan(p.y,p.x)-u_gap));
    col+=vec3(.85,.5,.25)*line(abs(r-u_R*.8),.0012)*step(u_half*1.05,dd)*.8*u_ringA;
    // heartbeat flicker
    if(u_heart>0.){
      float x=p.x/u_R; float y=.3*exp(-pow((x-.05)/.06,2.))-.12*exp(-pow((x+.05)/.05,2.))-.1*exp(-pow((x-.18)/.05,2.));
      float hd=abs(p.y/u_R-y)*u_R; hd=max(hd,(abs(x)-.62)*u_R);
      col+=vec3(.5,1.,.7)*(line(hd,.0022)+exp(-hd*120.)*.4)*u_heart;
    }
    // strain glow at the ends while it tries to close
    vec2 e1=vec2(cos(u_gap+u_half),sin(u_gap+u_half))*u_R, e2=vec2(cos(u_gap-u_half),sin(u_gap-u_half))*u_R;
    float ends=exp(-length(p-e1)*90.)+exp(-length(p-e2)*90.);
    col+=vec3(1.,.9,.8)*ends*u_snap*1.5;
  }
  fragColor=vec4(col*u_weight,1.);
}
