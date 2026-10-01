#version 330
// t11 · the assembled machine, drawn.  Units: cm.  Orthographic.  The parts of the Analytical Engine
// (a studded barrel, figure wheels, cards) put together as a card sorter.
uniform vec2 u_res; uniform float u_time, u_weight;
uniform vec3 u_c, u_fwd, u_right, u_up; uniform float u_scale;
uniform float u_exec;
uniform sampler2D u_odo, u_ui;
out vec4 fragColor;

const float PI = 3.14159265;
const vec3 VIEW = vec3(1., -.55, 1.3);

float h11(float p){ p = fract(p * .1031); p *= p + 33.33; p *= p + p; return fract(p); }
float h21(vec2 p){ vec3 p3 = fract(vec3(p.xyx) * .1031); p3 += dot(p3, p3.yzx + 33.33); return fract((p3.x + p3.y) * p3.z); }
float h31(vec3 p){ p = fract(p * .1031); p += dot(p, p.zyx + 31.32); return fract((p.x + p.y) * p.z); }
float vn(vec3 p){
  vec3 i = floor(p), f = fract(p); f = f * f * (3. - 2. * f);
  return mix(mix(mix(h31(i), h31(i + vec3(1,0,0)), f.x), mix(h31(i + vec3(0,1,0)), h31(i + vec3(1,1,0)), f.x), f.y),
             mix(mix(h31(i + vec3(0,0,1)), h31(i + vec3(1,0,1)), f.x), mix(h31(i + vec3(0,1,1)), h31(i + vec3(1,1,1)), f.x), f.y), f.z);
}
float fbm(vec3 p){ float a = .5, s = 0.; for(int i = 0; i < 4; i++){ s += a * vn(p); p = p * 2.03 + 7.1; a *= .5; } return s; }
float box(vec3 p, vec3 b){ vec3 q = abs(p) - b; return length(max(q, 0.)) + min(max(q.x, max(q.y, q.z)), 0.); }
mat2 rot(float a){ float c = cos(a), s = sin(a); return mat2(c, -s, s, c); }

// the counters: figure wheels on an axle along x; the reading faces the viewer
const float CX0 = -2., CDX = 4.6, CY = 29., CZ = 10.4, CR = 3.6, CW = 1.7;
const int NCNT = 6;
uniform float u_cnt[6];
// the machine is laid out with the cards running toward -x; mirrored so they run left to right on the sheet
vec3 M(vec3 p){ return vec3(-p.x, p.y, p.z); }
float odo(vec3 q, float digit){
  float phiF = atan(-VIEW.y, -VIEW.z);
  float phi = atan(q.y, q.z);
  float s = (phiF - phi) / (2. * PI / 10.) + digit + .5;
  s = floor(s) + 1. - fract(s);                              // each glyph turned the right way up
  float u = .5 + q.x / (2. * CW);
  if(u < 0. || u > 1.) return 0.;
  return textureLod(u_odo, vec2(u, 1. - fract(s / 10.)), 0.).r;
}

// store columns over the pockets
const float SX0 = 4., SZ = 10.2, SY0 = 11.4, SP = 1.72, SR = 1.85, SH = .5;
float storeDigit(float ic, float j){ return abs(ic - 6.) < .5 ? u_cnt[int(5. - j)] : 0.; }
uniform sampler2D u_col;
float colDigit(vec3 w, float digit){                         // a figure wheel's rim, the reading toward us
  float phiF = atan(-VIEW.z, VIEW.x);                          // toward the viewer, in the mirrored layout
  float phi = atan(w.z, w.x);
  float s = (phi - phiF) / (2. * PI / 10.) + digit + .5;
  float v = w.y / (2. * SH) + .5;
  if(v < 0. || v > 1.) return 0.;
  return textureLod(u_col, vec2(fract(s / 10.), v), 0.).r;
}
float gearZ(vec3 q, float R, float N, float th){               // a spoked spur gear, axis z
  float r = length(q.xy), a = atan(q.y, q.x);
  float rim = (r - R - clamp(cos(a * N) * 1.6, -1., 1.) * .16 * R / 5.) * .7;
  float web = max(rim, -(r - .74 * R));
  float sa = mod(a, 2. * PI / 5.) - PI / 5.;
  float arm = max(abs(r * sin(sa)) - .07 * R, r - .8 * R);
  float d2 = min(web, min(r - .22 * R, arm));
  return max(d2, abs(q.z) - th);
}

