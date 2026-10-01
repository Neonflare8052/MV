// Translucent mathematical cross-sections. Broad surfaces, not panel borders.
uniform float u_bgStrength, u_ghostStrength;
float bgEase(float x){x=clamp(x,0.,1.);return x*x*(3.-2.*x);}
float bgInk(float d,float w,float aa){return 1.-smoothstep(w,w+aa,abs(d));}
float bgSeg(vec2 p,vec2 a,vec2 b){vec2 v=b-a;return length(p-a-v*clamp(dot(p-a,v)/max(dot(v,v),1e-6),0.,1.));}

void bgSurface(inout vec3 color,vec3 ro,vec3 rd,int index,float strength){
  float k=float(index);
  float align=bgEase((u_time-33.)/3.1);
  float az=mix(1.1,0.,align)+(.22-.05*align)*(k-1.);
  float tilt=(k-1.)*.15;
  vec3 n=normalize(vec3(sin(az),tilt,cos(az)));
  vec3 ex=normalize(cross(vec3(0.,1.,0.),n));
  vec3 ey=cross(n,ex);
  float drift=bgEase((u_time-36.8)/2.2);
  float shift=k<.5?-2.35:(k<1.5?2.2:.15);
  vec3 center=vec3(0.,1.1,0.)-n*(2.8+1.3*k)
             +ex*shift+ey*(k<.5?.40:(k<1.5?-.60:1.40));
  float den=dot(rd,n);
  if(abs(den)<.01)return;
  float depth=dot(center-ro,n)/den;
  if(depth<=.05)return;
  vec3 delta=ro+rd*depth-center;
  vec2 q=vec2(dot(delta,ex),dot(delta,ey));
  float aa=max(.003,PXW*depth/max(abs(den),.2))+blurAt(depth)*.25;
  float radius=2.05+.30*k;
  float ring=length(q)-radius;
  float j=16.+8.*k;
  float time=max(37.067,u_time-.70-.22*k);
  float wy=.70*sin(1.1*q.x+.22*j-(time-37.067)*1.2)
           +.24*sin(2.15*q.x-.15*j);
  float dy=.77*cos(1.1*q.x+.22*j-(time-37.067)*1.2)
           +.516*cos(2.15*q.x-.15*j);
  float wave=(q.y-wy)/sqrt(1.+dy*dy);
  float unfold=bgEase((u_time-36.75-.3*k)/1.8);
  float field=mix(ring,wave,unfold);
  float halfWidth=.42+.11*k;
  float membrane=1.-smoothstep(halfWidth,halfWidth+aa,abs(field));
  float trim=1.-smoothstep(3.75,4.30,abs(q.x));
  trim*=1.-smoothstep(2.75,3.20,abs(q.y));
  // A gap in the closed section persists as the surface unfolds.
  float angle=atan(q.y,q.x);
  float gap=1.-(1.-smoothstep(.24,.36,abs(angle+.5+k*.33)))*(1.-unfold);
  membrane*=trim*gap;
  if(membrane<.0001)return;

  // Transmitted far layers remain visible at the intersections.
  float opacity=(.37-.065*k)*membrane*strength;
  float across=clamp(.5+.5*field/halfWidth,0.,1.);
  float light=.65+.35*pow(1.-abs(den),.5);
  vec3 tint=mix(vec3(.19,.205,.22),vec3(.23,.195,.16),k*.12);
  tint*=light*(.66+.44*across);
  color=mix(color,tint,clamp(opacity,0.,.72));

  // Isolines and transverse sections describe the membrane's shape.
  float bands=abs(fract((field+halfWidth)/.145)-.5)*.145;
  float iso=bgInk(bands,.004,aa)*membrane;
  float along=mix(angle*radius,q.x,unfold);
  float sections=abs(fract(along/.38)-.5)*.38;
  float sectionInk=bgInk(sections,.0035,aa)*membrane;
  float rim=bgInk(abs(field)-halfWidth,.009,aa)*trim*gap;
  color+=(vec3(.105,.116,.128)*iso*.55+vec3(.095,.096,.10)*sectionInk*.34
          +vec3(.26,.275,.285)*rim)*strength;

  // Sparse intersections lie on the surface and turn with it.
  float nodes=bgInk(bands,.009,aa)*bgInk(sections,.012,aa)*membrane;
  color+=vec3(.23,.185,.135)*nodes*.75*strength;
}

void bgMemory(inout vec3 color,vec3 ro,vec3 rd,float strength){
  float life=bgEase((u_time-36.4)/.8)*(1.-bgEase((u_time-40.1)/.8));
  if(life<.001)return;
  vec3 n=normalize(vec3(-.10,.05,1.));
  vec3 ex=normalize(cross(vec3(0.,1.,0.),n)),ey=cross(n,ex);
  vec3 center=vec3(-2.25,1.62,-2.35);
  float den=dot(rd,n);
  if(abs(den)<.01)return;
  float z=dot(center-ro,n)/den;
  if(z<.05)return;
  vec3 hit=ro+rd*z-center;
  vec2 q=vec2(dot(hit,ex),dot(hit,ey));
  float aa=max(.003,PXW*z/max(abs(den),.2))+blurAt(z)*.22;
  float unroll=bgEase((u_time-38.7)/1.55);
  float ink=0.,dots=0.;
  for(int curve=0;curve<3;curve++){
    float j=16.+8.*float(curve),r=.12+.045*j;
    for(int i=0;i<36;i++){
      float t0=.2+float(i)*.15,t1=t0+.15;
      vec2 a=r*vec2(cos(t0),sin(t0)),b=r*vec2(cos(t1),sin(t1));
      float xa=(t0/PI-1.)*2.2,xb=(t1/PI-1.)*2.2;
      float delayed=u_time-1.6-37.067;
      vec2 wa=vec2(xa,-.55+.35*sin(1.7*xa+.22*j-delayed*1.2)+.12*sin(3.3*xa-.15*j));
      vec2 wb=vec2(xb,-.55+.35*sin(1.7*xb+.22*j-delayed*1.2)+.12*sin(3.3*xb-.15*j));
      a=mix(a,wa,unroll); b=mix(b,wb,unroll);
      ink=max(ink,bgInk(bgSeg(q,a,b),.010,aa));
      if(i%3==0)dots=max(dots,bgInk(length(q-a),.024,aa));
    }
  }
  color+=(vec3(.30,.245,.18)*ink+vec3(.23,.24,.24)*dots)*life*strength;
}

vec3 studyBackground(vec3 ro,vec3 rd){
  vec3 color=vec3(.004,.004,.005);
  float show=bgEase((u_time-32.3)/.8)*(1.-.25*bgEase((u_time-40.45)/1.2));
  if(u_bgStrength<=.0001)return color;
  bgSurface(color,ro,rd,2,show*u_bgStrength);
  bgSurface(color,ro,rd,1,show*u_bgStrength);
  bgSurface(color,ro,rd,0,show*u_bgStrength);
  bgMemory(color,ro,rd,show*u_ghostStrength*u_bgStrength);
  return color;
}
