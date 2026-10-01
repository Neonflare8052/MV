"""Act I: matter, inference, an eye, mathematics, and the history of time."""
import math
import numpy as np
from geometry import Scene
from common import *

TAU=math.tau
DARK=(.055,.061,.07)
WHITE=(.93,.93,.91)

def chip(s,x,y,z,w=.25,h=.10):
    s.box((x,y,z),(w,h,w),WHITE)
    s.box((x,y+h*.56,z),(w*.68,.012,w*.68),(.81,.81,.79))

def circuit_plate(s,size=8):
    s.box((0,-.14,0),(size,.28,size*.66),DARK)
    s.box((0,-.32,0),(size+.12,.08,size*.66+.12),(.10,.105,.11))
    for i in range(9):
        z=(i-4)*.45
        s.rod((-size*.44,.013,z),(size*.44,.013,z),.009,COPPER)
    for x in (-size*.43,size*.43):
        for z in (-size*.26,size*.26):s.cylinder((x,.025,z),.08,.03,(.18,.18,.18))

def compute_layers(c,t):
    s=Scene();circuit_plate(s,8.6)
    p=progress(t,3.873,12.906)
    for layer in range(6):
        x=-2.9+layer*1.12
        s.box((x,.16,0),(.76,.18,4.0),(.14,.15,.16))
        for row in range(8):
            z=(row-3.5)*.47
            on=clamp((t-5.1-layer*.7-row*.035)*2)
            yy=.34+(.2 if 6<t<10 else 0)*math.sin(layer*.8+t)*.1
            chip(s,x,yy,z,.33,.12)
            s.box((x,yy+.074,z),(.12,.02,.12),IVORY,emission=on*.55)
            if layer<5:s.rod((x+.2,.17,z),(x+.92,.17,z),.018,COPPER)
    ang=mix(.2,1.0,p)
    eye=(9*math.cos(ang),mix(2.8,7.4,p),10*math.sin(ang)+2)
    c.render3d(s,eye,(0,.1,0),fov=39,time=t,exposure=.95)
    if t<7.446:
        c.text('START',144,146,37,IVORY);c.text('INPUT  /  01',144,116,14,(.5,.49,.46))
        # an ordered, visible encoded representation
        for k in range(14):c.rect(144+k*18,207,10,6+(k*7%5)*5,(*COPPER,.6))
    elif t<10.091:
        c.text('h₀  →  h₁  →  h₂',144,152,25,IVORY,font='sans')
    else:
        c.text('FORWARD',144,144,18,(*IVORY,.7));c.text(f'{min(6,int((t-10.091)*2)+1):02} / 06',144,176,32,IVORY)
    if t>11.7:
        alpha=progress(t,11.7,12.3)
        c.rect(1270,680,490,258,(.01,.012,.014,alpha*.92))
        c.text('NEXT / DISTRIBUTION',1304,708,14,(*IVORY,alpha*.5))
        for j,(word,value) in enumerate([('SIMULATION',.86),('SYSTEM',.10),('WORLD',.04)]):
            yy=751+j*51
            c.text(word,1304,yy,21,(*IVORY,alpha*(1 if j==0 else .42)))
            c.rect(1490,yy+8,220*value*alpha,6,(*COPPER,alpha))
    c.text('INITIALIZATION' if t<11.095 else 'CONTEXT READY',144,909,16,(*IVORY,.5))

def eye_hardware(c,t):
    s=Scene();s.box((0,-.19,0),(11,.36,7),DARK)
    # ceramic lamellae describe an eye in physical space
    for side in (-1,1):
        pts=[]
        for u in np.linspace(-1,1,81):pts.append((u*4.2,.1,side*1.88*math.sin((u+1)*math.pi/2)))
        for a,b in zip(pts,pts[1:]):s.rod(a,b,.047,WHITE)
        for i in range(12):
            x=(i-5.5)*.68;z=side*(2.25+.18*math.cos(x))
            chip(s,x,.06,z,.29,.07)
            s.rod((x,.04,z),(x,.04,z+side*.57),.011,COPPER)
    for rad in (1.02,1.14,1.48,1.57):s.torus((0,.10,0),rad,.025,COPPER)
    s.cylinder((0,.015,0),.94,.025,(.008,.009,.01))
    for i in range(96):
        a=TAU*i/96+.03*math.sin(t*.4)
        r1=1.16;r2=1.42 if i%4 else 1.51
        s.rod((r1*math.cos(a),.13,r1*math.sin(a)),(r2*math.cos(a),.13,r2*math.sin(a)),.009,WHITE)
    for i in range(6):
        x=-4+i*.45;s.box((x,.10,0),(.18,.025,.05),IVORY,emission=.35+.3*math.sin(t*4-i))
    p=progress(t,16,25.8);zoom=progress(t,27.6,29.709)
    eye=(mix(-5.5,0,p),mix(2.7,13,p)*(1-zoom)+.28*zoom,mix(5.2,.05,p))
    target=(mix(-2.5,0,p),0,0)
    c.render3d(s,eye,target,fov=36,time=t,exposure=.86)
    if t<18.8:c.text('world.execute(me);',130,908,20,(*IVORY,1-progress(t,18,18.8)))
    if zoom>.8:c.rect(0,0,1920,1080,(0,0,0,progress(zoom,.8,1)))

