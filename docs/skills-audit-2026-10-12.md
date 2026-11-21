# Full skills audit — October 12, 2026

> Historical pre-cleanup inventory. The authorized cleanup supersedes these recommendations; see [cleanup report](skills-cleanup-2026-10-12.md).

The migration relocated existing sources; it did not create new skills. Explainer-video was created earlier in this conversation.
The current catalogs contain 72 entries: 40 general entries and 32 engineering entries, including six mission commands.
Reforge appeared after the previous migration. It is included here without attributing its creation to that migration.

The strongest consolidation targets are design extraction, model-pinned delegation, commit-message tutorials, duplicated authoring guidance, and the redundant YouTube service entrypoint.
Do not retire data-access scripts, extractors, state schemas, runtime formats, or source-grounded personal methods just because a newer model can write fluent prose.

## Method and limits

Inspected all maintained entrypoints, their descriptions, support-file inventory, source pointers, and selected runtime helpers.
Checked migration records, Git introduction history, installed source-lock metadata, active hook configuration, and current official model guidance.
Also inventoried 115 physical top-level installed copies with 80 unique names outside the maintained symlinks; these include manually installed and installer-managed upstream skills.
Provider plugin caches, nested examples, private stores, and every individual third-party helper were not audited line by line.
This is a static relevance, duplication, provenance, and integration audit. It is not a controlled with-skill/without-skill evaluation.
No usage-frequency claims are made. A recommendation to retire does not prove the skill never helped.

Current frontier models can implement and use tools with little generic instruction, but skill selection and detailed instructions still affect their behavior.
OpenAI specifically recommends auditing skills because stronger instruction following can amplify unclear or conflicting guidance.
Treat the following as a retention rule: keep a preferred output contract, proprietary context, tested scripts, exact runtime invariants, or an integration procedure; trim generic lectures, repeated policies, and fixed model rankings.

