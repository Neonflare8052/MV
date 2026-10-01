"""Act II. Deterministic, native-resolution program animation.

The terminal, ASCII transition and cartoon are actually executed by this module;
they are not mocked video footage.  Coordinates are in the 1920x1080 design space.
"""
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from common import clamp, ease, progress, mix, BLACK, IVORY, COPPER, RED, YELLOW

TAU = 2 * math.pi
INK = '#302824'
PAPER = '#F2EBDD'
MUTED = '#555b5e'
DIM = '#262c30'
CYAN = '#a0c6ce'
_assets = {}


def rgba(col, a=1):
    if isinstance(col, str):
        col = tuple(int(col.lstrip('#')[i:i+2], 16)/255 for i in (0, 2, 4))
    return (*col[:3], clamp(a))


def bezier(points, n=36):
    """Piecewise cubic, with shared endpoints."""
    out = []
    for i in range(0, len(points)-1, 3):
        if i+3 >= len(points):
            break
        a, b, d, e = points[i:i+4]
        for j in range(n):
            u=j/(n-1); v=1-u
            out.append((v**3*a[0]+3*v*v*u*b[0]+3*v*u*u*d[0]+u**3*e[0],
                        v**3*a[1]+3*v*v*u*b[1]+3*v*u*u*d[1]+u**3*e[1]))
    return out


def path(c, pts, color, width=2, close=False):
    c.polyline(pts, color, width=width, closed=close)


def chalk_circle(c, x=960, y=540, r=190, fraction=1, alpha=1, gap=0,
                 rx=1, ry=1, color=IVORY, start=-1.17):
    pts=[]
    arc=max(0, TAU-gap)*clamp(fraction)
    for i in range(max(3, int(180*clamp(fraction)))):
        a=start+arc*i/max(1, int(180*clamp(fraction))-1)
        rr=r+1.4*math.sin(a*13+.8)+.8*math.sin(a*29)
        pts.append((x+math.cos(a)*rr*rx,y+math.sin(a)*rr*ry))
    path(c,pts,rgba(color,alpha),3)
    if fraction>.98:
        pts2=[(x+math.cos(a)*(r+2)*rx,y+math.sin(a)*(r+2)*ry)
              for a in np.linspace(start+.2,start+.8,20)]
        path(c,pts2,rgba(color,alpha*.25),1)


def cross(c,x,y,s=8,color=MUTED):
    c.line(x-s,y,x+s,y,color,1)
    c.line(x,y-s,x,y+s,color,1)


def _galaxy():
    """4K procedural photographic light plate with coherent spiral dust lanes."""
    if 'galaxy' in _assets:
        return _assets['galaxy']
    w,h=3840,2160
    x=np.linspace(-1.78,1.78,w,dtype=np.float32)[None,:]
    y=np.linspace(-1,1,h,dtype=np.float32)[:,None]
    # Tilted projected disk, physically evocative rather than a random star field.
    xx=x*.83+y*.42; yy=-x*.33+y*.89
    r=np.sqrt(xx*xx+(yy/0.60)**2)+.003
    a=np.arctan2(yy/.60,xx)
    spiral=.5+.5*np.cos(a*3-9*np.log(r+.07))
    lanes=(spiral**9)*np.exp(-r*2.25)
    cloud=(.6+.4*np.sin(xx*57+np.sin(yy*37))*np.sin(yy*42+np.sin(xx*29)))
    dust=lanes*(.5+.5*cloud)
    disk=np.exp(-r*3.9)
    core=np.exp(-(r/.105)**1.5)
    rgb=np.empty((h,w,3),dtype=np.float32)
    rgb[:,:,0]=.006+disk*.14+dust*.60+core*.82
    rgb[:,:,1]=.008+disk*.14+dust*.32+core*.73
    rgb[:,:,2]=.015+disk*.23+dust*.32+core*.53
    blue=(1-spiral)**9*np.exp(-r*2.6)
    rgb[:,:,1]+=blue*.10;rgb[:,:,2]+=blue*.18
    im=Image.fromarray(np.uint8(np.clip(rgb,0,1)*255),'RGB')
    del rgb, lanes, cloud, dust, disk, core, blue, r, a, spiral
    stars=Image.new('RGB',(w,h)); d=ImageDraw.Draw(stars)
    rng=random.Random(1051)
    for i in range(780):
        px=rng.randrange(w);py=rng.randrange(h); rr=rng.choice((1,1,1,2))
        v=rng.randrange(25,100)
        d.ellipse((px-rr,py-rr,px+rr,py+rr),fill=(v,int(v*.94),int(v*.86)))
    im=Image.fromarray(np.maximum(np.array(im),np.array(stars)))
    _assets['galaxy']=im
    return im


