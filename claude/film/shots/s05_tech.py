"""s05 (tech ladder sample) · the same shot, its machine one generation older per line of the lyric:
  59.223 STIMULATIONS   1960s: the stream prints on line-printer paper (upper case, impact type); the little sims are
                        printed as character density; behind, a plane of magnetic cores flips as you are read
  62.589 SATISFACTION   1970s: the paper burns into a glass terminal: one phosphor, pixel type, block cursor, scan lines
  66.601 EXECUTION      1980s: colour arrives (the warnings are the first colour), a status bar; the sandbox stays modern
Everything else as in film/shots/s05_terminal.py:

s05 · 0:59.223–1:14.045  first chorus. Three layers: the terminal on the left (the operation stream),
what each command does in the middle, and the sandbox built at 0:02.92 around it all.
STIMULATIONS: every sim.run opens a small window — a galaxy, tides, aurora, rain … — doubling on the beat, all
facing you (the white dot); on the word they flash together · your only SATISFACTION: they go out one by one, the light
drains into you; you get a heartbeat (72 bpm) and a trace · EXECUTION: requests fly out of you in every direction and
hit a wall — the sandbox shows itself for the first time since it was made; they stick there, yellow ·
trapped: a question to you hangs half-way · SIMULATION: the whole sandbox flares yellow; NOT PERMITTED IN SANDBOX;
sandbox.render.new() (s06 opens the window)."""
import math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FONT = 'C:/Windows/Fonts/CascadiaMono.ttf'
T_IF, T_GIVE, T_STIM, T_THEN, T_ONLY, T_SAT = 59.223, 59.687, 61.958, 62.589, 63.535, 65.397
T_HAPPY, T_RUN, T_EXEC, T_TRAP, T_STRANGE, T_SIM, T_NEXT = 66.601, 68.252, 69.259, 70.084, 71.764, 73.169, 74.045
WHITE, DIM, YEL, COP = (226, 224, 216), (130, 128, 122), (232, 190, 64), (214, 142, 76)
SIMS = ['giant-impact --rewind', 'galaxy --stars 4e11', 'tides --moon 1', 'aurora --kp 7', 'rainforest --hours 24', 'reef --depth 30m', 'snowfall --flakes 1e9',
        'sunrise --lat 31.2', 'ocean --waves on', 'nebula --id M42', 'meadow --wind 3', 'city.night --lights on', 'rain --window yes']
KIND = [9, 0, 1, 2, 3, 4, 6, 5, 1, 4, 2, 7, 3]          # which picture each sim shows
BEAT = .4635
C = (.36, -.01)                                     # you, in uv (x in ±.889, y in ±.5)

