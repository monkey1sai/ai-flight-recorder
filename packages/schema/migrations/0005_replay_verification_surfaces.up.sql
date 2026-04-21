create table if not exists replay_runs (
    id uuid primary key,
    trace_id uuid not null references traces(id) on delete cascade,
    status text not null,
    method text not null,
    frame_count integer not null default 0 check (frame_count >= 0),
    verified_claim_count integer not null default 0 check (verified_claim_count >= 0),
    started_at timestamptz not null default now(),
    completed_at timestamptz,
    metadata_json jsonb not null default '{}'::jsonb
);

create index if not exists idx_replay_runs_trace_started
    on replay_runs (trace_id, started_at desc);

create table if not exists verification_records (
    id uuid primary key,
    trace_id uuid not null references traces(id) on delete cascade,
    claim_id uuid not null references claims(id) on delete cascade,
    claim_text text not null,
    explanation_id uuid references explanation_records(id) on delete cascade,
    replay_run_id uuid references replay_runs(id) on delete set null,
    verification_status claim_verification_status not null,
    evidence_grade evidence_grade not null,
    verification_badge text not null,
    method text not null,
    summary text not null,
    confidence numeric(4, 3),
    replay_trace_id uuid,
    supporting_edge_ids uuid[] not null default array[]::uuid[],
    metadata_json jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create index if not exists idx_verification_records_trace_created
    on verification_records (trace_id, created_at desc);

create index if not exists idx_verification_records_claim_created
    on verification_records (claim_id, created_at desc);
