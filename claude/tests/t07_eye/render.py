"""t07 · ASCII eye study (standalone). A full field of garbage characters that never stops changing; in the middle an eye
drawn by density — rounder than before and filled: shaded sclera with the lid's shadow, an iris of radial fibres with a
dark limbal edge (the iris itself is still the rotating gap ring), a dark pupil with a catch-light, a heavy upper lid with
lashes, a thin lower lid, the tear duct. The eye's characters are steady; the garbage around it is not.
python render.py [--stills a,b] [--out file.mp4]"""
import sys, math, argparse, time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'engine'))
from gl import Renderer, encode, save_png

RAMP = ' .:-=+*#%@'
JUNK = ''.join(chr(c) for c in range(33, 127) if chr(c) not in RAMP)
CHARS = RAMP + JUNK
CW, CH = 48, 80


def atlas():
    f = ImageFont.truetype('C:/Windows/Fonts/CascadiaMono.ttf', 64)
    img = Image.new('L', (CW * len(CHARS), CH), 0); d = ImageDraw.Draw(img)
    for i, ch in enumerate(CHARS):
        b = d.textbbox((0, 0), ch, font=f)
        d.text((i * CW + (CW - (b[2] - b[0])) / 2 - b[0], 6), ch, font=f, fill=255)
    return img