int MAT; float PID; vec2 CUV;
void U(inout float d, float nd, int m, float id){ if(nd < d){ d = nd; MAT = m; PID = id; } }
void UC(inout float d, float nd, float id, vec2 uv){ if(nd < d){ d = nd; MAT = 3; PID = id; CUV = uv; } }

float map(vec3 pw){
  vec3 p = M(pw);
  float d = 1e9;
  // cast-iron base on four short feet
  U(d, box(p - vec3(-2., -2., 0.), vec3(72., 2., 16.)), 1, 1.);
  U(d, box(p - vec3(-2., -6.5, 0.), vec3(68., 2.5, 13.)), 1, 2.);
  U(d, box(vec3(abs(p.x + 2.) - 64., p.y + 11., abs(p.z) - 10.), vec3(3., 2.5, 3.)), 1, 3. + step(-2., p.x) + 2. * step(0., p.z));

  // hopper: platform, side walls, back stop, the stack of cards
  U(d, box(p - vec3(-58., 4., 0.), vec3(10., 4., 11.)), 1, 10.);
  U(d, box(vec3(p.x + 58., p.y - 13., abs(p.z) - 9.8), vec3(7., 5., .35)), 1, 11. + step(0., p.z));
  U(d, box(p - vec3(-65.6, 13., 0.), vec3(.35, 5., 10.1)), 1, 13.);
  U(d, box(p - vec3(-58., 12., 0.), vec3(4.15, 4., 9.35)), 4, 14.);
  UC(d, box(p - vec3(-58., 16.03, 0.), vec3(4.15, .03, 9.35)), 15., vec2((p.z + 9.35) / 18.7, (p.x + 58. + 4.15) / 8.3));

  // the barrel (from the Engine's control barrels), studded; here it draws the cards off the stack
  vec3 bq = p - vec3(-44., 13.5, 0.);
  U(d, max(length(bq.xy) - 3.2, abs(bq.z) - 9.5), 2, 70.);
  U(d, max(length(bq.xy) - .7, max(bq.z - 12.4, -17.9 - bq.z)), 6, 72.);
  U(d, box(vec3(bq.x, p.y - 6.8, abs(bq.z) - 11.2), vec3(1.6, 6.8, .8)), 1, 73. + step(0., bq.z));
  {
    float na = 22., ang = atan(bq.y, bq.x);
    float ai = round(ang / (2. * PI / na)), zi = clamp(round(bq.z / 1.5), -6., 6.);
    float a = ai * 2. * PI / na;
    vec3 c = vec3(cos(a) * 3.2, sin(a) * 3.2, zi * 1.5);
    if(h21(vec2(ai, zi) + 3.7) > .42) U(d, length(bq - c) - .42, 5, 71.);
  }
  // the reading brushes
  U(d, box(p - vec3(-31., 12.4, 0.), vec3(1.6, 2.3, 10.4)), 2, 80.);

  // the bed up to the pockets, then a narrow rail along the back over them
  U(d, box(p - vec3(-20., 9.6, 0.), vec3(20., .5, 10.5)), 1, 21.);
  U(d, box(p - vec3(29., 9.6, 8.6), vec3(29., .5, 1.9)), 1, 22.);
  for(int i = 0; i < 2; i++){
    float cx = -22. + 15. * float(i);
    UC(d, box(p - vec3(cx, 10.13, 0.), vec3(4.15, .03, 9.35)), 16. + float(i), vec2((p.z + 9.35) / 18.7, (p.x - cx + 4.15) / 8.3));
  }
  // a card falling into pocket 4
  {
    vec3 q = p - vec3(29.2, 12.9, -2.6); q.xy = rot(-1.12) * q.xy;
    UC(d, box(q, vec3(4.15, .03, 9.35)), 19., vec2((q.z + 9.35) / 18.7, (q.x + 4.15) / 8.3));
  }

  // thirteen pockets: separators, back wall, a low front lip
  float kk = clamp(round((p.x - 1.9) / 4.2), 0., 13.);
  U(d, box(vec3(p.x - (1.9 + 4.2 * kk), p.y - 4.5, p.z), vec3(.15, 4.5, 10.)), 1, 30. + kk);
  U(d, box(p - vec3(29.2, 4.5, 10.2), vec3(27.3, 4.5, .2)), 1, 50.);
  U(d, box(p - vec3(29.2, .9, -10.2), vec3(27.3, .9, .2)), 1, 51.);
  // pocket 4 (the seventh) is full: cards leaning back, faces up
  {
    float lean = .5, sl = tan(lean);
    float xs = p.x + (p.y - .3) * sl;
    float ck = clamp(round((xs - 26.4) / .75), 0., 5.);
    float cx = 26.4 + .75 * ck;
    vec3 q = vec3((xs - cx) * cos(lean), p.y - .3, p.z);
    float dc = max(max(abs(q.x) - .03, abs(q.y - 4.15 * cos(lean)) - 4.15 * cos(lean)), abs(q.z) - 9.35);
    UC(d, dc, 60. + ck, vec2((p.z + 9.35) / 18.7, (p.y - .3) / (8.3 * cos(lean))));
  }

  // the Engine's store, kept: over each pocket a column of figure wheels counts what falls in
  U(d, box(p - vec3(29.2, 21.3, 10.2), vec3(27.6, .5, 1.3)), 1, 92.);
  U(d, box(vec3(abs(p.x - 29.2) - 28.1, p.y - 15.6, p.z - 10.2), vec3(.5, 5.6, .9)), 1, 93. + step(29.2, p.x));
  {
    float ic = clamp(round((p.x - SX0) / 4.2), 0., 12.);
    vec3 c = p - vec3(SX0 + ic * 4.2, 0., SZ);
    U(d, max(length(c.xz) - .32, abs(p.y - 15.9) - 5.5), 6, 95.);
    float j = clamp(round((p.y - SY0) / SP), 0., 5.);
    vec3 w = c - vec3(0., SY0 + j * SP, 0.);
    float rr = length(w.xz);
    vec2 e = vec2(rr - SR, abs(w.y) - SH);
    float dw = min(max(e.x, e.y), 0.) + length(max(e + .08, 0.)) - .08;
    if(rr > SR - .2) dw += .05 * colDigit(w, storeDigit(ic, j));
    U(d, dw, 2, 100. + ic * 10. + j);
    vec3 g = w + vec3(0., SH + .28, 0.);
    float a = atan(g.z, g.x);
    float dg = max((length(g.xz) - 1.45 - clamp(cos(a * 20.) * 1.6, -1., 1.) * .09) * .7, abs(g.y) - .14);
    U(d, dg, 2, 230. + ic * 10. + j);
  }

  // the drive: a crank, three gears, the barrel's axle brought out to the front
  {
    vec3 q = p - vec3(0., 0., -17.2);
    U(d, gearZ(q - vec3(-44., 13.5, 0.), 3.6, 18., .45), 2, 310.);
    U(d, gearZ(q - vec3(-38.5, 6., 0.), 5.7, 28., .45), 2, 311.);
    U(d, gearZ(q - vec3(-27.2, -3.4, 0.), 9., 44., .5), 2, 312.);
    U(d, max(length(p.xy - vec2(-38.5, 6.)) - .6, abs(p.z + 17.2) - .9), 6, 313.);
    U(d, max(length(p.xy - vec2(-27.2, -3.4)) - .7, abs(p.z + 17.) - 1.1), 6, 314.);
    U(d, box(p - vec3(-38.5, 2.6, -16.3), vec3(1.3, 3.2, .3)), 1, 315.);
    vec2 cq = rot(-.62) * (p.xy - vec2(-27.2, -3.4));
    U(d, box(vec3(cq.x - 3.7, cq.y, p.z + 18.), vec3(4.1, .55, .3)), 1, 316.);
    U(d, max(length(cq - vec2(7.4, 0.)) - .75, abs(p.z + 19.6) - 1.6), 6, 317.);
  }
  return d;
}

