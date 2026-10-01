#version 330
in vec2 in_corner;
in vec4 in_a,in_b,in_c,in_d;
uniform vec2 u_res;
uniform vec3 u_cam,u_look,u_sp[3];
uniform float u_time,u_fov,u_roll,u_focus,u_aper,u_bridge,u_e0,u_var,u_burst,u_fade;
out vec2 v_q;
out float v_radius;
out vec3 v_color;
const float PI=3.14159265359;
float h11(float n){return fract(sin(n*12.9898)*43758.5453);}
void main(){
    vec3 fw=normalize(u_look-u_cam),rt=normalize(cross(fw,vec3(0,1,0))),up=cross(rt,fw);
    float tf=tan(u_fov*.5),pxw=2.*tf/u_res.y;
    float r1=in_a.z,r2=in_a.w,r3=in_b.x,r4=in_b.y,id=in_b.z;
    float cluster=floor(r1*28.);
    vec3 center=vec3(h11(cluster+1.)-.5,h11(cluster+2.)-.5,h11(cluster+3.)-.5)*vec3(3.6,1.7,3.6)+vec3(0,1.05,0);
    float gr=sqrt(-2.*log(max(r2,1e-4)));
    vec3 gs=vec3(gr*cos(6.2832*r3),gr*sin(6.2832*r3),sqrt(-2.*log(max(r4,1e-4)))*cos(6.2832*fract(r1*7.)));
    vec3 cloud=center+gs*vec3(1.,.7,1.)*.16*(.5+h11(cluster+4.));
    float ca=(u_time-33.412)*.12;
    cloud.xz=mat2(cos(ca),-sin(ca),sin(ca),cos(ca))*cloud.xz;
    cloud=vec3(0,1.05,0)+(cloud-vec3(0,1.05,0))*(1.+.18*u_burst);
    if(id<2.5)cloud=u_sp[int(id)];
    float ringR=.30+1.96*in_c.z,omega=.09+.15*(1.-in_c.z);
    float angle=(in_c.x/5.4+1.)*PI+u_time*omega;
    vec3 ring=vec3(cos(angle)*ringR,sin(angle)*ringR,(in_c.y/3.3)*.42);
    vec3 p=mix(cloud,ring,u_bridge);
    vec3 delta=p-u_cam;float depth=dot(delta,fw);
    if(depth<.08){gl_Position=vec4(2,2,2,1);return;}
    vec2 screen=vec2(dot(delta,rt),dot(delta,up))/(depth*2.*tf);
    float cs=cos(u_roll),sn=sin(u_roll);screen=mat2(cs,sn,-sn,cs)*screen;
    screen=screen*u_res.y+.5*u_res;
    float oldEnergy=mix(u_e0,u_e0*(.3+1.4*r4*r4)*2.,u_var)*(1.+u_burst*2.*step(.7,r4));
    vec3 oldColor=fract(r1*97.)>.93?vec3(1.,.6,.32):vec3(.92,.91,.88);
    float oldRadius=.0048;
    if(id<.5){oldColor=vec3(1.);oldEnergy=2.6;oldRadius=.011;}
    else if(id<1.5){oldColor=vec3(1.,.62,.32);oldEnergy=2.2*u_fade;oldRadius=.0095;}
    else if(id<2.5){oldColor=vec3(1.,.78,.6);oldEnergy=1.8*u_fade;oldRadius=.009;}
    oldEnergy/=id<7920.?2.:1.;
    float newRadius=.0052*(.65+.65*in_c.w);
    float blur=u_aper*abs(depth-u_focus)/max(u_focus,.1);
    float oldRW=oldRadius+blur+pxw*depth*.8,newRW=newRadius+blur+pxw*depth*.6;
    vec3 oldInk=oldColor*oldEnergy*oldRadius*oldRadius/(oldRW*oldRW)*exp(-depth*.08);
    vec3 newColor=mix(vec3(.83,.86,.87),vec3(.96,.62,.29),step(.925,in_d.x));
    vec3 newInk=newColor*(.27+.52*in_c.w*in_c.w)*newRadius*newRadius/(newRW*newRW)*.74*exp(-depth*.035);
    float pixels=mix(oldRW,newRW,u_bridge)/(depth*2.*tf)*u_res.y;
    vec2 q=in_corner*pixels*mix(2.2,2.6,u_bridge);
    v_q=q;v_radius=pixels;v_color=mix(oldInk,newInk,u_bridge);
    gl_Position=vec4((screen+q)/u_res*2.-1.,0.,1.);
}
