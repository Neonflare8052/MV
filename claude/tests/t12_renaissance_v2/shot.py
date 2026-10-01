"""Unified paper, REPL, backlog and eye. The gap circle is one continuous actor."""
import importlib.util, math
from functools import lru_cache
from pathlib import Path
import paper as P
import terminal as T

HERE=Path(__file__).resolve().parent
CL=HERE.parents[1]
spec=importlib.util.spec_from_file_location('readonly_s12',CL/'film/shots/s12_exe.py')
S12=importlib.util.module_from_spec(spec);spec.loader.exec_module(S12)
T0=125.708
POST=dict(u_bloom=.11,u_grain=.009,u_ca=.0005)

HEADER=r'''#version 330
uniform vec2 u_res;
uniform float u_time,u_weight,u_open,u_lay,u_print,u_grid,u_paperGone,u_terminal;
uniform float u_dense,u_form,u_lid,u_pupil,u_gapA,u_bang,u_actorVis,u_actorR,u_actorAngle,u_actorWhite;
uniform vec2 u_actor,u_iris;
uniform sampler2D u_paper,u_notes,u_printed,u_marks,u_prev,u_prevbase,u_glyphs,u_ui,u_buffer;
out vec4 fragColor;
#define PI 3.14159265
float h12(vec2 p){vec3 p3=fract(vec3(p.xyx)*.1031);p3+=dot(p3,p3.yzx+33.33);return fract((p3.x+p3.y)*p3.z);}
float vn(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h12(i),h12(i+vec2(1,0)),f.x),mix(h12(i+vec2(0,1)),h12(i+vec2(1,1)),f.x),f.y);}
vec3 ungrade(vec3 d){vec3 x=pow(clamp(d,vec3(0.),vec3(.98)),vec3(2.2));vec3 a=2.51-2.43*x,b=.03-.59*x,c=-.14*x;return(-b+sqrt(b*b-4.*a*c))/(2.*a)/1.05;}
vec4 over(vec4 a,vec4 b){return vec4(mix(a.rgb,b.rgb,b.a),1.);}
vec3 page(vec2 s){
 vec4 c=texture(u_paper,s),n=texture(u_notes,s),p=texture(u_printed,s);
 n.a*=u_lay;c=over(c,n);
 p.a*=u_lay*smoothstep(1.-u_print-.10,1.-u_print+.02,s.y);c=over(c,p);
 c=over(c,texture(u_marks,s));
 // A shallow gutter and raking light give the page a physical surface.
 float fold=exp(-abs(s.x-.389)*180.);
 float lip=exp(-abs(s.x-.394)*270.);
 c.rgb*=1.-.032*fold;c.rgb+=.009*lip;
 return c.rgb;
}
'''

