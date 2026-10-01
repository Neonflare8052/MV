"""Validate the delivered MV using decoded media, not filenames or encode receipts.

Run from any directory:
    python src/validate_movie.py
    python src/validate_movie.py --source path/to/canonical_audio.wav

The JSON records actual checks and limitations. Native raster resolution is a
renderer property; ffprobe can verify delivery dimensions, not prove no upscale.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from fractions import Fraction
import wave


ROOT = Path(__file__).resolve().parents[1]
DECODER_DIR = ROOT / "tools"


def executable(name: str, override: str | None = None) -> str:
    if override:
        return str(Path(override).resolve())
    local = DECODER_DIR / f"{name}.exe"
    if local.is_file():
        return str(local)
    found = shutil.which(name)
    if not found:
        raise FileNotFoundError(f"Cannot find {name}; specify --{name}")
    return found


def run(command: list[str], timeout: float = 1800) -> subprocess.CompletedProcess:
    return subprocess.run(command, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout)


def probe(path: Path, ffprobe: str) -> dict:
    result = run([ffprobe, "-v", "error", "-show_streams", "-show_format",
                  "-of", "json", str(path)])
    if result.returncode:
        raise RuntimeError(f"ffprobe failed for {path}: {result.stderr[-4000:]}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        # The AV3A build writes its create/destroy diagnostics to stdout, even
        # between JSON closing braces. Preserve only ffprobe's JSON lines.
        lines = []
        for line in result.stdout.splitlines():
            stripped = line.lstrip()
            if stripped.startswith('"'):
                lines.append(line)
            elif stripped.startswith(("{", "}", "[", "]")):
                match = re.match(r"\s*([{}\[\]],?)", line)
                if match:
                    lines.append(match.group(1))
        return json.loads("\n".join(lines))


def file_identity(path: Path) -> dict:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return {"path": str(path.resolve()), "bytes": path.stat().st_size,
            "sha256": digest.hexdigest()}


def rational_rate(value: str | None) -> Fraction | None:
    try:
        return Fraction(value or "0")
    except (ValueError, ZeroDivisionError):
        return None


def seconds(stream: dict, fallback: float = 0.0) -> float:
    try:
        return float(stream.get("duration", fallback))
    except (TypeError, ValueError):
        return fallback


def decode_audio(ffmpeg: str, source: Path, destination: Path) -> None:
    result = run([ffmpeg, "-v", "error", "-xerror", "-nostdin", "-y",
                  "-i", str(source), "-map", "0:a:0", "-vn", "-ac", "2",
                  "-ar", "48000", "-c:a", "pcm_s16le", str(destination)])
    if result.returncode or not destination.is_file():
        raise RuntimeError(f"Audio decode failed: {source}\n{result.stderr[-4000:]}")


def compare_audio(ffmpeg: str, source: Path, movie: Path, work: Path,
                  minimum: float, allowed_lag: float) -> dict:
    try:
        import numpy as np
        from scipy.signal import correlate, correlation_lags
    except ImportError as exc:
        return {"status": "unavailable", "passed": False,
                "reason": str(exc), "install": "python -m pip install numpy scipy"}

    reference_wav = work / "source_decoded_stereo.wav"
    movie_wav = work / "movie_decoded_stereo.wav"
    decode_audio(ffmpeg, source, reference_wav)
    decode_audio(ffmpeg, movie, movie_wav)

    def read_pcm(path: Path):
        with wave.open(str(path), "rb") as reader:
            if reader.getsampwidth() != 2 or reader.getnchannels() != 2:
                raise ValueError(f"Unexpected PCM format: {path}")
            hz = reader.getframerate()
            data = np.frombuffer(reader.readframes(reader.getnframes()),
                                 dtype="<i2").reshape(-1, 2).astype(np.float64)
        return data / 32768.0, hz

    reference, hz = read_pcm(reference_wav)
    actual, actual_hz = read_pcm(movie_wav)
    if hz != actual_hz:
        raise ValueError("Decoded PCM rates differ")
    duration = min(len(reference), len(actual)) / hz
    window_seconds = min(10.0, max(1.0, duration / 4))
    start_times = [min(0.5, max(0.0, duration - window_seconds)),
                   max(0.0, (duration - window_seconds) / 2),
                   max(0.0, duration - window_seconds - 0.25)]
    windows = []
    # Downsample only for delay estimation; the final coefficient compares
    # both decoded stereo channels at the original 48 kHz sample rate.
    max_search_seconds = max(0.25, allowed_lag * 2)
    for label, start in zip(("start", "middle", "end"), start_times):
        begin = round(start * hz)
        count = round(window_seconds * hz)
        x = reference[begin:begin + count]
        y = actual[begin:begin + count]
        n = min(len(x), len(y))
        x, y = x[:n], y[:n]
        a = x.mean(axis=1)[::4]
        b = y.mean(axis=1)[::4]
        a = a - a.mean()
        b = b - b.mean()
        xc = correlate(b, a, mode="full", method="fft")
        lags = correlation_lags(len(b), len(a), mode="full")
        mask = np.abs(lags) <= round(max_search_seconds * hz / 4)
        best_lag = int(lags[mask][np.argmax(xc[mask])]) * 4
        # Refine to individual samples around the downsampled estimate.
        candidates = []
        for lag in range(best_lag - 5, best_lag + 6):
            if lag > 0:
                xx, yy = x[:-lag], y[lag:]
            elif lag < 0:
                xx, yy = x[-lag:], y[:lag]
            else:
                xx, yy = x, y
            xx = xx - xx.mean(axis=0)
            yy = yy - yy.mean(axis=0)
            denom = float(np.sqrt(np.sum(xx * xx) * np.sum(yy * yy)))
            coefficient = float(np.sum(xx * yy) / denom) if denom > 1e-12 else 0.0
            candidates.append((coefficient, lag))
        coefficient, lag = max(candidates)
        rms_reference = float(np.sqrt(np.mean(x * x)))
        rms_final = float(np.sqrt(np.mean(y * y)))
        gain_db = 20 * math.log10(max(rms_final, 1e-12) / max(rms_reference, 1e-12))
        passed = (coefficient >= minimum and abs(lag / hz) <= allowed_lag
                  and rms_reference > 1e-5 and rms_final > 1e-5)
        windows.append({"region": label, "start_seconds": round(start, 6),
                        "length_seconds": n / hz,
                        "correlation": round(coefficient, 8),
                        "final_delay_seconds": lag / hz,
                        "reference_rms": rms_reference, "final_rms": rms_final,
                        "gain_db": round(gain_db, 5), "passed": bool(passed)})
    return {"status": "completed", "passed": all(w["passed"] for w in windows),
            "method": "decoded stereo PCM, FFT lag search then normalized correlation",
            "minimum_correlation": minimum, "maximum_abs_delay_seconds": allowed_lag,
            "source_decoded_duration": len(reference) / hz,
            "movie_decoded_duration": len(actual) / hz,
            "duration_difference_seconds": (len(actual) - len(reference)) / hz,
            "source_decode": str(reference_wav), "movie_decode": str(movie_wav),
            "windows": windows}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--movie", type=Path,
                        default=ROOT / "output/world_execute_me_4K60.mp4")
    parser.add_argument("--source", type=Path,
                        default=ROOT / "Mili - world.execute (me) ;.mp3")
    parser.add_argument("--report", type=Path, default=ROOT / "output/verification.json")
    parser.add_argument("--work-dir", type=Path, default=ROOT / "work/verification")
    parser.add_argument("--ffmpeg")
    parser.add_argument("--ffprobe")
    parser.add_argument("--duration-tolerance", type=float, default=0.2)
    parser.add_argument("--min-correlation", type=float, default=0.98)
    parser.add_argument("--max-audio-lag", type=float, default=0.08)
    parser.add_argument("--skip-audio-correlation", action="store_true",
                        help="Mark content comparison as skipped; structural checks still run")
    args = parser.parse_args()
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.work_dir.mkdir(parents=True, exist_ok=True)
    report = {"checked_at_utc": datetime.now(timezone.utc).isoformat(),
              "passed": False, "checks": {},
              "limitations": ["Encoded dimensions cannot prove native render resolution.",
                              "Technical validation does not substitute for visual review."]}
    try:
        ffmpeg, ffprobe = executable("ffmpeg", args.ffmpeg), executable("ffprobe", args.ffprobe)
        report["tools"] = {"ffmpeg": ffmpeg, "ffprobe": ffprobe}
        report["movie"] = file_identity(args.movie)
        report["source_audio"] = file_identity(args.source)
        metadata = probe(args.movie, ffprobe)
        source_metadata = probe(args.source, ffprobe)
        (args.work_dir / "movie_probe.json").write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
        (args.work_dir / "source_probe.json").write_text(
            json.dumps(source_metadata, indent=2, ensure_ascii=False), encoding="utf-8")
        videos = [s for s in metadata.get("streams", [])
                  if s.get("codec_type") == "video"
                  and not s.get("disposition", {}).get("attached_pic")]
        audios = [s for s in metadata.get("streams", []) if s.get("codec_type") == "audio"]
        source_audios = [s for s in source_metadata.get("streams", []) if s.get("codec_type") == "audio"]
        if not videos or not audios or not source_audios:
            raise ValueError("Movie must contain video and audio; reference must contain audio")
        video, audio = videos[0], audios[0]
        movie_duration = seconds(metadata.get("format", {}))
        source_duration = seconds(source_audios[0], seconds(source_metadata.get("format", {})))
        checks = report["checks"]
        checks["dimensions"] = {"width": video.get("width"), "height": video.get("height"),
                                "passed": video.get("width") == 3840 and video.get("height") == 2160}
        avg_rate = rational_rate(video.get("avg_frame_rate"))
        nominal_rate = rational_rate(video.get("r_frame_rate"))
        checks["frame_rate"] = {"avg_frame_rate": video.get("avg_frame_rate"),
                                "r_frame_rate": video.get("r_frame_rate"),
                                "required_exact": "60/1",
                                "avg_normalized": (f"{avg_rate.numerator}/{avg_rate.denominator}"
                                                   if avg_rate is not None else None),
                                "nominal_normalized": (f"{nominal_rate.numerator}/{nominal_rate.denominator}"
                                                       if nominal_rate is not None else None),
                                "passed": avg_rate == Fraction(60, 1)
                                and nominal_rate == Fraction(60, 1)}
        checks["duration"] = {"movie_seconds": movie_duration, "source_seconds": source_duration,
                              "difference_seconds": movie_duration - source_duration,
                              "tolerance_seconds": args.duration_tolerance,
                              "passed": source_duration > 0 and
                              abs(movie_duration - source_duration) <= args.duration_tolerance}
        audio_duration = seconds(audio, movie_duration)
        checks["audio_stream"] = {"codec": audio.get("codec_name"), "channels": audio.get("channels"),
                                  "sample_rate": audio.get("sample_rate"), "duration_seconds": audio_duration,
                                  "passed": audio.get("channels", 0) >= 1 and
                                  abs(audio_duration - source_duration) <= args.duration_tolerance}
        nb_frames = video.get("nb_frames")
        checks["frame_count"] = {"reported_frames": nb_frames,
                                  "expected_near": round(movie_duration * 60),
                                  "passed": nb_frames is not None and
                                  abs(int(nb_frames) - round(movie_duration * 60)) <= 2}
        print("Decoding the complete 4K video and audio streams...", flush=True)
        decoded = run([ffmpeg, "-v", "error", "-xerror", "-nostdin", "-i", str(args.movie),
                       "-map", "0:v:0", "-map", "0:a:0", "-f", "null", "-"], timeout=3600)
        decode_log = args.work_dir / "full_decode.log"
        decode_log.write_text(decoded.stdout + "\n" + decoded.stderr, encoding="utf-8")
        checks["full_decode"] = {"exit_code": decoded.returncode,
                                  "log": str(decode_log), "passed": decoded.returncode == 0}
        if args.skip_audio_correlation:
            report["audio_content_comparison"] = {"status": "skipped", "passed": None}
            report["limitations"].append("Audio content identity was not compared.")
        else:
            print("Comparing decoded source and movie audio at start, middle and end...", flush=True)
            comparison = compare_audio(ffmpeg, args.source, args.movie, args.work_dir,
                                       args.min_correlation, args.max_audio_lag)
            report["audio_content_comparison"] = comparison
            checks["audio_content"] = {"passed": comparison["passed"]}
        report["passed"] = all(c.get("passed") is True for c in checks.values())
    except Exception as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "report": str(args.report.resolve()),
                      "error": report.get("error")}, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
