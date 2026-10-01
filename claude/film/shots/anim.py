"""Keyframed motion for things that move like the machine's eye (s14e_desk).

A track is a list of moves.  Each move starts at a time and goes to a value.  Kinds:
  'sac'  a saccade: it accelerates (continuous, ACCEL s), smears across the bulk of the way (continuous, `smear`
         frames — the renderer blurs these), then lands in steps held for HOLD frames each: 104.5 %, 99 %, 100 %.
  'hop'  it is simply there from that time on (a step).
  'tick' a pen's step: `smear` frames of smear, then there (no settling).
  'set'  the starting value.
Frames are 60 fps on the absolute clock (t = k / 60): render ranges starting on a frame boundary keep this true.

sample(track, ts, fps, shutter, sub) gives, for one sub-frame at time ts, the value at the start and at the end of
that sub-frame's slice of the exposure.  In continuous phases the exposure is the whole frame (a full shutter, for a
proper smear); in stepped phases both ends are the frame's held value, so nothing blurs."""
import math

FPS = 60
ACCEL = 3 / FPS
HOLD = 5
SETTLE = (1.045, .99, 1.)


def lerpv(a, b, k):
    if isinstance(a, tuple): return tuple(x + (y - x) * k for x, y in zip(a, b))
    return a + (b - a) * k


def move(t0, to, kind='sac', smear=2):
    return dict(t0=t0, to=to, kind=kind, smear=smear)


def _active(track, t):
    i = 0
    for j, m in enumerate(track):
        if m['t0'] <= t: i = j
    return track[i], (track[i - 1]['to'] if i > 0 else track[i]['to'])       # the move, and where it starts from


def value(track, t):
    """(value, mode) at time t; mode 'cont' (moving smoothly or smearing) or 'step' (held)"""
    m, a = _active(track, t)
    if m['kind'] in ('set', 'hop'): return m['to'], 'step'
    tau = t - m['t0']
    if m['kind'] == 'dart':                                          # a quick glance: two frames' start, one of smear, there
        if tau < 2 / FPS: return lerpv(a, m['to'], .2 * (tau * FPS / 2) ** 2), 'cont'
        if tau < 3 / FPS: return lerpv(a, m['to'], .2 + .8 * (tau * FPS - 2)), 'cont'
        return m['to'], 'step'
    if m['kind'] == 'tick':                                          # a pen's step: one smeared frame, then there
        S = m['smear'] / FPS
        if tau < S: return lerpv(a, m['to'], tau / S), 'cont'
        return m['to'], 'step'
    S = m['smear'] / FPS
    if tau < ACCEL: return lerpv(a, m['to'], .12 * (tau / ACCEL) ** 2), 'cont'
    if tau < ACCEL + S: return lerpv(a, m['to'], .12 + .78 * (tau - ACCEL) / S), 'cont'
    k = int((tau - ACCEL - S) * FPS / HOLD)
    return lerpv(a, m['to'], SETTLE[min(k, len(SETTLE) - 1)]), 'step'


def frame_of(ts):
    return round(ts * FPS) / FPS


def sample(track, ts, shutter=.5, sub=4):
    """(value at the start, value at the end) of this sub-frame's slice of the exposure"""
    tf = frame_of(ts)
    v, mode = value(track, tf)
    if mode == 'step':
        # a frame that lands exactly on a move's start still holds: the move shows from its first continuous frame
        return v, v
    u = (ts - tf) / (shutter / FPS) + .5                       # which sub-frame, 0 .. 1
    i = min(sub - 1, max(0, int(u * sub)))
    e0 = tf - .5 / FPS + i / (sub * FPS); e1 = e0 + 1 / (sub * FPS)
    return value(track, e0)[0], value(track, e1)[0]


def smooth(track, t, lag=.07, dur=.16):
    """the same path, followed smoothly and a little late (for the light the eye throws)"""
    m, a = _active(track, t - lag)
    if m['kind'] in ('set',): return m['to']
    k = (t - lag - m['t0']) / (dur if m['kind'] == 'sac' else dur * .5)
    k = max(0., min(1., k)); k = k * k * (3 - 2 * k)
    return lerpv(a, m['to'], k)


def next_move(track, t, within=.12):
    for m in track:
        if t < m['t0'] <= t + within: return m
    return None