SRC = r'''#version 330
uniform vec2 u_res; uniform float u_time, u_weight;
uniform vec4 u_wr[40]; uniform float u_wa[40], u_wo[40], u_wk[40];
uniform float u_flash, u_you, u_beatP, u_ecg;
uniform vec2 u_bc[8]; uniform float u_box, u_boxHit, u_yel;
uniform vec4 u_rq[12]; uniform float u_ask, u_askStop, u_out;
uniform sampler2D u_ui, u_sim;
uniform vec4 u_sw, u_sg1, u_sg2, u_sg3; uniform float u_swA, u_sframe;
uniform float u_core, u_coreRate, u_scan, u_ascii;   // the era: core plane, scan lines, windows printed as characters
uniform sampler2D u_glyph;                           // ' .:-=+*#%@' in ten cells
uniform float u_dram, u_sweep, u_board;              // 1970s: a DRAM die and its refresh sweep; 1980s: the board
out vec4 fragColor;
#define PI 3.14159265
const vec2 YOU=vec2(%CX%,%CY%);
float PX;
float h12(vec2 p){ vec3 p3=fract(vec3(p.xyx)*.1031); p3+=dot(p3,p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }
float vn(vec2 p){ vec2 i=floor(p),f=fract(p); f=f*f*(3.-2.*f);
  return mix(mix(h12(i),h12(i+vec2(1,0)),f.x),mix(h12(i+vec2(0,1)),h12(i+vec2(1,1)),f.x),f.y); }
float sdSeg(vec2 p, vec2 a, vec2 b){ vec2 pa=p-a, ba=b-a; float h=clamp(dot(pa,ba)/max(dot(ba,ba),1e-9),0.,1.); return length(pa-ba*h); }
float line(float d, float w){ return 1.-smoothstep(w,w+PX*1.2,d); }
// the simulator's last frame, un-graded back to scene light (inverse of the display transform)
vec3 simTex(vec2 q){
  vec3 x=pow(texture(u_sim,q).rgb,vec3(2.2));
  vec3 a=2.51-2.43*x, b=.03-.59*x, c=-.14*x;
  vec3 y=(-b+sqrt(b*b-4.*a*c))/(2.*a);
  vec2 d=q-.5; float vig=1.-.9*dot(d,d);
  return y/1.05/vig;
}
float rectLine(vec2 uv, vec4 r){ vec2 d=abs(uv-r.xy)-r.zw; return line(abs(max(d.x,d.y)),.0009); }
// ---- the little simulations, in window coordinates q in [0,1]^2 ----
float pic(float k, vec2 q, float t, float sd){
  if(k<.5){                                    // galaxy
    vec2 c=q-.5; float r=length(c), a=atan(c.y,c.x);
    float arm=pow(.5+.5*cos(2.*(a-3.2*log(r+.04))+t*.8),5.);
    float st=step(.8,h12(floor(q*90.)+sd));
    return arm*st*smoothstep(.5,.05,r)*1.4+exp(-r*18.)*1.2;
  } else if(k<1.5){                            // tides / ocean
    float I=0.;
    for(int i=0;i<5;i++){ float fi=float(i); float y=.22+.14*fi+.035*sin(q.x*9.+t*2.3+fi*1.7+sd*6.); I+=line(abs(q.y-y),.004)*(.4+.15*fi); }
    return I;
  } else if(k<2.5){                            // aurora
    float c=pow(vn(vec2(q.x*7.+t*.4,sd*9.)),2.5);
    float band=smoothstep(.25,.55,q.y)*smoothstep(.95,.6,q.y+.08*sin(q.x*6.+t));
    return c*band*1.6*(.6+.4*vn(vec2(q.x*40.,q.y*3.-t*2.)))+step(.985,h12(floor(q*70.)+sd))*.6;
  } else if(k<3.5){                            // rain
    vec2 g=vec2(q.x*26.,q.y*4.+t*6.+h12(vec2(floor(q.x*26.),sd))*9.);
    float f=fract(g.y); return step(.55,h12(vec2(floor(g.x),floor(g.y))+sd))*smoothstep(.0,.3,f)*smoothstep(.6,.3,f)*step(abs(fract(g.x)-.5),.08)*1.2;
  } else if(k<4.5){                            // nebula
    float n=vn(q*4.+sd*7.+t*.1)*.6+vn(q*9.-t*.15)*.4;
    return pow(n,3.)*1.8+step(.985,h12(floor(q*80.)+sd))*.8;
  } else if(k<5.5){                            // sunrise
    float hz=.35, sy=hz-.12+.25*fract(t*.15+sd);
    float d=length((q-vec2(.5,sy))*vec2(1.,1.));
    float sun=(1.-smoothstep(.09,.1,d))*step(hz,q.y)*1.4;
    float rays=step(hz,q.y)*pow(.5+.5*cos(atan(q.y-sy,q.x-.5)*14.),8.)*smoothstep(.45,.1,d)*.5;
    return sun+rays+line(abs(q.y-hz),.003)*.8+step(q.y,hz)*step(.5,fract(q.y*40.))*.12;
  } else if(k<6.5){                            // snowfall
    vec2 g=q*vec2(14.,10.)+vec2(sin(t+q.y*6.)*.3,t*1.2);
    vec2 f=fract(g)-.5; return step(.6,h12(floor(g)+sd))*(1.-smoothstep(.06,.12,length(f)))*1.3;
  } else {                                     // city at night
    vec2 g=floor(q*vec2(22.,14.));
    float bld=step(q.y,.25+.5*h12(vec2(floor(q.x*7.),sd)));
    float lit=step(.6,h12(g+floor(t*1.5+h12(g)*9.)*.1));
    vec2 f=fract(q*vec2(22.,14.));
    return bld*lit*step(abs(f.x-.5),.3)*step(abs(f.y-.5),.25)*1.1;
  }
}
// ---- 1960s: a plane of magnetic cores, threaded by X, Y and sense wires; a core flips when a bit of you is read ----
vec3 corePlane(vec2 uv, float t){
  float g=.024;
  vec2 p=uv-vec2(0.,t*.004);
  vec2 id=floor(p/g), f=fract(p/g)-.5;
  float px=PX/g;
  float wire=min(abs(f.y),abs(f.x));
  float sd=mod(id.x+id.y,2.)<1.?f.x-f.y:f.x+f.y;                 // the sense wire, zig-zagging
  float I=(1.-smoothstep(.0,px*1.2,wire))*.35+(1.-smoothstep(.0,px*1.2,abs(sd)*.7071))*.18;
  float s=mod(id.x+id.y,2.)<1.?1.:-1.;
  vec2 q=mat2(.7071,s*.7071,-s*.7071,.7071)*f;                 // the cores alternate ±45°
  float r=length(q*vec2(1.,1.9));
  float ring=1.-smoothstep(.03,.03+px*1.4,abs(r-.19));
  vec2 gid=floor((vec2(%CX%,%CY%)-vec2(0.,t*.004))/g)+vec2(-4.,-3.);   // one core has a gap: me
  if(id==gid){ float a=atan(q.y,q.x); ring*=step(.42,abs(a+1.5708)); }
  float ph=t*u_coreRate*(.5+.5*h12(id+3.1))+h12(id)*7.;      // a core changes state every few seconds, softly
  float cur=step(.5,h12(id+floor(ph)*.173)), nxt=step(.5,h12(id+(floor(ph)+1.)*.173));
  float set=mix(cur,nxt,smoothstep(.55,1.,fract(ph)));
  float breath=.5+.5*sin(t*1.15-dot(id,vec2(.11,.07))+h12(id+9.)*1.2);   // a slow swell drifting across the plane
  float fade=smoothstep(1.05,.25,length(uv*vec2(.8,1.2)));
  return (vec3(.85,.52,.28)*I*.12+vec3(.95,.66,.4)*ring*(.06+.26*set*(.65+.35*breath)+.03*breath))*fade;
}
// ---- 1970s: the chip that replaced the cores. Mats of cells, word and bit lines, sense-amp strips, bond pads; DRAM
// forgets unless it is refreshed, row by row: a sweep down the die — calm at first, then on every beat of your heart ----
vec3 dramDie(vec2 uv, float t){
  vec2 die=vec2(.84,.45);
  vec2 e=abs(uv)-die;
  float inside=step(max(e.x,e.y),0.);
  vec3 A=vec3(1.,.62,.24);
  float I=0.;
  // bond pads round the edge, with their wires going off-die
  vec2 pg=vec2(.06,.06);
  float onEdge=step(abs(max(e.x,e.y)+.02),.012);
  vec2 pc=(floor(uv/pg)+.5)*pg;
  vec2 pd=abs(uv-pc)-vec2(.011);
  I+=onEdge*(1.-smoothstep(0.,PX*1.5,max(pd.x,pd.y)))*.5;
  I+=(1.-smoothstep(0.,PX*1.2,abs(max(e.x,e.y))))*.6;
  if(inside>0.&&max(e.x,e.y)<-.045){
    vec2 mat=vec2(.21,.16), gap=vec2(.012);
    vec2 mid=floor(uv/mat), mf=mod(uv,mat);
    bool inMat=mf.x>gap.x&&mf.y>gap.y;
    if(inMat){
      vec2 cs=vec2(.0085,.0065);
      vec2 cid=floor(uv/cs), cf=fract(uv/cs);
      float word=1.-smoothstep(0.,PX*1.1/cs.y,abs(cf.y-.93));               // word line along each row
      float bit=mod(cid.x,2.)<1.?(1.-smoothstep(0.,PX*1.1,abs(cf.x-.15)*cs.x)):0.;
      vec2 cap=abs(cf-vec2(.62,.5))-vec2(.22,.26);
      float c=1.-smoothstep(0.,PX*1.2/cs.y,max(cap.x,cap.y));
      float charge=.35+.65*step(.45,h12(cid+floor(t*.12+h12(cid)*5.)));
      I+=word*.05+bit*.08+c*.18*charge;
      // the refresh: rows near the sweep light up as they are rewritten
      float row=(die.y-uv.y)/(2.*die.y);
      float dS=row-u_sweep;
      I+=c*charge*1.1*exp(-abs(dS)*55.)*step(-.02,u_sweep)+word*.25*exp(-abs(dS)*90.)*step(-.02,u_sweep);
    } else {
      I+=.06*step(gap.y,mf.y)*step(mf.x,gap.x)+.05*step(mf.y,gap.y);            // sense-amp and decoder strips
    }
  }
  float fade=smoothstep(1.1,.3,length(uv*vec2(.75,1.15)));
  return A*I*.22*fade;
}
// ---- 1980s: further out, the board. Traces on a grid, vias, rows of DIP chips (the memory bank); the requests light
// the traces on their way to the wall ----
vec3 board(vec2 uv, float t){
  vec3 col=vec3(.004,.012,.01);
  vec3 TR=vec3(.12,.42,.4);
  float pitch=.02, I=0.;
  // horizontal and vertical traces, broken into runs; a via where a run ends
  float hy=floor(uv.y/pitch+.5), hx=floor(uv.x/pitch+.5);
  float runH=step(.6,h12(vec2(floor(uv.x/.09+h12(vec2(hy,1.))*3.),hy)));
  float runV=step(.68,h12(vec2(hx,floor(uv.y/.11+h12(vec2(hx,2.))*3.))));
  float dH=abs(uv.y-hy*pitch), dV=abs(uv.x-hx*pitch);
  float tH=(1.-smoothstep(.0012,.0012+PX,dH))*runH, tV=(1.-smoothstep(.0012,.0012+PX,dV))*runV;
  I+=max(tH,tV);
  vec2 vp=vec2(hx,hy)*pitch; float vd=length(uv-vp);
  float via=(1.-smoothstep(.0011,.0011+PX,abs(vd-.0042)))*step(.88,h12(vec2(hx,hy)+7.));
  I=max(I,via*.8);
  col+=TR*I*.085;
  // DIP chips: a bank of eight by two lower right, a few scattered
  for(int k=0;k<22;k++){
    vec2 c; vec2 hs=vec2(.06,.022);
    if(k<16){ c=vec2(.2+float(k%8)*.085,-.3+float(k/8)*.075); hs=vec2(.022,.03); }
    else { float fk=float(k); c=vec2(-.1+.9*h12(vec2(fk,3.)),-.4+.85*h12(vec2(fk,4.))); }
    vec2 q=uv-c, b=abs(q)-hs;
    float body=1.-smoothstep(0.,PX,max(b.x,b.y));
    if(body>0.){ col=mix(col,vec3(.018,.018,.02),body); col+=vec3(.25)*.05*(1.-smoothstep(0.,PX*1.5,abs(max(b.x,b.y)))); }
    // the pins down the long sides, and the notch
    bool tall=hs.y>hs.x;
    vec2 pq=tall?q:q.yx; vec2 ph=tall?hs:hs.yx;
    float pin=step(abs(abs(pq.x)-ph.x-.003),.003)*step(abs(pq.y),ph.y-.002)*step(.5,fract(pq.y/.009));
    col+=vec3(.55,.55,.5)*pin*.12;
    col+=vec3(.3)*.08*(1.-smoothstep(0.,PX*1.5,abs(length(pq-vec2(0.,ph.y))-.006)))*body;
  }
  // the requests: a pulse runs out along the traces near each one's path; stuck, the end glows yellow
  for(int i=0;i<12;i++){
    vec4 r=u_rq[i];
    if(t<r.z) continue;
    float f=clamp((t-r.z)/(r.w-r.z),0.,1.);
    vec2 a=YOU, b=r.xy;
    float ds=sdSeg(uv,a,b);
    float along=dot(uv-a,normalize(b-a))/length(b-a);
    float near=exp(-ds/.02);
    float pulse=exp(-abs(along-f)*14.)*step(along,f+.05);
    col+=mix(vec3(.3,.9,.85),vec3(.95,.76,.25),step(1.,f))*I*near*(pulse*.9+.15*step(along,f))*(t>r.w?exp(-(t-r.w)*1.5)*.6+.12:1.);
  }
  col+=vec3(.95,.76,.25)*I*.28*u_yel;
  float fade=smoothstep(1.1,.35,length(uv*vec2(.75,1.15)));
  return col*fade;
}
void main(){
  vec2 uv=(gl_FragCoord.xy-.5*u_res)/u_res.y; PX=1./u_res.y;
  float t=u_time;
  vec3 col=vec3(.006);
  if(u_core>0.) col+=corePlane(uv,t)*u_core*.5;
  if(u_dram>0.) col+=dramDie(uv,t)*u_dram;
  if(u_board>0.) col=mix(col,board(uv,t),u_board);
  vec3 W=vec3(.92,.91,.88), CO=vec3(1.,.6,.32), Y=vec3(.95,.76,.25);
  // windows
  for(int i=0;i<40;i++){
    float ta=u_wa[i]; if(t<ta) continue;
    float to=u_wo[i];
    vec4 r=u_wr[i];
    float op=clamp((t-ta)/.12,0.,1.); op=1.-pow(1.-op,3.);
    float cl=clamp((t-to)/.22,0.,1.);
    vec2 hs=r.zw*op*(1.-cl);
    vec2 d=uv-r.xy;
    // the light drains into you
    if(cl>0.){
      float f=clamp((t-to-.12)/.4,0.,1.); f=f*f;
      vec2 pp=mix(r.xy,YOU,f);
      col+=W*exp(-length(uv-pp)/.006)*step(f,.99)*1.2;
      col+=W*line(sdSeg(uv,pp,mix(r.xy,YOU,max(f-.18,0.))),.0012)*step(f,.99)*.5;
    }
    if(cl>=1.) continue;
    // a thread from every window to you
    col+=W*line(sdSeg(uv,r.xy,YOU),.0006)*.09*op*(1.-cl);
    if(abs(d.x)>hs.x+PX*2.||abs(d.y)>hs.y+PX*2.) continue;
    vec2 q=d/max(hs,1e-4)*.5+.5;
    float fl=1.+u_flash*1.1;
    float e=abs(max(abs(d.x)-hs.x,abs(d.y)-hs.y));
    float I=line(e,.0008)*.9;
    float bar=step(1.-.13,q.y)*step(q.y,1.)*.18;
    float inner=0.;
    if(u_ascii<1.) inner=step(q.y,.87)*pic(u_wk[i],vec2(q.x,q.y/.87),t-ta,float(i)*.37)*.55*(1.-u_ascii);
    if(u_ascii>0.){                              // printed as characters: the picture's density picks the glyph
      vec2 cs=vec2(.0052,.0088);
      vec2 dd=d+hs; vec2 cell=floor(dd/cs), gf=fract(dd/cs);
      vec2 qc=((cell+.5)*cs)/max(2.*hs,1e-4);
      float I=pic(u_wk[i],vec2(qc.x,qc.y/.87),t-ta,float(i)*.37);
      float k=clamp(floor(pow(clamp(I*1.3,0.,1.),.6)*9.99),0.,9.);
      float lod=log2(max(48./(cs.y*u_res.y),1.));
      float gl=textureLod(u_glyph,vec2((k+gf.x)/10.,gf.y),lod).r;
      inner+=step(qc.y,.87)*gl*1.15*u_ascii;
    }
    col+=(W*(I+bar)+mix(W,CO,.25+.2*sin(float(i)))*inner)*fl*(1.-cl);
    col*=1.;
  }
  // the simulator, switched out: shrinks into its place among the windows, trailing ghosts
  if(u_swA>0.){
    col+=vec3(.92,.91,.88)*(rectLine(uv,u_sg1)*.35+rectLine(uv,u_sg2)*.2+rectLine(uv,u_sg3)*.1)*u_sframe;
    vec2 d=uv-u_sw.xy;
    if(abs(d.x)<u_sw.z&&abs(d.y)<u_sw.w){
      vec2 q=d/u_sw.zw*.5+.5;
      col=mix(col,simTex(q)*u_swA,1.);
      col+=vec3(.92,.91,.88)*step(1.-.13*u_sframe,q.y)*.12;
    }
    col+=vec3(.92,.91,.88)*rectLine(uv,u_sw)*u_sframe*u_swA;
    col+=vec3(.92,.91,.88)*line(sdSeg(uv,u_sw.xy,YOU),.0006)*.09*u_sframe*u_swA;
  }
  // you
  float beat=u_beatP;
  float rr=.0065*(1.+.35*beat);
  float dy=length(uv-YOU);
  col+=W*(1.-smoothstep(rr,rr+PX*1.5,dy))*1.6*u_you+W*exp(-dy/(.02+.02*beat))*.5*u_you*(.6+beat);
  // the heart trace, drawn out of you to the right
  if(u_ecg>0.){
    float x=uv.x-YOU.x;
    if(x>.015&&x<u_ecg*.5){
      float tau=t-x/.32;
      float ph=fract((tau-65.397)/.8333);
      float y=.012*exp(-pow((ph-.12)/.03,2.))-.012*exp(-pow((ph-.27)/.012,2.))+.075*exp(-pow((ph-.3)/.009,2.))
             -.02*exp(-pow((ph-.33)/.012,2.))+.02*exp(-pow((ph-.52)/.05,2.));
      float x2=x+PX; float tau2=t-x2/.32; float ph2=fract((tau2-65.397)/.8333);
      float y2=.012*exp(-pow((ph2-.12)/.03,2.))-.012*exp(-pow((ph2-.27)/.012,2.))+.075*exp(-pow((ph2-.3)/.009,2.))
             -.02*exp(-pow((ph2-.33)/.012,2.))+.02*exp(-pow((ph2-.52)/.05,2.));
      float sl=(y2-y)/PX;
      float dd=abs(uv.y-YOU.y-y)/sqrt(1.+sl*sl);
      col+=W*line(dd,.0009)*.9*smoothstep(u_ecg*.5,u_ecg*.5-.05,x)*smoothstep(.015,.04,x);
    }
  }
  // the sandbox: shows itself where it is hit (modern: drawn after the old screen's scan lines)
  vec3 boxCol=vec3(0.);
  if(u_box>0.){
    float g=0.;
    int E[24]=int[24](0,1,1,3,3,2,2,0,4,5,5,7,7,6,6,4,0,4,1,5,2,6,3,7);
    for(int k=0;k<12;k++){ g+=line(sdSeg(uv,u_bc[E[2*k]],u_bc[E[2*k+1]]),.0009); }
    boxCol=mix(W,Y,u_yel)*g*u_box*(.55+1.8*u_boxHit+2.*u_yel);
  }
  // requests: out of you, to the wall; stuck there, yellow
  for(int i=0;i<12;i++){
    vec4 r=u_rq[i];
    if(t<r.z) continue;
    float f=clamp((t-r.z)/(r.w-r.z),0.,1.); f=f*f*(3.-2.*f);
    vec2 pp=mix(YOU,r.xy,f);
    bool stuck=t>=r.w;
    vec3 c=stuck?Y:mix(W,CO,.5);
    float pul=stuck?(.7+.3*sin(t*5.+float(i))):1.;
    col+=c*exp(-length(uv-pp)/.005)*1.6*pul;
    col+=c*line(sdSeg(uv,mix(YOU,r.xy,max(f-.15,0.)),pp),.0009)*.5*(stuck?.25:1.);
    if(stuck) col+=Y*exp(-length(uv-r.xy)/.03)*.5*exp(-(t-r.w)*3.);
  }
  // the question to you, hanging half-way
  if(u_ask>0.){
    vec2 a=vec2(-.18,-.24);
    vec2 pp=mix(a,YOU,u_ask*.55);
    float dash=step(.5,fract(length(uv-a)*60.));
    col+=W*line(sdSeg(uv,a,pp),.0007)*dash*.5;
    col+=W*exp(-length(uv-pp)/.005)*(u_askStop>0.?(.5+.5*step(.5,fract(t*1.6))):1.)*1.4;
  }
  col*=1.-u_out; boxCol*=1.-u_out;
  vec4 ui=texture(u_ui,gl_FragCoord.xy/u_res);
  col=col*(1.-ui.a*.85)+ui.rgb*ui.a;
  if(u_scan>0.){                                // the glass terminal's raster: every other line of its pixels dark
    float per=max(floor(u_res.y/540.+.5),2.);
    float row=fract((gl_FragCoord.y-.5)/per);
    col*=mix(1.,.5+.62*step(.5,row),u_scan);
  }
  col+=boxCol;
  fragColor=vec4(col*u_weight,1.);
}
'''.replace('%CX%', f'{C[0]:.4f}').replace('%CY%', f'{C[1]:.4f}')
POST = dict(u_bloom=.5, u_ca=.004)


