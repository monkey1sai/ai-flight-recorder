# Repository contract for Codex

## Mission

Build and maintain an **AI / Agent / LLM observability platform** that helps humans understand:

- what the system did
- what state changed
- what tools and documents affected the result
- why the final output was produced
- what parts of the explanation are observed, inferred, self-reported, or verified

The canonical product specification is in `COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md`.

## Mandatory read order

Before doing non-trivial work, read these files in order:

1. `AGENTS.md`
2. `COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md`
3. `.agent/PLANS.md`
4. the newest relevant plan in `plans/active/`
5. supporting docs in `docs/`

If these sources conflict, prefer the closest task-specific plan, then this file, then the main guide.

## When a plan is required

Create or update an ExecPlan in `plans/active/` when any of the following is true:

- the task spans multiple files or subsystems
- the task will likely take longer than 30 minutes
- the task changes architecture, storage, APIs, schemas, security, or tests
- the task includes external research
- the task introduces a connector, worker, or migration
- the task has unclear feasibility and needs a proof of concept

For tiny edits, bugfixes, or typo changes, a full plan is optional.

## Working style

- Humans steer. Agents execute.
- Treat repository docs as the system of record.
- Keep code, docs, tests, and validation notes in sync.
- Prefer small, reviewable diffs.
- Do not perform unrelated refactors.
- Resolve local ambiguities autonomously and record the decision in the active plan.
- If a task is blocked by missing credentials, unavailable infrastructure, or incompatible requirements, stop, document the blocker clearly, and leave the repo in a valid state.

## Product rules

- Never claim direct access to a hidden chain-of-thought or internal consciousness.
- Model explanations must be separated into these evidence grades:
  - `observed`
  - `self_reported`
  - `inferred`
  - `verified`
- Preserve provenance. Do not collapse evidence into opaque text summaries.
- Use append-only event history for execution records.
- Prefer typed boundaries and explicit schemas.
- Never guess external API shapes when a schema, SDK, or sample payload is available.
- For Google Drive and arXiv ingestion, retain source IDs, timestamps, and provenance metadata.

## Repository knowledge rules

- Architecture notes belong in `docs/`.
- Active implementation plans belong in `plans/active/`.
- Completed plans move to `plans/done/`.
- Validation reports belong in `reports/validation/`.
- If a change affects behavior, update docs in the same change.
- If a change introduces a new recurring workflow, add or update a skill in `.agents/skills/` only when the task explicitly targets workflow infrastructure.

## Default implementation contract

If the repo does not yet provide these commands, bootstrap them first:

- `make setup`
- `make lint`
- `make typecheck`
- `make unit`
- `make integration`
- `make smoke`
- `make test`
- `make validate`

Preferred meaning:

- `make setup`: install all dependencies and developer tooling
- `make lint`: static style checks
- `make typecheck`: type and schema checks
- `make unit`: fast deterministic tests
- `make integration`: service and connector integration tests
- `make smoke`: minimal end-to-end verification
- `make test`: aggregate local test target
- `make validate`: full gate used before merge

## Validation requirements for every meaningful change

Before declaring work done, do all applicable items:

1. run the narrowest relevant tests first
2. run `make lint`
3. run `make typecheck`
4. run `make test` or the smallest valid subset
5. update the active ExecPlan
6. write or update a validation note in `reports/validation/` for major work
7. document any remaining risk, gap, or follow-up item

## Research rules

For tasks involving external knowledge:

- prefer official documentation first
- prefer current information over memory
- record source, retrieval date, and why it matters
- add findings to a research note if the information will be reused
- respect product and API terms, rate limits, and copyright constraints

Use the `$research-evidence` skill when the task depends on current docs, papers, Google Drive search patterns, arXiv metadata, or policy-sensitive external data.

## Implementation rules

When asked to implement from a plan:

- use the `$implement-execplan` skill
- implement one milestone at a time
- keep the plan updated after each milestone
- do not ask for “next steps” if the current plan already defines them
- stop after a safe checkpoint if you encounter a hard blocker

## Release / QA rules

When asked to validate, audit, or prepare a release:

- use the `$validate-release` skill
- produce a concrete validation report
- separate confirmed facts from assumptions
- include reproduction commands
- include failing cases if any remain

## File placement conventions

- main guide: `COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md`
- recurring docs: `docs/`
- active plans: `plans/active/`
- completed plans: `plans/done/`
- validation reports: `reports/validation/`
- repo skills: `.agents/skills/`
- project Codex config: `.codex/config.toml`

## Initial implementation priorities

Unless a task explicitly says otherwise, prioritize work in this order:

1. repo bootstrap and developer contract
2. canonical schema and storage
3. ingestion API and event capture
4. web UI shell and timeline
5. evidence graph and state diff
6. research connectors
7. why engine
8. replay, evals, and production hardening
