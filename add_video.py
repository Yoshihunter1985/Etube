#!/usr/bin/env python3
"""
add_video.py - paste a YouTube URL, get a compressed mp4 + thumbnail dropped
into this project, and videos.json updated automatically.

Requires (one-time setup):
    pip install yt-dlp
    ffmpeg installed and on your PATH (winget install ffmpeg, or from ffmpeg.org)
    deno installed and on your PATH (winget install DenoLand.Deno)

Usage:
    python add_video.py https://www.youtube.com/watch?v=XXXXXXXX
"""
import json
import re
import subprocess
import sys
import uuid
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
VIDEOS_DIR = ROOT / "videos"
THUMBS_DIR = ROOT / "thumbs"
MANIFEST = ROOT / "videos.json"

COLORS = ["#FF6B6B", "#4ECDC4", "#FFD93D", "#95E06C", "#B185DB"]
SHAPES = ["sun", "star", "flower", "heart", "rocket"]

SCALE = "854:480"
CRF = "26"


def load_manifest():
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text())
    return []


def save_manifest(data):
    MANIFEST.write_text(json.dumps(data, indent=2))


def next_style(count):
    return COLORS[count % len(COLORS)], SHAPES[count % len(SHAPES)]


def run(cmd):
    print("  $", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main():
    if len(sys.argv) < 2:
        print("Usage: python add_video.py <youtube-url>")
        sys.exit(1)

    url = sys.argv[1]
    VIDEOS_DIR.mkdir(exist_ok=True)
    THUMBS_DIR.mkdir(exist_ok=True)

    vid_id = uuid.uuid4().hex[:8]
    raw_path = ROOT / f"_raw_{vid_id}.mp4"
    out_path = VIDEOS_DIR / f"{vid_id}.mp4"
    thumb_path = THUMBS_DIR / f"{vid_id}.jpg"

    YTDLP = [sys.executable, "-m", "yt_dlp"]

    print(f"[1/4] Downloading -> {raw_path.name}")
    run([
        *YTDLP,
        "--remote-components", "ejs:github",
        "--no-playlist",
        "-f", "bv*[height<=720]+ba/b[height<=720]",
        "--merge-output-format", "mp4",
        "-o", str(raw_path),
        url,
    ])

    print("[2/4] Reading title")
    title_result = subprocess.run(
        [*YTDLP, "--no-playlist", "--get-title", url],
        check=True, capture_output=True, text=True,
    )
    title = title_result.stdout.strip() or vid_id

    print(f"[3/4] Compressing -> {out_path.name}")
    run([
        "ffmpeg", "-y", "-i", str(raw_path),
        "-vf", f"scale={SCALE}",
        "-c:v", "libx264", "-crf", CRF, "-preset", "veryfast",
        "-c:a", "aac", "-b:a", "96k",
        "-movflags", "+faststart",
        str(out_path),
    ])

    print(f"[4/4] Thumbnail -> {thumb_path.name}")
    run([
        "ffmpeg", "-y", "-i", str(out_path),
        "-ss", "00:00:02", "-vframes", "1",
        "-vf", "scale=320:-1",
        str(thumb_path),
    ])

    raw_path.unlink(missing_ok=True)

    manifest = load_manifest()
    color, shape = next_style(len(manifest))
    manifest.append({
        "id": vid_id,
        "title": title,
        "color": color,
        "shape": shape,
        "src": f"videos/{vid_id}.mp4",
        "thumb": f"thumbs/{vid_id}.jpg",
    })
    save_manifest(manifest)

    print(f"\nDone. Added {title} as {vid_id}.")
    print(f"  video:  videos/{vid_id}.mp4")
    print(f"  thumb:  thumbs/{vid_id}.jpg")
    print(f"  videos.json updated ({len(manifest)} total)")


if __name__ == "__main__":
    main()
