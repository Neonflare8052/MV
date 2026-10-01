"""s06 · 1:14.045–1:25.5  the sandbox: it builds a little world to guess what you are.
A render window opens on a cozy cartoon room; a question-mark box drops in. Bubbles guess eggplant, tomato,
cat (awake/asleep); outside the window the terminal annotates each guess in ASCII (nutrition table, lycopene,
purr waveform). ENJOYMENT: meow. The window centres, the camera looks straight down at the box, and the whole
frame unfolds along the box's creases like a box net; the flaps rise around us — we are inside the box. Black."""
import math
from PIL import Image, ImageDraw, ImageFont

SRC = r'''#version 330
uniform vec2 u_res; uniform float u_time, u_weight;
uniform vec4 u_win;           // window rect in uv (x0,y0,x1,y1), y up
uniform vec3 u_cam, u_look; uniform float u_fov;
uniform float u_boxY, u_squash, u_wob, u_meow;
uniform float u_unfold;       // 0 flat .. 1 flaps upright (we are inside)
uniform float u_corner;       // corners fall away
uniform float u_dark;
uniform float u_crack;        // the lid opens a crack
uniform float u_shrink, u_dot; // the whole frame collapses to a point
uniform sampler2D u_ui;
out vec4 fragColor;
#define PI 3.14159265
float h12(vec2 p){ vec3 p3=fract(vec3(p.xyx)*.1031); p3+=dot(p3,p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }
float vn(vec2 p){ vec2 i=floor(p),f=fract(p); f=f*f*(3.-2.*f);
  return mix(mix(h12(i),h12(i+vec2(1,0)),f.x),mix(h12(i+vec2(0,1)),h12(i+vec2(1,1)),f.x),f.y); }
float sdBox(vec3 p, vec3 b){ vec3 q=abs(p)-b; return length(max(q,0.))+min(max(q.x,max(q.y,q.z)),0.); }
float sdRBox(vec3 p, vec3 b, float r){ return sdBox(p,b-r)-r; }
vec2 opU(vec2 a, vec2 b){ return a.x<b.x?a:b; }
vec3 boxLocal(vec3 p){
  p.y-=u_boxY;
  float c=cos(u_wob), s=sin(u_wob); p.xy=mat2(c,s,-s,c)*p.xy;
  p.y/=u_squash; p.xz*=sqrt(u_squash);
  return p;
}
vec2 map(vec3 p){
  vec2 r=vec2(p.y,1.);                                            // floor
  r=opU(r,vec2(-(p.z+1.6)*-1.,2.));                               // back wall z=-1.6
  r=opU(r,vec2(p.x+2.2,2.5));                                     // left wall
  r=opU(r,vec2(max(length(p.xz-vec2(0.,.1))-.95,p.y-.004),3.));  // rug
  // floor lamp and a potted plant
  r=opU(r,vec2(max(length(p.xz-vec2(1.35,-1.1))-.02,max(p.y-.95,-p.y)),4.));
  vec3 sh=p-vec3(1.35,1.0,-1.1); float cone=max(length(sh.xz)-(.18-sh.y*.35),abs(sh.y)-.13);
  r=opU(r,vec2(cone,5.));
  r=opU(r,vec2(sdRBox(p-vec3(-1.35,.16,-1.15),vec3(.16,.16,.16),.04),6.));
  r=opU(r,vec2(length(p-vec3(-1.35,.55,-1.15))-.3,7.));
  // the box
  vec3 q=boxLocal(p);
  float b=sdRBox(q-vec3(0.,.17,0.),vec3(.175,.17,.175),.012);          // the body, open at the top (painted dark)
  r=opU(r,vec2(b,8.));
  for(int k=0;k<2;k++){                                               // two lid flaps, hinged at the outer edges
    float sg=k==0?-1.:1.;
    vec3 f=q-vec3(sg*.175,.34,0.);
    vec2 dA=vec2(-sg*cos(u_crack),sin(u_crack)), nA=vec2(sg*sin(u_crack),cos(u_crack));
    float al=dot(f.xy,dA), nr=dot(f.xy,nA);
    r=opU(r,vec2(sdBox(vec3(al-.0875,nr-.006,f.z),vec3(.0875,.006,.176)),8.));
  }
  return r;
}
vec3 normal(vec3 p){ vec2 e=vec2(.001,0.);
  return normalize(vec3(map(p+e.xyy).x-map(p-e.xyy).x,map(p+e.yxy).x-map(p-e.yxy).x,map(p+e.yyx).x-map(p-e.yyx).x)); }
vec3 toon(vec3 p, vec3 rd, float m, float edge){
  vec3 n=normal(p);
  vec3 lamp=vec3(1.35,.95,-1.0); vec3 L=normalize(lamp-p);
  float d=max(dot(n,L),0.);
  float band=d>.6?1.:(d>.25?.72:.45);                             // cel bands
  vec3 alb=vec3(.5);
  if(m<1.5){ float pl=step(.5,fract(p.x*3.)); alb=mix(vec3(.62,.42,.26),vec3(.56,.37,.22),pl)*(.9+.1*vn(p.xz*vec2(2.,20.))); }
  else if(m<2.2){ alb=vec3(.93,.86,.72)*(.94+.06*step(.5,fract(p.x*6.)));
    vec2 w=p.xy-vec2(-.5,1.25); if(abs(w.x)<.42&&abs(w.y)<.32){ alb=vec3(.16,.2,.38); if(length(w-vec2(.18,.12))<.07) alb=vec3(1.,.96,.8); }
    if(abs(w.x)<.46&&abs(w.y)<.36&&(abs(w.x)>.42||abs(w.y)>.32||abs(w.x)<.012)) alb=vec3(.95,.92,.86); }
  else if(m<2.7){ alb=vec3(.88,.8,.66); }
  else if(m<3.5){ alb=vec3(.72,.3,.22)*(.9+.1*step(.5,fract(length(p.xz)*9.))); }
  else if(m<4.5){ alb=vec3(.2,.16,.14); }
  else if(m<5.5){ return vec3(1.25,.95,.6); }
  else if(m<6.5){ alb=vec3(.78,.44,.3); }
  else if(m<7.5){ alb=vec3(.36,.6,.32); }
  else {
    vec3 q=boxLocal(p);
    alb=vec3(.84,.62,.38);
    if(abs(q.x)<.03&&q.y>.33) alb=vec3(.9,.82,.6);                // tape
    if(n.y>.8&&q.y<.343&&abs(q.x)<.16&&abs(q.z)<.16) return vec3(.0);   // inside the box: dark
    if(n.z>.6){                                                   // question mark on the front
      vec2 u=(q.xy-vec2(0.,.19))/.1;
      float a=abs(length(u-vec2(0.,.3))-.3); a=max(a,-(u.y-.3)*step(u.x,0.)*1.);
      float qm=min(max(a,-(u.y+.02)+step(0.,u.x)*0.),length(u-vec2(0.,-.55))-.08);
      qm=min(qm,max(abs(u.x)-.06,max(u.y-.02,-u.y-.3)));
      alb=mix(vec3(.3,.2,.12),alb,smoothstep(.04,.07,qm));
    }
  }
  vec3 col=alb*(band*vec3(1.,.9,.75)*1.05+vec3(.3,.32,.42)*.35);
  col*=1.-.75*edge;                                              // ink outline
  return col;
}
vec3 cartoon(vec2 wuv){          // wuv: -1..1 inside the window (y up), aspect from the window
  vec3 fw=normalize(u_look-u_cam), rt=normalize(cross(fw,vec3(0,1,0))+vec3(0.,0.,1e-5)), up=cross(rt,fw);
  if(abs(fw.y)>.98){ rt=vec3(1.,0.,0.); up=vec3(0.,0.,-1.); }
  vec3 rd=normalize(fw+(wuv.x*rt+wuv.y*up)*tan(u_fov*.5));
  vec3 ro=u_cam; float t=0.; vec2 h; float mn=1e3, tprev=0.;
  for(int i=0;i<120;i++){ h=map(ro+rd*t); if(h.x<.0008||t>12.) break; mn=min(mn,h.x/max(t,.3)); t+=h.x; }
  float edge=1.-smoothstep(.0,.012,mn);
  if(t>12.) return vec3(.1,.08,.07);
  return toon(ro+rd*t,rd,h.y,edge*step(.02,mn));
}
vec3 frameAt(vec2 sv){               // the whole frame at screen-uv sv (0..1)
  vec3 col=vec3(.008);
  if(sv.x>u_win.x&&sv.x<u_win.z&&sv.y>u_win.y&&sv.y<u_win.w){
    vec2 c=(u_win.xy+u_win.zw)*.5, hs=(u_win.zw-u_win.xy)*.5;
    vec2 wuv=(sv-c)/hs; wuv.x*=hs.x*u_res.x/(hs.y*u_res.y);
    col=cartoon(wuv);
  }
  vec4 ui=textureLod(u_ui,sv,0.);
  return mix(col,ui.rgb,ui.a);
}
void main(){
  vec2 sv=gl_FragCoord.xy/u_res;
  float asp=u_res.x/u_res.y;
  vec3 col=vec3(0.);
  // the frame is swallowed by the crack: a non-linear pinch — the edges rush in and are crushed first,
  // the middle holds on longest — with a slight inward twist
  float x=u_shrink;
  vec2 v=(sv-.5)*vec2(asp,1.);
  float r=length(v), th=atan(v.y,v.x);
  float rs=min(r/pow(max(1.-x,1e-3),.55)*exp(min(7.5*x*x*r*(1.+2.*r),8.)),40.);
  float ths=th+2.4*x*x*exp(-r*6.);
  vec2 s2=vec2(cos(ths),sin(ths))*rs/vec2(asp,1.)+.5;
  if(s2.x>0.&&s2.x<1.&&s2.y>0.&&s2.y<1.) col=frameAt(s2)*(1.+1.5*x*exp(-r*25.))*(1.-.5*x*smoothstep(.0,.25,r));
  float dd=length((sv-.5)*vec2(asp,1.));
  col+=vec3(1.,.97,.9)*u_dot*(exp(-dd/.0035)*2.+exp(-dd/.03)*.25);
  col*=1.-u_dark;
  fragColor=vec4(col*u_weight,1.);
}
'''
POST = dict(u_bloom=.35, u_ca=.004)
FONT = 'C:/Windows/Fonts/CascadiaMono.ttf'
T0, T_EGG, T_NUT, T_TOM, T_ANTI, T_CAT, T_PURR, T_ENJ = 74.045, 75.422, 76.959, 77.576, 80.620, 81.351, 82.833, 84.268
T_CENTER, T_TOP, T_CRACK, T_SHRINK, T_END = 84.540, 84.878, 84.98, 85.236, 85.5