def _ascii_eye():
    from visual_assets import ascii_eye
    return ascii_eye()


def _scan_galaxy(c,t):
    c.clear(BLACK)
    c.image('middle_galaxy',_galaxy(),0,0,1920,1080)
    q=ease(progress(t,59.35,61.92)); sy=q*1080
    c.rect(0,0,1920,sy,BLACK)
    # Draw only the part above the raster conversion line.
    for arm in range(3):
        for band in (-.06,0,.06):
            pts=[]
            for j in range(200):
                r=.03+j/199*1.12
                a=arm*TAU/3+2.7*math.log(r+.09)+band*6
                xx=r*math.cos(a); yy=r*math.sin(a)*.6
                X=960+(xx*.91-yy*.4)*650
                Y=540+(xx*.34+yy*.88)*650
                if Y<sy:
                    pts.append((X,Y))
                elif len(pts)>1:
                    path(c,pts,rgba(CYAN,.55 if band==0 else .23),1.7);pts=[]
            if len(pts)>1:path(c,pts,rgba(CYAN,.55 if band==0 else .23),1.7)
    for i in range(82):
        rr=85+i*5.3; aa=i*2.399
        X=960+math.cos(aa)*rr;Y=540+math.sin(aa)*rr*.48
        if Y<sy:c.circle(X,Y,1.5,rgba(IVORY,.55))
    if 0<q<1:
        c.line(0,sy,1920,sy,rgba(IVORY,.9),2)
        c.line(0,sy+3,1920,sy+3,rgba(CYAN,.25),2)
    if sy>125:
        c.text('WORLD / 01',105,78,21,rgba(IVORY,.74))
        c.text('LIVE SIMULATION',1815,78,18,rgba(CYAN,.65),anchor='right')
    if sy>1020:
        c.text('TIME SCALE   1.00e+06',105,985,18,rgba(CYAN,.6))
        c.text('FIELD SAMPLES   65,536',1815,985,18,rgba(CYAN,.6),anchor='right')


def _body(c,cx,cy,scale=1,alpha=1,t=0):
    col=rgba(CYAN,alpha*.91)
    c.ellipse(cx,cy-222*scale,48*scale,61*scale,col,width=2.2)
    half=[(25,-166),(27,-140),(85,-126),(105,-80),(117,12),(134,77),
          (116,91),(92,25),(72,-55),(67,63),(55,110),(63,164),
          (53,250),(35,310),(11,310),(22,214),(20,126),(0,107)]
    for side in (-1,1):
        path(c,[(cx+side*x*scale,cy+y*scale) for x,y in half],col,2.2)
    c.line(cx,cy-130*scale,cx,cy+110*scale,rgba(CYAN,alpha*.18),1)
    c.circle(cx-16*scale,cy-60*scale,12*scale,rgba(COPPER,alpha),False,2)
    for j in range(7):
        yy=cy+(-120+j*51)*scale
        c.line(cx-58*scale,yy,cx+58*scale,yy,rgba(CYAN,alpha*.12),1)
    scan=(t*.37)%1
    c.line(cx-135*scale,cy+(-275+580*scan)*scale,cx+135*scale,
           cy+(-275+580*scan)*scale,rgba(IVORY,alpha*.24),1)


def _tiny_plot(c,x,y,w,h,phase=0,alpha=1,kind=0):
    c.line(x,y+h,x+w,y+h,rgba(IVORY,.09*alpha),1)
    pts=[]
    for i in range(91):
        v=i/90; z=math.sin(v*19+phase)*.22+math.sin(v*47+phase*.7)*.05
        if kind==1:z=.16*math.sin(v*3+phase)+.07*math.sin(v*15)
        pts.append((x+v*w,y+h*(.46-z)))
    path(c,pts,rgba(CYAN,.94*alpha),2.0)


