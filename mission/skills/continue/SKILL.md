---
name: continue
description: >-
  Resume a mission from the last completed milestone. Use after /clear,
  in a new session, or when context is getting long. Reads plan and
  progress from .mission/ files and picks up where you left off.
disable-model-invocation: true
effort: high
---

# Mission Continue — Forced Reorientation

You are resuming a mission with fresh context. Your old context, with its drift and stale assumptions, is gone, and the `.mission/` files carry the shared orientation forward.

## Reorientation procedure

### 1. Observe — Read the state from disk

Read these files in order, so the current state is freshest in context:

1. `.mission/plan.md` — the full plan (shared intent)
2. `.mission/learnings.md` — if it exists, patterns from earlier work
3. `.mission/progress.md` — current state

If `.mission/plan.md` doesn't exist, say "No mission plan found. Run `/mission:plan <task>` first." and stop.

### 2. Orient

From the files, identify the completed milestones (`[x]`), the next milestone (first `[ ]` or `[>]`), any blockers, partial work, or discoveries, and the next milestone's acceptance criteria.

### 3. Announce

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MISSION RESUMED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Completed: {N}/{total} milestones
Resuming:  Milestone {N+1}: {title}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4. Mismatch check

If progress notes mention partially completed work, read the relevant source files and run a quick verification. If progress.md disagrees with the actual file state, trust the files and update progress.md to match.

### 5. Execute

Follow [../../references/execution-protocol.md](../../references/execution-protocol.md) from the **next incomplete milestone**. Re-read source files and the plan before each milestone instead of relying on memory.