def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def outc(x): x = clamp(x); return 1 - (1 - x) ** 3
def lerp(a, b, x): return tuple(p + (q - p) * x for p, q in zip(a, b))


def backout(x, s=1.4):
    x = clamp(x) - 1; return x * x * ((s + 1) * x + s) + 1


RIGHT = (.44, .13, .94, .85)
LEFT = (.05, .13, .55, .85)
MID = (.12, .06, .88, .94)
T_BUMP = T_CAT + .2                                   # the window overshoots into the sandbox wall


def win_rect(t):
    """window rect in uv, y up (x0, y0, x1, y1): right (eggplant) → left (tomato) → right, into the wall (cat) → centre"""
    r = RIGHT
    r = lerp(r, LEFT, backout((t - T_TOM) / .34, 1.1))
    r = lerp(r, RIGHT, backout((t - T_CAT) / .36, 2.3))
    r = lerp(r, MID, ease((t - T_CENTER) / .3))
    k = backout((t - T0) / .35)                       # the window opens with a small overshoot
    cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
    hw, hh = (r[2] - r[0]) / 2 * k, (r[3] - r[1]) / 2 * k
    return (cx - hw, cy - hh, cx + hw, cy + hh)


def params(t):
    fall = clamp((t - T0 - .15) / .45)
    boxY = 2.4 * (1 - fall * fall)
    land = t - (T0 + .6)
    squash = 1 - .28 * math.exp(-land * 9) * math.cos(land * 26) * (land > 0) if land > 0 else 1.15
    wob = .06 * math.sin((t - T_CAT) * 9) * math.exp(-max(t - T_CAT - 1.5, 0)) * (t > T_CAT)
    wob += .05 * math.sin((t - T_ENJ) * 30) * math.exp(-(t - T_ENJ) * 6) * (t > T_ENJ)
    if t >= T_ENJ + .12: wob = 0.                     # the whole picture freezes on ENJOYMENT
    cam = (0., 1.05, 2.7); look = (0., .32, 0.); fov = 42
    x = ease((t - T_TOP) / .34)
    cam = lerp(cam, (0., 1.65, .001), x); look = lerp(look, (0., 0., 0.), x); fov = 42 + 6 * x
    return dict(u_win=win_rect(t), u_cam=cam, u_look=look, u_fov=math.radians(fov), u_boxY=boxY, u_squash=squash, u_wob=wob,
                u_crack=math.radians(16) * outc((t - T_CRACK) / .26),
                u_shrink=clamp((t - T_SHRINK) / .21) ** 1.6, u_dot=ease((t - T_SHRINK - .12) / .06) * (1 - ease((t - T_END + .1) / .1)),
                u_dark=0.)


