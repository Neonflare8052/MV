#version 330
// t05 · EIN DOS TROIS NE FEM LIU (2:38.9–2:41.6)
// 2D, layered in depth: six geometric bearers lift one person in six held, slow-motion stages;
// ahead on the horizon the guillotine, above it a blazing sun that is the gap ring.
// Ends with a dolly zoom (subject fixed, background looming) and a blur.
uniform vec2  u_res;
uniform float u_time, u_weight;
uniform float u_h;        // height of the carried body
uniform float u_crouch;   // bearers: 1 deep crouch .. 0 standing
uniform float u_arm;      // 0 hands under the body .. 1 hands overhead
uniform float u_walk;     // walking phase (stage six)
uniform float u_cz;       // camera z (dolly)
uniform float u_f;        // focal length (zoom)
uniform float u_blur;
uniform float u_black;
uniform float u_rays;
out vec4 fragColor;

#define PI 3.14159265
const vec3 CREAM=vec3(.93,.89,.8), BLACK=vec3(.055,.05,.045), RED=vec3(.72,.1,.08);
const float CY=2.5, YOFF=.2, F0=1.1;
float PX;

float h12(vec2 p){ vec3 p3=fract(vec3(p.xyx)*.1031); p3+=dot(p3,p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }
float vn(vec2 p){ vec2 i=floor(p),f=fract(p); f=f*f*(3.-2.*f);
  return mix(mix(h12(i),h12(i+vec2(1,0)),f.x),mix(h12(i+vec2(0,1)),h12(i+vec2(1,1)),f.x),f.y); }
float sdCap(vec2 p, vec2 a, vec2 b, float ra, float rb){ vec2 pa=p-a, ba=b-a; float h=clamp(dot(pa,ba)/max(dot(ba,ba),1e-9),0.,1.); return length(pa-ba*h)-mix(ra,rb,h); }
float sdBox(vec2 p, vec2 b){ vec2 d=abs(p)-b; return length(max(d,0.))+min(max(d.x,d.y),0.); }
float sdTrap(vec2 p, float r1, float r2, float he){          // bottom half-width r1, top r2, half height he
  vec2 k1=vec2(r2,he), k2=vec2(r2-r1,2.*he); p.x=abs(p.x);
  vec2 ca=vec2(p.x-min(p.x,(p.y<0.)?r1:r2),abs(p.y)-he);
  vec2 cb=p-k1+k2*clamp(dot(k1-p,k2)/dot(k2,k2),0.,1.);
  float s=(cb.x<0.&&ca.y<0.)?-1.:1.;
  return s*sqrt(min(dot(ca,ca),dot(cb,cb)));
}
float fillA(float d, float s){ return 1.-smoothstep(-PX,PX,d*s); }

// camera: position (0, CY, u_cz), looking down +z, level; YOFF shifts the horizon up a little
vec3 proj(vec3 w){ float s=u_f/(w.z-u_cz); return vec3(w.x*s,(w.y-CY)*s+YOFF,s); }

void layer(inout vec3 col, vec3 c, float a){ col=mix(col,c,clamp(a,0.,1.)); }

// ---- the sun: the gap ring, with constructivist rays ----
void sky(vec2 uv, inout vec3 col){
  vec2 sc=vec2(0.,YOFF+.19*u_f);
  vec2 d=uv-sc; float r=length(d), a=atan(d.y,d.x);
  col=mix(vec3(.95,.9,.82),vec3(.7,.5,.4),smoothstep(.05,.9,r));
  float rays=step(.5,fract(a/(2.*PI)*16.+u_time*.02));
  col=mix(col,col*vec3(1.,.55,.45),rays*u_rays*.55*smoothstep(.08,.3,r));
  float R=.07*u_f;
  float gap=radians(26.);
  float ga=-PI*.5;                                            // the gap looks down at them
  float dd=abs(mod(a-ga+PI,2.*PI)-PI);
  float ring=abs(r-R)-.022*u_f;
  if(dd<gap) ring=1e3;
  col+=vec3(1.,.8,.55)*exp(-max(ring,0.)*45./u_f)*.25;      // glare
  layer(col,RED*.9,fillA(ring-.006*u_f,1.));
  layer(col,vec3(1.25,1.15,1.),fillA(ring,1.));
}

// ---- ground: a black road with red lines converging on the guillotine ----
void ground(vec2 uv, inout vec3 col){
  if(uv.y>YOFF) return;
  float zr=u_f*CY/(YOFF-uv.y);                                // distance from camera
  float x=uv.x*zr/u_f;
  vec3 g=mix(BLACK*1.2,CREAM*.55,exp(-zr*.03)*0.+smoothstep(30.,80.,zr)*.6);
  float road=step(abs(x),1.6);
  float line=1.-smoothstep(.02,.02+zr*.004,abs(abs(x)-1.6));
  float mid=(1.-smoothstep(.02,.02+zr*.004,abs(x)))*step(.5,fract((zr+u_cz)*.35));
  g=mix(g,vec3(.12,.1,.09),road);
  g=mix(g,RED,max(line,mid*.8));
  col=g;
}

// ---- the guillotine, far away on the road ----
void guillotine(vec2 uv, inout vec3 col){
  vec3 b=proj(vec3(0.,0.,16.)); float s=b.z; vec2 q=(uv-b.xy)/s;
  float posts=min(sdBox(q-vec2(-.75,2.1),vec2(.09,2.1)),sdBox(q-vec2(.75,2.1),vec2(.09,2.1)));
  float beam=sdBox(q-vec2(0.,4.25),vec2(1.,.12));
  float lunette=max(sdBox(q-vec2(0.,1.05),vec2(.7,.22)),-(length(q-vec2(0.,1.05))-.14));
  float base=sdBox(q-vec2(0.,.08),vec2(1.3,.08));
  layer(col,BLACK,fillA(min(min(posts,beam),min(lunette,base)),s));
  // the red wedge
  vec2 w=q-vec2(0.,3.55);
  float wedge=max(sdBox(w,vec2(.66,.45)),-(w.y+.45-(w.x+.66)*.55));
  layer(col,RED,fillA(wedge,s));
}

// ---- one bearer, seen from behind ----
void bearer(vec2 uv, inout vec3 col, float x, float z, float side, bool red, float seed){
  float walk=u_walk*(1.+.1*seed);
  z+=.05*sin(walk*2.*PI+seed*3.);
  float bob=.03*abs(sin(walk*2.*PI+seed*3.));
  vec3 b=proj(vec3(x,bob,z)); float s=b.z; vec2 q=(uv-b.xy)/s;
  float c=u_crouch*(.9+.2*seed);
  float hip=.9-.38*c;
  float spread=.12+.1*c;
  // shadow on the road
  layer(col,BLACK*.6,fillA(length((q-vec2(0.,.0))*vec2(1.,5.))-.35,s)*.6);
  float legs=min(sdCap(q,vec2(-.09,hip),vec2(-spread,0.),.075,.06),sdCap(q,vec2(.09,hip),vec2(spread,0.),.075,.06));
  float sh=hip+.55-.12*c;
  float torso=sdTrap(q-vec2(0.,(hip+sh)*.5),.15,.25,(sh-hip)*.5);
  vec2 hc=vec2(0.,sh+.2-.05*c);
  float head=length(q-hc)-.12;
  // arms: reach under the body, or up to hold it overhead / on the shoulder
  vec3 hand=vec3(-side*.12,u_h-.1,z+.1);
  if(u_arm>.5) hand=vec3(-side*.14,u_h-.08,z);
  vec3 hp=proj(hand); vec2 hq=(hp.xy-b.xy)/s;
  vec2 shI=vec2(-side*.2,sh-.04), shO=vec2(side*.2,sh-.04);
  float arms=min(sdCap(q,shI,hq,.055,.045),sdCap(q,shO,mix(hq,hq+vec2(side*.1,-.05),.6),.055,.045));
  float body=min(min(legs,torso),min(head,arms));
  layer(col,BLACK,fillA(body,s));
  layer(col,red?RED:BLACK*1.8,fillA(torso+.02,s));
  // a sliver of light on the head (Schlemmer's sphere)
  layer(col,CREAM,fillA(max(head,-(length(q-hc-vec2(0.,-.03))-.12)),s)*.9);
}

// ---- the person being carried: lying on the back, head towards the blade ----
void carried(vec2 uv, inout vec3 col){
  vec3 a=proj(vec3(0.,u_h,2.9)), b=proj(vec3(0.,u_h,5.3)), hd=proj(vec3(0.,u_h+.03,5.55));
  float d=sdCap(uv,a.xy,b.xy,.17*a.z,.17*b.z);
  float head=length(uv-hd.xy)-.12*hd.z;
  float o=min(d,head);
  layer(col,BLACK,1.-smoothstep(-PX,PX,o-.006*a.z));
  layer(col,CREAM,1.-smoothstep(-PX,PX,o));
  // folds of the shroud
  float fold=abs(fract((uv.y-a.y)/(.05*a.z))-.5);
  layer(col,CREAM*.8,(1.-smoothstep(-PX,PX,d))*step(fold,.08)*.5);
}

vec3 scene(vec2 uv){
  vec3 col;
  sky(uv,col);
  ground(uv,col);
  guillotine(uv,col);
  // back to front
  bearer(uv,col,-.58,5.4,-1.,true,.3);  bearer(uv,col,.58,5.4,1.,false,.7);
  bearer(uv,col,-.58,4.2,-1.,false,.5); bearer(uv,col,.58,4.2,1.,true,.1);
  carried(uv,col);
  bearer(uv,col,-.58,3.0,-1.,true,.9);  bearer(uv,col,.58,3.0,1.,false,.4);
  // slow dust in the light
  vec2 g=floor(uv*60.+vec2(0.,u_time*.8)); float h=h12(g);
  col=mix(col,CREAM,step(.993,h)*.5*(1.-smoothstep(.0,.3,length(fract(uv*60.+vec2(0.,u_time*.8))-.5))));
  // printed-paper grain
  col*=.94+.08*vn(uv*400.);
  return col;
}

void main(){
  vec2 uv=(gl_FragCoord.xy-.5*u_res)/u_res.y;
  PX=1./u_res.y;
  vec3 col;
  if(u_blur>.001){
    col=vec3(0.);
    for(int i=0;i<28;i++){ float a=float(i)*2.3999; vec2 o=vec2(cos(a),sin(a))*sqrt((float(i)+.5)/28.)*u_blur*.05;
      col+=scene(uv+o); }
    col/=28.;
  } else col=scene(uv);
  col=mix(col,vec3(0.),u_black);
  fragColor=vec4(col*u_weight,1.);
}
