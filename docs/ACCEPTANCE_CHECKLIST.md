# Acceptance checklist

Use this checklist before moving a plan to `plans/done/`.

## A. Product correctness

- [ ] The feature solves a clearly stated user problem.
- [ ] User-visible behavior is documented.
- [ ] Evidence grades are explicit where explanations are shown.
- [ ] The implementation does not claim hidden chain-of-thought access.

## B. Code quality

- [ ] The diff is scoped to the task.
- [ ] Lint passes.
- [ ] Type checks pass.
- [ ] Narrow unit tests were added or updated.
- [ ] Integration tests were added or updated where relevant.
- [ ] No dead code or abandoned TODOs were left without an issue note.

## C. Data and provenance

- [ ] Primary IDs are stable and deterministic where required.
- [ ] Parent / child relationships are preserved.
- [ ] Timestamps are stored consistently.
- [ ] Source IDs, source URIs, and retrieval times are retained for external data.
- [ ] Raw payload references and normalized metadata are both handled correctly.

## D. Research connectors

### Google Drive
- [ ] Search queries are recorded or reproducible.
- [ ] Export size limits are handled.
- [ ] Change tracking is incremental.
- [ ] Activity fields are mapped when required.
- [ ] Tests use fixtures or mocks when live credentials are unavailable.

### arXiv
- [ ] Search and paging parameters are correct.
- [ ] Repeated requests are rate-limited politely.
- [ ] Metadata only is persisted by default.
- [ ] Source attribution is preserved.

## E. Security

- [ ] No unnecessary network or filesystem permissions were introduced.
- [ ] Secrets are not hard-coded.
- [ ] Prompt / user content redaction behavior is documented where telemetry is enabled.
- [ ] `.codex/` and `.agents/` were not modified unless the task explicitly required workflow infrastructure changes.

## F. Documentation

- [ ] The active ExecPlan is updated.
- [ ] Relevant docs were updated.
- [ ] A validation report exists for major work.
- [ ] Follow-up items are explicit.

## G. Release recommendation

Mark one:
- [ ] ready_to_merge
- [ ] merge_with_known_risks
- [ ] not_ready
