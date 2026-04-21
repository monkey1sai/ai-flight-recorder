BEGIN;

DROP TABLE IF EXISTS interventions;
DROP TABLE IF EXISTS evaluations;
DROP TABLE IF EXISTS explanation_records;
DROP TABLE IF EXISTS evidence_edges;
DROP TABLE IF EXISTS claims;
DROP TABLE IF EXISTS state_deltas;
DROP TABLE IF EXISTS observations;
DROP TABLE IF EXISTS artifacts;
DROP TABLE IF EXISTS steps;
DROP TABLE IF EXISTS traces;
DROP TABLE IF EXISTS sessions;

DROP TYPE IF EXISTS claim_verification_status;
DROP TYPE IF EXISTS entity_kind;
DROP TYPE IF EXISTS step_status;
DROP TYPE IF EXISTS trace_status;
DROP TYPE IF EXISTS session_status;
DROP TYPE IF EXISTS evidence_grade;

COMMIT;

