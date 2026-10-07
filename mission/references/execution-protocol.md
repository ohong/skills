# Execution Protocol

The milestone OODA loop. `mission:start` and `mission:continue` both follow it.

Each milestone is a complete OODA cycle: orient to the goal, act on it, observe the results, reorient for what's next.

## 1. Orient — Load the milestone

Print a header:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MILESTONE {N}/{TOTAL}: {title}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

- Read `.mission/progress.md` for current state and `.mission/plan.md` for this milestone's goal and acceptance criteria. The files are the source of truth, not your memory of the conversation.
- Read the source files you'll modify. The disk may differ from what you remember.
- If `.mission/learnings.md` exists, check it for relevant patterns.
- Mismatch check: if the code doesn't match what earlier milestones should have produced, investigate before proceeding, because errors compound downstream.

## 2. Decide

For familiar patterns (standard CRUD, common test setup, well-known library), act directly. For novel situations (unfamiliar architecture, unexpected behavior, complex integration), read more code and deliberate first.

The acceptance criteria set the goal and the approach is yours: the plan specifies intent, not scripts.

## 3. Act — Implement

- **Stay scoped.** Touch only files relevant to this milestone. Don't refactor adjacent code or pull in later milestones' features.
- **Commit incrementally** after each meaningful change as `mission(N/total): {description}`. Commits are rollback checkpoints.
- Each change is a hypothesis that the acceptance criteria will now pass. Step 4 tests it.

## 4. Observe — Validate

Run every acceptance criterion in the plan for this milestone, and report results from the commands you ran. A claim like "tests pass" or "build succeeds" needs the actual run behind it.

If a command fails, your hypothesis doesn't match reality, so reorient before retrying. After 3 failed attempts at the same fix, go to Level 2 below.

## 5. Reorient — Update state

After validation passes, update `.mission/progress.md`:

```markdown
- [x] Milestone 1: Set up database schema ✅ (verified: tests pass, migrations run)
- [x] Milestone 2: Implement API routes ✅ (verified: all endpoints return expected responses)
- [>] Milestone 3: Build frontend components (in progress)
- [ ] Milestone 4: Integration testing
```

Write discoveries that change the orientation for later milestones to `.mission/learnings.md`.

## 6. Tempo check — Manage context

- If context is heavy (20+ minutes of work, many file reads, failed attempts) or the milestone was novel or hard, tell the user: "Context is getting heavy. I recommend `/clear` then `/mission:continue` for fresh context." A refresh sheds accumulated drift, and nothing is lost because plan, progress, learnings, and code are on disk.
- Otherwise go straight to the next milestone.

Use focused direct reads. Delegate to subagents only when the user requests it or independent parallel work repays the handoff cost.

## After all milestones — Final observation

1. Run a full verification sweep: all tests, build, lint, type-check.
2. Update `.mission/progress.md` with the final status.
3. Print:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MISSION COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Milestones: {completed}/{total}
Files changed: {list key files}
Verification: {all checks passed / issues remaining}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

4. Ask the user whether to commit, create a PR, or continue with additional work.

## Failure recovery

A failure means your mental model differs from reality. The response depends on how deep the mismatch is.

**Level 1 — Fix (attempts 1-3).** Read the error, fix the specific issue, re-run.

**Level 2 — Destroy and create (after 3 failures).** Retrying variations won't help.
1. Stop coding.
2. Re-read the relevant source files from disk and the error messages, without your assumptions layered on top.
3. Name the assumption that was wrong.
4. Build a new approach from the pieces that still hold plus the new information.
5. If the plan itself is wrong, tell the user: "This milestone needs rethinking. Run `/mission:pivot`."

**Level 3 — Escalate.** If Level 2 doesn't resolve it, write what you tried to `.mission/progress.md`. State the goal, what failed, what you tried, and your best hypothesis about the root cause. Ask the user for direction and stop working autonomously.

Don't work around a failing gate: bypassing it lets the mismatch compound downstream.
