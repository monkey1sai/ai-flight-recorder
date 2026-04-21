BEGIN;

CREATE TABLE research_sync_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_type TEXT NOT NULL,
    query TEXT NOT NULL DEFAULT '',
    cursor TEXT,
    status TEXT NOT NULL,
    item_count INTEGER NOT NULL DEFAULT 0 CHECK (item_count >= 0),
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    metadata_json JSONB NOT NULL DEFAULT '{}'::JSONB
);

CREATE TABLE research_sync_cursors (
    source_type TEXT NOT NULL,
    cursor_key TEXT NOT NULL,
    cursor_value TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata_json JSONB NOT NULL DEFAULT '{}'::JSONB,
    PRIMARY KEY (source_type, cursor_key)
);

CREATE TABLE research_documents (
    id TEXT PRIMARY KEY,
    source_type TEXT NOT NULL,
    source_id TEXT NOT NULL,
    source_uri TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    authors JSONB NOT NULL DEFAULT '[]'::JSONB,
    published_at TIMESTAMPTZ,
    mime_type TEXT,
    content_ref TEXT,
    tags JSONB NOT NULL DEFAULT '[]'::JSONB,
    retrieved_at TIMESTAMPTZ NOT NULL,
    query TEXT NOT NULL DEFAULT '',
    cursor TEXT,
    license_or_terms_note TEXT,
    checksum TEXT,
    export_status TEXT,
    sync_run_id UUID REFERENCES research_sync_runs(id) ON DELETE SET NULL,
    metadata_json JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_research_documents_source_type ON research_documents (source_type);
CREATE INDEX idx_research_documents_query ON research_documents (query);
CREATE INDEX idx_research_documents_retrieved_at ON research_documents (retrieved_at DESC);
CREATE INDEX idx_research_documents_sync_run_id ON research_documents (sync_run_id);
CREATE INDEX idx_research_sync_runs_source_started ON research_sync_runs (source_type, started_at DESC);

COMMIT;
