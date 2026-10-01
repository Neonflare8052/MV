uniform vec2 u_res;
uniform float u_time,u_weight,u_fov,u_focus,u_aper,u_roll;
uniform vec3 u_cam,u_look,u_you;
uniform float u_unfold,u_quiet,u_clock,u_give,u_ringFade;
uniform float u_viewChange;
uniform vec3 u_ringOrigin,u_ringX,u_ringY,u_ringZ;
uniform float u_contactAngle,u_ringContact,u_catchPulse,u_landed,u_impact;
uniform vec2 u_waveDir,u_dips[3];
uniform int u_activePlane;
uniform vec4 u_planes[7]; // contact x, z, half length, half width
uniform float u_growth[7];
uniform float u_stretch,u_limit,u_limitPulse;
uniform vec3 u_flowDir,u_flowSide;
uniform vec3 u_streamOrigin,u_freeFall;
uniform vec3 u_releasePoint;
uniform float u_releaseTime,u_rowActivation[56];
uniform vec2 u_planeExtent;
const float PI=3.14159265359;
vec3 FW,RT,UP;
float TF,PXW;
void camera(){
    FW=normalize(u_look-u_cam); RT=normalize(cross(FW,vec3(0,1,0)));
    UP=cross(RT,FW);TF=tan(u_fov*.5);PXW=2.*TF/u_res.y;
}
float smooth01(float x){x=clamp(x,0.,1.);return x*x*(3.-2.*x);}
float blurAt(float d){return u_aper*abs(d-u_focus)/max(u_focus,.1);}
// Exact height and partial derivatives of the same surface used by the cloud.
vec3 waveField(float x,float z){
    vec2 side=vec2(-u_waveDir.y,u_waveDir.x);
    vec2 rel=vec2(x-.70,z);
    float q=dot(rel,u_waveDir),r=dot(rel,side);
    float a=1.19*q+u_clock;
    float h=.76*sin(a)+.045*(cos(.9*r)-1.);
    float dq=.9044*cos(a),dr=-.0405*sin(.9*r);
    for(int i=0;i<3;i++){
        float localq=q-u_dips[i].x;
        float dip=u_dips[i].y*exp(-localq*localq/.64-r*r/1.21);
        h+=dip;dq+=dip*(-2.*localq/.64);dr+=dip*(-2.*r/1.21);
    }
    vec2 gradient=dq*u_waveDir+dr*side;
    return vec3(h,gradient.x,gradient.y);
}
void planeBasis(int i,out vec3 center,out vec3 ex,out vec3 ez,out vec3 n){
    vec4 p=u_planes[i];vec3 f=waveField(p.x,p.y);
    center=vec3(p.x,f.x,p.y);
    n=normalize(vec3(-f.y,1.,-f.z));
    ex=normalize(vec3(u_waveDir.x,dot(f.yz,u_waveDir),u_waveDir.y));
    ez=normalize(cross(ex,n));
}
float planeHit(int i,vec3 ro,vec3 rd,out vec2 uv,out float facing){
    vec3 center,ex,ez,n;planeBasis(i,center,ex,ez,n);
    facing=abs(dot(rd,n));float den=dot(rd,n);
    if(abs(den)<.00001){uv=vec2(999.);return -1.;}
    float t=dot(center-ro,n)/den;
    vec3 d=ro+rd*t-center;uv=vec2(dot(d,ex),dot(d,ez));return t;
}
float planeMask(int i,vec2 uv,float aa){
    vec2 size=u_planes[i].zw*vec2(u_growth[i],sqrt(u_growth[i]));
    return (1.-smoothstep(-aa,aa,max(abs(uv.x)-size.x,abs(uv.y)-size.y)))*u_growth[i];
}
float sphereHit(vec3 ro,vec3 rd){
    vec3 q=ro-u_you;float b=dot(q,rd),h=b*b-dot(q,q)+.105*.105;
    return h>0.?-b-sqrt(h):-1.;
}
float boundaryHit(vec3 ro,vec3 rd,out vec2 uv){
    float den=dot(rd,u_flowDir);
    if(abs(den)<.00001){uv=vec2(999.);return -1.;}
    float t=dot(u_you-ro,u_flowDir)/den;
    vec3 local=ro+rd*t-u_you;
    uv=vec2(local.y,dot(local,u_flowSide));return t;
}
float boundaryMask(vec2 uv,float aa){
    vec2 extent=u_planeExtent*u_limit;
    return (1.-smoothstep(-aa,aa,max(abs(uv.x)-extent.x,abs(uv.y)-extent.y)))*smooth01(u_limit*8.);
}
