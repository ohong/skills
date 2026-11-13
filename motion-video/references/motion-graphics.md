# Motion graphics

Read when a beat is marked `source: motion`: diagrams, equations, charts, kinetic type, UI recreations, title cards, and end cards. Motion graphics are code, so they are exact, cheap to change, and never drift off-model, which makes them the right choice for anything that must be correct (a formula, a number, a product name, a map). Render each scene to its own MP4 at the project size and frame rate, and bring it into the edit as a `motion` shot in `shots.json`.

## Pick the tool by what the scene is

| Scene | Tool | Why |
| --- | --- | --- |
| Math, geometry, physics, graphs, algorithm steps | Manim | It animates mathematical objects directly (equations transform term by term, graphs plot themselves), which is the 3Blue1Brown look. |
| Web-grounded scenes: kinetic type, UI mockups, layouts built from HTML and CSS, GSAP timelines | HyperFrames | Plain HTML and CSS with a deterministic headless renderer, so anything a browser can draw becomes video. |
| Product-film motion with the existing kit, React components, or a scene that needs the motion kit's camera and exposure primitives | Remotion | The house default for product films; see [product films](product-film.md) and `assets/motion-kit`. |
| Vector animation authored as a timeline of generator functions | Motion Canvas | Good authoring model, but it has no official headless render command, so use it only when the user asks for it or already has a Motion Canvas project. |

Don't mix tools within one scene, and keep type, color, and easing the same across tools so the film reads as one piece. Put shared tokens (font files, hex colors, easing curves, safe-area margins) in `motion/tokens.json` and have each scene read them.

## Manim

Manim isn't installed globally; run it through uv so nothing is added to the system:

```sh
uv run --with manim manim -qh --format mp4 -r 1920,1080 --fps 30 -o S04.mp4 motion/s04_resonance.py Resonance
```

`-ql` renders a fast low-quality draft; use it while iterating and `-qh` (or `-qk` for 4k) for the final. Manim needs a LaTeX install only for `Tex` and `MathTex`; if `latex` isn't on the PATH, use `Text` or `MarkupText` and say so in `review.md`. Set the background and colors from the tokens rather than Manim's default black and blue. Time each animation's `run_time` against the beat's narration in `vo/timing.json`, so a transform lands on the word that names it.

## HyperFrames

HyperFrames renders an HTML composition to video in headless Chrome. Setup, the isolated runtime, and the wrapper script are in [HyperFrames](hyperframes.md). The render command is:

```sh
npx hyperframes render -o motion/S02.mp4 -f 30 -q high --resolution 1080p
```

Author each scene as one HTML file with a paused GSAP timeline that the renderer seeks frame by frame. Never use CSS transitions or `setTimeout` for timing, because they run on wall-clock time and render inconsistently. Size the stage to the project aspect ratio and keep text inside the title-safe area. HyperFrames also has `transcribe` and `tts` commands; ignore them here, because narration comes from [voice](voice.md) and captions from [captions](captions.md).

## Remotion

Use the existing motion kit in `assets/motion-kit` (camera, exposure, primitives, timing) as [product films](product-film.md) describes, and render one composition per scene with `npx remotion render`. Remotion can also be the whole film when the piece is almost all motion graphics; in that case render it once and skip OTIO assembly.

## Checking a scene

Before rendering the final, grab frames at the start, middle, and end of each scene and check that every label is spelled correctly, every number matches its source, text is readable at the delivery size (on a phone for 9:16), and nothing moves so fast it can't be read. A motion-graphics scene that is wrong is worse than no scene, because viewers trust diagrams more than footage.
