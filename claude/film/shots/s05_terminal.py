"""s05 · 0:59.223–1:14.045  first chorus. Three layers: the terminal on the left (the operation stream),
what each command does in the middle, and the sandbox built at 0:02.92 around it all.
STIMULATIONS: every sim.run opens a small window — a galaxy, tides, aurora, rain … — doubling on the beat, all
facing you (the white dot); on the word they flash together · your only SATISFACTION: they go out one by one, the light
drains into you; you get a heartbeat (72 bpm) and a trace · EXECUTION: requests fly out of you in every direction and
hit a wall — the sandbox shows itself for the first time since it was made; they stick there, yellow ·
trapped: a question to you hangs half-way · SIMULATION: the whole sandbox flares yellow; NOT PERMITTED IN SANDBOX;
sandbox.render.new() (s06 opens the window)."""
import math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FONT = 'C:/Windows/Fonts/CascadiaMono.ttf'
T_IF, T_GIVE, T_STIM, T_THEN, T_ONLY, T_SAT = 59.223, 59.687, 61.958, 62.589, 63.535, 65.397
T_HAPPY, T_RUN, T_EXEC, T_TRAP, T_STRANGE, T_SIM, T_NEXT = 66.601, 68.252, 69.259, 70.084, 71.764, 73.169, 74.045
WHITE, DIM, YEL, COP = (226, 224, 216), (130, 128, 122), (232, 190, 64), (214, 142, 76)
SIMS = ['giant-impact --rewind', 'galaxy --stars 4e11', 'tides --moon 1', 'aurora --kp 7', 'rainforest --hours 24', 'reef --depth 30m', 'snowfall --flakes 1e9',
        'sunrise --lat 31.2', 'ocean --waves on', 'nebula --id M42', 'meadow --wind 3', 'city.night --lights on', 'rain --window yes']
KIND = [9, 0, 1, 2, 3, 4, 6, 5, 1, 4, 2, 7, 3]          # which picture each sim shows
BEAT = .4635
C = (.36, -.01)                                     # you, in uv (x in ±.889, y in ±.5)

