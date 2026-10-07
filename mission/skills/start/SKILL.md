---
name: start
description: >-
  Begin executing an approved mission plan from milestone 1.
  Requires .mission/plan.md to exist. Runs milestones sequentially
  with validation gates between each. Use /mission:plan first.
disable-model-invocation: true
effort: high
---

# Mission Start — Enter the OODA Cycle

You are beginning execution. Each milestone is its own OODA cycle: orient to the milestone, act on it, observe the results, reorient for the next.

## Pre-flight

1. If `.mission/plan.md` doesn't exist, say "No mission plan found. Run `/mission:plan <task>` first." and stop.
2. If `.mission/progress.md` doesn't exist, say "No progress file found. Run `/mission:plan <task>` first." and stop.
3. Read both files. If milestones are already done, ask: "Previous progress detected. Resume with `/mission:continue`, or restart from milestone 1?"
4. Run the plan's build, test, and lint commands once. If one fails, fix the environment before starting, because a broken environment contaminates every later observation.

## Execution

Follow [../../references/execution-protocol.md](../../references/execution-protocol.md) from **Milestone 1**. It covers the per-milestone loop, validation, failure recovery, and context management.

Rules that hold throughout:

- Run the acceptance criteria. Reading your own code and judging it correct is not validation.
- Touch only files in the current milestone. New work goes through `/mission:pivot`.
- Commit after each meaningful change as `mission(N/total): {description}`, and make sure each passing milestone ends in a checkpoint commit.
- Use subagents only when the user requests them or independent parallel work clearly repays the coordination cost.
