"""
video_core.py - shared logic for turning one YouTube URL into a compressed
mp4 + thumbnail + videos.json entry. Used by both add_video.py (single video,
command line) and studio_server.py (batch, local web UI).
"""
import json
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

YTDLP = [sys.executable, "-m", "yt_dlp"]


def get_duration(path):
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())


def load_manifest():
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text())
    return []


def save_manifest(data):
    MANIFEST.write_text(json.dumps(data, indent=2))


def next_style(count):
    return COLORS[count % len(COLORS)], SHAPES[count % len(SHAPES)]


def process_url(url, log=print):
    """
    Download, compress, thumbnail, and append one video to videos.json.
    Never raises - always returns a dict describing what happened, so a
    batch run can keep going even if one URL fails.
    """
    VIDEOS_DIR.mkdir(exist_ok=True)
    THUMBS_DIR.mkdir(exist_ok=True)

    vid_id = uuid.uuid4().hex[:8]
    raw_path = ROOT / f"_raw_{vid_id}.mp4"
    out_path = VIDEOS_DIR / f"{vid_id}.mp4"
    thumb_path = THUMBS_DIR / f"{vid_id}.jpg"

    try:
        log(f"[{vid_id}] downloading...")
        subprocess.run(
            [
                *YTDLP,
                "--remote-components", "ejs:github",
                "--no-playlist",
                "-f", "bv*[height<=720]+ba/b[height<=720]",
                "--merge-output-format", "mp4",
                "-o", str(raw_path),
                url,
            ],
            check=True, capture_output=True, text=True,
        )

        title_result = subprocess.run(
            [*YTDLP, "--no-playlist", "--get-title", url],
            check=True, capture_output=True, text=True,
        )
        title = title_result.stdout.strip() or vid_id

        log(f"[{vid_id}] compressing...")
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(raw_path),
                "-vf", f"scale={SCALE}",
                "-c:v", "libx264", "-crf", CRF, "-preset", "veryfast",
                "-c:a", "aac", "-b:a", "96k",
                "-movflags", "+faststart",
                str(out_path),
            ],
            check=True, capture_output=True, text=True,
        )

        log(f"[{vid_id}] thumbnail...")
        try:
            duration = get_duration(out_path)
        except Exception:
            duration = 10.0
        thumb_time = min(max(duration * 0.15, 3), 20)

        subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(out_path),
                "-ss", f"{thumb_time:.2f}", "-vframes", "1",
                "-vf", "scale=320:-1",
                str(thumb_path),
            ],
            check=True, capture_output=True, text=True,
        )

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

        log(f"[{vid_id}] done: {title}")
        return {"url": url, "status": "done", "title": title, "id": vid_id}

    except subprocess.CalledProcessError as e:
        raw_path.unlink(missing_ok=True)
        stderr = (e.stderr or "").strip().splitlines()
        message = stderr[-1] if stderr else str(e)
        log(f"[{vid_id}] failed: {message}")
        return {"url": url, "status": "error", "error": message}

    except Exception as e:
        raw_path.unlink(missing_ok=True)
        log(f"[{vid_id}] failed: {e}")
        return {"url": url, "status": "error", "error": str(e)}
