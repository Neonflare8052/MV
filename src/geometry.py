"""Original geometry renderer for the MV. Uses no generated image assets."""
import math, contextlib
from collections import defaultdict
import numpy as np
import moderngl

def normalize(x):
    x=np.asarray(x,dtype='f4'); return x/max(float(np.linalg.norm(x)),1e-8)

def transform(pos=(0,0,0),rot=(0,0,0),scale=1):
    x,y,z=rot; cx,sx=math.cos(x),math.sin(x); cy,sy=math.cos(y),math.sin(y); cz,sz=math.cos(z),math.sin(z)
    rx=np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]],dtype='f4')
    ry=np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]],dtype='f4')
    rz=np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]],dtype='f4')
    m=np.eye(4,dtype='f4'); m[:3,:3]=(rz@ry@rx)*np.asarray(scale); m[:3,3]=pos; return m

class Scene:
    def __init__(self): self.items=defaultdict(list); self.parent=np.eye(4,dtype='f4')
    @contextlib.contextmanager
    def group(self,pos=(0,0,0),rot=(0,0,0),scale=1):
        p=self.parent; self.parent=p@transform(pos,rot,scale)
        try: yield self
        finally: self.parent=p
    def add(self,mesh,pos,scale,color,rot=(0,0,0),emission=0):
        m=self.parent@transform(pos,rot,scale)
        self.items[mesh].append(np.concatenate((m.T.ravel(),np.asarray((*color[:3],emission),dtype='f4'))))
    def box(self,pos,size,color,rot=(0,0,0),emission=0): self.add('box',pos,size,color,rot,emission)
    def glass(self,pos,size,color=(.30,.65,.71),opacity=.07,rot=(0,0,0)): self.add('glass',pos,size,color,rot,-opacity)
    def sphere(self,pos,scale,color,emission=0): self.add('sphere',pos,scale,color,emission=emission)
    def cylinder(self,pos,radius,height,color,rot=(0,0,0),emission=0): self.add('cylinder',pos,(radius,height,radius),color,rot,emission)
    def cone(self,pos,radius,height,color,rot=(0,0,0),emission=0): self.add('cone',pos,(radius,height,radius),color,rot,emission)
    def torus(self,pos,radius,tube,color,rot=(0,0,0),emission=0):
        # Unit major radius; cache ratio-specific geometry.
        key=('torus',round(tube/radius,4)); self.add(key,pos,radius,color,rot,emission)
    def rod(self,a,b,radius,color,emission=0):
        a=np.asarray(a,dtype='f4'); b=np.asarray(b,dtype='f4'); v=b-a; length=float(np.linalg.norm(v))
        if length<1e-6:return
        y=v/length; ref=np.array((0,0,1) if abs(y[2])<.95 else (1,0,0),dtype='f4'); x=normalize(np.cross(y,ref)); z=np.cross(x,y)
        m=np.eye(4,dtype='f4');m[:3,0]=x*radius;m[:3,1]=y*length;m[:3,2]=z*radius;m[:3,3]=(a+b)/2
        m=self.parent@m; self.items['cylinder'].append(np.concatenate((m.T.ravel(),np.asarray((*color[:3],emission),dtype='f4'))))

def mesh_data(kind):
    rows=[]
    def tri(a,b,c,n=None):
        if n is None:n=normalize(np.cross(np.array(b)-a,np.array(c)-a))
        for p in (a,b,c):rows.append((*p,*n))
    if kind in ('box','glass'):
        for axis in range(3):
            for sign in (-1,1):
                n=np.zeros(3);n[axis]=sign;u=np.zeros(3);v=np.zeros(3);u[(axis+1)%3]=.5;v[(axis+2)%3]=.5;c=n*.5
                p=[c-u-v,c+u-v,c+u+v,c-u+v]
                tri(p[0],p[1],p[2],n);tri(p[0],p[2],p[3],n)
    elif kind=='sphere':
        lat,lon=12,20
        def pt(i,j):
            a=math.pi*i/lat;b=2*math.pi*j/lon;return (math.sin(a)*math.cos(b),math.cos(a),math.sin(a)*math.sin(b))
        for i in range(lat):
            for j in range(lon):
                a,b,c,d=pt(i,j),pt(i+1,j),pt(i+1,j+1),pt(i,j+1)
                for p in (a,b,c,a,c,d):rows.append((*p,*p))
    elif kind in ('cylinder','cone'):
        N=24
        for i in range(N):
            a=2*math.pi*i/N;b=2*math.pi*(i+1)/N
            pa=(math.cos(a),-.5,math.sin(a));pb=(math.cos(b),-.5,math.sin(b))
            pc=(math.cos(b),.5,math.sin(b));pd=(math.cos(a),.5,math.sin(a))
            tri((0,-.5,0),pb,pa,(0,-1,0))
            if kind=='cone': tri(pa,pb,(0,.5,0))
            else:
                tri((0,.5,0),pd,pc,(0,1,0))
                for p,n in [(pa,(math.cos(a),0,math.sin(a))),(pb,(math.cos(b),0,math.sin(b))),(pc,(math.cos(b),0,math.sin(b))),(pa,(math.cos(a),0,math.sin(a))),(pc,(math.cos(b),0,math.sin(b))),(pd,(math.cos(a),0,math.sin(a)))]:rows.append((*p,*n))
    else:
        tube=kind[1];N,M=48,10
        def pt(i,j):
            a=2*math.pi*i/N;b=2*math.pi*j/M;n=(math.cos(a)*math.cos(b),math.sin(b),math.sin(a)*math.cos(b))
            return ((math.cos(a)*(1+tube*math.cos(b)),tube*math.sin(b),math.sin(a)*(1+tube*math.cos(b))),n)
        for i in range(N):
            for j in range(M):
                for ij in ((i,j),(i+1,j),(i+1,j+1),(i,j),(i+1,j+1),(i,j+1)):
                    p,n=pt(*ij);rows.append((*p,*n))
    return np.asarray(rows,dtype='f4')