vec3 normal(vec3 p, float e){
  const vec2 k = vec2(1., -1.);
  return normalize(k.xyy * map(p + k.xyy * e) + k.yyx * map(p + k.yyx * e) + k.yxy * map(p + k.yxy * e) + k.xxx * map(p + k.xxx * e));
}

vec3 rayO(vec2 fc){
  vec2 uv = (fc - .5 * u_res) / u_res.y;
  return u_c + (uv.x * u_right + uv.y * u_up) * (2. * u_scale) - u_fwd * 400.;
}

float trace(vec2 fc, out vec3 p, out float id, out int mat, out vec2 cuv){
  vec3 ro = rayO(fc);
  float t = 250.;
  id = -1.; mat = 0; p = ro; cuv = vec2(0.);
  for(int i = 0; i < 320; i++){
    p = ro + u_fwd * t;
    float d = map(p);
    if(d < .003){ mat = MAT; id = PID; cuv = CUV; return t; }
    t += d * .85;
    if(t > 560.) break;
  }
  return -1.;
}

vec3 srgb(float r, float g, float b){ return vec3(r, g, b) / 255.; }
vec3 untone(vec3 c, vec2 fc){
  vec3 L = pow(clamp(c, 0., .985), vec3(2.2));
  vec3 A = 2.51 - 2.43 * L, B = .03 - .59 * L, C = -.14 * L;
  vec3 y = (-B + sqrt(B * B - 4. * A * C)) / (2. * A);
  vec2 d = fc / u_res - .5;
  return y / 1.05 / (1. - .9 * dot(d, d));
}

