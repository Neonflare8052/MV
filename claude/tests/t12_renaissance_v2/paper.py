"""Independent s11 study: palimpsest -> Machiavelli / marginal argument -> terminal.

The Prince excerpt is genuine; the handwritten type restriction and function call
are the film's fictional annotations. Nothing here changes the master timeline.
"""
import math
from functools import lru_cache
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

T0, T_MADE, T_ERROR = 125.708, 128.661, 131.224
T_GRID, T_TERM, T_HANDOFF = 132.533, 133.95, 139.2
ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
W, H, SS = 1920, 1080, 2
INK = (51, 43, 34)
FAINT = (129, 111, 89)
COPPER = (121, 68, 39)
RED = (164, 29, 24)
CREAM = (230, 219, 191)

def clamp(x): return max(0., min(1., x))
def ease(x): x = clamp(x); return x*x*(3-2*x)
def mix(a, b, k): return a+(b-a)*k
def phase(t, a, b): return ease((t-a)/(b-a))

@lru_cache(None)
def font(name, size):
    return ImageFont.truetype('C:/Windows/Fonts/'+name, round(size*SS))

def canvas(): return Image.new('RGBA', (W*SS, H*SS), (0,0,0,0))
def down(im): return im.resize((W,H), Image.Resampling.LANCZOS)

class Pen:
    def __init__(self, im): self.d = ImageDraw.Draw(im)
    def text(self, xy, text, size=32, name='pala.ttf', color=INK, alpha=255, anchor=None):
        if alpha <= 0: return
        self.d.text(tuple(v*SS for v in xy), text, font=font(name,size), fill=(*color,int(alpha)), anchor=anchor)
    def line(self, points, color=INK, width=2, alpha=255):
        self.d.line([(x*SS,y*SS) for x,y in points], fill=(*color,int(alpha)), width=max(1,round(width*SS)), joint='curve')
    def rect(self, box, color=INK, width=2, alpha=255):
        self.d.rectangle([v*SS for v in box], outline=(*color,int(alpha)), width=max(1,round(width*SS)))
    def path(self, pts, progress=1., color=COPPER, width=3, alpha=255):
        progress=clamp(progress)
        if len(pts)<2 or progress<=0: return
        lengths=[math.dist(a,b) for a,b in zip(pts,pts[1:])]
        target=sum(lengths)*progress; walked=0.; out=[pts[0]]
        for a,b,d in zip(pts,pts[1:],lengths):
            if walked+d<=target: out.append(b); walked+=d
            else:
                q=(target-walked)/max(d,1e-9); out.append((mix(a[0],b[0],q),mix(a[1],b[1],q))); break
        self.line(out,color,width,alpha)
    def oval(self, cx,cy,rx,ry, progress=1.,color=COPPER,width=3,alpha=255):
        pts=[(cx+rx*math.cos(-.7+2*math.pi*k/120),cy+ry*math.sin(-.7+2*math.pi*k/120)) for k in range(121)]
        self.path(pts,progress,color,width,alpha)

def bezier(a,b,c,d,n=70):
    return [((1-v)**3*a[0]+3*(1-v)**2*v*b[0]+3*(1-v)*v*v*c[0]+v**3*d[0],
             (1-v)**3*a[1]+3*(1-v)**2*v*b[1]+3*(1-v)*v*v*c[1]+v**3*d[1]) for v in np.linspace(0,1,n)]

def ring(p,x,y,r=42,color=COPPER,alpha=255,angle=90):
    pts=[(x+r*math.cos(math.radians(angle+27+k*306/100)),y+r*math.sin(math.radians(angle+27+k*306/100))) for k in range(101)]
    p.line(pts,color,3,alpha)