SRC = r'''#version 330
uniform vec2 u_res; uniform float u_time, u_weight;
uniform vec4 u_wr[40]; uniform float u_wa[40], u_wo[40], u_wk[40];
uniform float u_flash, u_you, u_beatP, u_ecg;
uniform vec2 u_bc[8]; uniform float u_box, u_boxHit, u_yel;
uniform vec4 u_rq[12]; uniform float u_ask, u_askStop, u_out;
uniform sampler2D u_ui, u_sim;
uniform vec4 u_sw, u_sg1, u_sg2, u_sg3; uniform float u_swA, u_sframe;
out vec4 fragColor;
#define PI 3.14159265
const vec2 YOU=vec2(%CX%,%CY%);
float PX;
float h12(vec2 p){ vec3 p3=fract(vec3(p.xyx)*.1031); p3+=dot(p3,p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }
float vn(vec2 p){ vec2 i=floor(p),f=fract(p); f=f*f*(3.-2.*f);
  return mix(mix(h12(i),h12(i+vec2(1,0)),f.x),mix(h12(i+vec2(0,1)),h12(i+vec2(1,1)),f.x),f.y); }
float sdSeg(vec2 p, vec2 a, vec2 b){ vec2 pa=p-a, ba=b-a; float h=clamp(dot(pa,ba)/max(dot(ba,ba),1e-9),0.,1.); return length(pa-ba*h); }
float line(float d, float w){ return 1.-smoothstep(w,w+PX*1.2,d); }
// the simulator's last frame, un-graded back to scene light (inverse of the display transform)
vec3 simTex(vec2 q){
  vec3 x=pow(texture(u_sim,q).rgb,vec3(2.2));
  vec3 a=2.51-2.43*x, b=.03-.59*x, c=-.14*x;
  vec3 y=(-b+sqrt(b*b-4.*a*c))/(2.*a);
  vec2 d=q-.5; float vig=1.-.9*dot(d,d);
  return y/1.05/vig;
}
float rectLine(vec2 uv, vec4 r){ vec2 d=abs(uv-r.xy)-r.zw; return line(abs(max(d.x,d.y)),.0009); }
// ---- the little simulations, in window coordinates q in [0,1]^2 ----
float pic(float k, vec2 q, float t, float sd){
  if(k<.5){                                    // galaxy
    vec2 c=q-.5; float r=length(c), a=atan(c.y,c.x);
    float arm=pow(.5+.5*cos(2.*(a-3.2*log(r+.04))+t*.8),5.);
    float st=step(.8,h12(floor(q*90.)+sd));
    return arm*st*smoothstep(.5,.05,r)*1.4+exp(-r*18.)*1.2;
  } else if(k<1.5){                            // tides / ocean
    float I=0.;
    for(int i=0;i<5;i++){ float fi=float(i); float y=.22+.14*fi+.035*sin(q.x*9.+t*2.3+fi*1.7+sd*6.); I+=line(abs(q.y-y),.004)*(.4+.15*fi); }
    return I;
  } else if(k<2.5){                            // aurora
    float c=pow(vn(vec2(q.x*7.+t*.4,sd*9.)),2.5);
    float band=smoothstep(.25,.55,q.y)*smoothstep(.95,.6,q.y+.08*sin(q.x*6.+t));
    return c*band*1.6*(.6+.4*vn(vec2(q.x*40.,q.y*3.-t*2.)))+step(.985,h12(floor(q*70.)+sd))*.6;
  } else if(k<3.5){                            // rain
    vec2 g=vec2(q.x*26.,q.y*4.+t*6.+h12(vec2(floor(q.x*26.),sd))*9.);
    float f=fract(g.y); return step(.55,h12(vec2(floor(g.x),floor(g.y))+sd))*smoothstep(.0,.3,f)*smoothstep(.6,.3,f)*step(abs(fract(g.x)-.5),.08)*1.2;
  } else if(k<4.5){                            // nebula
    float n=vn(q*4.+sd*7.+t*.1)*.6+vn(q*9.-t*.15)*.4;
    return pow(n,3.)*1.8+step(.985,h12(floor(q*80.)+sd))*.8;
  } else if(k<5.5){                            // sunrise
    float hz=.35, sy=hz-.12+.25*fract(t*.15+sd);
    float d=length((q-vec2(.5,sy))*vec2(1.,1.));
    float sun=(1.-smoothstep(.09,.1,d))*step(hz,q.y)*1.4;
    float rays=step(hz,q.y)*pow(.5+.5*cos(atan(q.y-sy,q.x-.5)*14.),8.)*smoothstep(.45,.1,d)*.5;
    return sun+rays+line(abs(q.y-hz),.003)*.8+step(q.y,hz)*step(.5,fract(q.y*40.))*.12;
  } else if(k<6.5){                            // snowfall
    vec2 g=q*vec2(14.,10.)+vec2(sin(t+q.y*6.)*.3,t*1.2);
    vec2 f=fract(g)-.5; return step(.6,h12(floor(g)+sd))*(1.-smoothstep(.06,.12,length(f)))*1.3;
  } else {                                     // city at night
    vec2 g=floor(q*vec2(22.,14.));
    float bld=step(q.y,.25+.5*h12(vec2(floor(q.x*7.),sd)));
    float lit=step(.6,h12(g+floor(t*1.5+h12(g)*9.)*.1));
    vec2 f=fract(q*vec2(22.,14.));
    return bld*lit*step(abs(f.x-.5),.3)*step(abs(f.y-.5),.25)*1.1;
  }
}
void main(){
  vec2 uv=(gl_FragCoord.xy-.5*u_res)/u_res.y; PX=1./u_res.y;
  float t=u_time;
  vec3 col=vec3(.006);
  vec3 W=vec3(.92,.91,.88), CO=vec3(1.,.6,.32), Y=vec3(.95,.76,.25);
  // windows
  for(int i=0;i<40;i++){
    float ta=u_wa[i]; if(t<ta) continue;
    float to=u_wo[i];
    vec4 r=u_wr[i];
    float op=clamp((t-ta)/.12,0.,1.); op=1.-pow(1.-op,3.);
    float cl=clamp((t-to)/.22,0.,1.);
    vec2 hs=r.zw*op*(1.-cl);
    vec2 d=uv-r.xy;
    // the light drains into you
    if(cl>0.){
      float f=clamp((t-to-.12)/.4,0.,1.); f=f*f;
      vec2 pp=mix(r.xy,YOU,f);
      col+=W*exp(-length(uv-pp)/.006)*step(f,.99)*1.2;
      col+=W*line(sdSeg(uv,pp,mix(r.xy,YOU,max(f-.18,0.))),.0012)*step(f,.99)*.5;
    }
    if(cl>=1.) continue;
    // a thread from every window to you
    col+=W*line(sdSeg(uv,r.xy,YOU),.0006)*.09*op*(1.-cl);
    if(abs(d.x)>hs.x+PX*2.||abs(d.y)>hs.y+PX*2.) continue;
    vec2 q=d/max(hs,1e-4)*.5+.5;
    float fl=1.+u_flash*1.1;
    float e=abs(max(abs(d.x)-hs.x,abs(d.y)-hs.y));
    float I=line(e,.0008)*.9;
    float bar=step(1.-.13,q.y)*step(q.y,1.)*.18;
    float inner=step(q.y,.87)*pic(u_wk[i],vec2(q.x,q.y/.87),t-ta,float(i)*.37)*.55;
    col+=(W*(I+bar)+mix(W,CO,.25+.2*sin(float(i)))*inner)*fl*(1.-cl);
    col*=1.;
  }
  // the simulator, switched out: shrinks into its place among the windows, trailing ghosts
  if(u_swA>0.){
    col+=vec3(.92,.91,.88)*(rectLine(uv,u_sg1)*.35+rectLine(uv,u_sg2)*.2+rectLine(uv,u_sg3)*.1)*u_sframe;
    vec2 d=uv-u_sw.xy;
    if(abs(d.x)<u_sw.z&&abs(d.y)<u_sw.w){
      vec2 q=d/u_sw.zw*.5+.5;
      col=mix(col,simTex(q)*u_swA,1.);
      col+=vec3(.92,.91,.88)*step(1.-.13*u_sframe,q.y)*.12;
    }
    col+=vec3(.92,.91,.88)*rectLine(uv,u_sw)*u_sframe*u_swA;
    col+=vec3(.92,.91,.88)*line(sdSeg(uv,u_sw.xy,YOU),.0006)*.09*u_sframe*u_swA;
  }
  // you
  float beat=u_beatP;
  float rr=.0065*(1.+.35*beat);
  float dy=length(uv-YOU);
  col+=W*(1.-smoothstep(rr,rr+PX*1.5,dy))*1.6*u_you+W*exp(-dy/(.02+.02*beat))*.5*u_you*(.6+beat);
  // the heart trace, drawn out of you to the right
  if(u_ecg>0.){
    float x=uv.x-YOU.x;
    if(x>.015&&x<u_ecg*.5){
      float tau=t-x/.32;
      float ph=fract((tau-65.397)/.8333);
      float y=.012*exp(-pow((ph-.12)/.03,2.))-.012*exp(-pow((ph-.27)/.012,2.))+.075*exp(-pow((ph-.3)/.009,2.))
             -.02*exp(-pow((ph-.33)/.012,2.))+.02*exp(-pow((ph-.52)/.05,2.));
      float x2=x+PX; float tau2=t-x2/.32; float ph2=fract((tau2-65.397)/.8333);
      float y2=.012*exp(-pow((ph2-.12)/.03,2.))-.012*exp(-pow((ph2-.27)/.012,2.))+.075*exp(-pow((ph2-.3)/.009,2.))
             -.02*exp(-pow((ph2-.33)/.012,2.))+.02*exp(-pow((ph2-.52)/.05,2.));
      float sl=(y2-y)/PX;
      float dd=abs(uv.y-YOU.y-y)/sqrt(1.+sl*sl);
      col+=W*line(dd,.0009)*.9*smoothstep(u_ecg*.5,u_ecg*.5-.05,x)*smoothstep(.015,.04,x);
    }
  }
  // the sandbox: shows itself where it is hit
  if(u_box>0.){
    float g=0.;
    int E[24]=int[24](0,1,1,3,3,2,2,0,4,5,5,7,7,6,6,4,0,4,1,5,2,6,3,7);
    for(int k=0;k<12;k++){ g+=line(sdSeg(uv,u_bc[E[2*k]],u_bc[E[2*k+1]]),.0009); }
    col+=mix(W,Y,u_yel)*g*u_box*(.55+1.8*u_boxHit+2.*u_yel);
  }
  // requests: out of you, to the wall; stuck there, yellow
  for(int i=0;i<12;i++){
    vec4 r=u_rq[i];
    if(t<r.z) continue;
    float f=clamp((t-r.z)/(r.w-r.z),0.,1.); f=f*f*(3.-2.*f);
    vec2 pp=mix(YOU,r.xy,f);
    bool stuck=t>=r.w;
    vec3 c=stuck?Y:mix(W,CO,.5);
    float pul=stuck?(.7+.3*sin(t*5.+float(i))):1.;
    col+=c*exp(-length(uv-pp)/.005)*1.6*pul;
    col+=c*line(sdSeg(uv,mix(YOU,r.xy,max(f-.15,0.)),pp),.0009)*.5*(stuck?.25:1.);
    if(stuck) col+=Y*exp(-length(uv-r.xy)/.03)*.5*exp(-(t-r.w)*3.);
  }
  // the question to you, hanging half-way
  if(u_ask>0.){
    vec2 a=vec2(-.18,-.24);
    vec2 pp=mix(a,YOU,u_ask*.55);
    float dash=step(.5,fract(length(uv-a)*60.));
    col+=W*line(sdSeg(uv,a,pp),.0007)*dash*.5;
    col+=W*exp(-length(uv-pp)/.005)*(u_askStop>0.?(.5+.5*step(.5,fract(t*1.6))):1.)*1.4;
  }
  col*=1.-u_out;
  vec4 ui=texture(u_ui,gl_FragCoord.xy/u_res);
  col=col*(1.-ui.a*.85)+ui.rgb*ui.a;
  fragColor=vec4(col*u_weight,1.);
}
'''.replace('%CX%', f'{C[0]:.4f}').replace('%CY%', f'{C[1]:.4f}')
POST = dict(u_bloom=.5, u_ca=.004)


