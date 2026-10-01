"""Independent 3D-to-cel train / 2D foreground camera study.

Local meshes, depth-tested rasterization and a deliberately small ink palette.
No source film modules are imported. Time is evaluated directly, without a
simulation clock, so stills and encoded frames share exactly the same camera.
"""
from pathlib import Path
import argparse
import json
import math
import subprocess
import sys
import time

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE / '_vendor'))
import moderngl

START = 162.632
DURATION = 6.0
FPS = 60
PALETTE = [(0.075, .072, .070), (.24, .225, .20), (.69, .65, .57), (.89, .86, .79), (.60, .025, .04)]


def smooth(a, b, t):
    q = np.clip((t-a)/(b-a), 0., 1.)
    return q*q*(3.-2.*q)


def normalize(v):
    return np.asarray(v, dtype='f4') / np.linalg.norm(v)


def track(s):
    # Bend spacing is longer than a wagon: its two bogies can negotiate it.
    return np.array([12*math.sin(s/26)+4*math.sin(s/11), 0, s], dtype='f4')


def pose(s):
    f = normalize(track(s+1.5)-track(s-1.5))
    r = normalize(np.cross([0, 1, 0], f))
    m = np.eye(4, dtype='f4')
    m[:3, 0], m[:3, 1], m[:3, 2], m[:3, 3] = r, [0, 1, 0], f, track(s)
    return m


def model(base, pos, size):
    m = base.copy()
    m[:3, 3] = (base @ np.array([*pos, 1], dtype='f4'))[:3]
    m[:3, :3] = base[:3, :3] @ np.diag(size)
    return m


def view_matrix(eye, target):
    f = normalize(target-eye)
    r = normalize(np.cross(f, [0, 1, 0]))
    u = np.cross(r, f)
    v = np.eye(4, dtype='f4')
    v[:3, :3] = np.array([r, u, -f])
    v[:3, 3] = -v[:3, :3] @ eye
    return v


def projection(fov, aspect):
    f = 1/math.tan(math.radians(fov)/2)
    n, z = .15, 360.
    return np.array([[f/aspect, 0, 0, 0], [0, f, 0, 0], [0, 0, (z+n)/(n-z), 2*z*n/(n-z)], [0, 0, -1, 0]], dtype='f4')


def cube():
    faces = [([1, 0, 0], [[.5, -.5, -.5], [.5, .5, -.5], [.5, .5, .5], [.5, -.5, .5]]),
             ([-1, 0, 0], [[-.5, -.5, .5], [-.5, .5, .5], [-.5, .5, -.5], [-.5, -.5, -.5]]),
             ([0, 1, 0], [[-.5, .5, -.5], [-.5, .5, .5], [.5, .5, .5], [.5, .5, -.5]]),
             ([0, -1, 0], [[-.5, -.5, .5], [-.5, -.5, -.5], [.5, -.5, -.5], [.5, -.5, .5]]),
             ([0, 0, 1], [[.5, -.5, .5], [.5, .5, .5], [-.5, .5, .5], [-.5, -.5, .5]]),
             ([0, 0, -1], [[-.5, -.5, -.5], [-.5, .5, -.5], [.5, .5, -.5], [.5, -.5, -.5]])]
    out = []
    for n, points in faces:
        for i in [0, 1, 2, 0, 2, 3]:
            out.append([*points[i], *n])
    return np.array(out, dtype='f4')


def cylinder(axis='y', segments=24):
    out = []
    def cv(v):
        if axis == 'x': return [v[1], v[0], v[2]]
        if axis == 'z': return [v[0], v[2], v[1]]
        return v
    for j in range(segments):
        a, b = j*math.tau/segments, (j+1)*math.tau/segments
        p = [math.cos(a)*.5, math.sin(a)*.5]
        q = [math.cos(b)*.5, math.sin(b)*.5]
        n = cv([math.cos((a+b)/2), 0, math.sin((a+b)/2)])
        pts = [[p[0], -.5, p[1]], [p[0], .5, p[1]], [q[0], .5, q[1]], [q[0], -.5, q[1]]]
        for i in [0, 1, 2, 0, 2, 3]: out.append([*cv(pts[i]), *n])
        for sign in [-1, 1]:
            for point in [[0, sign*.5, 0], [p[0], sign*.5, p[1]], [q[0], sign*.5, q[1]]]:
                out.append([*cv(point), *cv([0, sign, 0])])
    return np.array(out, dtype='f4')


