"""s12 · 2:13.5–2:24.8  the paper is blown away; the terminal; execute(make_you_happy) typed faster and shorter
until it is only exe; EXE floods the screen; the flood's density becomes the ASCII eye, which starts to look around.
Hands over to the teletype shot (t06) at 2:24.8 with the same eye field and the same iris motion."""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

import importlib.util
_T7 = Path(__file__).resolve().parents[2] / 'tests' / 't07_eye' / 'render.py'
_spec = importlib.util.spec_from_file_location('t07eye', _T7); T7 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(T7)
_src7 = T7.build_src()
EYE_GLSL = ('''const float NG=%d., NR=10., NJ=%d., EXCL=%d.;
const float COLS=200., ROWS=78.;
float LOD=0.;
float glyphMask(float g, vec2 f){ if(g<.5) return 0.; f=clamp(f,vec2(.02),vec2(.98)); return textureLod(u_glyphs,vec2((g+f.x)/NG,f.y),LOD).r; }
''' % (len(T7.CHARS), len(T7.JUNK), T7.CHARS.index('!'))) + _src7[_src7.index('// the eye, in eye space'):_src7.index('void main(){')]
GE, GX = T7.CHARS.index('E'), T7.CHARS.index('X')
_slash = T7.JUNK.index(chr(92)), T7.JUNK.index('/'), T7.JUNK.index('|')

