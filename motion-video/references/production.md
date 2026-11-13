# Production toolbox

Read when moving from the designed storyboard to editable animation and exports. Tool choices serve the treatment. Verify the tools and versions actually available in the current environment; installing this skill does not install After Effects, Blender, Remotion, an image/video API, or paid accounts.

## Discover and choose

Inspect existing video projects before scaffolding one. Keep dependencies inside the video project and avoid altering the product application's package graph. Follow local instructions about dependency additions. Keep a package manifest and lockfile. The bundled [motion kit](../assets/motion-kit/README.md) provides reusable mechanics without prescribing a finished layout. The scaffold creates an explicit diagnostics composition; it is not a product film.

Check Node, ffmpeg, ffprobe, a Python interpreter with Pillow, the installed Remotion version, browser capture, fonts, and perceptual audio/video review. In Codex desktop, use `load_workspace_dependencies` if system Python lacks Pillow. Discover paths; do not assume the user's shell Python and bundled Python have the same packages. Distinguish file playback for the user from audio/video input the model can actually perceive.

Prefer Remotion for deterministic, editable software films built from typography, vector shapes, layered UI, footage, and audio. A captured-only FFmpeg edit is efficient for a faithful walkthrough but makes custom UI choreography harder. A native After Effects/Blender workflow can justify its complexity for bespoke compositing or 3D assets. Choose the approach based on the needed shots and available tools, and record the trade-off briefly.

