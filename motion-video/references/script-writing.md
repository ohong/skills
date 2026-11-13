# Script and plan

Read before writing any narration, on-screen copy, or shot plan. The script is the spine of the film: every later stage (voice, keyframes, footage search, music cues, captions, critic) reads from the files this step produces, so write them to be parsed as well as read.

## Outputs

Write these into the project folder before generating any paid media:

- `brief.md`: the four intake answers (what, aspect ratio, length, style), viewer, the one sentence the viewer should remember, sources and claims that need evidence, and any budget cap.
- `script.md`: narration in beats, one beat per shot or group of shots, using the format below.
- `shots.json`: the machine-readable shot list that generation, assembly, and the critic consume.

## Beat format

```markdown
## B03 · 0:14–0:22 · "Why the bridge didn't fall"
VO [calm, curious, slightly slower; lean on "resonance"]:
The wind didn't push the bridge over. It pushed at just the right rhythm, and the deck began to answer it, a little more with every gust, until the motion that started as a shiver became a wave you could see from the shore.
ON SCREEN: archival clip of the Tacoma Narrows deck twisting (CC, see footage ledger)
MUSIC: bed drops to low strings; hold under VO
SFX: low wind, single metallic groan at 0:19
```

The bracketed direction after `VO` is the performance note that `scripts/tts.py` passes to the voice model (see [voice](voice.md)). Keep it to tone, pace, and one or two words to stress. Beat IDs (`B03`) are stable names: shots, assets, and review notes refer to them, so don't renumber after generation starts.

## shots.json

One entry per shot. Durations come from the narration estimate first (about 150 spoken words per minute for a measured delivery) and are corrected later from the real TTS timing.

```json
{
  "fps": 30, "width": 1920, "height": 1080,
  "shots": [
    {"id": "S07", "beat": "B03", "start": 14.0, "duration": 4.0,
     "source": "clip", "path": "footage/tacoma-1940.mp4", "in": 12.5,
     "prompt": null, "refs": [], "notes": "hold on the twist, no zoom"},
    {"id": "S08", "beat": "B03", "start": 18.0, "duration": 4.0,
     "source": "generate", "model": "seedance", "keyframe": "keyframes/S08.png",
     "prompt": "slow dolly along a suspension bridge deck, cables vibrating ...",
     "refs": ["refs/bridge-sheet.png"]}
  ]
}
```

`source` is one of `capture` (product UI), `generate` (image or video model), `motion` (Manim, HyperFrames, Motion Canvas, or Remotion render), `clip` (real footage from yt-dlp), or `still`. The assembler reads `path` and `in`; the generator reads `prompt`, `keyframe`, `refs`, and `model`.

## Plan the film before the words

Start from the viewer and the single idea they should leave with, then decide the shape. For a product film the spine is dream outcome, solution, demo, outro (see [directing](directing.md)). For an explainer it is usually a question the viewer already has, the intuition that answers it, the evidence that makes the intuition believable, and a return to the question with the answer in hand. For a narrative or mood piece it is a situation, a change, and a consequence. Pick one and write it as three or four sentences in `brief.md` before any beat exists.

Then allocate time. Narration sets the floor on length: a 60-second film holds about 130 to 150 spoken words, and it's better to use fewer, because images need room to land. Leave at least one beat with no narration so music and picture carry it.

## Voice of the narration

Narrate like a university professor giving a lecture they care about: someone who knows the material well, explains the mechanism behind each claim, links ideas with "so", "because", and "which means", and trusts the listener to follow a full sentence. The register is warm and exact, never salesy.

Avoid the patterns that make machine-written narration sound machine-written:

- Don't write strings of short punchy fragments ("Fast. Simple. Powerful.") or one-line dramatic sentences. Let sentences run with clauses that carry the reasoning, and vary their length the way speech does.
- Don't lean on numbers. One well-chosen figure that the viewer can picture is worth more than five statistics, and a stack of percentages is unreadable when heard. If a number matters, say what it means ("about the weight of a car") rather than reciting precision.
- Don't open with a rhetorical hook such as "What if I told you" or "Imagine a world", and don't use setup phrases such as "here's the thing", "the truth is", or "but here's the kicker". State the idea.
- Don't use "not just X, but Y" or "it's not X, it's Y" constructions. Say what the thing is.
- Don't stack triads of adjectives, and don't end every beat on a quotable line. A beat can end on a plain fact that leads into the next picture.
- Don't describe what the picture already shows ("Here we see a bridge"). Narration adds the why; the image carries the what.

Read the whole script aloud at speaking pace (or run it through TTS once) before generating images. Anything you stumble over, rewrite.

## Check before moving on

- Every factual claim in `script.md` has a source noted in `brief.md` or is marked as the author's framing.
- Every beat has a visual source type decided, and every `clip` beat has a search plan (see [footage](footage.md)).
- Estimated narration time fits the requested length with at least 10 percent slack.
- The user's style preference is visible in concrete choices: palette, type, pacing, music character, and which motion tool renders which shots.
