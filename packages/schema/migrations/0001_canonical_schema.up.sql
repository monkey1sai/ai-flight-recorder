BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TYPE evidence_grade AS ENUM (
    'observed',
    'self_reported',
    'inferred',
    'verified'
);

CREATE TYPE session_status AS ENUM (
    'queued',
    'running',
    'completed',
    'failed',
    'cancelled'
);

CREATE TYPE trace_status AS ENUM (
    'queued',
    'running',
    'completed',
    'failed',
    'cancelled'
);

CREATE TYPE step_status AS ENUM (
    'queued',
    'running',
    'completed',
    'failed',
    'cancelled',
    'skipped'
);

CREATE TYPE entity_kind AS ENUM (
    'trace',
    'step',
    'observation',
    'state_delta',
    'artifact',
    'claim',
    'explanation_record',
    'evaluation',
    'intervention'
);

CREATE TYPE claim_verification_status AS ENUM (
    'supported',
    'partially_supported',
    'unsupported',
    'model_prior_only',
    'conflicted'
);

CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source TEXT NOT NULL,
    user_id TEXT,
    project_id UUID,
    external_conversation_id TEXT,
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,
    status session_status NOT NULL DEFAULT 'queued',
    metadata_json JSONB NOT NULL DEFAULT '{}'::JSONB,
    labels_jsonb JSONB NOT NULL DEFAULT '[]'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (ended_at IS NULL OR ended_at >= started_at)
);

CREATE TABLE traces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    parent_trace_id UUID REFERENCES traces(id) ON DELETE SET NULL,
    task_id UUID,
    model_name TEXT,
    trace_kind TEXT NOT NULL DEFAULT 'agent_run',
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,
    status trace_status NOT NULL DEFAULT 'queued',
    config_ref TEXT,
    metadata_json JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (ended_at IS NULL OR ended_at >= started_at)
);

CREATE TABLE steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trace_id UUID NOT NULL REFERENCES traces(id) ON DELETE CASCADE,
    parent_step_id UUID REFERENCES steps(id) ON DELETE SET NULL,
    step_index INTEGER NOT NULL CHECK (step_index >= 0),
    step_type TEXT NOT NULL,
    actor TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,
    status step_status NOT NULL DEFAULT 'queued',
    summary TEXT,
    metadata_json JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (trace_id, step_index),
    CHECK (ended_at IS NULL OR ended_at >= started_at)
);

CREATE TABLE artifacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_type TEXT NOT NULL,
    source_system TEXT,
    source_uri TEXT,
    mime_type TEXT,
    checksum TEXT,
    storage_ref TEXT,
    metadata_json JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE observations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    step_id UUID NOT NULL REFERENCES steps(id) ON DELETE CASCADE,
    kind TEXT NOT NULL,
    content_ref TEXT NOT NULL,
    confidence NUMERIC(5,4),
    source_artifact_id UUID REFERENCES artifacts(id) ON DELETE SET NULL,
    metadata_json JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1))
);

CREATE TABLE state_deltas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    step_id UUID NOT NULL REFERENCES steps(id) ON DELETE CASCADE,
    facet TEXT NOT NULL,
    before_json JSONB,
    after_json JSONB,
    metadata_json JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE claims (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trace_id UUID NOT NULL REFERENCES traces(id) ON DELETE CASCADE,
    claim_text TEXT NOT NULL,
    claim_type TEXT NOT NULL,
    confidence NUMERIC(5,4),
    position_index INTEGER NOT NULL CHECK (position_index >= 0),
    verification_status claim_verification_status NOT NULL DEFAULT 'unsupported',
    metadata_json JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (trace_id, position_index),
    CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1))
);

CREATE TABLE evidence_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_kind entity_kind NOT NULL,
    from_id UUID NOT NULL,
    to_kind entity_kind NOT NULL,
    to_id UUID NOT NULL,
    relation TEXT NOT NULL,
    weight NUMERIC(5,4),
    metadata_json JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (weight IS NULL OR (weight >= 0 AND weight <= 1))
);

CREATE TABLE explanation_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id UUID NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    grade evidence_grade NOT NULL,
    method TEXT NOT NULL,
    summary TEXT NOT NULL,
    supporting_edge_ids UUID[] NOT NULL DEFAULT '{}'::UUID[],
    confidence NUMERIC(5,4),
    metadata_json JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1))
);

CREATE TABLE evaluations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trace_id UUID NOT NULL REFERENCES traces(id) ON DELETE CASCADE,
    suite_name TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    score NUMERIC(10,4),
    verdict TEXT NOT NULL,
    details_json JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE interventions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trace_id UUID NOT NULL REFERENCES traces(id) ON DELETE CASCADE,
    step_id UUID REFERENCES steps(id) ON DELETE SET NULL,
    intervention_type TEXT NOT NULL,
    reason TEXT NOT NULL,
    actor TEXT NOT NULL,
    result TEXT NOT NULL,
    metadata_json JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sessions_started_at ON sessions (started_at DESC);
CREATE INDEX idx_traces_session_started_at ON traces (session_id, started_at DESC);
CREATE INDEX idx_traces_parent_trace_id ON traces (parent_trace_id);
CREATE INDEX idx_steps_trace_step_index ON steps (trace_id, step_index);
CREATE INDEX idx_steps_parent_step_id ON steps (parent_step_id);
CREATE INDEX idx_artifacts_source_uri ON artifacts (source_uri);
CREATE INDEX idx_observations_step_id ON observations (step_id);
CREATE INDEX idx_observations_source_artifact_id ON observations (source_artifact_id);
CREATE INDEX idx_state_deltas_step_id ON state_deltas (step_id);
CREATE INDEX idx_claims_trace_position ON claims (trace_id, position_index);
CREATE INDEX idx_claims_status ON claims (verification_status);
CREATE INDEX idx_evidence_edges_from ON evidence_edges (from_kind, from_id);
CREATE INDEX idx_evidence_edges_to ON evidence_edges (to_kind, to_id);
CREATE INDEX idx_explanation_records_claim_grade ON explanation_records (claim_id, grade);
CREATE INDEX idx_evaluations_trace_suite ON evaluations (trace_id, suite_name);
CREATE INDEX idx_interventions_trace_step ON interventions (trace_id, step_id);

COMMIT;

