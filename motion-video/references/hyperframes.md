# Optional HyperFrames local renderer

Remotion remains preferred for the existing motion kit, React components, and established project workflow. HyperFrames is an optional fit for plain HTML, CSS, and GSAP scenes. This choice changes authoring, not the film's quality requirements. Remotion also provides [official GSAP integration](https://www.remotion.dev/docs/gsap), including a paused timeline that seeks to each frame.

## Isolated setup

Use a dedicated video project with Node 22+, an installed Chrome, and FFmpeg/FFprobe for verification. Keep the lockfile and browser version. The following installation and wrapper settings were used in the local smoke test; change the Chrome path for another machine. These commands avoid the vendor's global skill setup and authenticated media workflow.

```sh
mkdir -p runtime
cd runtime
npm install --save-exact --cache .npm-cache hyperframes@0.8.30 gsap@3.14.2
mkdir -p cache/fonts cache/frames cache/tmp film/assets
cp node_modules/gsap/dist/gsap.min.js film/assets/gsap.min.js
cat > hf <<'SH'
#!/bin/sh
TASK_RUNTIME=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
export HYPERFRAMES_NO_TELEMETRY=1
export HYPERFRAMES_SKIP_SKILLS=1
export HYPERFRAMES_FONT_CACHE_DIR="$TASK_RUNTIME/cache/fonts"
export HYPERFRAMES_EXTRACT_CACHE_DIR="$TASK_RUNTIME/cache/frames"
export TMPDIR="$TASK_RUNTIME/cache/tmp"
export HYPERFRAMES_BROWSER_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
exec "$TASK_RUNTIME/node_modules/.bin/hyperframes" "$@"
SH
chmod +x hf
```

Use `npm ci --cache .npm-cache` with the saved lockfile for subsequent installs. Do not run `init`, `skills update`, authentication, hosted rendering, uploads, or generated-media commands for this recipe. Local rendering needs no HeyGen credits; optional services have separate costs. Installation still uses the network, and the package contains optional AI dependencies. [Official quickstart](https://hyperframes.heygen.com/quickstart).

## Authoring contract

Create `film/index.html` with local scripts, captures, and licensed font files. The fragment below illustrates the contract; it is not a complete film. Copy the exact fonts into `film/assets/`, declare every used weight, and record their sources. Generic Arial/Georgia names triggered font substitutions and downloads in the smoke test.

```html
<script src="assets/gsap.min.js"></script>
<style>
@font-face { font-family: "ProductLocal"; src: url("assets/product-regular.woff2") format("woff2"); font-weight: 400; }
body { margin: 0; font-family: "ProductLocal"; }
#root { position: relative; width: 1920px; height: 1080px; overflow: hidden; }
.clip { position: absolute; inset: 0; }
</style>
<div id="root" data-composition-id="main" data-start="0"
     data-width="1920" data-height="1080" data-duration="10" data-fps="30">
  <section id="proof" class="clip" data-start="0" data-duration="10" data-track-index="0">
    <img id="capture" src="assets/actual-product.png" alt="Actual product result">
  </section>
</div>
<script>
window.__timelines = window.__timelines || {};
const timeline = gsap.timeline({ paused: true });
timeline.fromTo('#capture', { opacity: 0 }, { opacity: 1, duration: 0.4 }, 0);
window.__timelines.main = timeline;
</script>
```

The registry key matches `data-composition-id`, which can differ from the DOM `id`. Give timed clips stable IDs. Declare CSS dimensions as well as metadata. Register one finite, paused timeline synchronously. Avoid clocks, unseeded randomness, infinite repeats, and fetching during rendering. Later `fromTo` tweens on the same property may need `immediateRender:false`. [HTML schema](https://hyperframes.heygen.com/reference/html-schema), [deterministic rendering](https://hyperframes.heygen.com/concepts/determinism).

Keep exactly one composition entry HTML at the project root; put style variants in separate directories. When reusing an image across scenes, give each instance a unique ID and explicit `data-start`/`data-duration`: duplicate-media checks do not infer parent timing. Mark deliberately cropped image elements with `data-layout-allow-overflow`, then visually inspect those crops. Do not use that annotation to hide accidental clipping.

## Check, render, inspect

Run from `runtime/`. The local diagnostic used these flags at 1280×720; replace `film` with the composition folder.

```sh
./hf check film
./hf render film --quality high --fps 30 --workers 1 --strict-all --no-best-effort --output film/final.mp4
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,nb_frames:format=duration,size -of json film/final.mp4
ffmpeg -v error -i film/final.mp4 -f null -
sips -g pixelWidth -g pixelHeight film/assets/actual-product.png
```

`check` examines lint, runtime, layout, motion, and contrast. Resolve its findings before delivery. The `high` flag selects an encoder preset; it does not certify composition, motion, or product proof. [Rendering guide](https://hyperframes.heygen.com/guides/rendering), [CLI reference](https://hyperframes.heygen.com/packages/cli).

Inspect decoded image dimensions and format, not the browser's reported device pixel ratio or the filename extension. In the Boardroom trial, files named `.png` contained JPEG data. Renaming or converting them cannot restore lost detail. Check the most enlarged settled UI crop at native export resolution. More output pixels cannot restore missing capture detail. Capture quality is independent of renderer choice.

Apply the main skill's full review: genuine action-to-result captures, readable holds, adjacent transition frames, first/last frames, complete playback, and sound listening. Preserve the capture ledger and mark any reconstruction. Check the requested duration, frame count, dimensions, and audio independently for each cut.
