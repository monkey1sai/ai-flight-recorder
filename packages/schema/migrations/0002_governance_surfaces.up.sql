create table if not exists audit_events (
    id uuid primary key default gen_random_uuid(),
    trace_id uuid null references traces(id) on delete set null,
    event_type text not null,
    actor text not null,
    outcome text not null,
    occurred_at timestamptz not null default now(),
    metadata_json jsonb not null default '{}'::jsonb
);

create table if not exists policy_rules (
    id uuid primary key default gen_random_uuid(),
    name text not null unique,
    category text not null,
    mode text not null,
    applies_to jsonb not null default '[]'::jsonb,
    description text not null,
    configured_by text not null,
    metadata_json jsonb not null default '{}'::jsonb
);

create table if not exists retention_policies (
    id uuid primary key default gen_random_uuid(),
    name text not null unique,
    applies_to jsonb not null default '[]'::jsonb,
    retention_days integer not null check (retention_days > 0),
    purge_strategy text not null,
    redaction_scope jsonb not null default '[]'::jsonb,
    metadata_json jsonb not null default '{}'::jsonb
);

create index if not exists idx_audit_events_trace_id on audit_events(trace_id);
create index if not exists idx_audit_events_occurred_at on audit_events(occurred_at);
