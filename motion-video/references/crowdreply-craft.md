# CrowdReply: making a sparse UI film feel directed

Read for films with restrained typography, large camera moves, connected UI objects, and a light-to-dark close. This is one treatment, not a required house style.

[Original, 41.84 seconds](videos/crowdreply-42s.mp4) · [overview](study/crowdreply-42s/overview/contact-sheet.jpg) · [opening](study/crowdreply-42s/opening/contact-sheet.jpg) · [camera passage](study/crowdreply-42s/camera/contact-sheet.jpg) · [document-to-notification passage](study/crowdreply-42s/payoff/contact-sheet.jpg)

Oscar supplied this reference on 2026-09-06. It is 1920×1080, 25 fps, H.264 with stereo AAC. The video stream lasts 41.84s; the container lasts 41.898667s. Its source and hash are in [library.json](library.json). The reference is private study material, not footage or music cleared for a new film. Its product claims and depicted integrations were not independently verified. Stylized interface footage does not establish how the underlying app actually works.

The study inspected timestamped frames across the full timeline, 0–10s at 4 samples/s, 12.5–15.5s at 12 samples/s, and 28–34s at 6 samples/s. Source seeks can quantize to nearby frames. These are observations of sampled frames, not a continuous playback or listening review. Audio input was explicitly unsupported in the study environment. FFmpeg measured approximately −18.9 LUFS integrated and +0.7 dBTP; that is a measurement of this copy, not a mastering target or evidence of audible quality.

## What carries the film

| Approximate passage | Visible construction | Transferable principle |
| --- | --- | --- |
| 0–3s | A short outcome phrase changes scale and then resolves into a small explanatory line. | Large scale contrast and brief, stable reading moments can create energy with little on screen. |
| 3–7s | A dark pill arrives. The camera approaches its right edge; a pointer pulls a connector into a second pill. | Establish an object, approach the part that matters, act, and return to context. Keep the object alive through the move. |
| 7–11s | Several source icons connect to one mark. Small colored pulses travel along the paths. A chosen icon becomes the route into the UI. | Abstract motion should explain a relationship and supply the next shot's entry point. |
| 11–19s | A clean input screen becomes a tight prompt view. A fast lateral camera move finds the send button; the click resolves into a response. | Separate typing, travel, click, and result. The target gets a clean hold after the camera lands. |
| 19–28s | Progress bars become action labels. A second request produces a report and downloadable document. | Alternate process and useful output. The result, rather than perpetual activity, pays off the action. |
| 28–33s | A document icon leaves its row, travels into an app icon, and resolves into a notification. | Carry one recognizable object across contexts. Match position, scale, direction, and cursor relationship at each handoff. |
| 33–41.84s | Large words bridge to black. A glowing rounded CTA settles while restrained colored light remains behind it. | Change contrast to mark the ending. Let the CTA resolve and remain legible. |

The important elements are ordinary 2D geometry, type, UI layers, and compositing. No observed shot establishes a need for generative video, photorealistic 3D, or After Effects itself. The ability to reproduce the visible mechanics is separate from matching the director's timing and sound choices.

## Implement the difficult parts

**A camera and its cursor share coordinates.** Put the capture, its crop geometry, and the pointer tip in one source coordinate system. Apply one camera transform to all three, or use `worldToScreen` for an overlay pointer. Record whether geometry uses CSS pixels or physical screenshot pixels; a DPR 2 screenshot has twice the coordinate values. Fit a source rectangle to the output, then interpolate the camera between a contextual view and the target. Avoid separately guessed cursor coordinates for each zoom.

**Travel and reading are different phases.** In the 12.5–15.5s study, typing receives a hold, the lateral move is brief, and the send target becomes sharp before the click. Use timing expressed in seconds, then derive frames at the composition's actual rate. The reference is 25 fps; do not transplant its frame numbers into a 30 fps film. Tune the velocity curve with adjacent frames. Copy the relationship between travel and rest, not an arbitrary duration from this example.

**Blur represents exposure along a path.** A large Gaussian blur on an entire screenshot smears stationary text in every direction. Sampled exposure averages the moving image at fractional times along its actual trajectory. The kit's `Shutter` takes a function of fractional seconds so the camera and child motion can both be resampled. Passing already computed integer-frame positions produces duplicated stills instead of motion blur. Limit expensive sampling to moving intervals; holds remain sharp. Inspect colored edges and alpha over both light and dark backgrounds. Remotion's separate [CameraMotionBlur component](https://www.remotion.dev/docs/motion-blur/camera-motion-blur) warns about color damage and render cost; a larger sample count is not automatically better.

**A shared object crosses the edit.** Describe the outgoing object's rectangle, radius, image crop, and parent transform. Map that rectangle into the next scene before changing its size or meaning. Prefer one persistent layer during a handoff; otherwise make the two layers coincide at the exchange frame. Do not cover a position jump with a flash. A captured result card can become a framing device without reauthoring the result inside it.

**Depth comes from a few consistent cues.** The reference combines a fine edge, a tight contact shadow, a broad soft shadow, and selective light behind an object. Match lighting direction across the sequence. Use a restrained highlight on a dark surface; do not put a glowing outline on every item. Most of the demonstration remains nearly frontal so text stays useful. These cues are available in SVG/CSS; they do not by themselves require a 3D renderer.

**Use contrast as punctuation.** Keep the ordinary proof frames quiet. Reserve the largest type, fastest travel, and strongest light change for different moments. A screen full of simultaneous motion defeats the reference's hierarchy. At 640px viewing width, decide exactly which text must be readable; enlarge the captured region until that text actually is.

## The short proof before the whole film

Make a connected passage with contextual UI → target approach → click → captured result → sharp hold. Inspect it alongside the camera study at the same display width. Verify the pointer tip at approach, click, and result; inspect the peak-velocity frame and first settled frame. Then test a result-object-to-outro handoff. If these passages still feel like moving screenshots, revise composition and continuity before adding scenes.

For sound, choose an appropriate cleared cue and build a timed cue sheet. A generated tone, a transcript, an onset chart, or a loudness report cannot establish musical fit. Retain a separate listening conclusion. See [sound and budget](sound-and-budget.md) for resource and authorization decisions.
