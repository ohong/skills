# Product films

Read when the subject is a software product. These rules add to the main pipeline: the captured product UI is the proof, and generated imagery can frame it but never replace it.

When the intake leaves them open, default to 1920×1080, 16:9, 30 fps, 10/20/30-second cuts, music and purposeful sound design, and no voiceover unless it helps this brief. These are production defaults, not aesthetic restrictions. Explicit duration/format/silent/voiceover requests override them. Additional aspect ratios require a composed reframe. The short cuts are not sped-up or abruptly truncated copies of the long one.

Making a video includes rendering and inspecting the deliverables. Continue through finished exports unless the user requests concept-only work. A helper skill's preview-only default must not strand this workflow at a Studio preview.

## Learn the product and the references

Read the local `AGENTS.md`, README, relevant specs, product copy, design tokens, and the code for the demonstrated flow. Inspect the supplied URL in a browser. Understand the target user, their desired outcome, the product's distinct mechanism, the best visible proof, and the desired next action. Separate deployed behavior, source-only features, and planned features. Use source paths and captured observations to ground claims.

Before locking the storyboard, rehearse and capture one useful workflow: input or starting state → decisive action → actual result. Save the source footage or sequential screenshots in `captures/`. Use the deployed app when available; a running local build or supplied capture is also valid when its version and status are recorded. Inspecting the app for inspiration is not enough: these captures must appear in the exports. If access prevents capture, prepare independent creative work and request the missing access or footage. Do not silently replace the demo with imagined UI.

Read [the reference atlas](reference-atlas.md). Resolve its files relative to this skill directory, not the current product repo. The installed skill includes the 12 original films plus the CrowdReply study, visual sheets, and a source manifest. Project-specific references or new user instructions take precedence. Use the bundled process studies when unfamiliar with the workflow, then inspect the two or three examples most relevant to the brief. For sparse UI films with fast camera moves and object transformations, read [the CrowdReply breakdown](crowdreply-craft.md).

Review the actual footage, not just its filename or this atlas. Use native video understanding/playback if available; otherwise use timestamped frames across the complete timeline, denser transition sequences, and speech transcription. Record the method and gaps. Sampled frames are not continuous playback; a transcript is not a sound-mix review. See [production](production.md) for inspection helpers. If local tools cannot perceive video and sound together, [perceptual review](perceptual-review.md) provides an optional Gemini adapter with a local preview and explicit upload/spending controls. An external model's opinion is additional evidence, not a quality certificate.

The bundled frame sheets and labeled narration studies are reusable evidence. Inspect them before repeating extraction or transcription; generate additional samples only for missing coverage, finer transitions, or full-resolution detail. Preserve their stated limits.

Write a compact `brief.md` in the output project: viewer, one-sentence promise, proof, CTA, brand facts, source evidence, constraints, assumptions, and reference moments worth learning from. Use a demo account or safe sample data for capture. Do not fabricate testimonials, benchmark numbers, integrations, or live behavior to make the film more impressive.

## Find the film before building it

Read [directing and craft](directing.md). Consider at least two genuinely different treatments: different ideas, visual metaphors, or editorial rhythms, rather than color swaps. Choose one and briefly explain its fit and trade-off. Keep this lightweight; the user has hired you to make decisions.

Use the preferred reference's rough story spine:

**Dream outcome → Solution → Demo → Outro.**

Lead with what becomes possible. Introduce the product as the means. Give most of the film to proof. Close by resolving the opening promise and making the next step clear. This is a flexible structure, not a compulsory pain-agitation script or four title cards. The demo may begin in the opening shot.

Plan all three edits before animating. For each shot, specify its time range, viewer takeaway, product state and evidence status (observed, documented, or conceptual), composition, motion into/within/out of the shot, and sound cue. For each product-proof shot, also name the capture file and source time range or screenshot sequence. Use the following only as a starting allocation:

| Cut | Dream outcome | Solution | Demo / visible proof | Outro |
| --- | --- | --- | --- | --- |
| 10s | 0–1.5s | 1.5–2.5s | 2.5–8s | 8–10s |
| 20s | 0–2s | 2–4s | 4–17.5s | 17.5–20s |
| 30s | 0–3s | 3–5s | 5–27s | 27–30s |

Create visual style frames for the opening, a difficult product-proof shot, and the close before bulk animation. Build the proof frame around an actual capture. A storyboard is a sequence of designed frames with timing and transitions, not merely a prose shot list. Inspect it at final aspect ratio and a realistic small viewing size. Check the most enlarged settled UI crop at native export resolution; resolve insufficient source pixels before committing to the camera plan. Improve the frames until the hierarchy, readability, and identity work. Show the chosen direction as useful progress, then continue unless the user requested an approval checkpoint.

