# Critic

Read after every full render. The critic's job is to find what's wrong before the user does. Run it as a fresh-context subagent when possible, because the agent that made the film tends to see what it intended rather than what's on screen. Give it the render, `script.md`, `shots.json`, and the brief, and nothing about what you think is good.

## 1. Run the automated pass

```sh
uv run scripts/critic.py renders/explainer-60s.mp4 --script script.md --shots shots.json --out review/critic-01
```

It writes `review/critic-01/report.md` plus evidence:

- **Frames** - one full-resolution frame at the middle of every shot, frames 2 before and 2 after every cut, the first and last frame, and a contact sheet (uses `inspect_video.py`).
- **Transcript** - word-timed ASR of the render, diffed against the narration in `script.md`, with word error rate per beat and every dropped, added, or changed word listed with its timecode.
- **Audio** - integrated loudness and true peak (`ebur128`), clipping, and silences longer than planned.
- **Video** - black frames, frozen frames, duration, dimensions, frame rate, and codec against the brief (uses `verify_video.py`).

## 2. Look and listen

Automated checks can't judge the picture, so open the frames and review them against the brief:

- Does each shot show what its beat says? Is the subject on-model against its reference sheet (face, product, colors, logo)?
- Are there generation artifacts: extra fingers, melting text, warped geometry, flicker between adjacent frames, garbled signage?
- Is every piece of on-screen text readable at the delivery size and inside the safe area, and do captions collide with anything?
- Do cuts land on the narration's sense, and does each shot hold long enough to read?
- Does the transcript diff show the voice mispronouncing, skipping, or adding words? Listen to those beats.
- If a model that can watch video with sound is available, run `scripts/review_video.py` for an independent opinion on pacing and sound (see [perceptual review](perceptual-review.md)), and verify its claims yourself.

## 3. Verdict

Write the findings into `review.md` as a list of defects, each with a timecode, the evidence file, and the fix. Anything that blocks delivery (a wrong or missing word, an off-model subject, unreadable text, clipping, a wrong duration or aspect ratio) must be fixed and re-rendered, then the critic runs again on the new file. Report taste notes separately from blocking defects, and don't invent a numerical quality score.
