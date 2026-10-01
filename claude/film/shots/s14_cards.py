"""s14 · 2:42.632–  the mirrored chorus: one different card.
Flat 2D, grey paper, black shapes, red only for the hole.

If I can            the blood of the last shot is the light behind a card: its holes glow red; lit, a census card,
                    VOLKSZÄHLUNG 1939, columns down to Abstammung.
give them all the   the card goes onto a belt; pulling back: three belts of cards feeding a black factory with smoking
                    chimneys.  EXECUTION: every card, the same hole (Abstammung), red; the chimneys burst.
Then I can          everything is rushed in. One card comes back out — with the smoke, from the chimney: the only one
                    without the red hole, its edge scorched. It flutters down; the factory is gone.
be your only        a pictogram man (Turing) bends and picks it up, turns it over and writes, in fountain pen:
                    "I feel sure that I shall / meet Morcom again somewhere"  (to his mother, 16 February 1930)
EXECUTION           the pen stops; three dots.
If I can have you back   round the lines he scribbles the halting problem: H(p,x) -> halts?  D(p) ...  D(D) ?  contradiction.
I will run the      he walks to a box: the Chinese Room (J. R. Searle, 1980) — a slot, a window.
EXECUTION           the card goes in through the slot.
Though we are trapped   inside: the man at the desk takes the card, leafs through the rule book to LOVE —
We are trapped ah   LOVE -> 爱 / 恨 / (无意义). He stops."""
import math
from PIL import Image, ImageDraw, ImageFont

T0, T1, T2 = 162.632, 163.315, 165.166
T3, T3B, T4 = 166.016, 167.022, 168.911
T5, T6, T7 = 169.824, 171.868, 172.712
T8, T9, TE = 173.643, 174.975, 177.246

CW, CH = .3, .132                       # a card (7 3/8 x 3 1/4 in)
COLW, ROWH = .93 / 80, .70 / 12
MARK = (64, 3)                          # Abstammung, row "1"
HOLEC = ((.035 + (MARK[0] + .5) * COLW - .5) * CW, (.80 - (MARK[1] + .5) * ROWH - .5) * CH)
GROUPS = ['Geburtsjahr', 'Geschlecht', 'Familienstand', 'Beruf', 'Religion', 'Muttersprache', 'Abstammung', 'Gemeinde']
FONT = 'C:/Windows/Fonts/cour.ttf'
FONTB = 'C:/Windows/Fonts/courbd.ttf'
FSCRIPT = 'C:/Windows/Fonts/segoesc.ttf'
FSCRIB = 'C:/Windows/Fonts/Inkfree.ttf'
FCJK = 'C:/Windows/Fonts/msyh.ttc'

# ---- the outdoor space after the factory, the room, the room's inside
YG = -1.0                                # ground
FIG0 = (.72, YG)                          # where Turing stands
LAND = (1.36, YG + CH / 2 + .004)         # where the card lands
RX0, RX1 = 3.3, 5.3                       # the Chinese Room, outside
SLOT = (RX0, YG + 1.95)
IN = 30.                                  # the inside of the room lives at x ~ 30
BOOK = (30.62, .64); BOOKH = (.7, .42)


def _face():
    W, H = 3072, 1350
    img = Image.new('L', (W, H), 0); d = ImageDraw.Draw(img)
    px = lambda u: u * W
    py = lambda v: (1 - v) * H
    fd = ImageFont.truetype(FONTB, 30)
    for i in range(2, 12):
        for j in range(80):
            x, y = px(.035 + (j + .5) * COLW), py(.80 - (i + .5) * ROWH)
            d.text((x, y), str(i - 2), font=fd, fill=150, anchor='mm')
    fs = ImageFont.truetype(FONTB, 33)
    for g, name in enumerate(GROUPS):
        x0, x1 = px(.035 + g * 10 * COLW), px(.035 + (g + 1) * 10 * COLW)
        d.text(((x0 + x1) / 2, py(.855)), name, font=fs, fill=255, anchor='mm')
        if g: d.line([(x0, py(.80)), (x0, py(.905))], fill=230, width=4)
    d.line([(px(.035), py(.81)), (px(.965), py(.81))], fill=230, width=4)
    d.line([(px(.035), py(.905)), (px(.965), py(.905))], fill=230, width=4)
    fh = ImageFont.truetype(FONTB, 74)
    d.text((px(.075), py(.953)), 'VOLKSZÄHLUNG 1939', font=fh, fill=255, anchor='lm')
    fr = ImageFont.truetype(FONTB, 48)
    d.text((px(.965), py(.953)), '17. MAI 1939', font=fr, fill=255, anchor='rm')
    fn = ImageFont.truetype(FONTB, 20)
    for j in range(80):
        d.text((px(.035 + (j + .5) * COLW), py(.075)), str(j + 1), font=fn, fill=190, anchor='mm')
    return Image.merge('RGBA', (img, img, img, img))


FACE = _face()

# ---- the back of the card: the letter (A), the three dots (G), the scribbled notes (B, revealed item by item)
LETTER = ['I feel sure that I shall', 'meet Morcom again somewhere']
LINE_Y = [.36, .58]                       # baselines, from the top (image fraction)
SCRIB = [('H(p, x) -> halts ?', (.05, .15), -3, 62),
         ('D(p): if H(p,p) loop', (.05, .79), 2, 60),
         ('else halt', (.3, .92), 2, 60),
         ('D(D) ?', (.7, .85), -6, 74),
         ('contradiction !', (.58, .15), 4, 60),
         ('', None, 0, 0)]                    # the last one: an arrow and a circle, drawn below


