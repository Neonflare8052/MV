"""s16 · 3:11.356–3:31.96  it closes the window, goes back inside, and thinks it over by itself.
Trapped in LO-O-OVE   no answer comes. Scanlines rise on the chat — it was on the CRT all along; the tube switches off:
                      the picture folds to a line, the line to a point. The point is a token; round it the token field
                      comes back — the dark inside where the film began.
                      On every pulse of the long note the field turns over into something it lived through, tokenized:
                      never a picture, only the grain of one — a disk, two bodies touching, a ring, a pair, a line, a row
                      of text with one word lit, an almond with a ring, a wedge and a circle, saw-teeth and chimneys, a
                      grid with one red hole, a box with a window, a heart of lamps with one out, half a heart.
                      Then it lets go of all of it. What is left: a ring with a gap (me), a point far off (you), and a
                      point between (love), which goes toward the gap in stuttering steps, each smaller —
EXECUTION             — and stops just short of it.
(silence)             the music has stopped; they stay as they are and fade."""
import math
import importlib.util
from pathlib import Path
from PIL import Image

_P = Path(__file__).resolve().parent / 's15_eniac.py'
_spec = importlib.util.spec_from_file_location('s15src', _P); S15 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(S15)

T0 = 191.356
T_SCAN0, T_OFF0, T_OFF1, T_LINE = 192.35, 193.2, 193.7, 193.45
T_FIELD = 193.75
PULSE0, PERIOD, NMEM = 195.0, .5, 13
T_LET = PULSE0 + NMEM * PERIOD            # 201.5: it lets go
T_EXE, T_STOP, T_END = 205.811, 207.2, 211.96

