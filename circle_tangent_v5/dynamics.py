"""Moving true tangent planes with unilateral contact, gravity and low friction."""
from __future__ import annotations
import math
import numpy as np

AMPLITUDE=.76
WAVENUMBER=1.19
OMEGA=2.26
GRAVITY=5.0
RADIUS=.105
LAND=38.65
END=40.7
BASE=np.array([.70,0.,0.])

def smooth(x):
    x=min(1.,max(0.,x));return x*x*(3.-2.*x)

def solve_wave_phase(velocity):
    slope=math.hypot(velocity[0],velocity[2])/abs(velocity[1])
    if slope>=AMPLITUDE*WAVENUMBER:raise ValueError('Incoming angle exceeds wave slope')
    return math.acos(slope/(AMPLITUDE*WAVENUMBER))

class Dynamics:
    def __init__(self,direction,phase,landing_velocity,half_length=.52,separation=.90,dt=1/1200):
        self.forward=np.array(direction,dtype=float,copy=True);self.forward[1]=0.;self.forward/=np.linalg.norm(self.forward)
        self.side=np.array([-self.forward[2],0.,self.forward[0]])
        self.phase=phase;self.landing_velocity=np.asarray(landing_velocity)
        self.half_length=half_length;self.separation=separation;self.dt=dt
        self.locations={3:0.,4:separation,5:separation*2.}
        self.lengths={3:half_length,4:1.05,5:.95}
        self.widths={3:.70,4:.63,5:.62}
        self.events=[{'time':LAND,'plane':3,'q':0.,'depth':.115}]
        self.transitions=[]

    def field(self,x,z,t):
        rel=np.array([x-.70,0.,z]);q=float(rel@self.forward);r=float(rel@self.side)
        phi=WAVENUMBER*q+OMEGA*(t-LAND)+self.phase
        height=AMPLITUDE*math.sin(phi)+.045*(math.cos(.9*r)-1.)
        dq=AMPLITUDE*WAVENUMBER*math.cos(phi);dr=-.0405*math.sin(.9*r)
        for event in self.events:
            age=t-event['time']
            if age<0. or age>1.2:continue
            tau=.15
            dip=-event['depth']*(age/tau)*math.exp(1.-age/tau)
            localq=q-event['q'];e=math.exp(-(localq/.80)**2-(r/1.1)**2)
            height+=dip*e;dq+=dip*e*(-2.*localq/.80**2);dr+=dip*e*(-2.*r/1.1**2)
        dx=dq*self.forward[0]+dr*self.side[0]
        dz=dq*self.forward[2]+dr*self.side[2]
        return height,dx,dz

    def growth(self,plane,t):
        if plane==5:return 0.
        onset={3:38.03,4:38.91,5:39.67}[plane]
        amount=smooth((t-onset)/.45)
        # Once the second tangent has taken over, release the first surface.
        handoffs=[e['time'] for e in self.events if e['plane']==4]
        if plane==3 and handoffs:amount*=1.-smooth((t-handoffs[0]-.06)/.32)
        return amount

    def pose(self,plane,t):
        point=BASE+self.forward*self.locations[plane]
        h,dx,dz=self.field(point[0],point[2],t);center=np.array([point[0],h,point[2]])
        normal=np.array([-dx,1.,-dz]);normal/=np.linalg.norm(normal)
        slope=dx*self.forward[0]+dz*self.forward[2]
        ex=np.array([self.forward[0],slope,self.forward[2]]);ex/=np.linalg.norm(ex)
        ez=np.cross(ex,normal);ez/=np.linalg.norm(ez)
        return center,ex,ez,normal

    def material_velocity(self,plane,t,u,v,dt=1e-4):
        c0,e0,z0,n0=self.pose(plane,t)
        c1,e1,z1,n1=self.pose(plane,t+dt)
        return (c1+e1*u+z1*v+n1*RADIUS-c0-e0*u-z0*v-n0*RADIUS)/dt

    def landing_target(self):
        c,_,_,n=self.pose(3,LAND)
        return c+n*RADIUS

    def simulate(self):
        dt=self.dt;p=self.landing_target();v=self.landing_velocity.copy()
        _,_,_,normal=self.pose(3,LAND)
        support_v=self.material_velocity(3,LAND,0.,0.)
        relative=v-support_v;vn=float(relative@normal)
        if vn<0:v-=vn*normal
        self.first_post_velocity=v.copy()
        rows=[np.r_[LAND,p,v,3.,0.,0.]]
        active=3;self.transitions=[{'time':LAND,'from':None,'to':3}]
        for step in range(1,math.ceil((END-LAND+.03)/dt)+1):
            t=LAND+step*dt;oldp=p.copy();oldactive=active
            v[1]-=GRAVITY*dt;p=p+v*dt;active=-1;cu=cv=0.
            order=[oldactive]+[i for i in (3,4,5) if i!=oldactive] if oldactive>=0 else [3,4,5]
            for plane in order:
                g=self.growth(plane,t)
                if g<.95:continue
                c,ex,ez,n=self.pose(plane,t);delta=p-c;d=float(delta@n)
                u,w=float(delta@ex),float(delta@ez)
                if abs(u)>self.lengths[plane]*g or abs(w)>self.widths[plane]*math.sqrt(g):continue
                cp,_,_,np_=self.pose(plane,t-dt);old_distance=float((oldp-cp)@np_)
                if d<RADIUS and d>-.05 and old_distance>RADIUS-.06:
                    p+=n*(RADIUS-d)
                    sv=self.material_velocity(plane,t,u,w)
                    relative=v-sv;vn=float(relative@n)
                    if vn<0:
                        v-=vn*n
                        tangent=relative-vn*n;speed=float(np.linalg.norm(tangent))
                        if speed>.0001:v-=tangent*min(.045*(-vn)/speed,1.)
                    active=plane;cu,cv=u,w
                    if not any(e['plane']==plane for e in self.events):
                        self.events.append({'time':t,'plane':plane,'q':self.locations[plane],'depth':0.})
                    break
            if active!=oldactive:self.transitions.append({'time':t,'from':int(oldactive),'to':int(active)})
            rows.append(np.r_[t,p,v,float(active),cu,cv])
        self.table=np.asarray(rows)
        return self

    def sample(self,t):
        f=max(0.,min(len(self.table)-1.000001,(t-LAND)/self.dt));i=int(f);u=f-i
        row=self.table[i]*(1.-u)+self.table[min(i+1,len(self.table)-1)]*u
        row[7]=self.table[i,7]
        return row

    def summary(self):
        counts={str(i):int(np.sum(self.table[:,7]==i)) for i in (-1,3,4,5)}
        return {'contact_seconds':{k:v*self.dt for k,v in counts.items()},'events':self.events,
                'transitions':self.transitions,'end_position':self.table[-1,1:4].tolist(),
                'peak_speed':float(np.max(np.linalg.norm(self.table[:,4:7],axis=1)))}
