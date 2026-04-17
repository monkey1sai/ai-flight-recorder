---
name: validate-release
description: Use when the task is to test, audit, verify, review, or prepare a feature / branch / milestone for merge or release. Appropriate for code validation, repo audits, smoke tests, evidence checks, and acceptance reviews.
---

## Goal

Produce a concrete validation result, not just a narrative summary.

## Validation workflow

1. Read the active plan and acceptance checklist.
2. Run the smallest fast checks first, then broader checks.
3. Record exact commands, outputs, failures, and reruns.
4. Distinguish:
   - passed
   - failed
   - not run
   - blocked
5. Write a validation report under `reports/validation/`.

## Minimum report sections

- `Scope`
- `Commands run`
- `Results`
- `Failures`
- `Risk assessment`
- `Recommendation`
- `Follow-up items`

## Special rules

- If the repository has UI work, capture screenshots or a textual smoke-check note.
- If the task touches research connectors, verify provenance fields and source retention behavior.
- If the task touches observability, verify event IDs, timestamps, and parent-child linkage.
- If the task touches explanations, verify evidence grades are not collapsed together.

## Completion

Recommend one of:
- `ready_to_merge`
- `merge_with_known_risks`
- `not_ready`
