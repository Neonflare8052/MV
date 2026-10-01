uniform vec2 u_res;
uniform float u_time,u_weight,u_fov,u_focus,u_aper,u_roll;
uniform vec3 u_cam,u_look,u_you;
uniform float u_unfold,u_quiet,u_clock,u_give,u_ringFade;
uniform float u_dip,u_contactAngle,u_ringContact,u_catchPulse,u_landed,u_impact;
uniform vec4 u_planes[7]; // contact x, z, half length, half width
uniform float u_growth[7];
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
    float a=1.19*x+.40*z-u_clock;
    float b=2.12*x-.27*z+u_clock*.34;
    float h=.68*sin(a)+.18*sin(b);
    float dx=.8092*cos(a)+.3816*cos(b);
    float dz=.272*cos(a)-.0486*cos(b);
    vec2 falloff=vec2((x-.70)/1.65,z/3.8);
    float z2=falloff.y*falloff.y;
    float e=exp(-falloff.x*falloff.x-z2*z2);
    float calm=u_quiet*e;
    float cx=calm*(-2.*(x-.70)/(1.65*1.65));
    float cz=calm*(-4.*z*z*z/(3.8*3.8*3.8*3.8));
    float rest=.24+u_dip;
    return vec3(mix(h,rest,calm),dx*(1.-calm)+(rest-h)*cx,dz*(1.-calm)+(rest-h)*cz);
}
void planeBasis(int i,out vec3 center,out vec3 ex,out vec3 ez,out vec3 n){
    vec4 p=u_planes[i];vec3 f=waveField(p.x,p.y);
    center=vec3(p.x,f.x,p.y);
    n=normalize(vec3(-f.y,1.,-f.z));ex=normalize(vec3(1.,f.y,0.));
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
