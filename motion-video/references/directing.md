# Directing and craft

Read when choosing a treatment, storyboarding, animating, or reviewing. The reference atlas contains the observed evidence; this guidance translates it into decisions for a new product. It is not a house visual template.

## A concept that belongs to the product

Find the transformation the viewer cares about: scattered material becoming a decision, a rough intention becoming a finished artifact, a complicated action becoming graspable. Choose a visual idea that embodies that particular change. The product itself often supplies the motif: a cursor, cell, route, conversation, selection ring, version branch, or recognizable object.

Write one sentence describing what the audience will remember. Evaluate two treatments against it. A restrained editorial film can make judgment and trust tangible; a fast field-to-detail film can communicate range and discovery; a continuous object transformation can explain a mechanism. These are choices, not required categories. A new product can demand a different language.

Borrow principles from several references without assembling their most obvious effects into a collage. Name what you are taking: the field-to-selection move at 1.8–4.8s in `quick-teaser`, the persistent square vocabulary in `reference-1m`, or the benefit-to-action alternation in `use-this-formula`. Name what is original to this product. Never inherit another brand's logo, copy, metric, or stock footage as if it belongs to the new product.

## Design the argument in pictures

The dream outcome is specific enough to picture. Replace vague claims such as “Work smarter” with a concrete result the product really supports. In a short film, a good demonstration can be the sentence.

Show causality: intention/input → meaningful action → visible change → useful result. Cut navigation, loading, repetitive typing, and settings that do not explain the benefit. Compress waits editorially; do not imply measured speed from an edited demonstration. For AI products, show the actual quality of the output and how the user can use it, not just a blinking “thinking” label.

If an exported artifact is the payoff, let the viewer see the actual artifact or a faithful excerpt from it. A prolonged hold on “Downloaded” confirms a control state but says little about what the user now has. Use the real exported contents and a truthful next context; do not invent a destination or integration to complete the story.

Design this sequence around captured product UI. Let its real controls and results supply the visual argument. Titles, metaphors, and transitions can build desire, while the demo shows what the viewer will actually use. Give the captured workflow most of the proof time in each edit, including the 10-second cut.

The 10s teaser should have a complete micro-argument. The 20s cut adds enough mechanism to believe it. The 30s cut can add context, a second linked benefit, or a payoff that reinterprets the opening. They share assets and motifs but may have different openings, shot orders, and musical endings. Remove ideas before reducing readable dwell time.

Use a shot table in `storyboard.md` with these useful fields:

| Time / frames | Viewer takeaway | Composition and product state | Motion / transition | Sound | Evidence / asset |
| --- | --- | --- | --- | --- | --- |
| A defined interval | One thing to understand | The exact frame and focal point | What carries attention into the next shot | A cue or intentional silence | Capture file and source range/sequence; note overlays or reconstruction |

Avoid filling the table with “zoom in,” “fade,” and “show feature.” Describe why a detail is revealed, what it changes into, and what the viewer sees after it lands. Include start and end states for complex transitions. Make a visual storyboard sheet or browser preview that corresponds to the shot table. Keep typography and layout editable when possible.

A style frame may show a fully built composition that takes several beats to reveal. Mark that build explicitly. For each beat, identify the one essential thing to read and the order in which supporting text or UI appears. A readable still with a headline, subcopy, and detailed result can still overload a two-second opening. Simplify the short cut's composition as well as its shot list.

## Motion craft

