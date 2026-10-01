"""s14e · 2:46.016–2:52.95  the envelope among Turing's papers; the seal; the letter.  (draft)
A detail view: face-on, flat, on the night sheet.  Cut in on "Then I can".

2:46.016 Then I can           the envelope alone, the red point on it.
2:46.47 … 2:48.33 be your only
                              his papers fall round it, one a beat, in order of their years: 1932 Nature of Spirit;
                              1936 On Computable Numbers (title, the first machine's table, the verdicts "u" and "s" that
                              cannot be); 1950 Computing Machinery and Intelligence (the question, the specimen answers,
                              Lady Lovelace's objection).  The envelope stays on top of them all.
2:48.911 EXECUTION            the red point is pressed into wax: the gapped ring, its gap down.
2:49.824 If I can have you back
                              the wax cracks; the flap lifts; the letter comes out, the envelope goes; the letter unfolds:
                              Turing to his mother, 16 February 1930.
2:51.868 I will run the       the page turns over: on the back, one red character, 爱; the papers round it go dim.
2:52.712 EXECUTION            the letter is taken out of the frame (to the slot of the room: next shot).

Words on the papers are the published or archived originals (checked 2026-09-30); everything else on them is
typesetting or handwriting too small to read."""
import math, random
from PIL import Image, ImageDraw, ImageFont

T_CUT, T_HIT, T_BACK, T_RUN, T_X = 166.016, 168.911, 169.824, 171.868, 172.712
LAND = [166.47, 166.94, 167.17, 167.40, 167.86, 168.10, 168.33]
POST = dict(u_bloom=0., u_ca=0., u_grain=.012)
F = 'C:/Windows/Fonts/'
# where each paper lies: centre, angle (deg) — around the envelope, in order of landing
LAY = [((-.62, .19), -6.), ((-.29, .27), 4.), ((-.67, -.23), 8.), ((-.27, -.29), -5.),
       ((.30, .29), -4.), ((.65, .17), 7.), ((.52, -.27), -8.)]


def clamp(x, a=0., b=1.): return a if x < a else b if x > b else x
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def outc(x): x = clamp(x); return 1 - (1 - x) ** 3


