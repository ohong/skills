# Voice

Read when the film has narration. The voice is Gemini 3.8 Flash TTS, called through Fal (`google/gemini-3.8-flash-tts`, about $0.045 per 1,000 characters) or directly with `GEMINI_API_KEY` if Fal is down. The model takes delivery direction in plain language, so the performance is written, not left to chance.

## Direct each beat

Every VO line in `script.md` carries a bracketed direction, and the direction is what turns a flat read into a performance:

```
## B03 · 0:14–0:22 · "Why the bridge moved"
VO [unhurried, curious, a slight smile on "gentle wind"; let the last clause land]:
The strange part is that it wasn't a storm that brought it down, <short pause> it was a gentle wind that happened to match the way the deck wanted to twist.
```

Write directions the way a director talks to an actor. Name the emotion, the pace, the energy, and where the emphasis falls ("warm and confident, slower on the product name", "quietly amazed, as if seeing it for the first time"). Avoid adjectives that fight each other, and don't ask for an accent or character the brief didn't choose. Keep one global voice note in `brief.md` (for example "a university professor explaining something they love to a curious first-year student, warm, measured, never salesy"), and `tts.py` prepends it to every beat's direction so the voice stays one person across the film.

Inline tags go inside the narration text where they should happen: `<breath>`, `<short pause>`, `<long pause>`, `<sigh>`, `<laugh>`. Use them sparingly, one or two per beat at most, because a tag on every line sounds staged. Punctuation also steers delivery: a comma gives a small breath, a full stop a real one, and an em dash a hesitation.

## Generate

```sh
uv run scripts/tts.py script.md --out vo/ --voice Kore
uv run scripts/tts.py script.md --out vo/ --beats B03 --force   # redo one beat
```

It writes `vo/B03.wav` for each beat and `vo/timing.json` with the real duration of each file. Re-time `shots.json` from `timing.json` before the animatic; the narration sets the pace of the edit, not the other way round.

Pick the voice once, early. Generate the same two beats with three or four candidate voices (Kore, Charon, Puck, and Aoede are good starting points; the endpoint lists 30), listen, and record the choice and why in `brief.md`. Use `--model google/gemini-3.8-flash-lite-tts` for voice auditions and scratch reads, and the full model for the final.

## Listen before you move on

Listen to every beat. Regenerate a beat when a word is mispronounced, the emphasis is on the wrong word, the energy doesn't match its neighbors, or the model added or dropped words. For a name the model keeps getting wrong, spell it phonetically in the text ("Tacoma" → "tah-KOH-mah") and note it in `script.md` so captions still use the real spelling. Two or three takes per beat is normal; if a beat needs more, rewrite the line, since it's usually the sentence that is hard to say.

Two-speaker dialogue (an interviewer and an expert, for example) uses the endpoint's `speakers` and `turns` inputs through `scripts/fal_run.py` directly; check the endpoint's schema first.
