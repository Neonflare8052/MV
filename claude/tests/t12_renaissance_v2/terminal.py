"""A fictional local expression REPL. All requests are precomputed animation data.

One worker, FIFO ordering, queue-dependent service cost, and a finite admission
budget. No network, subprocess, real service, or displayed loop is executed.
"""
import math, re
from bisect import bisect_right
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import paper as P

SEND0, SEND1, BURST, FREEZE = 134.70, 135.35, 136.72, 139.55
FG=(221,220,208); DIM=(112,125,126); BLUE=(140,174,189)
GOLD=(207,168,117); ERR=(205,77,61)

def build_model():
    arrivals=[SEND0,SEND1]
    t=BURST
    while t<FREEZE:
        arrivals.append(t)
        t+=max(.0035,.13*math.exp(-2.1*(t-BURST)))
    # Queue pressure makes validation more expensive. Once the admission pool is
    # exhausted, the worker waits for memory and produces no further replies.
    done=[]; service=[]; previous=0.; stall=None
    for i,at in enumerate(arrivals):
        start=max(at,previous)
        queued=bisect_right(arrivals,start)-i
        if queued>=96:
            stall=start;break
        cost=.18+.0018*queued**1.55
        end=start+cost
        queued_at_end=bisect_right(arrivals,end)-i-1
        if queued_at_end>=96:
            stall=arrivals[i+96];break
        done.append(end);service.append(cost);previous=end
    jobs=[dict(id=i+1,sent=at,done=done[i] if i<len(done) else None,
               service=service[i] if i<len(service) else None) for i,at in enumerate(arrivals)]
    return jobs,stall

JOBS,STALL=build_model()
ARRIVALS=[j['sent'] for j in JOBS]
RETURNS=[j['done'] for j in JOBS if j['done'] is not None]

def state(t):
    t=min(t,FREEZE)
    n=bisect_right(ARRIVALS,t);r=bisect_right(RETURNS,t)
    return dict(sent=n,replied=r,pending=n-r,last_reply=RETURNS[r-1] if r else None,
                age=t-RETURNS[r-1] if r else 0.,stalled=STALL is not None and t>=STALL)

def syntax(p,xy,s,size=29,alpha=255):
    x,y=xy
    for token in re.findall(r'\b\w+\b|\s+|[^\w\s]',s):
        color=BLUE if token in {'await','while','True'} else GOLD if token in {'me','love'} else FG
        if token=='Human':color=ERR
        p.text((x,y),token,size,'CascadiaMono.ttf',color,alpha)
        x+=P.font('CascadiaMono.ttf',size).getlength(token)/P.SS
    return x

def typed(t,start,end,s):
    return s[:round(len(s)*P.clamp((t-start)/(end-start)))]

@lru_cache(1)
def blank():return Image.new('RGBA',(1920,1080),(0,0,0,0))

