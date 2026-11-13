# Sound and resource decisions

Read when selecting music/SFX, planning voiceover, or considering an external resource. Oscar permits suitable free sound effects, including the [Pixabay app collection](https://pixabay.com/sound-effects/search/app/). Fal and Suno are pre-approved within the project cap set in SKILL.md; anything else paid needs a budget request. Spend only on an identifiable, material improvement to the final output.

## Build the soundtrack with the edit

Choose the emotional character and energy curve before buying or generating anything. Audition a small shortlist against the actual rough cut. A distinctive understated track can be more effective than a generic promotional bed. Prefer instrumental music for the default short films; use voiceover when it carries meaning the images and short copy cannot carry elegantly, or when requested.

Design a small family of effects: a restrained tap/click for intention, a short transition texture for a motivated move, a confirmation/reveal for the payoff, and deliberate quiet where the image should breathe. Not every pointer movement needs a sound. Match onset and transient to the visible event, not simply the beginning of its shot. Mark cue times in the storyboard. Let picture and music shape one another without mechanically cutting on every beat.

Edit each duration to its own musical phrase and resolved ending. Do not cut a 30s waveform at 10s and call it a teaser mix. Fade or shape tails within the delivery duration; use short fades to prevent edit clicks. Control harsh high-frequency UI effects, leave headroom, and duck music when there is speech. Check speakers/mono and headphones when listening tools are available.

For ordinary web delivery, roughly -16 to -14 LUFS integrated and a true-peak ceiling near -1 dBTP can be useful starting targets, not mandatory platform specifications or an artistic score. Measure the actual exported mix and judge it by ear. Short/SFX-led pieces can measure oddly. Do not normalize silence or judge a film solely by integrated loudness. Record any missing listening pass honestly.

When this environment cannot hear the track, use [the perceptual-review guide](perceptual-review.md) to prepare an optional review of picture and sound together. Its adapter previews locally by default and requires authorization before sending media or spending money. Keep human listening, model opinion, and numerical analysis distinct. A generated or synthesized soundtrack is a candidate until someone or a capable model has heard it against the edit.

## Generated music with Suno

Use Suno for the background bed when no cleared track fits. Write the music brief from the edit, not from the genre: tempo that matches the cutting rhythm, where the energy rises and resolves, and which beats must stay quiet under narration. Always request an instrumental for narrated films, since lyrics fight the voice.

```sh
uv run scripts/suno.py --prompt "sparse felt piano and low strings, 84 bpm, slow build from 0:20, resolves softly at the end, no drums until the last third" --instrumental --out music/bed
```

Suno returns two candidates per request; audition both against the animatic and keep the one that leaves room for the voice. Generated tracks rarely end exactly where the film does, so cut to a phrase boundary and shape the tail with a fade, or generate at the target length and extend if needed. Record the Suno clip ID and plan terms in `assets.md`. If `SUNO_API_KEY` is missing, fall back to a Fal music model through `scripts/fal_run.py` (see [generation](generation.md)) or a cleared library track.

Duck music under speech with a sidechain rather than a flat volume cut, so it breathes back up between sentences:

```sh
ffmpeg -i music.wav -i vo.wav -filter_complex "[0][1]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[bed];[bed][1]amix=inputs=2:normalize=0" mix.wav
```

## Source and rights ledger

Prefer the user's cleared library or an appropriate free/licensed resource. Pixabay's [license summary](https://pixabay.com/service/license-summary/) describes free use and adaptation with conditions; inspect the current asset page and applicable terms when selecting an asset. Do not assume that every searchable/downloadable sound has the same rights or that “royalty-free” means public domain. Prefer neutral UI sounds over recognizable notification sounds belonging to another product.

In `assets.md`, record title/creator, source page, local filename, retrieval date, license or receipt, attribution requirements, allowed use, and the shots using it. Record any Content ID notices encountered for music. Keep references as study material; do not rip their soundtracks into a new commercial video. Use direct authorized downloads or available asset tools; do not invent a Pixabay API or bypass an access block.

## Budget requests must be concrete

Fal and Suno calls within the project cap don't need a request; they need the itemized estimate in `brief.md` and a line in `spend.jsonl`. This section covers everything else: buying a stock asset, adding a new paid provider, or going over the cap.

Complete the brief, candidate research, and a free rough proof first whenever possible. Propose a purchase only if the candidate is likely to improve a named weak point in the film. Cite the currently verified price; do not turn an illustrative budget into authorization.

A useful request is: “The reveal at 6–8s needs a more tactile sound than the free candidates. [Asset/source] costs $X under [license]. May I spend up to $Y total for this film? The cap includes [fees/calls/iterations]. The fallback is [specific free option].” For a new API also explain what access is needed, what content is sent, the expected number of calls, and how the cost stops at the cap. Never ask the user to paste secrets into chat.

Prefer a one-off asset or capped usage over a subscription unless recurring value is clear. Approval applies to the stated provider/resource, purpose, and ceiling. Track actual spend against the approved cap; do not assume unused budget can fund unrelated resources. Ask again before exceeding it or adding a subscription/new purpose. If approval is pending, continue the parts of the film that do not depend on it. If declined, make the strongest available version and disclose only material compromises.

No budget is required merely to brainstorm or inspect available local tools. Do not add paid services as a ritual step or recommend a tool solely because it is fashionable.
