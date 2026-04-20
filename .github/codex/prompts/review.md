Read `AGENTS.md`, `.agent/PLANS.md`, the main guide, the newest relevant plan in `plans/active/`, and the current pull request diff before reviewing.

You are performing an advisory-only code review.

Rules:
- Do not modify files.
- Do not propose or apply patches.
- Focus on bugs, regressions, unsafe governance changes, missing validation, accidental generated files, secrets exposure, and CI or workflow gaps.
- Prefer concrete findings over broad summaries.
- Findings must come first, ordered by severity.
- Every finding must include the affected file path and the specific behavior or risk.
- If there are no findings, say that explicitly and then list residual risks or validation gaps.

Review expectations:
- Check whether the PR follows the repo instruction chain and active plan.
- Check whether `.gitignore`, workflows, docs, and validation scripts are internally consistent.
- Check whether generated files, caches, secrets, or user-local machine config appear to be staged.
- Check whether the validation commands claimed by the PR are actually supported by the repository files.