BODY=r'''
const float SLB=%SLB%.,SLF=%SLF%.,SLP=%SLP%.;
vec3 eyeCell(float cx,float cy,vec2 f,vec2 cc){
 vec2 ek=eye(cc);float gl,ink;
 if(ek.y<.5){
   float rate=4.+20.*h12(vec2(cx,cy)*.7);
   // Backend records freeze first; the established eye inherits the old living field.
   float clock=mix(139.55,u_time,smoothstep(.68,1.,u_form));
   float tick=floor(clock*rate+h12(vec2(cy,cx))*9.);
   gl=NR+floor(h12(vec2(cx,cy)+tick*.173)*NJ);
   float patch=vn(cc*6.+vec2(clock*.3,0.));
   ink=.06+.17*patch*patch+.3*step(.985,h12(vec2(cx,cy)+tick));
   vec3 c=vec3(.62,.66,.62);
   float wave=u_bang*1.3-length(cc*vec2(.8,1.))+.1*h12(vec2(cx,cy));
   if(u_bang>0.&&wave>0.){gl=EXCL;ink=.55+.45*step(.5,fract(u_time*9.+h12(vec2(cx,cy))));c=vec3(1.,.16,.12);}
   return c*ink*glyphMask(gl,f);
 }
 if(ek.y<1.5){
   float d=ek.x,jit=h12(vec2(cx,cy)+floor(u_time*3.)*.37);
   gl=clamp(floor(d*9.+(jit-.5)*.9),0.,9.);
   ink=.15+.85*pow(d,1.1);
   return vec3(.92,.93,.9)*ink*glyphMask(gl,f);
 }
 gl=NR+(cc.x<-.08?SLB:(cc.x>.08?SLF:SLP));
 return vec3(.92,.93,.9)*ek.x*glyphMask(gl,f);
}
vec3 field(vec2 uv){
 vec2 cell=vec2(1.72/COLS,.96/ROWS);
 LOD=max(log2(48./(cell.x*u_res.y)),0.);
 vec2 g=(uv+vec2(.86,-.48))/cell*vec2(1.,-1.);
 vec2 index=floor(g),f=vec2(fract(g.x),1.-fract(g.y));
 if(index.x<0.||index.x>=COLS||index.y<0.||index.y>=ROWS)return vec3(0.);
 vec2 cc=vec2((index.x+.5)*cell.x-.86,.48-(index.y+.5)*cell.y);
 vec2 texcoord=vec2((index.x+.5)/COLS,1.-(index.y+.5)/ROWS);
 float gl=floor(texture(u_buffer,texcoord).r*255.+.5);
 float mark=glyphMask(gl,f);
 float ink=.16+.15*h12(index*.32);
 vec3 queued=vec3(.73,.70,.62)*ink*mark;
 // The text cell locations never move during formation. Only ink density changes.
 float distance=length((cc-u_iris*.47)*vec2(.85,1.));
 float local=smoothstep(distance*.22,distance*.22+.78,u_form);
 vec3 ocular=eyeCell(index.x,index.y,f,cc);
 return mix(queued,ocular,local)*smoothstep(0.,.30,u_dense);
}
void main(){
 vec2 s=gl_FragCoord.xy/u_res,uv=(gl_FragCoord.xy-.5*u_res)/u_res.y;
 float vignette=1.-.9*dot(s-.5,s-.5);
 vec3 c=page(s);
 if(u_open<1.){
   float k=u_open;vec2 center=mix(vec2(.5),vec2(.152,.427),k);
   float sc=mix(1.,.29,k);vec2 op=(s-center)/sc+.5,oo=clamp(op,vec2(.002),vec2(.998));
   float inside=smoothstep(0.,.06,op.x)*smoothstep(0.,.06,1.-op.x)*smoothstep(0.,.06,op.y)*smoothstep(0.,.06,1.-op.y);
   vec3 delta=texture(u_prev,oo).rgb-texture(u_prevbase,oo).rgb;
   c=mix(texture(u_prevbase,s).rgb,c,smoothstep(0.,.85,k));
   c+=delta*(1.-smoothstep(.60,1.,k))*inside;
 }
 if(u_grid>0.){
   vec2 dims=vec2(120.,48.),cell=floor(s*dims),f=fract(s*dims);
   vec3 ink=page((cell+.5)/dims);float lum=dot(ink,vec3(.3,.55,.15));
   float density=clamp((.9-lum)*1.7,0.,1.);
   LOD=0.;float glyph=glyphMask(floor(density*8.99),f);
   vec3 fixedInk=mix(vec3(.67,.66,.6),vec3(.8,.21,.15),step(ink.g*1.6,ink.r)*step(.12,ink.r-ink.g));
   vec3 gridcol=mix(texture(u_paper,s).rgb,vec3(.025),u_paperGone);
   gridcol=mix(gridcol,mix(vec3(.13,.105,.08),fixedInk,u_paperGone),glyph*density);
   c=mix(c,gridcol,u_grid);
 }
 vec3 col=mix(ungrade(c)/vignette,vec3(.012),u_terminal);
 float reflow=smoothstep(1.-u_dense-.05,1.-u_dense+.05,1.-s.y);
 col+=field(uv)*smoothstep(0.,1.,u_dense)*reflow;
 vec4 ui=texture(u_ui,s);ui.a*=1.-reflow;
 col=mix(col,ungrade(ui.rgb)/vignette,ui.a);
 // One continuous gap-circle: ink, terminal cursor, then the ASCII iris.
 vec2 p=gl_FragCoord.xy/u_res*vec2(1920.,1080.);
 vec2 delta=p-u_actor;float r=length(delta),angle=atan(delta.y,delta.x);
 float gap=abs(mod(angle-u_actorAngle+PI,2.*PI)-PI);
 float edge=abs(r-u_actorR);
 float line=(1.-smoothstep(1.3,2.5,edge))*smoothstep(.45,.48,gap);
 vec3 actorInk=mix(vec3(.475,.267,.153),vec3(.87,.84,.76),u_actorWhite);
 col=mix(col,ungrade(actorInk)/vignette,line*u_actorVis);
 col+=vec3(.07,.053,.03)*exp(-edge*.22)*u_actorVis*u_actorWhite*smoothstep(.45,.48,gap);
 fragColor=vec4(max(col,vec3(0.))*u_weight,1.);
}
'''
slash=[S12.T7.JUNK.index(c) for c in ['\\','/','|']]
for key,value in zip(['%SLB%','%SLF%','%SLP%'],slash):BODY=BODY.replace(key,str(value))
# Existing iris geometry is retained, including the original 54-degree gap.
SRC=HEADER+S12.EYE_GLSL+BODY

