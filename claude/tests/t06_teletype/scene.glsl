#version 330
// t06 · the teletype (2:24.8–2:42.2)
// The ASCII eye was never on a screen: it was typed on paper. Twelve EXECUTIONs type twelve red lines
// (a staircase: line feeds without carriage return); the paper climbs over a roller to a small guillotine;
// six counts ratchet the blade up; it falls through the printed eye.
uniform vec2  u_res;
uniform float u_time, u_weight;
uniform float u_scene;          // 0 flat terminal, 1 teletype
uniform float u_bang;           // 0 random characters, 1 all '!'
uniform vec2  u_iris;           // iris offset (eye space)
uniform float u_gapA;           // gap direction of the iris
uniform float u_F;              // paper fed (m)
uniform float u_typed[12];      // characters typed on each EXECUTION line (0..9)
uniform float u_headX;          // type head x
uniform float u_strike;         // type head strike (0..1)
uniform float u_yb;             // blade bottom
uniform float u_cut, u_fall;
uniform vec3  u_cam, u_look;
uniform float u_fov;
uniform sampler2D u_glyphs, u_insc;
out vec4 fragColor;

#define PI 3.14159265
const float LH=.001136, CWD=.000833, X0=-.1;             // line height, char width, left margin
const float YP=.255, ZP=.0158, YR=.56, ZR=.035, RR=.0205;
const float CVERT=YR-YP;                              // paper length of the vertical run
const float CWRAP=CVERT+RR*PI*.5;
const float ZB=.3;                                    // blade plane
const float NG=42.;