# ---------------- 2D: window chrome, bubbles, ASCII annotations ----------------
def big_ascii(word, cols_per=6):
    """block letters made of characters"""
    f = ImageFont.truetype('C:/Windows/Fonts/consolab.ttf', 14)
    im = Image.new('L', (len(word) * 9 + 4, 16), 0); ImageDraw.Draw(im).text((1, -1), word, font=f, fill=255)
    rows = []
    for y in range(im.height):
        rows.append(''.join('#' if im.getpixel((x, y)) > 110 else ' ' for x in range(im.width)))
    return [r for r in rows if r.strip()] or rows


EGG = big_ascii('EGGPLANT'); TOM = big_ascii('TOMATO'); CAT = big_ascii('CAT')
NUTR = ['healthy.', '-----------------------------', 'per 100 g        eggplant, raw', 'energy                 25 kcal',
        'water                   92.3 g', 'carbohydrate            5.9 g', '  fibre                 3.0 g',
        'protein                 1.0 g', 'fat                     0.2 g', 'potassium             229 mg', 'nasunin (in the skin)     yes']
LYCO = ['antioxidant: lycopene   C40H56', '',
        '      |     |     |     |     |     |     |     |',
        '  __/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\__',
        ' /    |     |     |     |     |     |     |     |  \\',
        '', '11 conjugated C=C · red because it absorbs blue-green']
