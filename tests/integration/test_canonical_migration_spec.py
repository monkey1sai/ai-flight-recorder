from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UP_SQL = ROOT / "packages" / "schema" / "migrations" / "0001_canonical_schema.up.sql"
DOWN_SQL = ROOT / "packages" / "schema" / "migrations" / "0001_canonical_schema.down.sql"


def test_up_migration_contains_required_entities() -> None:
    sql = UP_SQL.read_text(encoding="utf-8")

    required_tables = [
        "CREATE TABLE sessions",
        "CREATE TABLE traces",
        "CREATE TABLE steps",
        "CREATE TABLE observations",
        "CREATE TABLE state_deltas",
        "CREATE TABLE artifacts",
        "CREATE TABLE evidence_edges",
        "CREATE TABLE claims",
        "CREATE TABLE explanation_records",
        "CREATE TABLE evaluations",
        "CREATE TABLE interventions",
    ]
    required_types = [
        "CREATE TYPE evidence_grade AS ENUM",
        "CREATE TYPE claim_verification_status AS ENUM",
        "CREATE TYPE entity_kind AS ENUM",
    ]

    for token in required_tables + required_types:
        assert token in sql


def test_down_migration_reverses_all_created_tables() -> None:
    sql = DOWN_SQL.read_text(encoding="utf-8")

    for token in [
        "DROP TABLE IF EXISTS interventions;",
        "DROP TABLE IF EXISTS evaluations;",
        "DROP TABLE IF EXISTS explanation_records;",
        "DROP TABLE IF EXISTS evidence_edges;",
        "DROP TABLE IF EXISTS claims;",
        "DROP TABLE IF EXISTS state_deltas;",
        "DROP TABLE IF EXISTS observations;",
        "DROP TABLE IF EXISTS artifacts;",
        "DROP TABLE IF EXISTS steps;",
        "DROP TABLE IF EXISTS traces;",
        "DROP TABLE IF EXISTS sessions;",
    ]:
        assert token in sql

