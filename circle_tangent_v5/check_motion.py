"""Check curved motion, persistent point circles, gradual unrolling, and contact."""
import sys
sys.dont_write_bytecode=True
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
    checks['vector_ring_absent_after_cut']=all(scene.state(float(t))['u_ringFade']==0.
        for t in np.linspace(scene.T_CUT,scene.END,120))
    checks['point_circle_retained_at_vector_ring_exit']=scene.state(scene.T_CUT)['u_unfold']==0.
    expansion=[scene.state(float(t))['u_unfold'] for t in np.linspace(scene.T_UNROLL,scene.T_UNROLLED,121)]
    checks['gradual_unrolling']=expansion[0]==0. and expansion[-1]==1. and all(b>a for a,b in zip(expansion,expansion[1:]))
    report['unrolling_duration_seconds']=scene.T_UNROLLED-scene.T_UNROLL
    orbit_speeds=[float(np.linalg.norm(scene.orbit(float(t))[1])) for t in times]
    report['orbit_max_min_speed_ratio']=max(orbit_speeds)/min(orbit_speeds)
    checks['expressive_orbit_speed_change']=report['orbit_max_min_speed_ratio']>2.5
    # The point body changes camera coordinates, retaining its image before it opens.
    point_match_errors=[]
    before_state=scene.state(scene.T_CUT,0);after_state=scene.state(scene.T_CUT,1)
    for radius in np.linspace(.3,2.26,9):
        for angle in np.linspace(0.,2.*math.pi,13):
            original=np.array([radius*math.cos(angle),radius*math.sin(angle),.15])
            mapped=scene.RING_ORIGIN+scene.RING_MAP@original
            screens=[]
            for position,state in ((original,before_state),(mapped,after_state)):
                q=scene.basis(state['u_cam'],state['u_look']).T@(position-state['u_cam'])
                screens.append(q[:2]/q[2]*1080./(2.*math.tan(state['u_fov']/2.)))
            point_match_errors.append(float(np.linalg.norm(screens[1]-screens[0])))
    report['point_circle_camera_change_error_px']=max(point_match_errors)
    checks['point_circle_does_not_jump']=max(point_match_errors)<.01
    flight_positions=[]
    for t in np.linspace(scene.START,scene.END,439):
        screen,_=project(float(t),int(t>=scene.T_CUT));flight_positions.append(screen.tolist())
    checks['visible_after_capture']=all(20.<project(float(t),int(t>=scene.T_CUT))[0][0]<1900.
        and 20.<project(float(t),int(t>=scene.T_CUT))[0][1]<1060.
        for t in np.linspace(scene.T_CATCH,scene.END,240))
    model=scene.MODEL
    contact_errors=[]
    for row in model.table:
        t=float(row[0]);plane=int(row[7])
        if plane<0:continue
        c,ex,ez,n=model.pose(plane,t)
        contact_errors.append(abs(float((row[1:4]-c)@n)-scene.RADIUS))
    report['maximum_landed_contact_error']=max(contact_errors)
    checks['contact_without_interpenetration']=max(contact_errors)<.0001
    arrival=scene.CUT_VELOCITY+np.array([0.,-scene.GRAVITY*(scene.T_LAND-scene.T_CUT),0.])
    normal=model.pose(3,scene.T_LAND)[3]
    opposition=float(-normal@arrival/np.linalg.norm(arrival))
    report['catch_normal_vs_incoming_velocity']=opposition
    checks['plane_faces_incoming_ball']=opposition>.9999
    first=model.table[model.table[:,7]==3]
    second=model.table[model.table[:,7]==4]
    angle0=math.asin(float(model.pose(3,scene.T_LAND)[1][1]))
    angle1=math.asin(float(model.pose(3,float(first[-1,0]))[1][1]))
    report['first_plane_rotation_degrees']=math.degrees(angle1-angle0)
    report['first_plane_slide_distance']=float(first[-1,8]-first[0,8])
    checks['plane_rotates_before_release']=abs(report['first_plane_rotation_degrees'])>45.
    checks['ball_slides_to_edge']=report['first_plane_slide_distance']>.50
    checks['next_tangent_catches']=len(second)*model.dt>.80
    checks['recipient_still_supported_at_end']=int(model.sample(scene.END)[7])==4
    checks['platform_ready_before_landing']=scene.state(scene.T_LAND-.05)['u_growth'][3]>.999
    checks['wave_keeps_moving']=scene.OMEGA==2.26 and scene.state(40.)['u_quiet']==0.
    checks['ballistic_arrival_position']=bool(np.linalg.norm(scene.air_flight(scene.T_LAND)-model.landing_target())<1e-9)
    report['dynamics']=model.summary()
    report.update(checks=checks,passed=all(checks.values()),screen_trajectory_px=flight_positions)
    (HERE/'motion_verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='screen_trajectory_px'},indent=2))
    return 0 if report['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
