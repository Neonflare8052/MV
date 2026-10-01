uniform vec3 u_recipient;
uniform float u_contactX,u_offer,u_landed,u_touch;
float tsEase(float x){x=clamp(x,0.,1.);return x*x*(3.-2.*x);}
float tsWave(float x){return .55+.35*sin(1.7*x+3.96-(u_time-37.067)*1.2)+.12*sin(3.3*x-2.7);}
float tsSlope(float x){return .595*cos(1.7*x+3.96-(u_time-37.067)*1.2)+.396*cos(3.3*x-2.7);}
float tsLine(float d,float w,float aa){return 1.-smoothstep(w,w+aa,abs(d));}
vec3 tsPlatform(vec3 ro,vec3 rd,float x,float visibility,bool active){
  float slope=tsSlope(x);
  vec3 p=vec3(x,tsWave(x),-.123076923);
  vec3 tangent=normalize(vec3(1.,slope,0.));
  vec3 n=normalize(vec3(-slope,1.,0.));
  float denominator=dot(rd,n);
  if(abs(denominator)<.0001)return vec3(0.);
  float d=dot(p-ro,n)/denominator;
  if(d<=0.)return vec3(0.);
  vec3 delta=ro+rd*d-p;
  vec2 q=vec2(dot(delta,tangent),delta.z);
  float aa=max(PXW*d,.0015)+blurAt(d)*.2;
  float halfLength=(active?.76:.40)*visibility;
  float end=1.-smoothstep(halfLength-aa,halfLength+aa,abs(q.x));
  vec3 color=vec3(0.);
  if(active){
    vec2 bound=abs(q)-vec2(halfLength,.19);
    float sd=max(bound.x,bound.y);
    float face=1.-smoothstep(-aa,aa,sd);
    float rim=tsLine(sd,.005,aa);
    color+=vec3(.075,.065,.050)*face*visibility;
    color+=vec3(.42,.29,.15)*rim*visibility;
    float contact=tsLine(length(q)-(.09+.18*(1.-u_touch)),.006,aa)*u_touch;
    color+=vec3(.50,.45,.32)*contact;
  }
  float ink=tsLine(q.y,active?.010:.006,aa)*end;
  color+=(active?vec3(.85,.62,.32):vec3(.15,.12,.08))*ink*visibility;
  return color;
}
vec3 supportScene(vec3 ro,vec3 rd){
  vec3 color=vec3(.004,.004,.005);
  for(int i=0;i<5;i++){
    float x=-1.65+float(i)*.8;
    float appear=tsEase((u_time-38.75-float(i)*.15)/.3);
    float quiet=1.-.7*exp(-pow((x-u_contactX)/.4,2.));
    color+=tsPlatform(ro,rd,x,appear*quiet,false);
  }
  color+=tsPlatform(ro,rd,u_contactX,u_offer,true);
  // The recipient is a compact white geometric body, physically touching the tangent.
  float radius=mix(.035,.072,tsEase((u_time-37.15)/1.25));
  vec3 oc=ro-u_recipient;
  float b=dot(oc,rd),disc=b*b-dot(oc,oc)+radius*radius;
  if(disc>0.){
    float dist=-b-sqrt(disc);
    if(dist>0.){
      vec3 n=normalize(ro+rd*dist-u_recipient);
      float light=dot(n,normalize(vec3(-.5,.9,1.)));
      float band=light>.45?1.1:(light>-.15?.68:.29);
      color=vec3(.94,.94,.90)*band;
      float rim=pow(1.-abs(dot(n,-rd)),4.);
      color+=vec3(.36,.23,.10)*rim;
    }
  }
  return color;
}
