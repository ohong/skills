# Assembly

Read when the shots, narration, and music exist and it's time to cut the film. The timeline lives in OpenTimelineIO (OTIO), an open interchange format for editorial timelines, so the edit is a readable file you can diff, re-render, and open in DaVinci Resolve or Premiere if a human editor wants to take over. ffmpeg does the actual rendering.

## Build the timeline

`scripts/assemble.py` reads `shots.json` and the audio files and writes `timeline.otio` with one video track and three audio tracks (voice, music, effects):

```sh
uv run scripts/assemble.py build shots.json \
  --voice vo/ --music music/bed.wav --sfx sfx/cues.json --out timeline.otio
```

Each shot becomes a clip whose media reference points at its file and whose source range comes from `in` and `duration`. Voice clips are placed at the start time of their beat, taken from the TTS timing manifest. Transitions in `shots.json` (`"transition": {"type": "dissolve", "duration": 0.5}`) become OTIO transitions. A transition belongs to the shot it leads into and is centered on that shot's `start`, so cuts never move and the voice stays in sync; give each clip about half the transition length as handle on both sides, or the renderer holds its first or last frame. Because everything is in one file, retiming a beat means editing `shots.json` and rebuilding, never hand-editing an ffmpeg command.

## Render

```sh
uv run scripts/assemble.py render timeline.otio \
  --width 1920 --height 1080 --fps 30 --out renders/explainer-60s.mp4
```

The renderer walks the OTIO timeline and emits one ffmpeg command. It conforms every clip to the output frame rate and size (scale to cover, then crop, unless the shot sets `"fit": "contain"` or `"fit": "blurfill"`), applies transitions with `xfade`, lays the audio tracks with `adelay` and `amix`, ducks music under voice with `sidechaincompress`, and normalizes the final mix to about -14 LUFS with `loudnorm`. It writes the exact ffmpeg command it ran to `render.md`, so the render is reproducible without the script.

For the animatic, pass `--animatic`: still keyframes are held for their shot duration, missing shots render as a labeled slate showing the shot ID and prompt, and the output is 720p for speed. Slate text needs an ffmpeg built with `drawtext`; without it the slates are blank cards and the script prints each slate's ID and prompt instead.

## When to use something else

A Remotion or HyperFrames project can be the whole film when it's mostly motion graphics; render it there and bring the result in as a single clip, or skip OTIO entirely. OTIO earns its place when the film mixes many sources (generated shots, real footage, captures, motion-graphics renders) and gets re-cut several times.

Aspect-ratio variants are separate edits, not crops of the master. Build a second `shots.json` (or a `framing` override per shot) for 9:16 and render a second timeline, so text and subjects stay composed for the new frame.
