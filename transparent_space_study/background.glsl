// Three translucent sections remain in world space while the foreground changes.
// Their delayed arcs use the foreground ring radii and its actual wave equation.
uniform float u_bgStrength, u_ghostStrength;

float bgEase(float x) { x=clamp(x,0.,1.); return x*x*(3.-2.*x); }
float bgSeg(vec2 p,vec2 a,vec2 b) {
  vec2 v=b-a; float h=clamp(dot(p-a,v)/max(dot(v,v),1e-6),0.,1.);
  return length(p-a-h*v);
}
float bgInk(float d,float width,float aa) {
  float r=max(width+aa,1e-5);
  return width/r*exp(-2.*d*d/(r*r));
}
vec2 bgRemember(float th,float j,float unroll) {
  float r=.12+.045*j;
  vec2 circle=r*vec2(cos(th),sin(th));
  float x=(th/PI-1.)*2.2;
  float memoryTime=max(37.067,u_time-1.15);
  float y=.55+.35*sin(1.7*x+.22*j-(memoryTime-37.067)*1.2)
             +.12*sin(3.3*x-.15*j)-1.1;
  return mix(circle,vec2(x,y),unroll);
}

void bgSection(inout vec3 color,vec3 ro,vec3 rd,int layer,float show) {
  float k=float(layer);
  float align=bgEase((u_time-33.15)/3.10);
  float angle=mix(1.15,0.,align)+(.12-.10*align)*(k-1.);
  vec3 n=vec3(sin(angle),0.,cos(angle));
  vec3 ex=vec3(cos(angle),0.,-sin(angle)), ey=vec3(0.,1.,0.);
  vec3 center=vec3(0.,1.1,0.)-n*(3.+1.45*k)
             +ex*(.40*(k-1.)) + ey*(.12*(k-1.));
  float denominator=dot(rd,n);
  if(abs(denominator)<.015) return;
  float z=dot(center-ro,n)/denominator;
  if(z<=.05) return;
  vec3 hit=ro+rd*z-center;
  vec2 q=vec2(dot(hit,ex),dot(hit,ey));
  vec2 halfSize=vec2(4.10+.30*k,2.25+.15*k);
  vec2 over=abs(q)-halfSize;
  float boundary=max(over.x,over.y);
  float aa=max(PXW*z/max(abs(denominator),.20),.002)+blurAt(z)*.38;
  float inside=1.-smoothstep(-aa,aa,boundary);
  if(inside<.0001) return;

  // Face density changes gently with the angle: front-on it almost disappears.
  float grazing=1.-abs(denominator);
  float density=(.09+.14*grazing)*show*exp(-.035*z);
  float softInterior=1.-smoothstep(.55,1.05,length(q/halfSize));
  vec3 tint=mix(vec3(.013,.014,.016),vec3(.017,.014,.011),.14*k);
  color=mix(color,tint,density*inside*(.55+.45*softInterior));

  // Open boundaries, with interrupted corners, imply sheets rather than HUD boxes.
  float edgeD=abs(boundary);
  float cornerMask=1.-smoothstep(.74,.98,min(abs(q.x)/halfSize.x,abs(q.y)/halfSize.y));
  float edge=bgInk(edgeD,.012,aa)*inside*cornerMask;
  float slowEdge=.60+.25*sin(q.x*.9+q.y*.7+k*1.7);
  color+=vec3(.075,.080,.089)*edge*slowEdge*show*exp(-.028*z);

  // A handful of short connections are sampled from a wave section. No grid.
  float path=0.,dots=0.;
  for(int i=0;i<5;i++) {
    float fi=float(i);
    float x=-3.45+1.42*fi+.14*k;
    float j=8.+10.*k;
    float y=.20+.27*sin(x*1.7+.22*j)-.20*k;
    vec2 a=vec2(x,y), b=vec2(x+.33,y+.08*cos(1.7*x+.22*j));
    path+=bgInk(bgSeg(q,a,b),.009,aa);
    dots+=bgInk(length(q-a),.018,aa);
  }
  // A second sparse collection sits above the main figures, leaving their outline clear.
  float upper=0.;
  for(int i=0;i<3;i++) {
    float x=-2.35+2.05*float(i)+.22*k;
    float y=1.62+.10*sin(float(i)*1.5+k);
    vec2 a=vec2(x,y), b=a+vec2(.42,-.09);
    upper+=bgInk(bgSeg(q,a,b),.008,aa);
  }
  color+=(vec3(.062,.065,.069)*path+vec3(.085,.081,.075)*dots
         +vec3(.052,.055,.061)*upper)*show*inside*exp(-.035*z);

  // Earlier geometry persists after the foreground has already become a wave.
  float memory=bgEase((u_time-36.15)/.85)*(1.-bgEase((u_time-39.75)/.85));
  float unroll=bgEase((u_time-38.10-.10*k)/1.35);
  float j=16.+8.*k;
  float speed=5.*pow(.9,j), phase=speed*(37.067-33.412);
  float arc=0.;
  for(int i=0;i<12;i++) {
    float ta=.25+phase+float(i)*.175;
    vec2 a=bgRemember(ta,j,unroll), b=bgRemember(ta+.175,j,unroll);
    arc+=bgInk(bgSeg(q,a,b),.011,aa);
  }
  vec3 memoryColor=mix(vec3(.12,.123,.13),vec3(.135,.084,.049),step(1.5,k));
  color+=memoryColor*arc*memory*u_ghostStrength*show*inside*exp(-.03*z);
}

vec3 studyBackground(vec3 ro,vec3 rd) {
  vec3 color=vec3(.004,.004,.005);
  float show=bgEase((u_time-32.35)/1.10)*(1.-bgEase((u_time-40.45)/1.20))*u_bgStrength;
  if(show<=.0001) return color;
  // Centers are spaced behind the main mathematical forms. Far planes composite first.
  bgSection(color,ro,rd,2,show);
  bgSection(color,ro,rd,1,show);
  bgSection(color,ro,rd,0,show);
  return color;
}
