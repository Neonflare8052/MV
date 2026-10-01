"""Offscreen shader renderer: scene shader -> HDR accumulation (motion blur subframes) -> bloom -> grade."""
from pathlib import Path
import subprocess
import numpy as np
import moderngl

ROOT = Path(__file__).resolve().parents[2]
FFMPEG = ROOT / 'tools' / 'ffmpeg.exe'
SONG = next(ROOT.glob('*.mp3'))

VERT = """#version 330
in vec2 in_pos; out vec2 v_uv;
void main(){ v_uv = in_pos*0.5+0.5; gl_Position = vec4(in_pos,0.,1.); }"""

BRIGHT = """#version 330
uniform sampler2D src; in vec2 v_uv; out vec4 o;
void main(){ vec3 c = texture(src,v_uv).rgb; float l = max(max(c.r,c.g),c.b);
  float k = clamp((l-0.8)/0.6,0.,1.); o = vec4(c*k*k,1.); }"""

BLUR = """#version 330
uniform sampler2D src; uniform vec2 dir; in vec2 v_uv; out vec4 o;
void main(){ vec2 px = dir/vec2(textureSize(src,0));
  const float w[5] = float[5](0.227027,0.1945946,0.1216216,0.054054,0.016216);
  vec3 c = texture(src,v_uv).rgb*w[0];
  for(int i=1;i<5;i++){ c += texture(src,v_uv+px*float(i)*1.5).rgb*w[i]; c += texture(src,v_uv-px*float(i)*1.5).rgb*w[i]; }
  o = vec4(c,1.); }"""

FINAL = """#version 330
uniform sampler2D hdr; uniform sampler2D b0; uniform sampler2D b1; uniform sampler2D b2; uniform sampler2D b3;
uniform float u_time; uniform float u_bloom; uniform float u_grain; uniform float u_ca;
uniform float u_sat; uniform float u_gain; uniform float u_pinch; uniform float u_pdot;
in vec2 v_uv; out vec4 o;
vec3 aces(vec3 x){ return clamp((x*(2.51*x+0.03))/(x*(2.43*x+0.59)+0.14),0.,1.); }
float h(vec2 p){ vec3 p3=fract(vec3(p.xyx)*.1031); p3+=dot(p3,p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }
void main(){
  vec2 suv = v_uv;
  vec2 res = vec2(textureSize(hdr,0)); float asp = res.x/res.y;
  float keep = 1.;
  if(u_pinch > 0.){                       // the whole picture swallowed by a point: a non-linear pinch with a twist
    float x = u_pinch;
    vec2 v = (v_uv-.5)*vec2(asp,1.);
    float r = length(v), th = atan(v.y,v.x);
    float rs = min(r/pow(max(1.-x,1e-3),.55)*exp(min(7.5*x*x*r*(1.+2.*r),8.)),40.);
    float ths = th+2.4*x*x*exp(-r*6.);
    suv = vec2(cos(ths),sin(ths))*rs/vec2(asp,1.)+.5;
    keep = step(0.,suv.x)*step(suv.x,1.)*step(0.,suv.y)*step(suv.y,1.)*(1.+1.5*x*exp(-r*25.))*(1.-.5*x*smoothstep(0.,.25,r));
  }
  vec2 d = suv-0.5; float r2 = dot(d,d);
  vec2 off = d*u_ca*r2;
  vec3 c = vec3(texture(hdr,suv-off).r, texture(hdr,suv).g, texture(hdr,suv+off).b);
  vec3 bl = texture(b0,suv).rgb*0.5 + texture(b1,suv).rgb*0.7 + texture(b2,suv).rgb*0.9 + texture(b3,suv).rgb*1.1;
  c += bl*u_bloom;
  c *= keep*u_gain;
  c = mix(vec3(dot(c,vec3(.3,.55,.15))), c, u_sat);
  if(u_pdot > 0.){ float dd = length((v_uv-.5)*vec2(asp,1.)); c += vec3(1.,.97,.9)*u_pdot*(exp(-dd/.0035)*2.+exp(-dd/.03)*.25); }
  c *= 1.0 - 0.9*r2;                       // vignette
  c = aces(c*1.05);
  c = pow(c, vec3(1./2.2));
  vec2 gp = gl_FragCoord.xy + fract(u_time*7.13)*vec2(311.,173.);
  float g = (h(gp)+h(gp+17.3)-1.0);
  c += g*u_grain*(0.6+0.4*(1.-dot(c,vec3(.333))));
  o = vec4(clamp(c,0.,1.),1.);
}"""


