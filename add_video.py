#!/usr/bin/env python3
"""
add_video.py - paste a YouTube URL, get a compressed mp4 + thumbnail dropped
into this project, and videos.json updated automatically.

For adding many videos in one sitting, use the batch studio instead:
    run_studio.bat
which gives you a local web page to paste a list of URLs and push once at
the end.

Requires (one-time setup):
    pip install yt-dlp flask
    ffmpeg installed and on your PATH (winget install ffmpeg, or from ffmpeg.org)
    deno installed and on your PATH (winget install DenoLand.Deno)

Usage:
    python add_video.py https://www.youtube.com/watch?v=XXXXXXXX
"""
import sys
from video_core import process_url


def main():
    if len(sys.argv) < 2:
        print("Usage: python add_video.py <youtube-url>")
        sys.exit(1)

    result = process_url(sys.argv[1], log=print)

    if result["status"] == "done":
        print(f"\nDone. Added {result['title']} as {result['id']}.")
        print(f"  video:  videos/{result['id']}.mp4")
        print(f"  thumb:  thumbs/{result['id']}.jpg")
    else:
        print(f"\nFailed: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
