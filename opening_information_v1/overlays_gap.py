"""Measure the changing aperture, then withdraw before the historical images."""
import math
from PIL import ImageDraw
from common import blank, gate, tag, color, WHITE, COPPER

WINDOWS = [(47.80, 51.30)]

def overlay(mod, t, w, h):
    img=blank(w,h); alpha=gate(t,WINDOWS)
    if alpha <= 0: return img
    p=mod.params(t); dr=ImageDraw.Draw(img); s=h/1080
    half=p['u_half']; theta=p['u_gap']; zoom=p['u_zoom']; cam=p['u_cam']
    def px(x,y):
        return ((x-cam[0])/zoom*h+w/2, h/2-(y-cam[1])/zoom*h)
    rr=min(.30,p['u_R']*.84)
    # A concentric construction arc uses the aperture's actual two boundary angles.
    arc=[px(rr*math.cos(theta-half+2*half*i/80),rr*math.sin(theta-half+2*half*i/80)) for i in range(81)]
    dr.line(arc,fill=color(WHITE,.36*alpha),width=max(1,round(s)))
    for ang in (theta-half,theta+half):
        a=px((rr-.016)*math.cos(ang),(rr-.016)*math.sin(ang))
        b=px((rr+.016)*math.cos(ang),(rr+.016)*math.sin(ang))
        dr.line([a,b],fill=color(COPPER,alpha*.8),width=max(1,round(1.4*s)))
    # A single leader moves with the centre of the viewing sector.
    anc=px(rr*math.cos(theta),rr*math.sin(theta))
    tag(dr,anc,[f'APERTURE  {math.degrees(half)*2:05.1f}°',f'VISIBLE  {half/math.pi*100:04.1f}%'],w,h,
        alpha,tint=WHITE,side=(1,-1),offset=(92,72),mark='circle')
    return img
