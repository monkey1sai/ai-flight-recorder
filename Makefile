.PHONY: setup lint typecheck unit integration e2e smoke test validate

setup:
	uv sync --group dev
	npm install --workspaces --include-workspace-root

lint:
	uv run ruff check .
	npm run lint --workspace @aeris/web

typecheck:
	uv run mypy apps packages workers tests
	cargo check --manifest-path edge/daemon/Cargo.toml
	npm run typecheck --workspace @aeris/web

unit:
	uv run python -m pytest tests/unit -q

integration:
	uv run python -m pytest tests/integration -q

e2e:
	uv run python -m pytest tests/e2e -q

smoke:
	uv run python -m pytest tests/smoke -q

test: unit integration e2e smoke

validate: lint typecheck test
