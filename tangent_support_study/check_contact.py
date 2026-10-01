"""Verify contact against the source curve, independently by finite differences."""
import sys
sys.dont_write_bytecode=True
import math,json
from pathlib import Path
import render
m,_=render.load()
rows=[]
for t in [39.04,39.1,39.4,39.7,40.1,40.4,40.65]:
    p=render.state(m,t);x=p['u_contactX'];eps=1e-5
    slope=(m.wave_y(x+eps,18,t)-m.wave_y(x-eps,18,t))/(2*eps)
    n=(-slope/math.sqrt(1+slope*slope),1/math.sqrt(1+slope*slope),0.)
    contact=(x,m.wave_y(x,18,t),-.123076923)
    delta=tuple(a-b for a,b in zip(p['u_recipient'],contact))
    normal_distance=sum(a*b for a,b in zip(delta,n))
    tangent_offset=(delta[0]+slope*delta[1])/math.sqrt(1+slope*slope)
    rows.append({'time':t,'sphere_gap':normal_distance-.072,'tangent_offset':tangent_offset})
passed=all(abs(x['sphere_gap'])<1e-6 and abs(x['tangent_offset'])<1e-6 for x in rows)
Path(__file__).with_name('contact_verification.json').write_text(json.dumps({'passed':passed,'samples':rows},indent=2),encoding='utf-8')
print('Contact and source-curve tangent verified:',passed)
if not passed:raise SystemExit(1)
