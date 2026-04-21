from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_operator_surface_assets_exist() -> None:
    required_paths = [
        ROOT / "plans" / "active" / "20260417-platform-slices-3-10.md",
        ROOT / "apps" / "api" / "app" / "routers" / "query.py",
        ROOT / "apps" / "api" / "app" / "routers" / "research.py",
        ROOT / "apps" / "web" / "app" / "timeline" / "page.tsx",
        ROOT / "apps" / "web" / "app" / "traces" / "[traceId]" / "page.tsx",
        ROOT / "apps" / "web" / "app" / "admin" / "page.tsx",
        ROOT / "edge" / "daemon" / "Cargo.toml",
        ROOT / "workers" / "drive_sync" / "job.py",
        ROOT / "workers" / "arxiv_sync" / "job.py",
        ROOT / "infra" / "compose" / "docker-compose.yml",
        ROOT / "infra" / "k8s" / "api-deployment.yaml",
        ROOT / "reports" / "validation" / "20260417-platform-slices-3-10.md",
    ]

    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]

    assert missing == []