- **Hierarchy before velocity.** Give each moment a focal point. Secondary movement can lead toward it or settle behind it; it should not compete for attention.
- **Intentional trajectories.** Plan origin, path, landing, and settling. Acceleration conveys urgency; deceleration reveals importance. Small spring overshoot can feel tactile, while text and serious UI may need a clean, restrained landing. Use adjacent-frame review to tune it.
- **Continuity through change.** Match cuts, masks, shape morphs, object persistence, and aligned camera moves make separate shots feel authored. A product control can expand into the result it creates. A field can resolve into one selected item. A border can become the next framing device.
- **Readable rests.** Separate arrival from reading. Let important copy or a product result stabilize before moving away. Contrast energetic passages with a calm payoff; equal-speed motion throughout feels mechanical.
- **Camera discipline.** Move to a reason. Use wide views to orient, close views to prove, and returns to context when useful. Avoid repeated push-ins on flat screenshots. If perspective obscures the essential action, flatten the camera during the proof.
- **Type as material.** Use masking, line reveals, scale, tracking, or letter choreography only when it suits the words. Choose deliberate line breaks, optical alignment, and a type hierarchy. A typewriter effect earns its place for an actual prompt/input; it need not reveal every headline.
- **Compositing.** Use depth, light, shadows, grain, motion blur, and texture to create a coherent world. Match blur to velocity and keep the legible hold crisp. Effects must survive compression. A good flat composition is preferable to noisy faux-cinematic depth.

Technical values depend on the implementation and frame rate. Do not copy timing constants from an unrelated film and assume they confer taste.

Plan the visible region during the whole camera path, including the middle of the move. A crop that looks clean at both ends can reveal a severed heading or neighboring card in between. If a shot needs one product object, isolate that captured region as a persistent layer before moving it. Give the surrounding interface a deliberate exit, then keep the object's bounds and camera coordinates consistent. A sequence of wider and tighter screenshots is useful for orientation, but the film also needs a visible relationship or transformation within that proof.

## Product and typography fidelity

Use the real logo, type family, colors, and interface grammar as raw material. Feature the actual captured interface. Crop unrelated chrome, isolate a captured panel, and move the camera while preserving the controls and layout relationships that explain the workflow. Keep explanatory graphics distinct from the UI. Reconstructed details may support a transition, but must not carry the entire demo. Conceptual UI belongs in explicitly requested concept work and must be labeled; it cannot substitute for a required product capture.

Essential text should be legible at the intended viewing size. At a 640px-wide preview of a 1920px-wide film, a 24px label becomes 8px. Enlarge the captured panel or add a separate editorial excerpt. Preserve the actual output in the interface. Keep generous safe margins and verify actual line breaks. Small source detail may be texture, but the fact supporting the promise must be readable.

Use a restrained type and color system chosen for the product. Gradients, glass, serif type, monospace, and bright accents are valid when they serve the treatment. None is an automatic marker of quality. Do not default to decorative cards, floating icons, or generic neon effects just because several software videos use them.

## Review that leads to a better film

Inspect the exported file, not only the component or Studio state. Review at delivery resolution and a realistic small size. Inspect every shot and transition; a handful of attractive stills can hide bad pacing. Record timecodes and concrete revisions in `review.md`.

Ask an independent reviewer, when useful, to see the cut before reading the brief. Ask what the product does, which action changed what, what they remember, and where they lost the thread. Their response is evidence about communication, not a vote that replaces the director.

Then compare the exported proof shots against the original captures. Verify that every cut shows recognizable, readable product UI and that the decisive action produces the result shown. Record those timecodes in review.md. An attractive recreation can pass a style review while failing this product-evidence check.

| Failure | Useful response |
| --- | --- |
| “I saw beautiful UI but do not know why I need it.” | Replace a feature montage with one concrete action and useful result. |
| “I understand the pitch, but what does the app actually look like?” | Replace reconstructed demo panels with a sustained captured workflow. Use motion and callouts to direct attention within the real interface. |
| “I could not read the result.” | Simplify the frame, enlarge the evidence, reduce copy, or lengthen its hold. |
| “Every scene feels like a different template.” | Unify type, material, motion behavior, and transition logic around the chosen idea. |
| “The short version feels rushed.” | Rebuild its argument with fewer shots; preserve a complete ending. |
| “It feels like slides with transitions.” | Animate the relationship or transformation inside the product proof. |
| “The sound calls attention to itself.” | Remove redundant cues, lower/soften transients, and use a coherent palette. |
| “It looks polished but could advertise anything.” | Replace the generic hook and imagery with the product's distinctive mechanism. |

Maintain three separate conclusions: product truth, technical export validity, and creative/temporal review. A passing encode does not prove the story works. A beautiful storyboard does not prove the finished animation works. A silent review does not prove the sound mix works.
