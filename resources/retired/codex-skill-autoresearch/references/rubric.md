# Candidate rubric

Score every candidate on the same 100-point rubric. Use conservative distinct root-session counts; overlapping candidates may cite the same session when the behaviors are genuinely separable.

| Dimension | Points | What earns a high score |
|---|---:|---|
| Recurrence | 25 | The same job appears across many root tasks, dates, or projects. Repeated automation runs alone do not count as repeated user demand. |
| Friction and rework | 20 | The traces show corrections, retries, missing evidence, fragile handoffs, or costly rediscovery that a protocol could prevent. |
| Expected time saved | 20 | A skill would remove meaningful search, setup, reconciliation, or verification work rather than merely rename a prompt. |
| Existing-skill gap | 20 | No current skill covers the protocol, or an existing skill has a concrete and evidenced missing mode. Give low points to generic routers and duplicates. |
| Feasibility and safety | 15 | The workflow has observable inputs and outputs, can preserve authorization boundaries, and does not depend on unreliable or prohibited access. |

## Required evidence

For every ranked item provide:

- a narrow action-oriented skill name;
- `Build`, `Improve existing`, or `Do not skillify`;
- total and dimension scores;
- a conservative supporting-session count;
- three to six full session IDs with one-line paraphrases;
- the repeatable input, procedure, and output;
- overlap with available skills;
- the permission boundary and likely failure mode;
- confidence: high, medium, or low.

Frequency is not sufficient. Reject a candidate when ordinary repository inspection already recovers the needed behavior, when the task is inherently one-off, when a connector skill already handles it well, or when skill instructions would add more ceremony than leverage.

## Comparison rules

- Compare recommendations within one frozen corpus and rubric. Do not mix counts from a live-growing trace store into a completed run.
- Separate human-initiated tasks from scheduled automations and subagent work.
- Prefer root-task evidence over tool-call volume; delegation-heavy sessions otherwise dominate.
- Distinguish a new skill from an improvement to an installed skill. The latter is often the better build.
- Note access-limited and private-source candidates explicitly. A useful skill can prepare a case or handoff without authorizing submission, purchase, cancellation, publication, or deletion.