SRC = r'''#version 330
uniform vec2 u_res; uniform float u_time, u_weight;
uniform float u_bang; uniform vec2 u_iris; uniform float u_gapA, u_lid, u_pupil;
uniform float u_blow;           // paper strips blown away 0..1
uniform float u_flood;          // EXE flood coverage 0..1
uniform float u_eyeMix;         // flood -> eye field 0..1
uniform float u_typed[12];      // (unused by the eye field; kept for the shared code)
uniform sampler2D u_glyphs, u_ui, u_last;
uniform float u_deg, u_glitch;   // the judgement page degrading into characters; the hit
out vec4 fragColor;
#define PI 3.14159265
float h12(vec2 p){ vec3 p3=fract(vec3(p.xyx)*.1031); p3+=dot(p3,p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }
float vn(vec2 p){ vec2 i=floor(p),f=fract(p); f=f*f*(3.-2.*f);
  return mix(mix(h12(i),h12(i+vec2(1,0)),f.x),mix(h12(i+vec2(0,1)),h12(i+vec2(1,1)),f.x),f.y); }
float fbm(vec2 p){ float s=0.,a=.5; for(int i=0;i<4;i++){ s+=a*vn(p); p=p*2.03+1.7; a*=.5; } return s; }
''' + EYE_GLSL + r'''
const float GE=%GE%., GX=%GX%., SLB=%SLB%., SLF=%SLF%., SLP=%SLP%.;
// one character cell of the eye study: the garbage field, or the eye (steady), or a lash
vec3 cellColor(float col, float row, vec2 f, vec2 cc){
  vec2 ek=eye(cc);
  float gl, ink;
  if(ek.y<.5){
    float rate=4.+20.*h12(vec2(col,row)*.7);
    float tick=floor(u_time*rate+h12(vec2(row,col))*9.);
    gl=NR+floor(h12(vec2(col,row)+tick*.173)*NJ);
    float patch=vn(cc*6.+vec2(u_time*.3,0.));
    ink=.06+.17*patch*patch+.3*step(.985,h12(vec2(col,row)+tick));
    vec3 c=vec3(.62,.66,.62);
    float wave=u_bang*1.3-length(cc*vec2(.8,1.))+.1*h12(vec2(col,row));   // it stares at you: red '!' from the eye outward
    if(u_bang>0.&&wave>0.){ gl=EXCL; ink=.55+.45*step(.5,fract(u_time*9.+h12(vec2(row,col)))); c=vec3(1.,.16,.12); }
    return c*ink*glyphMask(gl,f);
  } else if(ek.y<1.5){
    float d=ek.x;
    float jit=h12(vec2(col,row)+floor(u_time*3.)*.37);
    gl=clamp(floor(d*9.+(jit-.5)*.9),0.,9.);
    ink=.15+.85*pow(d,1.1);
    return vec3(.92,.93,.9)*ink*glyphMask(gl,f);
  }
  gl=NR+(cc.x<-.08?SLB:(cc.x>.08?SLF:SLP));
  return vec3(.92,.93,.9)*ek.x*glyphMask(gl,f);
}
vec3 field(vec2 uv){
  vec2 cell=vec2(1.72/COLS,.96/ROWS);
  LOD=max(log2(48./(cell.x*u_res.y)),0.);
  vec2 g=(uv+vec2(.86,-.48))/cell*vec2(1.,-1.);
  float col=floor(g.x), row=floor(g.y);
  vec2 f=vec2(fract(g.x),1.-fract(g.y));
  if(col<0.||col>COLS-1.||row<0.||row>=ROWS) return vec3(0.);
  vec2 cc=vec2((col+.5)*cell.x-.86,.48-(row+.5)*cell.y);
  float r1=h12(vec2(col,row)*.77+3.1), r2=h12(vec2(row,col)*.53+7.3);
  vec3 c=vec3(0.);
  if(r1<u_flood){                                            // the flood: EXE EXE EXE
    float k=mod(col+row*2.,4.);
    float gl=k==1.?GX:(k==3.?0.:GE);
    c=vec3(.9,.92,.9)*glyphMask(gl,f)*(.55+.25*h12(vec2(col,row)));
  }
  if(r2<u_eyeMix) c=cellColor(col,row,f,cc);                 // the flood settles into the garbage and the eye
  return c;
}

// the knife cut through (0,-.4): a thin ragged gap, shadowed inside, one lip catching the light.
// returns the colour after the cut; w = half gap width (0 = not yet opened)
vec3 knifeCut(vec3 c, vec2 uv, float w, float PXs){
  vec2 sd=normalize(vec2(1.,-.35)), nn=vec2(-sd.y,sd.x);
  float along=dot(uv-vec2(0.,-.4),sd), across=dot(uv-vec2(0.,-.4),nn);
  if(w<=0.) return c;
  float wr=w*(1.+.45*(vn(vec2(along*55.,1.3))-.5)+.25*(vn(vec2(along*260.,7.))-.5));
  float gap=1.-smoothstep(wr-PXs,wr+PXs,abs(across));
  vec3 inside=vec3(.004)+vec3(.02,.015,.01)*smoothstep(-wr,wr,across);          // light falls in from one side
  c=mix(c,inside,gap);
  float lip=exp(-abs(across-wr)*900.)*step(0.,across);                              // upper lip catches the light
  float sh=exp(-abs(-across-wr)*300.)*step(across,0.);                              // lower lip in shadow
  c+=vec3(.55,.48,.38)*.35*lip;
  c*=1.-.45*sh;
  return c;
}
vec3 parchment(vec2 p){
  vec3 c=vec3(.62,.5,.36)*(.55+.6*fbm(p*4.))*.085;
  c=knifeCut(c,p,.012,1./u_res.y);
  vec2 pe=abs(p)-vec2(.82,.48);
  return c*(1.-smoothstep(-.02,.01,max(pe.x,pe.y)));
}
// ---- the page, degrading: pixels → coarser blocks → characters → gone -----------------------------------------
vec3 ungrade(vec3 d){                                   // display colour back to scene light
  vec3 x=pow(max(d,vec3(0.)),vec3(2.2));
  vec3 a=2.51-2.43*x, b=.03-.59*x, c=-.14*x;
  return (-b+sqrt(b*b-4.*a*c))/(2.*a)/1.05;
}
vec3 lastAt(vec2 uv, float split){                      // the saved frame at screen uv (height units), with an RGB split
  vec2 s=uv*vec2(u_res.y/u_res.x,1.)+.5;
  vec3 c=vec3(texture(u_last,s+vec2(split,0.)).r,texture(u_last,s).g,texture(u_last,s-vec2(split,0.)).b);
  vec2 d=s-.5; return ungrade(c)/(1.-.9*dot(d,d));
}
vec3 degraded(vec2 uv){
  vec2 cell=vec2(1.62/COLS,.92/ROWS)*3.;                // coarse: readable characters
  float x=u_deg;
  // the hit: rows of the page thrown sideways for a few frames
  float band=floor(uv.y*28.+floor(u_time*60.)*3.1);
  uv.x+=u_glitch*(h12(vec2(band,floor(u_time*60.)))-.5)*.09*step(.55,h12(vec2(band,7.)));
  float split=u_glitch*.006+x*.002;
  if(x<.45){                                            // blocks growing to the size of a character cell
    float k=mix(1./u_res.y,cell.x,pow(x/.45,2.));
    vec2 b=(floor(uv/vec2(k,k*cell.y/cell.x))+.5)*vec2(k,k*cell.y/cell.x);
    vec2 sb=b*vec2(u_res.y/u_res.x,1.)+.5;
    vec3 dc=vec3(texture(u_last,sb+vec2(split,0.)).r,texture(u_last,sb).g,texture(u_last,sb-vec2(split,0.)).b);
    float lv=mix(64.,6.,x/.45);                          // fewer and fewer levels
    dc=floor(dc*lv+.5)/lv;
    vec2 d=sb-.5;
    return ungrade(clamp(dc,0.,.98))/(1.-.9*dot(d,d));
  }
  // one character per cell, chosen by the cell's brightness; colours drain to the terminal's grey
  vec2 g=(uv+vec2(.81,-.46))/cell*vec2(1.,-1.);
  float col=floor(g.x), row=floor(g.y);
  vec2 f=vec2(fract(g.x),1.-fract(g.y));
  vec2 cc=vec2((col+.5)*cell.x-.81,.46-(row+.5)*cell.y);
  vec3 c=lastAt(cc,split);
  vec2 sc=cc*vec2(u_res.y/u_res.x,1.)+.5;
  vec3 disp=texture(u_last,sc).rgb;                     // the frame's own colour (no hue shift)
  float L=clamp(log2(max(dot(c,vec3(.3,.55,.15)),1e-4)/.018)/5.2,0.,1.);
  float gi=floor(L*9.99);
  LOD=max(log2(48./(cell.x*u_res.y)),0.);
  float m=glyphMask(gi,f);
  float y=clamp((x-.45)/.3,0.,1.);                       // blocks → glyphs
  vec3 block=ungrade(clamp(floor(disp*6.+.5)/6.,0.,.98));
  float z=clamp((x-.72)/.28,0.,1.);                      // then grey, then gone
  vec3 gc=mix(pow(disp,vec3(2.2))*2.2+vec3(.015),vec3(.9,.92,.9)*L*.9,z*.8)*m;
  return mix(block,gc,y)*(1.-z*z);
}

void main(){
  vec2 uv=(gl_FragCoord.xy-.5*u_res)/u_res.y;
  if(u_deg>=0.&&u_deg<1.){ vec3 c=degraded(uv); vec4 ui0=texture(u_ui,gl_FragCoord.xy/u_res); c=mix(c,ui0.rgb,ui0.a); fragColor=vec4(c*u_weight,1.); return; }
  vec3 col=vec3(.012)+field(uv);
  vec4 ui=texture(u_ui,gl_FragCoord.xy/u_res);
  col=mix(col,ui.rgb,ui.a);
  // the torn parchment, blown away in strips (drawn over the terminal until it is gone)
  if(u_blow<1.){
    for(int k=0;k<7;k++){
      float fk=float(k);
      float y0=-.5+fk/7., y1=y0+1./7.;
      float delay=h12(vec2(fk,2.))*.35;
      float b=clamp((u_blow-delay)/(1.-delay),0.,1.); b=b*b;
      vec2 off=vec2(1.6+.6*h12(vec2(fk,4.)),.5+.7*h12(vec2(fk,5.)))*b;
      float ang=(h12(vec2(fk,6.))-.3)*2.2*b;
      vec2 c=vec2(0.,(y0+y1)*.5);
      vec2 p=uv-c-off; float ca=cos(-ang), sa=sin(-ang); p=mat2(ca,sa,-sa,ca)*p; p+=c;
      if(p.y>y0&&p.y<y1&&abs(p.x)<.9) { col=parchment(p)+vec3(.02)*b; }
    }
  }
  fragColor=vec4(col*u_weight,1.);
}
'''.replace('%GE%', str(GE)).replace('%GX%', str(GX)).replace('%SLB%', str(_slash[0])).replace('%SLF%', str(_slash[1])).replace('%SLP%', str(_slash[2]))
POST = dict(u_bloom=.4, u_ca=.005)
FONT = 'C:/Windows/Fonts/CascadiaMono.ttf'
T0, T_TYPE, T_FLOOD, T_EYE, T_LOOK, END = 133.5, 134.0, 137.4, 141.06, 141.988, 144.8   # (from 2:21.91 after s11; the eye forms 141.06–141.91)
T_HIT, T_GONE = 133.230, 133.95