Official guidance: [OpenAI](https://developers.openai.com/api/docs/guides/latest-model), [Claude model catalog](https://platform.claude.com/docs/en/models/overview), [Gemini model catalog](https://ai.google.dev/gemini-api/docs/models).
These catalogs do not establish a universal Claude-versus-Codex quality ranking. Evaluate routing on actual tasks.
Gemini 3.8 TTS references in motion-video are present in Google's current catalog; they were not classified as fabricated or obsolete.

## Provenance definitions

- **Adapted upstream:** a source pointer or preserved license establishes a specific upstream origin.
- **Created locally in this chat:** direct conversation history establishes creation.
- **Local source; authorship unverified:** the file was locally maintained or installed, but no upstream or original creation record was established.
- The previous physical location is shown per skill. Relocation is not authorship.

## Prioritized cleanup

| Priority | Candidates | Action and evidence |
|---|---|---|
| P1 | design-system-extractor, extracting-design-systems | Fold unique reference material into capture-design, then remove the two duplicate discovery entries. All three take the same references and produce a design-system document. |
| P1 | codex-first, delegate | Consolidate the routing contract. Remove untested fixed quality hierarchies, model pins, and stale companion-specific workarounds. Keep actual worker tooling and verification. |
| P1 | pls-fix, reforge | Choose one revival entrypoint or make the distinction explicit. They share the same repair/rebuild objective but disagree on default delegation. Do not silently erase that user choice. |
| P1 | vibe-security-audit | Replace broad generic automatic audit with current security tooling plus narrowly scoped project rules. Do not require an access policy on every deny-all table. PostgreSQL documents default-deny when RLS is enabled without a policy. |
| P1 | audit-and-improve | Its mandatory safety-net/TDD sequence conflicts with Oscar's current no-TDD, real-runtime QA preference. Correct those instructions before using it for implementation. |
| P1 | Git Commit Helper | Its frontmatter name contains spaces and capitals. Repaired to git-commit-helper, with catalog and global consumers relinked. It remains a retirement candidate because the body is a generic Conventional Commits tutorial. |
| P1 | caveman-stats | Depends on hooks absent from the checked active Claude configuration; the Caveman plugin is disabled. Made explicit-only and added a clear unavailable state. No statistics were fabricated. |
| P2 | skill-authoring, skill-evolver | Consolidate with built-in skill-creator and installed writing-for-agents. Skill-evolver has no working evaluator and instructs unbounded pattern accumulation. |
| P2 | transcribe-youtube | Calls the exact same save2md helper. Keep a short explicit alias or provider adapter and one copy of the API invariants. |
| P2 | caveman-commit, caveman-review, caveman-help | These are mostly style or help layers. Put their useful preferences in the corresponding canonical workflow's references instead of separate generic triggers. |
| P2 | cavecrew | Named presets are present in OpenCode but were not found in the checked Claude agent directory. Gate by actual harness; share worker ownership rules with swarm. |
| P2 | hatch-pet | Keep the atlas helpers and verified failure-specific invariants. Move phase-specific instructions out of the 11,570-word entrypoint. Compare with native work-pets only after checking required output/runtime differences. |
| P2 | task-manager, memory-curator | Retain for Meridian projects. Global discovery suggests they work everywhere, but task-manager requires .meridian templates and its schema. |
| P2 | mission-plan, mission-pivot, sync-well, name-it, motion-video | Remove unnecessary questionnaires and repeat approvals where session authority and context already resolve the decision. Keep real permission boundaries. |
| P3 | no-ai-slop, humanizer, writing-with-smart-brevity | Keep one core prose-editing checklist. Smart Brevity's information hierarchy is a distinct option; these need not all be deleted. |
| P3 | explain, how, repo-now | Keep distinct: completed changes, architecture/flow, and current operational state. Their goals differ even if all produce prose. |

Security reference: [PostgreSQL row security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html).

## Cleanup applied in this audit

1. Normalized git-commit-helper frontmatter and catalog name; renamed only its two matching global symlinks.
2. Disabled implicit Caveman stats invocation in Codex metadata and narrowed the shared trigger to named stats requests. Explicit requests now check the hook and report unavailable when missing.
3. Preserved all skill bodies, scripts, references, project consumers, and unrelated edits. No semantic retirement or deletion was performed on the basis of an unmeasured model-capability claim.

## Suggested evaluation before semantic removal

For each consolidation cluster, use the same real request, inputs, selected model, tools, and permissions against the existing and simplified variants.
Compare correct deliverable completion, source grounding, user interventions, failures, runtime, and model usage when measurable.
Design capture: one real URL plus one screenshot-only case. Delegation: one clear scoped edit and one ambiguous design request.
Video: a real UI demo and a source-grounded code explainer. Revival: one stalled app with a working journey and one broken integration.
Do not fabricate cost or accuracy gains, treat repeated model self-review as independent review, or infer lack of use from absence in a few logs.

## Each maintained skill

## This repository

| Skill | Purpose | Origin | Triage |
|---|---|---|---|
| [capture-design](../capture-design/skills/capture-design/SKILL.md) | Save a visual reference as a reusable design system and asset manifest. | Local source; original authorship unverified | Keep |
| [caveman](../caveman/SKILL.md) | Use a deliberately terse response style, including classical Chinese modes. | [Copied/adapted: JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | Thin |
| [caveman-compress](../caveman-compress/SKILL.md) | Compress prose files while preserving code, values, and recoverable originals. | [Copied/adapted: JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | Keep |
| [caveman-help](../caveman-help/SKILL.md) | List Caveman modes and related commands. | [Copied/adapted: JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | Merge |
| [caveman-stats](../caveman-stats/SKILL.md) | Display token statistics supplied by Caveman's runtime hook. | [Copied/adapted: JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | Repair |
| [claude-power-user-digest](../claude-power-user-digest/SKILL.md) | Map recent Claude product changes to recurring personal workflows. | Local source; original authorship unverified | Repair |
| [codex-skill-autoresearch](../codex-skill-autoresearch/SKILL.md) | Extract redacted session evidence and rank opportunities for new skills. | Local source; original authorship unverified | Keep |
| [create-mascot](../create-mascot/skills/create-mascot/SKILL.md) | Design a mascot and build it as an editable Blender asset. | Local source; original authorship unverified | Keep |
| [demo-video](../demo-video/SKILL.md) | Turn real product screenshots and narration into a simple MP4. | [Adapted: dctanner demo-video gist](https://gist.github.com/dctanner/ee7fe7997bba0efbca49b8c0bdc1936a) | Keep |
| [design-system-extractor](../design-system-extractor/SKILL.md) | Extract colors, typography, layout, and interactions from visual references. | Local source; original authorship unverified | Merge |
| [distill-taste](../distill-taste/skills/distill-taste/SKILL.md) | Research public work and create a sourced persona advisor skill. | Local source; original authorship unverified | Keep |
| [draft-zero](../draft-zero/SKILL.md) | Interview the writer and turn their ideas into an essay outline. | Local source; original authorship unverified | Keep |
| [extracting-design-systems](../extracting-design-systems/SKILL.md) | Reverse engineer a web application's visual design system. | Local source; original authorship unverified | Merge |
| [fast-wifi](../fast-wifi/skills/fast-wifi/SKILL.md) | Measure a Mac's network bottleneck and verify scoped fixes. | Local source; original authorship unverified | Thin |
| [hatch-pet](../hatch-pet/SKILL.md) | Generate, assemble, validate, and package animated Codex pet atlases. | Local source; original authorship unverified | Rework |
| [motion-video](../motion-video/SKILL.md) | Produce scripted, narrated films with shot generation and final media checks. | Local source; original authorship unverified | Thin |
| [name-it](../name-it/skills/name-it/SKILL.md) | Develop and validate brand names through a structured naming method. | Local synthesis of naming references | Thin |
| [no-ai-slop](../no-ai-slop/SKILL.md) | Edit AI-sounding prose while preserving the author's voice and claims. | [Copied/adapted: Peter Yang](https://github.com/petergyang/no-ai-slop) | Keep |
| [post-walk](../post-walk/skills/post-walk/SKILL.md) | Transcribe a voice memo into notes, tasks, and drafts. | Local source; original authorship unverified | Keep |
| [press-release-faq](../press-release-faq/SKILL.md) | Pressure-test a product through a customer-focused launch narrative and FAQ. | Local source; original authorship unverified | Repair |
| [quarterly-derisk-exercise](../quarterly-derisk-exercise/SKILL.md) | Lead a five-question personal risk reflection. | Local source; original authorship unverified | Keep |
| [recall](../recall/SKILL.md) | Recover prior decisions and verify them against current project state. | [Adapted: Cursor pstack](https://github.com/cursor/plugins/tree/e5a8186d7b43be8d6ac4452440fbead5f1a51c70/pstack/skills/recall) | Keep |
| [research-location](../research-location/SKILL.md) | Build a sourced architectural inspiration board for a place. | Local source; original authorship unverified | Keep |
| [save2md](../save2md/skills/save2md/SKILL.md) | Archive articles, X posts, and YouTube transcripts as readable Markdown. | Local source; original authorship unverified | Keep |
| [search-x](../search-x/skills/search-x/SKILL.md) | Find and verify an X post from an incomplete memory. | Local source; original authorship unverified | Keep |
| [skill-authoring](../skill-authoring/SKILL.md) | Apply concise authoring principles to skills and agent instructions. | Local source; original authorship unverified | Merge |
| [skill-evolver](../skill-evolver/SKILL.md) | Describe a generate, execute, reflect, and curate skill-improvement loop. | Local source; original authorship unverified | Retire candidate |
| [spring-cleaning](../spring-cleaning/SKILL.md) | Measure Mac disk use and carry out scoped cleanup. | Local source; original authorship unverified | Thin |
| [switch-model](../switch-model/SKILL.md) | Switch Codex providers through validated model discovery and recoverable configuration. | Local source; original authorship unverified | Keep |
| [take-notes](../take-notes/SKILL.md) | Save new conversation learnings and complete reusable prompts. | Local source; original authorship unverified | Keep |
| [transcribe-youtube](../transcribe-youtube/SKILL.md) | Transcribe YouTube through the existing service and save timestamped Markdown. | Local source; original authorship unverified | Merge |
| [video-analysis](../video-analysis/SKILL.md) | Analyze actual local video and audio with timestamped Gemini evidence. | Local source; original authorship unverified | Keep |
| [win-seo](../win-seo/SKILL.md) | Improve search performance using persistent evidence and measured follow-up. | Local source; original authorship unverified | Keep |
| [writing-with-smart-brevity](../writing-with-smart-brevity/SKILL.md) | Reorder and tighten prose around the reader's most important point. | Local source; original authorship unverified | Keep |