def look_at(eye,target,up=(0,1,0)):
    eye=np.asarray(eye,dtype='f4');f=normalize(np.asarray(target)-eye);r=normalize(np.cross(f,up));u=np.cross(r,f)
    m=np.eye(4,dtype='f4');m[:3,:3]=[r,u,-f];m[:3,3]=-m[:3,:3]@eye;return m
def perspective(fov,aspect,near=.1,far=150):
    f=1/math.tan(math.radians(fov)/2);m=np.zeros((4,4),dtype='f4');m[0,0]=f/aspect;m[1,1]=f;m[2,2]=(far+near)/(near-far);m[2,3]=2*far*near/(near-far);m[3,2]=-1;return m
def ortho(l,r,b,t,n,f):
    m=np.eye(4,dtype='f4');m[0,0]=2/(r-l);m[1,1]=2/(t-b);m[2,2]=-2/(f-n);m[0,3]=-(r+l)/(r-l);m[1,3]=-(t+b)/(t-b);m[2,3]=-(f+n)/(f-n);return m

VERT='''#version 330
in vec3 in_pos; in vec3 in_normal;
in vec4 m0; in vec4 m1; in vec4 m2; in vec4 m3; in vec4 in_color;
uniform mat4 vp; uniform mat4 light_vp;
out vec3 pos; out vec3 norm; out vec4 col; out vec4 light_pos;
void main(){mat4 m=mat4(m0,m1,m2,m3);vec4 p=m*vec4(in_pos,1.);pos=p.xyz;norm=normalize(transpose(inverse(mat3(m)))*in_normal);col=in_color;light_pos=light_vp*p;gl_Position=vp*p;}
'''
FRAG='''#version 330
in vec3 pos; in vec3 norm; in vec4 col; in vec4 light_pos;
uniform sampler2DShadow shadow_map;
uniform vec3 eye; uniform vec3 light_dir;uniform vec3 key_color;uniform vec3 ambient;uniform vec3 fog_color;uniform float fog_density;
out vec4 frag;
void main(){
vec3 n=normalize(norm);vec3 l=normalize(light_dir);vec3 v=normalize(eye-pos);
if(col.a<0.){float rim=pow(1.-abs(dot(n,v)),3.);frag=vec4(col.rgb*(.3+rim*.25),min(.30,-col.a+rim*.18));return;}
vec3 sc=light_pos.xyz/light_pos.w*.5+.5;float shadow=0.;float bias=max(.0022*(1.-dot(n,l)),.0012);
for(int x=-1;x<=1;x++)for(int y=-1;y<=1;y++)shadow+=texture(shadow_map,vec3(sc.xy+vec2(x,y)/2048.,sc.z-bias))/9.;
if(sc.x<0.||sc.x>1.||sc.y<0.||sc.y>1.||sc.z>1.)shadow=1.;
float diffuse=max(dot(n,l),0.);float hemi=.55+.45*n.y;
vec3 base=pow(max(col.rgb,vec3(0.)),vec3(1.8));
vec3 lit=base*(ambient*(.5+hemi*.5)+key_color*diffuse*shadow*1.7);
float rim=pow(1.-max(dot(n,v),0.),3.5)*.15;lit+=base*vec3(.65,.67,.70)*rim;
vec3 halfv=normalize(l+v);float spec=pow(max(dot(n,halfv),0.),48.)*.12*shadow;lit+=key_color*spec;
lit+=base*col.a*2.;float fog=1.-exp(-length(eye-pos)*fog_density);lit=mix(lit,fog_color,fog);
frag=vec4(lit,1.);}
'''
SVERT='''#version 330
in vec3 in_pos;in vec4 m0;in vec4 m1;in vec4 m2;in vec4 m3;uniform mat4 light_vp;
void main(){gl_Position=light_vp*mat4(m0,m1,m2,m3)*vec4(in_pos,1.);}
'''
QUAD='''#version 330
in vec2 in_vert;out vec2 uv;void main(){uv=in_vert*.5+.5;gl_Position=vec4(in_vert,0,1);}
'''
BLUR='''#version 330
in vec2 uv;out vec4 frag;uniform sampler2D tex;uniform vec2 direction;uniform int first_pass;
vec3 readtex(vec2 p){vec3 c=texture(tex,p).rgb;return first_pass==1?max(c-vec3(.65),vec3(0.)):c;}
void main(){vec3 c=readtex(uv)*.227027;c+=readtex(uv+direction*1.384615)*.316216;c+=readtex(uv-direction*1.384615)*.316216;c+=readtex(uv+direction*3.230769)*.070270;c+=readtex(uv-direction*3.230769)*.070270;frag=vec4(c,1);}
'''
POST='''#version 330
in vec2 uv;out vec4 frag;uniform sampler2D tex;uniform sampler2D bloom_tex;uniform sampler2D overlay_tex;uniform sampler2D depth_tex;
uniform float focus_distance;uniform vec2 pixel_size;
uniform float time;uniform float fade;uniform float glitch;uniform vec3 tint;uniform float exposure;
float hash(vec2 p){return fract(sin(dot(p,vec2(12.9898,78.233)))*43758.5453);}
vec3 aces(vec3 x){return clamp((x*(2.51*x+.03))/(x*(2.43*x+.59)+.14),0.,1.);}
void main(){vec2 q=uv;float strip=step(.91,hash(vec2(floor(uv.y*65.),floor(time*13.))));q.x+=strip*glitch*.017*sin(time*29.);
float d=texture(depth_tex,q).r;float z=(.2*150.)/(150.1-(2.*d-1.)*149.9);float radius=clamp(abs(z-focus_distance)/max(z,.1)*8.,0.,6.);
vec3 c=texture(tex,q).rgb*.28;
for(int k=0;k<8;k++){float a=float(k)*.785398;c+=texture(tex,q+vec2(cos(a),sin(a))*pixel_size*radius).rgb*.09;}
c+=texture(bloom_tex,q).rgb*.22;
if(glitch>.01){c.r=mix(c.r,texture(tex,q+vec2(.005*glitch,0)).r,.6);c.b=mix(c.b,texture(tex,q-vec2(.005*glitch,0)).b,.6);}
c=pow(aces(c*exposure*tint),vec3(1./2.2));
float vignette=1.-.30*pow(length((uv-.5)*vec2(1.,1.1)),1.6);c*=vignette;c+=(hash(uv*vec2(1920,1080)+time)-.5)*.003;

vec4 over=texture(overlay_tex,vec2(uv.x,1.-uv.y));c=mix(c,over.rgb,over.a);c*=fade;frag=vec4(c,1);}
'''

