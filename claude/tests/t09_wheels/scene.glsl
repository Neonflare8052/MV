#version 330
// t09 · figure wheels.  Units: cm.  y up; the columns stand in a row along x.
uniform vec2 u_res; uniform float u_time, u_weight;
uniform vec3 u_ro, u_fwd, u_right, u_up;
uniform float u_tanh, u_focus, u_ap;
uniform sampler2D u_dig;
out vec4 fragColor;

const float PI = 3.14159265;
const float S = 14.;          // column spacing
const float P = 2.4;          // wheel pitch
const float R = 5.;           // figure wheel radius
const float H = .45;          // half thickness of the figure wheel
const float WY = .25;         // figure wheel centre above the cell centre
const float RG = 4.;        // gear radius
const vec3 LDIR = normalize(vec3(-1., .42, -.55));   // towards the key light
const vec3 LCOL = vec3(1., .69, .42) * 5.5;

// smoothstep that also accepts a > b (GLSL leaves that undefined)
float sst(float a, float b, float x){ float t = clamp((x - a) / (b - a), 0., 1.); return t * t * (3. - 2. * t); }
float h11(float p){ p = fract(p * .1031); p *= p + 33.33; p *= p + p; return fract(p); }
float h21(vec2 p){ vec3 p3 = fract(vec3(p.xyx) * .1031); p3 += dot(p3, p3.yzx + 33.33); return fract((p3.x + p3.y) * p3.z); }
float h31(vec3 p){ p = fract(p * .1031); p += dot(p, p.zyx + 31.32); return fract((p.x + p.y) * p.z); }
float vn(vec3 p){
  vec3 i = floor(p), f = fract(p); f = f * f * (3. - 2. * f);
  return mix(mix(mix(h31(i), h31(i + vec3(1,0,0)), f.x), mix(h31(i + vec3(0,1,0)), h31(i + vec3(1,1,0)), f.x), f.y),
             mix(mix(h31(i + vec3(0,0,1)), h31(i + vec3(1,0,1)), f.x), mix(h31(i + vec3(0,1,1)), h31(i + vec3(1,1,1)), f.x), f.y), f.z);
}
float fbm(vec3 p){ float a = .5, s = 0.; for(int i = 0; i < 4; i++){ s += a * vn(p); p = p * 2.03 + 7.1; a *= .5; } return s; }

float sdRCyl(vec3 p, float r, float h, float e){      // rounded cylinder about y
  vec2 d = vec2(length(p.xz) - r + e, abs(p.y) - h + e);
  return min(max(d.x, d.y), 0.) + length(max(d, 0.)) - e;
}
mat2 rot(float a){ float c = cos(a), s = sin(a); return mat2(c, -s, s, c); }

// the wheel's turn: whole digits, with a little play
float wheelAngle(float k, float j){ return (floor(h21(vec2(k, j) * 1.7 + .3) * 10.) + (h21(vec2(k, j) + 9.1) - .5) * .12) * (2. * PI / 10.); }

// engraved digit on the rim, in local wheel coords (w rotated, y relative to the wheel centre)
float engrave(vec3 w){
  float phi = atan(w.z, w.x);
  float s = (-phi / (2. * PI) + .5) * 10.;
  float v = w.y / (2. * H) + .5;
  if(v < 0. || v > 1.) return 0.;
  return textureLod(u_dig, vec2(s / 10., v), 0.).r;
}