The local Remotion skill was already installed when this skill was created. Discover `remotion-best-practices` in the active skill catalog, then load its create, markup, render, and relevant sub-guides. On the original workstation it is at `~/.codex/skills/remotion-best-practices/SKILL.md`. If absent, use [official Remotion agent skills](https://www.remotion.dev/docs/ai/skills) and the relevant official API documentation. Do not require an unrelated plugin or mechanically reinstall/update a working environment.

The creation workflow in the Remotion helper may default to preview-only. For `/motion-video`, the user has requested finished videos: render all requested cuts. User/project instructions take precedence over supporting skills.

## Capture and assets

Use an available browser or native-app capture tool to rehearse and capture the selected product flow. Use recordings for interactions when supported; otherwise capture sequential screenshots of the actual starting state, action state, and result. Recordings and screenshots from the user are valid source material when their product version and provenance are understood. A running local build is valid; identify local-only features instead of implying they are deployed.

Capture at sufficient resolution for the planned crops. Record capture date, URL or app/build, viewport, state, and the source of data. Save originals before compositing. Keep a ledger in assets.md mapping each exported proof shot to its capture file and source time range or screenshot sequence. Distinguish captured UI, supplemental reconstruction, and editorial graphics. A login wall is a real access limitation: use available docs/public pages to prepare the brief and ask only for the access or asset needed to prove the missing flow. Never invent the inaccessible app's result.

Budget source pixels before choosing a close view. Divide the region's largest settled width in the export by its width in the saved image. A 500px captured panel enlarged to 1250px uses 2.5× magnification; a 1920px final encode cannot restore its missing detail. Inspect that exact crop at final output size before approving the proof style frame. Capture at a higher device scale, compose a smaller view with a separate readable callout, or use the limited reconstruction route below. Record any remaining softness as a failed craft condition, not as a passing resolution check. Motion blur during travel does not justify a soft settled hold.

Check the exported screenshot's actual pixel dimensions and visible edges before using measured DOM coordinates. A host-window capture can clip a larger virtual viewport; a stitched full-page capture can duplicate content. Inspect the file, including the decisive control and result, rather than trusting the requested viewport. Keep CSS pixels, device pixels, and any screenshot scaling explicit in the capture ledger. Use the browser's supported page capture when native window capture is insufficient.

If the available browser tool cannot produce adequate source pixels, identify a capture capability before requesting a new renderer. One candidate is [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/tool-reference.md): its documented `emulate` tool accepts viewport `1280x720x2`, and `take_screenshot` accepts PNG output with a local `filePath`. Discover the installed tool schema before use. This route is researched, not validated by this skill's benchmark. Request provisioning only when the capability is missing; do not use shell browser drivers to bypass the active environment's browser restrictions. After access is available, verify the actual saved pixels, layout, and action/result again. A correct toolbar setting or screenshot command without a file is not a successful capture.

Prepare a deterministic demonstration. Remove unrelated notifications and use non-sensitive sample data. Keep genuine interaction states and clean handles before/after the action for editing. Avoid executing a real send, purchase, destructive change, or public post just to capture a confirmation screen without appropriate user authorization.

Sample inputs may be staged inside the product. Show the output that the product actually produces for that example. For AI products, retain the actual generated response; do not author a stronger answer and insert it into the captured interface. If a fixture or example output is necessary, label it visibly and record its source. Such a fixture does not establish live generation. Cuts may remove waits and repetitive steps, but must preserve the relationship between the shown action and result.

Build the proof shots from these saved captures. Improve readability first with tighter crops, higher-resolution capture, camera framing, longer holds, and separate callouts. Keep enough interface context for viewers to recognize the control and where its result appears. Captured UI must remain the main proof material, rather than a fleeting insert or decorative backdrop.

Reconstruct a selected detail only when capture-based framing cannot serve the shot. Use verified text, geometry, and states; return to the actual captured interface for the decisive result. Re-typeset excerpts belong in distinct editorial callouts, not substituted product output. Compare any reconstructed detail against its capture. AI-generated imagery may serve an original metaphor or asset; generated screenshots and recreated app shells do not count as actual UI. Asset reuse or matching the product's fonts and colors alone does not make a reconstruction a capture.

When sharper recapture is unavailable and product source is available, test a limited source-based detail before accepting a soft close-up. Reuse the selected component's actual markup, styles, fonts, and observed data. Prefer rendering the existing component; for other frameworks, extract the smallest faithful fragment. Render it at the original size beside the genuine capture, then inspect it at the planned close-view size. Record differences in font metrics, line breaks, borders, and bounds. This is supplemental reconstruction even when the source code is identical. It can remove a raster-resolution limit without proving another product interaction.

Keep the captured workflow as the main proof and reserve this supplement for selected details. Give the original captured object and its source-based detail the same rectangle and transform. Change their ownership deliberately after extraction, and restore the captured object before it rejoins the interface. A separate editorial callout is still preferable when the source fragment cannot match faithfully. Do not declare the source-pixel problem unavoidable merely because one capture method is blocked; test the applicable local fallback and retain its evidence.

A README can establish documented behavior without establishing screen geometry, save behavior, or a live result. In concept-only work, label proposed UI details and list what must be observed before production. Keep the distinction visible in shot contracts; an imagined panel is not an observed product state.

Save assets locally when appropriate and keep licensing/source records. References are private study inputs, not a footage library for new commercial films. Preserve editable source and assets needed to rerender; do not leave the render dependent on a temporary signed URL.

## Animation and render invariants

For Remotion, drive animation from frame time and use APIs supported by the installed version. Avoid wall-clock timers, nondeterministic random values, CSS animations, and network activity that changes from frame to frame. Load fonts and media before rendering. Use the installed guides for current media/effect components instead of copying an old snippet blindly.

Share a small set of film-specific tokens and components across shots: typography, palette, spacing, framing, motion behavior, and cursor treatment. Keep scene files independently inspectable. Register the three cuts explicitly with `durationInFrames = seconds × fps`; at 30 fps they are 300, 600, and 900 frames. Account for transition overlaps rather than summing shot lengths incorrectly. The final visible frame is `durationInFrames - 1`.

Start with a few style stills, then rough renders at lower resolution to inspect temporal relationships. A thumbnail proof cannot certify full-resolution typography. Render the final cuts at their intended dimensions and inspect those files. Use a suitable H.264/yuv420p MP4 delivery profile with AAC when sound is present, unless the destination needs something else. Preserve readable details after compression; use a higher-resolution master only if assets and the brief justify it.

Keep exact render commands in `render.md` or package scripts. Typical CLI shape, with the actual entry point and registered composition IDs substituted:

```sh
npx remotion compositions src/index.ts
npx remotion render src/index.ts Teaser10 renders/teaser-10s.mp4 --codec=h264
npx remotion render src/index.ts Product20 renders/product-20s.mp4 --codec=h264
npx remotion render src/index.ts Complete30 renders/complete-30s.mp4 --codec=h264
```

Read `npx remotion render --help` or current official docs for optional quality/codec flags. Do not claim these example IDs exist before registering them. Preserve logs. Render a representative short passage to estimate cost before expensive full exports. Follow any time limit in the current project instructions; this skill imposes no universal five-minute approval checkpoint. Reduce concurrency or isolate a slow effect when measured resource use warrants it.

## Video inspection helper

`scripts/inspect_video.py` uses Python, ffmpeg, ffprobe, and Pillow. It writes native-resolution PNG frames by default, a labeled contact sheet, raw probe inventory, and coverage metadata; optional audio extraction writes a WAV. `--thumbnail-width` controls only the sheet's preview tiles (480 pixels by default). Set `--frame-width` explicitly when you need smaller saved PNGs. Coverage records the actual saved frame and thumbnail dimensions separately. It records requested positions separately from safe seek positions and derives final-frame targets from decoded timestamps rather than duration/FPS arithmetic. Other seeks may quantize to nearby source frames. It never claims to watch or listen. Resolve `motion_skill_dir` to the directory containing the active `SKILL.md`. Choose an available Python with Pillow, using `load_workspace_dependencies` in Codex desktop when needed. No Pillow is needed by the verification helper.

```sh
# Broad coverage, including both ends. Inspect the returned sheet and key full-size frames.
python3 "$motion_skill_dir/scripts/inspect_video.py" "$reference_video" \
  --output-dir "$review_dir/overview" --sample-fps 1 --columns 4

# Dense examination of a specific 2-second transition.
python3 "$motion_skill_dir/scripts/inspect_video.py" "$reference_video" \
  --output-dir "$review_dir/transition" --overview-samples 0 \
  --sample-fps 12 --range 4-6 --columns 4
```

Run from any directory with absolute input/output paths. Outputs are protected unless `--overwrite` is supplied. The default 240-frame cap limits extraction and sheet size: use short ranges or split long clips into manageable sections. Native PNGs use more disk space than thumbnails. Increase density around fast moves and open the saved PNGs where text matters; the contact sheet cannot establish fine-detail quality. Inspect older evidence's dimensions before calling it full-size: previous helper versions saved reduced PNGs using `--thumbnail-width`. A one-second sample can miss an entire transition; it is an index, not the final temporal review. For narration, transcribe the full audio with timestamps using available tooling and check suspicious gaps/repetition. Speech recognizers can hallucinate words over instrumental music.

## Verify the actual exports

```sh
python3 "$motion_skill_dir/scripts/verify_video.py" "$render_dir/teaser-10s.mp4" \
  --duration 10 --duration-tolerance-frames 1 --width 1920 --height 1080 \
  --fps 30 --aspect 16:9 --video-codec h264 --audio-codec aac \
  --expect-audio --decode --diagnostics --json "$review_dir/teaser-10s.json"
```

Repeat with 20 and 30 seconds and the correct filenames. For explicitly silent exports, omit `--audio-codec` and use `--expect-no-audio`. Substitute the actual requested dimensions, rates, and codecs. The duration check targets the video stream; also inspect reported container/audio durations and tails when relevant.

Exit 0 means the requested invariants passed, 1 means an invariant or decode failure, and 2 means a tool/input/output error. Black/silence/volume findings are warnings requiring interpretation: intentional black backgrounds and rests are valid. Check reported time ranges against the storyboard. The helper measures sample peak/mean volume, not integrated loudness or true peak. If the mix needs those measurements, use an available loudness meter or an ffmpeg `ebur128=peak=true` analysis and retain its output.

Combine technical reports with direct visual/temporal review. Neither helper proves legibility, smooth motion, musical fit, correct product claims, or persuasion. If listening/video understanding is unavailable, name the actual review method and remaining gap in `review.md` and the handoff.

## Deliverable layout

A useful project layout is:

```text
<product>-<date>/
  brief.md, storyboard.md, assets.md, review.md, render.md
  package.json, lockfile, src/       editable composition
  public/                           cleared production assets
  captures/                         verified source UI
  storyboard/                       designed frames and sheet
  renders/                          three MP4s and poster
  review/                           frame samples and technical reports
```

Adapt to an existing project rather than duplicating its structure. Keep reference-study MP4s outside public output folders. Link final artifacts with absolute paths. Publishing and paid resources follow their explicit authorization boundaries.
