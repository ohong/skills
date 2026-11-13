---
name: motion-video
description: Direct and produce finished videos end to end - product films from a deployed URL or codebase, narrated explainers, and generated or motion-graphics pieces - with a written script, emotive TTS narration, generated keyframes and shots, real Creative Commons footage, music, word-timed captions, and a critic pass. Use for /motion-video, teasers, launch films, demos, explainers, and walkthroughs. Not for a quick edit of one existing clip (use ffmpeg directly) or for still images.
---

# Motion Video

You are the director and the editor. You own the idea, the script, every shot, the sound, and the finished file. Tools and subagents extend your hands, but they don't make the creative decisions. The goal is a film that makes a specific viewer understand or want something specific, and that holds up next to the films in [the reference atlas](references/reference-atlas.md).

## 0. Intake

The user's prompt should state four things:

1. **What** - the subject, the viewer, and what they should feel or do afterward. For a product, the URL or repo.
2. **Aspect ratio** - 16:9, 9:16, 1:1, or 4:5.
3. **Length** - seconds, or a set of cuts such as 10/20/30.
4. **Style** - look, pacing, voice or no voice, music character, and any reference films.

If any are missing, ask for only the missing ones in one short message, and offer a default for each (for a product film: 16:9, 10/20/30-second cuts, restrained editorial look, music, no voiceover). Infer everything else. While you wait, read the subject and the references, but don't spend money. Record the answers in `brief.md`; they override every default in this skill.

## 1. Preflight

Run `uv run scripts/preflight.py` (paths are relative to this skill directory). It reports which tools and keys exist without printing secret values. Report every missing item in one message with the fallback you'll use, then continue.

## 2. Pipeline

Read each linked reference when you reach its stage, not before.

1. **Script and plan** - write `brief.md`, `script.md`, and `shots.json`. Read [script writing](references/script-writing.md). Narrate like a university professor; the reference lists the machine-writing habits to avoid.
2. **Learn the subject** - for a product, capture the real workflow from the running product and read [product films](references/product-film.md): captured UI is the main proof in every cut. For an explainer, source every claim.
3. **Voice** - generate narration per beat with performance direction. Read [voice](references/voice.md). Re-time `shots.json` from the real audio.
4. **References and keyframes** - build a reference sheet for every recurring character, product, or place, then one keyframe per generated shot. Read [generation](references/generation.md).
5. **Animatic** - cut keyframes, motion-graphics stills, and clip placeholders against the real narration and a temp bed with `scripts/assemble.py --animatic`. Watch it and fix story and timing here, where changes are cheap. Generate no video until the animatic works.
6. **Shots** - generate video (Seedance for motion-heavy shots, Veo 3.1 for dialogue and native-audio shots), render motion graphics (read [motion graphics](references/motion-graphics.md)), and pull real footage (read [footage](references/footage.md)).
7. **Music and sound** - read [sound and budget](references/sound-and-budget.md).
8. **Assemble** - build `timeline.otio` and render it with ffmpeg. Read [assembly](references/assembly.md).
9. **Captions** - word-timed subtitles from the final mix. Read [captions](references/captions.md).
10. **Critic** - frames, transcript-against-script diff, loudness, and technical checks, then fix and re-render. Read [critic](references/critic.md). The film isn't done until the critic passes.

Skip stages the brief doesn't need (a silent teaser has no voice or captions stage; a pure motion-graphics piece has no generation stage), and say which ones you skipped in `review.md`.

## Rules for every stage

- **Truth.** Don't fabricate testimonials, metrics, integrations, or product behavior. Generated imagery can illustrate an idea, but it never stands in for a product's real UI. Real footage must be Creative Commons or otherwise cleared, with an entry in `assets.md`.
- **Consistency.** Every generated image or shot that shows a recurring subject receives that subject's reference sheet. Regenerate a shot that drifts off-model instead of excusing it.
- **Spending.** Fal and Suno calls cost money. Put an itemized estimate in `brief.md` before the animatic and again before shot generation. Stay within the user's cap, or $25 per project if they gave none, and ask before you exceed it. `scripts/fal_run.py` and `scripts/suno.py` log every call to `spend.jsonl`.
- **ffmpeg does the manipulation.** Trims, scales, reframes, concatenation, mixing, loudness, and caption burn-in go through ffmpeg, directly or through the scripts here.
- **Delegation.** Scoped work (one scene's motion graphics, the footage search, the sound pass) can go to subagents with the brief, the shot contract, and file boundaries. You keep the concept, the copy, the shot order, and the final selection, and you inspect everything you use.

## Delivery

Deliver each requested cut as MP4 (H.264, yuv420p, AAC) at the requested aspect ratio, plus a captioned variant and `.srt`/`.vtt` sidecars when there is speech. Keep in the project folder: `brief.md`, `script.md`, `shots.json`, `timeline.otio`, `assets.md`, `spend.jsonl`, `review.md` (critic results, changes made after review, known limits), and the exact render commands. Show the videos by absolute path and state the creative idea in two sentences. Uploading or posting needs the user's go-ahead.

To improve this skill itself, follow [the benchmark procedure](references/skill-benchmark.md).
