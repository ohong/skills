# How these references were studied

Study date: 2026-09-04. Sources: Oscar's 12 local MP4s in the source directory recorded in [library.json](library.json). The skill bundles byte-identical copies so reference access does not depend on the product checkout. No reference footage or soundtrack is cleared here for inclusion in a new deliverable.

## Visual coverage

All 12 films were surveyed from opening to ending using FFmpeg frame extraction and model-visible contact sheets. The `motion-agent` overview samples every two seconds; all other overviews sample every second. Overview pages contain up to 20 labeled frames. A second pass inspected four-frame-per-second sequences in these ranges:

| Clip | Dense range in seconds |
| --- | --- |
| motion-agent | 20–30 |
| use-this-formula | 11–16 |
| use-storyboard | 25–31 |
| quick-teaser | 1.5–5.5 |
| reference-10s | 3.5–8 |
| reference-12s | 1.5–7 |
| reference-15s | 0–6 |
| apple-style | 15–20 |
| reference-37s | 9–14 |
| reference-45s | 19–26 |
| reference-50s | 17–24 |
| reference-1m | 16–22 |

The bundled study contains 29 overview pages and 12 dense sheets. A supplementary endpoint pass adds an opening/final-frame sheet and coverage metadata for each of the 12 films, under `study/<clip>/endpoints/`. These are navigation and analysis aids. The original overview extraction used FFmpeg's `fps` filter and approximate midpoint labels; labels do not retain source presentation timestamps. Seek the original film and inspect neighboring frames before making frame-level timing judgments. The reusable inspection script records requested positions separately from safe seek positions; final-frame targets come from decoded-frame timestamps and the stream time base. Other seeks may quantize to nearby frames.

## Audio and temporal limits

This creation environment did not support direct audio listening or continuous video input. An attempted compressed-audio tool submission explicitly reported that audio input was unsupported. Local speech recognition was used for narrated sections; instrumental sections sometimes produced fabricated repetition, and some narration needed shorter extraction windows. Such output must not be treated as verified speech or as an assessment of musical timing, timbre, or mix quality.

The atlas therefore makes visual observations and editorial inferences; it does not claim a continuous playback review or a listening pass. Audio stream presence and duration are probe facts. The 10-second reference has no audio stream. Future productions should use actual playback/listening when available and state any remaining review limitation.

## Reuse

Start from the atlas to select references, then inspect the relevant originals. Use more densely sampled frames for masks, text reveals, object morphs, or short transitions. Review full-size frames when essential details are unclear in a contact sheet. Do not treat this study's limited sampling as a sufficient final QA protocol for a newly generated film.
