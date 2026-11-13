# Captions

Read when the film has speech. Captions come from the final mix, not from the script, because the voice model sometimes drops or changes words and the captions must match what's actually said. Comparing the two is the critic's job.

## Transcribe with word timing

`scripts/captions.py` runs ASR with word-level timestamps and writes `captions/words.json`, `captions/<cut>.srt`, `captions/<cut>.vtt`, and an `.ass` file styled for burn-in:

```sh
uv run scripts/captions.py renders/explainer-60s.mp4 --backend fal --script script.md --style lower --max-chars 32
```

Backends, in order of preference:

- `fal` - ElevenLabs Scribe v2 on Fal (`fal-ai/elevenlabs/speech-to-text/scribe-v2`), which returns word-level timestamps and is accurate on names and technical terms (uses `FAL_KEY`, costs cents per minute).
- `local` - the `whisper` CLI with `--word_timestamps True`, free and offline but slower.

`--script` passes distinctive words from the script (names, product terms) to the ASR as key terms, so they come out spelled correctly. It does not replace the transcript.

## Readable subtitles

Group words into cues of one or two lines, at most about 32 characters per line for 9:16 and 42 for 16:9, and between 1 and 6 seconds per cue. Break at clause boundaries rather than mid-phrase. The script handles grouping; check the result in the `.srt` before burning in.

Styles: `lower` is a classic lower-third subtitle; `word` highlights each word as it's spoken (karaoke-style `\k` timing in ASS), which suits vertical social cuts. Keep captions inside the title-safe area and clear of any on-screen text or UI proof, and match the film's typeface when it's legible at small sizes.

## Burn in

Burn-in needs an ffmpeg built with libass (`scripts/preflight.py` checks this). Without it, deliver the clean render with `.srt` and `.vtt` sidecars and say so in `review.md`.

```sh
ffmpeg -i renders/explainer-60s.mp4 -vf "ass=captions/explainer-60s.ass" -c:a copy renders/explainer-60s-captioned.mp4
```

Always keep the clean render and the sidecars, since platforms that accept `.srt` or `.vtt` look better with their own caption rendering.