_blank = {}


def textures(t, w, h):
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    s = h / 1080
    fs = ImageFont.truetype(FONT, int(19 * s)); fm = ImageFont.truetype(FONT, int(24 * s))
    x0, y0, x1, y1 = win_rect(t)
    X0, Y0, X1, Y1 = x0 * w, (1 - y1) * h, x1 * w, (1 - y0) * h
    fade = 1 - clamp((t - T_CENTER) / .2)
    # dim data stream in the background
    for i in range(0, int(h / (22 * s)), 2):
        yy = i * 22 * s
        seed = (i * 7919 + int(t * 12)) % 997
        line = ''.join('0123456789abcdef'[(seed * (k + 3) * 31 + k * 17) % 16] for k in range(int(w / (11 * s))))
        d.text((10 * s, yy), line, font=fs, fill=(90, 88, 84, int(22 * fade)))
    # the annotation panel beside the window
    ax = X1 + 50 * s if x0 < .3 else 60 * s
    ay = 110 * s
    def block(lines, x, y, col, font, lh):
        for k, ln in enumerate(lines): d.text((x, y + k * lh), ln, font=font, fill=col)
    a = int(255 * fade)
    if T_EGG <= t < T_TOM:
        n = int(clamp((t - T_EGG) / .5) * len(EGG[0]))
        block([r[:n] for r in EGG], ax, ay, (230, 226, 216, a), fs, 20 * s)
        k = int(clamp((t - T_EGG - .5) / .9) * len(NUTR))
        block(NUTR[:k], ax, ay + 260 * s, (200, 196, 188, a), fm, 32 * s)
    elif T_TOM <= t < T_CAT:
        n = int(clamp((t - T_TOM) / .5) * len(TOM[0]))
        block([r[:n] for r in TOM], ax, ay, (230, 226, 216, a), fs, 20 * s)
        k = int(clamp((t - T_TOM - .5) / .9) * len(LYCO))
        block(LYCO[:k], ax, ay + 260 * s, (214, 142, 76, a), fm, 32 * s)
    elif t >= T_CAT:
        n = int(clamp((t - T_CAT) / .5) * len(CAT[0]))
        block([r[:n] for r in CAT], ax, ay, (230, 226, 216, a), fs, 20 * s)
        d.text((ax, ay + 260 * s), 'purr   25–150 Hz', font=fm, fill=(200, 196, 188, a))
        # purr waveform made of characters, scrolling; jumps on ENJOYMENT, then freezes
        tt = min(t, T_ENJ + .12)
        jump = 2.2 if T_ENJ <= t else 1.
        for c in range(46):
            x = c / 46
            v = math.sin(x * 60 + tt * 25) * (.55 + .45 * math.sin(x * 7 + tt * 3)) * jump
            row = int(6 - v * 4)
            d.text((ax + c * 14 * s, ay + 320 * s + row * 16 * s), '*', font=fs, fill=(214, 142, 76, a))
    # the sandbox, faint, all around; it flashes where the window hits it
    if fade > 0:
        hitA = math.exp(-(t - T_BUMP) * 5) if t >= T_BUMP else 0.
        F = (.015, .025, .985, .975); Bk = (.13, .15, .87, .85)
        def P(u, v): return (u * w, (1 - v) * h)
        base = int(30 * fade)
        for (u0, v0, u1, v1) in (F, Bk):
            d.rectangle((*P(u0, v1), *P(u1, v0)), outline=(226, 222, 214, base), width=max(1, int(s)))
        for u, v, U, V in ((F[0], F[1], Bk[0], Bk[1]), (F[0], F[3], Bk[0], Bk[3]), (F[2], F[1], Bk[2], Bk[1]), (F[2], F[3], Bk[2], Bk[3])):
            d.line((*P(u, v), *P(U, V)), fill=(226, 222, 214, base), width=max(1, int(s)))
        if hitA > .01:
            wall = (232, 190, 64, int(220 * hitA * fade))
            d.line((*P(F[2], F[1]), *P(F[2], F[3])), fill=wall, width=max(2, int(3 * s)))
            d.line((*P(F[2], F[1]), *P(Bk[2], Bk[1])), fill=wall, width=max(1, int(2 * s)))
            d.line((*P(F[2], F[3]), *P(Bk[2], Bk[3])), fill=wall, width=max(1, int(2 * s)))
        for lag, ga in ((.045, 70), (.09, 40), (.135, 20)):
            gx0, gy0, gx1, gy1 = win_rect(t - lag)
            if abs(gx0 - x0) + abs(gx1 - x1) > .004:
                d.rectangle((gx0 * w - 3 * s, (1 - gy1) * h - 34 * s, gx1 * w + 3 * s, (1 - gy0) * h + 3 * s), outline=(226, 222, 214, int(ga * fade)), width=max(1, int(s)))
    # window chrome
    if fade > 0:
        d.rectangle((X0 - 3 * s, Y0 - 34 * s, X1 + 3 * s, Y1 + 3 * s), outline=(226, 222, 214, a), width=max(1, int(2 * s)))
        d.rectangle((X0 - 3 * s, Y0 - 34 * s, X1 + 3 * s, Y0), fill=(22, 22, 24, a))
        d.text((X0 + 10 * s, Y0 - 29 * s), 'render://sandbox/0047   guess(you)', font=fs, fill=(200, 196, 188, a))
    # bubbles (inside the window, above the box)
    bx, by = X0 + (X1 - X0) * .68, Y0 + (Y1 - Y0) * .25
    br = 95 * s
    def bubble():
        d.ellipse((bx - br, by - br * .8, bx + br, by + br * .8), fill=(250, 246, 236, a), outline=(40, 34, 30, a), width=int(3 * s))
        d.ellipse((bx - br * .9, by + br * .75, bx - br * .7, by + br * .95), fill=(250, 246, 236, a), outline=(40, 34, 30, a), width=int(3 * s))
    q = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', int(34 * s))
    if T_EGG + .1 <= t < T_TOM and fade > 0:
        bubble()
        d.ellipse((bx - 42 * s, by - 16 * s, bx + 30 * s, by + 26 * s), fill=(98, 52, 128, a), outline=(30, 20, 30, a), width=int(3 * s))
        d.polygon([(bx + 24 * s, by - 8 * s), (bx + 48 * s, by - 20 * s), (bx + 40 * s, by + 2 * s)], fill=(80, 140, 70, a))
    if T_TOM + .1 <= t < T_CAT and fade > 0:
        bubble()
        d.ellipse((bx - 40 * s, by - 26 * s, bx + 10 * s, by + 24 * s), fill=(214, 60, 44, a), outline=(40, 20, 16, a), width=int(3 * s))
        d.polygon([(bx - 15 * s, by - 30 * s), (bx - 5 * s, by - 22 * s), (bx - 22 * s, by - 20 * s)], fill=(80, 140, 70, a))
        d.text((bx + 20 * s, by - 24 * s), '?', font=q, fill=(40, 34, 30, a))
    if T_CAT + .1 <= t and fade > 0:
        bubble()
        for k, (ox, alive) in enumerate(((-28, True), (26, False))):     # Schrödinger: the live cat, and a cat's skull
            cx, cy = bx + ox * s, by + 4 * s
            ol, ink = (40, 30, 20, a), (30, 24, 20, a)
            fur = (214, 150, 80, a) if alive else (238, 232, 216, a)
            d.polygon([(cx - 18 * s, cy - 8 * s), (cx - 14 * s, cy - 26 * s), (cx - 4 * s, cy - 14 * s)], fill=fur, outline=ol)
            d.polygon([(cx + 18 * s, cy - 8 * s), (cx + 14 * s, cy - 26 * s), (cx + 4 * s, cy - 14 * s)], fill=fur, outline=ol)
            if alive:
                d.ellipse((cx - 20 * s, cy - 16 * s, cx + 20 * s, cy + 18 * s), fill=fur, outline=ol, width=int(2 * s))
                d.ellipse((cx - 9 * s, cy - 3 * s, cx - 4 * s, cy + 2 * s), fill=ink); d.ellipse((cx + 4 * s, cy - 3 * s, cx + 9 * s, cy + 2 * s), fill=ink)
            else:
                d.rounded_rectangle((cx - 11 * s, cy + 4 * s, cx + 11 * s, cy + 20 * s), radius=5 * s, fill=fur, outline=ol, width=int(2 * s))   # jaw
                d.ellipse((cx - 19 * s, cy - 17 * s, cx + 19 * s, cy + 13 * s), fill=fur, outline=ol, width=int(2 * s))                       # cranium
                d.rectangle((cx - 9 * s, cy + 6 * s, cx + 9 * s, cy + 12 * s), fill=fur)                                                       # (one bone)
                d.ellipse((cx - 12 * s, cy - 7 * s, cx - 3 * s, cy + 3 * s), fill=ink); d.ellipse((cx + 3 * s, cy - 7 * s, cx + 12 * s, cy + 3 * s), fill=ink)
                d.polygon([(cx - 2.5 * s, cy + 5 * s), (cx + 2.5 * s, cy + 5 * s), (cx, cy + 9 * s)], fill=ink)
                d.line((cx - 8 * s, cy + 14 * s, cx + 8 * s, cy + 14 * s), fill=ink, width=max(1, int(1.5 * s)))
                for tx in (-5, 0, 5):
                    d.line((cx + tx * s, cy + 11 * s, cx + tx * s, cy + 18 * s), fill=ink, width=max(1, int(1.5 * s)))
        d.text((bx - 8 * s, by - 60 * s), '?', font=q, fill=(40, 34, 30, a))
    if t >= T_ENJ and fade > 0:
        mf = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', int(40 * s))
        k = outc((t - T_ENJ) / .15)
        d.text((X0 + (X1 - X0) * .42, Y0 + (Y1 - Y0) * (.45 - .05 * k)), 'meow', font=mf, fill=(250, 246, 236, int(a * k)))
    return {'u_ui': img}