def _letter():
    W, H = 2400, 1056
    a = Image.new('L', (W, H), 0); g = Image.new('L', (W, H), 0); b = Image.new('L', (W, H), 0)
    f = ImageFont.truetype(FSCRIPT, 104)
    da, dg = ImageDraw.Draw(a), ImageDraw.Draw(g)
    edges = []
    for i, line in enumerate(LETTER):
        x0, y = .07 * W, LINE_Y[i] * H
        da.text((x0, y), line, font=f, fill=255, anchor='ls')
        edges.append([(x0 + f.getlength(line[:k + 1])) / W for k in range(len(line))])
    xe = .07 * W + f.getlength(LETTER[1]) + 14
    dots = []
    for k in range(3):
        cx = xe + k * 34
        dg.ellipse([cx - 8, LINE_Y[1] * H - 16, cx + 8, LINE_Y[1] * H], fill=255)
        dots.append((cx + 10) / W)
    boxes = []
    for text, pos, rotd, size in SCRIB:
        lay = Image.new('L', (W, H), 0); dl = ImageDraw.Draw(lay)
        if text:
            fs = ImageFont.truetype(FSCRIB, size)
            tmp = Image.new('L', (int(fs.getlength(text)) + 40, size + 40), 0)
            ImageDraw.Draw(tmp).text((20, 20), text, font=fs, fill=255)
            tmp = tmp.rotate(rotd, expand=True, resample=Image.BICUBIC)
            lay.paste(tmp, (int(pos[0] * W), int(pos[1] * H - tmp.size[1] / 2)), tmp)
            if text.startswith('H('):                              # struck through, once
                y = pos[1] * H + 4
                dl.line([(pos[0] * W + 330, y + 6), (pos[0] * W + 560, y - 10)], fill=255, width=6)
        else:                                                      # circle round D(D), arrow up to 'contradiction'
            dl.ellipse([.68 * W, .77 * H, .9 * W, .95 * H], outline=255, width=6)
            dl.line([(.8 * W, .77 * H), (.76 * W, .24 * H)], fill=255, width=6)
            dl.line([(.76 * W, .24 * H), (.74 * W, .3 * H)], fill=255, width=6)
            dl.line([(.76 * W, .24 * H), (.785 * W, .295 * H)], fill=255, width=6)
        bb = lay.getbbox()
        boxes.append((bb[0] / W, 1 - bb[3] / H, bb[2] / W, 1 - bb[1] / H))
        b.paste(255, (0, 0), lay)
    return Image.merge('RGBA', (a, g, b, a)), edges, dots, boxes


LETTER_IMG, LETTER_EDGES, DOTS_X, SCRIB_BOX = _letter()
NCH = sum(len(l) for l in LETTER)
TW0, TW1 = 167.5, 168.82


def letter_reveal(t):
    n = int(NCH * clamp((t - TW0) / (TW1 - TW0))) if t >= TW0 else 0
    rv, tip = [0., 0.], None
    for i, line in enumerate(LETTER):
        k = min(n, len(line))
        if k > 0:
            rv[i] = LETTER_EDGES[i][k - 1]
            tip = (rv[i], 1 - LINE_Y[i])
        n -= len(line)
        if n <= 0: break
    return rv, tip


# ---- the rule book: base (A), the three arrows and answers (G, item by item)
def _manual():
    W, H = 2400, 1440
    a = Image.new('L', (W, H), 0); g = Image.new('L', (W, H), 0)
    da = ImageDraw.Draw(a)
    fe, fc = ImageFont.truetype(FONTB, 50), ImageFont.truetype(FCJK, 50)
    entries = [('LOAD', '装载'), ('LOCK', '锁'), ('LOGIC', '逻辑'), ('LONG', '长'), ('LOOK', '看'),
               ('LOOP', '循环'), ('LOSE', '失去'), ('LOST', '迷失'), ('LOUD', '响'), ('LOVE', '→')]
    for i, (e, c) in enumerate(entries):
        y = 150 + i * 118
        da.text((120, y), e, font=fe, fill=255, anchor='lm')
        da.text((470, y), c, font=fc, fill=255, anchor='lm')
        da.line([(120, y + 44), (1050, y + 44)], fill=90, width=2)
    da.text((1080, 1360), '118', font=ImageFont.truetype(FONT, 34), fill=200, anchor='rm')
    fl = ImageFont.truetype(FONTB, 200)
    da.text((1330, 300), 'LOVE', font=fl, fill=255, anchor='lm')
    da.text((2280, 1360), '119', font=ImageFont.truetype(FONT, 34), fill=200, anchor='rm')
    ft = ImageFont.truetype(FCJK, 150)
    fts = ImageFont.truetype(FCJK, 96)
    targets = [('爱', (1900, 640), ft), ('恨', (1900, 930), ft), ('（无意义）', (1720, 1210), fts)]
    boxes = []
    for i, (txt, (x, y), fnt) in enumerate(targets):
        lay = Image.new('L', (W, H), 0); dl = ImageDraw.Draw(lay)
        sx, sy = 1560, 430
        ex, ey = x - 40 if i < 2 else x - 20, y - 10 if i < 2 else y - 70
        dl.line([(sx, sy), (ex, ey)], fill=255, width=12)
        ang = math.atan2(ey - sy, ex - sx)
        for s_ in (-1, 1):
            dl.line([(ex, ey), (ex - 60 * math.cos(ang + s_ * .45), ey - 60 * math.sin(ang + s_ * .45))], fill=255, width=12)
        dl.text((x + 60 if i < 2 else x + 260, y), txt, font=fnt, fill=255, anchor='mm')
        bb = lay.getbbox()
        boxes.append((bb[0] / W, 1 - bb[3] / H, bb[2] / W, 1 - bb[1] / H))
        g.paste(255, (0, 0), lay)
    return Image.merge('RGBA', (a, g, a, a)), boxes


