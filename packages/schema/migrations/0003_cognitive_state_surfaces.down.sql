BEGIN;

ALTER TABLE traces
    DROP CONSTRAINT IF EXISTS traces_task_id_fkey;

DROP TABLE IF EXISTS state_snapshots;
DROP TABLE IF EXISTS plan_versions;
DROP TABLE IF EXISTS tasks;
DROP TYPE IF EXISTS task_status;

COMMIT;