// a census card's face: printed columns, punched holes, the one hole
vec4 cardFace(vec2 uv, float id, float px){
  vec3 c = srgb(247., 243., 232.);
  float ink = 0.;
  if(uv.y > .86) ink = max(ink, .12);                              // the printed head band
  float col = floor(uv.x * 80.), row = floor((.84 - uv.y) / .07);
  vec2 f = vec2(fract(uv.x * 80.), fract((.84 - uv.y) / .07));
  if(row >= 0. && row < 12.){
    float dot_ = length((f - .5) * vec2(1., 1.6)) ;
    ink = max(ink, (1. - smoothstep(.12, .22, dot_)) * .28);
    bool hole = h21(vec2(col, id * 1.3)) < .4 && abs(row - floor(h21(vec2(col * 1.7, id)) * 12.)) < .5;
    float inside = step(abs(f.x - .5), .32) * step(abs(f.y - .5), .36);
    if(hole) ink = max(ink, inside);
  }
  return vec4(c, ink);
}
// the one hole, and the red it bleeds into the paper around it (in card cm)
vec2 cardRed(vec2 uv){
  vec2 c = vec2(41.5 / 80., .84 - 5.5 * .07);           // column 41, row 5
  float d = length((uv - c) * vec2(18.7, 8.3));
  return vec2(1. - smoothstep(.32, .42, d), 1. - smoothstep(.9, 1.5, d));
}