SRC = r'''#version 330
uniform vec2 u_res; uniform float u_time, u_weight;
uniform float u_press, u_crack, u_flap, u_envY, u_letY, u_top, u_bot, u_flip, u_letX, u_zoom, u_dim, u_dotA;
uniform vec2 u_shake;
uniform vec4 u_pg[7];            // centre xy, angle, drop (0 lying .. 1 far above); w < -1: not yet
uniform float u_pgA[7];
uniform sampler2D u_front, u_back, u_pages;
out vec4 fragColor;
const float PI = 3.14159265;
float h11(float p){ p = fract(p * .1031); p *= p + 33.33; p *= p + p; return fract(p); }
float h21(vec2 p){ vec3 p3 = fract(vec3(p.xyx) * .1031); p3 += dot(p3, p3.yzx + 33.33); return fract((p3.x + p3.y) * p3.z); }
float vn(vec2 p){ vec2 i = floor(p), f = fract(p); f = f * f * (3. - 2. * f);
  return mix(mix(h21(i), h21(i + vec2(1, 0)), f.x), mix(h21(i + vec2(0, 1)), h21(i + vec2(1, 1)), f.x), f.y); }
float fbm(vec2 p){ float a = .5, s = 0.; for(int i = 0; i < 4; i++){ s += a * vn(p); p = p * 2.03 + 7.1; a *= .5; } return s; }
vec3 srgb(float r, float g, float b){ return vec3(r, g, b) / 255.; }
vec3 untone(vec3 c, vec2 fc){
  vec3 L = pow(clamp(c, 0., .985), vec3(2.2));
  vec3 A = 2.51 - 2.43 * L, B = .03 - .59 * L, C = -.14 * L;
  vec3 y = (-B + sqrt(B * B - 4. * A * C)) / (2. * A);
  vec2 d = fc / u_res - .5;
  return y / 1.05 / (1. - .9 * dot(d, d));
}
float seg(vec2 p, vec2 a, vec2 b){ vec2 pa = p - a, ba = b - a; return length(pa - ba * clamp(dot(pa, ba) / dot(ba, ba), 0., 1.)); }
float aa(float d, float w){ return 1. - smoothstep(w * .5, w * 1.5, d); }
mat2 rot(float a){ float c = cos(a), s = sin(a); return mat2(c, -s, s, c); }

const vec2 EH = vec2(.31, .22);              // the envelope, half size (C6)
const vec2 APEX = vec2(0., -.03);             // where the flap's point meets the seal
const float LW = .29, PH = .135;             // the letter: half width, half a panel (three panels)
const float LINE = 2.6;                      // outline width, px at 1080p
vec3 PAPER, INK, CREAM, WAX, NIGHT;

vec4 envBody(vec2 p, float px){
  if(abs(p.x) > EH.x || abs(p.y) > EH.y) return vec4(0.);
  vec3 c = CREAM * (.97 + .045 * fbm(p * 60.));
  float l = 0.;
  l = max(l, aa(seg(p, vec2(-EH.x, -EH.y), vec2(-.05, -.05)), px * 1.6) * .7);
  l = max(l, aa(seg(p, vec2(EH.x, -EH.y), vec2(.05, -.05)), px * 1.6) * .7);
  float open = smoothstep(.5, 1.6, u_flap);
  float mouth = step(p.y, EH.y) * step(EH.y - (EH.y - APEX.y) * (1. - abs(p.x) / EH.x), p.y);
  c = mix(c, c * .78, mouth * open);
  c = mix(c, INK, l);
  float edge = min(EH.x - abs(p.x), EH.y - abs(p.y));
  c = mix(c, INK, aa(edge, px * LINE));
  return vec4(c, 1.);
}
vec4 flap(vec2 p, float px, out float onTop){
  float ct = cos(u_flap);
  float ay = EH.y - (EH.y - APEX.y) * ct;
  onTop = step(0., ct);
  float t = (EH.y - p.y) / max(EH.y - ay, 1e-4);
  if(ct < 0.) t = (p.y - EH.y) / max(ay - EH.y, 1e-4);
  float halfw = EH.x * (1. - t);
  if(t < 0. || t > 1. || abs(p.x) > halfw) return vec4(0.);
  vec3 col = CREAM * (ct >= 0. ? .99 : .88) * (.97 + .04 * fbm(p * 60. + 3.));
  float slant = (halfw - abs(p.x)) * abs(EH.y - ay) / length(vec2(EH.x, EH.y - ay));
  float e = min(slant, t * abs(EH.y - ay));
  col = mix(col, INK, aa(e, px * LINE * .8));
  return vec4(col, 1.);
}
vec4 seal(vec2 p, vec2 at, float half_, float px){
  vec2 q = (p - at) / .56;                                                 // the seal, at the envelope's scale
  float jag = .003 * sin(q.x * 420.) + .002 * sin(q.x * 910.);
  if(half_ > 0. && q.y < jag) return vec4(0.);
  if(half_ < 0. && q.y > jag) return vec4(0.);
  float r = length(q);
  float R = mix(.012, .082, u_press) * (1. + .06 * (fbm(q * 60.) - .5) + .04 * sin(atan(q.y, q.x) * 7.));
  if(r > R) return vec4(0.);
  vec3 c = WAX * (.9 + .2 * fbm(q * 90.));
  c *= mix(1., .7, smoothstep(R * .75, R, r));
  float ri = .044, w = .0075;
  float ang = atan(q.x, -q.y);
  float gap = smoothstep(.36, .48, abs(ang));
  float dr = r - ri;
  float ring = (1. - smoothstep(w * .7, w, abs(dr))) * gap * u_press;
  vec2 nrm = normalize(q + 1e-5) * sign(dr);
  c = mix(c, c * (1. + .55 * dot(nrm, normalize(vec2(-1., 1.)))), ring);
  c = mix(c, c * .75, (1. - smoothstep(.02, .026, r)) * u_press);
  c = mix(c, c * 1.35, pow(max(1. - length(q - vec2(-.025, .03)) / .02, 0.), 2.) * .5);
  if(half_ != 0.) c = mix(c, c * .45, 1. - smoothstep(0., .004, abs(q.y - jag)));   // the broken face
  return vec4(c, 1.);
}

vec3 page(vec2 uv, bool back){
  vec3 c = PAPER * (.97 + .04 * fbm(uv * vec2(30., 42.)));
  if(!back){ c = mix(c, INK, texture(u_front, uv).a * .9); }
  else {
    c = mix(c, INK, texture(u_front, uv).a * .07);
    c = mix(c, srgb(178., 24., 30.), texture(u_back, vec2(1. - uv.x, uv.y)).a * .92);   // the back is seen the right way round
  }
  c *= 1. - .08 * (1. - smoothstep(0., .004, abs(uv.y - 1. / 3.))) - .08 * (1. - smoothstep(0., .004, abs(uv.y - 2. / 3.)));
  return c;
}
vec4 letter(vec2 p, float px){
  p.x -= u_letX; p.y -= u_letY;
  p /= u_zoom;
  float xs = cos(PI * u_flip);
  if(abs(xs) < .01) return vec4(0.);
  bool back = xs < 0.;
  float x = p.x / abs(xs);
  if(abs(x) > LW) return vec4(0.);
  float u = back ? .5 - x / (2. * LW) : .5 + x / (2. * LW);
  vec3 col = vec3(0.); float a = 0.; float ey = 1.;
  if(abs(p.y) <= PH){ col = page(vec2(u, .5 + p.y / (6. * PH)), back); a = 1.; ey = PH - abs(p.y); }
  float cb = cos(u_bot);
  if(cb > 0.){ float s = (p.y + PH) / max(cb, 1e-3); if(s >= 0. && s <= 2. * PH){ col = PAPER * .9 * (.97 + .03 * fbm(p * 40.)); a = 1.; ey = min(s, 2. * PH - s) * cb; } }
  else { float s = (-PH - p.y) / max(-cb, 1e-3); if(s >= 0. && s <= 2. * PH){ col = page(vec2(u, (2. * PH - s) / (6. * PH)), back); a = 1.; ey = (2. * PH - s) * -cb; } }
  float ctp = cos(u_top);
  if(ctp > 0.){ float s = (PH - p.y) / max(ctp, 1e-3); if(s >= 0. && s <= 2. * PH){ col = PAPER * .94 * (.97 + .03 * fbm(p * 40. + 5.)); a = 1.; ey = min(s, 2. * PH - s) * ctp; } }
  else { float s = (p.y - PH) / max(-ctp, 1e-3); if(s >= 0. && s <= 2. * PH){ col = page(vec2(u, (4. * PH + s) / (6. * PH)), back); a = 1.; ey = (2. * PH - s) * -ctp; } }
  if(a > 0.){
    float ex = LW * abs(xs) - abs(p.x);
    float full = (cb < 0. && ctp < 0.) ? 3. * PH - abs(p.y) : ey;
    col = mix(col, INK, aa(min(ex, full) * u_zoom, px * LINE));
  }
  return vec4(col, a);
}
// one of his papers, lying (or falling): an atlas cell
vec4 paper(vec2 p, int i, float px, out float shadow){
  shadow = 0.;
  vec4 g = u_pg[i];
  if(g.w < -1.) return vec4(0.);
  float s = 1. + .55 * g.w * g.w;                                  // nearer the eye while it falls
  vec2 q = rot(-g.z - g.w * .25) * (p - g.xy) / s;
  vec2 hs = vec2(.19, .27);
  vec2 qs = rot(-g.z) * (p - g.xy - vec2(.006, -.009));
  float sd = max(abs(qs.x) - hs.x, abs(qs.y) - hs.y);
  shadow = (1. - smoothstep(-.004, .012, sd)) * (1. - g.w) * .55;
  if(abs(q.x) > hs.x || abs(q.y) > hs.y) return vec4(0.);
  vec2 uv = q / hs * .5 + .5;
  vec2 cell = vec2(float(i % 4), float(1 - i / 4));
  vec2 auv = (cell + clamp(uv, .002, .998)) / vec2(4., 2.);
  float ink = texture(u_pages, auv).a;
  vec3 c = PAPER * (.955 + .05 * fbm(q * 50. + float(i) * 7.));
  if(i == 0) c *= vec3(1., .985, .95);                             // the manuscript: an older, warmer paper
  c = mix(c, INK, ink * .92);
  float e = min(hs.x - abs(q.x), hs.y - abs(q.y)) * s;
  c = mix(c, INK, aa(e, px * LINE));
  return vec4(c, u_pgA[i]);
}

void main(){
  float s1 = h11(u_time * 1731.7 + .13), s2 = h11(u_time * 911.3 + .71);
  vec2 fc = gl_FragCoord.xy + vec2(s1, s2) - .5;
  vec2 p = (fc - .5 * u_res) / u_res.y + u_shake;
  float px = 1. / u_res.y;
  PAPER = srgb(246., 241., 229.); INK = srgb(38., 30., 24.); CREAM = srgb(242., 235., 219.); WAX = srgb(150., 18., 24.);
  NIGHT = srgb(13., 12., 11.);
  vec3 col = NIGHT * (1. + .05 * (fbm(fc * .05 / (u_res.y / 1080.)) - .5));
  vec2 fr = abs(p) - vec2(.855, .47);
  col = mix(col, srgb(200., 196., 186.), aa(abs(max(fr.x, fr.y)), px * 1.4) * .4);

  // his papers, in the order they fell
  for(int i = 0; i < 7; i++){
    float sh; vec4 P = paper(p, i, px, sh);
    col *= 1. - sh;
    if(P.a > 0.) col = mix(col, P.rgb, P.a);
  }
  col *= 1. - u_dim;

  vec2 pe = p - vec2(0., u_envY);
  float onTop;
  vec4 Fl = flap(pe, px, onTop);
  vec4 B = envBody(pe, px);
  vec4 Lt = letter(p, px);
  bool leaving = u_envY < -.001;
  vec2 es = abs(pe - vec2(.006, -.009)) - EH;
  if(u_envY > -1.) col *= 1. - (1. - smoothstep(-.004, .012, max(es.x, es.y))) * .55;
  if(onTop < .5 && Fl.a > 0.) col = Fl.rgb;
  if(!leaving && u_letY > .001 && Lt.a > 0.) col = Lt.rgb;
  if(B.a > 0.) col = B.rgb;
  if(onTop > .5 && Fl.a > 0.) col = Fl.rgb;
  vec2 at = APEX + vec2(0., u_envY);
  if(u_press <= 0.) col = mix(col, srgb(196., 22., 30.), (1. - smoothstep(7. * px, 8.5 * px, length(p - at))) * u_dotA);
  if(u_press > 0.){
    float ct = cos(u_flap);
    if(u_crack <= 0.){ vec4 S = seal(p, at, 0., px); if(S.a > 0.) col = S.rgb; }
    else {
      vec4 S = seal(p, at + vec2(.003, -.002), -1., px); if(S.a > 0.) col = S.rgb;
      vec2 up = vec2(-.003, EH.y - (EH.y - APEX.y) * ct + u_envY);
      if(ct > -.2){ vec4 S2 = seal(p, up, 1., px); if(S2.a > 0.) col = S2.rgb; }
    }
  }
  if(leaving && Lt.a > 0.) col = Lt.rgb;
  if(any(isnan(col))) col = NIGHT;
  fragColor = vec4(untone(col, gl_FragCoord.xy) * u_weight, 1.);
}
'''


