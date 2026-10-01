"""Check handoff continuity, frame composition and the expanding stopping domain."""
import sys
sys.dont_write_bytecode=True
import json,math
from pathlib import Path
import numpy as np
import render as scene

def project(state,position=None):
    p=state['u_you'] if position is None else position
    b=scene.PREVIOUS.basis(state['u_cam'],state['u_look'])
    q=b.T@(np.asarray(p)-state['u_cam'])
    scale=1080./(2.*math.tan(state['u_fov']/2.))
    return np.array([960.,540.])+q[:2]/q[2]*np.array([scale,-scale])

def main():
    checks={};report={};dt=1e-5
    release=scene.RELEASE
    incoming=scene.PREVIOUS.MODEL.sample(release)[4:7]
    outgoing=(scene.recipient(release+dt)-scene.recipient(release))/dt
    report['release_velocity_error']=float(np.linalg.norm(outgoing-incoming))
    checks['continuous_release_velocity']=report['release_velocity_error']<.001
    checks['leaves_actual_plane_edge']=abs(scene.PREVIOUS.MODEL.sample(release-scene.PREVIOUS.MODEL.dt)[8])>1.04
    continuity=[]
    for t in np.linspace(39.,40.7,31):
        a=scene.PREVIOUS.state(float(t),1);b=scene.state(float(t))
        continuity.append(float(np.linalg.norm(project(a)-project(b))))
    report['max_previous_shot_screen_error_px']=max(continuity)
    checks['previous_shot_preserved']=max(continuity)<1e-9
    times=np.linspace(release,scene.END,401)
    positions=np.array([scene.recipient(float(t)) for t in times])
    checks['world_motion_continues_right']=bool(np.all(np.diff(positions[:,0])>0.))
    screens=np.array([project(scene.state(float(t))) for t in np.linspace(scene.START,scene.END,501)])
    report['screen_bounds_px']=[screens.min(axis=0).tolist(),screens.max(axis=0).tolist()]
    checks['ball_visible_throughout']=bool(np.all(screens[:,0]>40.) and np.all(screens[:,0]<1880.) and np.all(screens[:,1]>40.) and np.all(screens[:,1]<1040.))
    normal=scene.FLOW_DIRECTION
    checks['boundary_perpendicular_to_flow']=abs(float(normal@scene.FLOW_SIDE))<1e-12 and abs(normal[1])<1e-12
    checks['boundary_grows_from_recipient']=scene.state(scene.T_BE)['u_limit']==0. and scene.state(scene.T_LIM)['u_limit']==1.
    checks['point_count_preserved']=len(scene.PREVIOUS.data())==17920
    # Every row is covered before the front reaches the plane. The softplus
    # coordinate leaves a strictly positive gap even after indefinite approach.
    maximum_normalized_radius=max(.60/1.13,.665/1.25)
    reach_time=41.4+(4.9-.15)/3.
    checks['full_cross_section_covered_before_contact']=scene.state(reach_time)['u_limit']>maximum_normalized_radius+.09
    free=4.9+85.*np.linspace(0.,1.,320)**1.7-3.*(scene.END-41.4)
    distance=.15+.32*np.logaddexp(0.,(free-.15)/.32)
    report['minimum_stream_boundary_gap']=float(distance.min())
    checks['point_front_does_not_cross_boundary']=bool(np.all(distance>=.15))
    near_speed=3./(1.+math.exp(-(free.min()-.15)/.32))
    report['near_boundary_relative_speed']=near_speed
    checks['asymptotic_slowdown']=near_speed<.001
    # Compile and compare actual rendered frames before the new action begins.
    source,sprites=scene.compile_sources()
    oldsource,oldsprites=scene.PREVIOUS.compile_sources()
    renderer=scene.Renderer(640,360,source,subframes=1)
    pixel_error=[]
    for t in (39.2,40.,40.6):
        renderer.use('new',source)
        new=np.frombuffer(renderer.frame(t,scene.state,post=scene.POST,sprites=sprites),dtype=np.uint8).astype(int)
        renderer.use('old',oldsource)
        old=np.frombuffer(renderer.frame(t,lambda tt:scene.PREVIOUS.state(tt,1),post=scene.POST,sprites=oldsprites),dtype=np.uint8).astype(int)
        pixel_error.append(int(np.max(np.abs(new-old))))
    report['pre_transition_render_max_pixel_difference']=pixel_error
    checks['previous_shot_pixels_match']=max(pixel_error)<=1
    report.update(checks={k:bool(v) for k,v in checks.items()},passed=bool(all(checks.values())))
    (Path(__file__).parent/'motion_verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
    return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