int MAT;
float map(vec3 p){
  float k = clamp(round(p.x / S), -4., 9.);
  vec3 q = p - vec3(k * S, 0., 0.);
  float j = clamp(round(q.y / P), -14., 14.);
  vec3 w = q - vec3(0., j * P, 0.);
  w.xz = rot(wheelAngle(k, j)) * w.xz;

  // figure wheel: rounded disc, engraved rim, a raised hub
  vec3 fw = w - vec3(0., WY, 0.);
  float dF = sdRCyl(fw, R, H, .07);
  float rr = length(fw.xz);
  if(rr > R - .25 && abs(fw.y) < H) dF += .045 * engrave(fw);
  dF = min(dF, sdRCyl(fw - vec3(0., .06, 0.), 1.25, H + .06, .05));
  dF = max(dF, -(abs(rr - 3.3) - .05));                               // a turned groove on the face

  // gear under it: forty teeth
  vec3 gw = w - vec3(0., WY - H - .3, 0.);
  float th = atan(gw.z, gw.x);
  float tooth = clamp(cos(th * 48.) * 1.3, -1., 1.) * .11;
  float dG = max((length(gw.xz) - RG - tooth) * .7, abs(gw.y) - .24);

  // steel axle through the column
  float dA = length(q.xz) - .55;

  // frame pillars between the columns
  float kp = clamp(floor(p.x / S), -5., 9.);
  vec3 pp = p - vec3((kp + .5) * S, 0., 3.2);
  float dP = max(abs(pp.x), abs(pp.z)) - .45;

  // horizontal racks behind the columns, on every third gear level
  float jr = clamp(round((p.y - (WY - H - .3)) / (3. * P)), -5., 5.);
  vec3 rp = p - vec3(0., jr * 3. * P + WY - H - .3, RG + .55);
  float teeth = clamp(cos(rp.x * 2. * PI / (2. * PI * RG / 48.)) * 1.3, -1., 1.) * .09;
  float dR = max(abs(rp.y) - .22, abs(rp.z + teeth) - .32);
  dR = max(dR, abs(p.x - 30.) - 90.);

  float d = dF; MAT = 1;
  if(dR < d){ d = dR; MAT = 2; }
  if(dG < d){ d = dG; MAT = 2; }
  if(dA < d){ d = dA; MAT = 3; }
  if(dP < d){ d = dP; MAT = 3; }
  return d;
}

vec3 normal(vec3 p, float e){
  const vec2 k = vec2(1., -1.);
  return normalize(k.xyy * map(p + k.xyy * e) + k.yyx * map(p + k.yyx * e) + k.yxy * map(p + k.yxy * e) + k.xxx * map(p + k.xxx * e));
}

float shadow(vec3 ro, vec3 rd){
  float res = 1., t = .04;
  for(int i = 0; i < 64; i++){
    float h = map(ro + rd * t);
    res = min(res, 10. * h / t);
    t += clamp(h, .03, .8);
    if(res < .002 || t > 60.) break;
  }
  return clamp(res, 0., 1.);
}

float ao(vec3 p, vec3 n){
  float o = 0., s = 1.;
  for(int i = 1; i <= 5; i++){ float h = .08 + .22 * float(i); o += (h - map(p + n * h)) * s; s *= .7; }
  return clamp(1. - 1.2 * o, 0., 1.);
}

// the room, as the metal sees it: a warm window of light on the key side, dark elsewhere
vec3 env(vec3 r, float rough){
  // a black room with two lights in it: a hard-edged warm box on the key side, a thin cold strip high on the far side
  vec3 L = normalize(LDIR + vec3(0., .15, 0.));
  vec3 u = normalize(cross(L, vec3(0., 1., 0.))), v = cross(u, L);
  float z = dot(r, L);
  vec2 q = vec2(dot(r, u), dot(r, v)) / max(z, 1e-3);
  float soft = .02 + .5 * rough * rough;
  float box = z > 0. ? (sst(.95 + soft, .95 - soft, abs(q.x)) * sst(.3 + soft, .3 - soft, abs(q.y - .05))) : 0.;
  vec3 c = LCOL * .5 * box * (.75 + .25 * smoothstep(-.3, .3, q.y));
  vec3 S2 = normalize(vec3(.9, .55, -.1));
  float strip = sst(.03 + soft, 0., abs(dot(r, normalize(cross(S2, vec3(0., 0., 1.)))))) * smoothstep(.2, .7, dot(r, S2));
  c += vec3(.55, .65, .8) * .5 * strip;
  c += vec3(.012, .009, .007) * (.4 + .6 * r.y);
  c += LCOL * .035 * sst(.05, -.5, r.y) * (.6 + .4 * smoothstep(-1., 1., dot(r, u)));   // the lit floor, seen in the metal
  return c;
}

float D_GGX(float nh, float a){ float a2 = a * a; float d = nh * nh * (a2 - 1.) + 1.; return a2 / (PI * d * d); }
float G_S(float nv, float nl, float a){ float k = a * .5; return nl / (nl * (1. - k) + k) * nv / (nv * (1. - k) + k); }

