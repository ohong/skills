# Writing and reviewing a skill

## Choose a trigger

When proposing a skill, identify a recurring decision the agent gets wrong or a local fact it repeatedly rediscovers. Look for an existing skill that owns that decision. A one-off instruction can stay with its task.

For automatic discovery, write a short third-person description using the requester's vocabulary. Include the capability and the condition that makes it relevant. Compare it with the closest installed skill. For example, “revise instructions a coding agent will follow” distinguishes this skill from one that edits a customer newsletter.

Preserve the author's choice of automatic or explicit invocation. For an explicit-only skill, Claude Code uses `disable-model-invocation: true` in frontmatter. Codex uses `policy.allow_implicit_invocation: false` in `agents/openai.yaml`. Both can retain a useful description for the human reader.

## Package what the agent needs

Keep shared decisions in the entrypoint. Link a branch-specific reference directly from the decision that needs it. Give a long reference a short contents list. Split out a separately discoverable skill only when it serves a distinct request. A single entrypoint can route several related workflows.

Keep stable constraints in prose. For changing flags or schemas, point to the installed tool's help or the maintained schema. If a bundled snapshot is necessary, record its source and how to regenerate it. Package repeated mechanical checks as scripts when they make execution more reliable. State the prerequisites and what a failed check means.

When several manually invoked skills are hard to remember, give the user one entrypoint that names each skill and when to choose it. If several skills need the same definitions, link directly to one shared reference file. This keeps the definitions available whichever skill the user starts with.

## Evaluate a revision

Choose realistic requests and define visible success before judging the wording. Useful cases include a typical request, a tricky variation, and a nearby request that belongs to another skill.

For example, try “Write instructions for our release-note agent,” then “Review the agent instructions in this README.” Both should produce actionable instructions for an agent. “Edit these release notes for customers” should select a prose-editing workflow.

Compare the same cases with and without the revision in fresh sessions on the intended model. Leave the skill name out when testing discovery. For execution, inspect the resulting work and which references or tools the agent used. A valid file alone proves little about behavior.

When a run fails, locate the first wrong decision. Did the agent miss the trigger, lack a prerequisite, or accept a bad result? Change the instruction responsible and replay the case. Keep evidence of what actually improved.
