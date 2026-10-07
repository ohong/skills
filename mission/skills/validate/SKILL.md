---
name: validate
description: >-
  Run acceptance criteria for the current milestone (or all milestones).
  Reports pass/fail. Pure observation — does not advance or fix anything.
argument-hint: "[milestone number or 'all']"
disable-model-invocation: true
---

# Mission Validate

Run acceptance criteria without advancing. Use it to check your work, verify a fix, or confirm the full mission is healthy.

**Target:** $ARGUMENTS

## Procedure

1. Read `.mission/plan.md` and `.mission/progress.md`.

2. Determine scope:
   - `$ARGUMENTS` is a number → validate that specific milestone
   - `$ARGUMENTS` is "all" → validate ALL milestones (full sweep)
   - `$ARGUMENTS` is empty → validate the current milestone (first incomplete)

3. For each milestone, run every acceptance criterion from the plan.

4. Report:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VALIDATION: Milestone {N}: {title}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ `bun test` — passed (12 tests, 0 failures)
  ✅ `bun run build` — passed
  ❌ `bun run typecheck` — FAILED
     → src/api/users.ts:42 — Type 'string' not assignable to 'number'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Result: 2/3 passed, 1 FAILED
```

5. For "all" validation, show a summary:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FULL VALIDATION SWEEP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ Milestone 1: Set up schema — all pass
  ✅ Milestone 2: API routes — all pass
  ❌ Milestone 3: Frontend — 1/3 failed
  ⬜ Milestone 4: Integration — not yet implemented
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

6. Suggest next action:
   - All pass → "Validation clean. Continue with `/mission:continue`."
   - Failures → "Mismatches detected. Fix the failures, then re-run `/mission:validate`."

## Rules

- Validation means running the commands. Reading code and judging it correct is not validation.
- Include exact error output, because whoever fixes the failure needs it.
- Don't fix anything. Fixes happen in `/mission:start` or `/mission:continue`.
