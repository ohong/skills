---
name: demo-video
description: Create a narrated MP4 demo from browser screenshots, low-cost fal.ai text-to-speech, and ffmpeg. Use for still-image product walkthroughs synchronized to narration.
---

# Demo Video

Capture browser scenes, write narration, generate speech with fal.ai, and combine still images with audio into an MP4.

Adapted from [dctanner's demo-video gist](https://gist.github.com/dctanner/ee7fe7997bba0efbca49b8c0bdc1936a).

## Setup and voice choice

Use available browser controls to capture screenshots. Install `ffmpeg` if needed; both `ffmpeg` and `ffprobe` must be available.

Use `FAL_KEY` from the environment. Never print it or place it in the skill, narration, or output artifacts. For Python, install the client in an isolated environment:

```bash
python3 -m venv /tmp/demo-video-venv
/tmp/demo-video-venv/bin/python -m pip install fal-client
```

Default to `fal-ai/kokoro/american-english`, voice `af_heart`, speed `1`. It is a fast, inexpensive choice for English narration. Its [listed price](https://fal.ai/models/fal-ai/kokoro/american-english) was $0.02 per 1,000 characters on 2026-09-06: 5,000 characters cost about $0.10. Recheck pricing before estimating a new job. Latency depends on queue and request length.

Use another model when the user needs a different language, voice, or higher expressiveness. Check that model's current API schema; fields differ. Do not introduce voice cloning unless requested.

## Prepare the scenes

1. Choose an output directory such as `tmp/video/`, without overwriting unrelated files.
2. Capture each scene at a consistent viewport. Prefer readable viewport captures over tall full-page screenshots.
3. Write one narration file per scene, such as `scene01.txt`, paired with `scene01.png`. Keep narration tied to visible actions and results.
4. Set the scene order and review the script before paid synthesis. Keep one voice and speed across scenes.

When subagents are available, delegate speech generation and rendering after the screenshots and script are ready. Use the environment's actual subagent tool, such as `collaboration.spawn_agent`. Give the worker ordered file paths, narration, output settings, and the requested destination. Keep review and final verification with the main agent. If delegation is unavailable, run the same workflow directly.

## Generate speech

Run this example from the chosen output directory. It reads `scene01.txt`, saves the response for reuse, and downloads the returned WAV file. Use a separate response and audio file for each scene.

```bash
/tmp/demo-video-venv/bin/python - <<'PY'
import json
import os
from pathlib import Path
from urllib.request import urlretrieve

import fal_client

if not os.environ.get("FAL_KEY"):
    raise SystemExit("Set FAL_KEY before generating narration.")

text = Path("scene01.txt").read_text().strip()
if not text:
    raise SystemExit("scene01.txt is empty.")

response_path = Path("scene01.response.json")
if response_path.exists():
    result = json.loads(response_path.read_text())
else:
    result = fal_client.subscribe(
        "fal-ai/kokoro/american-english",
        arguments={"prompt": text, "voice": "af_heart", "speed": 1},
    )
    response_path.write_text(json.dumps(result, indent=2))

urlretrieve(result["audio"]["url"], "scene01.wav")
PY
```

See the [Kokoro API documentation](https://fal.ai/models/fal-ai/kokoro/american-english/api) for current limits and voice options. The input field is `prompt`; the output is `audio.url`.

Reuse successful audio to avoid paying twice. The example assumes the text, voice, and speed have not changed when a response file exists. After editing them, use a new scene version or remove its stale response and audio deliberately. If a download fails, retry that download from the saved response. For API failures, inspect the error before retrying; stop repeated failures instead of submitting blindly. Do not assume provider-specific concurrency limits.

Validate each downloaded file by checking its audio stream and positive duration, then decoding it. File size alone does not establish validity:

```bash
ffprobe -v error -select_streams a:0 \
  -show_entries stream=codec_name,sample_rate,channels:format=duration \
  -of json scene01.wav
ffmpeg -v error -i scene01.wav -f null -
```

## Render and combine

Render every scene with the same even dimensions, frame rate, pixel format, video codec, and audio settings. This example letterboxes to 1920×1080 at 30 fps; choose another shared size when the user requests it. Avoid stretching screenshots.

Run for each scene, changing the three filenames together:

```bash
duration=$(ffprobe -v error -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 scene01.wav)
ffmpeg -hide_banner -loglevel error -n \
  -loop 1 -framerate 30 -i scene01.png -i scene01.wav \
  -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p" \
  -c:v libx264 -preset fast -tune stillimage -r 30 \
  -c:a aac -ar 48000 -ac 2 -b:a 128k -af apad \
  -t "$duration" -movflags +faststart scene01.mp4
```

Build the concat file in scene order. Use simple filenames without apostrophes:

```bash
cat > concat.txt <<'EOF'
file 'scene01.mp4'
file 'scene02.mp4'
file 'scene03.mp4'
EOF
ffmpeg -hide_banner -loglevel error -n -f concat -safe 0 \
  -i concat.txt -c copy -movflags +faststart demo.mp4
```

Adjust the list to the actual scene count. Inspect the final streams and duration with `ffprobe`, then decode the full video with `ffmpeg -v error -i demo.mp4 -f null -`. Compare its duration with the sum of scene audio durations, allowing frame and codec rounding.

Review sampled frames and listen to the narration, including scene boundaries. Confirm readable UI, correct order, complete speech, and no clipping or blank endings. Report listening as unverified if audio playback or inspection is unavailable.

Return the local MP4 as an absolute-path media embed or link. Publish only when the user requests it and supplies or identifies a destination. Do not assume an R2 bucket, public URL, or upload permission.