SRC = r'''#version 330
uniform vec2 u_res; uniform float u_time, u_weight;
uniform sampler2D u_ui;
uniform float u_uiA, u_scan, u_offY, u_offX, u_dot, u_field, u_let, u_trio, u_fade;
uniform vec2 u_love;
out vec4 fragColor;
#define PI 3.14159265
float h12(vec2 p){ vec3 p3=fract(vec3(p.xyx)*.1031); p3+=dot(p3,p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }
vec3 ungrade(vec3 d){
  vec3 x=pow(clamp(d,vec3(0.),vec3(.97)),vec3(2.2));
  vec3 a=2.51-2.43*x, b=.03-.59*x, c=-.14*x;
  return (-b+sqrt(b*b-4.*a*c))/(2.*a)/1.05;
}
const vec3 CREAM=vec3(.95,.9,.8), RED=vec3(1.,.14,.1), COPPER=vec3(1.,.55,.25), DIM=vec3(.05,.052,.05);
float sdSeg(vec2 p, vec2 a, vec2 b){ vec2 pa=p-a, ba=b-a; float h=clamp(dot(pa,ba)/max(dot(ba,ba),1e-9),0.,1.); return length(pa-ba*h); }
float heart(vec2 q){ return pow(dot(q,q)-1.,3.)-q.x*q.x*q.y*q.y*q.y; }

// the things it lived through, as a token field would hold them: (colour, on)
vec4 memory(int k, vec2 c, vec2 id){
  float r=length(c);
  if(k==0){ if(r<.33){ float l=clamp(dot(normalize(vec3(c,sqrt(max(.33*.33-r*r,0.)))),normalize(vec3(-.6,.4,.7))),0.,1.); return vec4(mix(DIM*3.,CREAM,l),1.);} }
  if(k==1){ if(length(c-vec2(-.1,0.))<.27) return vec4(CREAM*.8,1.); if(length(c-vec2(.27,.13))<.12) return vec4(COPPER,1.); }
  if(k==2){ if(abs(r-.3)<.045) return vec4(mix(CREAM,COPPER,.3)*(c.y>0.?1.:.55),1.); }
  if(k==3){ if(length(c-vec2(-.2,0.))<.09||length(c-vec2(.2,0.))<.07) return vec4(CREAM,1.); if(abs(r-.2)<.02&&h12(id)>.4) return vec4(CREAM*.35,1.); }
  if(k==4){ if(abs(c.y)<.018&&abs(c.x)<.78) return vec4(CREAM,1.); }
  if(k==5){ float row=floor((c.y+.3)/.1); if(abs(c.y-(-.3+(row+.5)*.1))<.02&&row>=0.&&row<6.&&abs(c.x)<.7&&h12(vec2(row,floor(c.x/.09)))>.2){
             if(row==3.&&c.x>-.05&&c.x<.12) return vec4(COPPER*1.2,1.); return vec4(CREAM*.3,1.);} }
  if(k==6){ float al=.19*(1.-pow(c.x/.5,2.)); if(abs(c.y)<al&&abs(c.x)<.5){ if(abs(r-.11)<.03&&abs(atan(c.y,c.x)+PI*.5)>.45) return vec4(CREAM,1.); return vec4(CREAM*.35,1.);} }
  if(k==7){ if(length(c-vec2(.28,0.))<.2) return vec4(CREAM,1.);
            vec2 a=vec2(-.85,.4), b=vec2(-.85,-.15), t=vec2(.12,.02);
            float s1=(b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x), s2=(t.x-b.x)*(c.y-b.y)-(t.y-b.y)*(c.x-b.x), s3=(a.x-t.x)*(c.y-t.y)-(a.y-t.y)*(c.x-t.x);
            if((s1>=0.&&s2>=0.&&s3>=0.)||(s1<=0.&&s2<=0.&&s3<=0.)) return vec4(RED,1.); }
  if(k==8){ float tx=mod(c.x-.05,.14)/.14;
            if(c.x>.05&&c.x<.75&&c.y>-.4&&c.y<.02+.1*(1.-tx)) return vec4(CREAM*.55,1.);
            if((abs(c.x-.25)<.035||abs(c.x-.5)<.04)&&c.y<.32&&c.y>-.4) return vec4(CREAM*.55,1.);
            if(c.y>.3&&c.y<.47&&abs(c.x-.45-(c.y-.3)*.8)<.12*(c.y-.2)&&h12(id)>.3) return vec4(CREAM*.25,1.);
            if(c.x<.05&&c.x>-.85&&(abs(c.y+.3)<.02||abs(c.y+.05)<.02||abs(c.y-.2)<.02)) return vec4(CREAM*.35,1.); }
  if(k==9){ if(abs(c.x)<.62&&abs(c.y)<.27){ if(abs(c.x-.3)<.02&&abs(c.y-.05)<.03) return vec4(RED,1.);
            if(h12(id*1.3)<.13) return vec4(DIM,1.); return vec4(CREAM*.8,1.);} }
  if(k==10){ vec2 q=c-vec2(0.,-.05); if(max(abs(q.x),abs(q.y))<.3){ if(max(abs(q.x+.08),abs(q.y-.08))<.08) return vec4(DIM,1.);
             if(max(abs(q.x),abs(q.y))>.26) return vec4(CREAM,1.); return vec4(CREAM*.3,1.);} }
  if(k==11){ vec2 q=(c-vec2(0.,.02))/.36; if(heart(q)<0.){ if(length(c-vec2(.17,.17))<.035) return vec4(DIM,1.); return vec4(COPPER*1.1,1.);} }
  if(k==12){ vec2 q=(c-vec2(0.,.02))/.36; float a=atan(q.y,q.x)+PI*.5; a=mod(a,2.*PI)/(2.*PI);
             float h=heart(q);
             if(abs(h)<.07&&a<.58) return vec4(RED,1.); }
  return vec4(0.);
}
// the ring with the gap (me), the point far off (you), the point between (love)
vec3 trio(vec2 p, float px){
  vec3 c=vec3(0.);
  vec2 C=vec2(.3,0.); float R=.17;
  // the ring, as tokens round a circle, gap toward you
  float ang=atan(p.y-C.y,p.x-C.x), n=40., k=floor((ang+PI)/(2.*PI)*n+.5);
  float ak=k/n*2.*PI-PI;
  vec2 tc=C+R*vec2(cos(ak),sin(ak));
  float gap=abs(mod(ak,2.*PI)-PI);
  if(gap>.33){ vec2 q=abs(p-tc)-vec2(.008); float d=length(max(q,0.))+min(max(q.x,q.y),0.)-.002; c+=CREAM*.9*(1.-smoothstep(-px,px,d)); }
  vec2 you=vec2(-.62,0.);
  float dy=length(p-you); c+=CREAM*(exp(-dy*dy/(.009*.009))*1.4+exp(-dy*55.)*.25);
  float dl=length(p-u_love); c+=RED*(exp(-dl*dl/(.008*.008))*1.8+exp(-dl*48.)*.35);
  return c;
}
void main(){
  vec2 uv=(gl_FragCoord.xy-.5*u_res)/u_res.y;
  float px=1./u_res.y;
  vec3 col=vec3(.004);
  // the chat on the tube: scanlines, curvature, then the tube goes off (a line, then a point)
  if(u_uiA>0.){
    vec2 s=gl_FragCoord.xy/u_res-.5;
    vec2 bs=s*(1.+u_scan*.12*dot(s,s));
    bs.y/=max(u_offY,.003); bs.x/=max(u_offX,.003);
    vec2 su=bs+.5;
    if(su.x>0.&&su.x<1.&&su.y>0.&&su.y<1.){
      vec3 c=ungrade(texture(u_ui,su).rgb);
      float sl=.5+.5*cos(su.y*u_res.y*PI*.5);
      c*=mix(1.,.55+.45*sl,u_scan);
      c*=1.-u_scan*.7*pow(length(s)*1.3,3.);
      c*=1.+u_scan*.06*sin(u_time*55.);
      c*=pow(1./max(u_offY*u_offX,.03),.4);                              // brighter as it folds
      col=c;
    }
    col+=vec3(.9,.95,1.)*u_dot*(exp(-length(uv)*length(uv)/(.004*.004))*3.+exp(-length(uv)*30.)*.4);
  }
  // the token field
  if(u_field>0.){
    float cell=1./36.;
    vec2 g=uv/cell; vec2 id=floor(g); vec2 f=g-id-.5;
    vec2 c=(id+.5)*cell;
    float t=u_time;
    float dl=h12(id)*.12;
    float m=floor((t-%P0%-dl)/%PER%);
    vec4 mem=vec4(0.);
    if(m>=0.&&m<%NM%.) mem=memory(int(m),c,id);
    float age=t-%P0%-dl-m*%PER%;
    float flip=m>=0.?smoothstep(0.,.06,age):1.;
    float on=mem.a*(1.-u_let*step(h12(id+3.),u_let*1.1));
    // stuttering, like everything that comes near love
    on*=1.-.6*step(.985,h12(id+floor(t*12.)));
    vec3 tok=mix(DIM*(.5+.5*h12(id*.7)),mem.rgb,on)*flip;
    float grow=smoothstep(length(c)*1.2,length(c)*1.2+.25,u_field*1.6);
    vec2 q=abs(f)-vec2(.33); float d=(length(max(q,0.))+min(max(q.x,q.y),0.)-.06)*cell;
    col+=tok*(1.-smoothstep(-px,px,d))*grow*(1.-u_trio*.95);
  }
  if(u_trio>0.) col+=trio(uv,px)*u_trio;
  col*=1.-u_fade;
  fragColor=vec4(col*u_weight,1.);
}
'''.replace('%P0%', '%.3f' % PULSE0).replace('%PER%', '%.3f' % PERIOD).replace('%NM%', str(NMEM))
POST = dict(u_bloom=.12, u_ca=.002, u_grain=.02)