def sphere():
    out = []
    def p(a, b): return [math.sin(a)*math.cos(b)*.5, math.cos(a)*.5, math.sin(a)*math.sin(b)*.5]
    for i in range(10):
        for j in range(16):
            a, c, b, d = i*math.pi/10, (i+1)*math.pi/10, j*math.tau/16, (j+1)*math.tau/16
            points = [p(a, b), p(c, b), p(c, d), p(a, d)]
            for k in [0, 1, 2, 0, 2, 3]: out.append([*points[k], *normalize(points[k])])
    return np.array(out, dtype='f4')


def card_image():
    im = Image.new('RGB', (1600, 704), (226, 219, 199))
    d = ImageDraw.Draw(im)
    ink = (23, 22, 21)
    bold = lambda n: ImageFont.truetype('C:/Windows/Fonts/courbd.ttf', n)
    font = lambda n: ImageFont.truetype('C:/Windows/Fonts/cour.ttf', n)
    d.rectangle((14, 14, 1585, 689), outline=ink, width=3)
    d.rectangle((24, 24, 1575, 679), outline=ink, width=1)
    d.text((54, 36), 'VOLKSZÄHLUNG 1939', font=bold(45), fill=ink)
    d.text((1540, 43), '17. MAI 1939', font=font(24), fill=ink, anchor='ra')
    d.line((40, 95, 1560, 95), fill=ink, width=2)
    groups = ['Geburtsjahr', 'Geschlecht', 'Familienstand', 'Beruf', 'Religion', 'Muttersprache', 'Abstammung', 'Gemeinde']
    for g, label in enumerate(groups):
        x = 44 + g*189
        d.text((x+94, 118), label, font=bold(15), fill=ink, anchor='mm')
        if g: d.line((x, 95, x, 146), fill=ink, width=1)
    d.line((40, 146, 1560, 146), fill=ink, width=2)
    for row in range(10):
        for col in range(80):
            x, y = 53+col*18.9, 174+row*42
            d.text((x, y), str(row), font=font(15), fill=(116, 110, 99), anchor='mm')
            if (col*11+17)%10 == row:
                d.rectangle((x-3, y-10, x+3, y+10), fill=ink)
    # The same selected field stays attached to this one wagon.
    x, y = 53+64*18.9, 174+1*42
    d.rectangle((x-6, y-13, x+6, y+13), fill=(162, 15, 28))
    d.text((48, 641), 'STATISTISCHE KARTE', font=bold(18), fill=ink)
    d.text((1543, 641), 'NR. 0062', font=font(18), fill=ink, anchor='ra')
    for col in range(80): d.text((53+col*18.9, 672), str(col+1), font=font(10), fill=ink, anchor='mm')
    im.save(HERE/'card.png')
    return im