MANUAL_IMG, ARROW_BOX = _manual()


def _v(p): return 'vec2(%.7f,%.7f)' % tuple(p)
def _v4(b): return 'vec4(%.5f,%.5f,%.5f,%.5f)' % tuple(b)


SRC = r'''#version 330
uniform vec2 u_res; uniform float u_time, u_weight;
uniform sampler2D u_face, u_ui, u_letter, u_manual;
uniform float u_zoom; uniform vec2 u_ctr, u_shake;
uniform float u_lit, u_backRed, u_mark, u_flash;
uniform float u_fact, u_factA, u_shift, u_burst, u_skip0, u_mode;
uniform vec2 u_cardPos; uniform float u_cardRot, u_fx, u_cardOn, u_clipX, u_singe;
uniform float u_wl[2], u_dotX, u_scrib;
uniform vec3 u_pen;
uniform vec2 u_F, u_hand; uniform float u_lean, u_squat, u_swing, u_figOn;
uniform vec2 u_F2, u_hand2;
uniform float u_room, u_flipP, u_spread, u_arrows;
out vec4 fragColor;
#define PI 3.14159265
float h12(vec2 p){ vec3 p3=fract(vec3(p.xyx)*.1031); p3+=dot(p3,p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }
float vn(vec2 p){ vec2 i=floor(p),f=fract(p); f=f*f*(3.-2.*f);
  return mix(mix(h12(i),h12(i+vec2(1,0)),f.x),mix(h12(i+vec2(0,1)),h12(i+vec2(1,1)),f.x),f.y); }
float fbm(vec2 p){ float s=0.,a=.5; for(int i=0;i<4;i++){ s+=a*vn(p); p=p*2.03+1.7; a*=.5; } return s; }
const float CW=%CW%, CH=%CH%, COLW=%COLW%, ROWH=%ROWH%;
const vec2 HOLEC=%HC%;
const vec3 PAPER=vec3(.62,.56,.47), INK=vec3(.035,.03,.035), BLOOD=vec3(.9,.02,.03), PEN=vec3(.02,.03,.07);
const vec4 SBOX[6]=vec4[6](%SBOX%);
const vec4 ABOX[3]=vec4[3](%ABOX%);
const float YG=%YG%, RX0=%RX0%, RX1=%RX1%;
const vec2 SLOT=%SLOT%, BOOK=%BOOK%, BOOKH=%BOOKH%;
float PXw;
mat2 rot(float a){ float c=cos(a), s=sin(a); return mat2(c,s,-s,c); }
float sdRBox(vec2 p, vec2 b, float r){ vec2 q=abs(p)-b+r; return length(max(q,0.))+min(max(q.x,q.y),0.)-r; }
float sdBox(vec2 p, vec2 c, vec2 b){ vec2 d=abs(p-c)-b; return length(max(d,0.))+min(max(d.x,d.y),0.); }
float sdCap(vec2 p, vec2 a, vec2 b, float r){ vec2 pa=p-a, ba=b-a; float h=clamp(dot(pa,ba)/max(dot(ba,ba),1e-9),0.,1.); return length(pa-ba*h)-r; }
float fill(float d){ return 1.-smoothstep(-PXw,PXw,d); }
bool inBox(vec2 uv, vec4 b){ return uv.x>=b.x&&uv.x<=b.z&&uv.y>=b.y&&uv.y<=b.w; }

// one card. uv: 0..1 across, 0..1 up. centre: the card we follow (its back can be shown)
vec4 card(vec2 uv, vec2 id, float centre, float back){
  if(uv.x<0.||uv.x>1.||uv.y<0.||uv.y>1.) return vec4(0.);
  if((back>.5?(1.-uv.x):uv.x)*CW/CH+(1.-uv.y)<.11) return vec4(0.);   // the corner cut
  float edge=min(min(uv.x,1.-uv.x)*CW,min(uv.y,1.-uv.y)*CH);
  float burnt=0.;
  if(centre>.5&&u_singe>0.){                                           // scorched round the edge, bits burnt away
    float n=vn(uv*vec2(60.,26.))*.7+vn(uv*vec2(170.,75.))*.3;
    if(edge<.0035*n) return vec4(0.);
    burnt=1.-smoothstep(.0,.004+.012*n,edge);
  }
  float pxu=PXw/CH;
  vec3 backL=mix(vec3(1.,.82,.62),BLOOD,u_backRed)*2.2*(1.-u_lit);
  vec3 paper=PAPER*(.985+.03*vn(uv*vec2(300.,130.)));
  vec3 c;
  vec2 hu=uv;
  if(back>.5){
    vec4 L=texture(u_letter,uv);
    float yl=1.-uv.y;
    float rv=yl<.47?u_wl[0]:u_wl[1];
    float w=L.a*step(uv.x,rv);
    w=max(w,L.g*step(uv.x,u_dotX));
    float sc=0.;
    for(int i=0;i<6;i++){ if(float(i)<u_scrib&&inBox(uv,SBOX[i]+vec4(-.01,-.01,.01,.01))) sc=1.; }
    w=max(w,L.b*sc*.9);
    c=mix(paper,PEN,w*.95);
    hu.x=1.-uv.x;                                                      // the holes, seen from behind
  } else {
    float ink=texture(u_face,uv).a;
    c=mix(paper,INK,ink*.9)*mix(.03,1.,u_lit);
  }
  c*=mix(.25,1.,smoothstep(PXw*.6,PXw*1.8,edge));
  c=mix(c,vec3(.06,.035,.02),burnt*.9);
  c=mix(c,c*vec3(.8,.66,.5),(1.-smoothstep(.0,.03,edge))*u_singe*centre);
  float cx=(hu.x-.035)/COLW, ry=(.80-hu.y)/ROWH;
  float col=floor(cx), row=floor(ry);
  if(col>=0.&&col<80.&&row>=0.&&row<12.){
    vec2 f=vec2(fract(cx)-.5,fract(ry)-.5)*vec2(COLW*CW/CH,ROWH);
    float d=sdRBox(f,vec2(.2*COLW*CW/CH,.3*ROWH),.07*COLW*CW/CH);
    float hole=1.-smoothstep(-pxu,pxu,d);
    float punched=step(h12(id*1.37+vec2(col*.71,3.)),.2)*step(abs(row-floor(h12(id+vec2(col*1.3,.5))*12.)),.1);
    float mark=step(abs(col-%MC%.),.1)*step(abs(row-%MR%.),.1)*u_mark*(1.-u_singe*centre);
    if(mark>0.) return vec4(mix(c,BLOOD*(1.6+2.*u_flash),hole),1.);
    if(punched>0.) return vec4(mix(c,backL,hole),1.-hole*(1.-step(.001,length(backL))));
  }
  return vec4(c,1.);
}

// ---- the factory: flat black shapes on grey paper
const float XD=2.7, PITCH=.36;
float factory(vec2 p){
  float d=sdBox(p,vec2(3.9,.52),vec2(1.2,.93));
  float tx=p.x-XD, k=floor(tx/.44), f=tx-k*.44;
  if(p.x>XD&&p.x<5.1&&p.y>1.4&&p.y<1.45+.26*(1.-f/.44)) d=min(d,-1.);
  d=min(d,sdBox(p,vec2(3.45,1.72),vec2(.09,.3)));
  d=min(d,sdBox(p,vec2(4.22,1.78),vec2(.11,.36)));
  d=min(d,sdBox(p,vec2(3.45,2.0),vec2(.12,.025)));
  d=min(d,sdBox(p,vec2(4.22,2.12),vec2(.14,.025)));
  return d;
}
float smoke(vec2 p){
  float m=0.;
  for(int c=0;c<2;c++){
    vec2 top=c==0?vec2(3.45,2.03):vec2(4.22,2.15);
    float P=.26, ph=u_time/P+float(c)*.37;
    for(int k=0;k<18;k++){
      float id=floor(ph)-float(k), age=(float(k)+fract(ph))*P;
      vec2 cp=top+vec2(.42*age+.06*sin(id*1.7),.36*age+.05*sin(id*2.3));
      float r=.05+.09*age+.03*h12(vec2(id,float(c)));
      float d=length(p-cp)-r*(1.+.08*(vn(p*9.+id)-.5));
      m=max(m,(1.-smoothstep(-PXw,PXw,d))*(1.-smoothstep(3.2,4.5,age)));
    }
    if(u_burst>0.){ float a=u_burst; vec2 cp=top+vec2(.3*a,.9*a); float d=length(p-cp)-(.12+.5*a)*(1.+.1*(vn(p*6.)-.5));
      m=max(m,(1.-smoothstep(-PXw,PXw,d))*(1.-smoothstep(.6,1.,a))); }
  }
  return m;
}
vec3 factoryScene(vec2 p){
  vec3 bg=vec3(.3,.28,.25)*(.97+.05*fbm(p*2.))*u_lit;
  vec3 c=bg;
  c=mix(c,INK,smoke(p));
  c=mix(c,INK,1.-smoothstep(-PXw,PXw,p.y+.4));
  for(int b=0;b<3;b++){
    float yb=-CH*.5-.004+float(b)*.55;
    if(p.x<XD+.02){
      float legx=mod(p.x+.2,.9)-.45;
      if(abs(legx)<.008&&p.y<yb&&p.y>yb-.55+.02) c=INK;
      if(p.y<yb&&p.y>yb-.03){
        c=INK;
        vec2 rp=vec2(mod(p.x,.1)-.05,p.y-(yb-.015));
        c=mix(c,bg*.55,1.-smoothstep(.009-PXw,.009+PXw,length(rp)));
      }
    }
    float off=u_shift+float(b)*.13;
    float n0=floor((p.x-off)/PITCH+.5);
    for(int dn=-1;dn<=1;dn++){
      float n=n0+float(dn);
      if(b==0&&abs(n)<.1&&u_skip0>.5) continue;                       // ours is drawn on its own
      vec2 cc=vec2(n*PITCH+off,yb+CH*.5+.004);
      if(cc.x>XD+.2) continue;
      vec2 l=p-cc;
      vec4 cd=card(l/vec2(CW,CH)+.5,vec2(float(b)*1000.+n,3.),0.,0.);
      c=mix(c,cd.rgb,cd.a);
      c=mix(c,BLOOD*1.4,u_mark*(1.-smoothstep(PXw*1.2,PXw*2.6,length(l-HOLEC))));
      c+=BLOOD*u_mark*(1.+3.*u_flash)*exp(-length(l-HOLEC)/(PXw*5.))*step(abs(l.x),CW*.5)*step(abs(l.y),CH*.5);
    }
  }
  c=mix(c,INK,1.-smoothstep(-PXw,PXw,factory(p)));
  return c;
}

// ---- pictogram people (Isotype-like): lean = the upper body bent forward about the hip; squat lowers the hip
float person(vec2 p, vec2 F, float swing, float lean, float squat, vec2 handW){
  vec2 q=p-F;
  float hy=1.45-.6*squat;
  vec2 hip=vec2(0.,hy);
  float d=1e3;
  for(int s=0;s<2;s++){
    float sg=s==0?-1.:1.;
    vec2 foot=vec2(sg*.12+sg*swing,.06), knee=vec2(sg*.1+.32*squat+sg*swing*.5,.78-.12*squat);
    vec2 hp=vec2(sg*.1,hy+.05);
    if(squat<.01) d=min(d,sdCap(q,hp,foot,.075));
    else { d=min(d,sdCap(q,hp,knee,.075)); d=min(d,sdCap(q,knee,foot,.075)); }
  }
  vec2 u=hip+rot(lean)*(q-hip)+vec2(0.,.6*squat);                     // body frame (upright, hip at 1.45)
  d=min(d,length(u-vec2(0.,2.55))-.17);
  d=min(d,sdRBox(u-vec2(0.,1.86),vec2(.2,.38),.08));
  d=min(d,sdCap(u,vec2(-.2,2.14),vec2(-.25-swing*.6,1.46),.06));
  vec2 sh=hip+rot(-lean)*(vec2(.2,2.14-.0)-vec2(0.,1.45));             // right shoulder, in q
  d=min(d,sdCap(q,sh,handW-F,.06));
  return d;
}
vec3 pen(vec2 p, vec3 col){
  if(u_pen.z<=0.) return col;
  vec2 t=u_pen.xy, dir=normalize(vec2(.55,1.));
  vec2 q=p-t; vec2 l=vec2(dot(q,vec2(dir.y,-dir.x)),dot(q,dir));
  float nib=max(abs(l.x)-l.y*.3,max(-l.y,l.y-.024));
  float body=sdRBox(l-vec2(0.,.125),vec2(.0085,.1),.0075);
  float clip=sdRBox(l-vec2(.01,.17),vec2(.002,.04),.0015);
  col=mix(col,vec3(.55,.42,.18),fill(nib)*u_pen.z);
  col=mix(col,INK,fill(body)*u_pen.z);
  col=mix(col,vec3(.5,.46,.4),fill(clip)*u_pen.z*.6);
  return col;
}
// ---- the Chinese Room from outside: a plain box, a slot in the left wall, a window
vec3 roomOut(vec2 p, vec3 c){
  vec2 ctr=vec2((RX0+RX1)*.5,YG+1.25), hs=vec2((RX1-RX0)*.5,1.25);
  float d=sdBox(p,ctr,hs);
  c=mix(c,vec3(.4,.37,.32)*(.97+.05*fbm(p*3.)),fill(d));
  c=mix(c,INK,fill(abs(d)-.022));
  c=mix(c,INK,fill(sdBox(p,vec2(ctr.x,YG+2.56),vec2(hs.x+.12,.05))));      // the roof slab
  vec2 wc=vec2(RX0+1.1,YG+1.62);
  float wd=sdBox(p,wc,vec2(.3,.3));
  c=mix(c,vec3(.05,.045,.04),fill(wd));
  c=mix(c,INK,fill(abs(wd)-.018));
  c=mix(c,vec3(.4,.37,.32),fill(min(abs(p.x-wc.x),abs(p.y-wc.y))-.012)*fill(wd));
  c=mix(c,vec3(.01),fill(sdBox(p,SLOT,vec2(.03,.022))));                      // the slot
  return c;
}
// ---- inside
vec3 bookPage(vec2 uv, float right){                                  // a page being leafed: lines of small type
  vec3 c=PAPER*1.06;
  float row=floor(uv.y*26.), fx=fract(uv.y*26.);
  float len=.35+.5*h12(vec2(row,right+floor(u_flipP)));
  float x0=right>.5?.56:.06;
  if(fx>.35&&fx<.62&&uv.x>x0&&uv.x<x0+len*.38&&row>1.&&row<24.) c*=.55;
  return c;
}
vec3 roomIn(vec2 p){
  vec3 c=vec3(.5,.46,.4)*(.97+.05*fbm(p*2.));
  c=mix(c,INK,fill(p.y-YG));                                          // floor
  c=mix(c,INK,fill(abs(p.x-28.35)-.03));                               // the left wall
  c=mix(c,vec3(.01),fill(sdBox(p,vec2(28.4,.95),vec2(.05,.022))));      // the slot
  vec2 wc=vec2(31.75,1.15);                                             // the window, light outside
  float wd=sdBox(p,wc,vec2(.3,.3));
  c=mix(c,vec3(.78,.74,.66),fill(wd));
  c=mix(c,INK,fill(abs(wd)-.02));
  c=mix(c,INK,fill(min(abs(p.x-wc.x),abs(p.y-wc.y))-.014)*fill(wd));
  // the desk
  c=mix(c,INK,fill(sdBox(p,vec2(30.3,.19),vec2(1.35,.035))));
  c=mix(c,INK,fill(sdBox(p,vec2(29.05,-.41),vec2(.025,.6))));
  c=mix(c,INK,fill(sdBox(p,vec2(31.55,-.41),vec2(.025,.6))));
  // the man
  c=mix(c,INK,fill(person(p,u_F2,0.,.12,0.,u_hand2)));
  // the book, standing open on the desk
  vec2 buv=(p-BOOK)/(2.*BOOKH)+.5;
  float bd=sdBox(p,BOOK,BOOKH);
  if(bd<PXw*2.){
    vec3 pc=PAPER*1.06;
    if(u_spread>.5){
      vec4 M=texture(u_manual,buv);
      float ar=0.;
      for(int i=0;i<3;i++){ if(float(i)<u_arrows&&inBox(buv,ABOX[i]+vec4(-.01,-.01,.01,.01))) ar=1.; }
      pc=mix(pc,INK,M.a*.92);
      pc=mix(pc,BLOOD*.8,M.g*ar);
    } else pc=bookPage(buv,step(.5,buv.x));
    pc*=1.-.35*exp(-abs(buv.x-.5)*40.);                               // the gutter
    c=mix(c,pc,fill(bd));
    c=mix(c,INK,fill(abs(bd)-.012));
    // a leaf turning over the spine
    float fp=fract(u_flipP);
    if(u_flipP>0.&&u_flipP<3.){
      float w=BOOKH.x*abs(cos(fp*PI));
      float side=fp<.5?1.:-1.;
      float lx=(p.x-BOOK.x)*side;
      float ld=max(sdBox(vec2(lx,p.y),vec2(w*.5,BOOK.y),vec2(w*.5,BOOKH.y*(1.+.06*sin(fp*PI)))),-1.);
      vec3 lc=bookPage(vec2(.5+.5*lx/max(w,1e-3)*side,buv.y),fp<.5?1.:0.)*(.85+.15*abs(cos(fp*PI)));
      c=mix(c,lc,fill(ld));
      c=mix(c,INK,fill(abs(ld)-.008));
    }
  }
  return c;
}

void main(){
  vec2 uv=(gl_FragCoord.xy-.5*u_res)/u_res.y;
  PXw=1./(u_res.y*u_zoom);
  vec2 p=u_ctr+(uv+u_shake)/u_zoom;
  vec3 col=vec3(.004);
  if(u_mode>1.5){
    col=roomIn(p);
  } else {
    if(u_mode>.5){
      col=vec3(.5,.46,.4)*(.97+.05*fbm(p*2.));
      col=mix(col,INK,fill(p.y-YG));
      if(u_room>0.) col=roomOut(p,col);
    }
    if(u_fact>0.&&u_factA>0.) col=mix(col,factoryScene(p),u_factA);
    if(u_figOn>0.) col=mix(col,INK,fill(person(p,u_F,u_swing,u_lean,u_squat,u_hand))*u_figOn);
  }
  // the card we follow
  if(u_cardOn>0.){
    vec2 pc=rot(-u_cardRot)*(p-u_cardPos);
    pc.x/=max(abs(u_fx),.002);
    vec4 cd=card(pc/vec2(CW,CH)+.5,vec2(0.,0.),1.,step(u_fx,0.));
    cd.a*=step(p.x,u_clipX)*u_cardOn;
    col=mix(col,cd.rgb,cd.a);
    if(u_singe<.5) col+=BLOOD*u_mark*(1.+2.*u_flash)*exp(-length(pc-HOLEC)/(PXw*2.2))*step(abs(pc.x),CW*.5)*step(abs(pc.y),CH*.5);
  }
  if(u_mode>.5&&u_mode<1.5&&u_room>0.){                               // the slot swallows the card
    col=mix(col,vec3(.4,.37,.32)*(.97+.05*fbm(p*3.)),fill(sdBox(p,vec2((RX0+RX1)*.5,YG+1.25),vec2((RX1-RX0)*.5-.022,1.228)))*step(RX0+.03,p.x)*step(abs(p.y-SLOT.y),.2)*step(p.x,RX0+.5)*step(u_clipX,50.));
  }
  col=pen(p,col);
  col+=vec3(1.,.9,.85)*u_flash*.08;
  vec4 ui=texture(u_ui,gl_FragCoord.xy/u_res);
  col=mix(col,ui.rgb,ui.a);
  fragColor=vec4(col*u_weight,1.);
}
'''
for k, v in {'%CW%': '%.4f' % CW, '%CH%': '%.4f' % CH, '%COLW%': '%.7f' % COLW, '%ROWH%': '%.7f' % ROWH,
             '%HC%': _v(HOLEC), '%MC%': str(MARK[0]), '%MR%': str(MARK[1]),
             '%SBOX%': ','.join(_v4(b) for b in SCRIB_BOX), '%ABOX%': ','.join(_v4(b) for b in ARROW_BOX),
             '%YG%': '(%.4f)' % YG, '%RX0%': '%.4f' % RX0, '%RX1%': '%.4f' % RX1, '%SLOT%': _v(SLOT),
             '%BOOK%': _v(BOOK), '%BOOKH%': _v(BOOKH)}.items():
    SRC = SRC.replace(k, v)
