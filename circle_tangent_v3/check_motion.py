"""Check the specific action promises: entry, half turn, match cut, and contact."""
import json,math
from pathlib import Path
import numpy as np
import render as scene

HERE=Path(__file__).resolve().parent

def project(t,shot):
    p=scene.state(t,shot);b=scene.basis(p['u_cam'],p['u_look'])
    q=b.T@(np.array(p['u_you'])-np.array(p['u_cam']))
    scale=1080./(2.*math.tan(p['u_fov']/2))
    return np.array([960.+q[0]/q[2]*scale,540.-q[1]/q[2]*scale]),scene.RADIUS/q[2]*scale

def main():
    report={};checks={};step=.00001
    start,radius=project(scene.START,0)
    checks['enters_from_outside_frame']=bool(start[0]+radius<0.)
    report['initial_projected_center_px']=start.tolist()
    times=np.linspace(scene.T_CATCH,scene.T_RELEASE,121)
    positions=np.array([scene.orbit(t)[0] for t in times])
    angles=np.unwrap(np.arctan2(positions[:,1],positions[:,0]))
    turn=math.degrees(angles[-1]-angles[0])
    report['orbit_degrees']=turn
    report['maximum_circle_contact_error']=float(np.max(np.abs(np.linalg.norm(positions,axis=1)+scene.RADIUS-2.10)))
    checks['half_orbit']=abs(turn-180.)<1e-8
    checks['ball_touches_inside_circumference']=report['maximum_circle_contact_error']<1e-8
    p0,v0,_=scene.orbit(scene.T_CATCH)
    capture_velocity=(p0-scene.incoming(scene.T_CATCH-step))/step
    capture_error=float(np.linalg.norm(capture_velocity-v0))
    report['capture_velocity_error']=capture_error
    checks['capture_continuity']=capture_error<.002
    p1,v1,_=scene.orbit(scene.T_RELEASE)
    release_p,release_v=scene.exit_flight(scene.T_RELEASE)
    release_normal=float(abs(np.dot(p1,v1))/(np.linalg.norm(p1)*np.linalg.norm(v1)))
    report['release_tangent_normal_dot']=release_normal
    checks['tangential_release']=release_normal<1e-8 and float(np.linalg.norm(release_p-p1))<1e-8
    before,r0=project(scene.T_CUT,0);after,r1=project(scene.T_CUT,1)
    velocity0=(before-project(scene.T_CUT-step,0)[0])/step
    velocity1=(project(scene.T_CUT+step,1)[0]-after)/step
    report['cut_position_error_px']=float(np.linalg.norm(after-before))
    report['cut_radius_error_px']=abs(float(r1-r0))
    report['cut_velocity_error_px_per_second']=float(np.linalg.norm(velocity1-velocity0))
    checks['match_cut_position']=report['cut_position_error_px']<.01
    checks['match_cut_size']=report['cut_radius_error_px']<.01
    checks['match_cut_velocity']=report['cut_velocity_error_px_per_second']<.05
    checks['circle_absent_after_cut']=all(scene.state(float(t))['u_ringFade']==0. and scene.state(float(t))['u_unfold']==1.
        for t in np.linspace(scene.T_CUT,scene.END,120))
    flight_positions=[]
    for t in np.linspace(scene.START,scene.END,439):
        screen,_=project(float(t),int(t>=scene.T_CUT));flight_positions.append(screen.tolist())
    checks['visible_after_capture']=all(20.<project(float(t),int(t>=scene.T_CUT))[0][0]<1900.
        and 20.<project(float(t),int(t>=scene.T_CUT))[0][1]<1060.
        for t in np.linspace(scene.T_CATCH,scene.END,240))
    contact_errors=[]
    for t in np.linspace(scene.T_LAND,scene.END,120):
        state=scene.state(float(t));h,dx,dz=scene.field(.70,0.,state['u_clock'],state['u_quiet'],state['u_dip'])
        normal=np.array([-dx,1.,-dz]);normal/=np.linalg.norm(normal)
        contact_errors.append(abs(float(np.dot(np.array(state['u_you'])-[.70,h,0.],normal))-scene.RADIUS))
    report['maximum_landed_contact_error']=max(contact_errors)
    checks['supported_after_landing']=max(contact_errors)<1e-8
    checks['platform_ready_before_landing']=scene.state(scene.T_LAND-.05)['u_growth'][3]>.999
    report.update(checks=checks,passed=all(checks.values()),screen_trajectory_px=flight_positions)
    (HERE/'motion_verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='screen_trajectory_px'},indent=2))
    return 0 if report['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