def params(t):
    press = outc((t - T_HIT) / .06) if t >= T_HIT else 0.
    k = t - T_HIT
    shake = (0., 0.)
    if 0 <= k < .07:
        r = random.Random(int(t * 60))
        shake = (r.uniform(-1, 1) * .005, r.uniform(-1, 1) * .005)
    pg, pa = [], []
    for (c, ang), tl in zip(LAY, LAND):
        if t < tl - .17: pg.append((0., 0., 0., -9.)); pa.append(0.); continue
        a = clamp((t - tl + .17) / .17)
        pg.append((c[0], c[1], math.radians(ang), (1 - a) ** 2)); pa.append(min(1., a * 3.))
    return dict(u_press=press, u_shake=shake, u_crack=1. if t >= T_BACK else 0.,
                u_flap=math.pi * ease((t - T_BACK - .04) / .26),
                u_envY=-1.3 * ease((t - 170.35) / .28), u_letY=.36 * ease((t - 170.05) / .33) - .36 * ease((t - 170.38) / .25),
                u_top=math.pi * ease((t - 170.6) / .18), u_bot=math.pi * ease((t - 170.78) / .18),
                u_flip=ease((t - T_RUN) / .34), u_letX=1.9 * ease((t - T_X) / .3),
                u_zoom=1. + .05 * ease((t - 170.96) / .9) - .05 * ease((t - T_RUN) / .3),
                u_dim=.5 * ease((t - T_RUN) / .3), u_dotA=1.,
                u_pg=pg, u_pgA=pa)