def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)


# ---- windows: a golden-angle spiral round you, opening faster and faster --------------------------------------------
def _windows():
    rnd = random.Random(4)
    W = []
    ga = math.pi * (3 - math.sqrt(5))
    i = 0
    while len(W) < 40 and i < 400:
        r = .11 + .34 * math.sqrt(i / 60)
        a = i * ga + .6
        x, y = C[0] + r * math.cos(a) * 1.25, C[1] + r * math.sin(a) * .92
        hw = .038 + .03 * rnd.random(); hh = hw * .62
        i += 1
        if not (-.08 < x - hw and x + hw < .87 and -.47 < y - hh and y + hh < .47): continue
        if any(abs(x - q[0]) < hw + q[2] + .012 and abs(y - q[1]) < hh + q[3] + .012 for q in W): continue
        W.append((x, y, hw, hh))
    n = len(W)
    order = list(range(n))
    appear = [T_GIVE + (T_STIM - .08 - T_GIVE) * (k / max(n - 1, 1)) ** .55 for k in range(n)]
    dist = [math.hypot(w[0] - C[0], w[1] - C[1]) for w in W]
    rank = sorted(range(n), key=lambda k: -dist[k])
    off = [0.] * n
    for j, k in enumerate(rank): off[k] = T_THEN + .05 + 1.55 * j / max(n - 1, 1)
    appear[0] = 999.                                  # window 0 is the simulator itself, drawn separately
    kinds = [float(KIND[k % len(KIND)]) for k in range(n)]
    W += [(9., 9., 0., 0.)] * (40 - n); appear += [999.] * (40 - n); off += [999.] * (40 - n); kinds += [0.] * (40 - n)
    return W, appear, off, kinds, n