void main(){
  // pixel and aperture jitter per subframe: antialiasing and depth of field
  float s1 = h11(u_time * 1731.7 + .13), s2 = h11(u_time * 911.3 + .71), s3 = h11(u_time * 377.9 + .37), s4 = h11(u_time * 2297.1 + .59);
  vec2 uv = (gl_FragCoord.xy + vec2(s1, s2) - .5 - .5 * u_res) / u_res.y;
  vec3 rd0 = normalize(u_fwd + 2. * u_tanh * (uv.x * u_right + uv.y * u_up));
  vec3 fp = u_ro + rd0 * (u_focus / dot(rd0, u_fwd));
  float ang = s3 * 2. * PI, rad = sqrt(s4) * u_ap;
  vec3 ro = u_ro + (cos(ang) * u_right + sin(ang) * u_up) * rad;
  vec3 rd = normalize(fp - ro);

  float t = 0.; bool hit = false;
  for(int i = 0; i < 260; i++){
    float d = map(ro + rd * t);
    if(d < .0015 * t){ hit = true; break; }
    t += d * .75;
    if(t > 260.) break;
  }

  vec3 fogc = vec3(.012, .009, .006);
  vec3 col = fogc;
  if(hit){
    vec3 p = ro + rd * t;
    map(p); int mat = MAT;
    vec3 n = normal(p, max(.002, .0008 * t));
    vec3 v = -rd;

    // material
    float k = clamp(round(p.x / S), -4., 9.);
    float j = clamp(round(p.y / P), -14., 14.);
    vec3 F0; float rough; float grime = 0.;
    float wear = fbm(p * .9 + vec3(k * 3.1, 0., 0.));
    if(mat == 3){
      F0 = vec3(.52, .52, .55) * (.75 + .3 * wear); rough = .32 + .2 * fbm(p * 3.);
    } else {
      F0 = vec3(.93, .66, .38) * (.72 + .35 * wear);                         // bronze, unevenly polished
      F0 = mix(F0, vec3(.35, .28, .18), smoothstep(.55, .8, fbm(p * 2.3 + 4.)) * .6);   // tarnish
      rough = .07 + .2 * pow(fbm(p * 1.7 + 2.), 2.) + (mat == 2 ? .16 : 0.);
      if(mat == 2) F0 *= .6;
      // turned (lathe) rings on the flat faces
      vec3 q = p - vec3(k * S, j * P, 0.);
      if(abs(n.y) > .9) rough += .06 * (.5 + .5 * sin(length(q.xz) * 260.));
      // the engraving holds dirt
      if(mat == 1){
        vec3 w = q; w.xz = rot(wheelAngle(k, j)) * w.xz; w.y -= WY;
        if(length(w.xz) > R - .25) grime = engrave(w);
      }
      F0 *= 1. - .75 * grime; rough = mix(rough, .75, grime);
    }
    rough = clamp(rough, .06, .9);
    float a = rough * rough;

    vec3 l = LDIR, hh = normalize(l + v);
    float nl = max(dot(n, l), 0.), nv = max(dot(n, v), 1e-3), nh = max(dot(n, hh), 0.), vh = max(dot(v, hh), 0.);
    vec3 F = F0 + (1. - F0) * pow(1. - vh, 5.);
    float sh = nl > 0. ? shadow(p + n * .01, l) : 0.;
    float band = dot(p, normalize(vec3(.55, 1., .2)));
    sh *= smoothstep(-4.5, -2.2, band - 1.) * (1. - smoothstep(1.2, 3.5, band - 1.)) * .95 + .05;
    vec3 spec = D_GGX(nh, a) * G_S(nv, nl, a) * F / (4. * nv + 1e-3) * nl;     // (nl cancels in the usual form)
    float occ = ao(p, n);
    vec3 r = reflect(rd, n);
    vec3 Fe = F0 + (max(vec3(1. - rough), F0) - F0) * pow(1. - nv, 5.);
    col = spec * LCOL * sh;
    col += env(r, rough) * Fe * occ * mix(.25, 1., shadow(p + n * .02, r) * .7 + .3);
    col += F0 * .08 * nl * sh * LCOL * .05 + vec3(.004, .003, .002) * occ * grime;
    col = mix(col, fogc, 1. - exp(-max(t - 12., 0.) * .018));
  }
  // light in the air, towards the key
  float ph = pow(max(dot(rd, LDIR), 0.), 6.);
  col += LCOL * .006 * ph * (1. - exp(-min(t, 120.) * .02)) + vec3(.0025, .0017, .001) * (1. - exp(-min(t, 120.) * .01));
  if(any(isnan(col)) || any(isinf(col))) col = vec3(0.);
  fragColor = vec4(col * u_weight, 1.);
}
