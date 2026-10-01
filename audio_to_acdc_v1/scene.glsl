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
            float field=abs(radius-2.25)-.15;
            float face=(1.-smoothstep(-aa,aa,field))*reveal*u_ringFade;
            vec3 tint=vec3(.17,.165,.15)*(1.+.2*(radius-2.25)/.15);
            color=mix(color,tint,face*.42);
            color+=vec3(.48,.35,.19)*ink(field,.005,aa)*reveal*u_ringFade;
            color+=vec3(.095,.105,.12)*ink(radius-2.25,.002,aa)*reveal*u_ringFade;
            float angleGap=atan(sin(u_contactAngle-angle),cos(u_contactAngle-angle));
            float contact=exp(-angleGap*angleGap/.013)*u_ringContact;
            float trail=exp(-max(angleGap,0.)*5.)*smoothstep(-.012,.02,angleGap)*u_ringContact;
            color+=vec3(.72,.43,.17)*ink(radius-2.10,.012,aa)*(contact*.65+trail*.38);
            color+=vec3(.28,.20,.11)*face*contact*(.4+u_catchPulse);
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
        float attention=float(id==u_activePlane);
        vec3 tint=mix(vec3(.13,.16,.18),vec3(.23,.185,.125),attention*.62);
        tint*=.82+.22*q.y/max(size.y,.001);
        float alpha=mix(.32,.49,attention)*mask;
        color=mix(color,tint,alpha);
        color+=mix(vec3(.28,.32,.34),vec3(.68,.44,.20),attention)*(rim*.65+lengthLine*.22);
        color+=vec3(.085,.09,.10)*(sections*.30+band*.48);
        // The recipient's shadow anchors it to the central plane.
        if(id==u_activePlane){
            vec3 c,e,z,n;planeBasis(id,c,e,z,n);
            vec3 offset=u_you-c;vec2 contact=q-vec2(dot(offset,e),dot(offset,z));
            float sh=exp(-dot(contact/vec2(.18,.12),contact/vec2(.18,.12))*1.4);
            color*=1.-.55*sh*u_landed;
            float ring=ink(length(contact)-(.19+.24*(1.-u_impact)),.003,aa)*u_impact;
            color+=vec3(.38,.27,.14)*ring;
        }
    }
    if(u_limit>.0001){
        vec2 q;float distance=boundaryHit(ro,rd,q);
        if(distance>0.&&(recipient<0.||distance<recipient)){
            vec3 center,ex,ez,n;boundaryFrame(center,ex,ez,n);
            float aa=PXW*distance/max(abs(dot(rd,n)),.25);
            float mask=boundaryMask(q,aa);
            vec2 size=boundaryExtent();
            float edge=ink(max(abs(q.x)-size.x,abs(q.y)-size.y),.003,aa)*mask;
            float centerLine=ink(q.y,.0017,aa)*mask;
            float horizontal=ink(q.x,.0012,aa)*mask;
            // Thin vector membrane: its only origin is the recipient itself.
            color=mix(color,vec3(.13,.145,.16),mask*.17);
            color+=vec3(.52,.40,.25)*edge*(.55+.22*u_limitPulse);
            color+=vec3(.42,.43,.43)*centerLine*.36;
            color+=vec3(.28,.24,.18)*horizontal*.22;
            float originGlow=exp(-length(q)*9.);
            color+=vec3(.27,.19,.10)*originGlow*mask;
            if(u_switch>.001){
                // A signed AC trace changes into a positive constant DC level.
                // It is part of the hinged surface, not a separate screen overlay.
                float theta=(q.x+size.x)*3.7-u_signalClock;
                float value=.22*mix(sin(theta),1.,u_dc);
                float slope=.814*cos(theta)*(1.-u_dc);
                float trace=ink((q.y-value)/sqrt(1.+slope*slope),.0035,aa)*mask;
                float rail=ink(abs(q.y)-.52,.002,aa)*mask;
                color+=vec3(.89,.54,.23)*trace*u_switch*.9;
                color+=vec3(.29,.31,.32)*rail*u_switch*.30;
                float carrier=mod((q.x+size.x)+u_currentTravel,1.2);
                float beads=exp(-pow((carrier-.60)/.055,2.))*rail;
                color+=vec3(.92,.85,.69)*beads*u_switch*.7;
            }
        }
    }
    fragColor=vec4(color*u_weight,1.);
}