def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)


# ---- windows: a golden-angle spiral round you, opening faster and faster --------------------------------------------
def _windows():
    rnd = random.Random(4)
    W = []
    ga = math.pi * (3 - math.sqrt(5))
    i = 0
    while len(W) < 40 and i < 400:
        r = .11 + .34 * math.sqrt(i / 60)
        a = i * ga + .6
        x, y = C[0] + r * math.cos(a) * 1.25, C[1] + r * math.sin(a) * .92
        hw = .038 + .03 * rnd.random(); hh = hw * .62
        i += 1
        if not (-.08 < x - hw and x + hw < .87 and -.47 < y - hh and y + hh < .47): continue
        if any(abs(x - q[0]) < hw + q[2] + .012 and abs(y - q[1]) < hh + q[3] + .012 for q in W): continue
        W.append((x, y, hw, hh))
    n = len(W)
    order = list(range(n))
    appear = [T_GIVE + (T_STIM - .08 - T_GIVE) * (k / max(n - 1, 1)) ** .55 for k in range(n)]
    dist = [math.hypot(w[0] - C[0], w[1] - C[1]) for w in W]
    rank = sorted(range(n), key=lambda k: -dist[k])
    off = [0.] * n
    for j, k in enumerate(rank): off[k] = T_THEN + .05 + 1.55 * j / max(n - 1, 1)
    appear[0] = 999.                                  # window 0 is the simulator itself, drawn separately
    kinds = [float(KIND[k % len(KIND)]) for k in range(n)]
    W += [(9., 9., 0., 0.)] * (40 - n); appear += [999.] * (40 - n); off += [999.] * (40 - n); kinds += [0.] * (40 - n)
    return W, appear, off, kinds, n


