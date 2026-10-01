"""Spectral-flux onset detection for a mono WAV excerpt. Prints onset times (song seconds)."""
import sys, wave
import numpy as np
from scipy.signal import find_peaks, stft


def onsets(path, offset, lo=None, hi=None):
    with wave.open(path) as w:
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    hop = 256
    f, t, Z = stft(x, sr, nperseg=1024, noverlap=1024 - hop)
    mag = np.log1p(100 * np.abs(Z))
    flux = np.maximum(np.diff(mag, axis=1), 0).sum(0)
    flux = (flux - np.median(flux)) / (np.std(flux) + 1e-9)
    times = t[1:] + offset
    peaks, props = find_peaks(flux, height=1.5, distance=int(0.09 * sr / hop))
    out = [(times[p], flux[p]) for p in peaks]
    if lo is not None:
        out = [o for o in out if lo <= o[0] <= hi]
    return out


if __name__ == '__main__':
    path, offset = sys.argv[1], float(sys.argv[2])
    lo, hi = (float(sys.argv[3]), float(sys.argv[4])) if len(sys.argv) > 4 else (None, None)
    for tm, s in onsets(path, offset, lo, hi):
        print(f'{tm:8.3f}  {s:5.2f}  ' + '#' * int(s * 3))