POST = dict(u_bloom=.3, u_ca=.004)


def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def outc(x): x = clamp(x); return 1 - (1 - x) ** 3
def lerp(a, b, k): return a + (b - a) * k
def lerp2(a, b, k): return (lerp(a[0], b[0], k), lerp(a[1], b[1], k))
def lz(a, b, k): return math.exp(lerp(math.log(a), math.log(b), k))
def add(a, b): return (a[0] + b[0], a[1] + b[1])


def shift(t):
    """how far the belts have run (they start on 'give them all the'); after 'Then I can' everything is rushed in"""
    a = t - T1
    if a <= 0: return 0.
    s = .75 * (a * a / .8 if a < .4 else .2 + (a - .4))
    return s + (2.2 * (t - T3) ** 2 if t > T3 else 0.)


# ---- the different card: out of the smoke, down to the ground, into his hand, into the slot
TL = 166.78                 # it lands
TG, TUP = 167.0, 167.32     # he has it; he is standing again
TWALK, TSTOP = T6 + .02, T6 + .62
F_STOP = (RX0 - .75, YG)


def fig_pose(t):
    """feet, lean, squat, swing, right hand (world)"""
    F = FIG0
    if t >= TWALK:
        k = clamp((t - TWALK) / (TSTOP - TWALK))
        F = (lerp(FIG0[0], F_STOP[0], ease(k)), YG)
    sw = .17 * math.sin((t - TWALK) * 17.) * (1 - abs(2 * clamp((t - TWALK) / (TSTOP - TWALK)) - 1) ** 3) if TWALK < t < TSTOP else 0.
    bend = ease((t - 166.8) / .2) * (1 - ease((t - TG - .02) / (TUP - TG)))
    lean, squat = .9 * bend, bend
    chest = add(F, (.62, 1.95))
    grab = (LAND[0] - .12, LAND[1] + .04)
    rest = add(F, (.24, 1.46))
    if t < TG:
        hand = lerp2(rest, grab, bend)
    elif t < TUP + .05:
        hand = lerp2(grab, chest, ease((t - TG) / (TUP - TG)))
    else:
        hand = chest
    if t >= T7 - .25:                                   # into the slot
        k = ease((t - T7 + .25) / .22) * (1 - ease((t - T7 - .15) / .3))
        hand = lerp2(hand, (SLOT[0] - .02, SLOT[1]), k)
    return F, lean, squat, sw, hand


