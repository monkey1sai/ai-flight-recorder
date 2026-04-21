.PHONY: setup lint typecheck unit integration e2e smoke test test validate bootstrap-local emit-demo

setup:
	uv sync --group dev
	npm install --workspaces --include-workspace-root

lint:
	uv run ruff check .
	npm run lint --workspace @aeris/web

typecheck:
	node ./node_modules/pyright/index.js -p pyrightconfig.json --level error apps packages workers tests
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

bootstrap-local:
	uv run python scripts/bootstrap_local.py

emit-demo:
	uv run python scripts/emit_demo_trace.py
