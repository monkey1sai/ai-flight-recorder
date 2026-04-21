import type { TaskState } from "../lib/mock-data";

export function TaskSummaryPanel({ taskState }: { taskState?: TaskState }) {
  if (!taskState) {
    return (
      <article className="panel">
        <div className="panel-header">
          <strong>Task</strong>
          <span>unavailable</span>
        </div>
        <p className="muted-line">No cognitive task state was recorded for this trace.</p>
      </article>
    );
  }

  const { task, latestPlan, latestSnapshot, planRevisionCount, snapshotCount } = taskState;

  return (
    <article className="panel">
      <div className="panel-header">
        <strong>{task.title}</strong>
        <span className="badge">{task.status}</span>
      </div>
      <p>{task.summary ?? "No task summary was captured."}</p>
      <div className="chip-row">
        <span className="chip">{planRevisionCount} plan revisions</span>
        <span className="chip">{snapshotCount} state snapshots</span>
        {task.owner ? <span className="chip">{task.owner}</span> : null}
      </div>
      {latestPlan ? (
        <div className="json-columns">
          <div>
            <span className="eyebrow">Latest Plan</span>
            <pre>{JSON.stringify(latestPlan.plan_json, null, 2)}</pre>
          </div>
          <div>
            <span className="eyebrow">Latest Snapshot</span>
            <pre>{JSON.stringify(latestSnapshot?.state_json ?? {}, null, 2)}</pre>
          </div>
        </div>
      ) : null}
    </article>
  );
}