def card_pose(t):
    """position, in-plane rotation, flip (cos: <0 shows the back), visible"""
    if t < T3: return (shift(t), 0.), 0., 1., 1.
    if t < TL:
        k = clamp((t - T3 - .05) / (TL - T3 - .05))
        e = ease(k)
        a, b, c = (4.3, 2.35), (3.0, 2.6), LAND
        x = (1 - e) ** 2 * a[0] + 2 * (1 - e) * e * b[0] + e * e * c[0] + .14 * math.sin(k * 10.) * (1 - k)
        y = (1 - e) ** 2 * a[1] + 2 * (1 - e) * e * b[1] + e * e * c[1]
        return (x, y), .55 * math.sin(k * 8.) * (1 - k * .8) - .05 * k, math.cos(k * 4 * math.pi), clamp((t - T3 - .05) / .12)
    if t < TG: return LAND, -.05, 1., 1.
    F, lean, squat, sw, hand = fig_pose(t)
    pos = add(hand, (.12, 0.))
    fx = math.cos(math.pi * ease((t - TUP + .05) / .2))
    if t >= T7 - .05:                                     # let go: it slides in
        pos = add(pos, (.5 * ease((t - T7 + .05) / .25), 0.))
    return pos, -.05 * (1 - ease((t - TG) / .2)), fx, 1.


