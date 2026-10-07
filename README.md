# ohong-skills

Reusable Claude Code plugins and Codex skills that add scripts, external retrieval, or durable specialist workflows.

## Claude Code

Add the marketplace, then install the plugins you want:

```text
/plugin marketplace add ohong/agent-skills
/plugin install save2md@ohong-skills
```

## Marketplace plugins

| Plugin | Description |
|---|---|
| [audit-and-improve](audit-and-improve/) | Audits a repository and produces a prioritized improvement plan. |
| [capture-design](capture-design/) | Saves reference visuals as a reusable design-system swipefile. |
| [distill-taste](distill-taste/) | Distills a person's publicly shared taste into an ask-* advisor skill. |
| [fast-wifi](fast-wifi/) | Diagnoses macOS Wi-Fi and internet problems with measured checks. |
| [fieldtheory-research](fieldtheory-research/) | Searches, exports, and analyzes local X bookmarks with preserved provenance. |
| [mission](mission/) | Runs file-backed milestone planning and execution for long-horizon work. |
| [name-it](name-it/) | Runs a structured brand or product naming and validation process. |
| [post-walk](post-walk/) | Turns an Apple Voice Memo into project notes, tasks, todos, and drafts. |
| [repo-now](repo-now/) | Produces a read-only briefing on a repository's current state and next actions. |
| [save2md](save2md/) | Saves articles, X posts, and YouTube transcripts as local Markdown. |
| [search-x](search-x/) | Finds a remembered X post from fuzzy clues and verifies it live. |
| [sync-well](sync-well/) | Safely inspects and reconciles local Git work with its upstream. |

## Standalone skills

| Skill | Description |
|---|---|
| [architect](architect/) | Compares architecture designs and prototypes uncertain claims before implementation. |
| [ask-lulu](ask-lulu/skills/ask-lulu/) | Gives communications advice and work reviews through a research-grounded model of Lulu Cheng Meservey. |
| [benchmark-checklist](benchmark-checklist/) | Validates performance measurements and user-visible impact. |
| [correct](correct/) | Finds repeated agent mistakes in history and fixes the repository environment that enables them. |
| [create-mascot](create-mascot/skills/create-mascot/) | Designs an original product mascot and builds it as an editable, animatable Blender asset. |
| [delegate](delegate/) | Hands a ready plan to Codex workers to implement while Claude specs and reviews. |
| [explain](explain/) | Explains what an agent did in a session: changes, reasons, evidence of completion, and what remains. |
| [explainer-video](explainer-video/) | Creates narrated videos for codebases, subsystems, and PR changes with Manim, fast speech, and ffmpeg. |
| [figure-it-out](figure-it-out/) | Designs and executes evidence-backed workflows for substantial migrations. |
| [how](how/) | Explains how a codebase, subsystem, or user flow works by tracing its implementation; critiques only on request. |
| [interrogate](interrogate/) | Challenges designs and diffs for correctness, scope, performance, and maintainability without applying fixes. |
| [pls-fix](pls-fix/) | Revives paused projects through fresh assessment, implementation, design improvement, and real user-flow verification. |
| [poteto-mode](poteto-mode/) | Coordinates portable engineering playbooks with explicit planning and delivery gates. |
| [press-release-faq](press-release-faq/) | Writes an Amazon-style Working Backwards PR/FAQ grounded in the current project. |
| [recall](recall/) | Recovers relevant project history and verifies its current state. |
| [show-me-your-work](show-me-your-work/) | Keeps a concise decision trail backed by inspectable artifacts. |
| [skill-authoring](skill-authoring/) | Keeps new and edited skills, commands, and agent definitions thin, deterministic, and progressively disclosed. |
| [spring-cleaning](spring-cleaning/) | Inspects Mac disk use, then carries out scoped, verified cleanup (read-only when asked for a plan). |
| [swarm](swarm/) | Coordinates authorized parallel workers with isolated scopes and verified coverage. |
| [switch-model](switch-model/) | Switches Codex's default model and provider, lists Fireworks serverless models, or restores GPT and Grok. |
| [take-notes](take-notes/) | Saves learnings, references, and full prompts from the current conversation as concise project notes. |
| [transcribe-youtube](transcribe-youtube/) | Transcribes YouTube links through usetranscribe.io and saves timestamped Markdown. |
| [vibe-security-audit](vibe-security-audit/) | Audits and fixes security holes in AI-built apps, especially Supabase and Firebase backends. |

## Codex

Each standalone plugin keeps its canonical skill under `skills/<name>/`. Copy or symlink that folder into a Codex skill directory:

```bash
mkdir -p ~/.agents/skills
ln -s /path/to/agent-skills/save2md/skills/save2md ~/.agents/skills/save2md
```

Restart Claude Code or Codex, or start a fresh task, after installing or updating skills.
