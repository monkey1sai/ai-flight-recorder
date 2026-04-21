from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_canonical_schema_assets_exist() -> None:
    required_paths = [
        ROOT / "plans" / "active" / "20260417-canonical-schema-migrations.md",
        ROOT / "packages" / "schema" / "migrations" / "0001_canonical_schema.up.sql",
        ROOT / "packages" / "schema" / "migrations" / "0001_canonical_schema.down.sql",
        ROOT / "packages" / "schema" / "flight_recorder_schema" / "canonical.py",
        ROOT / "tests" / "fixtures" / "canonical_trace_fixture.json",
        ROOT / "docs" / "architecture" / "canonical-schema.md",
        ROOT / "reports" / "validation" / "20260417-canonical-schema-migrations.md",
    ]

    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]

    assert missing == []