def foreground_image():
    # An authored 2D wall/factory silhouette, with no bevels or plastic highlights.
    im = Image.new('RGBA', (2560, 1440), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ink, face, edge = (20, 19, 18, 255), (52, 48, 42, 255), (104, 95, 79, 255)
    # Sawtooth roof and chimneys deliberately readable in silhouette.
    roof = [(0, 900), (0, 705)]
    for x in range(0, 2560, 320): roof += [(x+245, 490), (x+245, 705), (x+320, 705)]
    roof += [(2560, 1440), (0, 1440)]
    d.polygon(roof, fill=ink)
    for x, top in [(370, 130), (1270, 15), (1970, 180)]:
        d.rectangle((x, top, x+112, 750), fill=ink)
        d.rectangle((x-14, top-10, x+126, top+22), fill=ink)
        d.rectangle((x+17, top+32, x+23, 700), fill=edge)
    for x in range(70, 2550, 320):
        for y in [754, 924]:
            d.rectangle((x, y, x+190, y+84), fill=(143, 130, 108, 255))
            for w in [x+63, x+126]: d.line((w, y, w, y+84), fill=ink, width=9)
            d.line((x, y+42, x+190, y+42), fill=ink, width=8)
    # Wall is in front of the lower facade; coarse lines resist video aliasing.
    d.rectangle((0, 1075, 2560, 1440), fill=face)
    d.rectangle((0, 1056, 2560, 1084), fill=ink)
    for y in range(1100, 1440, 63):
        d.line((0, y, 2560, y), fill=ink, width=3)
        for x in range(-100+(y//63%2)*100, 2560, 210): d.line((x, y, x, y+63), fill=ink, width=3)
    for x in range(0, 2560, 640):
        d.rectangle((x, 1000, x+68, 1440), fill=ink)
        d.rectangle((x-10, 985, x+78, 1010), fill=ink)
    im = im.filter(ImageFilter.GaussianBlur(2.5))
    im.save(HERE/'foreground.png')
    return im


VS = '''#version 330
in vec3 in_pos; in vec3 in_normal;
uniform mat4 mvp, model;
out vec3 normal; out vec3 world; out vec2 uv;
void main(){vec4 w=model*vec4(in_pos,1); world=w.xyz; normal=normalize(mat3(transpose(inverse(model)))*in_normal);
uv=vec2(.5-in_pos.z,.5-in_pos.y); gl_Position=mvp*vec4(in_pos,1);}
'''
FS = '''#version 330
in vec3 normal; in vec3 world; in vec2 uv;
uniform vec3 color; uniform vec3 eye;
uniform sampler2D card; uniform int kind;
layout(location=0) out vec4 frag;
void main(){
 vec3 n=normalize(normal); float l=dot(n,normalize(vec3(-.6,1.,.5)));
 float shade=l>.55 ? 1.0 : (l>-.15 ? .74 : .48);
 vec3 c=color*shade;
 float facing=abs(dot(n,normalize(eye-world)));
 if(kind==1) c=texture(card,uv).rgb;
 if(kind==2) c=color;
 if(kind==0 && facing<.13) c=vec3(.075,.072,.070);
 // Fog is an ink-to-paper distance blend, not bloom or an exposure transform.
 float fog=smoothstep(90.,220.,length(eye-world));
 c=mix(c,vec3(.82,.79,.72),fog*.65);
 frag=vec4(c,1);
}
'''
POST_VS = '''#version 330
in vec2 in_pos; out vec2 uv;
void main(){uv=(in_pos+1)*.5; gl_Position=vec4(in_pos,0,1);}
'''
POST_FS = '''#version 330
in vec2 uv; out vec4 frag;
uniform sampler2D scene, depthtex, foreground;
uniform vec2 resolution; uniform float time;
float ss(float a,float b,float x){return smoothstep(a,b,x);}
vec4 fg(vec2 p,float blur){
 vec4 s=vec4(0); float w=0;
 for(int j=-3;j<=3;j++) for(int i=-3;i<=3;i++){
  vec2 q=p+vec2(i*1.2,j)*(.30*blur)/resolution;
  float k=exp(-float(i*i+j*j)*.35);
  vec4 c= (q.x<0||q.x>1||q.y<0||q.y>1) ? vec4(0) : texture(foreground,q);
  s+=vec4(c.rgb*c.a,c.a)*k; w+=k;
 }
 s/=w; if(s.a>.001)s.rgb/=s.a; return s;
}
void main(){
 vec3 c=texture(scene,uv).rgb;
 float z=texture(depthtex,uv).r, edge=0;
 vec2 dx=1./resolution;
 for(int j=-1;j<=1;j++)for(int i=-1;i<=1;i++){
  float d=texture(depthtex,uv+vec2(i,j)*dx).r;
  edge=max(edge,abs(z-d));
 }
 // Only silhouette discontinuities receive a narrow line; no giant black rim.
 if(edge>.0011 && z<.9999)c=mix(c,vec3(.075,.072,.07),.75);
 float enter=ss(4.05,5.85,time);
 float left=1.08-enter*1.30;
 vec2 p=vec2((uv.x-left)/1.55,(1.-uv.y-.02)/1.02);
 // The wall is a near layer: more displacement and more defocus than the train.
 vec4 layer=fg(p,3.+enter*4.);
 c=mix(c,layer.rgb,layer.a);
 // A much nearer gate post passes across the lens after the facade arrives.
 float postx=mix(1.25,-.42,ss(5.05,6.25,time));
 float width=.13;
 float mask=ss(postx-width-.012,postx-width+.012,uv.x)*(1.-ss(postx+width-.012,postx+width+.012,uv.x));
 c=mix(c,vec3(.075,.072,.07),mask*ss(5.05,5.15,time));
 // Fine paper grain is anchored to the screen; small enough to preserve ink.
 float grain=fract(sin(dot(floor(uv*resolution),vec2(12.9898,78.233)))*43758.5453)-.5;
 c+=grain*.009;
 frag=vec4(c,1);
}
'''


class Renderer:
    def __init__(self, width=1920, height=1080):
        self.w, self.h = width, height
        self.ctx = moderngl.create_standalone_context(require=330)
        self.prog = self.ctx.program(vertex_shader=VS, fragment_shader=FS)
        self.post = self.ctx.program(vertex_shader=POST_VS, fragment_shader=POST_FS)
        self.meshes = {}
        for name, vertices in [('box', cube()), ('cy', cylinder()), ('cx', cylinder('x')), ('cz', cylinder('z')), ('sphere', sphere())]:
            buf = self.ctx.buffer(vertices.tobytes())
            self.meshes[name] = self.ctx.vertex_array(self.prog, [(buf, '3f 3f', 'in_pos', 'in_normal')])
        self.color = self.ctx.texture((width, height), 4)
        self.depth = self.ctx.depth_texture((width, height))
        self.depth.compare_func = ''
        self.fbo = self.ctx.framebuffer([self.color], self.depth)
        self.msaa = self.ctx.framebuffer([self.ctx.renderbuffer((width,height), components=4, samples=4)], self.ctx.depth_renderbuffer((width,height), samples=4))
        self.final = self.ctx.simple_framebuffer((width, height), components=3)
        self.card = self.ctx.texture((1600, 704), 3, card_image().tobytes())
        fgimage = foreground_image()
        self.fg = self.ctx.texture(fgimage.size, 4, fgimage.tobytes())
        for tex in [self.card, self.fg]: tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self.card.use(3); self.prog['card'] = 3
        self.quad = self.ctx.vertex_array(self.post, [(self.ctx.buffer(np.array([-1,-1, 1,-1, -1,1, 1,1], dtype='f4').tobytes()), '2f', 'in_pos')])
        self.post['scene'], self.post['depthtex'], self.post['foreground'] = 0, 1, 2
        self.post['resolution'] = (width, height)

    def draw(self, name, mat, color, kind=0):
        self.prog['model'].write(mat.T.astype('f4').tobytes())
        self.prog['mvp'].write((self.vp@mat).T.astype('f4').tobytes())
        self.prog['color'] = tuple(color)
        self.prog['kind'] = kind
        self.meshes[name].render()

    def part(self, base, name, pos, size, col, kind=0):
        self.draw(name, model(base, pos, size), PALETTE[col], kind)

    def wheels(self, base, zs, radius=.62, rod=False, t=0):
        for z in zs:
            for x in [-1.24, 1.24]:
                self.part(base, 'cx', (x, radius+.16, z), (.22, radius*2, radius*2), 0)
                self.part(base, 'cx', (x*1.105, radius+.16, z), (.025, radius*1.45, radius*1.45), 2)
                self.part(base, 'cx', (x*1.12, radius+.16, z), (.04, .25, .25), 0)
                for a in range(0, 6):
                    ang = a*math.tau/6-t*7/radius
                    spoke = model(base, (x*1.118, radius+.16, z), (1,1,1))
                    rot = np.eye(4, dtype='f4')
                    rot[1:3,1:3] = [[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]]
                    spoke = spoke@rot
                    self.part(spoke, 'box', (0, 0, radius*.24), (.035, .055, radius*.49), 0)
        if rod:
            for x in [-1.41, 1.41]:
                self.part(base, 'box', (x, radius+.16+math.sin(t*6)*.27, sum(zs)/len(zs)+math.cos(t*6)*.27), (.08, .12, max(zs)-min(zs)+.18), 3)

    def wagon(self, base, index, t):
        self.part(base, 'box', (0, 1.35, 0), (2.8, .30, 7.6), 0)
        self.part(base, 'box', (0, 2.72, 0), (2.55, 2.5, 7.1), 2)
        self.part(base, 'box', (0, 3.97, 0), (2.85, .12, 7.55), 0)
        # Curved roof: cylinder sits on the substantial box body, with a thin cap.
        self.part(base, 'cz', (0, 3.92, 0), (2.78, .68, 7.48), 0)
        for x in [-1.286, 1.286]:
            self.part(base, 'box', (x, 2.72, 0), (.032, 2.36, 1.28), 1)
            for z in [-2.75, -2.1, 2.1, 2.75]:
                self.part(base, 'box', (x, 3.27, z), (.034, .64, .43), 0)
            for z in [-3.36, -1.25, 1.25, 3.36]:
                self.part(base, 'box', (x*1.009, 2.7, z), (.038, 2.45, .045), 0)
        self.wheels(base, [-2.7, 2.7], .54, t=t)
        for z in [-4.05, 4.05]: self.part(base, 'box', (0, 1.1, z), (.18, .18, .7), 0)
        # Card lives on the first carriage immediately behind the engine.
        if index == 0:
            self.part(base, 'box', (1.32, 2.76, .0), (.048, 2.15, 4.88), 0)
            self.part(base, 'box', (1.352, 2.76, .0), (.008, 2.04, 4.64), 3, 1)
        else:
            self.part(base, 'box', (1.31, 2.6, .0), (.022, 1.49, 3.42), 0)
            self.part(base, 'box', (1.329, 2.6, .0), (.012, 1.40, 3.22), 3, 1)

    def locomotive(self, base, t):
        self.part(base, 'box', (0, 1.25, 0), (2.9, .35, 8.0), 0)
        self.part(base, 'cz', (0, 2.48, 1), (2.12, 2.12, 4.9), 1)
        for z in [-.9, .6, 2.3]: self.part(base, 'cz', (0, 2.48, z), (2.2, 2.2, .12), 0)
        self.part(base, 'cz', (0, 2.48, 3.47), (2.14, 2.14, .18), 0)
        self.part(base, 'cz', (0, 2.48, 3.58), (1.65, 1.65, .03), 1)
        self.part(base, 'cz', (0, 3.1, 3.7), (.4, .4, .22), 3)
        self.part(base, 'cy', (0, 4.0, 2.05), (.64, 1.7, .64), 0)
        self.part(base, 'cy', (0, 4.81, 2.05), (.92, .24, .92), 0)
        self.part(base, 'cy', (0, 3.65, -.3), (.67, .55, .67), 2)
        self.part(base, 'box', (0, 2.73, -2.82), (2.77, 2.56, 2.1), 1)
        self.part(base, 'box', (0, 4.1, -2.82), (3.12, .18, 2.42), 0)
        for x in [-1.40, 1.40]: self.part(base, 'box', (x, 3.2, -2.7), (.03, 1.0, 1.1), 3)
        self.part(base, 'box', (0, 1.88, -4.36), (2.45, 1.40, 1.25), 0)
        self.wheels(base, [-1.15, .2, 1.55], .78, True, t)
        self.wheels(base, [-3.05, 3.05], .42, t=t)
        # Near-black coals; steam is a handful of coherent, faceted light forms.
        for i in range(7):
            phase = (t*.43+i/7)%1
            z = 2.05-phase*8.7
            y = 5.02+phase*4.6
            size = .48+phase*1.65
            self.part(base, 'sphere', (.25*math.sin(i*2+phase*4), y, z), (size, size*.9, size*1.4), 3, 2)

    def camera(self, t, head):
        first = pose(head-9.1)
        # Camera starts on the card side and a little toward the locomotive.
        close_eye = (first@np.array([12.0, 3.8, 2.1, 1]))[:3]
        close_target = (first@np.array([.6, 2.85, 3.8, 1]))[:3]
        front = pose(head+3.)
        wide_eye = (front@np.array([24., 31., 23., 1]))[:3]
        # The raised camera remains at the FRONT, looking back down the train.
        wide_target = track(head-28.)+np.array([0, 1.8, 0])
        lift = smooth(1.05, 3.50, t)
        eye = close_eye*(1-lift)+wide_eye*lift
        target = close_target*(1-lift)+wide_target*lift
        # A gentle descent connects the aerial reveal to the near industrial wall.
        near = smooth(4.10, 6., t)
        eye += np.array([-3.2, -6.0, 0])*near
        target += np.array([0, 2.5, 10.])*near
        return eye.astype('f4'), target.astype('f4'), 51.+lift*5.

    def frame(self, t):
        head = t*7.
        eye, target, fov = self.camera(t, head)
        self.vp = projection(fov, self.w/self.h)@view_matrix(eye, target)
        self.prog['eye'] = tuple(eye)
        self.msaa.use(); self.ctx.enable(moderngl.DEPTH_TEST)
        self.msaa.clear(.87, .84, .77, 1, depth=1)
        identity = np.eye(4, dtype='f4')
        self.part(identity, 'box', (0, -.17, -50), (650, .20, 650), 3, 2)
        # Rails and sleepers are in the same curved coordinate system as bogies.
        for s in np.arange(head-170, head+45, 1.7):
            base = pose(float(s))
            self.part(base, 'box', (0, .025, 0), (3.35, .085, .20), 2)
        for s in np.arange(head-170, head+45, 1.0):
            base = pose(float(s))
            for x in [-.98, .98]: self.part(base, 'box', (x, .13, 0), (.10, .14, 1.24), 0)
        # Sparse trackside poles cross the close view and establish real travel.
        # Fixed world positions avoid the scenery being attached to the train.
        for s in range(-180, 80, 24):
            base = pose(float(s))
            self.part(base, 'box', (-5.2, 2.4, 0), (.15, 4.8, .15), 1)
            self.part(base, 'box', (-5.2, 4.65, 0), (1.9, .12, .12), 1)
            for x in [-5.9, -4.5]: self.part(base, 'cy', (x,4.8,0), (.16,.2,.16), 0)
        for i in reversed(range(18)):
            self.wagon(pose(head-9.1-i*8.2), i, t)
        self.locomotive(pose(head), t)
        self.ctx.copy_framebuffer(self.fbo, self.msaa)
        self.ctx.disable(moderngl.DEPTH_TEST)
        self.final.use(); self.color.use(0); self.depth.use(1); self.fg.use(2)
        self.post['time'] = t
        self.quad.render(moderngl.TRIANGLE_STRIP)
        return Image.frombytes('RGB', (self.w, self.h), self.final.read(components=3, alignment=1)).transpose(Image.Transpose.FLIP_TOP_BOTTOM)


def contact(images, name):
    sheet = Image.new('RGB', (1920, math.ceil(len(images)/3)*392), (20, 19, 18))
    d = ImageDraw.Draw(sheet)
    font = ImageFont.truetype('C:/Windows/Fonts/cour.ttf', 23)
    for i, (t, im) in enumerate(images):
        x, y = i%3*640, i//3*392
        sheet.paste(im.resize((640,360), Image.Resampling.LANCZOS), (x,y))
        d.text((x+12,y+363), f'{t:04.2f}s', font=font, fill=(225,218,198))
    sheet.save(HERE/name, quality=95)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--stills', action='store_true')
    ap.add_argument('--width', type=int, default=1920); ap.add_argument('--height', type=int, default=1080)
    args = ap.parse_args()
    r = Renderer(args.width, args.height)
    print('Renderer:', r.ctx.info['GL_RENDERER'], flush=True)
    if args.stills:
        images = []
        for t in [.2, .8, 1.3, 2., 2.7, 3.5, 4.2, 5., 5.8]:
            im = r.frame(t); im.save(HERE/f'still_{t:04.1f}.jpg', quality=95); images.append((t,im))
        contact(images, 'design_sheet.jpg')
        return
    out = HERE/'train_cel_study_1080p60.mp4'
    ff = ROOT/'tools/ffmpeg.exe'
    song = next(ROOT.glob('*.mp3'))
    cmd = [str(ff), '-y', '-hide_banner', '-loglevel', 'warning', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{args.width}x{args.height}', '-r', str(FPS), '-i', 'pipe:0', '-ss', str(START), '-i', str(song), '-map', '0:v:0', '-map', '1:a:0', '-t', str(DURATION), '-c:v', 'h264_nvenc', '-preset', 'p5', '-rc', 'vbr', '-cq', '18', '-b:v', '18M', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '320k', '-movflags', '+faststart', str(out)]
    clock = time.perf_counter()
    with open(HERE/'encode.log', 'w', encoding='utf-8') as log:
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=log, stderr=log)
        for frame in range(round(DURATION*FPS)):
            p.stdin.write(r.frame(frame/FPS).tobytes())
            if frame%30 == 0: print(f'{frame}/{round(DURATION*FPS)} frames, {time.perf_counter()-clock:.1f}s', flush=True)
        p.stdin.close()
        if p.wait(): raise RuntimeError('Encoding failed: see encode.log')
    manifest = {'source_audio': song.name, 'source_start': START, 'duration': DURATION, 'fps': FPS, 'frames': round(DURATION*FPS), 'resolution': [args.width,args.height], 'renderer': r.ctx.info['GL_RENDERER'], 'render_seconds': time.perf_counter()-clock, 'camera': {'close': [0,1.05], 'lift_and_look_back': [1.05,3.5], 'long_train': [3.5,4.1], 'foreground_factory': [4.1,6.0]}}
    (HERE/'render_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps(manifest), flush=True)


if __name__ == '__main__': main()
