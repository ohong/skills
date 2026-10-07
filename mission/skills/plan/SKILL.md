---
name: plan
description: >-
  Interactive mission planning — research the codebase, ask clarifying questions,
  decompose work into milestones with acceptance criteria, and save an approved plan.
  Start here before /mission:start.
argument-hint: "<task description>"
disable-model-invocation: true
effort: high
---

# Mission Planning — Orientation

Plan quality decides how the rest of the mission goes, so take the time to understand the task and the codebase before you draft milestones.

**Task:** $ARGUMENTS

## 1. Check the starting point

If `$ARGUMENTS` is empty or vague, ask: "What would you like me to build? Describe the end state."

If `.mission/plan.md` already exists, read it and ask: "An existing mission plan was found. Do you want to (a) replace it with a new plan, or (b) refine the existing plan?"

## 2. Ask clarifying questions

Ask 3-7 focused questions that cover:

- **Scope boundaries**: what is explicitly out of scope?
- **Existing code**: patterns, conventions, or architecture to follow.
- **Verification**: how we'll know each piece works (existing tests, manual checks, specific commands).
- **Dependencies**: external services, APIs, or packages.
- **Priority**: MVP versus nice-to-have if this runs long.

Wait for the answers before you plan. Constraints you guess at become wrong milestones.

## 3. Research the codebase

1. **Project conventions**: read `CLAUDE.md`, `README.md`, and `package.json` / `pyproject.toml`.
2. **Existing architecture**: map the relevant code with focused reads. Use subagents only when the user requests them or the work has independent, parallel branches.
3. **Build, test, and lint commands**: find them, because the acceptance criteria will use them.
4. **Fit**: decide whether the task fits the existing architecture. If something needs to change, name the tension now.

## 4. Draft the plan

Use the template at [../../references/mission-plan-template.md](../../references/mission-plan-template.md).

- **3-7 milestones.** Fewer means each milestone is too large to finish in one context; more adds coordination overhead.
- **Runnable acceptance criteria.** Each milestone has at least one command that exits 0 on success, such as "`curl localhost:3000/api/users` returns 200 with a JSON array", not "the API works".
- **Intent, not scripts.** State the goal and acceptance criteria and leave the method to the executor. Step-by-step instructions go stale as soon as reality diverges.
- **Order by dependency.** Foundational work first. The final milestone is always integration with a full verification sweep.
- **Size honestly.** S (< 15 min), M (15-45 min), L (45-90 min). Split anything larger, and split any milestone that touches more than 5-7 files.
- **Risk register.** Name the risks you can foresee so they don't surprise the executor mid-flight.

## 5. Iterate with the user

Present the plan and ask: "Does this plan look right? Any milestones to add, remove, or reorder?" The user has domain knowledge, business context, and history you don't, so fold their feedback in. Iterate until the user explicitly approves; never treat silence or your own judgment as approval.

## 6. Save the approved plan

1. Create the `.mission/` directory in the project root.
2. Write the plan to `.mission/plan.md`.
3. Create `.mission/progress.md` with all milestones listed as pending:

```markdown
# Mission Progress

**Mission:** {title}
**Started:** {date}
**Status:** Planning complete. Ready to execute.

## Milestones

- [ ] Milestone 1: {title}
- [ ] Milestone 2: {title}
- [ ] Milestone 3: {title}
...
```

4. Confirm: "Plan saved to `.mission/plan.md`. Run `/mission:start` to begin execution."