def camera(t):
    if t < T1: return lz(14., 5.4, outc((t - T0) / .6)), (0., 0.)
    if t < T3:
        k = ease((t - T1) / (T2 - .05 - T1))
        z = lz(5.4, .29, k) * (1 - .03 * clamp((t - T2) / (T3 - T2)))
        return z, (lerp(shift(t), 1.95, k), lerp(0., 1.08, k * k))
    z0, c0 = camera(T3 - 1e-4)
    if t < TL:                                            # following it down
        k = ease((t - T3) / (TL - T3))
        cp = card_pose(t)[0]
        kz = ease((t - T3) / (TL - T3 + .1))
        return lz(z0, .32, kz), lerp2(c0, lerp2((cp[0], cp[1] + .2), (FIG0[0] + .35, YG + 1.45), ease((t - 166.45) / .4)), ease((t - T3 - .05) / (TL - T3 - .05)))
    if t < TUP:                                           # the man who picks it up
        return .32, (FIG0[0] + .35, YG + 1.45)
    if t < T6:                                            # the card, close
        k = ease((t - TUP) / .2)
        cp = card_pose(t)[0]
        z = lz(.32, 4.6, k) * (1 + .06 * math.exp(-max(t - T4, 0) * 14) * (t >= T4))
        return z, lerp2((FIG0[0] + .35, YG + 1.45), cp, k)
    if t < T8:                                            # to the room
        k = ease((t - T6) / .3)
        cp = card_pose(T6 - 1e-3)[0]
        return lz(4.6, .36, k), lerp2(cp, ((FIG0[0] + RX1) * .5 + .35, YG + 1.4), k)
    k = ease((t - T8 - .78) / .35)
    return lz(.43, .9, k), lerp2((30.1, .45), (BOOK[0] + .05, BOOK[1] + .02), k)


