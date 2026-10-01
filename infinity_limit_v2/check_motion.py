"""Check actual GPU trajectories as well as recipient and camera kinematics."""
import sys
sys.dont_write_bytecode=True
import json,math
from pathlib import Path
import numpy as np
import render as scene
import moderngl

def project(t):
    state=scene.state(t)
    b=scene.PREVIOUS.basis(state['u_cam'],state['u_look'])
    q=b.T@(state['u_you']-state['u_cam'])
    scale=1080./(2.*math.tan(state['u_fov']/2.))
    return np.array([960.,540.])+q[:2]/q[2]*np.array([scale,-scale])

def main():
    report={};checks={};step=1e-4
    times=np.linspace(scene.RELEASE+.01,scene.END-.01,301)
    vel=np.array([(scene.recipient(t+step)-scene.recipient(t-step))/(2.*step) for t in times])
    expected=np.array([scene.V0+scene.ACCELERATION*(t-scene.RELEASE) for t in times])
    report['max_ballistic_velocity_error']=float(np.max(np.abs(vel-expected)))
    report['horizontal_speed_range']=[float(vel[:,0].min()),float(vel[:,0].max())]
    checks['unforced_horizontal_velocity_conserved']=np.max(np.abs(vel[:,[0,2]]-scene.V0[[0,2]]))<1e-7
    checks['same_gravity_as_contact_scene']=report['max_ballistic_velocity_error']<1e-7
    incoming=scene.PREVIOUS.MODEL.sample(scene.RELEASE)[4:7]
    outgoing=(scene.recipient(scene.RELEASE+step)-scene.recipient(scene.RELEASE))/step
    report['edge_release_velocity_error']=float(np.linalg.norm(outgoing-incoming))
    checks['edge_release_continuous']=report['edge_release_velocity_error']<.001
    screens=np.array([project(t) for t in times])
    report['screen_x_minimum_frame_step']=float(np.min(np.diff(screens[:,0])))
    checks['camera_does_not_pull_ball_backwards']=report['screen_x_minimum_frame_step']>-.001
    allscreens=np.array([project(t) for t in np.linspace(scene.START,scene.END,400)])
    report['screen_bounds_px']=[allscreens.min(axis=0).tolist(),allscreens.max(axis=0).tolist()]
    checks['ball_visible']=np.all(allscreens[:,0]>50.) and np.all(allscreens[:,0]<1870.) and np.all(allscreens[:,1]>50.) and np.all(allscreens[:,1]<1030.)

    source,sprites=scene.compile_sources();oldsource,oldsprites=scene.PREVIOUS.compile_sources()
    renderer=scene.Renderer(640,360,source,subframes=1)
    pixel_error=[]
    for t in (39.2,40.,40.6):
        renderer.use('new',source)
        new=np.frombuffer(renderer.frame(t,scene.state,post=scene.POST,sprites=sprites),dtype=np.uint8).astype(int)
        renderer.use('old',oldsource)
        old=np.frombuffer(renderer.frame(t,lambda tt:scene.PREVIOUS.state(tt,1),post=scene.POST,sprites=oldsprites),dtype=np.uint8).astype(int)
        pixel_error.append(int(np.max(np.abs(new-old))))
    report['pre_transition_pixel_differences']=pixel_error
    checks['prior_shot_pixels_unchanged']=max(pixel_error)<=1

    # Read the positions that the production vertex shader actually calculates.
    ctx=renderer.ctx
    program=ctx.program(vertex_shader=sprites[1],varyings=['v_world','v_captured','v_streamDistance'])
    data=scene.PREVIOUS.data();count=len(data)
    db=ctx.buffer(data.astype('f4').tobytes());corners=ctx.buffer(np.zeros((count,2),dtype='f4').tobytes())
    bindings=[]
    if 'in_corner' in program:bindings.append((corners,'2f','in_corner'))
    bindings.append((db,'4f 4f','in_a','in_b') if 'in_b' in program else (db,'4f 16x','in_a'))
    vao=ctx.vertex_array(program,bindings);output=ctx.buffer(reserve=count*5*4)
    renderer.acc_fbo.use();ctx.enable(moderngl.RASTERIZER_DISCARD)
    def positions(t):
        p=scene.state(t);p.update(u_time=t,u_res=(640.,360.),u_weight=1.)
        renderer._set(program,p)
        vao.transform(output,mode=moderngl.POINTS,vertices=count)
        return np.frombuffer(output.read(),dtype='f4').reshape(count,5).copy()
    minimum_gap=999.;captured_end=0;escaped=0;min_dx=999.
    last=None
    for t in np.linspace(42.3,scene.END,131):
        current=positions(float(t))
        capture=current[:,3]>.5
        if capture.any():
            gap=(scene.recipient(t)-current[capture,:3])@scene.FLOW_DIRECTION
            minimum_gap=min(minimum_gap,float(gap.min()))
        if last is not None:min_dx=min(min_dx,float((current[:,0]-last[:,0]).min()))
        last=current
    captured_end=int(np.sum(last[:,3]>.5));escaped=int(np.sum(last[:,4]<0.))
    jumps=[]
    rows=np.rint(data[:,2]*55.).astype(int)
    for row,t in enumerate(scene.ROW_ACTIVATION):
        before=positions(t-step);after=positions(t+step);mask=rows==row
        jumps.append(float(np.linalg.norm(after[mask,:3]-before[mask,:3],axis=1).max()))
    ctx.disable(moderngl.RASTERIZER_DISCARD)
    report.update(gpu_minimum_captured_plane_gap=minimum_gap,gpu_minimum_forward_step=min_dx,
                  gpu_captured_particle_count=captured_end,gpu_escaped_particle_count=escaped,
                  gpu_maximum_boundary_activation_displacement=max(jumps))
    checks['gpu_particles_keep_forward_motion']=min_dx>=-1e-4
    checks['gpu_captured_particles_remain_before_plane']=minimum_gap>.148
    checks['gpu_boundary_does_not_teleport_points']=max(jumps)<.012
    checks['gpu_both_escaping_and_captured_populations']=captured_end>1000 and escaped>1000
    report.update(checks={k:bool(v) for k,v in checks.items()},passed=bool(all(checks.values())))
    (Path(__file__).parent/'motion_verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
    return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
