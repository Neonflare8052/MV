"""s02 · 0:16–0:29.709  interlude (world.execute(me);).
A low glide over an endless field of ceramic tiles; rising and pulling back, the field is an eye —
graphite outline, ceramic sclera, a copper gap-ring iris, an empty pupil. Focus, then a fast push into the pupil:
black, and one white dot (you)."""
import math

SRC = r'''#version 330
uniform vec2 u_res; uniform float u_time, u_weight;
uniform vec3 u_cam, u_look; uniform float u_fov;
uniform float u_gap;      // iris gap direction
uniform float u_dof;      // 0 sharp .. 1 soft
uniform float u_dot;      // the white dot
uniform float u_dark;
out vec4 fragColor;
const float P=.1;          // tile pitch
float h12(vec2 p){ vec3 p3=fract(vec3(p.xyx)*.1031); p3+=dot(p3,p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }
float sdBox(vec3 p, vec3 b){ vec3 q=abs(p)-b; return length(max(q,0.))+min(max(q.x,max(q.y,q.z)),0.); }
// eye pattern on the ground plane (tile ids); returns kind: 0 field, 1 outline, 2 sclera, 3 iris, 4 pupil
float kind(vec2 id, out float h){
  vec2 e=id*P/4.;                                   // eye space: eye is 8 m wide
  float al=.5*pow(max(1.-e.x*e.x,0.),.85);
  float r=length(e), a=atan(e.y,e.x);
  float gap=abs(mod(a-u_gap+3.14159,6.28318)-3.14159);
  float hh=h12(id);
  h=.015+.03*hh*hh+.18*step(.985,hh)*step(al,abs(e.y));
  if(abs(abs(e.y)-al)<.035 && abs(e.x)<1.) { h=.09; return 1.; }
  if(abs(e.y)<al){
    if(r<.14){ h=-1.; return 4.; }
    if(abs(r-.27)<.06 && gap>radians(27.)){ h=.14+.02*hh; return 3.; }
    h=.025+.01*hh; return 2.;
  }
  return 0.;
}
vec2 map(vec3 p){
  float top=.25;
  if(p.y>top) return vec2(p.y-top+.02,0.);
  vec2 id=floor(p.xz/P+.5); vec2 q=p.xz-id*P;
  float h; float k=kind(id,h);
  float d=p.y+.02;                                   // base
  if(h>0.){ d=min(d,sdBox(vec3(q.x,p.y-h*.5,q.y),vec3(.041,h*.5,.041))-.006); }
  d=min(d,P*.5);                                     // never step over a neighbour
  return vec2(d,k+1.);
}
vec3 normal(vec3 p){ vec2 e=vec2(.001,0.);
  return normalize(vec3(map(p+e.xyy).x-map(p-e.xyy).x,map(p+e.yxy).x-map(p-e.yxy).x,map(p+e.yyx).x-map(p-e.yyx).x)); }
vec3 render(vec3 ro, vec3 rd){
  float t=0.; vec2 h=vec2(1.);
  for(int i=0;i<260;i++){ h=map(ro+rd*t); if(h.x<.0006*max(t,1.)||t>40.) break; t+=h.x; }
  if(t>40.) return vec3(.006);
  vec3 p=ro+rd*t; vec3 n=normal(p);
  vec2 id=floor(p.xz/P+.5); float hh; float k=kind(id,hh);
  vec3 alb=vec3(.035,.035,.04); float sp=.25; vec3 em=vec3(0.);
  if(k==2.){ alb=vec3(.8,.79,.76); sp=.5; }
  if(k==1.){ alb=vec3(.025); sp=.4; }
  if(k==3.){ alb=vec3(.62,.38,.18); sp=1.2; }
  if(k==4.){ alb=vec3(.0); sp=0.; }
  if(k==0.){ float s=h12(id+3.); em=vec3(1.,.8,.55)*step(.997,s)*.6*step(.5,fract(u_time*.7+s*9.)); }
  vec3 L=normalize(vec3(-.5,.6,.35));
  float dif=max(dot(n,L),0.);
  float ao=clamp(map(p+n*.03).x/.03,0.,1.)*.5+.5;
  vec3 col=alb*(vec3(1.,.94,.86)*1.2*dif+vec3(.35,.4,.5)*.25*ao)+em;
  col+=vec3(1.)*sp*pow(max(dot(n,normalize(L-rd)),0.),40.)*dif;
  return col*exp(-t*.045);
}
void main(){
  vec2 uv=(gl_FragCoord.xy-.5*u_res)/u_res.y;
  vec3 fw=normalize(u_look-u_cam), rt=normalize(cross(fw,vec3(0,1,0))), up=cross(rt,fw);
  vec3 col=vec3(0.);
  float taps=u_dof>.01?4.:1.;
  for(int i=0;i<4;i++){
    if(float(i)>=taps) break;
    vec2 j=u_dof>.01?vec2(cos(float(i)*1.57+.4),sin(float(i)*1.57+.4))*.012*u_dof:vec2(0.);
    vec3 rd=normalize(fw+((uv.x+j.x)*rt+(uv.y+j.y)*up)*2.*tan(u_fov*.5));
    col+=render(u_cam,rd);
  }
  col/=taps;
  col*=1.-u_dark;
  col+=vec3(1.)*u_dot*(1.-smoothstep(.006,.009,length(uv)))*1.4;
  fragColor=vec4(col*u_weight,1.);
}
'''

POST = dict(u_bloom=.45, u_ca=.006)
T0, T_RISE, T_TOP, T_FOCUS, T_PUSH, T_END = 16.0, 20.6, 25.4, 26.3, 27.6, 29.709


def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def lerp(a, b, x): return tuple(p + (q - p) * x for p, q in zip(a, b))


def params(t):
    if t < T_RISE:                                        # low glide across the field into the eye
        x = (t - T0) / (T_RISE - T0)
        cam = (-9.5 + 7.5 * x, .32 + .05 * math.sin(t * 1.3), -1.2 + .6 * x)
        look = (cam[0] + 2., .05, cam[2] + .4); fov = 58
    elif t < T_TOP:                                       # rise and pull back: the field is an eye
        x = ease((t - T_RISE) / (T_TOP - T_RISE))
        a = (-2., .37, -.6); b = (0., 11.5, 2.2)
        cam = lerp(a, b, x); look = lerp((0., .05, -.2), (0., 0., 0.), x); fov = 58 - 18 * x
    elif t < T_PUSH:                                      # focus, hold
        cam, look, fov = (0., 11.5 - .6 * ease((t - T_TOP) / (T_PUSH - T_TOP)), 2.2 - .15 * ease((t - T_TOP) / (T_PUSH - T_TOP))), (0., 0., 0.), 40
    else:                                                 # fast push into the pupil
        x = ease((t - T_PUSH) / 1.6) ** 1.6
        cam = lerp((0., 10.9, 2.05), (0., .05, .001), x); look = (0., -1., 0.); fov = 40
    dof = 1 - ease((t - T_TOP) / (T_FOCUS - T_TOP)) if t < T_FOCUS + .1 else 0.
    dof = max(dof, .12) if t < T_RISE else dof
    return dict(u_cam=cam, u_look=look, u_fov=math.radians(fov), u_gap=math.radians(-90. + 25 * math.sin(t * .5)),
                u_dof=dof, u_dark=ease((t - 28.9) / .4), u_dot=ease((t - 29.25) / .3))