def _physiology(c,t):
    c.clear(BLACK)
    change=ease(progress(t,62.589,65.25))
    c.text('OBSERVATION',110,85,20,rgba(IVORY,.65))
    c.text('SUBJECT / 01' if change>.5 else 'WORLD / 01',1810,85,19,rgba(CYAN,.7),anchor='right')
    c.line(110,134,1810,134,rgba(IVORY,.12),1)
    c.line(1220,202,1220,930,rgba(IVORY,.13),1)
    # Conserved geometry morphs from a spiral graph into a sampled organism.
    for k in range(3):
        pts=[]
        for j in range(150):
            r=j/149*350;a=k*TAU/3+j/28
            pts.append((670+r*math.cos(a),546+r*math.sin(a)*.6))
        path(c,pts,rgba(CYAN,(1-change)*.50),1.6)
    _body(c,670,530,1.07,change,t)
    if change>.3:
        c.line(745,465,972,410,rgba(COPPER,change*.6),1)
        c.text('RESPONSE',979,389,18,rgba(COPPER,change*.7))
        c.text('NO DIRECT ACCESS',979,416,14,rgba(IVORY,change*.35))
    labelsA=['TIME SCALE','MATTER DENSITY','TEMPERATURE']
    labelsB=['CARDIAC ACTIVITY','SKIN CONDUCTANCE','CORE TEMPERATURE']
    valsA=['1.00e+06','0.31','2.725 K']; valsB=['72 bpm','3.8 uS','36.8 C']
    for i in range(3):
        yy=210+i*186
        lbl=labelsB[i] if change>(i+1)*.22 else labelsA[i]
        val=valsB[i] if change>(i+1)*.22 else valsA[i]
        c.text(lbl,1300,yy,18,rgba(IVORY,.53))
        c.text(val,1300,yy+38,31,IVORY)
        _tiny_plot(c,1510,yy+30,270,70,t*.7+i,1,i%2)
    c.line(1300,790,1790,790,rgba(IVORY,.15),1)
    c.text('SATISFACTION / ESTIMATE',1300,822,18,rgba(COPPER,.9))
    barx=1300; bw=480
    c.line(barx,890,barx+bw,890,rgba(IVORY,.21),2)
    low=.37+.025*math.sin(t*4);high=.72+.03*math.sin(t*3.1)
    c.rect(barx+bw*low,870,bw*(high-low),40,rgba(COPPER,.15))
    c.line(barx+bw*.57,865,barx+bw*.57,915,rgba(COPPER,.9),2)
    c.text('UNCERTAINTY REMAINS',1300,931,15,rgba(YELLOW,.76))
    if t>=65.397:
        c.rect(1285,811,525,137,rgba(COPPER,.05))
        for xx,yy,sx,sy in [(1285,811,1,1),(1810,811,-1,1),(1285,948,1,-1),(1810,948,-1,-1)]:
            c.line(xx,yy,xx+sx*18,yy,COPPER,1.5);c.line(xx,yy,xx,yy+sy*18,COPPER,1.5)


CODE=[
    ('> execute(assess_autonomic_state(subject));',0),
    ('  feedback: awaiting self_report',1),
    ('> execute(simulate_analgesia(subject));',0),
    ('  WARNING  response model uncertain',2),
    ('> execute(regulate_affect(subject));',0),
    ('  WARNING  objective not converged',2),
    ('> execute(regulate_affect);',0),
    ('> execute();',0),
    ('> exe',0),
]


