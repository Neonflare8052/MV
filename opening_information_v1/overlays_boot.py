"""Opening identity, memory writes, and audio analysis annotations.

All numbers come from the copied scene's state.  The overlay shares its camera
and keeps the terminal and point field visible; it contains no lyric captions.
"""
import math
from PIL import ImageDraw
from common import WHITE, COPPER, blank, clamp, color, gate, project, smooth, tag as _tag

WINDOWS = {
    'boot': [(6.0, 7.4), (10.15, 12.5)],
    'execute': [(17.0, 20.4), (27.4, 29.6)],
}


def _anchor(point, params, w, h):
    xy = project(point, params, w, h)
    inset = 12 * h / 1080
    return xy if xy and inset < xy[0] < w-inset and inset < xy[1] < h-inset else None


def tag(draw, xy, lines, w, h, alpha, tint, **kwargs):
    if xy is None:
        return
    edge = min(xy[0], w-xy[0], xy[1], h-xy[1])
    visibility = smooth((edge - 12*h/1080) / (75*h/1080))
    _tag(draw, xy, lines, w, h, alpha*visibility, tint, **kwargs)


def _route(mod):
    """One continuous branch already present in the source activation tree."""
    branch = [mod.SEGS[0]]
    for k in range(1, 6):
        previous = branch[-1][1]
        choices = [s for s in mod.SEGS if s[2] == k]
        connected = [s for s in choices if s[0] == previous]
        if not connected:
            # All source nodes have an upward connection, but keep this robust
            # for a future snapshot with an explicitly pruned activation tree.
            break
        branch.append(connected[0])
    return branch


def _boot(draw, mod, t, w, h):
    p = mod.params(t)
    a = gate(t, [(6.0, 7.4)])
    if a:
        # The input marker belongs to the prompt plane; the output marker is
        # the top layer's one-node convergence point in the actual scene.
        tag(draw, _anchor((-1.05, 0., .05), p, w, h),
            ['YOU / INPUT', 'prompt enters L0'], w, h, a, WHITE,
            side=(-1, -1), offset=(48, 70), mark='diamond')
        top_y = 5 * mod.LHp * p['u_rise']
        tag(draw, _anchor((.05, top_y, .05), p, w, h),
            ['ME / MODEL', '6 layers'], w, h, a, COPPER,
            side=(1, -1), offset=(55, 55), mark='circle')
        tag(draw, _anchor((-2.7, 2.1, -2.7), p, w, h),
            ['SANDBOX', 'net none  /  fs readonly'], w, h, a * .82,
            WHITE, side=(-1, -1), offset=(55, 45), mark='cross')

    a = gate(t, [(10.15, 11.65)], fade=.16)
    if a:
        written = sum(v > 0. for v in p['u_mem'])
        # u_mem becomes nonzero exactly when a layer's press reaches memory.
        # Counting instantaneous u_press would incorrectly decrease after its
        # bounce, so writes use the source's persistent memory state.
        tag(draw, _anchor((1.65, -.2, 0.), p, w, h),
            [f'WRITE {written}/6', 'L5 > L0  /  memory'],
            w, h, a, COPPER, side=(-1, 1), offset=(55, 45), mark='cross')

    a = gate(t, [(11.25, 12.5)], fade=.18)
    if a:
        act = float(p['u_act'])
        branch = _route(mod)
        head = branch[0][0]
        scale = h / 1080
        for pa, pb, layer in branch:
            f = clamp(act - layer)
            if f <= 0:
                break
            end = tuple(x + (y-x)*f for x, y in zip(pa, pb))
            sa, sb = project(pa, p, w, h), project(end, p, w, h)
            if sa and sb:
                draw.line([sa, sb], fill=color(COPPER, a * .78),
                          width=max(1, round(1.3 * scale)))
            head = end
        if act < 0:
            title, detail = 'YOU / INPUT', '14 tokens  /  ready'
        else:
            k = min(5, max(0, int(math.floor(act))))
            title = f'ROUTE L{k} > L{min(5, k+1)}'
            detail = '14 > 10 > 7 > 5 > 3 > 1'
        tag(draw, _anchor(head, p, w, h), [title, detail],
            w, h, a, WHITE, side=(-1, -1), offset=(75, 55), mark='diamond')


def _execute(draw, mod, t, w, h):
    p = mod.params(t)
    a = gate(t, [(17.0, 20.4)])
    if a:
        loaded = [k for k, tm in enumerate(mod.MOD_T) if t >= tm]
        if loaded:
            k = loaded[-1]
            tm = mod.tau(t)
            value = float(mod._fv(k, tm))
            tag(draw, _anchor((1.5, 0., -1.8), p, w, h),
                [mod.MOD_N[k].upper(), f'sample {tm:06.3f} s  /  {value:.3f}'],
                w, h, a, COPPER, side=(-1, -1), offset=(70, 80), mark='cross')

    a = gate(t, [(27.4, 29.6)])
    if a:
        clock = mod.tau(t)
        if t < mod.T_OPEN:
            state = 'FOUND'
        elif t < mod.T_PROC:
            state = 'OPEN'
        elif t - clock > .035:
            state = 'WAIT'
        else:
            state = 'PROCESSING'
        process = f'{clock:06.3f} s' if t >= mod.T_PROC else '--'
        tag(draw, _anchor((1.4, .25, -1.55), p, w, h),
            [f'LOVE / {state}', f'AUDIO   {t:06.3f} s', f'PROCESS {process}'],
            w, h, a, WHITE, side=(-1, -1), offset=(65, 65), mark='circle')


def overlay(name, mod, t, w, h):
    image = blank(w, h)
    if name not in WINDOWS or not gate(t, WINDOWS[name]):
        return image
    draw = ImageDraw.Draw(image)
    if name == 'boot':
        _boot(draw, mod, t, w, h)
    else:
        _execute(draw, mod, t, w, h)
    return image
