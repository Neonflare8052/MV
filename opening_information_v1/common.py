"""Restrained, camera-anchored drafting marks; no lyric typography."""
import math
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont

WHITE = (220, 217, 207)
COPPER = (232, 160, 105)
DIM = (132, 136, 135)
FONT = 'C:/Windows/Fonts/CascadiaMono.ttf'

def clamp(x, lo=0., hi=1.):
    return max(lo, min(hi, x))

def smooth(x):
    x = clamp(x)
    return x*x*(3.-2.*x)

def gate(t, windows, fade=.18):
    return max((min(smooth((t-a)/fade), smooth((b-t)/fade)) for a,b in windows), default=0.)

@lru_cache(maxsize=32)
def font(px):
    return ImageFont.truetype(FONT, max(10, int(px)))

def project(p, params, w, h):
    cam, look = params['u_cam'], params['u_look']
    sub = lambda a,b: tuple(x-y for x,y in zip(a,b))
    dot = lambda a,b: sum(x*y for x,y in zip(a,b))
    def norm(a):
        n=math.sqrt(dot(a,a)); return tuple(v/n for v in a)
    cross = lambda a,b:(a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
    fw=norm(sub(look,cam)); rt=norm(cross(fw,(0.,1.,0.))); up=cross(rt,fw)
    v=sub(p,cam); z=dot(v,fw)
    if z <= .08: return None
    tf=2.*math.tan(params['u_fov']*.5)
    x,y=dot(v,rt)/z/tf, dot(v,up)/z/tf
    r=params.get('u_roll',0.); c,s=math.cos(r),math.sin(r)
    return (c*x-s*y)*h+w/2, h/2-(s*x+c*y)*h

def color(c, alpha):
    return (*c, round(255*clamp(alpha)))

def tag(draw, xy, lines, w, h, alpha=1., tint=WHITE, side=(1,-1), offset=(55,50), mark='diamond'):
    """Leader and two readable lines, bounded inside the frame."""
    if xy is None or alpha <= .001: return
    x,y=xy; scale=h/1080; sx,sy=side
    if not (-20<x<w+20 and -20<y<h+20): return
    f=font(30*scale); fs=font(25*scale)
    widths=[draw.textlength(s,font=f if i==0 else fs) for i,s in enumerate(lines)]
    bw=max(widths,default=0); bh=36*scale+(len(lines)-1)*32*scale
    ex=x+sx*offset[0]*scale; ey=y+sy*offset[1]*scale
    tx=ex+12*scale if sx>0 else ex-12*scale-bw
    tx=clamp(tx,38*scale,w-38*scale-bw)
    ty=clamp(ey-18*scale,35*scale,h-35*scale-bh)
    # Dark ink is a thin halo around the letters, with no opaque card behind them.
    col=color(tint,alpha); r=8*scale
    if mark=='diamond':
        draw.line([(x,y-r),(x+r,y),(x,y+r),(x-r,y),(x,y-r)],fill=col,width=max(1,round(1.5*scale)))
    elif mark=='circle':
        draw.ellipse((x-r,y-r,x+r,y+r),outline=col,width=max(1,round(1.5*scale)))
    elif mark=='cross':
        draw.line([(x-r,y),(x+r,y)],fill=col,width=max(1,round(scale)))
        draw.line([(x,y-r),(x,y+r)],fill=col,width=max(1,round(scale)))
    edge=tx-7*scale if sx>0 else tx+bw+7*scale
    draw.line([(x+sx*11*scale,y),(ex,ey),(edge,ey)],fill=color(tint,alpha*.65),width=max(1,round(scale)))
    for i,line in enumerate(lines):
        ff=f if i==0 else fs
        yy=ty+i*33*scale
        draw.text((tx,yy),line,font=ff,fill=color(tint if i==0 else DIM,alpha),stroke_width=max(1,round(scale)),stroke_fill=(4,5,5,round(alpha*185)))

def blank(w,h):
    return Image.new('RGBA',(w,h),(0,0,0,0))
