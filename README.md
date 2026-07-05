# Kid Video Player — setup notes

## 1. What's in this folder
- `index.html` — the whole app, one file, no build step
- `videos.json` — the list she can watch. Gets updated automatically now (see below)
- `add_video.py` — paste a YouTube URL, get it downloaded, compressed, thumbnailed,
  and added to `videos.json`
- `add_video.bat` — Windows double-click wrapper for the above
- `push.bat` — commits and pushes everything to GitHub
- `add_and_publish.bat` — does both of the above in one go: paste a URL, walk away,
  it's downloaded, converted, added, and pushed live
- Currently `videos.json` has 5 public sample clips wired up so you can see the app
  working immediately

Push this folder to a GitHub repo, turn on GitHub Pages (Settings → Pages → deploy
from main branch, root folder), and it's live at
`https://yourusername.github.io/reponame/`.

## 2. One-time setup (per machine)
```bash
pip install yt-dlp
```
Also install ffmpeg and make sure it's on your PATH — easiest on Windows is
`winget install ffmpeg`, or download from ffmpeg.org.

## 3. Adding a video — the easy way (one at a time)
Double-click `add_and_publish.bat`, paste a YouTube URL when prompted, hit enter.
It will:
1. Download the video (capped at 720p source, no point pulling 4K just to shrink it)
2. Compress it to 480p H.264 (~5–10MB per minute — see settings below)
3. Grab a thumbnail frame automatically
4. Add an entry to `videos.json` with a rotating color/shape so tiles don't all
   look identical
5. `git add`, `commit`, `push` — live on GitHub Pages a minute or two later

If you'd rather review before pushing, use `add_video.bat` on its own (just
downloads/converts/adds to the manifest), check things look right, then run
`push.bat` separately when you're ready.

You can also just run `python add_video.py <url>` directly from a terminal if
that's easier than the .bat files.

### Compression settings (already baked into add_video.py)
```bash
ffmpeg -i source.mp4 -vf "scale=854:480" -c:v libx264 -crf 26 -preset veryfast \
  -c:a aac -b:a 96k -movflags +faststart output.mp4
```
- `scale=854:480` → 480p, plenty sharp for the size it'll display at
- `-crf 26` → good quality/size tradeoff; raise to ~28–30 in `add_video.py` if you
  want files smaller
- Rough output size: **~5–10 MB per minute** of video at these settings

## 3b. Adding many videos at once — the batch studio

For sitting down and curating a bunch of videos in one go: paste a list of
URLs into a local web page, hit Start, let it churn through the whole list,
then hit one Push button at the end.

One-time setup (in addition to yt-dlp/ffmpeg/deno from above):
```powershell
pip install flask
```

To run it:
```powershell
run_studio.bat
```
This opens `http://localhost:5050` in your browser (it only runs on your own
machine — nothing here is exposed to the internet). Paste one YouTube URL
per line into the box, hit **Start**. Each one gets downloaded, compressed,
thumbnailed, and added to `videos.json` in sequence — you can leave it
running and walk away. Each line shows a status dot (waiting / working /
done / failed) so you can see progress at a glance.

Once everything's finished, the **Push to GitHub** button lights up. Hit it
once and it commits and pushes everything from that whole session in a
single go.

If a particular URL fails (private video, region-locked, playlist link,
etc.), it won't stop the rest of the batch — that one just shows as failed
and everything else keeps going.

Close the `run_studio.bat` window when you're done for the session.

## 4. Where the video files live

Videos are now stored directly in the repo, under `/videos`, with thumbnails under
`/thumbs` — that's what makes the one-script workflow possible (a plain `git push`
handles everything, no separate upload step to a release or bucket).

**GitHub's real limits** (checked July 2026):
- Hard block on any single file over 100MB — compressed clips will be way under this
- Repo itself should stay under ~1GB (soft), definitely under 5GB
- At ~5–10MB/minute, that's **well over 100 short clips** before size becomes
  anything to think about

If the library eventually grows past that, two options, both easy to swap to later:
- **GitHub Releases** — attach large files as release assets instead of committing
  them, point `src` at the release asset URL. No cumulative cap, built for exactly
  this.
- **Cloudflare R2** — free tier is 10GB storage with no egress fees. Same idea,
  just point `src` at the R2 URL instead of a local path.

Neither is needed yet — direct-in-repo is simpler and you're nowhere near the limit.

## 5. Editing the video list

Each entry in `videos.json`:
```json
{
  "id": "unique-id",
  "title": "not shown to her, just for your reference",
  "color": "#FF6B6B",
  "shape": "sun | star | flower | heart | rocket",
  "src": "https://.../video.mp4",
  "thumb": "optional/path/to/thumb.jpg"
}
```
Add or remove entries, commit, push — done. No code changes needed.

## 6. Getting it onto the iPad like an app
1. Open the GitHub Pages URL in Safari
2. Share button → "Add to Home Screen"
3. It'll launch full-screen with no address bar or Safari chrome

## 7. Locking her into just this app (the actual "no escaping" part)
The app avoids native video controls (no fullscreen/share/cast buttons) and blocks
long-press menus, but the OS level is still open to her. For real toddler-proofing,
turn on **Guided Access**:
- Settings → Accessibility → Guided Access → on, set a passcode
- Open the app, triple-click the side/home button, tap Start
- She's now locked into just this app until you enter the passcode

That combo (curated JSON + no algorithm + no native controls + Guided Access) covers
everything you asked for: no ads, no recommendations, nothing outside what you put
in the list, and no extra cost anywhere in the stack.