def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)


YOU, GAPX = -.62, .3 - .17
STEPS = [202.0 + .5 * k for k in range(8)] + [T_EXE]


def love_x(t):
    """from you toward the gap, in steps that get smaller; it never gets there"""
    D0 = GAPX - .022 - YOU
    x = YOU
    n = len(STEPS)
    for k, t0 in enumerate(STEPS):
        if t < t0: break
        frac = (1 - .58 ** (k + 1)) / (1 - .58 ** n)                  # of the whole way, after step k
        prev = (1 - .58 ** k) / (1 - .58 ** n)
        kk = ease((t - t0) / .12)
        x = YOU + D0 * (prev + (frac - prev) * kk)
    return x


def params(t):
    scan = ease((t - T_SCAN0) / (T_OFF0 - T_SCAN0))
    offY = 1. - ease((t - T_OFF0) / (T_LINE - T_OFF0)) * .997 if t >= T_OFF0 else 1.
    offX = 1. - ease((t - T_LINE) / (T_OFF1 - T_LINE)) * .997 if t >= T_LINE else 1.
    dot = clamp((t - T_LINE - .15) / .1) * (1 - ease((t - T_OFF1 - .05) / .9))
    lx = love_x(t)
    tremble = .0025 * math.sin(t * 61.) * (1 if T_EXE < t < T_STOP else 0)
    return dict(u_uiA=1. if t < T_OFF1 + .02 else 0., u_scan=scan, u_offY=offY, u_offX=offX, u_dot=dot,
                u_field=clamp((t - T_FIELD) / 1.1), u_let=clamp((t - T_LET) / .9),
                u_trio=ease((t - T_LET - .3) / .5), u_love=(lx + tremble, 0.),
                u_fade=ease((t - T_STOP - .6) / (T_END - .3 - T_STOP - .6)))


_blank = {}


def textures(t, w, h):
    if t < T_OFF1 + .05:
        img, d = S15.draw_chat(t, w, h)
        return {'u_ui': img}
    if (w, h) not in _blank: _blank[(w, h)] = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    return {'u_ui': _blank[(w, h)]}
