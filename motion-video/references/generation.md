# Generation

Read when a beat is marked `source: generate`. All image, video, and music generation goes through Fal with one key (`FAL_KEY`) via `scripts/fal_run.py`, which uploads local files, waits on the queue, downloads the results, and logs the estimated cost to `spend.jsonl`:

```sh
uv run scripts/fal_run.py <endpoint-id> --input job.json --out gen/S08 --label S08 --cap-usd 25
```

Any input value that starts with `@` is treated as a local file and uploaded first, so `"image_urls": ["@refs/host-sheet.png"]` works. Check an endpoint's exact inputs at `https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=<endpoint-id>` before the first call, since models change their schemas. Prices are in [prices.json](prices.json); confirm them on the model page before a large batch.

The order is fixed: reference sheets, then keyframes, then the animatic, then video. Each step is cheap compared with the next, and each one catches problems the next would pay for.

## 1. Reference sheets

Every recurring subject (a person, a product, a mascot, a place) gets a reference sheet before any shot shows it. Generate it with GPT Image 2.5 Sunburst:

- `openai/gpt-image-2.5/sunburst/text-to-image` for a new subject.
- `openai/gpt-image-2.5/sunburst/edit` with `image_urls` (up to 16) when you have real photos, a logo, or product renders to start from.

A useful sheet is one image with the subject from the front, three-quarter, and side, a neutral background, even light, and a label strip with the name and key colors. Save it to `refs/<subject>-sheet.png` and describe it in one sentence in `shots.json` notes, so every prompt can use the same words for the subject. Use `quality: "high"` and `image_size` matching the project aspect ratio (multiples of 16, up to 3840 on a side). Check the sheet carefully; every later shot inherits its mistakes.

## 2. Keyframes

Generate one keyframe per generated shot with the `edit` endpoint, passing the relevant reference sheets in `image_urls` and a prompt that describes the frame as a cinematographer would: subject and action, framing and lens ("35mm, waist-up, eye level"), light, palette, and what is in the background. Name each reference in the prompt ("the woman from the first image, the lamp from the second"). Generate two to four variants for important shots with `quality: "medium"`, pick one, and re-run the winner at `high`. Save it as the shot's `keyframe` in `shots.json`.

Keyframes are also the style check. If three keyframes don't look like one film, fix the style words and the references now, before anything moves.

## 3. Animatic

Cut the keyframes, motion-graphics stills, and clip placeholders against the real narration and a temp music bed:

```sh
uv run scripts/assemble.py build shots.json --voice vo/ --music music/temp.wav --out timeline.otio --animatic
uv run scripts/assemble.py render timeline.otio --width 1920 --height 1080 --fps 30 --out renders/animatic-01.mp4 --animatic
```

Watch it with sound. The animatic answers whether the story works, whether each beat is long enough, and which shots are unnecessary. Cut shots here; a shot removed from the animatic costs nothing, and the same shot removed after generation costs its full price. Show the animatic to the user when the brief allows a review round.

## 4. Video

Choose the model per shot, and record the choice in `shots.json`:

| Shot type | Model | Why |
| --- | --- | --- |
| Motion-heavy: camera moves, action, dance, vehicles, water, crowds, anything that should feel physical | Seedance 2.5 (`bytedance/seedance-2.5/image-to-video`, or `/reference-to-video` with many refs) | It handles large, fast motion and camera movement more convincingly. Durations 4 to 30 s, up to 720p, many aspect ratios. |
| People speaking on camera, lip sync, shots that need native sound (ambience, foley) | Veo 3.1 (`fal-ai/veo3.1/image-to-video`, `/reference-to-video`, or `/first-last-frame-to-video`) | Better faces, speech, and generated audio. Durations 4, 6, or 8 s, up to 1080p or 4k, 16:9 or 9:16 only. |
| Calm, slow shots where either works | Veo 3.1 Fast or Seedance at 480p for drafts | Cheaper; decide after seeing a draft. |

Always start from the approved keyframe (image-to-video) so the shot matches the animatic, and pass the reference sheets when the endpoint takes them. Use first-and-last-frame mode when a shot must end on a specific frame, such as a hand-off into the next shot or a match cut.

Write the video prompt about motion, not appearance, because the keyframe already fixes the look. Describe what moves, how the camera moves ("slow push-in", "handheld follow at walking pace", "locked-off"), the speed, and how the shot ends. One action per shot; a prompt with three events produces a shot where none of them lands. For Veo, put spoken lines in quotes and describe the sound you want; set `generate_audio: false` when the shot will sit under narration, which also halves the price.

Generate at the shortest duration that covers the shot plus about half a second of handle on each end. Draft motion-heavy shots at 480p when the brief is uncertain, then re-run approved shots at full resolution. Keep every take in `gen/<shot>/` and record the chosen one in `shots.json`.

## Checking a shot

Open frames from the start, middle, and end of every take (`scripts/inspect_video.py` makes a contact sheet). Reject a take when the subject drifts off its reference sheet, hands or text warp, physics looks wrong, the camera does something the prompt didn't ask for, or it doesn't cut with its neighbors in the animatic. Change one thing per retry (the prompt's motion description, the seed, the model) so you learn what fixed it. After three failed takes, change the shot instead: a different angle, a shorter action, a still with a slow push-in, or a motion-graphics treatment.

## Music on Fal

When `SUNO_API_KEY` is missing, generate the music bed with `fal-ai/elevenlabs/music` (`prompt`, `music_length_ms`, `force_instrumental: true`). Fal lists that endpoint as deprecated from 2026-12-17, so check for its replacement when the call fails. See [sound and budget](sound-and-budget.md) for how to write the music prompt and mix the bed.