SRC = r'''#version 330
uniform vec2 u_res; uniform float u_time, u_weight;
uniform vec2 u_iris; uniform float u_gapA, u_lid, u_pupil, u_bang;
uniform sampler2D u_glyphs;
out vec4 fragColor;
#define PI 3.14159265
const float NG=%NG%., NR=10., NJ=%NJ%., EXCL=%EX%.;
const float COLS=200., ROWS=78.;
float LOD=0.;
float h12(vec2 p){ vec3 p3=fract(vec3(p.xyx)*.1031); p3+=dot(p3,p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }
float vn(vec2 p){ vec2 i=floor(p),f=fract(p); f=f*f*(3.-2.*f);
  return mix(mix(h12(i),h12(i+vec2(1,0)),f.x),mix(h12(i+vec2(0,1)),h12(i+vec2(1,1)),f.x),f.y); }
float glyphMask(float g, vec2 f){ if(g<.5) return 0.; f=clamp(f,vec2(.02),vec2(.98)); return textureLod(u_glyphs,vec2((g+f.x)/NG,f.y),LOD).r; }

// the eye, in eye space: x across (±1 = the corners), y up; returns (density, kind) — kind 0 junk, 1 eye, 2 lash
vec2 eye(vec2 p){
  float W=.47;                                           // half width of the eye in screen height units
  vec2 e=p/W;
  float open=u_lid;                                       // 1 open .. 0 shut
  float top=.66*pow(max(1.-e.x*e.x,0.),.62)*open;          // upper lid (higher, rounder)
  float bot=-.5*pow(max(1.-e.x*e.x,0.),.8)*mix(.25,1.,open);
  bool inside=e.y<top&&e.y>bot&&abs(e.x)<1.;
  float dT=abs(e.y-top), dB=abs(e.y-bot);
  // lids: a heavy upper line with lashes, a thin lower line
  float upper=(1.-smoothstep(.0,.07,dT))*step(abs(e.x),1.02);
  float lower=(1.-smoothstep(.0,.035,dB))*step(abs(e.x),1.);
  if(!inside){
    float lash=0.;
    if(e.y>top&&e.y<top+.22&&abs(e.x)<.92){               // lashes: short strokes leaning outward
      float k=floor((e.x+1.)*22.);
      float lx=(k+.5)/22.-1.;
      float lean=lx*.35;
      float t=(e.y-top)/.22;
      float xl=lx+lean*t;
      lash=(1.-smoothstep(.0,.018,abs(e.x-xl)))*(1.-t)*step(.25,h12(vec2(k,3.)))*open;
    }
    float d=max(upper*.95,lower*.7);
    if(lash>.1) return vec2(max(d,lash),2.);
    return vec2(d,d>.2?1.:0.);
  }
  // sclera: a sphere, lit from above-left, the upper lid shading it
  float sph=sqrt(max(1.-dot(e*vec2(.9,1.25),e*vec2(.9,1.25)),0.));
  float d=.45+.35*sph;
  d*=.55+.45*smoothstep(.0,.3,dT);                        // shadow under the upper lid
  d+=.1*(vn(p*40.)-.5);
  // tear duct at the inner corner
  d=max(d,(1.-smoothstep(.0,.08,length(e-vec2(-.93,-.05))))*.55);
  // iris: the rotating gap ring, radial fibres inside it, a dark limbal edge; pupil dark with a catch-light
  vec2 q=(p-u_iris*W)/W; float r=length(q), a=atan(q.y,q.x);
  float R=.42;
  if(r<R){
    float fib=.5+.5*sin(a*34.+vn(vec2(a*6.,r*9.))*5.);
    d=.18+.42*fib*smoothstep(.13,.4,r)+.1*vn(vec2(a*20.,r*30.));
    d*=.45+.55*smoothstep(R+.01,R-.07,r);                 // limbal ring, dark
    float gap=abs(mod(a-u_gapA+PI,2.*PI)-PI);
    float ring=(1.-smoothstep(.03,.05,abs(r-.3)))*step(radians(27.),gap);
    d=max(d,ring*.95);
    d*=mix(.6,1.,smoothstep(.0,.25,dT));
  }
  if(r<u_pupil) d=.0;                                     // pupil: empty (dilates at the end)
  d=max(d,(1.-smoothstep(.0,.045,length(q-vec2(-.1,.12))))*1.);  // catch-light
  d=max(d,max(upper*.95,lower*.7));
  return vec2(clamp(d,0.,1.),1.);
}

void main(){
  vec2 uv=(gl_FragCoord.xy-.5*u_res)/u_res.y;
  vec2 cell=vec2(1.72/COLS,.96/ROWS);
  vec2 g=(uv+vec2(.86,-.48))/cell*vec2(1.,-1.);
  float col=floor(g.x), row=floor(g.y);
  vec2 f=vec2(fract(g.x),1.-fract(g.y));
  vec2 cc=vec2((col+.5)*cell.x-.86,.48-(row+.5)*cell.y);
  LOD=max(log2(48./(cell.x*u_res.y)),0.);
  vec3 col3=vec3(.006);
  if(col>=0.&&col<COLS&&row>=0.&&row<ROWS){
    vec2 ek=eye(cc);
    float gl, ink;
    if(ek.y<.5){
      // the garbage: every cell its own clock; brightness drifts in slow patches
      float rate=4.+20.*h12(vec2(col,row)*.7);
      float tick=floor(u_time*rate+h12(vec2(row,col))*9.);
      gl=NR+floor(h12(vec2(col,row)+tick*.173)*NJ);
      float patch=vn(cc*6.+vec2(u_time*.3,0.));
      ink=.06+.17*patch*patch+.3*step(.985,h12(vec2(col,row)+tick));
      vec3 c=vec3(.62,.66,.62);
      // it looks straight at you: the garbage turns to red '!', from the eye outward
      float wave=u_bang*1.3-length(cc*vec2(.8,1.))+.1*h12(vec2(col,row));
      if(u_bang>0.&&wave>0.){ gl=EXCL; ink=.55+.45*step(.5,fract(u_time*9.+h12(vec2(row,col)))); c=vec3(1.,.16,.12); }
      col3+=c*ink*glyphMask(gl,f);
    } else if(ek.y<1.5){
      float d=ek.x;
      float jit=h12(vec2(col,row)+floor(u_time*3.)*.37);
      gl=clamp(floor(d*9.+(jit-.5)*.9),0.,9.);
      ink=.15+.85*pow(d,1.1);
      col3+=vec3(.92,.93,.9)*ink*glyphMask(gl,f);
    } else {
      float lx=(cc.x);
      gl=NR+float(index_of_slash(cc.x));
      col3+=vec3(.92,.93,.9)*ek.x*glyphMask(gl,f);
    }
  }
  fragColor=vec4(col3*u_weight,1.);
}
'''


