"""t02 (relay sample) · the hole that opened out of the box in s06 is this black hole.

The room's last picture (room_backdrop.png: s06 at 85.3, un-lensed, a view twice as wide) hangs behind the hole as a
backdrop at infinity: every ray that escapes looks it up where an unbent ray with its final direction would have
landed on the screen, so far from the hole the room is exactly where it was, and near it the room is wrapped into the
Einstein ring and its flipped second image — the same picture s06's lens equation ends on. From the cut the black breaks
open again where the box was and pushes the rest of the room out past the frame by 85.95, as the star comes in; the starry sky and everything after are t02 unchanged.
"""
import math, importlib.util
from pathlib import Path
from PIL import Image
HERE = Path(__file__).resolve().parent
T02 = HERE.parents[1] / 'tests' / 't02_blackhole'
_spec = importlib.util.spec_from_file_location('t02_orig', T02 / 'render.py')
M = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(M)

ZOOM = 2.                                    # the backdrop's field is this many screens wide (s06 CAPTURE u_zoomOut)
T_IN = 85.5
T_OUT = 85.95                                 # the room is gone past the frame

SRC = (T02 / 'scene.glsl').read_text(encoding='utf-8')
SRC = SRC.replace('out vec4 fragColor;', '''out vec4 fragColor;
uniform sampler2D u_room; uniform float u_roomA, u_zoom, u_push, u_soap2;
// the backdrop is a graded picture: back to scene light (the inverse of the display transform, vignette and all)
vec3 roomTex(vec2 q){
  vec3 x=pow(textureLod(u_room,q,0.).rgb,vec3(2.2));
  vec3 a=2.51-2.43*x, b=.03-.59*x, c=-.14*x;
  vec3 y=(-b+sqrt(max(b*b-4.*a*c,0.)))/(2.*a);
  vec2 d=q-.5; return y/1.05/(1.-.9*dot(d,d));
}''', 1)
SRC = SRC.replace('  if(fate<.5){\n', '''  if(fate<.5&&u_roomA>0.){                                       // the room, bent round the hole it came out of
    float z=dot(sd,fw);
    if(z>0.){
      vec2 pu=vec2(dot(sd,rt),dot(sd,up))/z/(2.*tan(u_fov*.5));
      vec2 q=vec2(pu.x*u_res.y/u_res.x/u_zoom+.5,pu.y/u_zoom+.5);
      // the black breaks open again where the box was and pushes the rest of the room out past the frame
      float rho=length(pu), an=atan(pu.y,pu.x);
      float rg=1.+u_soap2*(.2*(vn3(vec3(an*2.2,u_time*1.5,0.))-.5)+.1*(vn3(vec3(an*7.,u_time*3.,5.))-.5));
      float rim=(rho/rg-u_push)/(.03+.05*u_soap2);
      if(q.x>0.&&q.x<1.&&q.y>0.&&q.y<1.&&rim>0.){
        vec3 rc=roomTex(q);
        if(rim<1.){ float hh=rim*1.6+.6*vn3(vec3(an*4.,u_time*2.,9.)); vec3 film=.5+.5*cos(6.2832*(hh+vec3(0.,.33,.67)));
          rc=mix(rc,rc*.6+film*.55,(1.-rim)*(.2+.3*u_soap2)); }
        col+=rc*u_roomA;
      }
    }
  }
  if(fate<.5){
''', 1)
assert 'u_roomA>0.' in SRC
POST = dict(u_bloom=.45, u_ca=.008)
_IMG = {}


def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)


def params(t):
    p = M.params(t)
    x = clamp((t - T_IN) / (T_OUT - T_IN))
    p['u_push'] = 2.05 * (.35 * x + .65 * x * x)                # moving from the cut on, faster as it goes: the outer room
                                                                 # is past the frame by ~85.73, the flipped inner ring is
                                                                 # squeezed into the shadow by 85.95
    p['u_soap2'] = 1 - x
    p['u_roomA'] = 1. if t < T_OUT else 0.
    p['u_zoom'] = ZOOM
    if t >= T_IN: p.update(u_glow=.05, u_bright=.95, u_corona=.3)   # over the room, the star cannot fade up from black
    return p


def textures(t, w, h):
    if 'room' not in _IMG: _IMG['room'] = Image.open(HERE.parent / 'assets' / 'room_backdrop.png').convert('RGB')
    return {'u_room': _IMG['room']}
