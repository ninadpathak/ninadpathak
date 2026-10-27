#!/usr/bin/env python3
"""Import a finished film from the ninadpathak-video repo as an article video.

Usage:
  python tools/import_video.py <slug> --name "..." --description "..." [--video-repo PATH] [--allow-newer-sources]

Reads (never writes) the video repo:
  out/<slug>.mp4, out/<slug>-poster.png       the delivered film and its poster
  films/<slug>/script.md                       "## Full text" or "### Full text" becomes the transcript
  films/<slug>/timeline.json                   voice.lines start frames -> line_offsets
  films/<slug>/assets/voice/words.json         word timings for the captions
  films/<slug>/assets/voice/L*.wav, mix.wav    used only to prove the render is current

Writes content/videos/<slug>/{video.yaml,words.json} and static/videos/<slug>/
(<slug>.mp4, poster.png, poster.webp, captions.vtt), then runs build_video_captions.py
and build_video_poster.py.

It refuses a stale render: the script, word timings, timeline or a voice take newer
than the delivered mp4 means the film was revised after it was rendered, and each
voice take must match the mp4's own audio at its timeline offset. Captions built from
newer timings than the audio would put the wrong words on screen.

The video repo sometimes rewrites timeline.json and words.json after a render without
changing them in substance. --allow-newer-sources turns the date check into a warning
for that case; the audio check still has to pass.

Fields stay provider-neutral (name, description, upload_date, duration, transcript,
captions), so a later switch to a hosted player only adds a provider field.
"""
import argparse
import array
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

import yaml

IST = timezone(timedelta(hours=5, minutes=30))
# Scores are loudness-envelope correlations. The known-good speculative-decoding render
# scores 0.89-0.96 per line; the stale release-notes-template render scored 0.22 on its
# re-recorded line. Raw waveform correlation was too noisy after AAC (0.72 on a good line).
MIN_MATCH = 0.6


def load_wav(path: Path):
    """Read the first channel of 16-bit PCM, including the extensible header afconvert writes."""
    data = path.read_bytes()
    index, channels, rate, samples = 12, 1, 0, None
    while index < len(data):
        chunk, size = data[index:index + 4], int.from_bytes(data[index + 4:index + 8], "little")
        if chunk == b"fmt ":
            channels = int.from_bytes(data[index + 10:index + 12], "little")
            rate = int.from_bytes(data[index + 12:index + 16], "little")
            if int.from_bytes(data[index + 22:index + 24], "little") != 16:
                raise SystemExit(f"{path}: expected 16-bit PCM")
        if chunk == b"data":
            samples = array.array("h")
            samples.frombytes(data[index + 8:index + 8 + size - size % 2])
        index += 8 + size + (size & 1)
    if samples is None or not rate:
        raise SystemExit(f"{path}: not a PCM WAV file")
    return samples[0::channels], rate


def envelope(path: Path):
    """Loudness per 10 ms frame, which survives AAC encoding and the music bed."""
    samples, rate = load_wav(path)
    width = rate // 100
    return [(sum(x * x for x in samples[i:i + width]) / width) ** 0.5
            for i in range(0, len(samples) - width, width)]


def centred(values):
    mean = sum(values) / len(values)
    values = [v - mean for v in values]
    return values, sum(v * v for v in values) ** 0.5


