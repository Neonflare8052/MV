"""Native-resolution GPU vector compositor and instanced lit 3D scene renderer."""
import math
from pathlib import Path
import numpy as np
import moderngl
from PIL import Image,ImageDraw,ImageFont
from geometry import Renderer

V='''#version 330
in vec2 xy;in vec2 uv;in vec4 rgba;in float mode;
out vec2 p;out vec4 col;flat out int kind;
void main(){gl_Position=vec4(xy.x/960.-1.,1.-xy.y/540.,0,1);p=uv;col=rgba;kind=int(mode+.5);}
'''
F='''#version 330
in vec2 p;in vec4 col;flat in int kind;out vec4 frag;uniform sampler2D atlas;
void main(){float a=1.;if(kind==1){float d=length(p);a=1.-smoothstep(1.-fwidth(d),1.+fwidth(d),d);}if(kind==2)a=texture(atlas,p).r;frag=vec4(col.rgb,col.a*a);}
'''
IV='''#version 330
in vec2 xy;in vec2 uv;out vec2 p;
void main(){gl_Position=vec4(xy.x/960.-1.,1.-xy.y/540.,0,1);p=uv;}
'''
IF='''#version 330
in vec2 p;out vec4 frag;uniform sampler2D img;void main(){frag=texture(img,p);}
'''

def color(c):
    if isinstance(c,str):
        h=c.lstrip('#'); c=tuple(int(h[i:i+2],16)/255 for i in range(0,len(h),2))
    return tuple(c) if len(c)==4 else (*c,1.)

