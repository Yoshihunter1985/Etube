#!/usr/bin/env python3
"""
studio_server.py - local web UI for adding a batch of YouTube videos in one
sitting. Paste a list of URLs, hit Start, let it run, then hit Push once at
the end. Everything happens on your own machine; nothing here is exposed
to the internet.

Requires (one-time setup):
    pip install flask

Run with:
    run_studio.bat
or directly:
    python studio_server.py
then open http://localhost:5050 in a browser.
"""
import pathlib
import subprocess
import threading

from flask import Flask, jsonify, request

from video_core import process_url

ROOT = pathlib.Path(__file__).resolve().parent
app = Flask(__name__)

state_lock = threading.Lock()
state = {
    "running": False,
    "items": [],  # [{url, status: pending|working|done|error, title?, id?, error?}]
}


def run_batch(urls):
    with state_lock:
        state["running"] = True
        state["items"] = [{"url": u, "status": "pending"} for u in urls]

    for i, url in enumerate(urls):
        with state_lock:
            state["items"][i]["status"] = "working"

        result = process_url(url)

        with state_lock:
            state["items"][i].update(result)

    with state_lock:
        state["running"] = False


@app.route("/")
def index():
    return (ROOT / "studio.html").read_text(encoding="utf-8")


@app.route("/api/batch", methods=["POST"])
def start_batch():
    with state_lock:
        if state["running"]:
            return jsonify({"error": "A batch is already running"}), 409

    body = request.get_json(force=True) or {}
    raw_urls = body.get("urls", [])
    urls = [u.strip() for u in raw_urls if u.strip()]

    if not urls:
        return jsonify({"error": "No URLs given"}), 400

    threading.Thread(target=run_batch, args=(urls,), daemon=True).start()
    return jsonify({"started": len(urls)})


@app.route("/api/status")
def status():
    with state_lock:
        return jsonify(state)


@app.route("/api/push", methods=["POST"])
def push():
    try:
        add_result = subprocess.run(
            ["git", "add", "."], cwd=ROOT, capture_output=True, text=True,
        )
        commit_result = subprocess.run(
            ["git", "commit", "-m", "Batch add videos"],
            cwd=ROOT, capture_output=True, text=True,
        )
        push_result = subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=ROOT, capture_output=True, text=True,
        )
        return jsonify({
            "add_output": add_result.stdout + add_result.stderr,
            "commit_output": commit_result.stdout + commit_result.stderr,
            "push_output": push_result.stdout + push_result.stderr,
            "push_ok": push_result.returncode == 0,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=False)