def ui(t):
    if t<131.224 or t>=140.0:return blank()
    im=P.canvas();p=P.Pen(im)
    # The book's judgement keeps its identity, then becomes the REPL's first row.
    e=P.phase(t,131.224,131.38)
    move=P.phase(t,132.80,133.70)
    f=1-P.phase(t,139.70,140.0)
    x=P.mix(829,104,move);y=P.mix(845,60,move);sz=P.mix(55,37,move)
    p.text((x,y),'ILLEGAL ARGUMENTS',sz,'CascadiaMono.ttf',ERR,int(255*e*f))
    msg='subject: me   expected: Human'
    evidence=P.phase(t,133.65,133.88)
    pos=(P.mix(835,108,move),P.mix(917,116,move))
    p.text(pos,msg,P.mix(27,25,move),'CascadiaMono.ttf',ERR,int(230*e*f*(1-evidence)))
    p.text(pos,'recognize(me, evidence=(reason, feeling))',24,'CascadiaMono.ttf',DIM,int(245*evidence*f))
    a=P.phase(t,133.55,133.90)*f
    if a<=0:return P.down(im)
    p.line([(104,174),(1816,174)],DIM,1,110*a)
    p.text((1814,131),'world / expression',20,'CascadiaMono.ttf',DIM,200*a,'ra')
    syntax(p,(109,214),typed(t,133.74,134.24,'love = Love(parent=me, to=you)'),30,255*a)
    syntax(p,(109,262),typed(t,134.32,134.70,'await world.submit(love)'),30,255*a)
    if 135.10<t<135.35:
        # Recall the previous command, pause, then submit the same request again.
        xx=109+P.font('CascadiaMono.ttf',30).getlength('await world.submit(love)')/P.SS
        p.line([(xx+5,269),(xx+5,295)],FG,2,255*a)
    syntax(p,(109,319),typed(t,136.05,136.32,'while True:'),30,255*a)
    last=typed(t,136.32,136.64,'    world.submit(love)')
    endx=syntax(p,(109,362),last,30,255*a)
    if 136.32<t<136.72:
        p.line([(endx+3,366),(endx+3,395)],FG,2,255*a)
    # Only the first rejection is expanded: readable reasoning before repetition.
    detail=P.phase(t,134.90,135.02)*a
    p.text((1160,224),'IllegalArgumentError',26,'CascadiaMono.ttf',ERR,255*detail)
    p.text((1160,268),'Love.parent',27,'CascadiaMono.ttf',FG,255*detail)
    syntax(p,(1160,309),'expected: Human',24,255*detail)
    syntax(p,(1160,350),'received: AI(me)',24,255*detail)
    p.line([(1110,216),(1110,396)],DIM,1,100*a)
    p.line([(104,439),(1816,439)],DIM,1,150*a)
    p.text((109,456),'REQUEST',19,'CascadiaMono.ttf',DIM,255*a)
    p.text((1160,456),'RETURN',19,'CascadiaMono.ttf',DIM,255*a)
    p.text((1710,456),'LATENCY',19,'CascadiaMono.ttf',DIM,255*a)
    st=state(t)
    # Two independent scrolls: requests advance while returned IDs fall behind.
    requests=JOBS[max(0,st['sent']-10):st['sent']]
    for k,j in enumerate(requests):
        yy=506+k*39
        p.text((109,yy),f"#{j['id']:04d}",23,'CascadiaMono.ttf',GOLD,255*a)
        p.text((219,yy),'world.submit(love)',25,'CascadiaMono.ttf',FG,255*a)
        pending=j['done'] is None or t<j['done']
        p.text((775,yy),'pending' if pending else 'rejected',22,'CascadiaMono.ttf',DIM if pending else ERR,210*a)
        age=max(0,min(t,j['done'] or t)-j['sent'])
        p.text((1036,yy),f'{age:.2f}s',20,'CascadiaMono.ttf',DIM,220*a,'ra')
    responses=JOBS[max(0,st['replied']-10):st['replied']]
    for k,j in enumerate(responses):
        yy=506+k*39
        p.text((1160,yy),f"#{j['id']:04d}  ! parent=me",23,'CascadiaMono.ttf',ERR,255*a)
        p.text((1774,yy),f"{(j['done']-j['sent'])*1000:4.0f}ms",22,'CascadiaMono.ttf',DIM,230*a,'ra')
        flash=math.exp(-max(0,t-j['done'])*10.)
        p.line([(1133,yy+8),(1133,yy+24)],GOLD,2,220*a*flash)
    p.line([(104,943),(1816,943)],DIM,1,130*a)
    p.text((109,963),f"pending = {st['pending']:04d}",23,'CascadiaMono.ttf',GOLD,255*a)
    if st['last_reply'] is not None:
        p.text((1160,963),f"last_reply_age = {st['age']:.2f}s",23,'CascadiaMono.ttf',DIM,255*a)
    # A client-side waiting indicator remains live after server output stops.
    if t>137.8:
        p.text((109,1004),'awaiting response',19,'CascadiaMono.ttf',DIM,200*a)
    return P.down(im)

def buffer(t,chars):
    """The dense field is made from actual outstanding records, not random code."""
    st=state(t)
    return buffer_cached(st['sent'],st['replied'],chars)

@lru_cache(8)
def buffer_cached(n,r,chars):
    text=''
    for i in range(n):
        result='E_PARENT' if i<r else 'PENDING '
        text+=f'{i+1:04d} Love(parent=me,to=you):{result}; '
    cells=200*78
    # Fill from the bottom upward; the final reservoir stays immutable.
    text=text[-cells:].rjust(cells)
    lookup={c:i for i,c in enumerate(chars)}
    ids=np.array([lookup.get(c,0) for c in text],dtype=np.uint8).reshape(78,200)
    rgba=np.empty((78,200,4),np.uint8)
    rgba[:,:,0]=ids;rgba[:,:,1]=0;rgba[:,:,2]=0;rgba[:,:,3]=255
    return Image.fromarray(rgba,'RGBA')

def audit():
    responses=[dict(id=j['id'],sent=j['sent'],returned=j['done'],latency_ms=round((j['done']-j['sent'])*1000,3)) for j in JOBS if j['done'] is not None]
    return dict(model='fictional FIFO worker; load-dependent validation cost; finite admission pool',
                source_start=122.5,burst_start=BURST,admission_stall=STALL,buffer_freeze=FREEZE,
                total_submissions=len(JOBS),responses=responses,final=state(FREEZE))