def take_matches_mix(take: Path, mix_envelope, offset_s: float) -> float:
    """Best envelope correlation of the take's first 4 s against the mix, +/-0.3 s."""
    clip, clip_norm = centred(envelope(take)[:400])
    start, best = round(offset_s * 100), -1.0
    for shift in range(-30, 31):
        if start + shift < 0 or start + shift + len(clip) > len(mix_envelope):
            continue
        seg, seg_norm = centred(mix_envelope[start + shift:start + shift + len(clip)])
        best = max(best, sum(x * y for x, y in zip(clip, seg)) / (clip_norm * seg_norm + 1e-9))
    return best


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("slug")
    parser.add_argument("--name", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--allow-newer-sources", action="store_true",
                        help="warn instead of refusing when sources postdate the mp4; the audio check still runs")
    parser.add_argument("--video-repo", default=str(Path.home() / "Development/Personal/ninadpathak-video"))
    args = parser.parse_args()
    slug = args.slug
    if not re.fullmatch(r"[a-z0-9-]+", slug):
        raise SystemExit(f"bad slug {slug!r}")

    repo = Path(args.video_repo)
    film = repo / "films" / slug
    mp4, poster = repo / "out" / f"{slug}.mp4", repo / "out" / f"{slug}-poster.png"
    script, timeline_path = film / "script.md", film / "timeline.json"
    voice = film / "assets" / "voice"
    words_path, mix_path = voice / "words.json", film / "assets" / "mix.wav"
    for path in (mp4, poster, script, timeline_path, words_path, mix_path):
        if not path.is_file():
            raise SystemExit(f"missing {path}")

    timeline = json.loads(timeline_path.read_text(encoding="utf-8"))
    words = json.loads(words_path.read_text(encoding="utf-8"))
    fps = timeline["fps"]
    offsets = {line: round(frame / fps, 3) for line, frame in timeline["voice"]["lines"].items()}

    # Freshness: nothing the captions come from may postdate the delivered render.
    rendered = mp4.stat().st_mtime
    # mix.wav is left out: the video repo regenerates it byte-identically as a check.
    newer = [p for p in (script, timeline_path, words_path, *sorted(voice.glob("L*.wav")))
             if p.stat().st_mtime > rendered + 1]
    if newer:
        listed = ", ".join(str(p.relative_to(repo)) for p in newer)
        if not args.allow_newer_sources:
            raise SystemExit("stale render: changed after the delivered mp4 -> " + listed)
        print("warning: changed after the delivered mp4 (allowed) -> " + listed)
    # Compare each take with the audio inside the delivered mp4 itself (macOS afconvert
    # decodes its AAC track); without afconvert, fall back to the repo's mix.wav.
    audio_source = mix_path
    if shutil.which("afconvert"):
        decoded = Path(tempfile.mkdtemp()) / "delivered.wav"
        subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI16@48000", str(mp4), str(decoded)], check=True,
                       capture_output=True)
        audio_source = decoded
    else:
        print("afconvert not found: checking takes against mix.wav instead of the mp4's audio")
    mix_envelope = envelope(audio_source)
    for line in offsets:
        score = take_matches_mix(voice / f"{line}.wav", mix_envelope, offsets[line])
        print(f"{line}: take vs delivered audio {score:.2f}")
        if score < MIN_MATCH:
            raise SystemExit(f"stale render: {line}.wav does not match the delivered mix ({score:.2f} < {MIN_MATCH})")

    full = re.search(r"#{2,3} Full text[^\n]*\n\s*\n(.+?)\n", script.read_text(encoding="utf-8"))
    if not full:
        raise SystemExit(f"{script} has no 'Full text' paragraph")
    transcript = full.group(1).strip()
    # Each line's written text when the voice spelled something out ("Claude dot MD"),
    # otherwise the words it said.
    written = " ".join(words[line].get("text") or " ".join(w["w"] for w in words[line]["words"]) for line in offsets)
    if written != transcript:
        raise SystemExit("words.json does not match the script's full text")

    duration = round(timeline["durationInFrames"] / fps)
    content, static = Path("content/videos") / slug, Path("static/videos") / slug
    content.mkdir(parents=True, exist_ok=True)
    static.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(mp4, static / f"{slug}.mp4")
    shutil.copyfile(poster, static / "poster.png")
    shutil.copyfile(words_path, content / "words.json")
    landscape = timeline["formats"]["landscape"]
    meta = {
        "name": args.name,
        "description": args.description,
        "upload_date": datetime.fromtimestamp(rendered, IST).replace(microsecond=0).isoformat(),
        "duration_seconds": duration,
        "width": landscape["width"],
        "height": landscape["height"],
        "file": f"{slug}.mp4",
        "poster": "poster.png",
        "poster_webp": "poster.webp",
        "captions": "captions.vtt",
        "line_offsets": offsets,
        "transcript": transcript,
    }
    header = (f"# Narrated explainer for /articles/{slug}/, imported by tools/import_video.py from\n"
              f"# ninadpathak-video films/{slug} (render of {meta['upload_date']}).\n")
    (content / "video.yaml").write_text(header + yaml.safe_dump(meta, sort_keys=False, allow_unicode=True, width=1000),
                                        encoding="utf-8")
    subprocess.run([sys.executable, "tools/build_video_captions.py", slug], check=True)
    subprocess.run([sys.executable, "tools/build_video_poster.py", slug], check=True)
    print(f"imported {slug}: {duration}s, {mp4.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
