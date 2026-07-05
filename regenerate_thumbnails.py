#!/usr/bin/env python3
"""
regenerate_thumbnails.py - re-extracts a better thumbnail frame for every
video already in videos.json, using the same "15% into the video" logic
that new videos get automatically. Run this once after updating
video_core.py to fix thumbnails that were all grabbed at a fixed 2 seconds.

Usage:
    python regenerate_thumbnails.py
"""
from video_core import ROOT, VIDEOS_DIR, THUMBS_DIR, load_manifest, get_duration
import subprocess


def main():
    manifest = load_manifest()
    if not manifest:
        print("No videos in videos.json.")
        return

    for entry in manifest:
        vid_id = entry["id"]
        video_path = VIDEOS_DIR / f"{vid_id}.mp4"
        thumb_path = THUMBS_DIR / f"{vid_id}.jpg"

        if not video_path.exists():
            print(f"[{vid_id}] skipped - video file not found ({video_path})")
            continue

        try:
            duration = get_duration(video_path)
        except Exception:
            duration = 10.0
        thumb_time = min(max(duration * 0.15, 3), 20)

        print(f"[{vid_id}] grabbing frame at {thumb_time:.1f}s...")
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(video_path),
                "-ss", f"{thumb_time:.2f}", "-vframes", "1",
                "-vf", "scale=320:-1",
                str(thumb_path),
            ],
            check=True, capture_output=True, text=True,
        )

    print("\nDone. Thumbnails regenerated.")


if __name__ == "__main__":
    main()
