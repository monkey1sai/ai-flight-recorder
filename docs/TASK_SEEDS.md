# Task seeds for Codex

These prompts are intended to reduce setup friction. Adapt paths and file names if your repo differs.

## 1. Inspect instruction sources

```bash
codex --ask-for-approval never "Summarize the active instruction files, then explain the repository contract in 12 bullets."
```

## 2. Bootstrap the repository contract

```bash
codex exec --json --full-auto "Read AGENTS.md, COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md, and .agent/PLANS.md. Create plans/active/$(date +%Y%m%d)-bootstrap-monorepo.md and execute Milestone 0 bootstrap. Create the smallest usable monorepo skeleton, Makefile targets, lint/typecheck/test wiring, and validation report."
```

## 3. Research current implementation constraints

```bash
codex --profile research_live --search "Use the $research-evidence skill. Gather official current guidance for Codex operating model, Google Drive search/export/change tracking, arXiv API and OAI-PMH, and OpenTelemetry GenAI spans. Save the evidence note under docs/ with implementation consequences for this repository."
```

## 4. Build the canonical schema first

```bash
codex exec --json --full-auto "Use the $implement-execplan skill. Create and execute a plan for the canonical observability schema: Session, Trace, Step, Observation, StateDelta, Artifact, EvidenceEdge, Claim, ExplanationRecord, Evaluation, Intervention. Add migrations, model tests, and sample fixtures."
```

## 5. Implement the ingestion API

```bash
codex exec --json --full-auto "Use the active ExecPlan or create one if missing. Implement the ingestion API for trace events and artifacts, add request validation, persistence, and tests. Do not build the UI yet beyond a minimal health/status endpoint."
```

## 6. Implement Google Drive read-only connector

```bash
codex exec --json --full-auto "Create a plan and implement a read-only Google Drive connector that supports files.list search, Google Docs export when allowed, Drive change tracking, and activity enrichment. Store provenance metadata. Use mocks or fixtures for tests unless real credentials are explicitly provided."
```

## 7. Implement arXiv connector

```bash
codex exec --json --full-auto "Create a plan and implement an arXiv metadata connector with real-time search, paging, polite delays for repeated calls, and optional daily-harvest mode abstraction. Persist metadata only. Add source attribution fields and tests."
```

## 8. Build the operator UI shell

```bash
codex exec --json --full-auto "Create a plan for the first operator UI. Build a minimal timeline view, run detail page, evidence panel, and state-diff placeholder. Use fixture data first. Add UI tests and screenshots if the repo supports them."
```

## 9. Add the Why Engine

```bash
codex exec --json --full-auto "Create or update the plan for the Why Engine. Implement claim extraction, evidence linking, explanation grades (observed/self_reported/inferred/verified), and the first why-panel API. Add tests that prove unsupported claims are marked clearly."
```

## 10. Validate a milestone read-only

```bash
codex exec --json --sandbox read-only --ask-for-approval never "Use the $validate-release skill. Audit the repository against docs/ACCEPTANCE_CHECKLIST.md and the newest active plan. Write a validation report and return a readiness verdict."
```