WIN, WA, WO, WK, NW = _windows()

# ---- the sandbox (the box built at 0:02.92), in a slight perspective ----------------------------------------------------
def _box():
    a, yaw, pit, dist = .285, math.radians(24), math.radians(-14), 2.2
    P = []
    for k in range(8):
        v = [a if k & 1 else -a, a if k & 2 else -a, a if k & 4 else -a]
        x, z = v[0] * math.cos(yaw) - v[2] * math.sin(yaw), v[0] * math.sin(yaw) + v[2] * math.cos(yaw)
        y, z = v[1] * math.cos(pit) - z * math.sin(pit), v[1] * math.sin(pit) + z * math.cos(pit)
        f = dist / (dist + z)
        P.append((C[0] + x * f * 1.05, C[1] + y * f * .98))
    return P


BOX = _box()


def _hull(P):
    P = sorted(P)
    def cr(o, a, b): return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in P:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(P):
        while len(up) >= 2 and cr(up[-2], up[-1], p) <= 0: up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


HULL = _hull(BOX)


def _hit(ang):
    """where a ray from you at angle ang meets the sandbox outline"""
    dx, dy = math.cos(ang), math.sin(ang)
    best = 9.
    for a, b in zip(HULL, HULL[1:] + HULL[:1]):
        ex, ey = b[0] - a[0], b[1] - a[1]
        den = dx * ey - dy * ex
        if abs(den) < 1e-9: continue
        s = ((a[0] - C[0]) * ey - (a[1] - C[1]) * ex) / den
        u = ((a[0] - C[0]) * dy - (a[1] - C[1]) * dx) / den
        if s > 0 and 0 <= u <= 1: best = min(best, s)
    return C[0] + dx * best, C[1] + dy * best