class Renderer:
    def __init__(self, w, h, frag_src, subframes=4, shutter=0.5, fps=60):
        self.w, self.h, self.sub, self.shutter, self.fps = w, h, subframes, shutter, fps
        self.ctx = moderngl.create_standalone_context(require=330)
        quad = self.ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], 'f4').tobytes())
        mk = lambda fs: self.ctx.program(vertex_shader=VERT, fragment_shader=fs)
        self._mk, self._quad = mk, quad
        self.bright, self.blur, self.final = mk(BRIGHT), mk(BLUR), mk(FINAL)
        self.vao = {p: self.ctx.vertex_array(p, [(quad, '2f', 'in_pos')]) for p in (self.bright, self.blur, self.final)}
        self.scenes = {}
        self.use('main', frag_src)
        tex = lambda W, H: self.ctx.texture((W, H), 4, dtype='f4')
        self.acc = tex(w, h); self.acc_fbo = self.ctx.framebuffer([self.acc])
        self.levels = []
        for k in range(1, 5):
            W, H = max(1, w >> k), max(1, h >> k)
            a, b = tex(W, H), tex(W, H)
            for t in (a, b):
                t.filter = (moderngl.LINEAR, moderngl.LINEAR); t.repeat_x = t.repeat_y = False
            self.levels.append((a, b, self.ctx.framebuffer([a]), self.ctx.framebuffer([b])))
        self.acc.filter = (moderngl.LINEAR, moderngl.LINEAR); self.acc.repeat_x = self.acc.repeat_y = False
        self.out = self.ctx.texture((w, h), 3); self.out_fbo = self.ctx.framebuffer([self.out])
        self.post = dict(u_bloom=0.6, u_grain=0.035, u_ca=0.012, u_sat=1., u_gain=1., u_pinch=0., u_pdot=0.)

    def use(self, name, frag_src=None):
        """Select (compiling on first use) the scene shader for a shot; post-processing is shared."""
        if name not in self.scenes:
            prog = self._mk(frag_src)
            self.vao[prog] = self.ctx.vertex_array(prog, [(self._quad, '2f', 'in_pos')])
            self.scenes[name] = prog
        self.scene = self.scenes[name]

    def _set(self, prog, params):
        for k, v in params.items():
            if k in prog:
                prog[k].value = v

    def texture(self, name, img, unit):
        """Upload a PIL RGBA image (top-down) as sampler `name`, sampled with gl_FragCoord/u_res."""
        from PIL import Image
        cache = self.__dict__.setdefault('_src', {})
        if cache.get(name) is img:                       # unchanged image: just bind it
            self._tex[name].use(unit)
            if name in self.scene: self.scene[name].value = unit
            return
        cache[name] = img
        img = img.convert('RGBA').transpose(Image.FLIP_TOP_BOTTOM)
        tex = getattr(self, '_tex', {}).get(name)
        if tex is None or tex.size != img.size:
            tex = self.ctx.texture(img.size, 4); tex.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
            tex.anisotropy = 8.0
            self._tex = {**getattr(self, '_tex', {}), name: tex}
        tex.write(img.tobytes()); tex.build_mipmaps(); tex.use(unit)
        if name in self.scene:
            self.scene[name].value = unit

    def sprite_pass(self, name, vs, fs, data):
        """Instanced point sprites drawn additively after the scene pass (data: float32 array, n x 8 per instance)."""
        cache = self.__dict__.setdefault('_spr', {})
        if name not in cache:
            prog = self.ctx.program(vertex_shader=vs, fragment_shader=fs)
            quad = self.ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], 'f4').tobytes())
            inst = self.ctx.buffer(np.ascontiguousarray(data, 'f4').tobytes())
            attributes=(inst, '4f 4f 4f 4f/i', 'in_a', 'in_b', 'in_c', 'in_d') if data.shape[1]==16 else (inst, '4f 4f/i', 'in_a', 'in_b')
            vao = self.ctx.vertex_array(prog, [(quad, '2f', 'in_corner'), attributes])
            cache[name] = (prog, vao, len(data))
        return cache[name]

    def frame(self, t, params_fn, textures_fn=None, post=None, sprites=None):
        if post is not None:
            self.post = dict(dict(u_bloom=0.6, u_grain=0.035, u_ca=0.012, u_sat=1., u_gain=1., u_pinch=0., u_pdot=0.), **post)
        if textures_fn:
            for unit, (name, img) in enumerate(textures_fn(t).items(), start=8):
                self.texture(name, img, unit)
        self.acc_fbo.use(); self.acc_fbo.clear(0, 0, 0, 0)
        self.ctx.enable(moderngl.BLEND); self.ctx.blend_func = moderngl.ONE, moderngl.ONE
        for i in range(self.sub):
            ts = t + ((i + 0.5) / self.sub - 0.5) * self.shutter / self.fps
            p = dict(params_fn(ts)); p['u_time'] = ts; p['u_res'] = (float(self.w), float(self.h)); p['u_weight'] = 1.0 / self.sub
            self._set(self.scene, p); self.vao[self.scene].render(moderngl.TRIANGLE_STRIP)
            if sprites:
                prog, vao, n = self.sprite_pass(*sprites)
                self._set(prog, p); vao.render(moderngl.TRIANGLE_STRIP, instances=n)
        self.ctx.disable(moderngl.BLEND)
        src = self.acc
        for k, (a, b, fa, fb) in enumerate(self.levels):
            if k == 0:
                fa.use(); src.use(0); self.bright['src'] = 0
                self.vao[self.bright].render(moderngl.TRIANGLE_STRIP)
            else:
                self._blit(src, fa)
            fb.use(); a.use(0); self.blur['src'] = 0; self.blur['dir'] = (1.0, 0.0); self.vao[self.blur].render(moderngl.TRIANGLE_STRIP)
            fa.use(); b.use(0); self.blur['dir'] = (0.0, 1.0); self.vao[self.blur].render(moderngl.TRIANGLE_STRIP)
            src = a
        self.out_fbo.use(); self.acc.use(0)
        for k, (a, *_rest) in enumerate(self.levels):
            a.use(k + 1)
        self.final['hdr'] = 0
        for k in range(4):
            self.final[f'b{k}'] = k + 1
        self._set(self.final, dict(self.post, u_time=t))
        self.vao[self.final].render(moderngl.TRIANGLE_STRIP)
        return self.out_fbo.read(components=3)

    def _blit(self, src, fbo):
        # downsample with linear filtering: blur program with zero offset is a plain copy
        fbo.use(); src.use(0); self.blur['src'] = 0; self.blur['dir'] = (0.0, 0.0)
        self.vao[self.blur].render(moderngl.TRIANGLE_STRIP)


def encode(path, w, h, fps, start, dur, frames, audio=True, cq=19):
    cmd = [str(FFMPEG), '-y', '-hide_banner', '-loglevel', 'error', '-f', 'rawvideo', '-pixel_format', 'rgb24',
           '-video_size', f'{w}x{h}', '-framerate', str(fps), '-i', 'pipe:0']
    if audio:
        cmd += ['-ss', f'{start:.3f}', '-t', f'{dur:.3f}', '-i', str(SONG), '-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '320k']
    cmd += ['-vf', 'vflip,format=yuv420p', '-c:v', 'h264_nvenc', '-preset', 'p5', '-rc', 'vbr', '-cq', str(cq),
            '-b:v', '30M', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
            '-movflags', '+faststart', str(path)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in frames:
        proc.stdin.write(f)
    proc.stdin.close()
    if proc.wait():
        raise RuntimeError('ffmpeg failed')


def save_png(data, w, h, path):
    from PIL import Image
    Image.frombytes('RGB', (w, h), data).transpose(Image.FLIP_TOP_BOTTOM).save(path)
