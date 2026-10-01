#version 330
// t02 · only god: pure black; a star passes the camera and dives behind an unseen black hole.
// Photon paths are integrated in Schwarzschild geometry (r_s = 1): a = -1.5 h^2 x / r^5.
uniform vec2  u_res;
uniform float u_time, u_weight;
uniform vec3  u_cam;      // camera position
uniform vec3  u_look;     // look-at point
uniform float u_fov;      // vertical fov (radians)
uniform vec3  u_star;     // star centre
uniform float u_rstar;    // star radius
uniform float u_glow;     // halo strength
uniform float u_bright;   // star brightness
uniform float u_corona;   // corona strength
uniform float u_sky;      // the sky behind it: stars, the galaxy's band, the celestial grid (0 .. 1)
uniform float u_grid;     // the grid alone
uniform vec3  u_trail[4]; // where the star was (older and older)
uniform float u_rev;      // how wide the sky it brings (radians)
uniform float u_gather;   // the sky drawn in to one circle (the next shot's ring)
uniform vec2  u_ringC;    // that circle, px
uniform float u_ringR;
uniform float u_shadowR;  // the shadow's radius on screen, px
out vec4 fragColor;

float h13(vec3 p3){ p3=fract(p3*.1031); p3+=dot(p3,p3.zyx+31.32); return fract((p3.x+p3.y)*p3.z); }
float vn3(vec3 p){ vec3 i=floor(p),f=fract(p); f=f*f*(3.-2.*f);
  float a=mix(mix(h13(i),h13(i+vec3(1,0,0)),f.x),mix(h13(i+vec3(0,1,0)),h13(i+vec3(1,1,0)),f.x),f.y);
  float b=mix(mix(h13(i+vec3(0,0,1)),h13(i+vec3(1,0,1)),f.x),mix(h13(i+vec3(0,1,1)),h13(i+vec3(1,1,1)),f.x),f.y);
  return mix(a,b,f.z); }

float fbm3(vec3 p){ float s=0.,a=.5; for(int i=0;i<4;i++){ s+=a*vn3(p); p=p*2.03+1.7; a*=.5; } return s; }
// a layer of stars on the sphere: one candidate per cell of a grid in direction space
float starLayer(vec3 d, float sc, float thr, float sz){
  vec3 p=d*sc, c=floor(p);
  float best=0.;
  for(int k=0;k<8;k++){
    vec3 cc=c+vec3(k&1,(k>>1)&1,(k>>2)&1);
    float h=h13(cc*1.37+11.);
    if(h<thr) continue;
    vec3 o=vec3(h13(cc+2.1),h13(cc+5.3),h13(cc+8.7));
    vec3 sp=normalize(cc+o)/1.;
    float dd=length(normalize(d)-normalize(sp))*sc;
    best=max(best,exp(-dd*dd/sz)*(.35+.65*h13(cc+9.9)));
  }
  return best;
}
vec3 sky(vec3 d){
  vec3 c=vec3(0.);
  c+=vec3(.85,.9,1.)*starLayer(d,160.,.95,.012)*.8;
  c+=vec3(1.,.95,.88)*starLayer(d,70.,.96,.01)*1.5;
  c+=vec3(1.,.93,.85)*starLayer(d,420.,.94,.02)*.3;
  // the galaxy's band, across the frame behind the hole, with dust lanes
  vec3 n=normalize(vec3(.55,.83,.08));
  float b=dot(d,n);
  float band=exp(-b*b/.01)*(.4+1.*fbm3(d*7.));
  float dust=smoothstep(.45,.75,fbm3(d*11.+4.))*exp(-b*b/.004);
  c+=vec3(.9,.82,.72)*band*(1.-.85*dust)*.035;
  c+=vec3(.8,.85,1.)*starLayer(d,700.,.85,.03)*band*.6;
  return c;
}

vec3 starColor(vec3 hitDir, float limb){
  float gran=vn3(hitDir*22.+u_time*.3)*.5+vn3(hitDir*61.)*.5;
  gran=smoothstep(.25,.75,gran);
  vec3 c=mix(vec3(1.,.72,.45),vec3(1.,.93,.82),limb);          // limb darkening reddens the edge
  return c*u_bright*(.2+.8*pow(limb,.6))*(.72+.45*gran);
}