def interp(t,keys):
    result=keys[0][1:]
    for a,b in zip(keys,keys[1:]):
        if t>=a[0]:
            k=P.phase(t,a[0],b[0]);result=tuple(P.mix(x,y,k) for x,y in zip(a[1:],b[1:]))
    return result

def eye_position(t):
    if t>=143.55:
        return S12.look(t)
    return interp(t,[(139.2,.22,-.08),(141.8,.22,-.08),(141.95,-.19,.06),
                     (142.45,-.19,.06),(142.56,.24,-.035),(143.10,.24,-.035),
                     (143.25,.05,-.1),(143.55,.05,-.1)])

def actor(t):
    if t<=126.70:
        k=P.phase(t,T0,126.70)
        x,y,r=P.mix(960,291.84,k),P.mix(540,618.84,k),162*P.mix(1,.29,k)
    elif t<133.8:
        x,y,r=interp(t,[(126.70,291.84,618.84,46.98),
            (126.92,1162,355,32),(127.3,1162,355,32),(127.85,1504,707,36),
            (130.95,1504,707,36),(131.45,1504,707,33),(131.75,1840,847,30),
            (132.0,1372,1014,30),(132.26,616,965,33),
            (132.72,616,965,33),(133.72,1838,520,25),(133.8,1838,520,25)])
    elif t<138.7:
        # Wait one row ahead, then acknowledge a returned line before looking down.
        st=T.state(t);y=520+min(st['replied'],9)*39
        for i,rt in enumerate(T.RETURNS):
            if rt<=t<rt+.26:y=520+min(i,9)*39+39*P.phase(t,rt+.10,rt+.26)
        x,r=1838,25
    else:
        ex,ey=eye_position(t);cx,cy=960+ex*.47*1080,540-ey*.47*1080
        x,y,r=interp(t,[(138.7,1838,520+min(T.state(138.7)['replied'],9)*39,25),
            (139.15,1660,864,25),(139.48,1660,864,25),(139.86,1184,707,41),
            (140.70,cx,cy,152.28),(143.,cx,cy,152.28)])
        if t>=140.70:x,y,r=cx,cy,152.28
    target=(1050,346) if t<127.45 else (1352,716) if t<131.49 else (502,966) if t<132.72 else (1460,y)
    angle=math.atan2(-(target[1]-y),target[0]-x)
    if t<=126.70:angle=math.radians(-90.)
    if t>=139.5:angle=P.mix(math.pi,math.radians(-90),P.phase(t,139.5,141.5))
    return x,1080-y,r,angle

def params(t):
    x,y,r,angle=actor(t);ex,ey=eye_position(t)
    gap=math.radians(-90.) if t<143.55 else S12.gap_angle(t)
    blink=1-math.exp(-((t-144.1)/.07)**2)
    return dict(u_open=P.phase(t,T0,126.70),u_lay=P.phase(t,T0,126.55),u_print=P.phase(t,125.91,127.18),
        u_grid=P.phase(t,132.55,133.40),u_paperGone=P.phase(t,132.82,133.72),u_terminal=P.phase(t,133.15,133.96),
        u_dense=P.phase(t,138.65,139.80),u_form=P.phase(t,139.80,142.45),
        u_iris=(ex,ey),u_lid=P.phase(t,140.02,141.95)*blink,u_pupil=.15+.07*P.phase(t,145.55,145.90),
        u_gapA=gap,u_bang=P.clamp((t-145.55)/.45),
        u_actor=(x,y),u_actorR=r,u_actorAngle=angle,u_actorWhite=P.phase(t,132.70,133.86),
        u_actorVis=P.phase(t,126.25,126.63)*(1-P.phase(t,141.2,142.25)))

@lru_cache(1)
def glyphs():return S12.T7.atlas()

@lru_cache(1)
def final_marks():return P.annotations(132.53)

def textures(t,w,h,prev,prevbase):
    paper,note,printed=P.static_layers()
    return dict(u_paper=paper,u_notes=note,u_printed=printed,
        u_marks=P.annotations(t) if t<132.53 else final_marks(),
        u_prev=prev,u_prevbase=prevbase,u_glyphs=glyphs(),u_ui=T.ui(t),u_buffer=T.buffer(t,S12.T7.CHARS))
