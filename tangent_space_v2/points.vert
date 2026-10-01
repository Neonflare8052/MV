in vec2 in_corner;
in vec4 in_a,in_b;
out vec2 v_q;
out float v_radius;
out vec3 v_color;
void main(){
    camera();float x=in_a.x,z=in_a.y,phase=in_a.z,jitter=in_a.w;
    float ringR=.30+1.96*phase;
    float angle=(x/5.4+1.)*PI+u_time*(.09+.15*(1.-phase));
    vec3 ring=vec3(cos(angle)*ringR,sin(angle)*ringR,(z/3.3)*.42);
    // Unroll the circular body into an entire landscape, not the old small patch.
    vec3 wave=vec3(x,waveField(x,z).x,z);
    float unfold=smooth01((u_unfold-.08*jitter)/.92);
    vec3 p=mix(ring,wave,unfold);
    vec3 delta=p-u_cam;float depth=dot(delta,FW);
    if(depth<.08){gl_Position=vec4(2.,2.,2.,1.);return;}
    vec2 screen=vec2(dot(delta,RT),dot(delta,UP))/(depth*2.*TF);
    float cs=cos(u_roll),sn=sin(u_roll);screen=mat2(cs,sn,-sn,cs)*screen;
    screen=screen*u_res.y+.5*u_res;
    vec3 rd=normalize(delta);float distance=length(delta);
    float transmission=1.;
    for(int i=0;i<7;i++)if(u_growth[i]>.001){
        vec2 q;float facing;float hit=planeHit(i,u_cam,rd,q,facing);
        if(hit>0.&&hit<distance-.005)transmission*=1.-planeMask(i,q,.002)*.56;
        // A narrow source ribbon is handed off from points to continuous vector surface.
        float stripDistance=(z-u_planes[i].y)/.19;
        float stripDistance2=stripDistance*stripDistance;
        float strip=exp(-stripDistance2*stripDistance2);
        float span=1.-smoothstep(u_planes[i].z-.15,u_planes[i].z+.15,abs(x-u_planes[i].x));
        transmission*=1.-.93*strip*span*u_growth[i];
    }
    float hit=sphereHit(u_cam,rd);
    if(hit>0.&&hit<distance)transmission=0.;
    vec2 quietDistance=vec2(x-.70,z/1.15);
    float peripheral=1.-.55*u_quiet*exp(-dot(quietDistance,quietDistance));
    float radius=.0052*(.65+.65*jitter);
    float blur=blurAt(depth);
    float rw=radius+blur+PXW*depth*.60;
    float px=rw/(depth*2.*TF)*u_res.y;
    vec2 q=in_corner*px*2.6;
    v_q=q;v_radius=px;
    vec3 col=mix(vec3(.83,.86,.87),vec3(.96,.62,.29),step(.925,in_b.x));
    float perimeterHandoff=1.-.88*u_ringFade*u_give*smoothstep(2.03,2.11,ringR)*(1.-unfold);
    float amplitude=(.27+.52*jitter*jitter)*radius*radius/(rw*rw)*perimeterHandoff;
    v_color=col*amplitude*transmission*peripheral*exp(-depth*.035);
    gl_Position=vec4((screen+q)/u_res*2.-1.,0.,1.);
}