void main(){
  float s1 = h11(u_time * 1731.7 + .13), s2 = h11(u_time * 911.3 + .71);
  vec2 fc = gl_FragCoord.xy + vec2(s1, s2) - .5;
  float px = u_res.y / 1080.;
  vec3 PAPER = srgb(240., 233., 218.), INK = srgb(38., 30., 24.), RED = srgb(196., 22., 30.);

  vec3 p; float id; int mat; vec2 cuv;
  float t = trace(fc, p, id, mat, cuv);
  vec3 col = PAPER * (.975 + .035 * fbm(vec3(fc / px * .08, 1.)) + .012 * (h21(floor(fc)) - .5));

  vec3 n = vec3(0.);
  if(t > 0.){
    n = normal(p, .005);
    vec3 L = normalize(vec3(-.55, .8, -.45));
    float lam = dot(n, L);
    vec3 wash = mat == 2 || mat == 5 ? srgb(226., 198., 140.) : (mat == 6 ? srgb(196., 204., 206.) : (mat >= 3 && mat <= 4 ? srgb(250., 246., 236.) : srgb(200., 202., 200.)));
    col = mix(PAPER, wash, lam > .15 ? .3 : .6);
    if(n.y < -.6) col = mix(PAPER, wash * .82, .9);
    float ink = 0.;
    // shaded faces: open diagonal hatching; undersides: close
    if(lam < .1 && mat != 3){
      float x = (fc.x - fc.y) / (7. * px);
      ink = max(ink, (1. - smoothstep(.3, 1., abs(fract(x) - .5) * 7.)) * .7);
    }
    if(n.y < -.6){
      float x = (fc.x + fc.y) / (4. * px);
      ink = max(ink, 1. - smoothstep(.4, 1.1, abs(fract(x) - .5) * 4.));
    }
    // the stack in the hopper: the edges of the cards
    if(mat == 4 && abs(n.y) < .5) ink = max(ink, (1. - smoothstep(.1, .35, abs(fract(p.y / .3) - .5) * 2.)) * .55);
    // cylinders: shading lines along the axis
    if(mat == 2 && id == 70.){
      vec3 bq = M(p) - vec3(-44., 13.5, 0.);
      float x = atan(bq.y, bq.x) * 40. / (2. * PI);
      float fw = max(fwidth(x), 1e-4), dark = clamp((.4 - lam) / .9, 0., 1.);
      ink = max(ink, (1. - smoothstep(fw * (.3 + 1.4 * dark) - fw * .5, fw * (.3 + 1.4 * dark) + fw * .5, abs(fract(x + .5) - .5))) * step(.05, dark));
    }
    if(mat == 2 && id >= 100. && id < 230.){
      float ic = floor((id - 100.) / 10.), j = id - 100. - ic * 10.;
      vec3 c = M(p) - vec3(SX0 + ic * 4.2, SY0 + j * SP, SZ);
      if(length(c.xz) > SR - .2 && abs(c.y) < SH) ink = max(ink, smoothstep(.35, .65, colDigit(c, storeDigit(ic, j))));
      float x = atan(c.z, c.x) * 60. / (2. * PI);
      float fw = max(fwidth(x), 1e-4), dark = clamp((.3 - lam) / .9, 0., 1.);
      if(abs(n.y) < .5) ink = max(ink, (1. - smoothstep(fw * (.3 + 1.2 * dark) - fw * .5, fw * (.3 + 1.2 * dark) + fw * .5, abs(fract(x + .5) - .5))) * step(.05, dark));
    }
    // card faces
    if(mat == 3){
      bool face = id < 60. ? abs(n.y) > .5 || id == 19. : abs(n.x) > .3;
      if(face){
        vec4 cf = cardFace(cuv, id, px);
        col = mix(cf.rgb, INK, cf.a * .8);
        if(u_exec > 0.){ vec2 cr = cardRed(cuv); col = mix(col, mix(PAPER, RED, .45), cr.y * .6); col = mix(col, RED, cr.x); }
      }
    }
    col = mix(col, INK, ink * .8);
  }

  // outlines: thin between parts and at creases, heavy against the paper or across a depth step
  float e = 0.;
  float wpx = 2. * u_scale / u_res.y;                    // one pixel, in cm: depth thresholds scale with it
  for(int ring = 0; ring < 2; ring++){
    float o = (ring == 0 ? 1.05 : 2.2) * px;
    vec2 offs[4] = vec2[4](vec2(o, 0.), vec2(-o, 0.), vec2(0., o), vec2(0., -o));
    for(int i = 0; i < 4; i++){
      vec3 p2; float id2; int m2; vec2 c2;
      float t2 = trace(fc + offs[i], p2, id2, m2, c2);
      if((t > 0.) != (t2 > 0.)){ e = 1.; continue; }
      if(t < 0.) continue;
      if(ring == 1){ if(t2 - t > 2. * wpx / .115) e = 1.; continue; }
      if(abs(t2 - t) > .4 * wpx / .115 || abs(id2 - id) > .5) e = max(e, .75);
      else if(dot(n, normal(p2, .005)) < .75) e = max(e, .5);
    }
  }
  col = mix(col, INK, e * .92);

  // the drawing sheet: margins, notes, dimensions, the title block
  vec4 ui = texture(u_ui, gl_FragCoord.xy / u_res);
  col = mix(col, ui.rgb, ui.a);

  if(any(isnan(col))) col = PAPER;
  fragColor = vec4(untone(col, gl_FragCoord.xy) * u_weight, 1.);
}