def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)


T_STARE, T_BANG, T_END = 145.5, 145.55, 147.66
LOOK = [(141.06, (0., 0.)), (141.988, (-.25, .05)), (142.226, (.28, -.03)), (142.5, (-.1, .1)), (142.65, (.2, .08)),
        (142.8, (-.22, -.06)), (142.95, (.05, -.1)), (143.7, (.3, .05)), (144.5, (-.2, -.02)), (T_STARE, (0., 0.))]


def look(t):
    x, y = LOOK[0][1]
    for t0, (tx, ty) in LOOK:
        if t >= t0:
            k = 1 - (1 - clamp((t - t0) / .07)) ** 3
            x, y = x + (tx - x) * k, y + (ty - y) * k
    return x, y


def gap_angle(t):
    """the gap points the way the eye last turned; staring at you, it turns straight down"""
    ang = math.radians(-90.)
    prev = LOOK[0][1]
    for t0, tgt in LOOK[1:]:
        if t < t0 - .04: break
        dx, dy = tgt[0] - prev[0], tgt[1] - prev[1]
        if math.hypot(dx, dy) > 1e-3:
            d = (math.atan2(dy, dx) - ang + math.pi) % (2 * math.pi) - math.pi
            ang += d * ease((t - t0 + .04) / .12)
        prev = tgt
    down = ease((t - T_STARE - .05) / .2)
    return ang + (((math.radians(-90.) - ang + math.pi) % (2 * math.pi)) - math.pi) * down