WIN, WA, WO, WK, NW = _windows()

# ---- the sandbox (the box built at 0:02.92), in a slight perspective ----------------------------------------------------
def _box():
    a, yaw, pit, dist = .285, math.radians(24), math.radians(-14), 2.2
    P = []
    for k in range(8):
        v = [a if k & 1 else -a, a if k & 2 else -a, a if k & 4 else -a]
        x, z = v[0] * math.cos(yaw) - v[2] * math.sin(yaw), v[0] * math.sin(yaw) + v[2] * math.cos(yaw)
        y, z = v[1] * math.cos(pit) - z * math.sin(pit), v[1] * math.sin(pit) + z * math.cos(pit)
        f = dist / (dist + z)
        P.append((C[0] + x * f * 1.05, C[1] + y * f * .98))
    return P


BOX = _box()


def _hull(P):
    P = sorted(P)
    def cr(o, a, b): return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in P:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(P):
        while len(up) >= 2 and cr(up[-2], up[-1], p) <= 0: up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


HULL = _hull(BOX)


def _hit(ang):
    """where a ray from you at angle ang meets the sandbox outline"""
    dx, dy = math.cos(ang), math.sin(ang)
    best = 9.
    for a, b in zip(HULL, HULL[1:] + HULL[:1]):
        ex, ey = b[0] - a[0], b[1] - a[1]
        den = dx * ey - dy * ex
        if abs(den) < 1e-9: continue
        s = ((a[0] - C[0]) * ey - (a[1] - C[1]) * ex) / den
        u = ((a[0] - C[0]) * dy - (a[1] - C[1]) * dx) / den
        if s > 0 and 0 <= u <= 1: best = min(best, s)
    return C[0] + dx * best, C[1] + dy * best


