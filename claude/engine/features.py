"""Band-split audio features at 60 fps for a mono WAV excerpt (no stem separation).
rows: 0 loudness, 1 kick, 2 bass, 3 snare, 4 hats; plus a log-band spectrogram.
python features.py seg.wav offset out.npz"""
import sys, wave
import numpy as np
from scipy.signal import stft

FPS = 60


def load(path):
    with wave.open(path) as w:
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return x, sr


def features(path, offset, nb=48):
    x, sr = load(path)
    hop = sr // FPS
    f, t, Z = stft(x, sr, nperseg=4096, noverlap=4096 - hop, boundary=None)
    M = np.abs(Z)
    t = t + offset
    def band(lo, hi): return M[(f >= lo) & (f < hi)].sum(0)
    def flux(lo, hi):
        L = np.log1p(50 * M[(f >= lo) & (f < hi)])
        return np.r_[0, np.maximum(np.diff(L, axis=1), 0).sum(0)]
    def norm(v, p=98):
        v = v - np.percentile(v, 5); return np.clip(v / (np.percentile(v, p) + 1e-9), 0, 1.5)
    def env(v, decay):                        # instant attack, exponential release (per frame)
        out = np.zeros_like(v); a = 0.
        for i, s in enumerate(v): a = max(s, a * decay); out[i] = a
        return out
    loud = norm(np.sqrt((M ** 2).sum(0)))
    kick = env(norm(flux(30, 120)) ** 2, .86)
    bass = norm(band(40, 250)); bass = np.convolve(bass, np.ones(5) / 5, 'same')
    snare = env(norm(flux(1500, 5000)) ** 2, .84)
    hats = env(norm(flux(8000, 16000)) ** 2, .75)
    edges = np.geomspace(60, 12000, nb + 1)
    rows = []
    for a, b in zip(edges, edges[1:]):
        m = (f >= a) & (f < b)
        rows.append(M[m].mean(0) if m.any() else M[np.argmin(abs(f - np.sqrt(a * b)))])
    spec = np.stack(rows)
    spec = 20 * np.log10(spec + 1e-6)
    lo, hi = np.percentile(spec, 25, axis=1, keepdims=True), np.percentile(spec, 99.5, axis=1, keepdims=True)
    spec = np.clip((spec - lo) / (hi - lo + 1e-9), 0, 1)                  # per band, so the highs are not lost
    return t, np.stack([loud, kick, bass, snare, hats]), spec


if __name__ == '__main__':
    t, F, S = features(sys.argv[1], float(sys.argv[2]))
    np.savez_compressed(sys.argv[3], t=t, F=F.astype(np.float32), S=S.astype(np.float32))
    for k in np.arange(t[0] + 2, t[-1], .5):
        i = int(np.searchsorted(t, k))
        print(f'{t[i]:6.2f} ' + '  '.join(f'{n} {v:.2f}' for n, v in zip(('loud', 'kick', 'bass', 'snr', 'hat'), F[:, i])))