void main(){
  vec2 uv=(gl_FragCoord.xy-.5*u_res)/u_res.y;
  vec3 fw=normalize(u_look-u_cam), rt=normalize(cross(fw,vec3(0,1,0))), up=cross(rt,fw);
  vec3 dir=normalize(fw+(uv.x*rt+uv.y*up)*2.*tan(u_fov*.5));

  vec3 pos=u_cam, vel=dir;
  vec3 hc=cross(pos,vel); float h2=dot(hc,hc);
  vec3 col=vec3(0.);
  vec3 halo=vec3(1.,.82,.62);
  float fate=0.;                                                // 0 escaped, 1 captured, 2 the star
  for(int i=0;i<520;i++){
    float r=length(pos);
    if(r<1.){ fate=1.; break; }                                  // captured: the shadow
    float ds=clamp(.04+.07*(r-1.),.03,1.2);
    vec3 acc=-1.5*h2*pos/pow(r,5.);
    vec3 v1=vel+acc*ds*.5;
    vec3 np=pos+v1*ds;
    float rn=length(np);
    vec3 v2=v1-1.5*h2*np/pow(rn,5.)*ds*.5;
    // star: closest approach of this segment
    vec3 seg=np-pos; float L=length(seg);
    vec3 sd=seg/max(L,1e-6);
    float tt=clamp(dot(u_star-pos,sd),0.,L);
    vec3 cp=pos+sd*tt; float d=length(cp-u_star);
    col+=halo*u_glow*exp(-(max(d-u_rstar,0.))*4.)*L*.05/(1.+d*d*.8);
    // corona: radial streamers anchored to the star, thin inner glow
    if(d>u_rstar && d<u_rstar*3.2){
      vec3 cd=normalize(cp-u_star);
      float h=(d-u_rstar)/u_rstar;
      float str=pow(vn3(cd*5.+vec3(0.,0.,u_time*.05)),2.2)*1.4+pow(vn3(cd*13.+3.),3.)*.8;
      float cor=str*exp(-max(h,0.)*2.6)+exp(-max(h,0.)*10.)*.6;
      col+=vec3(1.,.86,.7)*cor*u_corona*L/u_rstar*.9;
    }
    if(d<u_rstar){
      float limb=sqrt(max(1.-d*d/(u_rstar*u_rstar),0.));
      vec3 surf=cp-sd*sqrt(max(u_rstar*u_rstar-d*d,0.));
      col+=starColor(normalize(surf-u_star),limb);
      fate=2.;
      break;
    }
    pos=np; vel=v2;
    if(rn>60. && dot(pos,vel)>0.) break;                       // escaped: empty sky
  }
  // where it escaped: the sky it came from, bent round the hole
  vec3 sd=normalize(vel);
  float lon=atan(sd.x,-sd.z), lat=asin(clamp(sd.y,-1.,1.));
  vec2 g=vec2(lon/radians(15.),lat/radians(10.));
  vec2 fg=fwidth(g)+1e-5;
  vec2 gl=abs(fract(g+.5)-.5)/fg;
  float grid=1.-smoothstep(.6,1.6,min(gl.x,gl.y));
  vec2 g2=vec2(lon/radians(5.),lat/radians(5.));
  vec2 gl2=abs(fract(g2+.5)-.5)/(fwidth(g2)+1e-5);
  float fine=1.-smoothstep(.5,1.2,min(gl2.x,gl2.y));
  float eq=1.-smoothstep(.8,2.2,abs(lat)/fwidth(lat)+0.);
  float calm=clamp(1.-max(fg.x,fg.y)*6.,0.,1.);                 // where the sky is stretched to nothing, the grid lets go
  vec3 gold=vec3(.95,.72,.4);
  // the sky comes with the star: around it, and a fading wake along where it came from; only in a band round the hole
  float ang=acos(clamp(dot(sd,normalize(u_star)),-1.,1.));
  float rev=smoothstep(u_rev,u_rev*.35,ang);
  for(int k=0;k<4;k++){
    float a2=acos(clamp(dot(sd,normalize(u_trail[k])),-1.,1.));
    rev=max(rev,smoothstep(u_rev*.7,u_rev*.2,a2)*(.55-.12*float(k)));
  }
  float rs=length(gl_FragCoord.xy-u_ringC);
  float band=smoothstep(u_shadowR*.98,u_shadowR*1.1,rs)*(1.-smoothstep(u_shadowR*1.55,u_shadowR*2.3,rs));
  // gathering: the band closes in on one circle
  float gw=mix(u_shadowR*1.2,6.,u_gather*u_gather);
  float gband=1.-smoothstep(gw*.3,gw,abs(rs-u_ringR));
  band=mix(band,gband*band+gband*u_gather,u_gather);
  if(fate<.5){
    col+=sky(sd)*u_sky*rev*band*(1.+2.5*u_gather);
    col+=gold*(.16*grid+.05*fine+.12*eq)*calm*u_grid;
  }
  // the gathered circle: faint, strongest where the star's arcs are (left and right), so the next shot's arcs take over
  vec2 rv=(gl_FragCoord.xy-u_ringC)/max(rs,1.);
  float side=.25+.75*abs(rv.x);
  col+=vec3(1.,.95,.88)*u_gather*u_gather*side*(1.-smoothstep(1.2,3.5,abs(rs-u_ringR)))*.35;
  fragColor=vec4(col*u_weight,1.);
}
