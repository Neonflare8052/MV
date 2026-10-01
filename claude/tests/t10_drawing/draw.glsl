// ---- t10: drawn, not lit
uniform vec3 u_c; uniform float u_scale;

vec3 normal(vec3 p, float e){
  const vec2 k = vec2(1., -1.);
  return normalize(k.xyy * map(p + k.xyy * e) + k.yyx * map(p + k.yyx * e) + k.yxy * map(p + k.yxy * e) + k.xxx * map(p + k.xxx * e));
}

vec3 rayO(vec2 fc){
  vec2 uv = (fc - .5 * u_res) / u_res.y;
  return u_c + (uv.x * u_right + uv.y * u_up) * (2. * u_scale) - u_fwd * 300.;
}

// orthographic ray: hit distance (or -1), the part it hit
float trace(vec2 fc, out vec3 p, out float id, out int mat){
  vec3 ro = rayO(fc);
  float t = 200.;                                   // the machine lies within ~100 of the centre
  id = -1.; mat = 0; p = ro;
  for(int i = 0; i < 300; i++){
    p = ro + u_fwd * t;
    float d = map(p);
    if(d < .002){
      mat = MAT;
      float k = clamp(round(p.x / S), -2., 6.), j = clamp(round(p.y / P), -7., 7.);
      id = float(mat) * 1000. + (mat == 1 || mat == 2 ? k * 37. + j : (mat == 4 ? sign(p.y) : floor(p.x / S)));
      return t;
    }
    t += d * .8;
    if(t > 420.) break;
  }
  return -1.;
}

vec3 srgb(float r, float g, float b){ return vec3(r, g, b) / 255.; }

// the post chain applies a vignette, ACES and gamma: undo them so the paper prints as paper
vec3 untone(vec3 c, vec2 fc){
  vec3 L = pow(clamp(c, 0., .985), vec3(2.2));
  vec3 A = 2.51 - 2.43 * L, B = .03 - .59 * L, C = -.14 * L;
  vec3 y = (-B + sqrt(B * B - 4. * A * C)) / (2. * A);
  vec2 d = fc / u_res - .5;
  return y / 1.05 / (1. - .9 * dot(d, d));
}

void main(){
  float s1 = h11(u_time * 1731.7 + .13), s2 = h11(u_time * 911.3 + .71);
  vec2 fc = gl_FragCoord.xy + vec2(s1, s2) - .5;
  float px = u_res.y / 1080.;

  vec3 PAPER = srgb(240., 233., 218.), INK = srgb(30., 26., 22.);
  vec3 p; float id; int mat;
  float t = trace(fc, p, id, mat);

  // paper: a little fibre and tooth
  vec3 col = PAPER * (.975 + .035 * fbm(vec3(fc / px * .08, 1.)) + .012 * (h21(floor(fc)) - .5));

  vec3 n = vec3(0.);
  if(t > 0.){
    n = normal(p, .004);
    vec3 L = normalize(vec3(-.55, .8, -.45));         // drafting light: from the upper left, in front
    float lam = dot(n, L);
    vec3 wash = mat == 3 ? srgb(196., 204., 206.) : (mat == 4 ? srgb(186., 184., 176.) : srgb(226., 196., 138.));
    if(mat == 2) wash = mix(wash, srgb(200., 170., 120.), .5);
    col = mix(PAPER, wash, lam > .15 ? .28 : .6);
    if(n.y < -.6) col = mix(PAPER, wash * .8, .9);

    float ink = 0.;
    // shading lines along the axis of each cylinder: equal steps in angle, so they crowd toward the silhouette
    float k = clamp(round(p.x / S), -2., 6.);
    vec3 q = p - vec3(k * S, 0., 0.);
    if(abs(n.y) < .45 && (mat == 1 || mat == 3)){
      float phi = atan(q.z, q.x);
      float x = phi * (mat == 1 ? 96. : 20.) / (2. * PI);
      float fw = max(fwidth(x), 1e-4);
      float dark = clamp((.35 - lam) / .9, 0., 1.);
      float w = fw * (.3 + 1.5 * dark);
      float dd = abs(fract(x + .5) - .5);
      ink = max(ink, (1. - smoothstep(w - fw * .5, w + fw * .5, dd)) * step(.02, dark));
    }
    // undersides: close diagonal hatching
    if(n.y < -.6){
      float x = (fc.x + fc.y) / (5. * px);
      float dd = abs(fract(x) - .5) * 5.;
      ink = max(ink, 1. - smoothstep(.45, 1.1, dd));
    }
    // the digits on the rims, in ink
    if(mat == 1){
      float j = clamp(round(p.y / P), -7., 7.);
      vec3 w = q - vec3(0., j * P, 0.); w.xz = rot(wheelAngle(k, j)) * w.xz; w.y -= WY;
      if(length(w.xz) > R - .2) ink = max(ink, smoothstep(.35, .65, engrave(w)));
    }
    col = mix(col, INK, ink * .85);
  }

  // outlines: where depth, part or surface direction jumps between neighbouring samples
  float e = 0.;
  float o = 1.05 * px;
  vec2 offs[4] = vec2[4](vec2(o, 0.), vec2(-o, 0.), vec2(0., o), vec2(0., -o));
  for(int i = 0; i < 4; i++){
    vec3 p2; float id2; int m2;
    float t2 = trace(fc + offs[i], p2, id2, m2);
    if((t > 0.) != (t2 > 0.)) { e = 1.; continue; }
    if(t < 0.) continue;
    if(abs(t2 - t) > .3 || abs(id2 - id) > .5) e = max(e, t2 > t ? 1. : .8);
    else if(dot(n, normal(p2, .004)) < .75) e = max(e, .55);
  }
  float e2 = 0.;
  float o2 = 2.1 * px;
  vec2 offs2[4] = vec2[4](vec2(o2, 0.), vec2(-o2, 0.), vec2(0., o2), vec2(0., -o2));
  for(int i = 0; i < 4; i++){
    vec3 p2; float id2; int m2;
    float t2 = trace(fc + offs2[i], p2, id2, m2);
    if((t > 0.) != (t2 > 0.) || (t > 0. && t2 - t > 1.5)) e2 = 1.;
  }
  e = max(e * .75, e2);
  col = mix(col, INK, e * .92);

  // centre lines of the columns: thin dash-dot, drawn over everything
  vec2 uv = (fc - .5 * u_res) / u_res.y;
  for(int kk = -2; kk <= 6; kk++){
    vec3 A = vec3(float(kk) * S, 0., 0.) - u_c;
    float ax = dot(A, u_right) / (2. * u_scale);
    float dx = abs(uv.x - ax) * u_res.y / px;
    if(dx > 1.5) continue;
    float y0 = dot(A - vec3(0., 23.5, 0.), u_up) / (2. * u_scale), y1 = dot(A + vec3(0., 23.5, 0.), u_up) / (2. * u_scale);
    if(uv.y < y0 || uv.y > y1) continue;
    float s = fract((uv.y - y0) * u_res.y / px / 34.);
    float dash = step(s, .62) + step(.74, s) * step(s, .8);
    col = mix(col, srgb(120., 60., 50.), dash * (1. - smoothstep(.35, 1., dx)) * .7);
  }

  if(any(isnan(col))) col = PAPER;
  fragColor = vec4(untone(col, gl_FragCoord.xy) * u_weight, 1.);
}
