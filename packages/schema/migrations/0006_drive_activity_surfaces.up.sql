BEGIN;

CREATE TABLE research_drive_activity_events (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL,
    primary_action TEXT NOT NULL,
    actors JSONB NOT NULL DEFAULT '[]'::JSONB,
    targets JSONB NOT NULL DEFAULT '[]'::JSONB,
    raw_ref TEXT,
    metadata_json JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_research_drive_activity_source_time
    ON research_drive_activity_events (source_id, occurred_at DESC);

COMMIT;
