from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_bootstrap_skeleton_exists() -> None:
    required_paths = [
        ROOT / "Makefile",
        ROOT / "package.json",
        ROOT / "pyproject.toml",
        ROOT / "apps" / "api" / "app" / "main.py",
        ROOT / "apps" / "web" / "app" / "page.tsx",
        ROOT / "packages" / "schema" / "flight_recorder_schema" / "events.py",
        ROOT / "workers" / "drive_sync" / "README.md",
        ROOT / "plans" / "active" / "20260417-bootstrap-monorepo.md",
    ]

    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]

    assert missing == []


def test_makefile_exposes_required_targets() -> None:
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

    for target in [
        "setup:",
        "lint:",
        "typecheck:",
        "unit:",
        "integration:",
        "e2e:",
        "smoke:",
        "test:",
        "validate:",
    ]:
        assert target in makefile
