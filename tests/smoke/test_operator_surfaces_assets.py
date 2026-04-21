from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_operator_surface_assets_exist() -> None:
    required_paths = [
        ROOT / "plans" / "active" / "20260417-platform-slices-3-10.md",
        ROOT / "plans" / "active" / "20260421-mvp-phase-1-7-execution.md",
        ROOT / "apps" / "api" / "app" / "routers" / "query.py",
        ROOT / "apps" / "api" / "app" / "settings.py",
        ROOT / "apps" / "api" / "app" / "bootstrap.py",
        ROOT / "apps" / "api" / "app" / "why.py",
        ROOT / "apps" / "api" / "app" / "routers" / "research.py",
        ROOT / "apps" / "web" / "app" / "timeline" / "page.tsx",
        ROOT / "apps" / "web" / "app" / "traces" / "[traceId]" / "page.tsx",
        ROOT / "apps" / "web" / "components" / "task-summary-panel.tsx",
        ROOT / "apps" / "web" / "components" / "plan-history-panel.tsx",
        ROOT / "apps" / "web" / "app" / "admin" / "page.tsx",
        ROOT / "apps" / "web" / "lib" / "api.ts",
        ROOT / "edge" / "daemon" / "Cargo.toml",
        ROOT / "packages" / "edge_sdk" / "client.py",
        ROOT / "packages" / "schema" / "migrations" / "0002_governance_surfaces.up.sql",
        ROOT / "packages" / "schema" / "migrations" / "0003_cognitive_state_surfaces.up.sql",
        ROOT / "workers" / "drive_sync" / "job.py",
        ROOT / "workers" / "arxiv_sync" / "job.py",
        ROOT / "infra" / "compose" / "docker-compose.yml",
        ROOT / "infra" / "k8s" / "api-deployment.yaml",
        ROOT / "scripts" / "bootstrap_local.py",
        ROOT / "scripts" / "emit_demo_trace.py",
        ROOT / "reports" / "validation" / "20260417-platform-slices-3-10.md",
        ROOT / "reports" / "validation" / "20260421-mvp-live-local-baseline.md",
    ]

    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]

    assert missing == []
