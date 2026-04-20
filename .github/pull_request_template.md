## Summary

- What changed:
- Why this change is needed:

## Scope

- In scope:
- Out of scope:

## Validation

- [ ] `uv run ruff check .`
- [ ] `uv run mypy apps packages workers tests`
- [ ] `uv run python -m pytest tests/unit -q`
- [ ] `uv run python -m pytest tests/integration -q`
- [ ] `uv run python -m pytest tests/e2e -q`
- [ ] `uv run python -m pytest tests/smoke -q`
- [ ] `npm run lint --workspace @aeris/web`
- [ ] `npm run typecheck --workspace @aeris/web`
- [ ] `cargo check --manifest-path edge/daemon/Cargo.toml`
- [ ] `docker compose -f infra/compose/docker-compose.yml config`

## Docs And Plans

- [ ] Relevant docs updated
- [ ] Relevant `plans/active/` entry updated
- [ ] Validation or audit report added/updated when needed

## Risks

- Known risks:
- Follow-up items:

## Reviewer Checklist

- [ ] No secrets, tokens, or local machine credentials were added
- [ ] No generated directories or cache artifacts were intentionally staged
- [ ] The change stays within the stated scope