class Renderer:
    def __init__(self,w=1920,h=1080):
        self.w,self.h=w,h;self.ctx=moderngl.create_standalone_context();c=self.ctx
        self.prog=c.program(vertex_shader=VERT,fragment_shader=FRAG);self.sp=c.program(vertex_shader=SVERT,fragment_shader='#version 330\nvoid main(){}')
        self.post=c.program(vertex_shader=QUAD,fragment_shader=POST);self.blur=c.program(vertex_shader=QUAD,fragment_shader=BLUR)
        q=c.buffer(np.array([[-1,-1],[1,-1],[-1,1],[1,1]],dtype='f4').tobytes());self.qa=c.simple_vertex_array(self.post,q,'in_vert');self.qb=c.simple_vertex_array(self.blur,q,'in_vert')
        self.tex=c.texture((w,h),3,dtype='f2');self.depthtex=c.depth_texture((w,h));self.depthtex.compare_func='';self.resolved=c.framebuffer([self.tex],self.depthtex);self.depth=c.depth_renderbuffer((w,h),samples=4);self.mscolor=c.renderbuffer((w,h),components=3,samples=4,dtype='f2');self.fbo=c.framebuffer([self.mscolor],self.depth)
        self.out=c.simple_framebuffer((w,h),components=3);self.shadow=c.depth_texture((2048,2048));self.shadow.compare_func='<=';self.shadow.repeat_x=False;self.shadow.repeat_y=False;self.sfbo=c.framebuffer(depth_attachment=self.shadow)
        self.bt=[c.texture((w//2,h//2),3,dtype='f2') for _ in range(2)];self.bf=[c.framebuffer([t]) for t in self.bt]
        for t in [self.tex,*self.bt]:t.filter=(moderngl.LINEAR,moderngl.LINEAR);t.repeat_x=False;t.repeat_y=False
        self.overlay=c.texture((w,h),4);self.overlay.write(bytes(w*h*4));self.meshes={}
    def mesh(self,key):
        if key not in self.meshes:
            c=self.ctx;b=c.buffer(mesh_data(key).tobytes());inst=c.buffer(reserve=80*4096)
            vao=c.vertex_array(self.prog,[(b,'3f 3f','in_pos','in_normal'),(inst,'4f 4f 4f 4f 4f /i','m0','m1','m2','m3','in_color')])
            sva=c.vertex_array(self.sp,[(b,'3f 12x','in_pos'),(inst,'4f 4f 4f 4f 16x /i','m0','m1','m2','m3')])
            self.meshes[key]=(inst,vao,sva)
        return self.meshes[key]
    def set_overlay(self,image):self.overlay.write(image.tobytes())
    def render(self,scene,eye,target,fov=42,time=0,fade=1,glitch=0,theme='cool',exposure=1):
        c=self.ctx
        if theme=='mono': key=(1.15,1.08,.97);amb=(.19,.20,.23);fog=(.008,.009,.010);bg=(.008,.009,.010)
        elif theme=='warm': key=(1.5,1.13,.7);amb=(.32,.4,.45);fog=(.09,.13,.15);bg=(.16,.23,.28)
        elif theme=='alarm':key=(1.3,.42,.28);amb=(.26,.32,.46);fog=(.05,.038,.072);bg=(.055,.035,.065)
        elif theme=='night':key=(.28,.48,.75);amb=(.06,.10,.21);fog=(.012,.023,.05);bg=(.015,.027,.055)
        else:key=(1.3,1.17,.98);amb=(.24,.39,.5);fog=(.025,.07,.095);bg=(.055,.12,.16)
        light=np.array((-9,16,10),dtype='f4');lv=ortho(-19,19,-19,19,.1,80)@look_at(light,(0,0,0))
        eye=np.asarray(eye,dtype='f4');vp=perspective(fov,self.w/self.h)@look_at(eye,target)
        batches=[]
        for kind,items in scene.items.items():
            if not items:continue
            ins,vao,sva=self.mesh(kind);data=np.asarray(items,dtype='f4').tobytes()
            if len(data)>ins.size:ins.orphan(len(data))
            ins.write(data);batches.append((vao,sva,len(items),kind=='glass'))
        c.enable(moderngl.DEPTH_TEST);c.disable(moderngl.CULL_FACE);self.sfbo.use();self.sfbo.clear(depth=1);c.viewport=(0,0,2048,2048);self.sp['light_vp'].write(lv.T.tobytes())
        for _,v,n,glass in batches:
            if not glass:v.render(instances=n)
        self.fbo.use();self.fbo.clear(*bg,1,depth=1);c.viewport=(0,0,self.w,self.h)
        p=self.prog;p['vp'].write(vp.T.tobytes());p['light_vp'].write(lv.T.tobytes());p['eye'].value=tuple(eye);p['light_dir'].value=tuple(normalize(light));p['key_color'].value=key;p['ambient'].value=amb;p['fog_color'].value=fog;p['fog_density'].value=.010
        self.shadow.use(0);p['shadow_map'].value=0
        for v,_,n,glass in batches:
            if not glass:v.render(instances=n)
        c.enable(moderngl.BLEND);c.blend_func=(moderngl.SRC_ALPHA,moderngl.ONE_MINUS_SRC_ALPHA)
        for v,_,n,glass in batches:
            if glass:v.render(instances=n)
        c.disable(moderngl.BLEND)
        c.copy_framebuffer(self.resolved,self.fbo)
        c.disable(moderngl.DEPTH_TEST);c.viewport=(0,0,self.w//2,self.h//2);self.blur['tex'].value=0
        for k in range(4):
            self.bf[k%2].use();(self.tex if k==0 else self.bt[(k-1)%2]).use(0);self.blur['direction'].value=(2/self.w,0) if k%2==0 else (0,2/self.h);self.blur['first_pass'].value=int(k==0);self.qb.render(moderngl.TRIANGLE_STRIP)
        self.out.use();c.viewport=(0,0,self.w,self.h);self.tex.use(0);self.bt[1].use(1);self.overlay.use(2);self.depthtex.use(3)
        p=self.post;p['tex'].value=0;p['bloom_tex'].value=1;p['overlay_tex'].value=2;p['depth_tex'].value=3;p['focus_distance'].value=float(np.linalg.norm(eye-np.asarray(target)));p['pixel_size'].value=(1/self.w,1/self.h);p['time'].value=time;p['fade'].value=fade;p['glitch'].value=glitch;p['tint'].value=(1,1,1);p['exposure'].value=exposure;self.qa.render(moderngl.TRIANGLE_STRIP)
        return self.out
