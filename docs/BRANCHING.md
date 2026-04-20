# Branching

## Branch Roles

- `main`
  受保護主線，只接受已審查、已驗證的小 PR。
- 短期功能 / 修補分支
  使用 `feat/`, `fix/`, `chore/`, `docs/`, `ops/` 前綴。
- Codex 執行分支
  建議使用 `codex/YYYYMMDD-short-slug` 或 `codex/<topic>`。

## Rules

- 一個 branch 對應一個主要目標。
- 不要在同一 branch 混入 unrelated work。
- 發現 branch 已包含大量不相干變更時，先停下來切出新 branch，不要硬疊。
- 未經明確要求，不做 force push 或 history rewrite。

## Suggested Naming

- `feat/timeline-claim-filter`
- `fix/replay-state-diff-null-guard`
- `docs/governance-baseline`
- `ops/ci-python-node-rust`
- `codex/20260420-governance-baseline`

## Merge Expectations

- PR 應保持小且容易 review。
- 若某工作需要多個階段，請拆成多個 branch / PR，而不是一個超大 PR。