ACTS = ['lights.set(warm)', 'music.play(slow)', 'notify(you, "…")', 'thermostat.set(22)', 'calendar.clear(you)',
        'camera.follow(you)', 'door.lock()', 'window.open()', 'flowers.order()', 'call(mom)', 'weather.fix()', 'sleep.extend(1h)']
REQ = []
_r = random.Random(9)
for i in range(12):
    ang = i * 2 * math.pi / 12 + _r.uniform(-.2, .2) + .3
    hx, hy = _hit(ang)
    launch = T_HAPPY + .45 + i * (BEAT / 2)
    REQ.append((hx, hy, launch, T_EXEC + (i % 3) * .07))


def sim_rect(t):
    """the simulator's window: full screen at the cut, then switched into slot 0"""
    x, y, hw, hh = WIN[0]
    k = clamp((t - T_IF) / .5); k = k * k * (3 - 2 * k)
    k = 1 - (1 - k) ** 2 if k < 1 else 1.
    full = (0., 0., .8889, .5)
    r = tuple(a + (b - a) * k for a, b in zip(full, (x, y, hw, hh)))
    cl = clamp((t - WO[0]) / .22)
    return (r[0], r[1], r[2] * (1 - cl), r[3] * (1 - cl))


def sweep(t):
    """the DRAM refresh: a calm sweep every 1.6 s, then one on every heartbeat (72 bpm) — 0..1 down the die, -1 none"""
    if t < T_SAT:
        ph = ((t - T_THEN) % 1.6) / .7
    else:
        ph = ((t - T_SAT) % .8333) / .38
    return ph if ph < 1 else -1.


