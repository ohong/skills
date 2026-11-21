# Skills cleanup — October 12, 2026

Completed the authorized cleanup in ohong/skills and ohong/ostack.
The catalogs now contain 20 general skills and 10 engineering skills.
Three additional personal skills remain local, ignored, and installed.

## Result

- Merged how into explain. Separate change and runtime references preserve the two explanation modes and upstream attribution.
- Preserved the completed pls-fix/reforge merge.
- Merged design-system-extractor and extracting-design-systems into capture-design, including responsive inspection, component states, and examples.
- Removed skill-authoring as a duplicate of built-in skill-creator and installed writing-for-agents.
- Kept transcribe-youtube as a thin adapter to save2md's single service guide and helper.
- Replaced delegate's model pins and stale companion assumptions with explicit authorization, worker ownership, and integrated verification.
- Moved press-release-faq, switch-model, take-notes, and win-seo into ostack with their complete support files.
- Updated both README catalogs, maintenance records, marketplace registrations, installers, dependent skills, and installed consumers.

The explicit retirement set includes git-commit-helper, skill-evolver, hatch-pet,
vibe-security-audit, architect, audit-and-improve, audit-choices, benchmark-checklist,
codex-first, figure-it-out, interrogate, memory-curator, every mission command,
poteto-mode, show-me-your-work, swarm, sync-well, task-manager,
claude-power-user-digest, codex-skill-autoresearch, create-mascot, recall,
research-location, and the entire Caveman family, including cavecrew.

Mission, Caveman, and audit-and-improve were uninstalled through Claude's plugin
CLI, preserving plugin data. Mission is replaced by the built-in /goal.
Useful retired support files remain under resources/retired in their owning repo.
Removed prompts and the prior consumer map have a separate local backup at
/Users/ohong/.codex/backups/skills-cleanup-2026-10-12.

## Design choices

A merged explain router with two focused references preserves both purposes while
avoiding competing discovery entries. Keeping two entrypoints would retain familiar
names but leave duplicated evidence and read-only rules.

Public and personal catalogs stay separate. This prevents portable installs from
requiring ignored personal files. --include-local adds the local catalog explicitly.

Retired support files remain outside skill discovery. Keeping disabled SKILL.md
files would retain accidental discovery and stale prompts; deleting entire packages
would discard usable scripts, contracts, tests, templates, and licenses.

Prompt edits followed the current [OpenAI model guidance](https://developers.openai.com/api/docs/guides/latest-model),
with focused instructions, existing authorization, and no fixed model ranking.

## Verification

- Built-in quick_validate.py: all 30 maintained skills passed, using an isolated uv environment with PyYAML. System Python initially lacked PyYAML.
- Catalog/source parity and unique names: passed for both repositories.
- Real installer into temporary project directories: passed for agents, Claude, and Codex.
- Repeated installation: created zero additional links.
- Existing-installation conflict: failed clearly without creating other pending links.
- Current global links: all maintained and personal entries resolve to their canonical sources.
- Consumer scan: no retired skill links or broken links to owned sources. Removed two additional stale Claude synced links found during validation.
- Claude installed and enabled plugin registrations: obsolete plugins absent.
- Personal directories: on disk, ignored, absent from Git's tracked file list, and installed for all three agents.
- Retired scripts and support files: 73 files preserved byte-for-byte against the pre-cleanup backup.
- Moved switch-model and take-notes CLI help commands: passed. The codex-switch-model executable symlink resolves to ostack.
- git diff --check: passed in both repositories.

## Limits

These checks verify packaging, metadata, resource preservation, and actual installer
behavior. They do not establish behavioral quality improvements for every workflow.
No live transcription, model-provider switch, SEO mutation, or production deployment
was performed. Existing unrelated edits remain. No commit, push, or history rewrite
was performed. Start a fresh chat to refresh the skill list already loaded in context.
