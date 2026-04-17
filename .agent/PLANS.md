# ExecPlan standard for this repository

This file defines the **execution plan** format used for long-running Codex work.

An ExecPlan must be understandable to a complete newcomer who only has:
- the current working tree
- this file
- the plan file itself

The plan must be self-sufficient enough that work can restart from the plan alone.

## When to create a plan

Create a plan for:
- architecture changes
- new modules or services
- schema changes or migrations
- long-running research or integration tasks
- features that need staged delivery
- work that spans frontend + backend + infra
- anything risky enough that rollback matters

## Where plans live

- active: `plans/active/YYYYMMDD-short-slug.md`
- done: `plans/done/YYYYMMDD-short-slug.md`

Move the plan to `plans/done/` only after validation is complete.

## Naming rule

Use a date plus a short action-oriented slug.

Examples:
- `plans/active/20260417-bootstrap-monorepo.md`
- `plans/active/20260417-google-drive-ingestion.md`

## Plan structure

Every plan must contain these sections.

---

# <Short action-oriented title>

## 1. Purpose / Big Picture

Explain:
- what user-visible outcome this work enables
- why it matters now
- how someone will know it works

## 2. Scope

List:
- in-scope work
- out-of-scope work
- assumptions
- constraints
- dependencies

## 3. Repository context

Point to the relevant files, directories, services, docs, and interfaces.
If the repo is missing required structure, say so explicitly.

## 4. Success criteria

Define completion in observable terms.
Prefer concrete criteria over vague intent.

Include:
- behavior checks
- API or UI checks
- data correctness checks
- performance or reliability checks if relevant
- documentation and test expectations

## 5. Milestones

Break the work into ordered milestones.

For each milestone include:
- goal
- deliverables
- validation method
- rollback or containment note if failure risk is meaningful

## 6. Progress

Maintain a live checklist.

Use this exact format:

- [ ] not started
- [x] done
- [-] partially done; explain what remains

Include timestamps in UTC for meaningful progress updates.

## 7. Research notes

Record external facts that influenced the implementation.
Each entry should include:
- source
- finding
- why it matters
- confidence level
- any remaining uncertainty

## 8. Surprises & Discoveries

Write down:
- unexpected behaviors
- hidden dependencies
- broken assumptions
- useful shortcuts
- failed ideas worth remembering

## 9. Decision log

Record important decisions with:
- date
- decision
- rationale
- alternatives rejected

## 10. Validation plan

List exactly what to run:
- lint
- typecheck
- unit tests
- integration tests
- smoke checks
- manual QA or screenshots when applicable

Include the exact command names whenever known.

## 11. Risks / Blockers

Describe:
- operational risk
- data risk
- auth or credentials risk
- rollout risk
- unresolved blockers

## 12. Deliverables

List the expected artifacts:
- code files
- migrations
- docs
- tests
- reports
- screenshots
- dashboards
- example data

## 13. Completion note

At the end of the work, summarize:
- what shipped
- what did not ship
- what remains as follow-up
- where the validation evidence lives

---

## Plan-writing rules

- Write for execution, not discussion.
- Avoid vague phrases like “improve architecture” without naming the exact change.
- If a library or framework is a key dependency, state how to validate the integration.
- If the task contains real uncertainty, include a proof-of-concept milestone before full buildout.
- Plans are living documents. Update them as work progresses.

## Plan-execution rules for Codex

When implementing from a plan:

1. Read the whole plan before editing code.
2. If the plan is incomplete, improve the plan first.
3. Follow milestones in order unless the plan explicitly allows parallel work.
4. Update `Progress`, `Research notes`, `Surprises & Discoveries`, and `Decision log` as you go.
5. Do not mark the work complete without validation evidence.
6. Leave the repo in a runnable and reviewable state at every pause point.