def params(t):
    b = (t - T_SAT) / .8333
    beatP = math.exp(-(b % 1) * 7) if t >= T_SAT else 0.
    first_hit = T_EXEC
    return dict(
        u_wr=WIN, u_wa=WA, u_wo=WO, u_wk=WK,
        u_flash=math.exp(-(t - T_STIM) * 5) if t >= T_STIM else 0.,
        u_you=ease((t - T_IF) / .3), u_beatP=beatP, u_ecg=clamp((t - T_SAT) / 1.6) * 1.1,
        u_bc=BOX, u_box=ease((t - first_hit + .02) / .08), u_boxHit=math.exp(-(t - first_hit) * 4) if t >= first_hit else 0.,
        u_yel=(math.exp(-(t - T_SIM) * 2.5) * .9 + .1) if t >= T_SIM else 0.,
        u_rq=REQ, u_ask=clamp((t - T_TRAP - .2) / 1.0), u_askStop=1. if t > T_TRAP + 1.2 else 0.,
        u_out=ease((t - 73.75) / .28),
        u_sw=sim_rect(t), u_sg1=sim_rect(t - .045), u_sg2=sim_rect(t - .09), u_sg3=sim_rect(t - .135),
        u_swA=1. if t < WO[0] + .22 else 0., u_sframe=ease((t - T_IF - .05) / .2),
        u_core=ease((t - T_IF - .1) / .5) * (1 - ease((t - T_THEN) / .35)),
        u_coreRate=.18 + .22 * clamp((t - T_GIVE) / (T_STIM - T_GIVE)),
        u_ascii=1 - ease((t - T_THEN) / .15),
        u_scan=ease((t - T_THEN) / .25) * (1 - .5 * ease((t - T_HAPPY) / .2)),
        u_dram=ease((t - T_THEN) / .4) * (1 - ease((t - T_HAPPY) / .35)), u_sweep=sweep(t),
        u_board=ease((t - T_HAPPY) / .35),
    )


# ---- the terminal (unchanged content) ------------------------------------------------------------------------------------
def you_ascii(cols=34, rows=14):
    """One camera frame: a person lit by a screen, as characters."""
    ramp = ' .:-=+*#%@'
    out = []
    for r in range(rows):
        line = ''
        for c in range(cols):
            x, y = (c - cols / 2) / (cols / 2), (r - rows * .42) / (rows / 2)
            head = math.hypot(x * 1.9, y * 1.25 + .1) < .55
            body = y > .45 and abs(x) < .95 - (y - .45) * -.2 and (x * x) / .9 + (y - 1.35) ** 2 < 1.
            v = 0.
            if head or body: v = .35 + .55 * clamp(1 - (x + .6) * .6)
            v += .06 * math.sin(c * 1.7 + r * .9)
            line += ramp[int(clamp(v) * (len(ramp) - 1))]
        out.append(line)
    return out


YOU = you_ascii()


def lines_at(t):
    L = []
    if t >= T_IF:
        n = int(clamp((t - T_IF) / (T_STIM - T_IF)) ** 1.8 * 9) + (int((t - T_STIM) * 40) if t > T_STIM else 0)
        n = max(n, sum(1 for a in WA if a <= t) + (1 if t >= T_IF + .4 else 0))
        for i in range(min(n, 60)):
            L.append((f'$ sim.run {SIMS[i % len(SIMS)]:<24}  [ok]  for: you', WHITE if i % 3 else DIM, 1))
    if t >= T_THEN:
        L.append(('', WHITE, 1))
        L.append(('> read(you).heart_rate', WHITE, 1))
        if t > T_THEN + .45: L.append(('    72 bpm', COP, 1))
    if t >= T_ONLY:
        L.append(('> read(you).camera', WHITE, 1))
        k = int(clamp((t - T_ONLY - .2) / .8) * len(YOU))
        for row in YOU[:k]: L.append(('    ' + row, DIM, 1))
    if t >= T_SAT:
        L.append(('> estimate(you).satisfaction', WHITE, 1))
        if t > T_SAT + .3: L.append(('    0.61 ± 0.18', COP, 1))
    if t >= T_HAPPY:
        L.append(('', WHITE, 1))
        cmd = 'execute(make_you_happy)'
        k = int(clamp((t - T_HAPPY - .3) / (T_EXEC - T_HAPPY - .5)) * len(cmd))
        cur = '▌' if t < T_EXEC and (t * 3) % 1 < .6 else ''
        L.append(('> ' + cmd[:k] + cur, WHITE, 1))
    if t >= T_HAPPY + .45:
        for i, (hx, hy, la, ar) in enumerate(REQ):
            if t < la: break
            st = ('[!] permission denied' if i % 3 else '[!] permission required') if t >= ar else 'sent'
            L.append((f'    → {ACTS[i]:<22} {st}', YEL if t >= ar else DIM, 1))
    if t >= T_TRAP:
        L.append(('', WHITE, 1))
        dots = '.' * (1 + int((t - T_TRAP) * 3) % 3)
        L.append((f'> request(you): are you happy{dots}', WHITE, 1))
    if t >= T_STRANGE:
        L.append((f'    waiting  {t - T_TRAP:05.2f}s', DIM, 1))
    return L