def params(t):
    x, y = look(t)
    live = ease((t - T_EYE) / 1.8)
    x += .006 * math.sin(t * 13.) * live; y += .005 * math.sin(t * 9.1) * live
    blink = 1. - math.exp(-((t - 144.1) / .07) ** 2)
    return dict(u_deg=(t - T_HIT) / (T_GONE - T_HIT) if T_HIT <= t < T_GONE else -1.,
                u_glitch=1. - ease((t - T_HIT - .03) / .07) if t >= T_HIT else 0.,
                u_bang=clamp((t - T_BANG) / .45) if t >= T_BANG else 0., u_iris=(x, y), u_gapA=gap_angle(t),
                u_lid=blink, u_pupil=.15 + .07 * ease((t - T_STARE - .05) / .35),
                u_blow=1., u_flood=ease((t - T_FLOOD) / 1.6), u_eyeMix=ease((t - T_EYE) / .85), u_typed=[0.] * 12)


# the degradation: the command typed again and again, faster, shorter
CMD = 'execute(make_you_happy)'
LINES = []
_tt = T_TYPE
for k in range(46):
    L = len(CMD) if k < 6 else max(3, int(len(CMD) * (1 - (k - 6) / 30)))
    s = CMD[:L]
    if L <= 4: s = 'exe'
    LINES.append((_tt, s))
    _tt += max(.045, .42 * .88 ** k)
_glyphs = {}


def textures(t, w, h):
    if 'g' not in _glyphs: _glyphs['g'] = T7.atlas()
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    s = h / 1080
    f = ImageFont.truetype(FONT, int(26 * s)); lh = int(34 * s)
    fade = 1 - ease((t - T_FLOOD - .4) / 1.2)
    if fade > 0 and t >= T_TYPE:
        shown = [(tt, x) for tt, x in LINES if t >= tt]
        rows = []
        for tt, x in shown:
            k = int(clamp((t - tt) / max(.04, len(x) * .012)) * len(x))
            rows.append(('> ' if x != 'exe' else '') + x[:k])
        # exe fills lines, several per row, faster and faster
        packed = []
        for r in rows:
            if r == 'exe' and packed and packed[-1].startswith('exe') and len(packed[-1]) < 60: packed[-1] += ' exe'
            else: packed.append(r)
        packed = packed[-int((h - 120 * s) / lh):]
        for i, r in enumerate(packed):
            d.text((90 * s, 60 * s + i * lh), r, font=f, fill=(226, 224, 216, int(255 * fade)))
    if 'last' not in _glyphs: _glyphs['last'] = Image.open(Path(__file__).resolve().parents[1] / 'assets' / 'judgement_last.png').convert('RGB')
    return {'u_ui': img, 'u_glyphs': _glyphs['g'], 'u_last': _glyphs['last']}
