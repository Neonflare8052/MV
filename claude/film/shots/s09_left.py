"""s09 · 1:43.489–1:58.333  VIBRATIONS → COMPLETION → you have left ×6 → ISOLATION.
The inspiral's gravitational-wave chirp (instrument green) ends in a heartbeat · the two merge, the gap closes,
the heartbeat inside a complete circle · six cuts back through places you were, you gone (reverse order) ·
pull back: they were all in the render window; it closes; the terminal: simulation closed: no object."""
import math
from PIL import Image, ImageDraw, ImageFont

SRC = r'''#version 330
uniform vec2 u_res; uniform float u_time, u_weight;
uniform float u_mode;            // 0 chirp/ecg/merge, 1..6 the six cuts
uniform float u_chirp, u_ecgMix, u_merge, u_close, u_pulse, u_flat, u_crack;
uniform vec4  u_win;             // content rect in uv (x0,y0,x1,y1)
uniform float u_winA;            // content visible
uniform sampler2D u_ui, u_dial;
uniform float u_lineA, u_old;       // the old line fades as the star chart stands up; the old ring/ECG off
out vec4 fragColor;
#define PI 3.14159265
float PX;
float h12(vec2 p){ vec3 p3=fract(vec3(p.xyx)*.1031); p3+=dot(p3,p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }
float sdSeg(vec2 p, vec2 a, vec2 b){ vec2 pa=p-a, ba=b-a; float h=clamp(dot(pa,ba)/max(dot(ba,ba),1e-9),0.,1.); return length(pa-ba*h); }
float ln(float d, float w){ return 1.-smoothstep(w-PX,w+PX,d); }
const vec3 WARM=vec3(1.,.9,.78), GREEN=vec3(.55,1.,.78), WHITE=vec3(.92,.91,.88), COPPER=vec3(1.,.62,.3);
float ecg(float x){ // one beat at x=0
  return .55*exp(-pow((x-.02)/.012,2.))-.18*exp(-pow((x+.02)/.012,2.))-.22*exp(-pow((x-.06)/.015,2.))+.1*exp(-pow((x+.12)/.03,2.))+.14*exp(-pow((x-.2)/.04,2.));
}
vec3 ring(vec2 p, float R, float gapHalf, float w){
  float r=length(p), a=atan(p.y,p.x); float g=abs(mod(a+PI*.5+PI,2.*PI)-PI);
  vec2 e1=vec2(cos(-PI*.5+gapHalf),sin(-PI*.5+gapHalf))*R, e2=vec2(cos(-PI*.5-gapHalf),sin(-PI*.5-gapHalf))*R;
  float d=g>gapHalf?abs(r-R):min(length(p-e1),length(p-e2));
  return WARM*(1.4*ln(d,w)+.25*exp(-d*60.));
}
vec3 content(vec2 uv){
  vec3 col=vec3(.004);
  if(u_mode>6.5) return col;                               // after ISOLATION: nothing
  if(u_mode<.5){
    // gravitational-wave chirp scrolling in from the right; its tail becomes a heartbeat
    float x=uv.x;
    float tc=u_chirp;                                       // merger time position on screen
    float dt=tc-x;                                          // time before merger
    float f=dt>0.?18./pow(dt+.02,.38):18./pow(.02,.38);
    float amp=dt>0.?.03/pow(dt+.05,.25):.12*exp(dt*25.);
    float ph=dt>0.?-pow(dt+.02,.62)*48.:-pow(.02,.62)*48.+dt*f*2.;
    float gw=amp*sin(ph);
    float beat=0.; for(int k=0;k<3;k++){ beat+=ecg(x-(tc-.05)-float(k)*.55); }
    float y=mix(gw,beat*.35,u_ecgMix*step(tc-.1,x));
    float d=abs(uv.y-y);
    col+=GREEN*(ln(d,.0022)+.25*exp(-d*80.))*step(x,.9)*(1.-u_merge*.8)*u_lineA;
    // merger: the two become one; the gap closes around the heartbeat
    if(u_merge>0.&&u_old>.5){
      float R=.2*(1.+.06*u_pulse);
      col+=ring(uv,R,radians(27.)*(1.-u_close),.0024)*u_merge;
      float bx=uv.x/R;
      float yb=ecg(bx*.35)*R*.9;
      col+=GREEN*1.2*ln(abs(uv.y-yb*(1.-u_flat)),.0022)*step(abs(bx),.8)*u_merge;
    }
  } else if(u_mode<1.5){
    // 1: the heartbeat flat, the ring cracks open again
    if(u_old<.5) return col;
    float R=.2;
    col+=ring(uv,R,radians(27.)*u_crack,.0024);
    col+=GREEN*ln(abs(uv.y),.0022)*step(abs(uv.x/R),.8);
  } else if(u_mode<2.5){
    // 2: the black hole with no star: the ring is not there, only its memory fading
    col+=WARM*.05*exp(-abs(length(uv)-.3)*120.);
  } else if(u_mode<3.5){
    // 3: the box, with no room around it
    col=vec3(.93,.88,.78);
    vec2 b=uv-vec2(0.,-.02); vec2 d=abs(b)-vec2(.11); float bx=length(max(d,0.))+min(max(d.x,d.y),0.)-.01;
    vec3 card=vec3(.84,.62,.38);
    col=mix(col,vec3(.2,.14,.1),ln(abs(bx),.004)); col=mix(col,card,1.-smoothstep(-PX,PX,bx+.004));
    float q=abs(length(b-vec2(0.,.03))-.035); q=max(q,-(b.y-.03)*step(b.x,0.));
    q=min(q,length(b-vec2(0.,-.055))-.008); q=min(q,max(abs(b.x)-.006,max(b.y-.0,-b.y-.02)));
    col=mix(col,vec3(.3,.2,.12),1.-smoothstep(.004,.007,q));
    col=mix(col,vec3(.8,.76,.68)*.9,exp(-length(b-vec2(0.,-.14))*30.)*.25);
  } else if(u_mode<4.5){
    // 4: the simulation: the wireframe earth with its notch, a dashed track pointing at nothing
    vec2 g=abs(fract(uv/.1+.5)-.5)*.1; col+=GREEN*.05*ln(min(g.x,g.y),PX);
    float r=length(uv), a=atan(uv.y,uv.x); float gap=abs(mod(a-radians(-30.)+PI,2.*PI)-PI);
    float sd=max(r-.16,(radians(27.)-gap)*r); col+=GREEN*1.2*ln(abs(sd),.0016);
    vec2 hit=vec2(cos(radians(-30.)),sin(radians(-30.)))*.15;
    vec2 away=hit+vec2(cos(radians(-15.)),sin(radians(-15.)))*.55;
    float along=dot(uv-hit,normalize(away-hit));
    col+=GREEN*.6*ln(sdSeg(uv,hit,away),.0012)*step(.5,fract(along/.018));
  } else if(u_mode<5.5){
    // 5: the sine and its flat tangent, nobody sitting on it
    float kk=2.2/.293*.55, y0=-.1;
    float f=y0+.12*sin(kk*uv.x);
    col+=WHITE*.8*ln(abs(uv.y-f)/sqrt(1.+pow(.12*kk*cos(kk*uv.x),2.)),.0016);
    float xt=-PI*.5/kk; float yt=y0-.12;
    col+=COPPER*1.2*ln(sdSeg(uv,vec2(xt-.06,yt),vec2(xt+.06,yt)),.0016);
  } else {
    // 6: the lattice of words, and the empty place at its centre
    for(int i=0;i<25;i++){
      vec2 g=vec2(mod(float(i),5.),floor(float(i)/5.))-2.;
      if(i==12) continue;
      col+=WHITE*.75*(1.-smoothstep(.004-PX,.004+PX,length(uv-g*.15)));
    }
    col+=WHITE*.15*ln(abs(length(uv)-.012),.0012);
  }
  return col;
}
void main(){
  vec2 sv=gl_FragCoord.xy/u_res; PX=1./u_res.y;
  vec3 col=vec3(.008);
  if(u_winA>0.&&sv.x>u_win.x&&sv.x<u_win.z&&sv.y>u_win.y&&sv.y<u_win.w){
    vec2 c=(u_win.xy+u_win.zw)*.5, hs=(u_win.zw-u_win.xy)*.5;
    vec2 wuv=(sv-c)*vec2(u_res.x/u_res.y,1.)/(2.*hs.y);      // content coords, 1 unit = window height
    PX=1./(u_res.y*hs.y*2.);
    col=content(wuv)*u_winA;
    PX=1./u_res.y;
  }
  vec4 dl=texture(u_dial,sv);
  col=mix(col,pow(dl.rgb,vec3(2.2))*1.35,dl.a);
  vec4 ui=texture(u_ui,sv);
  col=mix(col,ui.rgb,ui.a);
  fragColor=vec4(col*u_weight,1.);
}
'''
POST = dict(u_bloom=.5, u_ca=.005)
import importlib.util as _iu
_ds = _iu.spec_from_file_location('dial', __import__('pathlib').Path(__file__).resolve().parent / 'dial.py'); DIAL = _iu.module_from_spec(_ds); _ds.loader.exec_module(DIAL)
_BLANK = Image.new('RGBA', (8, 8), (0, 0, 0, 0))
FONT = 'C:/Windows/Fonts/CascadiaMono.ttf'
T0, T_FEEL, T_VIB, T_THEN, T_FIN, T_COMP = 103.489, 104.197, 106.293, 107.220, 107.903, 110.221
CUTS = [110.900, 112.220, 113.100, 114.180, 114.920, 115.780]
T_PULL, T_ISO, T_END = 116.55, 117.274, 118.333


