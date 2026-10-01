"""Census cards on a winding steam train. Independent procedural 2.5D study.

World geometry and camera are genuinely three-dimensional; visible surfaces are
painted as flat vector polygons. No models, images, or downloaded assets.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import subprocess
import time

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FFMPEG, FFPROBE = ROOT / 'tools/ffmpeg.exe', ROOT / 'tools/ffprobe.exe'
SONG = next(ROOT.glob('*.mp3'))
START = 162.632
STAMP = 165.166 - START
CUT = 166.016 - START
END = CUT + 2.0
INK = (29, 28, 31)
CREAM = (235, 227, 211)
PAPER = (246, 239, 221)
MID = (167, 157, 143)
RED = (171, 23, 30)
RUBY = (206, 33, 38)
N_CARS, SPACING, SPEED = 30, 6.84, 4.2
GEOMETRY_SCALE = 2.0
FONT = 'C:/Windows/Fonts/cour.ttf'
FONTB = 'C:/Windows/Fonts/courbd.ttf'
FAR_POS = np.array([-45.,58.,-35.])
FAR_LOOK = np.array([5.,9.,53.])


def smooth(x):
    x = np.clip(x, 0., 1.)
    return x*x*(3.-2.*x)


def mix(a, b, k):
    return np.asarray(a)*(1-k) + np.asarray(b)*k


def track():
    z = np.linspace(-68., 225., 10000)
    x = 21*np.sin((z-15)/27) + 5*np.sin(z/69)
    pts = np.stack((x, np.zeros_like(z), z), axis=1)
    length = np.r_[0., np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
    return pts, length


TRACK, DIST = track()


def pose(s):
    p = np.array([np.interp(s, DIST, TRACK[:,i]) for i in range(3)])
    a = np.array([np.interp(s-.3, DIST, TRACK[:,i]) for i in range(3)])
    b = np.array([np.interp(s+.3, DIST, TRACK[:,i]) for i in range(3)])
    tangent = b-a
    tangent /= max(np.linalg.norm(tangent), 1e-9)
    right = np.array([tangent[2], 0., -tangent[0]])
    return p, right, tangent


def local(s, pts):
    p, right, tangent = pose(s)
    v = np.asarray(pts, dtype=float)*GEOMETRY_SCALE
    return p + v[...,0,None]*right + v[...,1,None]*np.array([0.,1.,0.]) + v[...,2,None]*tangent


def make_card(index=4):
    w, h = 2200, 970
    im = Image.new('RGB', (w,h), PAPER)
    d = ImageDraw.Draw(im)
    bold = lambda n: ImageFont.truetype(FONTB,n)
    regular = lambda n: ImageFont.truetype(FONT,n)
    d.rectangle((7,7,w-8,h-8), outline=INK, width=7)
    d.text((68,76),'VOLKSZÄHLUNG 1939',font=bold(85),fill=INK,anchor='lm')
    d.text((w-60,76),'17. MAI 1939',font=bold(44),fill=INK,anchor='rm')
    d.line((55,143,w-55,143),fill=INK,width=5)
    labels=['Geburtsjahr','Geschlecht','Familienstand','Beruf','Religion','Muttersprache','Abstammung','Gemeinde']
    for j,label in enumerate(labels):
        x0=58+j*260
        if j:d.line((x0,153,x0,258),fill=INK,width=2)
        d.text((x0+125,195),label,font=bold(27),fill=INK,anchor='mm')
    d.line((55,263,w-55,263),fill=INK,width=3)
    for row in range(10):
        for col in range(80):
            x=70+col*26
            y=310+row*55
            d.text((x,y),str(row),font=regular(29),fill=(99,93,85),anchor='mm')
    for col in range(80):
        d.text((70+col*26,920),str(col+1),font=regular(16),fill=INK,anchor='mm')
    rng=np.random.default_rng(17+index*7)
    for col in range(80):
        row=int(rng.integers(0,10))
        x=70+col*26
        y=310+row*55
        d.rectangle((x-5,y-15,x+5,y+15),fill=INK)
    d.text((63,883),'STATISTISCHE KARTE',font=bold(28),fill=INK)
    d.text((w-61,883),f'NR. {57+index:04d}',font=regular(25),fill=INK,anchor='ra')
    return im


CARD_VARIANTS=[]
for _index in range(N_CARS):
    _base=make_card(_index)
    _marked=_base.copy()
    _red_draw=ImageDraw.Draw(_marked)
    _red_draw.rectangle((1720,372,1810,536),fill=RED)
    _red_draw.rectangle((7,940,2192,962),fill=RED)
    CARD_VARIANTS.append((_base,_marked))


class Camera:
    def __init__(self,t,w,h):
        self.w,self.h=w,h
        s=13.5 + 4*SPACING + SPEED*t
        p,right,tangent=pose(s)
        target=p-right*.83*GEOMETRY_SCALE+np.array([0.,1.74*GEOMETRY_SCALE,0.])
        close=target-right*2.18*GEOMETRY_SCALE + np.array([0.,.075,0.]) - tangent*.025
        # A single continuous crane: no cuts, logarithmic distance and smooth yaw.
        k=float(smooth((t-.48)/(STAMP-.48)))
        far_target=FAR_LOOK
        far_pos=FAR_POS
        self.look=mix(target,far_target,k*k)
        offset0=close-target
        offset1=far_pos-far_target
        dist0,dist1=np.linalg.norm(offset0),np.linalg.norm(offset1)
        direction=mix(offset0/dist0,offset1/dist1,k)
        direction/=np.linalg.norm(direction)
        distance=math.exp(math.log(dist0)*(1-k)+math.log(dist1)*k)
        self.eye=self.look+direction*distance
        tail=float(smooth((t-STAMP)/(END-STAMP)))
        self.eye+=np.array([-3.,1.,2.])*tail
        self.look+=np.array([0.,0.,3.])*tail
        self.f=(self.look-self.eye);self.f/=np.linalg.norm(self.f)
        self.r=np.cross(self.f,[0.,1.,0.]);self.r/=np.linalg.norm(self.r)
        self.u=np.cross(self.r,self.f)
        self.focal=h/(2*math.tan(math.radians(36)/2))
        self.roll=math.radians(-3.0*float(smooth((t-1.0)/1.0)))

    def project(self,p):
        v=np.asarray(p)-self.eye
        z=v@self.f
        xy=np.stack((v@self.r,v@self.u),axis=-1)
        xy=xy*self.focal/np.maximum(z[...,None],.02)
        cs,sn=math.cos(self.roll),math.sin(self.roll)
        xx=xy[...,0]*cs-xy[...,1]*sn
        yy=xy[...,0]*sn+xy[...,1]*cs
        return np.stack((self.w*.5+xx,self.h*.5-yy),axis=-1),z


class Painter:
    def __init__(self,camera):
        self.cam=camera
        self.commands=[]

    def polygon(self,points,color,outline=None,width=1,texture=False):
        pts=np.asarray(points)
        xy,z=self.cam.project(pts)
        if z.min()<=.025:return
        if xy[:,0].max()<-10 or xy[:,0].min()>self.cam.w+10 or xy[:,1].max()<-10 or xy[:,1].min()>self.cam.h+10:return
        self.commands.append((float(z.mean()),'texture' if texture is not False else 'poly',xy,color,outline,width,texture))

    def line(self,points,color,width=1):
        pts=np.asarray(points)
        xy,z=self.cam.project(pts)
        if z.min()<=.025:return
        if xy[:,0].max()<-10 or xy[:,0].min()>self.cam.w+10 or xy[:,1].max()<-10 or xy[:,1].min()>self.cam.h+10:return
        self.commands.append((float(z.mean())-.025,'line',xy,color,None,width,False))

    def box(self,s,center,size,colors=(INK,INK,INK),outline=None):
        c=np.asarray(center);sx,sy,sz=np.asarray(size)/2
        v=local(s,c+np.array([[-sx,-sy,-sz],[sx,-sy,-sz],[sx,sy,-sz],[-sx,sy,-sz],[-sx,-sy,sz],[sx,-sy,sz],[sx,sy,sz],[-sx,sy,sz]]))
        faces=[([0,1,2,3],0),([4,7,6,5],0),([0,3,7,4],1),([1,5,6,2],1),([3,2,6,7],2),([0,4,5,1],2)]
        for ids,ci in faces:
            pts=v[ids]
            normal=np.cross(pts[1]-pts[0],pts[2]-pts[0])
            if np.dot(normal,self.cam.eye-pts.mean(axis=0))<=0:
                self.polygon(pts,colors[ci],outline)

    def cylinder(self,s,center,radius,length,axis='z',color=INK,n=16):
        cs=[]
        for end in (-length/2,length/2):
            a=np.arange(n)*2*math.pi/n
            if axis=='z':v=np.stack((radius*np.cos(a),radius*np.sin(a),np.full(n,end)),axis=1)
            elif axis=='x':v=np.stack((np.full(n,end),radius*np.sin(a),radius*np.cos(a)),axis=1)
            else:v=np.stack((radius*np.cos(a),np.full(n,end),radius*np.sin(a)),axis=1)
            cs.append(local(s,np.asarray(center)+v))
        for side in cs:self.polygon(side,color)
        for j in range(n):
            self.polygon([cs[0][j],cs[0][(j+1)%n],cs[1][(j+1)%n],cs[1][j]],color)

    def paint(self,image):
        draw=ImageDraw.Draw(image)
        for _,kind,xy,color,outline,width,texture in sorted(self.commands,key=lambda item:item[0],reverse=True):
            coords=[tuple(p) for p in xy]
            if kind=='line':draw.line(coords,fill=color,width=max(1,int(width)),joint='curve')
            else:
                draw.polygon(coords,fill=color)
                if outline:draw.line(coords+[coords[0]],fill=outline,width=max(1,int(width)),joint='curve')
                if kind=='texture':
                    warp_texture(image,texture,xy)
                    draw=ImageDraw.Draw(image)
        return image


def warp_texture(image,texture,quad):
    """Project a planar card into its quad, operating only inside its screen crop."""
    # Vertex ordering is bottom-left, bottom-right, top-right, top-left.
    bbox=np.r_[quad.min(axis=0)-2,quad.max(axis=0)+2]
    x0,y0=max(0,int(bbox[0])),max(0,int(bbox[1]))
    x1,y1=min(image.width,int(math.ceil(bbox[2]))),min(image.height,int(math.ceil(bbox[3])))
    if x1<=x0 or y1<=y0:return
    dst=quad-np.array([x0,y0])
    src=np.array([[0,texture.height],[texture.width,texture.height],[texture.width,0],[0,0]],dtype=float)
    A=[];B=[]
    for (x,y),(u,v) in zip(dst,src):
        A.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]])
        B.extend([u,v])
    coeff=np.linalg.solve(np.asarray(A),np.asarray(B))
    tile=texture.transform((x1-x0,y1-y0),Image.Transform.PERSPECTIVE,coeff,Image.Resampling.BICUBIC)
    mask=Image.new('L',tile.size);ImageDraw.Draw(mask).polygon([tuple(p) for p in dst],fill=255)
    image.paste(tile,(x0,y0),mask)


def card(p,s,x,y,z,t,index):
    width,height=2.18,.963
    pts=np.array([[x,y-height/2,z-width/2],[x,y-height/2,z+width/2],[x,y+height/2,z+width/2],[x,y+height/2,z-width/2]])
    if x>0:pts=pts[[1,0,3,2]]
    world=local(s,pts)
    _,right,_=pose(s)
    normal=right*(1 if x>0 else -1)
    if np.dot(normal,p.cam.eye-world.mean(axis=0))<0:return
    xy,depth=p.cam.project(world)
    facewidth=np.linalg.norm(xy[0]-xy[1])
    p.polygon(world,PAPER,INK,max(1,p.cam.h/1000),texture=CARD_VARIANTS[index][int(t>=STAMP)] if facewidth>12 else False)
    if 10<facewidth<=12:
        for u in (.16,.3,.44,.58,.72,.86):
            yy=y-height*.5+height*u
            p.line(local(s,[[x-.005,yy,z-width*.46],[x-.005,yy,z+width*.46]]),(158,149,134),max(1,p.cam.h/1200))
        for u in (-.30,-.1,.1,.3):
            p.line(local(s,[[x-.007,y+height*.29,z+width*u],[x-.007,y+height*.46,z+width*u]]),INK,max(1,p.cam.h/1300))
    # Identical position, different cards: the classification becomes a train-long red line.
    hz=z+width*.31;hy=y+height*.1
    color=RUBY if t>=STAMP else INK
    hw,hh=.044,.076
    hole=local(s,[[x-.016,hy-hh,hz-hw],[x-.016,hy-hh,hz+hw],[x-.016,hy+hh,hz+hw],[x-.016,hy+hh,hz-hw]])
    # Far shot: a small red printed registration band makes the simultaneous event legible.
    if facewidth<=12:p.polygon(hole,color)


def wagon(p,s,t,index):
    # Open, ribbed freight cradle. Cards are a physical stack, not a window sticker.
    p.box(s,[0,.69,0],[1.96,.22,2.98],colors=((50,45,43),INK,(58,53,47)))
    p.box(s,[0,.5,0],[1.55,.19,2.90])
    for z in (-.92,.92):
        bogie_s=s+z*GEOMETRY_SCALE
        p.box(bogie_s,[0,.32,0],[1.45,.22,.45])
        for x in (-.88,.88):
            p.cylinder(bogie_s,[x,.30,0],.29,.14,axis='x',n=10)
            # Wheel rim and spoke are visible primarily in the revealing middle distance.
            a=SPEED*t/(.29*GEOMETRY_SCALE)
            wx=x-.077 if x<0 else x+.077
            p.line(local(bogie_s,[[wx,.3+.2*math.sin(a),.2*math.cos(a)],[wx,.3-.2*math.sin(a),-.2*math.cos(a)]]),MID,max(1,p.cam.h/1350))
    for z in (-1.53,1.53):p.box(s,[0,.60,z],[.15,.13,.35])
    for x in (.48,.16,-.16,-.50,-.80):
        # Cream edges of the stack; the nearest sheet carries the actual census face.
        p.box(s,[x,1.67,0],[.07,.963,2.18],colors=((181,170,150),(218,208,188),PAPER))
    # Both exposed sides carry the same census face across the S bends.
    card(p,s,-.845,1.67,0,t,index)
    card(p,s,.845,1.67,0,t,index)
    if t>=STAMP:
        # A printed red edge links the identical holes into one distant ribbon.
        for x in (-.82,.82):
            p.box(s,[x,2.166,0],[.07,.07,2.18],colors=(RED,RED,RED))
    for x in (-.94,.94):
        for z in (-1.37,1.37):p.box(s,[x,1.02,z],[.075,.66,.095])
        p.box(s,[x,.96,0],[.07,.14,2.94],colors=(INK,INK,INK))


def locomotive(p,s,t):
    # Distinct steam silhouette: boiler, funnel, cab, driving wheels and connecting rod.
    p.box(s,[0,.64,0],[2.2,.3,6.7])
    p.cylinder(s,[0,1.65,.82],.8,4.25,n=20)
    p.cylinder(s,[0,1.66,2.99],.85,.16,n=20)
    p.box(s,[0,2.1,-2.04],[2.13,2.75,1.96],colors=(INK,(41,38,38),(48,44,41)))
    p.box(s,[0,3.56,-2.03],[2.43,.15,2.15])
    # Empty geometric cab windows, not detailed model ornament.
    for x in (-1.074,1.074):
        p.polygon(local(s,[[x,2.22,-2.75],[x,2.22,-1.49],[x,3.06,-1.49],[x,3.06,-2.75]]),CREAM)
        p.line(local(s,[[x,2.2,-2.1],[x,3.08,-2.1]]),INK,max(1,p.cam.h/900))
    p.cylinder(s,[0,2.9,2.20],.35,1.25,axis='y',n=12)
    p.cylinder(s,[0,3.56,2.20],.5,.15,axis='y',n=12)
    p.cylinder(s,[0,2.7,.33],.42,.7,axis='y',n=12)
    for x in (-1.02,1.02):
        for z in (-1.3,.15,1.6):
            p.cylinder(s,[x,.62,z],.59,.20,axis='x',n=16)
            phase=SPEED*t/(.59*GEOMETRY_SCALE)
            dx=x-.105 if x<0 else x+.105
            a=np.array([dx,.62+.3*math.sin(phase),z+.3*math.cos(phase)])
            p.line(local(s,[[dx,.62,z],a]),RED,max(1,p.cam.h/700))
        dx=x-.13 if x<0 else x+.13
        p.line(local(s,[[dx,.62+.3*math.sin(phase),-1.3+.3*math.cos(phase)],[dx,.62+.3*math.sin(phase),1.6+.3*math.cos(phase)]]),MID,max(1,p.cam.h/450))
    # A flat triangular pilot gives the nose a clear direction.
    p.polygon(local(s,[[-1.12,.5,3.38],[1.12,.5,3.38],[0,.17,4.16]]),INK)
    p.box(s,[0,1.02,-4.65],[2.02,1.4,2.85],colors=(INK,(45,41,39),(56,49,44)))
    p.box(s,[0,1.77,-4.65],[1.65,.12,2.5])
    for zz in (-5.45,-3.82):
        for xx in (-.96,.96):p.cylinder(s,[xx,.3,zz],.28,.14,axis='x',n=10)


def rails(p,t):
    lo,hi=5.,295.
    ss=np.linspace(lo,hi,250)
    for x in (-.69,.69):
        pts=np.array([local(s,[[x,.03,0]])[0] for s in ss])
        for k in range(0,len(pts)-1,3):p.line(pts[k:k+4],INK,max(1,p.cam.h/720))
        pts=np.array([local(s,[[x-.055,.01,0]])[0] for s in ss])
        for k in range(0,len(pts)-1,3):p.line(pts[k:k+4],(188,175,153),max(1,p.cam.h/980))
    for s in np.arange(lo,hi,.78):
        p.line(local(s,[[-1.0,.00,0],[1.0,.00,0]]),(99,90,78),max(1,p.cam.h/950))
    # Far parallel siding underlines industrial perspective without filling the sky.
    for x in (-3.2,-3.85):
        pts=np.array([local(s,[[x,.02,0]])[0] for s in np.linspace(203.,295.,90)])
        for k in range(0,len(pts)-1,3):p.line(pts[k:k+4],(138,127,112),max(1,p.cam.h/1100))


def factory(p):
    # The destination belongs to the same paper world; no photoreal materials.
    s=264.
    p.box(s,[0,2.6,3.8],[11.,5.2,13.5],colors=((53,47,44),INK,(65,56,48)))
    # Saw-tooth roof planes, strongly graphic in the high view.
    for zz in np.arange(-1.9,10.,2.35):
        p.polygon(local(s,[[-5.5,5.2,zz],[5.5,5.2,zz],[5.5,6.8,zz+2.35],[-5.5,6.8,zz+2.35]]),INK)
        p.polygon(local(s,[[-5.5,5.2,zz+2.35],[5.5,5.2,zz+2.35],[5.5,6.8,zz+2.35],[-5.5,6.8,zz+2.35]]),(140,123,103))
    for xx in (-3.5,3.5):
        p.box(s,[xx,8.0,9.],[1.1,9.,1.1],colors=(INK,INK,(63,54,45)))
        p.box(s,[xx,12.5,9.],[1.5,.45,1.5])
    # Track mouth: a cream arch slit framed with black, used to read the destination.
    p.polygon(local(s,[[-1.6,.1,-2.97],[1.6,.1,-2.97],[1.6,3.3,-2.97],[-1.6,3.3,-2.97]]),CREAM)
    for xx in (-4.,4.):
        p.polygon(local(s,[[xx-.28,2.6,-2.98],[xx+.28,2.6,-2.98],[xx+.28,4.3,-2.98],[xx-.28,4.3,-2.98]]),MID)


def smoke(p,t,engine_s):
    # Discrete ink clouds, not volumetric fog. Wind carries the train's history backwards.
    for j in range(30):
        age=(j*.105+t*.55)%3.15
        emit_s=engine_s-SPEED*age
        base=local(emit_s,[[0,3.65,2.2]])[0]
        _,right,tangent=pose(emit_s)
        center=base-tangent*7.0*age+np.array([0.,5.8*age,0.])+right*.6*math.sin(age*1.5)
        radius=.40+1.35*age
        points=[]
        for k in range(28):
            a=k*2*math.pi/28
            rr=radius*(1+.10*math.sin(5*a+j*.7))
            points.append(center+p.cam.r*math.cos(a)*rr+p.cam.u*math.sin(a)*rr*.72)
        color=tuple(int(v) for v in mix((38,34,33),(127,114,96),smooth(age/3.4)))
        p.polygon(points,color)
        # Etched negative-space flow lines keep individual puffs legible.
        if j%4==0 and age>.45:
            pp=[center+p.cam.r*math.cos(a)*radius*.66+p.cam.u*math.sin(a)*radius*.42 for a in np.linspace(.12,2.1,12)]
            p.line(pp,CREAM,max(1,p.cam.h/1000))
    for stack in (-3.5,3.5):
        base=local(264.,[[stack,12.8,9.]])[0]
        for j in range(6):
            age=(j*.65+t*.38)%4.
            c=base+np.array([-1.5*age,1.1*age,.5*age])
            rad=.75+.45*age
            pp=[c+p.cam.r*math.cos(a)*rad+p.cam.u*math.sin(a)*rad*.75 for a in np.linspace(0,2*math.pi,18,endpoint=False)]
            p.polygon(pp,(84,73,61))


def poster_finish(image,t,ss):
    d=ImageDraw.Draw(image)
    w,h=image.size
    k=float(smooth((t-1.52)/.5))
    if k:
        fc=tuple(int(v) for v in mix(CREAM,INK,k))
        d.text((w*.056,h*.066),'17. V. 1939',font=ImageFont.truetype(FONTB,round(h*.023)),fill=fc)
        d.line((w*.056,h*.093,w*.195,h*.093),fill=fc,width=max(1,ss))
    # Edge paper grain is deterministic, not a visual-effect layer hiding the geometry.
    arr=np.asarray(image,dtype=np.float32)
    rng=np.random.default_rng(1951939)
    noise=rng.normal(0,.9,(h,w,1)).astype(np.float32)
    arr+=noise
    return Image.fromarray(np.clip(arr,0,255).astype(np.uint8))


def render(t,w,h,ss=2):
    W,H=w*ss,h*ss
    cam=Camera(t,W,H)
    image=Image.new('RGB',(W,H),CREAM)
    p=Painter(cam)
    rails(p,t)
    # Each wagon center follows arc length. Its front and back bogies see the bend independently.
    for i in range(N_CARS):
        s=13.5+i*SPACING+SPEED*t
        wagon(p,s,t,i)
    engine_s=13.5+N_CARS*SPACING+9.+SPEED*t
    locomotive(p,engine_s,t)
    factory(p)
    smoke(p,t,engine_s)
    image=p.paint(image)
    # Opening red-through-paper becomes a legible pale card within twelve frames.
    if t<.24:
        amount=.65*(1-float(smooth(t/.24)))
        image=Image.blend(image,Image.new('RGB',image.size,(38,15,16)),amount)
    image=poster_finish(image,t,ss)
    if ss!=1:image=image.resize((w,h),Image.Resampling.LANCZOS)
    return image


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--w',type=int,default=1920)
    ap.add_argument('--h',type=int,default=1080)
    ap.add_argument('--ss',type=int,default=2)
    ap.add_argument('--fps',type=int,default=60)
    ap.add_argument('--duration',type=float,default=END)
    ap.add_argument('--stills',type=str)
    ap.add_argument('--out',type=Path,default=HERE/'census_train_study_1080p60.mp4')
    args=ap.parse_args()
    HERE.mkdir(parents=True,exist_ok=True)
    if args.stills:
        d=HERE/'stills';d.mkdir(exist_ok=True)
        frames=[]
        for t in map(float,args.stills.split(',')):
            im=render(t,args.w,args.h,args.ss)
            path=d/f'{t:05.2f}.png';im.save(path);frames.append((t,im))
            print('still',t,flush=True)
        cw=640;ch=360;cols=3
        sheet=Image.new('RGB',(cw*cols,(ch+32)*math.ceil(len(frames)/cols)),(20,20,20))
        dr=ImageDraw.Draw(sheet)
        ft=ImageFont.truetype(FONT,24)
        for i,(t,im) in enumerate(frames):
            x,y=(i%cols)*cw,(i//cols)*(ch+32)
            sheet.paste(im.resize((cw,ch),Image.Resampling.LANCZOS),(x,y))
            dr.text((x+12,y+ch+3),f'{t:05.2f}s  /  {START+t:07.3f}',font=ft,fill='white')
        sheet.save(HERE/'design_sheet.jpg',quality=95)
        return
    n=round(args.duration*args.fps)
    cmd=[str(FFMPEG),'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{args.w}x{args.h}',
         '-framerate',str(args.fps),'-i','pipe:0','-ss',str(START),'-t',str(n/args.fps),'-i',str(SONG),'-map','0:v','-map','1:a',
         '-c:v','h264_nvenc','-preset','p5','-rc','vbr','-cq','18','-b:v','18M','-pix_fmt','yuv420p',
         '-c:a','aac','-b:a','320k','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','+faststart',str(args.out)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    began=time.monotonic()
    for i in range(n):
        im=render(i/args.fps,args.w,args.h,args.ss)
        proc.stdin.write(im.tobytes())
        if i%60==0:print(f'{i}/{n} frames  {time.monotonic()-began:.1f}s',flush=True)
    proc.stdin.close()
    code=proc.wait()
    if code:raise RuntimeError(f'Encoding failed: {code}')
    manifest={'source':str(SONG),'source_sha256':hashlib.sha256(SONG.read_bytes()).hexdigest(),
              'output':str(args.out),'start_in_song':START,'duration':n/args.fps,'width':args.w,'height':args.h,'fps':args.fps,'frames':n,
              'renderer':'Python / NumPy world projection + Pillow vector paint / 2x supersampling / H.264 NVENC',
              'cues':{'card_read_until':.48,'red_holes':STAMP,'original_cut':CUT},
              'external_visual_assets':[],'elapsed_seconds':round(time.monotonic()-began,2)}
    (HERE/'render_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print('done',str(args.out),flush=True)


if __name__=='__main__':main()
