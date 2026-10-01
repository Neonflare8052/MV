import math
BLACK=(.014,.016,.018)
IVORY=(.949,.922,.867)
COPPER=(.69,.44,.24)
RED=(.83,.16,.13)
YELLOW=(.88,.66,.24)
def clamp(x,a=0.,b=1.): return max(a,min(b,x))
def ease(x):
    x=clamp(x); return x*x*(3-2*x)
def progress(t,start,end): return ease((t-start)/max(end-start,.00001))
def mix(a,b,p): return a+(b-a)*p
def ring(c,x,y,r,gap=0,color=IVORY,width=3,turn=0):
    c.arc(x,y,r,turn+gap*.5,turn+math.tau-gap*.5,color,width)
