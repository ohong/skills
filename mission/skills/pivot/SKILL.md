---
name: pivot
description: >-
  Mid-flight mission plan adjustment. Use when the approach is wrong,
  requirements changed, a milestone needs splitting, or scope needs updating.
argument-hint: "[reason for pivot]"
disable-model-invocation: true
effort: high
---

# Mission Pivot

The current plan no longer matches reality. Rebuild the parts that are wrong from what still holds plus what you've learned, instead of forcing the old plan.

**Reason:** $ARGUMENTS

## 1. Identify the mismatch

Read `.mission/plan.md`, `.mission/progress.md`, and `.mission/learnings.md` (if it exists). Name the trigger: scope change, a milestone much larger than estimated, a technical approach that keeps failing, a newly discovered dependency, or a change of direction.

## 2. Sort the old plan

Decide which completed milestones stand, which upcoming milestones are still correct, which need to change, split, or be replaced, and what the failed approach taught you.

## 3. Draft the new plan

- Add milestones for added scope.
- Split oversized milestones into 2-3 smaller ones.
- Replace milestones whose approach is wrong.
- Insert dependency milestones where needed.
- Mark removed milestones as `[~] superseded` instead of deleting them, so the history stays readable.

Completed milestones are immutable. If their work needs to change, add a new milestone.

## 4. Get approval

Show what changed and why, the updated milestone list with old milestones marked, and the impact on remaining work. Get explicit approval before you modify any files.

## 5. Save the updated plan

- Update `.mission/plan.md` with the new milestones.
- Update `.mission/progress.md` to reflect the new structure.
- Write what changed, why, and what you learned to `.mission/learnings.md`. Later sessions and pivots depend on this record.

Tell the user: "Plan updated. Run `/mission:continue` to resume from milestone {N}." Don't resume execution in the same step: planning and execution stay separate so the user can review the plan first.