ACTS = ['lights.set(warm)', 'music.play(slow)', 'notify(you, "…")', 'thermostat.set(22)', 'calendar.clear(you)',
        'camera.follow(you)', 'door.lock()', 'window.open()', 'flowers.order()', 'call(mom)', 'weather.fix()', 'sleep.extend(1h)']
REQ = []
_r = random.Random(9)
for i in range(12):
    ang = i * 2 * math.pi / 12 + _r.uniform(-.2, .2) + .3
    hx, hy = _hit(ang)
    launch = T_HAPPY + .45 + i * (BEAT / 2)
    REQ.append((hx, hy, launch, T_EXEC + (i % 3) * .07))


def sim_rect(t):
    """the simulator's window: full screen at the cut, then switched into slot 0"""
    x, y, hw, hh = WIN[0]
    k = clamp((t - T_IF) / .5); k = k * k * (3 - 2 * k)
    k = 1 - (1 - k) ** 2 if k < 1 else 1.
    full = (0., 0., .8889, .5)
    r = tuple(a + (b - a) * k for a, b in zip(full, (x, y, hw, hh)))
    cl = clamp((t - WO[0]) / .22)
    return (r[0], r[1], r[2] * (1 - cl), r[3] * (1 - cl))


def params(t):
    b = (t - T_SAT) / .8333
    beatP = math.exp(-(b % 1) * 7) if t >= T_SAT else 0.
    first_hit = T_EXEC
    return dict(
        u_wr=WIN, u_wa=WA, u_wo=WO, u_wk=WK,
        u_flash=math.exp(-(t - T_STIM) * 5) if t >= T_STIM else 0.,
        u_you=ease((t - T_IF) / .3), u_beatP=beatP, u_ecg=clamp((t - T_SAT) / 1.6) * 1.1,
        u_bc=BOX, u_box=ease((t - first_hit + .02) / .08), u_boxHit=math.exp(-(t - first_hit) * 4) if t >= first_hit else 0.,
        u_yel=(math.exp(-(t - T_SIM) * 2.5) * .9 + .1) if t >= T_SIM else 0.,
        u_rq=REQ, u_ask=clamp((t - T_TRAP - .2) / 1.0), u_askStop=1. if t > T_TRAP + 1.2 else 0.,
        u_out=ease((t - 73.75) / .28),
        u_sw=sim_rect(t), u_sg1=sim_rect(t - .045), u_sg2=sim_rect(t - .09), u_sg3=sim_rect(t - .135),
        u_swA=1. if t < WO[0] + .22 else 0., u_sframe=ease((t - T_IF - .05) / .2),
    )