# ---------------- the papers: the originals' words; the rest typesetting or hand too small to read
W, H = 820, 1160


def _font(name, size): return ImageFont.truetype(F + name, size)


def _gray_lines(d, x0, y, x1, n, lead, r, h=5, fill=(255, 255, 255, 105), indent=True):
    for i in range(n):
        xe = x1 - (r.uniform(40, 300) if (i == n - 1 or r.random() < .08) else 0)
        x = x0 + (28 if indent and i == 0 else 0)
        while x < xe:
            wl = r.uniform(18, 70)
            d.rectangle([x, y, min(x + wl, xe), y + h], fill=fill)
            x += wl + r.uniform(7, 11)
        y += lead
    return y


def _scribble(d, x0, y, x1, r, w=3, a=235):
    x = x0
    while x < x1:
        wl = r.uniform(30, 90); pts = []
        for i in range(int(wl / 3)):
            xx = x + i * 3
            pts.append((xx, y + 7 * math.sin(xx * .33 + r.uniform(0, .4)) * r.uniform(.4, 1.)))
        d.line(pts, fill=(255, 255, 255, a), width=w)
        x += wl + r.uniform(12, 22)


def _wrap(d, x, y, text, font, width, lead, fill=(255, 255, 255, 250)):
    words, line = text.split(), ''
    for w_ in words:
        tt = (line + ' ' + w_).strip()
        if d.textlength(tt, font=font) > width and line:
            d.text((x, y), line, font=font, fill=fill); y += lead; line = w_
        else: line = tt
    d.text((x, y), line, font=font, fill=fill)
    return y + lead