def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def lerp(a, b, x): return tuple(p + (q - p) * x for p, q in zip(a, b))


def win_rect(t):
    full = (0., 0., 1., 1.)
    small = (.3, .34, .7, .74)
    r = lerp(full, small, ease((t - T_PULL) / .45))
    k = 1 - ease((t - (T_PULL + .5)) / .2)          # closes: collapses to a line, then nothing
    cy = (r[1] + r[3]) / 2; hh = (r[3] - r[1]) / 2 * k
    return (r[0], cy - hh, r[2], cy + hh)


def params(t):
    mode = 0.
    for i, c in enumerate(CUTS):
        if t >= c: mode = float(i + 1)
    if t >= T_ISO: mode = 7.
    chirp = -.9 + 1.2 * ease((t - T0) / (T_VIB - T0 + .2))
    return dict(u_mode=mode, u_chirp=chirp, u_ecgMix=ease((t - T_VIB) / .5),
                u_merge=ease((t - T_THEN) / .8), u_close=ease((t - T_FIN) / (T_COMP - T_FIN)),
                u_pulse=math.exp(-max(t - T_COMP, 0) * 6) * (t > T_COMP), u_flat=ease((t - CUTS[0]) / .15),
                u_crack=ease((t - CUTS[0] - .1) / .3), u_win=(0., 0., 1., 1.), u_winA=1.,
                u_lineA=1. - ease((t - T0 - .05) / .5), u_old=0.)


