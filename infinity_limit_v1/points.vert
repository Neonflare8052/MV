in vec2 in_corner;
in vec4 in_a,in_b;
out vec2 v_q;
out float v_radius;
out vec3 v_color;
void main(){
    camera();float x=in_a.x,z=in_a.y,phase=in_a.z,jitter=in_a.w;
    float ringR=.30+1.96*phase;
    float omega=.09+.15*(1.-phase);
    float baseAngle=(x/5.4+1.)*PI;
    float freezeTime=37.10;
    float angle=baseAngle+min(u_time,freezeTime)*omega;
    vec3 originalRing=vec3(cos(angle)*ringR,sin(angle)*ringR,(z/3.3)*.42);
    vec3 mappedRing=u_ringOrigin+u_ringX*originalRing.x+u_ringY*originalRing.y+u_ringZ*originalRing.z;
    vec3 ring=mix(originalRing,mappedRing,u_viewChange);
    // Keep each point's identity and angular order: each concentric ring becomes
    // one sine strand at its own depth. Outer rings lead, inner rings follow.
    float frozenAngle=mod(baseAngle+freezeTime*omega,2.*PI);
    x=(frozenAngle/PI-1.)*5.4;
    vec3 wave=vec3(x,waveField(x,z).x,z);
    float localProgress=clamp((u_unfold-.28*(1.-phase))/.72,0.,1.);
    float unfold=localProgress*localProgress*localProgress*(localProgress*(localProgress*6.-15.)+10.);
    vec3 p=mix(ring,wave,unfold);
    // Curl the strands into depth while opening, instead of straight interpolation.
    float curl=sin(PI*unfold);
    p+=vec3(.12*sin(frozenAngle),.30*sin(frozenAngle*.5),.70*cos(frozenAngle*.5))*curl;
    // Retain every point and its strand identity as the wave becomes a long flow.
    float column=(x/5.4+1.)*.5;
    float row=floor(phase*55.+.5);
    vec2 transverse=vec2((mod(row,7.)-3.)*.20,(floor(row/7.)-3.5)*.19);
    float freeDistance=4.9+85.*pow(1.-column,1.70)-3.*(u_time-41.4);
    float cover=smooth01((u_limit-max(abs(transverse.x)/u_planeExtent.x,abs(transverse.y)/u_planeExtent.y))/.09);
    float d=(freeDistance-.15)/.32;
    float limited=.15+.32*(max(d,0.)+log(1.+exp(-abs(d))));
    float streamDistance=mix(freeDistance,limited,cover);
    vec3 stream=u_you-u_flowDir*streamDistance+vec3(0.,transverse.x,0.)+u_flowSide*transverse.y;
    float progress=clamp((u_stretch-.16*column)/.84,0.,1.);
    float stretch=progress*progress*progress*(progress*(progress*6.-15.)+10.);
    p=mix(p,stream,stretch);
    vec3 delta=p-u_cam;float depth=dot(delta,FW);
    if(depth<.08){gl_Position=vec4(2.,2.,2.,1.);return;}
    vec2 screen=vec2(dot(delta,RT),dot(delta,UP))/(depth*2.*TF);
    float cs=cos(u_roll),sn=sin(u_roll);screen=mat2(cs,sn,-sn,cs)*screen;
    screen=screen*u_res.y+.5*u_res;
    vec3 rd=normalize(delta);float distance=length(delta);
    float transmission=1.;
    float sigmoid=1./(1.+exp(clamp(-d,-60.,60.)));
    transmission*=mix(1.,.06+.94*sigmoid,cover*stretch);
    if(u_limit>.001){
        vec2 q;float boundary=boundaryHit(u_cam,rd,q);
        if(boundary>0.&&boundary<distance-.005)transmission*=1.-boundaryMask(q,.002)*.32;
    }
    for(int i=0;i<7;i++)if(u_growth[i]>.001){
        vec2 q;float facing;float hit=planeHit(i,u_cam,rd,q,facing);
        if(hit>0.&&hit<distance-.005)transmission*=1.-planeMask(i,q,.002)*.56;
        // A narrow source ribbon is handed off from points to continuous vector surface.
        vec3 center,ex,ez,n;planeBasis(i,center,ex,ez,n);
        vec3 sourceOffset=wave-center;
        float stripDistance=dot(sourceOffset,ez)/.19;
        float stripDistance2=stripDistance*stripDistance;
        float strip=exp(-stripDistance2*stripDistance2);
        float span=1.-smoothstep(u_planes[i].z-.15,u_planes[i].z+.15,abs(dot(sourceOffset,ex)));
        transmission*=1.-.93*strip*span*u_growth[i];
    }
    float hit=sphereHit(u_cam,rd);
    if(hit>0.&&hit<distance)transmission=0.;
    vec2 quietDistance=vec2(x-.70,z/1.15);
    float peripheral=1.-.55*u_quiet*exp(-dot(quietDistance,quietDistance));
    float radius=mix(.0052,.010,stretch)*(.65+.65*jitter);
    float blur=blurAt(depth);
    float rw=radius+blur+PXW*depth*.60;
    float px=rw/(depth*2.*TF)*u_res.y;
    vec2 q=in_corner*px*2.6;
    v_q=q;v_radius=px;
    vec3 col=mix(vec3(.83,.86,.87),vec3(.96,.62,.29),step(.925,in_b.x));
    float perimeterHandoff=1.-.88*u_ringFade*u_give*smoothstep(2.03,2.11,ringR)*(1.-unfold);
    float amplitude=(.27+.52*jitter*jitter)*radius*radius/(rw*rw)*perimeterHandoff*mix(.74,1.,unfold);
    v_color=col*amplitude*transmission*peripheral*exp(-depth*mix(.035,.008,stretch));
    gl_Position=vec4((screen+q)/u_res*2.-1.,0.,1.);
}
