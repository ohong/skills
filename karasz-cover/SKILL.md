---
name: karasz-cover
description: Create artistic illustrated covers for projects or ideas with imagegen, using the supplied Ilonka Karasz cover references. Use for /karasz-cover or requests for this decorative editorial style; ordinary image generation does not need this skill.
---

# Karasz Cover

Create an original cover that gives a specific project or idea a memorable visual world.
Use Ilonka Karasz's supplied magazine covers as visual references for composition, pattern, color, and storytelling.
Translate the project's meaning into the scene; decorative resemblance alone is insufficient.

## Workflow

1. Establish the subject from the user's brief and relevant project context. Identify its purpose, distinctive activity, and emotional tone.
   Ask only when the project or idea itself is missing. Infer routine creative choices from context.
2. Establish the destination and format. Use the requested dimensions or the consuming layout; otherwise choose a portrait cover near 2:3.
   Include only requested cover text. With no text request, create artwork without lettering, leaving room only when the destination needs it.
3. Read [the reference atlas](references/atlas.md). Compare at least two composition approaches against the subject.
   Choose the stronger approach and explain the visual idea briefly. Generate one finished cover unless the user requests variants.
4. Inspect the most relevant one to three reference PNGs with `view_image`.
   Label them as style/composition references, not edit targets. Pass their actual files to imagegen using its supported reference mechanism.
5. Load the installed `$imagegen` skill and follow its workflow.
   Read [model and quality selection](references/model-quality.md) before generation; use the latest available flagship GPT Image model at its highest quality.
6. Write a concise imagegen spec using the structure below. Prepare the complete brief before resolving any unavailable execution controls.
7. Generate with imagegen after the model and quality requirement is resolved. Inspect the result at full size and thumbnail size.
   Check subject meaning, composition, pattern, texture, crop, and any exact text. Correct a material defect with a focused iteration.
8. Save the final cover in the requested destination or project workspace, following imagegen's non-destructive save rules.
   Show the image inline. Report its saved path, final prompt, generation route, and verified model/quality or any accepted limitation.

## Art direction

- Build a coherent scene around one visual metaphor grounded in the subject. Supporting details should reward a closer look.
- Use flattened perspective, irregular hand-drawn shapes, layered gouache-like color, fine decorative marks, and visible paper texture.
- Balance dense detail with clear masses and quiet areas. Keep the main idea readable as a small cover.
- Choose colors for the concept: muted botanical tones, bright folk colors, and dark orchard colors are distinct reference directions.
- Adapt the visual language to contemporary subjects. Farms, animals, plants, and period clothing are options, not required motifs.
- Produce new artwork. Exclude the references' magazine masthead, dates, prices, and artist signatures unless the user explicitly requests them.

## Prompt scaffold

Use imagegen's `illustration-story` taxonomy for narrative scenes, or `stylized-concept` for primarily decorative concepts.
Replace the fields with a concrete scene; do not send the placeholders to the generator.

```text
Use case: illustration-story
Asset type: illustrated cover for <project or idea>; <format and intended use>
Primary request: <one concrete visual metaphor that communicates the subject>
Input images: <numbered references and the composition/texture qualities to borrow>
Scene/backdrop: <setting and visible activity>
Subject: <main action; meaningful supporting details>
Style/medium: decorative editorial illustration informed by Ilonka Karasz; <selected reference qualities>
Composition/framing: <dominant shape, visual rhythm, quiet areas, crop and text space if needed>
Color palette: <concept-specific palette>
Materials/textures: layered matte gouache, fine drawn patterns, tactile paper; purposeful handmade irregularity
Text (verbatim): <exact requested text and placement, or no lettering>
Constraints: original scene; <subject requirements>; no unrequested masthead, date, price, signature, or watermark
```