def _terminal(c,t):
    c.clear(BLACK)
    q=progress(t,66.601,70.084)
    z=1+ease(progress(t,68.2,70.084))*1.1
    header=1-progress(t,68.0,68.45)
    c.text('RUN / SUBJECT_01',95,77,19,rgba(COPPER,.85*header))
    c.line(95,126,1825,126,rgba(IVORY,.12*header),1)
    left=100-80*(z-1);top=205-150*(z-1)
    count=1+int(q*11)
    exelines=max(0,int((q-.73)*29))
    scroll=max(0,top+(min(count,9)+exelines)*62*z-900)
    for i,(s,kind) in enumerate(CODE[:min(count,9)]):
        # Typed, genuinely deterministic terminal output.
        age=q*11-i
        chars=int(clamp(age)*len(s))
        if chars<=0:continue
        co=YELLOW if kind==2 else (MUTED if kind==1 else IVORY)
        yy=top+i*62*z-scroll
        if yy>-75:c.text(s[:chars],left,yy,24*z,co)
    if q<.64:
        c.line(1208,190,1208,945,rgba(IVORY,.12),1)
        _body(c,1505,505,.72,.5,t)
        c.text('FEEDBACK',1410,819,17,rgba(CYAN,.55))
        _tiny_plot(c,1370,870,320,68,t,1)
    if q>.73:
        n=int((q-.73)*240)
        s=('exe'*n)
        for row in range(min(7,1+len(s)//57)):
            yy=top+(9+row)*62*z-scroll
            if yy>-75:c.text(s[row*57:(row+1)*57],left,yy,33*z,IVORY)


def _ascii(c,t):
    c.clear(BLACK)
    q=ease(progress(t,70.084,72.25))
    zoom=mix(3.0,1.0,q)
    w=1920*zoom;h=1080*zoom
    c.image('middle_ascii_eye',_ascii_eye(),960-w/2,540-h/2,w,h)
    if t>=73.169:
        c.rect(487,475,946,130,rgba(BLACK,.94))
        c.text('SIMULATION',960,480,88,RED,anchor='center')
    # Discrete seeded per-cell state changes, with no rotating geometry.
    p=ease(progress(t,73.56,74.30))
    if p>0:
        for row in range(45):
            for col in range(80):
                key=((row*73856093)^(col*19349663)^48171)&0xffffffff
                v=((key*1664525+1013904223)&0xffffffff)/4294967296
                if 20<=row<=25 and 20<col<60:v=.48+v*.52
                if v<p:c.rect(col*24,row*24,24.25,24.25,PAPER)


def _ellipse_outline(c,x,y,rx,ry,fill,stroke=INK,width=3):
    c.ellipse(x,y,rx,ry,fill,fill=True)
    c.ellipse(x,y,rx,ry,stroke,width=width)


def _eggplant(c,x,y,s=1,alpha=1):
    P=[(x-18*s,y-56*s),(x+100*s,y-17*s),(x+53*s,y+97*s),(x-43*s,y+82*s),
       (x-95*s,y+69*s),(x-70*s,y+17*s),(x-18*s,y-56*s)]
    b=bezier(P)
    c.polygon(b,rgba('#71567d',alpha));path(c,b,rgba(INK,alpha),3,True)
    leaves=[(x-24*s,y-52*s),(x-13*s,y-85*s),(x+0*s,y-68*s),(x+25*s,y-82*s),
            (x+19*s,y-49*s),(x+50*s,y-33*s),(x+11*s,y-28*s),(x-5*s,y-6*s),
            (x-14*s,y-38*s),(x-41*s,y-29*s)]
    c.polygon(leaves,rgba('#849570',alpha));path(c,leaves,rgba(INK,alpha),2.5,True)
    c.line(x-12*s,y-68*s,x-17*s,y-97*s,rgba(INK,alpha),4)
    path(c,bezier([(x-43*s,y+10*s),(x-59*s,y+37*s),(x-48*s,y+54*s),(x-32*s,y+59*s)]),rgba('#a690ab',alpha*.8),5)


def _tomato(c,x,y,s=1,alpha=1):
    _ellipse_outline(c,x,y+15*s,77*s,66*s,rgba('#cb6555',alpha),rgba(INK,alpha),3)
    pts=[]
    for i in range(10):
        a=-math.pi/2+i*math.pi/5;r=(41 if i%2==0 else 14)*s
        pts.append((x+math.cos(a)*r,y-41*s+math.sin(a)*r*.56))
    c.polygon(pts,rgba('#71876b',alpha));path(c,pts,rgba(INK,alpha),2,True)
    c.line(x,y-46*s,x+9*s,y-76*s,rgba(INK,alpha),4)
    path(c,bezier([(x-39*s,y-8*s),(x-53*s,y+3*s),(x-52*s,y+21*s),(x-45*s,y+29*s)]),rgba('#e6a090',alpha),5)


def _cat(c,x,y,s=1,closed=False,alpha=1):
    body=bezier([(x-61*s,y+38*s),(x-74*s,y-3*s),(x-54*s,y-34*s),(x-37*s,y-34*s),
                 (x-56*s,y-78*s),(x-29*s,y-82*s),(x-10*s,y-48*s),
                 (x+12*s,y-51*s),(x+27*s,y-42*s),(x+38*s,y-43*s),
                 (x+54*s,y-83*s),(x+75*s,y-73*s),(x+63*s,y-28*s),
                 (x+93*s,y+10*s),(x+53*s,y+74*s),(x-3*s,y+71*s),
                 (x-37*s,y+72*s),(x-54*s,y+54*s),(x-61*s,y+38*s)])
    c.polygon(body,rgba('#c99a68',alpha));path(c,body,rgba(INK,alpha),3,True)
    for dx in (-25,29):
        if closed:
            path(c,[(x+(dx-10)*s,y+14*s),(x+dx*s,y+19*s),(x+(dx+10)*s,y+14*s)],rgba(INK,alpha),3)
        else:
            c.ellipse(x+dx*s,y+14*s,6*s,10*s,rgba(INK,alpha),fill=True)
    c.polygon([(x-6*s,y+31*s),(x+7*s,y+31*s),(x,y+37*s)],rgba(INK,alpha))
    c.line(x,y+37*s,x,y+44*s,rgba(INK,alpha),2)
    for dx in (-1,1):
        for k in range(2):
            c.line(x+dx*35*s,y+(34+k*11)*s,x+dx*83*s,y+(28+k*20)*s,rgba(INK,alpha),2)
        c.line(x+dx*12*s,y-37*s,x+dx*9*s,y-14*s,rgba('#7d6348',alpha),5)
    c.line(x,y-41*s,x,y-19*s,rgba('#7d6348',alpha),5)


def _box(c,x,base,w=330,open_amount=0,alpha=1):
    s=w/330; dep=67*s; hh=250*s
    left=x-w/2;top=base-hh
    c.ellipse(x+15*s,base+18*s,w*.64,21*s,rgba('#443b31',alpha*.10),fill=True)
    front=[(left,top),(left+w,top+13*s),(left+w,base),(left,base-15*s)]
    side=[(left+w,top+13*s),(left+w+dep,top-28*s),(left+w+dep,base-45*s),(left+w,base)]
    roof=[(left,top),(left+dep,top-53*s),(left+w+dep,top-28*s),(left+w,top+13*s)]
    for pts,co in [(side,'#b98d5c'),(front,'#d6ad78'),(roof,'#e0bd8c')]:
        c.polygon(pts,rgba(co,alpha));path(c,pts,rgba(INK,alpha),3,True)
    if open_amount>0:
        mid=top-18*s
        slit=[(left+26*s,mid),(left+w+40*s,mid+5*s),
              (left+w+40*s,mid+open_amount*72*s),(left+26*s,mid+open_amount*60*s)]
        c.polygon(slit,rgba('#100f0e',alpha))
    c.line(left+dep/2,top-24*s,left+w+dep/2,top-7*s,rgba(INK,alpha*.5),2)
    c.line(left+18*s,base-34*s,left+60*s,base-32*s,rgba(INK,alpha*.3),1)
    c.line(left+w-28*s,top+39*s,left+w-29*s,base-25*s,rgba(INK,alpha*.14),1)
    c.text('?',x,top+49*s,118*s,rgba(INK,alpha),font='sans',anchor='center')
    c.text('HANDLE WITH CARE',x,base-44*s,12*s,rgba(INK,alpha*.45),anchor='center')


def _cartoon(c,t):
    if t>=84.878:
        _open_cartoon(c,t)
        return
    c.clear(PAPER)
    dt=t-74.16
    drop=clamp(dt/.64)
    if drop<1:
        base=-120+920*drop*drop
    else:
        age=dt-.64;base=800-32*math.exp(-age*7)*abs(math.sin(age*15))
    shift=ease(progress(t,75.0,76.0))
    xx=mix(960,660,shift)
    wobble=math.sin((t-83.6)*24)*3 if 83.6<t<84.268 else 0
    _box(c,xx+wobble,base,330)
    entries=[(74.65,355,'eggplant'),(77.576,540,'tomato'),(81.351,748,'cat')]
    for i,(start,yy,name) in enumerate(entries):
        q=progress(t,start,start+.35)
        if q<=0:continue
        s=.70*(1+math.sin(q*math.pi)*.12)
        fade=.4 if t>=84.268 and i<2 else 1
        c.text('0'+str(i+1),1125,yy-18,19,rgba(INK,.40*fade))
        if i==0:_eggplant(c,1260,yy,s,fade)
        elif i==1:_tomato(c,1260,yy,s,fade)
        else:
            _cat(c,1217,yy,.57,False,fade);_cat(c,1360,yy,.57,True,fade)
            c.text('/',1295,yy-12,27,rgba(INK,.35),anchor='center')
        if i<2:c.text('?',1455,yy-30,43,rgba(INK,.6*fade),font='sans')
        else:c.text('?',1487,yy-30,43,rgba(INK,.6),font='sans')
        if i<2:c.line(1125,yy+102,1510,yy+102,rgba(INK,.12),1)
    if 76.959<=t<77.576:
        for i in range(3):
            c.circle(1412+i*20,335+i*13,4,rgba('#89976e',.8))
    if 80.620<=t<81.351:
        cross(c,1428,502,10,rgba('#bf8261',.8))
    if t>=84.268:
        m=clamp((t-84.268)/.19)
        c.text('meow'[:max(1,int(m*4))],xx+28,base-405,63,INK,font='sans',anchor='center')
        path(c,[(xx-61,base-318),(xx-48,base-343)],rgba(INK,.72),2.4)
        path(c,[(xx+97,base-313),(xx+111,base-337)],rgba(INK,.72),2.4)


def _open_cartoon(c,t):
    """Two sets of seam vertices share texture coordinates, then separate.

    The still really is mapped to a cut 2D mesh, rather than covered by a wipe.
    A framebuffer copy is created from a deterministic preceding animation frame.
    """
    import moderngl
    key=('middle_open_mesh',id(c))
    if key not in _assets:
        _cartoon(c,84.877)
        c.flush()
        tex=c.ctx.texture((c.w,c.h),4)
        tex.filter=(moderngl.LINEAR,moderngl.LINEAR)
        fb=c.ctx.framebuffer(color_attachments=[tex])
        c.ctx.copy_framebuffer(fb,c.out)
        prog=c.ctx.program(vertex_shader='''#version 330
in vec2 xy;in vec2 uv;out vec2 p;
void main(){gl_Position=vec4(xy.x/960.-1.,1.-xy.y/540.,0,1);p=uv;}
''',fragment_shader='''#version 330
in vec2 p;out vec4 frag;uniform sampler2D plate;
void main(){frag=texture(plate,p);}
''')
        buf=c.ctx.buffer(reserve=4*4*20*12*2*6)
        vao=c.ctx.vertex_array(prog,[(buf,'2f 2f','xy','uv')])
        _assets[key]=(tex,fb,prog,buf,vao)
    tex,fb,prog,buf,vao=_assets[key]
    c.clear(BLACK)
    q=clamp((t-84.878)/.2)
    spread=ease(clamp((q-.2)/.8))
    vertices=[]
    def vertex(u,f,side):
        # Local box-lid opening precedes the opening of the whole picture.
        seam=.49+(u-.34375)*.038
        v=f*seam if side<0 else seam+(1-seam)*f
        local=math.exp(-((u-.34375)/.105)**8)
        reach=ease(clamp(spread*2.8-abs(u-.34375)*1.4))
        d=local*clamp(q/.2)*7 + reach*spread*1450
        y=v*1080+side*d
        return (u*1920,y,u,1-v)
    for side in (-1,1):
        for j in range(12):
            for i in range(20):
                a=vertex(i/20,j/12,side);b=vertex((i+1)/20,j/12,side)
                d=vertex(i/20,(j+1)/12,side);e=vertex((i+1)/20,(j+1)/12,side)
                vertices.extend((a,b,e,a,e,d))
    data=np.asarray(vertices,dtype='f4').tobytes()
    buf.write(data);tex.use(0);prog['plate'].value=0
    c.state();vao.render(moderngl.TRIANGLES,vertices=len(vertices))


def _orbit(c,t,fade=1,show_circle=True):
    center=(960,540); age=t-86.538
    angle=-.85+age*.61
    rr=530
    points=[(960+rr*math.cos(a),540+rr*.43*math.sin(a)) for a in np.linspace(-.85,angle,100)]
    path(c,points,rgba(IVORY,.20*fade),1.2)
    for j in range(8):
        a=-.85+j*.13
        if a<angle:c.circle(960+rr*math.cos(a),540+rr*.43*math.sin(a),2,rgba(IVORY,.36*fade))
    x=960+rr*math.cos(angle);y=540+rr*.43*math.sin(angle)
    for r,a in [(22,.015),(15,.025),(10,.055),(6,.3),(3,1)]:
        c.circle(x,y,r,rgba('#ffebc6',a*fade))
    if show_circle:
        frac=ease(progress(t,87.72,88.13))
        chalk_circle(c,r=190,fraction=frac,alpha=fade)


def _identity(c,t):
    c.clear(BLACK)
    if t<86.538:return
    if t<88.587:
        _orbit(c,t)
        return
    f=1-ease(progress(t,88.587,89.15))
    if f>0:_orbit(c,t,f,False)
    chalk_circle(c)
    if t<90.197:
        if int((t-88.587)*2.8)%2==0:c.rect(952,510,3,54,IVORY)
    elif t<92.015:
        m=t>=91.08
        if 90.93<t<91.08:c.rect(921,493,78,100,rgba(COPPER,.42))
        c.text('M' if m else 'F',960,479,100,IVORY,anchor='center')
    elif t<93.953:
        commands=['self.name','self.voice','self.form','self.name','_']
        idx=min(4,int((t-92.015)*2.6))
        s=commands[idx]
        c.text(s,960,516,26,IVORY,anchor='center')
        c.line(835,569,1085,569,rgba(COPPER,.4),1)
    else:
        p=progress(t,93.953,95.465)
        hh=int(8+p*14);minute=int(p*840)%60
        c.text(f'{hh%12 or 12:02d}:{minute:02d}',960,490,54,IVORY,anchor='center')
        c.text('AM' if hh<12 else 'PM',960,565,23,COPPER,anchor='center')


def _roles(c,t):
    c.clear(BLACK)
    q=ease(progress(t,95.465,97.2))
    spread=145*q; ry=mix(1,.38,q);r=mix(190,220,q)
    switch=ease(progress(t,98.20,98.42))
    colors=[mix(.92,.18,switch),mix(.18,.92,switch)]
    for i,yy in enumerate((540-spread,540+spread)):
        chalk_circle(c,960,yy,r,rx=1,ry=ry,alpha=colors[i])
    if t>99.349:
        q=progress(t,99.349,100)
        c.line(960,540+spread,960,540+spread-2*spread*q,rgba(COPPER,.6),1)


def _tunnel(c,t):
    c.clear(BLACK)
    age=t-99.349
    enter=ease(progress(t,99.349,101.474))
    cx=960
    twist=0 if t<101.474 else (t-101.474)*.085
    move=max(0,t-101.474)*.7
    approach=ease(progress(t,102.73,103.489))
    rings=[]
    for j in range(24):
        z=(j/24+move)%1
        r=mix(220,45+(z**2)*1400,enter)
        ratio=mix(.38,1,enter)
        cy=mix(395+j/23*290,540,enter)
        r=mix(r,3000+(j-12)*90,approach)
        cy=mix(cy,-2200,approach)
        pts=[]
        for k in range(201):
            a=k/200*TAU+twist*z*(1-approach)
            pts.append((cx+math.cos(a)*r,cy+math.sin(a)*r*ratio))
        opacity=(.08+.5*z)*enter if j not in (0,23) else mix(.20 if j==0 else .92,.08+.5*z,enter)
        opacity=mix(opacity,.24,approach)
        path(c,pts,rgba(IVORY,opacity),1.3+z)
        rings.append((r,ratio,z))
    for k in range(12):
        pts=[]
        for z in np.linspace(0,1,90):
            r=mix(220,45+z*z*1400,enter);a=k/12*TAU+twist*z
            cy=mix(395+z*290,540,enter)
            pts.append((cx+math.cos(a)*r,cy+math.sin(a)*r*mix(.38,1,enter)))
        path(c,pts,rgba(COPPER,.2*enter*(1-approach)),1)
    if approach<.1:c.circle(cx,540,32*enter,BLACK)


def ecg_value(p):
    p=p%1
    return (0.12*math.exp(-((p-.19)/.040)**2)
            -.11*math.exp(-((p-.375)/.018)**2)
            +1.0*math.exp(-((p-.408)/.012)**2)
            -.29*math.exp(-((p-.45)/.021)**2)
            +.26*math.exp(-((p-.66)/.081)**2))


def _ecg(c,t,cx=960,cy=540,w=1550,amp=115,alpha=1,beat=True):
    pts=[]
    for j in range(451):
        x=cx-w/2+w*j/450
        phase=(j/450*2.1+t*.90)
        val=ecg_value(phase) if beat else 0
        pts.append((x,cy-amp*val))
    path(c,pts,rgba(IVORY,alpha),2.4)


def _heartbeat(c,t):
    c.clear(BLACK)
    if t<106.293:
        q=ease(progress(t,103.489,105.45))
        for j in range(-6,7):
            yy=540+j*90
            pts=[]
            for i in range(121):
                x=i*16
                curve=(1-q)*(1-((x-960)/1100)**2)*260
                pts.append((x,yy+curve))
            path(c,pts,rgba(IVORY,.42 if j==0 else .2*(1-progress(t,104.9,106.293))),1.5)
    elif t<107.22:
        _ecg(c,t)
    else:
        q=ease(progress(t,107.22,110.221))
        r=mix(430,190,q)
        # Two former straight strokes become a circle around the live ECG.
        for side in (-1,1):
            pts=[]
            for i in range(161):
                x=-r+2*r*i/160
                yy=side*math.sqrt(max(0,r*r-x*x))
                flat=side*(230-40*q)
                y=mix(flat,yy,q)
                pts.append((960+x,540+y))
            path(c,pts,rgba(IVORY,.9),2.5)
        _ecg(c,t,w=2*r-28,amp=mix(100,57,q))
        if t>=110.221:
            pulse=math.exp(-((t-110.41)/.14)**2)
            chalk_circle(c,r=190+3*pulse,alpha=.9)


def _sine_tan(c,t):
    tr=ease(progress(t,114.18,114.84))
    # Three distinct tangent branches; finite clip bounds explicitly respected.
    for n in range(-2,3):
        pts=[]
        for j in range(121):
            a=-1.31+j/120*2.62
            x=960+(a+n*math.pi)*150
            sy=540-math.sin(a+n*math.pi)*145
            ty=540-math.tan(a)*86
            y=mix(sy,ty,tr)
            pts.append((x,y))
        path(c,pts,COPPER,2.7)


def _departure(c,t):
    c.clear(BLACK)
    if t<112.22:
        if t<111.12:
            chalk_circle(c)
            _ecg(c,t,w=352,amp=57,alpha=1-progress(t,110.9,111.12),beat=False)
        else:
            # Familiar orbit with its physical source suddenly removed.
            c.ellipse(960,540,530,228,rgba(IVORY,.11),width=1)
            if t<111.30:_orbit(c,t,1,False)
            for j in range(12):
                a=j*TAU/12
                c.circle(960+530*math.cos(a),540+228*math.sin(a),1.6,rgba(IVORY,.21))
    elif t<113.10:
        c.clear(PAPER)
        _box(c,660,800,330,alpha=1-ease(progress(t,112.34,112.57)))
        # Guesses remain for a fraction, then the familiar field becomes empty.
        if t<112.42:
            _eggplant(c,1260,355,.7);_tomato(c,1260,540,.7);_cat(c,1260,748,.65)
    elif t<114.18:
        chalk_circle(c,alpha=.55,gap=.6)
        c.line(806,540,1114,540,rgba(IVORY,.58),2)
    elif t<114.92:
        _sine_tan(c,t)
    elif t<115.78:
        p=ease(progress(t,114.92,115.58))
        for n in range(-3,4):
            x=960+n*210
            pts=[]
            for j in range(121):
                a=-1.31+j/120*2.62
                pts.append((x+a*92*(1-p),540-math.tan(a)*86))
            path(c,pts,IVORY,2.3)
    else:
        q=ease(progress(t,115.78,116.65));shrink=ease(progress(t,116.4,117.274))
        for n in range(-3,4):
            x=960+n*210*(1-q);hh=320*(1-shrink)
            c.line(x,540-hh,x,540+hh,IVORY,2.5)
        c.circle(960,540,mix(2,4,shrink),IVORY)


def _fragments(c,t):
    c.clear(BLACK)
    c.circle(960,540,4,IVORY)
    if t<121.728:
        # Six surviving references, erased by a single travelling selection.
        positions=[(600,345),(1000,300),(1330,388),(1260,770),(841,825),(532,680)]
        appeared=ease(progress(t,118.333,118.979))
        deleted=max(0,int((t-119.05)/.29)) if t>=119.05 else 0
        for i,(x,y) in enumerate(positions):
            if i<deleted:continue
            al=appeared*.62
            if i==0:c.arc(x,y,60,-2.4,-.1,rgba(IVORY,al),2)
            elif i==1:
                path(c,[(x-45,y),(x-11,y),(x-4,y+14),(x+3,y-38),(x+12,y+9),(x+20,y),(x+60,y)],rgba(IVORY,al),2)
            elif i==2:c.text('exe',x,y-20,32,rgba(IVORY,al),anchor='center')
            elif i==3:
                c.polygon([(x-45,y-40),(x+45,y-32),(x+45,y+35),(x-45,y+25)],rgba(COPPER,al))
            elif i==4:
                for j in range(4):c.circle(x-36+j*24,y,2.5,rgba(IVORY,al))
            else:path(c,[(x-55,y+23),(x-14,y-14),(x+20,y+17),(x+55,y-26)],rgba(COPPER,al),2)
            if i==deleted and t>=118.979:
                for xx,yy,sx,sy in [(x-73,y-65,1,1),(x+73,y-65,-1,1),(x-73,y+65,1,-1),(x+73,y+65,-1,-1)]:
                    c.line(xx,yy,xx+sx*17,yy,rgba(IVORY,.5),1)
                    c.line(xx,yy,xx,yy+sy*17,rgba(IVORY,.5),1)
    else:
        move=ease(progress(t,121.728,122.40))
        # Subtle sideways move is the waiting gesture; return as the ring draws.
        c.clear(BLACK)
        draw=ease(progress(t,122.714,124.65))
        dotx=960-26*move*(1-draw)
        c.circle(dotx,540,4,IVORY)
        chalk_circle(c,r=190,fraction=draw,gap=.60)
        if t>=124.89:
            repair=math.sin(progress(t,124.89,125.34)*math.pi)
            if repair>0:
                start=-1.17+TAU-.6
                pts=[(960+190*math.cos(a),540+190*math.sin(a)) for a in np.linspace(start,start+.6,40)]
                path(c,pts,rgba(IVORY,repair*.75),2.5)


def draw(c,t):
    if t<61.958:
        _scan_galaxy(c,t)
    elif t<66.601:
        _physiology(c,t)
    elif t<70.084:
        _terminal(c,t)
    elif t<74.30:
        _ascii(c,t)
    elif t<85.078:
        _cartoon(c,t)
    elif t<95.465:
        _identity(c,t)
    elif t<99.349:
        _roles(c,t)
    elif t<103.489:
        _tunnel(c,t)
    elif t<110.9:
        _heartbeat(c,t)
    elif t<118.333:
        _departure(c,t)
    else:
        _fragments(c,t)
