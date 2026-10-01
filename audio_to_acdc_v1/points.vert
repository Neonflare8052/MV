in vec2 in_corner;
in vec4 in_a,in_b;
out vec2 v_q;
out float v_radius;
out vec3 v_color;
out vec3 v_world;
out float v_captured,v_streamDistance;
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
    // Points already ahead of the ball keep going right and leave the frame.
    // Only the rear field stretches into depth: no front points are pulled back.
    float sourceDistance=dot(u_releasePoint-vec3(x,0.,z),u_flowDir);
    float baseDistance=sourceDistance+1.8*pow(max(sourceDistance,0.),2.);
    vec3 freePoint=u_streamOrigin-u_flowDir*baseDistance+vec3(0.,transverse.x,0.)+u_flowSide*transverse.y;
    float freeDistance=dot(u_you-freePoint,u_flowDir);
    float activation=u_rowActivation[int(row)];
    float distanceAtActivation=baseDistance-3.*(activation-u_releaseTime);
    float cover=float(u_time>=activation&&distanceAtActivation>.15);
    float initial=max((distanceAtActivation-.15)/.32,.0001);
    float z0=initial>20.?initial:log(exp(initial)-1.);
    float d=z0-3.*max(0.,u_time-activation)/.32;
    float limited=.15+.32*(max(d,0.)+log(1.+exp(-abs(d))));
    float streamDistance=mix(freeDistance,limited,cover);
    vec3 stream=freePoint+u_flowDir*(freeDistance-streamDistance);
    // Gently bend only the remote guide into depth. Local incoming motion at
    // the boundary remains along the exact release direction.
    vec3 farDirection=normalize(vec3(.75,0.,.6614));
    float distanceIntoDepth=max(streamDistance,0.);
    float remoteCurve=distanceIntoDepth-4.*(1.-exp(-distanceIntoDepth/4.));
    stream-=(farDirection-u_flowDir)*remoteCurve;
    float progress=clamp((u_stretch-.16*column)/.84,0.,1.);
    float stretch=progress*progress*progress*(progress*(progress*6.-15.)+10.);
    // The shared gravitational translation is not part of the shape tween.
    p=mix(p,stream-u_freeFall,stretch)+u_freeFall;
    float currentBlend=u_switch*cover;
    float run=mod(in_b.z*4.8+u_currentTravel+9.6,4.8);
    float currentDistance=4.8-run;
    vec3 conductor=u_you-u_flowDir*currentDistance-vec3(0.,.078,0.)
        +u_flowSide*((floor(row/7.)-3.5)*.12)+vec3(0.,(mod(row,7.)-3.)*.008,0.);
    p=mix(p,conductor,currentBlend);
    v_world=p;v_captured=cover;v_streamDistance=streamDistance;
    vec3 delta=p-u_cam;float depth=dot(delta,FW);
    if(depth<.08){gl_Position=vec4(2.,2.,2.,1.);return;}
    vec2 screen=vec2(dot(delta,RT),dot(delta,UP))/(depth*2.*TF);
    float cs=cos(u_roll),sn=sin(u_roll);screen=mat2(cs,sn,-sn,cs)*screen;
    screen=screen*u_res.y+.5*u_res;
    vec3 rd=normalize(delta);float distance=length(delta);
    float transmission=1.;
    float sigmoid=1./(1.+exp(clamp(-d,-60.,60.)));
    float oldEnergy=mix(1.,.06+.94*sigmoid,cover*stretch);
    float edgeFade=smoothstep(0.,.16,run)*smoothstep(0.,.16,4.8-run);
    transmission*=mix(oldEnergy,.28*edgeFade,currentBlend);
    transmission*=1.-u_switch*(1.-cover);
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
    float radius=mix(mix(.0052,.010,stretch),.006,currentBlend)*(.65+.65*jitter);
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