def _runs(d, x0, y, runs, width, lead, fill=(255, 255, 255, 250)):
    """Words in mixed fonts (the paper's gothic D and M among roman), wrapped."""
    x = x0
    for s_, f_ in runs:
        for w_ in s_.split(' '):
            if not w_: continue
            wl = d.textlength(w_ + ' ', font=f_)
            if x + wl > x0 + width: x = x0; y += lead
            d.text((x, y), w_, font=f_, fill=fill); x += wl
    return y + lead


def _pages():
    atlas = Image.new('RGBA', (W * 4, H * 2), (0, 0, 0, 0))
    r = random.Random(36)
    serif, serifb, serifi = 'times.ttf', 'timesbd.ttf', 'timesi.ttf'
    WHITE = (255, 255, 255, 255)
    pages = []

    # 0 · c. 1932, Nature of Spirit (manuscript; Turing Archive AMT/C/29)
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((W / 2, 90), 'Nature of Spirit', font=_font('segoesc.ttf', 44), fill=WHITE, anchor='mm')
    y = 170
    for i in range(6): _scribble(d, 60, y, W - 60, r); y += 62
    y = _wrap(d, 70, y + 10, 'Personally, I think that spirit is really eternally connected with matter but certainly not always by the same kind of body.',
              _font('segoesc.ttf', 34), W - 130, 58)
    for i in range(6): _scribble(d, 60, y + 10, W - 60 - (200 if i == 5 else 0), r); y += 62
    pages.append(im)

    # 1 · 1936, On Computable Numbers: the opening
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for x, s_, an in ((60, '230', 'la'), (W / 2, 'A. M. TURING', 'ma'), (W - 60, '[Nov. 12,', 'ra')):
        d.text((x, 50), s_, font=_font(serif, 22), fill=(255, 255, 255, 220), anchor=an)
    d.text((W / 2, 150), 'ON COMPUTABLE NUMBERS, WITH AN APPLICATION', font=_font(serifb, 25), fill=WHITE, anchor='mm')
    d.text((W / 2, 188), 'TO THE ENTSCHEIDUNGSPROBLEM', font=_font(serifb, 25), fill=WHITE, anchor='mm')
    d.text((W / 2, 245), 'By A. M. TURING.', font=_font(serif, 26), fill=WHITE, anchor='mm')
    d.text((W / 2, 285), '[Received 28 May, 1936.—Read 12 November, 1936.]', font=_font(serif, 20), fill=(255, 255, 255, 220), anchor='mm')
    y = _wrap(d, 70, 340, 'The "computable" numbers may be described briefly as the real numbers whose expressions as a decimal are calculable by finite means.',
              _font(serif, 26), W - 140, 38)
    _gray_lines(d, 70, y + 8, W - 70, 17, 38, r)
    pages.append(im)

    # 2 · 1936, the first machine's table
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    y = _gray_lines(d, 70, 70, W - 70, 6, 36, r)
    d.text((70, y + 10), '3. Examples of computing machines.', font=_font(serifi, 26), fill=WHITE)
    y = _wrap(d, 70, y + 60, 'I. A machine can be constructed to compute the sequence 010101....', _font(serif, 26), W - 140, 38)
    fb = _font(serif, 28); fh = _font(serifi, 22)
    x0, x1, x2, x3, x4 = 110, 250, 390, 560, 720
    ty = y + 30
    d.text(((x0 + x2) / 2, ty), 'Configuration', font=fh, fill=WHITE, anchor='mm')
    d.text(((x2 + x4) / 2, ty), 'Behaviour', font=fh, fill=WHITE, anchor='mm')
    d.line([(x0, ty + 18), (x4, ty + 18)], fill=(255, 255, 255, 220), width=2)
    for x, h_ in ((x0, 'm-config.'), (x1, 'symbol'), (x2, 'operations'), (x3, 'final m-config.')):
        d.text((x + 6, ty + 30), h_, font=fh, fill=(255, 255, 255, 220))
    d.line([(x0, ty + 64), (x4, ty + 64)], fill=(255, 255, 255, 220), width=2)
    for x in (x1, x2, x3): d.line([(x, ty - 14), (x, ty + 290)], fill=(255, 255, 255, 200), width=2)
    for i, row in enumerate([('b', 'None', 'P0, R', 'c'), ('c', 'None', 'R', 'e'), ('e', 'None', 'P1, R', 'f'), ('f', 'None', 'R', 'b')]):
        yy = ty + 90 + i * 52
        for x, v in zip((x0, x1, x2, x3), row):
            d.text((x + 18, yy), v, font=fb, fill=WHITE)
    _gray_lines(d, 70, ty + 330, W - 70, 11, 36, r)
    pages.append(im)

    # 3 · 1936, the verdicts that cannot be (section 8)
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    y = _gray_lines(d, 70, 70, W - 70, 5, 36, r)
    ft = _font(serif, 26); fg = _font('OLDENGL.TTF', 28)
    y = _runs(d, 70, y + 20, [('Let us suppose that there is such a process; that is to say, that we can invent a machine', ft), ('D', fg),
                              ('which, when supplied with the S.D of any computing machine', ft), ('M', fg), ('will test this S.D and if', ft),
                              ('M', fg), ('is circular will mark the S.D with the symbol "u" and if it is circle-free will mark it with "s".', ft)], W - 130, 40)
    y = _gray_lines(d, 70, y + 16, W - 70, 11, 36, r)
    y2 = _runs(d, 70, y + 14, [('Thus both verdicts are impossible and we conclude that there can be no machine', ft), ('D.', fg)], W - 130, 40)
    d.line([(66, y2 - 2), (W - 180, y2 - 4)], fill=(255, 255, 255, 150), width=2)       # a pencil line under it
    _gray_lines(d, 70, y2 + 40, W - 70, 5, 36, r, indent=False)
    pages.append(im)

    # 4 · 1950, Computing Machinery and Intelligence: the opening
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((W / 2, 80), 'M I N D', font=_font(serifb, 46), fill=WHITE, anchor='mm')
    d.text((W - 60, 140), 'October, 1950', font=_font(serifi, 22), fill=(255, 255, 255, 220), anchor='ra')
    d.line([(60, 165), (W - 60, 165)], fill=(255, 255, 255, 200), width=2)
    d.text((W / 2, 215), 'COMPUTING MACHINERY AND INTELLIGENCE', font=_font(serifb, 28), fill=WHITE, anchor='mm')
    d.text((W / 2, 258), 'By A. M. TURING', font=_font(serif, 24), fill=WHITE, anchor='mm')
    d.text((70, 310), '1. The Imitation Game.', font=_font(serifi, 26), fill=WHITE)
    d.text((70, 360), 'I propose to consider the question,', font=_font(serif, 30), fill=WHITE)
    d.text((70, 405), '"Can machines think?"', font=_font(serifb, 40), fill=WHITE)
    _gray_lines(d, 70, 480, W - 70, 16, 38, r)
    pages.append(im)

    # 5 · 1950, specimen questions and answers
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    y = _gray_lines(d, 70, 70, W - 70, 5, 36, r)
    fq = _font(serif, 27)
    for ln in ['Q: Please write me a sonnet on the subject of', '     the Forth Bridge.',
               'A: Count me out on this one. I never could', '     write poetry.',
               'Q: Add 34957 to 70764.',
               'A: (Pause about 30 seconds and then give as', '     answer) 105621.',
               'Q: Do you play chess?', 'A: Yes.']:
        y += 44; d.text((70, y), ln, font=fq, fill=WHITE)
    _gray_lines(d, 70, y + 70, W - 70, 10, 36, r)
    pages.append(im)

    # 6 · 1950, Lady Lovelace's objection
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    y = _gray_lines(d, 70, 70, W - 70, 6, 36, r)
    d.text((W / 2, y + 40), "(6) Lady Lovelace's Objection", font=_font(serifi, 32), fill=WHITE, anchor='mm')
    y = _wrap(d, 70, y + 90, 'Our most detailed information of Babbage\'s Analytical Engine comes from a memoir by Lady Lovelace (1842). In it she states, "The Analytical Engine has no pretensions to originate anything. It can do whatever we know how to order it to perform" (her italics).',
              _font(serif, 26), W - 140, 38)
    _gray_lines(d, 70, y + 10, W - 70, 12, 36, r)
    pages.append(im)

    for i, im in enumerate(pages):
        atlas.paste(im, ((i % 4) * W, (i // 4) * H))
    return atlas


def _front():
    Wf, Hf = 1400, 1970
    img = Image.new('RGBA', (Wf, Hf), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    r = random.Random(1930)
    f = _font('segoesc.ttf', 56); fd = _font('segoesc.ttf', 40)
    d.text((Wf - 110, 120), '16. II. 1930', font=fd, fill=(255, 255, 255, 240), anchor='rm')
    y = 250
    for i in range(7): _scribble(d, 110 + (60 if i == 0 else 0), y, Wf - 120 - r.uniform(0, 300) * (i == 6), r); y += 78
    y += 20
    for ln in ['I feel sure that I shall meet', 'Morcom again somewhere &', 'that there will be some work', 'for us to do together']:
        d.text((130, y), ln, font=f, fill=(255, 255, 255, 250)); y += 96
    y += 30
    for i in range(8): _scribble(d, 110, y, Wf - 120 - r.uniform(0, 400) * (i == 7), r); y += 78
    return img


def _back():
    Wf, Hf = 1400, 1970
    img = Image.new('RGBA', (Wf, Hf), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.text((Wf / 2, Hf * .5), '爱', font=_font('simhei.ttf', 600), fill=(255, 255, 255, 255), anchor='mm')   # upright, black-letter Heiti: he can look it up
    return img


_TX = {}


def textures(t, w, h):
    if not _TX:
        _TX.update(f=_front(), b=_back(), p=_pages())
    return {'u_front': _TX['f'], 'u_back': _TX['b'], 'u_pages': _TX['p']}