Render the hardest connected passage early, usually a few seconds containing a camera move, decisive action, and settled result. Compare it with the chosen reference at equal display size. Resolve flat staging, drifting cursors, muddy blur, clipped masks, or unreadable holds before multiplying scenes. Define transitions with an outgoing object, its incoming counterpart, shared coordinates, and the moment ownership changes. A list of unrelated entrance animations is not a transition plan.

## Build with a coherent motion language

Read [production](production.md) and [sound and budget](sound-and-budget.md). Use the simplest capable medium. Remotion is the preferred editable compositor for UI, typography, vector animation, footage, and synchronized sound; native After Effects is an option only if actually available and useful. Canvas/SVG/WebGL, Blender renders, image tools, or generated footage can serve a specific shot. Do not limit the film to a screen recording because it is easy to capture, or add 3D because the tool exists.

For Remotion, the bundled [motion kit](../assets/motion-kit/README.md) supplies timing, shared camera coordinates, sampled motion blur, persistent containers, masked type, and path animation. Copy only useful primitives, or use `scripts/scaffold_motion.py` for an isolated starting project. Its diagnostics composition demonstrates mechanics; replace it with a film-specific design. The kit supplies no product, story, soundtrack, or proof footage.

For plain HTML, CSS, and GSAP scenes, [HyperFrames](hyperframes.md) is a tested local alternative. Choose by authoring fit and apply the same capture, craft, sound, and review requirements; renderer choice alone does not establish reference quality.

Compose around genuine product captures. Use crops, zooms, masks, camera moves, cursor emphasis, and editorial callouts to make the real interface clear. Faithful editable reconstructions may supplement a detail or transition; they must not replace the captured action-to-result proof. Preserve the product's controls, layout relationships, and output. Keep editorial copy visually separate from UI text. Record capture vs. reconstruction and any compressed wait times in the production notes. See [production](production.md) for capture and fidelity rules.

Design a small motion vocabulary for this film: object behavior, easing, camera/framing, type reveals, transitions, and sonic texture. Use each movement to direct attention or explain change. Carry an object, shape, alignment, color, or direction through important transitions. Let the viewer read the result after the motion lands.

Keep output in a dedicated local video project such as `teaser-video/motion-video/<product>-<date>/`, preserving existing work. Keep source, captures, audio, project/lock files, and review evidence reproducible. Do not change the product merely to stage a better demo unless that change is separately in scope.

## Direct the final pass

Render rough cuts early. Review both individual frames and the complete temporal sequence. Check each edit independently, sound off first for comprehension, then sound on when listening is available. Compare against the selected reference moments at a comparable display size. Identify the weakest shot and revise the cause: story, composition, proof, transition, or sound. More animation is not a universal fix.

Do not call the films finished until:

- A first-time viewer can identify the product's value and follow its decisive action-to-result sequence without pausing.
- Every cut contains actual product UI as its main demo/proof material, with a readable action and result. A brief screenshot flash or tiny background interface does not count.
- The demonstrated controls and results match the source captures. The capture ledger maps exported proof shots to their source files and identifies any supplemental reconstruction.
- The opening earns attention, the middle proves the promise, and the close remains long enough to read.
- Typography, UI, framing, and motion are deliberate and consistent with the product; a logo swap would not make the film fit an unrelated app.
- Every cut and transition has been inspected, including first/last frames and any fast motion, masked text, or camera move.
- Fast motion follows deliberate paths and settles sharply; cursor tips stay on their intended controls through camera transforms. Shared-object transitions preserve position and apparent scale at the handoff. Inspect adjacent frames for these properties.
- All three files decode, have the intended dimensions/frame rate/duration, contain the expected audio, and have no unintended gaps, truncated tails, missing assets, or clipping.
- Sound has been listened to if the environment supports it. If it does not, perform the available technical checks and clearly label the listening review incomplete; do not claim a fully reviewed mix.

Use the concrete review prompts and failure examples in [directing](directing.md), and the verification helper in [production](production.md). Technical checks cannot certify taste. When the output misses the references, revise it rather than hiding behind a self-assigned quality score.

For feedback such as “change the blue card at 6s” or “make the result easier to read,” locate the exact shot/object, preserve successful surrounding work, and update every cut that shares the changed asset. Rerender and inspect the affected transitions plus the final exports. Keep stable scene names and useful timecodes so natural-language revision stays precise.