class Canvas:
    def __init__(self,w=3840,h=2160):
        self.w,self.h=w,h;self.renderer=Renderer(w,h);self.ctx=self.renderer.ctx;self.out=self.renderer.out
        self.prog=self.ctx.program(vertex_shader=V,fragment_shader=F)
        self.buf=self.ctx.buffer(reserve=9*4*200000)
        self.vao=self.ctx.vertex_array(self.prog,[(self.buf,'2f 2f 4f 1f','xy','uv','rgba','mode')])
        self.ip=self.ctx.program(vertex_shader=IV,fragment_shader=IF)
        self.ib=self.ctx.buffer(reserve=4*4*6);self.iv=self.ctx.vertex_array(self.ip,[(self.ib,'2f 2f','xy','uv')])
        self.atlas=self.ctx.texture((8192,8192),1,data=bytes(8192*8192));self.atlas.filter=(moderngl.LINEAR,moderngl.LINEAR)
        self.glyphs={};self.fonts={};self.images={};self.effects={};self.vertices=[]
        for name,path in [('mono','CascadiaMono.ttf'),('sans','segoeui.ttf'),('cjk','msyh.ttc')]:
            self.fonts[name]=ImageFont.truetype('C:/Windows/Fonts/'+path,128)
        self.clear((0,0,0))
    def state(self):
        self.out.use();self.ctx.viewport=(0,0,self.w,self.h);self.ctx.disable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.BLEND);self.ctx.blend_func=(moderngl.SRC_ALPHA,moderngl.ONE_MINUS_SRC_ALPHA)
    def clear(self,col):
        self.vertices=[];self.state();self.out.clear(*color(col))
    def _quad(self,x0,y0,x1,y1,uv0,uv1,col,mode=0):
        u0,v0=uv0;u1,v1=uv1;co=color(col)
        self.vertices.extend([(x0,y0,u0,v0,*co,mode),(x1,y0,u1,v0,*co,mode),(x1,y1,u1,v1,*co,mode),(x0,y0,u0,v0,*co,mode),(x1,y1,u1,v1,*co,mode),(x0,y1,u0,v1,*co,mode)])
    def rect(self,x,y,w,h,color): self._quad(x,y,x+w,y+h,(0,0),(1,1),color)
    def polygon(self,points,color):
        if len(points)<3:return
        co=globals()['color'](color)
        for i in range(1,len(points)-1):
            for x,y in (points[0],points[i],points[i+1]):self.vertices.append((x,y,0,0,*co,0))
    def line(self,x1,y1,x2,y2,color,width=2):
        dx=x2-x1;dy=y2-y1;l=math.hypot(dx,dy)
        if l<1e-7:return
        nx=-dy/l*width*.5;ny=dx/l*width*.5
        self.polygon([(x1+nx,y1+ny),(x2+nx,y2+ny),(x2-nx,y2-ny),(x1-nx,y1-ny)],color)
    def polyline(self,points,color,width=2,closed=False):
        pts=list(points)
        for a,b in zip(pts,pts[1:]):self.line(*a,*b,color,width)
        if closed and len(pts)>2:self.line(*pts[-1],*pts[0],color,width)
    def circle(self,x,y,r,color,fill=True,width=2):
        if r<=0:return
        if fill:self._quad(x-r,y-r,x+r,y+r,(-1,-1),(1,1),color,1)
        else:self.arc(x,y,r,0,math.tau,color,width)
    def ellipse(self,x,y,rx,ry,color,fill=False,width=2):
        if fill:self._quad(x-rx,y-ry,x+rx,y+ry,(-1,-1),(1,1),color,1)
        else:self.polyline([(x+rx*math.cos(a),y+ry*math.sin(a)) for a in np.linspace(0,math.tau,128)],color,width)
    def arc(self,x,y,r,start,end,color,width=2):
        n=max(8,min(256,int(abs(end-start)*max(10,r/8))))
        self.polyline([(x+r*math.cos(a),y+r*math.sin(a)) for a in np.linspace(start,end,n)],color,width)
    def _glyph(self,ch,font):
        if ord(ch)>255:font='cjk'
        key=(ch,font)
        if key not in self.glyphs:
            i=len(self.glyphs);x=(i%42)*192;y=(i//42)*192
            if y+192>8192:raise RuntimeError('Glyph atlas capacity exceeded')
            im=Image.new('L',(192,192));d=ImageDraw.Draw(im);f=self.fonts[font]
            d.text((8,148),ch,font=f,fill=255,anchor='ls')
            self.atlas.write(im.tobytes(),viewport=(x,y,192,192))
            self.glyphs[key]=(x,y,float(f.getlength(ch)))
        return self.glyphs[key]
    def text(self,text,x,y,size=24,color='#F2EBDD',font='mono',anchor='left'):
        text=str(text);sf=size/128;lines=text.split('\n')
        for j,line in enumerate(lines):
            gl=[self._glyph(ch,font) for ch in line];ln=sum(g[2] for g in gl)*sf
            xx=x-ln/2 if anchor=='center' else x-ln if anchor=='right' else x
            for gx,gy,advance in gl:
                self._quad(xx-8*sf,y+j*size*1.4-20*sf,xx+184*sf,y+j*size*1.4+172*sf,(gx/8192,gy/8192),((gx+192)/8192,(gy+192)/8192),color,2);xx+=advance*sf
    def flush(self):
        if not self.vertices:return
        self.state();data=np.asarray(self.vertices,dtype='f4').tobytes()
        if len(data)>self.buf.size:self.buf.orphan(len(data))
        self.buf.write(data);self.atlas.use(0);self.prog['atlas'].value=0
        self.vao.render(moderngl.TRIANGLES,vertices=len(self.vertices));self.vertices=[]
    def image(self,key,image,x,y,w,h):
        self.flush();self.state()
        if key not in self.images:
            im=image.convert('RGBA');tex=self.ctx.texture(im.size,4,im.tobytes());tex.filter=(moderngl.LINEAR,moderngl.LINEAR);self.images[key]=tex
        self.images[key].use(0);self.ip['img'].value=0
        a=np.array([(x,y,0,0),(x+w,y,1,0),(x+w,y+h,1,1),(x,y,0,0),(x+w,y+h,1,1),(x,y+h,0,1)],'f4')
        self.ib.write(a.tobytes());self.iv.render(moderngl.TRIANGLES)
    def render3d(self,scene,eye,target,fov=42,theme='mono',time=0,exposure=1):
        self.flush();self.renderer.render(scene,eye,target,fov,time,theme=theme,exposure=exposure);self.state()
    def effect(self,name,fragment,uniforms):
        self.flush();self.state()
        if name not in self.effects:
            p=self.ctx.program(vertex_shader=IV,fragment_shader=fragment);v=self.ctx.vertex_array(p,[(self.ib,'2f 2f','xy','uv')]);self.effects[name]=(p,v)
        p,v=self.effects[name]
        for k,val in uniforms.items():
            if k in p:p[k].value=val
        a=np.array([(0,0,0,0),(1920,0,1,0),(1920,1080,1,1),(0,0,0,0),(1920,1080,1,1),(0,1080,0,1)],'f4');self.ib.write(a.tobytes());v.render(moderngl.TRIANGLES)
    def read(self):
        self.flush();return self.out.read(components=3,alignment=1)
    def save(self,path):
        im=Image.frombytes('RGB',(self.w,self.h),self.read()).transpose(Image.Transpose.FLIP_TOP_BOTTOM);im.save(path)
