# Skills

I keep these skills for work I do more than once, from finding a half-remembered X post to turning a voice memo into a draft. Each skill has a `SKILL.md` you can read before installing it. My software engineering skills live in [ostack](https://github.com/ohong/ostack).

## Writing

| Skill | When to use it |
|---|---|
| [draft-zero](draft-zero/) | Talk through an essay idea and come away with an outline in your own words. |
| [sense-of-style](sense-of-style/) | Shape rough notes into a piece a reader can follow, using Steven Pinker’s *The Sense of Style*. |
| [writing-clearly-and-concisely](writing-clearly-and-concisely/) | Make technical prose easier to follow, sentence by sentence. |
| [writing-with-smart-brevity](writing-with-smart-brevity/) | Lead with the news, explain why it matters, and keep the caveats that change the story. |
| [no-ai-slop](no-ai-slop/) | Spot stock phrases in a draft or edit them out while keeping the writer’s voice. |
| [writing-for-agents](writing-for-agents/) | Write instructions an agent can follow and check. I adapted and extended [Matt Pocock’s skill](https://github.com/mattpocock/skills/tree/abeeaf95660ba9e8b7c753eb38f441ca707a8823/skills/productivity/writing-for-agents) for my own use. |

## Research and creative work

| Skill | When to use it |
|---|---|
| [save2md](save2md/skills/save2md/) | Keep a local Markdown copy of an article, X thread, or YouTube transcript. |
| [search-x](search-x/skills/search-x/) | Find a post from the few details you remember and verify it on X. |
| [distill-taste](distill-taste/skills/distill-taste/) | Study someone’s public work and turn their recurring judgments into an advisor skill. |
| [name-it](name-it/skills/name-it/) | Develop names for a product or brand and check the candidates. |
| [transcribe-youtube](transcribe-youtube/) | Save a timestamped transcript of a YouTube video. |
| [video-analysis](video-analysis/) | Ask questions about a local video or get a timestamped summary and critique. |
| [demo-video](demo-video/) | Make a narrated product demo from browser screenshots. |
| [motion-video](motion-video/) | Take a film from script and shot plan through narration, captions, and final edit. |

## Everyday work

| Skill | When to use it |
|---|---|
| [post-walk](post-walk/skills/post-walk/) | Turn an Apple Voice Memo into a transcript, project notes, tasks, and drafts. |
| [quarterly-derisk-exercise](quarterly-derisk-exercise/) | Work through five questions about what could go wrong and what you can do now. |
| [fast-wifi](fast-wifi/skills/fast-wifi/) | Measure a slow Mac network connection and narrow down the cause. |
| [spring-cleaning](spring-cleaning/) | Find what takes up space on a Mac, clean up the items you choose, and measure what you recovered. |

## Install

Clone the repository and preview the links the installer will create.

```sh
git clone https://github.com/ohong/skills.git
cd skills
python3 scripts/link-skills.py --dry-run
```

Run `python3 scripts/link-skills.py` to install. Codex reads the links in `~/.agents/skills`. Claude Code reads them in `~/.claude/skills`. The installer stops if a destination conflicts with an existing skill. Keep the checkout in place; the links point back to it.

To install only selected skills in one project, run this command from the checkout.

```sh
python3 scripts/link-skills.py --target ~/dev/my-project --only save2md,search-x
```

For skills packaged as Claude plugins, you can use the marketplace instead.

```text
/plugin marketplace add ohong/skills
/plugin install save2md@ohong-skills
```

Start a fresh agent session to pick up the installation. For the older Codex-specific directory, use `--agents codex`. If you maintain a local catalog for skills under the Git-ignored `private/` directory, use `--include-local`. See [maintenance notes](MAINTENANCE.md) for the repository’s history.
