---
name: implement-execplan
description: Use when the repository already has an active ExecPlan and the task is to implement, extend, refactor, or migrate code according to that plan. Do not use for tiny isolated edits that do not need milestone tracking.
---

## Goal

Execute the active plan safely, one milestone at a time.

## Required workflow

1. Read `AGENTS.md`, the main guide, and the relevant file in `plans/active/`.
2. Identify the current milestone and its success criteria.
3. Implement the smallest vertical slice that makes progress on that milestone.
4. Run the narrowest relevant checks immediately.
5. Update the plan:
   - `Progress`
   - `Surprises & Discoveries`
   - `Decision log`
   - `Validation plan` if commands changed
6. Only then move to the next milestone.

## Implementation rules

- Keep diffs focused.
- Avoid unrelated cleanup unless it unblocks the milestone.
- If repository conventions are missing, create the smallest durable convention that future Codex runs can reuse.
- Prefer typed interfaces, explicit schemas, and migration-backed storage changes.
- If the plan is missing critical detail, repair the plan first instead of guessing blindly.

## Required outputs

At each safe checkpoint provide:
- what changed
- what passed
- what is still failing
- what milestone remains
- where validation evidence was stored

## Stop conditions

Pause and document clearly if:
- credentials are missing
- infrastructure is unavailable
- a schema choice has multiple incompatible interpretations
- the task would require unsafe permissions outside the agreed sandbox