@lru_cache(None)
def static_layers():
    # Sparse broad variation and fine fibres: authored paper, no downloaded image.
    rng=np.random.default_rng(1717)
    small=Image.fromarray(rng.integers(75,175,(90,160),dtype=np.uint8)).resize((W,H),Image.Resampling.BICUBIC)
    n=np.asarray(small).astype(np.float32)/255-.5
    yy,xx=np.mgrid[:H,:W]
    edge=np.minimum.reduce([xx/130.,(W-xx)/130.,yy/90.,(H-yy)/90.])
    wear=np.clip(1-edge,0,1)*12
    fibre=rng.normal(0,1.0,(H,W))
    rgb=np.empty((H,W,3),np.uint8)
    for c,v in enumerate(CREAM): rgb[:,:,c]=np.clip(v+n*9+fibre-wear,0,255)
    paper=Image.fromarray(rgb).convert('RGBA')

    note=canvas(); p=Pen(note)
    p.text((130,100),'draft, revised',24,'Inkfree.ttf',FAINT)
    p.text((130,143),'Heart, we will forget him,',36,'Inkfree.ttf',COPPER,135)
    p.text((143,194),'You and I, tonight!',33,'Inkfree.ttf',COPPER,115)
    p.text((126,253),'You may forget the warmth he gave,',25,'Inkfree.ttf',COPPER,95)
    p.line([(128,282),(630,271)],COPPER,1.5,110)
    p.text((141,304),'I will forget the light.',30,'Inkfree.ttf',COPPER,100)
    for k,(n0,lo,hi) in enumerate([(7,'3.03719','3.37102'),(14,'3.11529','3.19541'),(28,'3.13500','3.15484'),(56,'3.13994','3.14489')]):
        p.text((156,359+k*41),f'{n0:2d} : {lo} < π < {hi}',26,'palai.ttf',INK,185)
    # A small construction diagram whose geometry was originally above the poem.
    cx,cy,r=291,619,76
    p.oval(cx,cy,r,r,1,FAINT,1.5,150)
    pts=[(cx+r*math.cos(k*2*math.pi/7),cy+r*math.sin(k*2*math.pi/7)) for k in range(8)]
    p.line(pts,INK,1.5,185)
    p.line([(cx-r-25,cy),(cx+r+25,cy)],FAINT,1,125)
    p.line([(cx,cy-r-25),(cx,cy+r+25)],FAINT,1,125)
    p.text((388,582),'reason',31,'Inkfree.ttf',COPPER)
    p.text((388,628),'n → ∞',30,'cambria.ttc',INK)
    p.text((221,780),'Heart',61,'Inkfree.ttf',COPPER)
    p.text((389,798),'feeling',30,'Inkfree.ttf',COPPER)
    # The crease is a continuing wound; it is not a newly added cut.
    p.line([(90,754),(621,926)],(45,31,23),3,190)
    p.line([(90,749),(621,921)],(255,241,208),1.5,200)
    p.line([(153,465),(349,730)],INK,6,90)
    for k in range(19):
        x=348+rng.normal(0,38); y=730+rng.normal(0,21)
        rr=rng.uniform(1,4); p.d.ellipse([(x-rr)*SS,(y-rr)*SS,(x+rr)*SS,(y+rr)*SS],fill=(*INK,110))

    page=canvas(); p=Pen(page)
    p.line([(747,86),(747,976)],FAINT,1,130)
    p.text((828,83),'NICCOLÒ MACHIAVELLI',26,'pala.ttf',FAINT)
    p.text((828,126),'THE PRINCE',55,'palab.ttf',INK)
    p.text((1728,136),'XVII',42,'pala.ttf',INK,255,'ra')
    p.line([(828,204),(1740,204)],INK,2)
    p.line([(828,211),(1740,211)],FAINT,1)
    p.text((828,243),'Love, fear, and the will of others',29,'palai.ttf',FAINT)
    # Public-domain N. H. Thomson translation;
    # visible ellipses preserve that these are excerpts, not a continuous paragraph.
    lines=[('…being loved depends',315),('upon his subjects,',365),
           ('while his being feared',422),('depends upon himself…',472)]
    for txt,y in lines: p.text((828,y),txt,42,'pala.ttf',INK)
    p.text((828,547),'…a wise Prince should build',38,'pala.ttf',INK)
    p.text((828,594),'on what is his own…',38,'pala.ttf',INK)
    p.text((1740,948),'17',24,'pala.ttf',FAINT,255,'ra')

    return paper,down(note),down(page)

def annotations(t):
    im=canvas(); p=Pen(im)
    # The inherited doctrine is explicitly in manuscript, not in Machiavelli's print.
    a=round(255*phase(t,126.10,126.65))
    p.text((140,945),'reason + feeling :',31,'Inkfree.ttf',COPPER,a)
    p.text((456,945),'Human',31,'CascadiaMono.ttf',COPPER,a)
    # The ring reads the book, then the marginal note answers it.
    p.path([(1005,357),(1117,357)],phase(t,126.70,127.08),COPPER,2.2)
    p.path(bezier((1126,354),(1482,363),(1510,625),(1360,691)),phase(t,126.95,127.70),COPPER,2.2)
    if t>127.33:
        count=clamp((t-127.33)/.27)
        p.text((1320,680),'me'[:int(count*2+.01)],58,'Inkfree.ttf',COPPER)
    # Two proofs stay in place as lines bind them to the very same subject.
    p.path(bezier((470,616),(650,606),(716,679),(1290,682)),phase(t,T_MADE,T_MADE+.53),COPPER,3)
    p.path(bezier((453,822),(708,876),(878,786),(1290,758)),phase(t,T_MADE+.22,T_MADE+.82),COPPER,3)
    call=phase(t,129.45,130.08)
    # Written noun becomes an explicit call. The handwritten me never changes position.
    p.text((1050,691),'recognize(',42,'CascadiaMono.ttf',INK,int(call*255))
    p.text((1409,691),')',42,'CascadiaMono.ttf',INK,int(call*255))
    p.path([(1317,754),(1405,754)],phase(t,130.05,130.34),COPPER,2.2)
    p.text((1128,768),'argument: reason + feeling',25,'Inkfree.ttf',COPPER,int(phase(t,130.12,130.48)*210))
    # Diagnostic has a readable hold; tracing it back makes the disputed premise visible.
    e=phase(t,T_ERROR,T_ERROR+.14)
    if e>0:
        p.rect((1308,675,1410,750),RED,3,int(e*255))
        trace=bezier((1410,752),(1720,775),(1810,818),(1810,954))
        trace+=bezier((1810,954),(1690,1051),(741,1051),(563,965))[1:]
        p.path(trace,phase(t,131.49,132.08),RED,3)
        p.oval(502,966,57,24,phase(t,131.93,132.27),RED,3)
    # The gap circle is drawn in the unified shader so its path never cuts.
    return down(im)