def build_src():
    s = SRC.replace('%NG%', str(len(CHARS))).replace('%NJ%', str(len(JUNK))).replace('%EX%', str(CHARS.index('!')))
    # lashes lean outward: '\' on the left half, '/' on the right half, '|' near the middle
    jb, js, jp = JUNK.index('\\'), JUNK.index('/'), JUNK.index('|')
    s = s.replace('float(index_of_slash(cc.x))', f'(cc.x<-.08?{jb}.:(cc.x>.08?{js}.:{jp}.))')
    return s


def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def outc(x): x = clamp(x); return 1 - (1 - x) ** 3


# looking around: saccades between fixations, then straight at you
LOOK = [(0., (0., 0.)), (.9, (-.28, .05)), (1.7, (.3, -.04)), (2.4, (.12, .1)), (3.1, (-.22, -.08)), (3.9, (0., 0.))]


T_STARE, T_BANG = 3.9, 4.15


def look(t):
    x, y = LOOK[0][1]
    for t0, (tx, ty) in LOOK:
        if t >= t0:
            k = outc((t - t0) / .07)
            x, y = x + (tx - x) * k, y + (ty - y) * k
    return x, y


def gap_angle(t):
    """the gap points the way the eye is turning: toward the latest saccade's direction, eased; kept while still"""
    ang = math.radians(-90.)
    prev = LOOK[0][1]
    for t0, tgt in LOOK[1:]:
        if t < t0 - .04: break
        dx, dy = tgt[0] - prev[0], tgt[1] - prev[1]
        if math.hypot(dx, dy) > 1e-3:
            new = math.atan2(dy, dx)
            k = ease((t - t0 + .04) / .12)
            d = (new - ang + math.pi) % (2 * math.pi) - math.pi
            ang = ang + d * k
        prev = tgt
    return ang


def params(t):
    x, y = look(t)
    down = ease((t - T_STARE - .05) / .2)                 # staring at you: the gap turns to point straight down
    ga = gap_angle(t)
    ga = ga + (((math.radians(-90.) - ga + math.pi) % (2 * math.pi)) - math.pi) * down
    x += .006 * math.sin(t * 13.); y += .005 * math.sin(t * 9.1)
    blink = 1. - math.exp(-((t - 2.9) / .07) ** 2)
    return dict(u_iris=(x, y), u_gapA=ga, u_lid=blink,
                u_pupil=.15 + .07 * ease((t - T_STARE - .05) / .35), u_bang=clamp((t - T_BANG) / .45) if t >= T_BANG else 0.)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--w', type=int, default=1920); ap.add_argument('--h', type=int, default=1080)
    ap.add_argument('--sub', type=int, default=2); ap.add_argument('--stills', type=str)
    ap.add_argument('--out', type=str, default=str(HERE / 'eye_study_1080p.mp4'))
    a = ap.parse_args()
    r = Renderer(a.w, a.h, build_src(), subframes=a.sub)
    r.post.update(u_bloom=.35, u_ca=.004)
    G = atlas()
    tex = lambda t: {'u_glyphs': G}
    if a.stills:
        for t in map(float, a.stills.split(',')):
            save_png(r.frame(t, params, tex), a.w, a.h, HERE / f'still_{t:05.2f}.png'); print('still', t, flush=True)
        return
    fps, dur = 60, 5.
    encode(a.out, a.w, a.h, fps, 139.0, dur, (r.frame(i / fps, params, tex) for i in range(int(dur * fps))))
    print('done', a.out)


if __name__ == '__main__':
    main()
