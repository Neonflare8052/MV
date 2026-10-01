# MV production contract

Independent acts use `def draw(c, t):` with absolute seconds, no frame state.
Canvas coordinates are 1920x1080; actual rendering is native 3840x2160,60 fps.
Origin top left. Colors are RGB/RGBA 0..1 tuples or hex strings.

```
c.clear(color)
c.rect(x,y,w,h,color) # solid
c.line(x1,y1,x2,y2,color,width=2)
c.polyline(points,color,width=2,closed=False)
c.polygon(points,color)
c.circle(x,y,r,color,fill=True,width=2)
c.ellipse(x,y,rx,ry,color,fill=False,width=2)
c.arc(x,y,r,start,end,color,width=2) # angles radians
c.text(text,x,y,size=24,color='#F2EBDD',font='mono',anchor='left') # y is top; fonts mono,sans,cjk; anchor left/center/right
c.image(key,PIL_image,x,y,w,h) # caches by key; avoid new image each frame
c.render3d(scene,eye,target,fov=42,theme='mono',time=t,exposure=1)
c.flush() # batching happens automatically before 3D or images
```
Import `Scene` from `geometry` (copied original primitives renderer). Positions 3D Y up, front +Z. Mesh lighting real OpenGL, shadows. `scene.box(pos,size,rgb,rot=(0,0,0),emission=0)`, sphere, torus, cylinder, rod, group. See geometry.py. No original project art reused, just mesh/render engine.

Helpers in `common`: `clamp(x,a=0,b=1)`, `ease(x)` smoothstep 0..1, `progress(t,start,end)`, `mix(a,b,p)` supports scalars, `ring(c,x,y,r,gap=0,color=IVORY,width=3,turn=0)`, palette BLACK,IVORY,COPPER,RED,YELLOW each RGB tuples. Act code can define additional helpers and geometry.

No permanent letterboxing, no subtitles baked; matching SRT delivered. No title cards or explanatory chapter headings. Labels only where meaningful within depicted interfaces. Text minimum 18 design px except meaningful dense terminal/ASCII.

Keep areas of negative space intentional, material/camera detail but no arbitrary particle soup. Do NOT leave unfinished TODO assets. Modules never launch rendering or import other act modules. Output deterministic using seeded randomness per object, not frame.
