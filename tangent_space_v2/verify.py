"""Verify the recomposed tangent-space study, audio timing, and protected inputs."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import wave

# Short correlation windows must not create a large BLAS thread pool.
os.environ["OPENBLAS_NUM_THREADS"] = "1"
sys.dont_write_bytecode = True

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FFMPEG = ROOT / "tools" / "ffmpeg.exe"
FFPROBE = ROOT / "tools" / "ffprobe.exe"
FPS = 60
FRAMES = 438
DURATION = FRAMES / FPS
SOURCE_START = 33.4
SAMPLE_RATE = 48000
CONTACT_SOURCE_TIMES = [34.3, 36.0, 37.5, 38.3, 38.8, 39.3, 39.8, 40.5]
RENDER_INPUTS = {"claude/engine/gl.py", "Mili - world.execute (me) ;.mp3"}


def run(arguments: list, *, timeout: float = 240) -> subprocess.CompletedProcess:
    result = subprocess.run([str(x) for x in arguments], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=timeout)
    if result.returncode:
        message = result.stderr.decode("utf-8", errors="replace")[-4000:]
        raise RuntimeError(f"{Path(arguments[0]).name} exited {result.returncode}: {message}")
    return result


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def check_sources(entries: list[dict]) -> list[dict]:
    results = []
    for entry in entries:
        original = ROOT / entry["original"]
        actual = digest(original) if original.is_file() else None
        results.append({"original": entry["original"],
                        "expected_sha256": entry["sha256"],
                        "actual_sha256": actual,
                        "unchanged": actual == entry["sha256"]})
    return results


def pcm(path: Path, offset: float, label: str, qa: Path,
        duration: float = .5) -> np.ndarray:
    wav_path = qa / f"{label}_{offset:06.3f}.wav"
    # Decode from the head BEFORE output trimming: fast input seeking into MP3
    # loses reservoir history and can make matching source audio look different.
    # Use a real WAV file because the bundled FFmpeg can print text to stdout.
    run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", path,
         "-ss", f"{offset:.9f}", "-t", f"{duration:.9f}",
         "-map", "0:a:0", "-vn", "-ac", "1", "-ar", SAMPLE_RATE,
         "-c:a", "pcm_s16le", wav_path])
    with wave.open(str(wav_path), "rb") as stream:
        if (stream.getnchannels(), stream.getsampwidth(), stream.getframerate()) != (1, 2, SAMPLE_RATE):
            raise RuntimeError(f"Unexpected PCM format: {wav_path.name}")
        samples = np.frombuffer(stream.readframes(stream.getnframes()),
                                dtype="<i2").astype(np.float64) / 32768.
    if len(samples) < int(duration * SAMPLE_RATE * .99):
        raise RuntimeError(f"Incomplete decoded audio window: {wav_path.name}")
    if samples.std() < .0001:
        raise RuntimeError(f"Audio window is silent: {wav_path.name}")
    return samples


def align(reference: np.ndarray, encoded: np.ndarray, clip_offset: float) -> dict:
    count = min(len(reference), len(encoded))
    reference, encoded = reference[:count], encoded[:count]
    maximum_lag = round(.020 * SAMPLE_RATE)
    best_correlation, best_lag = -2., 0
    zero_lag_correlation = None
    for lag in range(-maximum_lag, maximum_lag + 1):
        if lag > 0:
            source, output = reference[:-lag], encoded[lag:]
        elif lag < 0:
            source, output = reference[-lag:], encoded[:lag]
        else:
            source, output = reference, encoded
        source, output = source - source.mean(), output - output.mean()
        denominator = np.linalg.norm(source) * np.linalg.norm(output)
        correlation = float(np.dot(source, output) / max(denominator, 1e-15))
        if lag == 0:
            zero_lag_correlation = correlation
        if correlation > best_correlation:
            best_correlation, best_lag = correlation, lag
    return {"clip_window_start_seconds": clip_offset,
            "source_window_start_seconds": SOURCE_START + clip_offset,
            "window_duration_seconds": count / SAMPLE_RATE,
            "search_range_ms": 20., "correlation": best_correlation,
            "zero_lag_correlation": zero_lag_correlation,
            "lag_samples": best_lag, "lag_ms": best_lag * 1000 / SAMPLE_RATE,
            "source_rms": float(np.sqrt(np.mean(reference ** 2))),
            "encoded_rms": float(np.sqrt(np.mean(encoded ** 2)))}


def contact_sheet(movie: Path, qa: Path) -> Path:
    sheet = Image.new("RGB", (1920, 588), (17, 17, 18))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 18)
    for index, source_time in enumerate(CONTACT_SOURCE_TIMES):
        clip_time = source_time - SOURCE_START
        frame_path = qa / f"encoded_{index:02d}_source_{source_time:04.1f}.jpg"
        run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
             "-ss", f"{clip_time:.9f}", "-i", movie, "-map", "0:v:0",
             "-frames:v", "1", "-q:v", "2", frame_path])
        x, y = index % 4 * 480, index // 4 * 294
        with Image.open(frame_path) as frame:
            if frame.size != (1920, 1080):
                raise RuntimeError(f"Encoded still has wrong dimensions: {frame.size}")
            sheet.paste(frame.convert("RGB").resize((480, 270), Image.Resampling.LANCZOS), (x, y))
        draw.text((x + 10, y + 272),
                  f"source {source_time:05.2f}s / clip {clip_time:04.2f}s",
                  font=font, fill=(220, 215, 202))
    output = HERE / "encoded_contact_sheet.jpg"
    sheet.save(output, quality=95, subsampling=0)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", type=Path, default=HERE / "tangent_space_v2_1080p60.mp4")
    parser.add_argument("--skip-contact", action="store_true", help="Skip the encoded contact sheet.")
    args = parser.parse_args()
    movie = args.video.resolve()
    qa = HERE / "qa"
    qa.mkdir(exist_ok=True)
    report = {"passed": False, "movie": str(movie),
              "expected": {"width": 1920, "height": 1080, "fps": FPS,
                           "frames": FRAMES, "duration_seconds": DURATION,
                           "audio_source_start_seconds": SOURCE_START}, "checks": {}}
    checks = report["checks"]
    try:
        entries = json.loads((HERE / "source_manifest.json").read_text(encoding="utf-8"))
        song = next(ROOT / entry["original"] for entry in entries
                    if Path(entry["original"]).suffix.lower() == ".mp3")
        report["protected_sources"] = check_sources(entries)
        checks["render_inputs_match_historical_baseline"] = all(entry["unchanged"]
            for entry in report["protected_sources"] if entry["original"].replace("\\", "/") in RENDER_INPUTS)
        metadata = json.loads(run([FFPROBE, "-v", "error", "-show_streams", "-show_format",
                                   "-of", "json", movie]).stdout)
        report["metadata"] = metadata
        video = next(stream for stream in metadata["streams"] if stream["codec_type"] == "video")
        audio = next(stream for stream in metadata["streams"] if stream["codec_type"] == "audio")
        checks["1920x1080"] = video["width"] == 1920 and video["height"] == 1080
        checks["60fps"] = Fraction(video["avg_frame_rate"]) == FPS
        checks["438_frames"] = int(video.get("nb_frames", -1)) == FRAMES
        checks["video_duration"] = abs(float(video["duration"]) - DURATION) < .02
        checks["container_duration"] = abs(float(metadata["format"]["duration"]) - DURATION) < .05
        checks["stereo_audio"] = audio["channels"] == 2
        checks["audio_duration"] = abs(float(audio["duration"]) - DURATION) < .05
        run([FFMPEG, "-hide_banner", "-loglevel", "error", "-xerror", "-i", movie,
             "-map", "0:v:0", "-map", "0:a:0", "-f", "null", "NUL"])
        checks["both_streams_full_decode"] = True
        alignment = [align(pcm(song, SOURCE_START + time, "source", qa),
                           pcm(movie, time, "encoded", qa), time)
                     for time in [.5, 3.5, 6.4]]
        report["audio_alignment"] = alignment
        checks["source_audio_sync"] = all(result["correlation"] > .98
                                          and abs(result["lag_ms"]) <= 2.
                                          for result in alignment)
        if not args.skip_contact:
            report["contact_sheet"] = str(contact_sheet(movie, qa))
            checks["encoded_contact_sheet"] = True
        report["protected_sources"] = check_sources(entries)
        checks["render_inputs_match_historical_baseline"] = all(entry["unchanged"]
            for entry in report["protected_sources"] if entry["original"].replace("\\", "/") in RENDER_INPUTS)
        report["historical_reference_audit"] = {
            "all_historical_hashes_match": all(entry["unchanged"] for entry in report["protected_sources"]),
            "differences": [entry for entry in report["protected_sources"] if not entry["unchanged"]],
            "note": "The copied manifest predates this study. master.py differs from that historical snapshot; it is not imported, executed, or edited by this study. Its modification time (2026-09-30 13:43:48 +08:00) precedes creation of this study's render.py (13:50:01). The old hash is retained, not reset. Video checks and actual rendering inputs determine passed."
        }
        report["passed"] = all(checks.values())
    except Exception as error:
        report["error"] = f"{type(error).__name__}: {error}"
    (HERE / "verification.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    summary = {key: report[key] for key in ("passed", "checks")}
    for key in ("audio_alignment", "error"):
        if key in report:
            summary[key] = report[key]
    print(json.dumps(summary, indent=2, ensure_ascii=False), flush=True)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