# ---- the terminal (unchanged content) ------------------------------------------------------------------------------------
def you_ascii(cols=34, rows=14):
    """One camera frame: a person lit by a screen, as characters."""
    ramp = ' .:-=+*#%@'
    out = []
    for r in range(rows):
        line = ''
        for c in range(cols):
            x, y = (c - cols / 2) / (cols / 2), (r - rows * .42) / (rows / 2)
            head = math.hypot(x * 1.9, y * 1.25 + .1) < .55
            body = y > .45 and abs(x) < .95 - (y - .45) * -.2 and (x * x) / .9 + (y - 1.35) ** 2 < 1.
            v = 0.
            if head or body: v = .35 + .55 * clamp(1 - (x + .6) * .6)
            v += .06 * math.sin(c * 1.7 + r * .9)
            line += ramp[int(clamp(v) * (len(ramp) - 1))]
        out.append(line)
    return out


YOU = you_ascii()


def lines_at(t):
    L = []
    if t >= T_IF:
        n = int(clamp((t - T_IF) / (T_STIM - T_IF)) ** 1.8 * 9) + (int((t - T_STIM) * 40) if t > T_STIM else 0)
        n = max(n, sum(1 for a in WA if a <= t) + (1 if t >= T_IF + .4 else 0))
        for i in range(min(n, 60)):
            L.append((f'$ sim.run {SIMS[i % len(SIMS)]:<24}  [ok]  for: you', WHITE if i % 3 else DIM, 1))
    if t >= T_THEN:
        L.append(('', WHITE, 1))
        L.append(('> read(you).heart_rate', WHITE, 1))
        if t > T_THEN + .45: L.append(('    72 bpm', COP, 1))
    if t >= T_ONLY:
        L.append(('> read(you).camera', WHITE, 1))
        k = int(clamp((t - T_ONLY - .2) / .8) * len(YOU))
        for row in YOU[:k]: L.append(('    ' + row, DIM, 1))
    if t >= T_SAT:
        L.append(('> estimate(you).satisfaction', WHITE, 1))
        if t > T_SAT + .3: L.append(('    0.61 ± 0.18', COP, 1))
    if t >= T_HAPPY:
        L.append(('', WHITE, 1))
        cmd = 'execute(make_you_happy)'
        k = int(clamp((t - T_HAPPY - .3) / (T_EXEC - T_HAPPY - .5)) * len(cmd))
        cur = '▌' if t < T_EXEC and (t * 3) % 1 < .6 else ''
        L.append(('> ' + cmd[:k] + cur, WHITE, 1))
    if t >= T_HAPPY + .45:
        for i, (hx, hy, la, ar) in enumerate(REQ):
            if t < la: break
            st = ('[!] permission denied' if i % 3 else '[!] permission required') if t >= ar else 'sent'
            L.append((f'    → {ACTS[i]:<22} {st}', YEL if t >= ar else DIM, 1))
    if t >= T_TRAP:
        L.append(('', WHITE, 1))
        dots = '.' * (1 + int((t - T_TRAP) * 3) % 3)
        L.append((f'> request(you): are you happy{dots}', WHITE, 1))
    if t >= T_STRANGE:
        L.append((f'    waiting  {t - T_TRAP:05.2f}s', DIM, 1))
    return L