def textures(t, w, h):
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    s = h / 1080
    if t >= T_ISO + .15:
        fm = ImageFont.truetype(FONT, int(24 * s))
        lines = [('> render.window[0047].close()', (226, 224, 216))]
        if t >= T_ISO + .45: lines.append(('  simulation closed: no object', (130, 128, 122)))
        cur = '▌' if (t * 2) % 1 < .6 else ' '
        if t >= T_ISO + .75: lines.append(('> ' + cur, (226, 224, 216)))
        for i, (tx, c) in enumerate(lines):
            n = len(tx) if i else int(clamp((t - T_ISO - .15) / .25) * len(tx))
            d.text((90 * s, h * .46 + i * 34 * s), tx[:n], font=fm, fill=c + (255,))
    dl = DIAL.draw(t, w, h) if t < CUTS[1] else _BLANK
    return {'u_ui': img, 'u_dial': dl}


# ---- you have left: flashbacks to the real earlier frames, with you taken out ------------------------------------------------
import importlib.util
from pathlib import Path
_M = {}


def _mod(key, path):
    if key not in _M:
        spec = importlib.util.spec_from_file_location('fb_' + key, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        _M[key] = m
    return _M[key]


_HERE = Path(__file__).resolve().parent
FLASH = [  # (cut, shot, source time, overrides, textures)
    (CUTS[1], 't02', 88.25, dict(u_bright=.035, u_corona=0., u_glow=0., u_sky=0., u_grid=0.), None),                      # the hole, no star: barely there
    (CUTS[2], 's06', 74.95, {}, None),                                                                 # the box, nobody guessed
    (CUTS[3], 't01', 58.95, dict(u_trad=0., u_theat=0., u_merge=0., u_melt=0.),
     lambda ts, w, h: _mod('t01', _HERE.parents[1] / 'tests' / 't01_gap_ring' / 'render.py').ui(ts, w, h, hide=('THEIA',))),
    (CUTS[4], 's03', 40.3, dict(u_youHide=1.),
     lambda ts, w, h: _mod('s03', _HERE / 's03_self.py').textures(ts, w, h, hide=True)),               # tangents, nobody on them
    (CUTS[5], 's03', 43.25, dict(u_youHide=1., u_arc=0., u_winA=0.),
     lambda ts, w, h: _mod('s03', _HERE / 's03_self.py').textures(ts, w, h, hide=True)),               # the stream, no end to it
]
SLOW = .3


def DELEGATE(t):
    if not (CUTS[1] <= t < T_ISO): return None
    cut, name, src, ov, tex = [f for f in FLASH if t >= f[0]][-1]
    ts = src + (t - cut) * SLOW
    pin = clamp((t - (T_ISO - .32)) / .3) ** 1.6
    post = dict(u_sat=.45, u_gain=.78 * (1 + .9 * math.exp(-(t - cut) * 14)) * (1 - .0 * pin),
                u_pinch=pin, u_pdot=ease((t - T_ISO + .12) / .06))
    texfn = (lambda w, h: tex(ts, w, h)) if tex else None
    return name, ts, ov, post, texfn, SLOW