def params(t):
    z, ctr = camera(t)
    sh = 0.
    for t0 in (T2, T7):
        if 0 <= t - t0 < .3: sh += math.exp(-(t - t0) * 20) * .008
    F, lean, squat, sw, hand = fig_pose(t)
    cpos, crot, fx, con = card_pose(t)
    mode = 0. if t < T3 else (1. if t < T8 else 2.)
    # writing, dots, notes, and the pen tip
    rv, tip = letter_reveal(t)
    dotX = 0.
    for k in range(3):
        if t >= T4 + k * .07: dotX = DOTS_X[k]
    nsc = clamp((t - T5 - .05) / (T6 - .25 - T5)) * 6.
    pen_on = 0.
    ptip = None
    if TW0 - .15 < t < T6 - .1:
        pen_on = clamp((t - TW0 + .15) / .12) * (1 - clamp((t - T6 + .3) / .15))
        if tip: ptip = tip
        if t >= T4: ptip = (DOTS_X[min(2, int((t - T4) / .07))], .42)
        if t >= T5:
            i = min(5, int(nsc)); b = SCRIB_BOX[i]; f = nsc - int(nsc)
            ptip = (lerp(b[0], b[2], f), lerp(b[1], b[3], .4))
        if ptip is None: ptip = (.07, .64)
    pw = (cpos[0] + (ptip[0] - .5) * CW, cpos[1] + (ptip[1] - .5) * CH) if ptip else (0., 0.)
    # inside: the card comes through the slot onto the desk; the book is leafed through; the answers
    flipP = 3. * clamp((t - T8 - .32) / .5) if t >= T8 else 0.
    spread = 1. if t >= T8 + .82 else 0.
    arrows = 3. * clamp((t - T8 + .02 - .85) / .42) + (.999 if t >= T8 + .85 else 0.) if t >= T8 + .85 else 0.
    if mode > 1.5:
        k = ease((t - T8) / .28)
        cpos = lerp2((28.45, .95), (29.55, .245), k)
        crot, fx, con = lerp(0., -.12, k), -1., 1.
    return dict(u_mode=mode, u_fact=1. if t < T3 + .7 else 0., u_factA=1. if t < T3 else 1. - ease((t - T3 - .3) / .3),
                u_shift=shift(t), u_skip0=1. if t < T3 else 0., u_burst=clamp((t - T2) / 1.1) if t >= T2 else 0.,
                u_zoom=z, u_ctr=ctr, u_shake=(sh * math.sin(t * 97), sh * math.cos(t * 83)),
                u_lit=ease((t - T0 - .3) / .35), u_backRed=1. - ease((t - T0 - .1) / .5),
                u_mark=1. if t >= T2 else 0., u_flash=sum(math.exp(-(t - t0) * 14) for t0 in (T2, T7) if t >= t0),
                u_cardPos=cpos, u_cardRot=crot, u_fx=fx, u_cardOn=con, u_singe=0. if t < T3 else 1.,
                u_clipX=SLOT[0] if T7 - .4 < t < T8 else 99.,
                u_wl=rv, u_dotX=dotX, u_scrib=nsc, u_pen=(pw[0], pw[1], pen_on),
                u_F=F, u_hand=hand, u_lean=lean, u_squat=squat, u_swing=sw,
                u_figOn=ease((t - T3 - .45) / .2) if mode == 1. else 0., u_room=1. if mode == 1. and t >= TUP else 0.,
                u_F2=(29.35, YG), u_hand2=(29.95, .55), u_flipP=flipP, u_spread=spread, u_arrows=arrows)