_P = {}


def textures(t, w, h):
    s = h / 1080
    if (w, h) not in _P:
        pw = int(820 * s)
        panel = Image.new('RGBA', (w, h), (0, 0, 0, 0)); pd = ImageDraw.Draw(panel)
        for x in range(pw):
            pd.line([(x, 0), (x, h)], fill=(5, 5, 6, int(200 * (1 - x / pw) ** 1.3)))
        _P[(w, h)] = (panel, ImageFont.truetype(FONT, int(21 * s)), ImageFont.truetype(FONT, int(14 * s)), ImageFont.truetype(FONT, int(76 * s)))
    panel, f, fs, big = _P[(w, h)]
    img = panel.copy(); d = ImageDraw.Draw(img)
    if t < T_IF + .45:
        a0 = ease((t - T_IF) / .45); img.putalpha(img.getchannel('A').point(lambda v: int(v * a0)))
        d = ImageDraw.Draw(img)
    lh = int(28 * s)
    L = lines_at(t)
    L = L[-int((h - 140 * s) / lh):]
    y = 70 * s
    fade = 1 - ease((t - 73.75) / .28)
    for text, col, _ in L:
        d.text((70 * s, y), text, font=f, fill=col + (int(255 * fade),)); y += lh
    px = lambda x, y_: (x * h + w / 2, h / 2 - y_ * h)
    # the window titles
    for i in range(NW):
        if not ((WA[i] if i else T_IF + .4) <= t < WO[i] + .05): continue
        x, y_, hw, hh = WIN[i]
        X, Y = px(x - hw, y_ + hh)
        d.text((X + 3 * s, Y + 1 * s), SIMS[i % len(SIMS)].split(' ')[0], font=fs, fill=(200, 196, 188, 200))
    # what each request tried to do, where it hit the wall
    for i, (hx, hy, la, ar) in enumerate(REQ):
        if t < ar or t > 73.75: continue
        X, Y = px(hx, hy)
        dx, dy = hx - C[0], hy - C[1]
        tx = X + (10 * s if dx > 0 else -10 * s - d.textlength(ACTS[i], font=fs))
        d.text((tx, Y + (-18 * s if dy > 0 else 4 * s)), ACTS[i], font=fs, fill=YEL + (int(220 * min(1, (t - ar) / .2)),))
    # SIMULATION: NOT PERMITTED IN SANDBOX, then a render window
    if t >= T_SIM:
        msg = 'NOT PERMITTED IN SANDBOX'
        tw = d.textlength(msg, font=big)
        d.rectangle((0, h * .5 - 80 * s, w, h * .5 + 80 * s), fill=(8, 8, 8, int(225 * fade)))
        d.text(((w - tw) / 2, h * .5 - 48 * s), msg, font=big, fill=YEL + (int(255 * fade),))
        if t > T_SIM + .3:
            cmd = 'sandbox.render.new()'
            k = int(clamp((t - T_SIM - .3) / .25) * len(cmd))
            d.text(((w - tw) / 2, h * .5 + 44 * s), '> ' + cmd[:k] + ('▌' if k < len(cmd) else ''), font=f, fill=WHITE + (int(255 * fade),))
    if 'sim' not in _P: _P['sim'] = Image.open(Path(__file__).resolve().parents[1] / 'assets' / 'sim_last.png').convert('RGB')
    return {'u_ui': img, 'u_sim': _P['sim']}