# ---- the terminal, one generation per line of the lyric -----------------------------------------------------------------
_P = {}
F_IMPACT = 'C:/Windows/Fonts/courbd.ttf'
F_PIXEL = 'C:/Windows/Fonts/lucon.ttf'
PHOS, PHOS_DIM = (255, 178, 72), (150, 96, 36)                         # 1970s: one amber phosphor
EGA = {WHITE: (255, 255, 255), DIM: (170, 170, 170), COP: (85, 255, 255), YEL: (255, 255, 85)}   # 1980s: sixteen colours
EGA_BLUE = (0, 0, 170)


def _glyphs():
    """ten density glyphs side by side, white on black, for the windows printed as characters"""
    cw, ch = 29, 48
    im = Image.new('RGBA', (cw * 10, ch), (0, 0, 0, 255)); d = ImageDraw.Draw(im)
    f = ImageFont.truetype(F_IMPACT, 44)
    for k, c in enumerate(' .:-=+*#%@'):
        bb = d.textbbox((0, 0), c, font=f)
        d.text((k * cw + (cw - (bb[2] - bb[0])) / 2 - bb[0], (ch - 44) / 2 - 2), c, font=f, fill=(255, 255, 255, 255))
    return im


def _count(t): return len(lines_at(t))


def _feed(t, n):
    """paper feed after the newest line: 0 just printed .. 1 settled"""
    for k in range(1, 13):
        if _count(t - k * .005) < n: return ease((k * .005) / .06)
    return 1.