float h12(vec2 p){ vec3 p3=fract(vec3(p.xyx)*.1031); p3+=dot(p3,p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }
float vn(vec2 p){ vec2 i=floor(p),f=fract(p); f=f*f*(3.-2.*f);
  return mix(mix(h12(i),h12(i+vec2(1,0)),f.x),mix(h12(i+vec2(0,1)),h12(i+vec2(1,1)),f.x),f.y); }
float sdBox(vec3 p, vec3 b){ vec3 q=abs(p)-b; return length(max(q,0.))+min(max(q.x,max(q.y,q.z)),0.); }
float sdRBox(vec3 p, vec3 b, float r){ return sdBox(p,b-r)-r; }
float sdCylX(vec3 p, float r, float h){ vec2 d=abs(vec2(length(p.yz),p.x))-vec2(r,h); return min(max(d.x,d.y),0.)+length(max(d,0.)); }
vec2 opU(vec2 a, vec2 b){ return a.x<b.x?a:b; }

// ---------------- the ASCII eye: a full field of characters, the eye made of density ----------------
const float COLS=240., ROWS=100.;
float LOD=0.;                                             // glyph mip level, set per pixel
float eyeDensity(float col, float row){
  vec2 p=vec2((col-(COLS-1.)*.5)/(COLS*.5),((ROWS-1.)*.5-row)/(ROWS*.5)*.57);   // eye space, width units
  float bg=.07+.05*h12(vec2(col,row)*.13);                 // the field outside the eye
  float al=.5*pow(max(1.-p.x*p.x,0.),.85);                 // almond
  float outline=1.-smoothstep(.0,.022,abs(abs(p.y)-al));
  if(abs(p.y)>al) return max(bg,outline*.9);
  float d=.22+.06*h12(vec2(col,row)*.31);                  // sclera
  vec2 q=p-u_iris; float r=length(q), a=atan(q.y,q.x);
  float gap=abs(mod(a-u_gapA+PI,2.*PI)-PI);
  float ring=(1.-smoothstep(.035,.055,abs(r-.27)))*step(radians(27.),gap);
  float pupil=1.-smoothstep(.12,.14,r);
  d=max(d,ring); d=max(d,pupil*.5); d=max(d,outline*.9);
  return clamp(d,0.,1.);
}
// glyph index + ink (x: glyph, y: ink 0..1, z: red)
vec3 glyphAt(float col, float row){
  if(col<0.||col>COLS-1.||row<0.||row>=ROWS) return vec3(0.);
  float d=eyeDensity(col,row);
  if(u_bang>.5) return vec3(10.,max(pow(d,2.4),.04),0.);
  float h=h12(vec2(col,row)+floor(u_time*15.)*.37);
  float g=clamp(floor(d*9.+(h-.5)*2.5),1.,9.);
  if(h>.86 && d>.15) g=19.+floor(h12(vec2(row,col)+floor(u_time*15.))*23.);
  return vec3(g,.12+.88*pow(d,1.2),0.);
}
float glyphMask(float g, vec2 f){                         // f in [0,1]^2, y up
  if(g<.5) return 0.;
  f=clamp(f,vec2(.02),vec2(.98));
  return textureLod(u_glyphs,vec2((g+f.x)/NG,f.y),LOD).r;
}

// ---------------- flat terminal (lead-in) ----------------
vec3 terminal(vec2 uv){
  vec2 cell=vec2(1.62/COLS,.92/ROWS);
  LOD=max(log2(48./(cell.x*u_res.y)),0.);
  vec2 g=(uv+vec2(.81,-.46))/cell*vec2(1.,-1.);
  float col=floor(g.x), row=floor(g.y);
  vec2 f=vec2(fract(g.x),1.-fract(g.y));
  vec3 gl=glyphAt(col,row);
  float m=glyphMask(gl.x,f);
  vec3 c=vec3(.9,.92,.9)*m*gl.y*(1.+.8*gl.y);
  c+=vec3(.012);
  return c;
}

// ---------------- 3D ----------------
vec3 pieceT(vec3 p){ float k=u_fall; p.z-=.5*k*k+.1*k; p.y+=1.3*k*k; return p; }

vec2 map(vec3 p){
  vec2 r=vec2(p.y,1.);                                                          // table
  r=opU(r,vec2(sdRBox(p-vec3(0.,.11,-.12),vec3(.3,.11,.22),.02),2.));           // body
  r=opU(r,vec2(sdRBox(p-vec3(0.,.2,-.2),vec3(.26,.04,.1),.02),2.));             // hood behind the platen
  // keyboard: a slanted deck with ceramic keys
  vec3 kp=p-vec3(0.,.19,.08); kp.yz=mat2(.96,.28,-.28,.96)*kp.yz;
  r=opU(r,vec2(sdRBox(kp,vec3(.2,.012,.05),.006),2.));
  vec3 kk=kp-vec3(0.,.016,0.); vec2 id=clamp(floor(kk.xz/.024+.5),vec2(-7.,-1.),vec2(7.,1.));
  kk.xz-=id*.024;
  r=opU(r,vec2(sdRBox(kk,vec3(.009,.006,.009),.003),7.));
  r=opU(r,vec2(sdCylX(p-vec3(0.,YP,ZP-.0358),.035,.14),9.));                   // platen (rubber)
  r=opU(r,vec2(min(sdCylX(p-vec3(-.155,YP,ZP-.0358),.022,.012),sdCylX(p-vec3(.155,YP,ZP-.0358),.022,.012)),3.));  // knobs
  r=opU(r,vec2(sdCylX(p-vec3(0.,.3,-.3),.06,.12),4.9));                          // paper roll behind
  // type head: a small copper cylinder that strikes the paper
  vec3 hp=p-vec3(u_headX,YP,ZP+.022-.012*u_strike);
  r=opU(r,vec2(length(vec2(length(hp.xy)-.0,hp.z))*0.+sdRBox(hp,vec3(.009,.011,.009),.004),3.));
  // paper: vertical run, wrap over the roller, horizontal run to the cutter
  float pv=sdBox(p-vec3(0.,(YP+YR)*.5,ZP),vec3(.108,(YR-YP)*.5,.0008));
  vec2 q=vec2(p.y-YR,p.z-ZR);
  float pw=max(max(abs(length(q)-RR)-.0008,abs(p.x)-.108),max(q.y*-1.,q.x));   // back-top quadrant
  float zEnd=u_cut>.5?ZB:.52;
  float ph=sdBox(p-vec3(0.,YR+RR,(ZR+zEnd)*.5),vec3(.108,.0008,(zEnd-ZR)*.5));
  r=opU(r,vec2(pv,4.)); r=opU(r,vec2(pw,4.2)); r=opU(r,vec2(ph,4.4));
  if(u_cut>.5){ vec3 pp=pieceT(p); r=opU(r,vec2(sdBox(pp-vec3(0.,YR+RR,(ZB+.52)*.5),vec3(.108,.0008,(.52-ZB)*.5)),4.6)); }
  r=opU(r,vec2(sdCylX(p-vec3(0.,YR,ZR),RR-.001,.125),3.));                       // copper roller
  // the board under the horizontal run, and its legs
  r=opU(r,vec2(sdBox(p-vec3(0.,YR+RR-.0045,.29),vec3(.14,.0035,.23)),6.));
  // the guillotine
  float yB=YR+RR;
  r=opU(r,vec2(min(sdBox(p-vec3(-.135,yB+.12,ZB),vec3(.008,.12,.01)),sdBox(p-vec3(.135,yB+.12,ZB),vec3(.008,.12,.01))),6.));
  r=opU(r,vec2(sdBox(p-vec3(0.,yB+.245,ZB),vec3(.15,.009,.012)),6.));
  // ratchet teeth on the right post
  vec3 tp=p-vec3(.135,yB+.12,ZB+.012); float saw=fract((tp.y+.12)/.02);
  r=opU(r,vec2(sdBox(tp,vec3(.006,.11,.003+.004*saw)),3.));
  vec3 bp=p-vec3(0.,u_yb,ZB);
  float blade=sdBox(bp-vec3(0.,.035,0.),vec3(.122,.035,.0018));
  blade=max(blade,-(bp.y-.022*(bp.x+.122)/.244));
  r=opU(r,vec2(blade,5.));
  r=opU(r,vec2(sdBox(p-vec3(0.,(u_yb+.07+yB+.245)*.5,ZB),vec3(.002,max((yB+.245-u_yb-.07)*.5,.001),.002)),6.));  // cord
  return r;
}
vec3 normal(vec3 p){ vec2 e=vec2(.0004,0.);
  return normalize(vec3(map(p+e.xyy).x-map(p-e.xyy).x,map(p+e.yxy).x-map(p-e.yxy).x,map(p+e.yyx).x-map(p-e.yyx).x)); }
float shadow(vec3 ro, vec3 rd){ float res=1., t=.003;
  for(int i=0;i<40;i++){ float h=map(ro+rd*t).x; res=min(res,10.*h/t); t+=clamp(h,.003,.06); if(res<.01||t>1.) break; }
  return clamp(res,0.,1.); }

// the twelve EXECUTION lines are typed at three times the pitch of the eye field
const float BIG=3.;
vec3 execGlyph(float x, float n, out vec2 f){
  float m=(n-(ROWS+4.))/6.;                                // one line + one blank line = 6 eye rows
  f=vec2(0.);
  if(m<0.) return vec3(0.);
  float i=floor(m); float fy=fract(m)*2.;
  if(i>11.||fy>=1.) return vec3(0.);
  float bc=(x-X0)/(CWD*BIG);
  float start=2.+3.*i;                                     // line feed without carriage return: a staircase
  float k=floor(bc-start);
  if(k<0.||k>8.||k>=u_typed[int(i)]) return vec3(0.);
  int ki=int(k);
  float g=ki==0||ki==2?11.:(ki==1?12.:(ki==3?13.:(ki==4?14.:(ki==5?15.:(ki==6?16.:(ki==7?17.:18.))))));
  f=vec2(fract(bc-start),1.-fy);
  return vec3(g,1.,1.);
}
vec3 paperInk(float x, float c){
  vec3 cream=vec3(.9,.87,.8);
  float n=(u_F-c)/LH;                                      // document coordinate, in eye rows
  float row=floor(n+.5), col=floor((x-X0)/CWD);
  vec3 gl; vec2 f;
  if(n<ROWS+2.){ gl=glyphAt(col,row); f=vec2(fract((x-X0)/CWD),1.-fract(n+.5)); }
  else { gl=execGlyph(x,n,f); LOD=max(LOD-log2(BIG),0.); }
  // a typewriter strike: slight jitter and uneven ink per character
  float jit=(h12(vec2(col,row)*1.7)-.5)*.06;
  float m=glyphMask(gl.x,vec2(f.x,f.y+jit));
  float ink=min(m*1.6,1.)*gl.y*(.8+.25*h12(vec2(row,col)));
  vec3 inkc=mix(vec3(.08,.07,.07),vec3(.62,.08,.06),gl.z);
  vec3 c0=mix(cream,inkc,clamp(ink,0.,1.));
  // tear line and pin-feed margins
  c0*=.95+.06*vn(vec2(x*800.,c*800.));
  return c0;
}

vec3 shade(vec3 p, vec3 rd, float m){
  vec3 n=normal(p);
  vec3 L1=normalize(vec3(-.25,.3,1.));
  vec3 alb=vec3(.1); float spec=.1, rough=32.;
  if(m<1.5){ alb=vec3(.07,.05,.035)*(.7+.5*vn(p.xz*vec2(8.,60.)));
  } else if(m<2.5){ alb=vec3(.04,.04,.045); spec=.3;
  } else if(m<3.5){ alb=vec3(.6,.38,.18); spec=.8; rough=48.;
  } else if(m<4.1){ alb=paperInk(p.x,p.y-YP);
  } else if(m<4.3){ vec2 q=vec2(p.y-YR,p.z-ZR); float th=atan(q.x,-q.y); alb=paperInk(p.x,CVERT+RR*clamp(th,0.,PI*.5));
  } else if(m<4.5){ alb=paperInk(p.x,CWRAP+(p.z-ZR));
  } else if(m<4.7){ vec3 pp=pieceT(p); alb=paperInk(pp.x,CWRAP+(pp.z-ZR));
  } else if(m<5.){ alb=vec3(.85,.82,.75);                         // the paper roll
  } else if(m<5.5){
    alb=vec3(.42,.44,.47)*(.85+.2*vn(vec2(p.x*400.,p.y*40.))); spec=1.3; rough=90.;
    vec3 bp=p-vec3(0.,u_yb,ZB);
    if(n.z>.5){
      vec2 uv=vec2((bp.x+.115)/.23,(bp.y-.036)/.03);
      if(uv.x>0.&&uv.x<1.&&uv.y>0.&&uv.y<1.){
        float v=1.-(5400.+(1.-uv.y)*150.)/5550.;
        alb=mix(alb,vec3(.07),smoothstep(.3,.7,texture(u_insc,vec2(uv.x,v)).r)*.85);
      }
      float edge=bp.y-.022*(bp.x+.122)/.244;
      alb=mix(alb,vec3(.78,.8,.83),1.-smoothstep(0.,.005,edge));
    }
  } else if(m<6.5){ alb=vec3(.03); spec=.2;
  } else if(m<7.5){ alb=vec3(.85,.84,.8); spec=.5;                // ceramic keys
  } else { alb=vec3(.02); spec=.3; }
  float pool=exp(-dot(p.xz-vec2(0.,.12),p.xz-vec2(0.,.12))*3.)*(.55+.45*smoothstep(0.,.45,p.y));
  float sh=shadow(p+n*.0015,L1);
  float dif=max(dot(n,L1),0.);
  vec3 col=alb*(vec3(1.,.93,.82)*1.1*dif*sh*pool+vec3(.25,.3,.4)*.05);
  col+=vec3(1.,.95,.9)*spec*pow(max(dot(n,normalize(L1-rd)),0.),rough)*sh*dif*pool*.6;
  return col;
}

void main(){
  vec2 uv=(gl_FragCoord.xy-.5*u_res)/u_res.y;
  vec3 col;
  if(u_scene<.5){ col=terminal(uv); }
  else {
    vec3 fw=normalize(u_look-u_cam), rt=normalize(cross(fw,vec3(0,1,0))), up=cross(rt,fw);
    vec3 rd=normalize(fw+(uv.x*rt+uv.y*up)*2.*tan(u_fov*.5));
    vec3 ro=u_cam; float t=0.; vec2 h;
    for(int i=0;i<220;i++){ h=map(ro+rd*t); if(h.x<.00008+t*.0002||t>4.) break; t+=h.x*.9; }
    col=vec3(.004);
    if(t<4.){ LOD=max(log2((t*2.*tan(u_fov*.5)/u_res.y)/(CWD/48.)),0.); col=shade(ro+rd*t,rd,h.y); col*=exp(-t*t*.25); }
  }
  fragColor=vec4(col*u_weight,1.);
}
