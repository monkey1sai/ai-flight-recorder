#!/usr/bin/env bash

set -u

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${repo_root}"

export UV_CACHE_DIR="${repo_root}/.uv-cache"
export CARGO_HOME="${repo_root}/.cargo-home"
export RUSTUP_HOME="${repo_root}/.rustup-home"
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1

failed=()
skipped=()
passed=0

docker_compose_tool=()
if command -v docker-compose >/dev/null 2>&1; then
  docker_compose_tool=(docker-compose)
elif command -v docker >/dev/null 2>&1; then
  docker_compose_tool=(docker compose)
fi

run_step() {
  local label="$1"
  local tool="$2"
  shift 2

  if ! command -v "${tool}" >/dev/null 2>&1; then
    echo "[SKIP] ${label}: missing executable '${tool}'"
    skipped+=("${label}")
    return 0
  fi

  echo "[RUN ] ${label}: ${tool} $*"
  if "${tool}" "$@"; then
    echo "[PASS] ${label}"
    passed=$((passed + 1))
  else
    echo "[FAIL] ${label}"
    failed+=("${label}")
  fi
}

run_step "Ruff" uv run ruff check .
run_step "Mypy" uv run mypy apps packages workers tests
run_step "Pytest unit" uv run python -m pytest tests/unit -q -p no:cacheprovider
run_step "Pytest integration" uv run python -m pytest tests/integration -q -p no:cacheprovider
run_step "Pytest e2e" uv run python -m pytest tests/e2e -q -p no:cacheprovider
run_step "Pytest smoke" uv run python -m pytest tests/smoke -q -p no:cacheprovider
run_step "Web lint" npm run lint --workspace @aeris/web
run_step "Web typecheck" npm run typecheck --workspace @aeris/web
run_step "Cargo check" cargo check --manifest-path edge/daemon/Cargo.toml
if ((${#docker_compose_tool[@]} == 0)); then
  echo "[SKIP] Docker compose config: missing executable 'docker-compose' or 'docker compose'"
  skipped+=("Docker compose config")
else
  run_step "Docker compose config" "${docker_compose_tool[0]}" "${docker_compose_tool[@]:1}" -f infra/compose/docker-compose.yml config
fi

echo
echo "Summary"
echo "Passed: ${passed}"
echo "Failed: ${#failed[@]}"
echo "Skipped: ${#skipped[@]}"

if ((${#failed[@]} > 0)); then
  exit 1
fi

exit 0
