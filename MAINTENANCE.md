# Source ownership

- `ohong/skills`: reusable productivity, research, writing, creative, and agent-tool workflows.
- `ohong/ostack`: reusable software engineering and software factory workflows.
- Project repositories: skills bound to their application's behavior, data, or runtime.
- Upstream installers and provider plugins: third-party skills, preserved with their original source and license.
- Existing private skill stores: workflows already separated from public sources, including Amex claims and flight check-in.

Keep canonical files in the owning repository. Global and project consumers use symlinks.
Use `scripts/link-skills.py --target <project> --only <names>` to add a project consumer.
Update `catalog.json` when adding, removing, or renaming a skill.

## October 12, 2026 migration

Renamed `ohong/agent-skills` to `ohong/skills` and the local checkout to `~/dev/skills`.
The old local name remains a compatibility symlink for active chats and historical paths.
Moved the clean, unused Anthropic clone to Trash at the user's request.
Moved 18 engineering packages into `ostack/skills`; their earlier Git history remains in this repository.
Preserved existing uncommitted save2md edits separately from the migration.

Imported local reusable sources for daily-close, demo-video, motion-video, no-ai-slop, research-location,
hatch-pet, win-seo, design-system-extractor, writing-with-smart-brevity, codex-skill-autoresearch, and skill-evolver.
Also centralized video-analysis, imessage-access, claude-power-user-digest, and quarterly-derisk-exercise from Documents and projects.
The digest source omits its hardwired personal contact address; the original is preserved locally.

Imported personal cloud-authored draft-zero, hobonichi, whisky-review, and extracting-design-systems.
Consolidated the dotfiles communication family; engineering-specific members moved to ostack.
These imports preserve existing instructions and supporting resources. Their origin is the existing local installation;
absence from an installer lock is not proof of original authorship. Preserve embedded licenses and attribution.

Installer-managed skills from Matt Pocock, Emil Kowalski, Vercel, Firecrawl, Impeccable, and other upstreams were not reclassified as Oscar-authored skills.
Provider-owned synced runtime guides remain provider-managed. Legacy slash commands remain in dotfiles.
The board-member persona skill remains in Board Meeting. Other application-specific research and CLI skills remain with their projects.

Divergent installed editions of capture-design, press-release-faq, vibe-security-audit, init-board-member,
and file-amex-claim were preserved in the local migration backup before consumers were linked to the maintained sources.
The maintained repository editions are authoritative. Review the preserved variants before deliberately merging behavioral differences.
The private flight-checkin source remains in its existing private store.

Large motion-video reference clips remain available locally under `motion-video/references/videos/`, but are ignored by Git.
The portable written reference atlas stays tracked. Files copied from upstream retain their individual license terms.

## Authorized cleanup — October 12, 2026

The earlier migration and audit sections describe historical states.
`catalog.json` and the README table list the current maintained entrypoints.

- Retired the user-selected obsolete workflows and every Caveman entrypoint, including cavecrew.
- Removed mission registration and installation; long-running work now uses `/goal`.
- Merged how into explain. Change and runtime guides remain separate references under explain; the upstream MIT notice remains intact.
- Preserved the already merged pls-fix/reforge source without reopening that merge.
- Folded both design extractors into capture-design with component, responsive, and example references.
- Removed duplicate skill-authoring discovery in favor of built-in skill-creator and installed writing-for-agents.
- Kept transcribe-youtube as a thin explicit adapter; save2md owns its helper and service procedure.
- Moved press-release-faq, switch-model, take-notes, and win-seo into ostack with all scripts, tests, and references.
- Removed personal hobonichi, imessage-access, and whisky-review from the public catalog. Their local files and installations remain; ohong/skills ignores them and catalog.local.json.

Useful retired scripts, tests, references, templates, and licenses remain under
`resources/retired/<name>/` in the owning repository. These are retained support
artifacts, not active skills; entrypoints and generated skill bundles are removed.
Historical workflow documents in that directory do not establish current instructions.
A separate local backup preserves removed entrypoints and the prior link map.
No Git history rewrite, commit, push, or remote publication was performed.
