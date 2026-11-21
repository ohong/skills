# skills

My reusable non-engineering skills for life, general knowledge work, and productivity.
Software engineering and product development workflows live in [ohong/ostack](https://github.com/ohong/ostack).
Project-specific skills stay with their projects. Installed upstream skills remain maintained by their original authors.

## Install

Clone this repo to `~/dev/skills`, then link its standalone skills into the global agent directories:

```sh
python3 scripts/link-skills.py --dry-run
python3 scripts/link-skills.py
```

The installer links `~/.agents/skills` and `~/.claude/skills` to these sources. Codex discovers the shared `.agents` directory.
Existing installations are preserved; conflicts stop before any links are created.
Use `--agents codex` if you need the older Codex-specific directory.

Link selected skills into a project:

```sh
python3 scripts/link-skills.py --target ~/dev/my-project --only save2md,search-x
```

The project stores symlinks, not copies. Update the canonical source here.
A local symlink requires this checkout on that machine; it is not a portable vendored installation.

For Claude marketplace plugins:

```text
/plugin marketplace add ohong/skills
/plugin install save2md@ohong-skills
```

Restart the agent or start a fresh chat after changing installations.
See [MAINTENANCE.md](MAINTENANCE.md) for source ownership and migration details.

Personal skills stay local and ignored. Reinstall them with `python3 scripts/link-skills.py --include-local`.

Retired support files are preserved under `resources/retired/`; they are excluded from skill discovery.

## Skills

| Skill | Purpose |
|---|---|
| [ask-lulu](ask-lulu/skills/ask-lulu/) | Chat with a research-grounded model of Lulu Cheng Meservey for candid communications advice or work review. |
| [daily-close](daily-close/) | Reconstruct Oscar's day into a concise, evidence-backed local daily log draft and at most three decisions. |
| [demo-video](demo-video/) | Create a narrated MP4 demo from browser screenshots, low-cost fal.ai text-to-speech, and ffmpeg. |
| [distill-taste](distill-taste/skills/distill-taste/) | Deep-research a named person's (or group of people's) public writing, interviews, and talks, then distill their taste into a standalone installable ask-person advisor skill. |
| [draft-zero](draft-zero/) | Interview the writer and turn an essay idea into a rough outline with their own words. |
| [fast-wifi](fast-wifi/skills/fast-wifi/) | Diagnose a slow macOS network with the bundled measurement script. |
| [fieldtheory-research](fieldtheory-research/skills/fieldtheory-research/) | Search, sync, export, and analyze the user's local X bookmarks with the Field Theory CLI while preserving full post text and provenance. |
| [karasz-cover](karasz-cover/) | Create artistic illustrated covers for projects or ideas with imagegen, using the supplied Ilonka Karasz cover references. |
| [motion-video](motion-video/) | Direct and produce finished videos end to end - product films from a deployed URL or codebase, narrated explainers, and generated or motion-graphics pieces - with a written script, emotive TTS narration, generated keyframes and shots, real Creative Commons footage, music, word-timed captions, and a critic pass. |
| [name-it](name-it/skills/name-it/) | Run a structured brand or product naming and validation process. |
| [no-ai-slop](no-ai-slop/) | Edit drafts into sharper, more human writing while preserving the writer's personal voice, or detect AI-slop patterns without rewriting. |
| [post-walk](post-walk/skills/post-walk/) | Process a local Apple Voice Memo into an archived transcript, project notes, tasks, todos, and drafts. |
| [quarterly-derisk-exercise](quarterly-derisk-exercise/) | Ask Oscar the "5 questions to de-risk life" exercise, once a quarter. |
| [save2md](save2md/skills/save2md/) | Save articles, X posts or threads, and YouTube transcripts as local Markdown with bundled tools. |
| [search-x](search-x/skills/search-x/) | Find a specific remembered X post from fuzzy clues and verify it on the live post. |
| [sense-of-style](sense-of-style/) | Turn notes or rough prose into clear, vivid writing using the principles in Steven Pinker’s *The Sense of Style*. |
| [spring-cleaning](spring-cleaning/) | Inspect Mac disk use, identify recoverable space, and carry out scoped cleanup with verification. |
| [transcribe-youtube](transcribe-youtube/) | Transcribe a YouTube video through usetranscribe.io and save timestamped Markdown. |
| [video-analysis](video-analysis/) | Analyze local videos with the Gemini API for timestamped summaries, spoken content, visual explanations, critique, and finding specific moments. |
| [writing-clearly-and-concisely](writing-clearly-and-concisely/) | Draft, revise, or review prose for clarity, precision, and concision. |
| [writing-for-agents](writing-for-agents/) | Write and review instructions agents follow. Adapted and extended for my own use from [Matt Pocock’s skill](https://github.com/mattpocock/skills/tree/abeeaf95660ba9e8b7c753eb38f441ca707a8823/skills/productivity/writing-for-agents). |
| [writing-with-smart-brevity](writing-with-smart-brevity/) | Rewrites long-winded, padded or AI-sounding text into Smart Brevity style (Axios / VandeHei, Allen & Schwartz) - main point first, why it matters, ranked support, clear next step - without losing facts, caveats or warmth. |