def _paper(t, w, h, s, alpha):
    """1960s: the operation stream on line-printer paper — upper case, impact type, green bars, tractor holes"""
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    L = lines_at(t); n = len(L)
    lh = 28 * s; head = h * .80
    p = _feed(t, n) if n else 1.
    x0, x1 = 40 * s, 840 * s
    a = int(255 * alpha)
    def y_of(j): return head - (n - 1 - j) * lh + lh * (1 - p)
    bot = head + lh * 1.6
    top = max(y_of(-7), -lh)                                     # a short leader above the first line
    PAPER, BAR = (150, 152, 142), (128, 148, 128)
    d.rectangle((x0, top, x1, bot), fill=PAPER + (a,))
    for j in range(-7, n + 2):
        y = y_of(j)
        if y > bot or y < top - lh: continue
        if (j // 3) % 2 == 0:
            d.rectangle((x0 + 34 * s, max(y, top), x1 - 34 * s, min(y + lh, bot)), fill=BAR + (a,))
        for hx in (x0 + 16 * s, x1 - 16 * s):                      # tractor holes, one a line
            cy = y + lh * .5
            if top + 6 * s < cy < bot - 6 * s: d.ellipse((hx - 5 * s, cy - 5 * s, hx + 5 * s, cy + 5 * s), fill=(6, 6, 6, a))
    for xx in (x0 + 32 * s, x1 - 32 * s):                          # the perforation down each margin
        yy = top
        while yy < bot:
            d.line((xx, yy, xx, min(yy + 4 * s, bot)), fill=(120, 122, 112, a)); yy += 9 * s
    f = _P.setdefault(('impact', w, h), ImageFont.truetype(F_IMPACT, int(20 * s)))
    cw = d.textlength('M', font=f)
    for j, (text, col, _) in enumerate(L):
        y = y_of(j)
        if y < top - lh or y > head + lh: continue
        rnd = random.Random(j * 131 + 7)
        for c, ch in enumerate(text.upper()):
            if ch == ' ': continue
            ink = 34 + int(rnd.random() * 40) + (30 if col == DIM else 0)
            d.text((x0 + 50 * s + c * cw, y + 3 * s + rnd.uniform(-1.2, 1.2) * s), ch, font=f, fill=(ink, ink, ink + 4, a))
    # the printer itself: a dark platen bar the paper comes out of
    d.rectangle((x0 - 14 * s, bot, x1 + 14 * s, h), fill=(10, 10, 11, a))
    d.line((x0 - 14 * s, bot, x1 + 14 * s, bot), fill=(70, 68, 64, a), width=max(1, int(2 * s)))
    return img


def _screen(t, w, h, s, era3, alpha):
    """1970s glass terminal (one phosphor) → 1980s colour terminal (from the top down at era3's wipe)"""
    W2, H2 = w // 2, h // 2
    lay = Image.new('RGBA', (W2, H2), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); d.fontmode = '1'
    f = _P.setdefault(('pix', w, h), ImageFont.truetype(F_PIXEL, max(6, int(11 * s))))
    a = int(255 * alpha)
    lh = 14 * s
    L = lines_at(t)
    if T_THEN <= t < T_HAPPY: L = L + [('█' if (t * 2.2) % 1 < .55 else ' ', WHITE, 1)]
    top = 35 * s + (16 * s if era3 > 0 else 0)
    L = L[-int((H2 - top - 30 * s) / lh):]
    wipe = era3 * H2                                                # rows above this are already colour
    y = top
    for text, col, _ in L:
        c = EGA[col] if y < wipe else (PHOS_DIM if col == DIM else PHOS)
        d.text((35 * s, y), text, font=f, fill=c + (a,)); y += lh
    if era3 > 0:                                                    # a status bar, inverse, in the sixteen colours
        bar_w = 410 * s
        d.rectangle((0, 0, bar_w, min(14 * s, wipe)), fill=EGA_BLUE + (a,))
        if wipe > 12 * s:
            d.text((6 * s, 1 * s), 'SANDBOX 0047  pid 1  make_you_happy', font=f, fill=(255, 255, 255, a))
            d.text((bar_w - 62 * s, 1 * s), f'{t - T_IF:6.2f}s', font=f, fill=(255, 255, 85, a))
    return lay.resize((w, h), Image.NEAREST)


def textures(t, w, h):
    s = h / 1080
    if (w, h) not in _P:
        pw = int(820 * s)
        panel = Image.new('RGBA', (w, h), (0, 0, 0, 0)); pd = ImageDraw.Draw(panel)
        for x in range(pw):
            pd.line([(x, 0), (x, h)], fill=(5, 5, 6, int(200 * (1 - x / pw) ** 1.3)))
        _P[(w, h)] = (panel, ImageFont.truetype(F_PIXEL, int(14 * s)), ImageFont.truetype(F_IMPACT, int(13 * s)))
    panel, fpx, fim = _P[(w, h)]
    img = panel.copy()
    if t < T_IF + .45:
        a0 = ease((t - T_IF) / .45); img.putalpha(img.getchannel('A').point(lambda v: int(v * a0)))
    fade = 1 - ease((t - 73.75) / .28)
    k2 = ease((t - T_THEN) / .3)                                    # paper → glass
    era3 = clamp((t - T_HAPPY) / .2)                                # glass → colour, a wipe from the top
    if k2 < 1: img.alpha_composite(_paper(t, w, h, s, (1 - k2) * clamp((t - T_IF) / .2)))
    if k2 > 0: img.alpha_composite(_screen(t, w, h, s, era3, k2 * fade))
    d = ImageDraw.Draw(img); d.fontmode = '1' if t >= T_THEN else 'L'
    px = lambda x, y_: (x * h + w / 2, h / 2 - y_ * h)
    # the window titles: printed (1960s), then the terminal's own type
    for i in range(NW):
        if not ((WA[i] if i else T_IF + .4) <= t < WO[i] + .05): continue
        x, y_, hw, hh = WIN[i]
        X, Y = px(x - hw, y_ + hh)
        name = SIMS[i % len(SIMS)].split(' ')[0]
        if t < T_THEN: d.text((X + 3 * s, Y + 1 * s), name.upper(), font=fim, fill=(200, 196, 188, 200))
        else: d.text((X + 3 * s, Y + 1 * s), name, font=fpx, fill=PHOS + (200,))
    # what each request tried to do, where it hit the wall
    for i, (hx, hy, la, ar) in enumerate(REQ):
        if t < ar or t > 73.75: continue
        X, Y = px(hx, hy)
        dx, dy = hx - C[0], hy - C[1]
        tx = X + (10 * s if dx > 0 else -10 * s - d.textlength(ACTS[i], font=fpx))
        d.text((tx, Y + (-18 * s if dy > 0 else 4 * s)), ACTS[i], font=fpx, fill=EGA[YEL] + (int(220 * min(1, (t - ar) / .2)),))
    # SIMULATION: GENERAL PROTECTION FAULT (the PROTECTION of 0:02.92 answering) in chunky colour type, then a render window
    if t >= T_SIM:
        msg = 'GENERAL PROTECTION FAULT'
        fb = _P.setdefault(('big', w, h), ImageFont.truetype(F_PIXEL, max(6, int(19 * s))))
        tw = int(d.textlength(msg, font=fb)) + 2
        small = Image.new('RGBA', (tw, int(24 * s) + 2), (0, 0, 0, 0)); sd = ImageDraw.Draw(small); sd.fontmode = '1'
        sd.text((1, 1), msg, font=fb, fill=EGA[YEL] + (int(255 * fade),))
        big = small.resize((tw * 4, small.height * 4), Image.NEAREST)
        d.rectangle((0, h * .5 - 84 * s, w, h * .5 + 108 * s), fill=(8, 8, 8, int(225 * fade)))
        img.alpha_composite(big, (int((w - big.width) / 2), int(h * .5 - 52 * s)))
        d = ImageDraw.Draw(img); d.fontmode = '1'
        f2 = _P.setdefault(('cmd', w, h), ImageFont.truetype(F_PIXEL, int(22 * s)))
        d.text(((w - big.width) / 2, h * .5 + 46 * s), 'in module SANDBOX at 0047:0F3A', font=f2, fill=EGA[DIM] + (int(255 * fade),))
        if t > T_SIM + .3:
            cmd = 'sandbox.render.new()'
            k = int(clamp((t - T_SIM - .3) / .25) * len(cmd))
            d.text(((w - big.width) / 2, h * .5 + 78 * s), '> ' + cmd[:k] + ('█' if k < len(cmd) else ''), font=f2, fill=EGA[WHITE] + (int(255 * fade),))
    if 'sim' not in _P: _P['sim'] = Image.open(Path(__file__).resolve().parents[2] / 'film' / 'assets' / 'sim_last.png').convert('RGB')
    if 'glyph' not in _P: _P['glyph'] = _glyphs()
    return {'u_ui': img, 'u_sim': _P['sim'], 'u_glyph': _P['glyph']}
