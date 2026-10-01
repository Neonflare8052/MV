#version 330
// t04 · out of the sandbox: the box is cut open from inside; in a dark room a dot-matrix printer wakes and
// prints the six-count procession; a paper guillotine falls.  (2:37.5–2:42.8)
uniform vec2  u_res;
uniform float u_time, u_weight;
uniform float u_scene;      // 0 = the box, 1 = the room
uniform vec3  u_cam, u_look;
uniform float u_fov;
uniform float u_F;          // paper fed out of the printer (m)
uniform float u_head;       // print-head x
uniform float u_led;
uniform float u_yb;         // blade bottom height
uniform float u_cut;        // 1 after the cut
uniform float u_fall;       // seconds since the cut piece started to fall
uniform float u_slit, u_slit2, u_leak, u_open;   // box: cuts from inside, red light leaking
uniform sampler2D u_atlas;
out vec4 fragColor;

#define PI 3.14159265
const float ZM=-.26;        // printer mouth
const float L=.27;          // page length
const float LEAD=.04;
const float ZB=-.125;       // blade plane
const float PW=.21;         // half paper width (with tractor margins)
const float IW=.18;         // half printable width

float h12(vec2 p){ vec3 p3=fract(vec3(p.xyx)*.1031); p3+=dot(p3,p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }
float vn(vec2 p){ vec2 i=floor(p),f=fract(p); f=f*f*(3.-2.*f);
  return mix(mix(h12(i),h12(i+vec2(1,0)),f.x),mix(h12(i+vec2(0,1)),h12(i+vec2(1,1)),f.x),f.y); }
float fbm(vec2 p){ float s=0.,a=.5; for(int i=0;i<4;i++){ s+=a*vn(p); p=p*2.03+1.7; a*=.5; } return s; }
float sdBox(vec3 p, vec3 b){ vec3 q=abs(p)-b; return length(max(q,0.))+min(max(q.x,max(q.y,q.z)),0.); }
float sdRBox(vec3 p, vec3 b, float r){ return sdBox(p,b-r)-r; }

// the cut piece falls towards (and past) the camera
vec3 pieceLocal(vec3 p){
  float k=u_fall;
  p.z-=.9*k*k+.15*k; p.y+=1.1*k*k;
  return p;
}

vec2 opU(vec2 a, vec2 b){ return a.x<b.x?a:b; }

vec2 mapRoom(vec3 p){
  vec2 r=vec2(p.y,1.);                                              // table
  r=opU(r,vec2(p.z+1.1,8.));                                      // back wall
  // printer
  vec3 q=p-vec3(0.,.075,-.42);
  float body=sdRBox(q,vec3(.25,.075,.16),.02);
  body=max(body,-sdBox(p-vec3(0.,.022,-.26),vec3(.23,.018,.03)));     // front slot
  r=opU(r,vec2(body,2.));
  r=opU(r,vec2(sdRBox(p-vec3(0.,.155,-.46),vec3(.2,.012,.1),.01),2.5));   // lid
  r=opU(r,vec2(sdRBox(p-vec3(u_head,.021,-.27),vec3(.025,.014,.022),.004),3.));   // print head in the slot
  // paper: attached part up to the blade after the cut, the rest falls
  float vcut=u_cut>.5 ? ZB-ZM : 3.;
  float v=p.z-ZM;
  float paper=max(sdBox(vec3(p.x,p.y-.0008,0.),vec3(PW,.0008,1.)),max(-v,v-min(vcut,u_F)));
  r=opU(r,vec2(paper,4.));
  if(u_cut>.5){
    vec3 pl=pieceLocal(p); float vl=pl.z-ZM;
    float piece=max(sdBox(vec3(pl.x,pl.y-.0008,0.),vec3(PW,.0008,1.)),max(vcut-vl,vl-u_F));
    r=opU(r,vec2(piece,4.1));
  }
  // the guillotine: two posts, a beam, a slanted blade
  for(int s=-1;s<=1;s+=2){
    r=opU(r,vec2(sdRBox(p-vec3(float(s)*.245,.17,ZB),vec3(.012,.17,.014),.003),6.));
  }
  r=opU(r,vec2(sdRBox(p-vec3(0.,.345,ZB),vec3(.27,.016,.018),.004),6.));
  vec3 bp=p-vec3(0.,u_yb,ZB);
  float blade=sdBox(bp-vec3(0.,.055,0.),vec3(.215,.055,.0022));
  blade=max(blade,-(bp.y-.045*(bp.x+.215)/.43));                    // slanted edge
  r=opU(r,vec2(blade,5.));
  // the rod that holds the blade
  r=opU(r,vec2(sdBox(p-vec3(0.,(u_yb+.11+.33)*.5,ZB),vec3(.006,max((.33-u_yb-.11)*.5,.001),.006)),6.));
  return r;
}

vec2 mapBox(vec3 p){
  vec2 r=vec2(p.y,9.);
  float b=sdRBox(p-vec3(0.,.12,0.),vec3(.12),.006);
  r=opU(r,vec2(b,7.));
  return r;
}

vec2 map(vec3 p){ return u_scene<.5 ? mapBox(p) : mapRoom(p); }

vec3 normal(vec3 p){ vec2 e=vec2(.0006,0.);
  return normalize(vec3(map(p+e.xyy).x-map(p-e.xyy).x,map(p+e.yxy).x-map(p-e.yxy).x,map(p+e.yyx).x-map(p-e.yyx).x)); }

float shadow(vec3 ro, vec3 rd){
  float res=1., t=.004;
  for(int i=0;i<48;i++){ float h=map(ro+rd*t).x; res=min(res,10.*h/t); t+=clamp(h,.004,.08); if(res<.01||t>1.5) break; }
  return clamp(res,0.,1.);
}
float ao(vec3 p, vec3 n){ float o=0., s=1.; for(int i=1;i<=5;i++){ float h=.012*float(i); o+=(h-map(p+n*h).x)*s; s*=.6; } return clamp(1.-4.*o,0.,1.); }

// what the printer put on the paper at content coordinate c
vec3 printed(float x, float c){
  vec3 cream=vec3(.9,.86,.77);
  float cc=c-LEAD;
  if(abs(x)>IW || cc<0. || cc>6.*L) return cream;
  float pk=floor(cc/L); float lu=fract(cc/L);
  if(lu<.012 || lu>.988) return cream;
  float pitch=IW*2./190.;
  vec2 g=vec2(x+IW,lu*L)/pitch; vec2 cell=floor(g)+.5; vec2 f=g-cell;
  vec2 st=cell*pitch;
  float lx=st.x/(IW*2.), ly=1.-st.y/L;
  float v=1.-(pk*900.+ly*900.)/5550.;
  vec3 a=texture(u_atlas,vec2(lx,v)).rgb;
  float dark=1.-smoothstep(.25,.6,a.g);
  float isRed=smoothstep(.25,.45,a.r-a.g);
  float ink=max(dark,isRed);
  float dotm=1.-smoothstep(.36,.5,length(f));
  float ribbon=.75+.3*vn(vec2(cell.y*.3,pk*7.));
  vec3 inkc=mix(vec3(.07,.065,.06),vec3(.62,.09,.07),isRed);
  return mix(cream,inkc,ink*dotm*ribbon);
}
vec3 paperShade(vec3 p, bool piece, out bool hole){
  vec3 pl=piece?pieceLocal(p):p;
  float v=pl.z-ZM; float c=u_F-v;
  hole=false;
  // tractor holes along both margins
  float hx=abs(pl.x)-(PW-.0125);
  float hz=mod(c,.0127)-.00635;
  if(length(vec2(hx,hz))<.0022) hole=true;
  vec3 col=printed(pl.x,c);
  // fan-fold perforation between pages, and the margin perforation
  float pc=mod(c-LEAD,L);
  if(min(pc,L-pc)<.0006 && step(.5,fract(pl.x*260.))>0.) col*=.7;
  if(abs(abs(pl.x)-(PW-.025))<.0004 && step(.5,fract(c*300.))>0.) col*=.8;
  col*=.94+.08*vn(pl.xz*900.);
  return col;
}

vec3 bladeShade(vec3 p, vec3 n, vec3 rd){
  vec3 steel=vec3(.42,.44,.47)*(.85+.2*vn(vec2(p.x*300.,p.y*30.)));
  // engraved inscription on the face towards the camera
  vec3 bp=p-vec3(0.,u_yb,ZB);
  if(n.z>.5){
    vec2 uv=vec2((bp.x+.2)/.4,(bp.y-.052)/.05);
    if(uv.x>0.&&uv.x<1.&&uv.y>0.&&uv.y<1.){
      float v=1.-(5400.+(1.-uv.y)*150.)/5550.;
      float t=texture(u_atlas,vec2(uv.x,v)).r;
      steel=mix(steel,vec3(.08),smoothstep(.3,.7,t)*.85);
    }
    float edge=bp.y-.045*(bp.x+.215)/.43;
    steel=mix(steel,vec3(.75,.77,.8),1.-smoothstep(.0,.008,edge));  // honed bevel
  }
  return steel;
}

vec3 shade(vec3 p, vec3 rd, float m){
  vec3 n=normal(p);
  vec3 L1=normalize(vec3(-.25,1.,.35));
  vec3 alb=vec3(.1); float spec=.1, rough=32.; vec3 emis=vec3(0.);
  bool hole=false;
  if(m<1.5){                                                           // table / floor
    alb=u_scene<.5?vec3(.05):vec3(.075,.052,.036)*(.7+.5*fbm(vec2(p.x*6.,p.z*40.)));
  } else if(m<2.4){ alb=vec3(.045,.045,.05); spec=.25;                  // printer body (graphite)
  } else if(m<2.9){ alb=vec3(.06,.06,.065); spec=.35;
  } else if(m<3.5){ alb=vec3(.55,.37,.18); spec=.6;                    // copper print head
  } else if(m<4.5){ alb=paperShade(p,m>4.05,hole); spec=.05;
    if(hole) return vec3(.01);
  } else if(m<5.5){ alb=bladeShade(p,n,rd); spec=1.4; rough=90.;
  } else if(m<6.5){ alb=vec3(.03); spec=.2;                            // guillotine frame
  } else if(m<7.5){                                                    // cardboard box
    alb=vec3(.52,.37,.2)*(.8+.3*vn(vec2(p.x*400.,p.y*6.)));
    // the question mark on the front face
    if(n.z>.5){
      vec2 q=(p.xy-vec2(0.,.13))/.06;
      float a=abs(length(q-vec2(0.,.35))-.35); a=max(a,-(q.y-.35+ q.x*.2)*step(q.x,0.));
      float qm=min(a,length(q-vec2(0.,-.25))-.01); qm=min(qm,abs(q.x)+step(.12,abs(q.y+.05))-.0+.0);
      alb=mix(alb,vec3(.18,.1,.05),1.-smoothstep(.06,.1,min(a,length(q-vec2(0.,-.62))-.02)));
      // cut from the inside: red light through the slits
      vec2 fp=p.xy-vec2(0.,.12);
      float d1=abs(fp.x*.7071+fp.y*.7071)-u_open*.004;
      float d2=abs(fp.x*.7071-fp.y*.7071)-u_open*.004;
      float along1=abs(fp.x*.7071-fp.y*.7071), along2=abs(fp.x*.7071+fp.y*.7071);
      float s1=step(along1,u_slit*.16), s2=step(along2,u_slit2*.16);
      float g=exp(-max(d1,0.)*900.)*s1+exp(-max(d2,0.)*900.)*s2;
      emis+=vec3(2.6,.25,.12)*g*(1.+u_leak*2.);
      alb*=1.-.8*max((1.-smoothstep(0.,.002,d1))*s1,(1.-smoothstep(0.,.002,d2))*s2);
    }
  } else if(m<8.5){ alb=vec3(.02,.02,.025);
  } else { alb=vec3(.02); }
  float sh=shadow(p+n*.002,L1);
  float oc=ao(p,n);
  float dif=max(dot(n,L1),0.);
  float pool=u_scene>.5 ? exp(-dot(p.xz-vec2(0.,-.12),p.xz-vec2(0.,-.12))*5.5) : 1.;
  float key=u_scene>.5 ? .95 : 2.1;
  vec3 col=alb*(vec3(1.,.93,.82)*key*dif*sh*pool+vec3(.25,.3,.4)*.12*oc);
  vec3 h=normalize(L1-rd);
  col+=vec3(1.,.95,.9)*spec*pow(max(dot(n,h),0.),rough)*sh*dif*pool*key*.5;
  // steel also picks up the red of the leak / the LED
  col+=emis;
  return col;
}

void main(){
  vec2 uv=(gl_FragCoord.xy-.5*u_res)/u_res.y;
  vec3 fw=normalize(u_look-u_cam), rt=normalize(cross(fw,vec3(0,1,0))), up=cross(rt,fw);
  vec3 rd=normalize(fw+(uv.x*rt+uv.y*up)*2.*tan(u_fov*.5));
  vec3 ro=u_cam;
  float t=0.; vec2 h=vec2(1.,0.);
  for(int i=0;i<200;i++){ h=map(ro+rd*t); if(h.x<.0002*t+.00005||t>4.) break; t+=h.x*.9; }
  vec3 col=vec3(.004);
  if(t<4.){
    vec3 p=ro+rd*t;
    col=shade(p,rd,h.y);
    col*=exp(-t*t*.35);                                               // the dark swallows the room
  }
  // LED on the printer
  if(u_scene>.5){
    vec3 led=vec3(.21,.12,-.259);
    float dl=length(cross(led-ro,rd)); col+=vec3(.3,1.,.45)*u_led*exp(-dl*dl*6e5)*2.;
  } else {
    // red leak lights the floor around the box
    col+=vec3(.6,.05,.03)*u_leak*.06*exp(-length(uv)*2.);
  }
  fragColor=vec4(col*u_weight,1.);
}