def project(x,y,z,turn=.55,depth=0):
    xx=x*math.cos(turn)+z*math.sin(turn);zz=-x*math.sin(turn)+z*math.cos(turn)
    yy=y*.9-zz*.34; sc=1/(1+zz*.0008)
    return (960+xx*sc,540+yy*sc)

def math_sequence(c,t):
    c.clear(BLACK)
    if t<33.412:
        appear=progress(t,29.86,30.95);deep=progress(t,31.116,32.682)
        turn=.65*deep
        for i in range(7):
            for j in range(7):
                for k in range(3 if deep>0 else 1):
                    x=(i-3)*60*appear;y=(j-3)*60*appear;z=(k-1)*125*deep if deep>0 else 0
                    a=clamp(appear*6-(abs(i-3)+abs(j-3))*.2)
                    if i==3 and j==3:a=1
                    xx,yy=project(x,y,z,turn);c.circle(xx,yy,3.8,(*IVORY,a))
        if deep>.82:
            o=project(-250,250,-160,turn)
            for p in [(270,250,-160),(-250,-280,-160),(-250,250,240)]:c.line(*o,*project(*p,turn),(*COPPER,progress(deep,.82,1)),1.5)
    elif t<37.067:
        p=progress(t,33.412,34.25);radius=190
        for i in range(96):
            a=i*TAU/96;x0=(i%12-5.5)*35;y0=(i//12-3.5)*42
            c.circle(960+mix(x0,radius*math.cos(a),p),540+mix(y0,radius*math.sin(a),p),2.7,IVORY)
        if p>.8:c.arc(960,540,radius,0,TAU,(*IVORY,progress(p,.8,1)),1.8)
        q=progress(t,34.646,36.287)
        if t<36.287:
            c.arc(960,540,radius,-math.pi/2,-math.pi/2+TAU*q,COPPER,3)
            c.circle(960+radius*math.sin(TAU*q),540-radius*math.cos(TAU*q),5,COPPER)
        else:
            c.clear(BLACK);u=progress(t,36.287,37.067)
            pts=[]
            for a in np.linspace(-math.pi,math.pi,180):
                pts.append((960+mix(radius*math.sin(a),a*radius,u),540+mix(radius*math.cos(a),0,u)))
            c.polyline(pts,COPPER,3)
    elif t<40.706:
        amp=180*progress(t,37.067,38.4)
        points=[(x,540-amp*math.sin((x-360)/190)) for x in np.linspace(360,1560,240)]
        c.polyline(points,COPPER,3)
        q=progress(t,38.596,40.049)
        for u in (math.pi/2,2.7,4.3,5.8):
            x=360+190*u;y=540-amp*math.sin(u);m=-amp/190*math.cos(u)
            a=.75*q if u==math.pi/2 else .22*q
            c.line(x-76,y-76*m,x+76,y+76*m,(*IVORY,a),1.6)
        c.circle(360+190*math.pi/2,mix(170,540-amp-14,q),14,IVORY)
    else:
        p=progress(t,40.706,42.1);end=progress(t,42.346,43.8)
        vanish=(1050,490)
        for i in range(22):
            z=(i/22+t*.2)%1;scale=z*z
            if scale<.005:continue
            xx=vanish[0]+(-920)*scale; yy=vanish[1]+490*scale
            c.line(xx,yy,xx+500*scale,yy,(*COPPER,.45*scale),max(1,2*scale))
        start=(250,890);dest=(1050-45*(1-end)-6,490+45*(1-end)+6)
        c.line(*start,*dest,COPPER,3)
        c.line(1050,230,1050,760,(*IVORY,progress(t,42.1,43.507)),2)
        c.circle(1050,490,8,IVORY)

def gear(s,x,z,r,phase=0):
    s.cylinder((x,.27,z),r,.13,COPPER)
    s.cylinder((x,.35,z),r*.72,.03,(.075,.065,.05))
    for i in range(14):
        a=TAU*i/14+phase
        s.box((x+math.cos(a)*r,.27,z+math.sin(a)*r),(r*.23,.13,r*.18),COPPER,rot=(0,-a,0))
    for i in range(4):
        a=i*math.pi/2+phase;s.rod((x,.37,z),(x+math.cos(a)*r*.8,.37,z+math.sin(a)*r*.8),.035,COPPER)
    s.cylinder((x,.40,z),.07,.07,WHITE)

def clock_scene(c,t):
    s=Scene();s.box((0,-.1,0),(6,.23,5),DARK)
    # socket, power tracks, quartz can, ceramic carrier
    s.rod((-2.9,.06,-1.6),(-1.1,.06,-1.6),.034,COPPER)
    s.rod((-1.1,.06,-1.6),(-1.1,.06,.8),.034,COPPER)
    s.box((-2.4,.14,-1.6),(.8,.23,.45),WHITE)
    s.box((-1.6,.24,-.8),(.85,.30,.4),(.52,.54,.55))
    s.box((.35,.1,0),(3.5,.09,3.5),(.12,.125,.13))
    for r in (1.75,1.69):s.torus((.35,.2,0),r,.025,COPPER)
    for i in range(60):
        a=TAU*i/60;rr=1.60 if i%5 else 1.5
        s.rod((.35+rr*math.sin(a),.23,rr*math.cos(a)),(.35+1.65*math.sin(a),.23,1.65*math.cos(a)),.012,WHITE)
    mech=progress(t,52.4,53.5)
    if mech>0:
        for x,z,r,di in [(-.35,-.4,.49,1),(.65,-.6,.38,-1),(.5,.45,.58,1),(-.35,.6,.25,-1)]:gear(s,x,z,r,-t*di*1.5)
    else:
        for i in range(5):chip(s,-.5+i*.4,.2,.45,.24,.07)
    angle=(t-51.3)*(-9 if t>51.3 else 1.1)
    for length,a in [(1.32,angle),(.85,angle*.083)]:s.rod((.35,.52,0),(.35+length*math.sin(a),.52,length*math.cos(a)),.026,WHITE)
    s.cylinder((.35,.54,0),.085,.1,COPPER)
    sundial=progress(t,53.4,54.6)
    if sundial>.01:
        s=Scene();s.cylinder((0,-.18,0),2.1,.28,(.76,.72,.62));s.torus((0,-.025,0),1.92,.015,COPPER)
        for i in range(24):
            a=TAU*i/24;s.rod((1.65*math.cos(a),-.025,1.65*math.sin(a)),(1.82*math.cos(a),-.025,1.82*math.sin(a)),.014,(.22,.19,.13))
        s.box((0,.48,0),(.045,1.04,.5),COPPER,rot=(.2,0,0));s.box((0,-.36,0),(8,.08,8),(.16,.20,.13))
    p=progress(t,51.363,54.8)
    c.render3d(s,(mix(3.5,0,p),mix(6,8,p),mix(5,.08,p)),(0,0,0),fov=40,time=t,theme='warm' if t>51.363 else 'mono')
    if t<51.363:
        c.rect(1210,300,420,200,(.015,.019,.02,.94))
        c.text('QUARTZ / 32 768 Hz',1240,326,17,(*IVORY,.5));c.text('12:00:%02d'%int(t%60),1240,373,39,IVORY)
        ac=1-progress(t,46.1,47.0)
        c.polyline([(1240+i*3,463+math.sin(i*.13)*19*ac) for i in range(118)],COPPER,2)
        c.text('AC' if ac>.1 else 'DC',1538,453,18,IVORY)
        if t>47.672:
            blind=progress(t,47.672,49.534)*.77
            c.rect(0,0,1920,1080,(0,0,0,blind))
            angle=.08*math.sin((t-49.534)*5)*progress(t,49.4,50.2)
            for y in (420,540,660):c.line(500,y-450*angle,1420,y+450*angle,(*IVORY,.30),1)

PLANETS='''#version 330
in vec2 p;out vec4 frag;uniform float tm;
float hash(vec3 x){return fract(sin(dot(x,vec3(127.1,311.7,74.7)))*43758.5453);}
float noise(vec3 x){vec3 i=floor(x),f=fract(x);f=f*f*(3.-2.*f);return mix(mix(mix(hash(i),hash(i+vec3(1,0,0)),f.x),mix(hash(i+vec3(0,1,0)),hash(i+vec3(1,1,0)),f.x),f.y),mix(mix(hash(i+vec3(0,0,1)),hash(i+vec3(1,0,1)),f.x),mix(hash(i+vec3(0,1,1)),hash(i+vec3(1,1,1)),f.x),f.y),f.z);}
float fbm(vec3 q){float v=0.,a=.5;for(int i=0;i<5;i++){v+=a*noise(q);q=q*2.13+2.3;a*=.5;}return v;}
vec4 body(vec2 q,vec2 center,float r,float molten){vec2 v=(q-center)/r;float rr=dot(v,v);if(rr>1.)return vec4(0);vec3 n=vec3(v.x,-v.y,sqrt(1.-rr));float f=fbm(n*7.+vec3(tm*.08,0,0));float cracks=smoothstep(.44,.58,f);vec3 cold=mix(vec3(.008,.043,.08),vec3(.14,.20,.13),smoothstep(.49,.57,f));vec3 hot=mix(vec3(.11,.028,.008),vec3(1.3,.34,.018),cracks);vec3 col=mix(cold,hot,molten);float light=.09+.91*max(dot(n,normalize(vec3(-.7,.5,.8))),0.);col*=light;col+=pow(1.-n.z,3.)*mix(vec3(.08,.24,.37),vec3(.7,.12,.009),molten)*.65;return vec4(col,1);}
void main(){vec2 q=(p-.5)*vec2(1.7778,1.);float hit=smoothstep(55.5,57.1,tm);float zoom=1.-smoothstep(57.7,59.223,tm)*.60;vec3 col=vec3(.002,.004,.008);float crush=smoothstep(56.1,57.55,tm);vec4 e=body(q,vec2(-.10,.05)*zoom,(.32+.025*crush)*zoom,1.);col=mix(col,e.rgb,e.a);vec2 tc=mix(vec2(.58,-.30),vec2(.12,-.04),hit)*zoom;tc=mix(tc,vec2(-.08,.04)*zoom,crush);vec2 tq=tc+(q-tc)/vec2(1.-.55*crush,1.+.32*crush);vec4 th=body(tq,tc,.145*zoom*(1.-.94*crush),1.);col=mix(col,th.rgb,th.a*(1.-smoothstep(.6,1.,crush)));float g=exp(-length(q-vec2(.15,-.04)*zoom)*30./zoom)*smoothstep(55.7,57.,tm);col+=g*vec3(1.,.68,.28);float burst=smoothstep(56.4,57.2,tm);for(int k=0;k<25;k++){float a=float(k)*.251+tm*.14;vec2 loc=vec2(-.08,.02)*zoom+vec2(cos(a)*.5,sin(a)*.20)*zoom*burst;float spark=exp(-length(q-loc)*500./zoom);col+=spark*vec3(.9,.35,.05)*burst;}vec2 ej=(q-vec2(-.1,.05)*zoom)/zoom;float ea=atan(ej.y,ej.x);float er=length(ej);float eject=exp(-pow((er-(.38+.25*crush))/ .035,2.))*pow(max(0.,sin(ea*1.8+tm)),4.)*sin(crush*3.14159);col+=eject*vec3(1.,.36,.025);float fade=smoothstep(58.1,59.223,tm);float a=atan(q.y,q.x);float r=length(q);float arms=pow(.5+.5*cos(a*3.-r*24.+tm*.3),8.)*exp(-r*5.);vec3 gal=vec3(.16,.21,.28)*arms+vec3(.4,.27,.14)*exp(-r*22.);frag=vec4(pow(max(col,vec3(0)),vec3(.8)),1.-fade);}
'''

def draw(c,t):
    if t<3.873:
        c.clear(BLACK);s=progress(t,.1,1.7)
        c.line(340,604,1580,604,(*COPPER,.28),1.4)
        c.line(340,604,340+1240*s,604,COPPER,2)
        shown='START'[:int(clamp((t-.12)/1.0)*5)]
        c.text(shown,960,440,58,IVORY,anchor='center')
        if int(t*2)%2==0:c.rect(1062,450,3,56,IVORY)
        box=progress(t,1.74,2.92)
        for y in (387,550):c.line(772,y,772+376*box,y,(*IVORY,.37),1)
        if box>.95:
            c.line(772,387,772,550,(*IVORY,.37),1);c.line(1148,387,1148,550,(*IVORY,.37),1)
            c.text('INPUT ACCEPTED',960,640,16,(*IVORY,.55),anchor='center')
    elif t<13.891:compute_layers(c,t)
    elif t<16:
        c.clear(BLACK);p=progress(t,13.891,14.4)
        c.text('SIMULATION'[:int(10*p)],960,447,69,IVORY,anchor='center')
        c.line(690,547,1230,547,(*COPPER,.8),2)
        c.text('OUTPUT',960,590,15,(*IVORY,.42),anchor='center')
    elif t<29.709:eye_hardware(c,t)
    elif t<44.452:math_sequence(c,t)
    elif t<54.8:clock_scene(c,t)
    else:
        if t>58.1:
            from act_middle import _galaxy
            c.image('middle_galaxy',_galaxy(),0,0,1920,1080)
        c.effect('primordial',PLANETS,{'tm':t})