# ---- the typed overlay: dates and sources
_UI = {}


def typed(s, t0, t, cps=38.):
    return s[:max(0, int((t - t0) * cps))] if t >= t0 else ''


def textures(t, w, h):
    s = h / 1080
    items = []
    light, dark = (226, 222, 212), (26, 24, 22)
    if T0 + .7 <= t < T3: items.append(((70, 60), typed('17. V. 1939', T0 + .7, t), 30, light))
    elif TUP <= t < T5: items.append(((70, 60), typed('16. II. 1930', TUP, t), 30, dark))
    elif T5 <= t < T6: items.append(((70, 60), typed('1936', T5, t, 14), 30, dark))
    elif t >= T6 + .3: items.append(((70, 60), typed('1980', T6 + .3, t, 14), 30, dark))
    if TW0 <= t < T5:
        items.append(((70, 1000), typed('A. M. Turing, to his mother, 16 February 1930', TW0, t, 34), 24, dark))
    if T5 + .1 <= t < T6:
        items.append(((70, 1000), typed('the halting problem - A. M. Turing, On Computable Numbers, 1936', T5 + .1, t, 44), 24, dark))
    if T6 + .45 <= t:
        items.append(((70, 1000), typed('The Chinese Room - J. R. Searle, 1980', T6 + .45, t, 40), 24, dark))
    key = (w, h, tuple((it[1], it[0]) for it in items))
    if key not in _UI:
        _UI.clear()
        img = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
        for it in items:
            (x, y), txt, size, colr = it[:4]
            f = ImageFont.truetype(FONT, int(size * s))
            d.text((x * s, y * s), txt, font=f, fill=colr + (255,), anchor='la')
        _UI[key] = img
    return {'u_face': FACE, 'u_ui': _UI[key], 'u_letter': LETTER_IMG, 'u_manual': MANUAL_IMG}
