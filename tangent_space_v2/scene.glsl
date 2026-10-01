out vec4 fragColor;
float ink(float d,float width,float aa){return 1.-smoothstep(width,width+aa,abs(d));}
void main(){
    camera();vec2 uv=(gl_FragCoord.xy-.5*u_res)/u_res.y;
    float c=cos(u_roll),s=sin(u_roll);uv=mat2(c,-s,s,c)*uv;
    vec3 ro=u_cam,rd=normalize(FW+2.*TF*(uv.x*RT+uv.y*UP));
    vec3 color=vec3(.0026,.0031,.0040);
    float glow=exp(-dot(uv-vec2(.14,-.04),uv-vec2(.14,-.04))*4.);
    color+=vec3(.002,.0023,.003)*glow;
    // Recipient first, with subsequent membranes correctly composited in depth.
    float recipient=sphereHit(ro,rd);
    if(recipient>0.){
        vec3 n=normalize(ro+rd*recipient-u_you);
        float light=dot(n,normalize(vec3(-.4,1.,1.)));
        color=vec3(1.,.96,.86)*(light>.3?1.05:(light>-.35?.65:.23));
        color+=vec3(.35,.23,.1)*pow(1.-abs(dot(n,-rd)),4.);
    }
    // The perimeter opens out of the point body, occupying the same locus.
    if(u_ringFade>.001){
        float den=rd.z;
        float d=abs(den)>.001?-ro.z/den:-1.;
        if(d>0.&&(recipient<0.||d<recipient)){
            vec2 q=(ro+rd*d).xy;float radius=length(q);
            float angle=mod(atan(q.y,q.x)+2.*PI,2.*PI);
            float reveal=1.-smoothstep(u_give*2.*PI-.025,u_give*2.*PI+.025,angle);
            float aa=PXW*d/max(abs(den),.25);
            float field=abs(radius-2.25)-.21;
            float face=(1.-smoothstep(-aa,aa,field))*reveal*u_ringFade;
            vec3 tint=vec3(.17,.165,.15)*(1.+.2*(radius-2.25)/.21);
            color=mix(color,tint,face*.42);
            color+=vec3(.48,.35,.19)*ink(field,.005,aa)*reveal*u_ringFade;
            color+=vec3(.095,.105,.12)*ink(radius-2.25,.002,aa)*reveal*u_ringFade;
        }
    }
    float depths[7];vec2 coords[7];float facings[7];
    for(int i=0;i<7;i++){
        depths[i]=planeHit(i,ro,rd,coords[i],facings[i]);
        if(u_growth[i]<.001)depths[i]=-1.;
    }
    // Seven real planar surfaces, sorted per ray for correct transparent overlap.
    for(int layer=0;layer<7;layer++){
        int id=-1;float far=0.;
        for(int i=0;i<7;i++)if(depths[i]>far){far=depths[i];id=i;}
        if(id<0)break;depths[id]=-1.;
        if(recipient>0.&&far>recipient)continue;
        vec2 q=coords[id];float facing=facings[id];
        float aa=PXW*far/max(facing,.22)+blurAt(far)*.26;
        float mask=planeMask(id,q,aa);
        if(mask<.001)continue;
        vec2 size=u_planes[id].zw*vec2(u_growth[id],sqrt(u_growth[id]));
        float sd=max(abs(q.x)-size.x,abs(q.y)-size.y);
        float rim=ink(sd,.004,aa)*mask;
        float lengthLine=ink(q.y,.0025,aa)*mask;
        float transverse=abs(fract((q.x+.12)/1.1)-.5)*1.1;
        float sections=ink(transverse,.0018,aa)*mask;
        float band=ink(abs(q.y)-size.y*.68,.0014,aa)*mask;
        vec3 tint=mix(vec3(.13,.16,.18),vec3(.23,.185,.125),float(id==3)*.62);
        tint*=.82+.22*q.y/max(size.y,.001);
        float alpha=(id==3?.49:.32)*mask;
        color=mix(color,tint,alpha);
        color+=mix(vec3(.28,.32,.34),vec3(.68,.44,.20),float(id==3))*(rim*.65+lengthLine*.22);
        color+=vec3(.085,.09,.10)*(sections*.30+band*.48);
        // The recipient's shadow anchors it to the central plane.
        if(id==3){
            float sh=exp(-dot(q/vec2(.18,.12),q/vec2(.18,.12))*1.4);
            color*=1.-.55*sh*u_quiet;
            float ring=ink(length(q)-.19,.003,aa)*exp(-max(u_time-39.22,0.)*3.);
            color+=vec3(.38,.27,.14)*ring*u_quiet;
        }
    }
    fragColor=vec4(color*u_weight,1.);
}
