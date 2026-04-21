import type { StateDeltaRecord } from "../lib/mock-data";

export function StateDiffPanel({ diffs }: { diffs: StateDeltaRecord[] }) {
  return (
    <div className="diff-grid">
      {diffs.map((diff) => (
        <article className="panel" key={diff.id}>
          <div className="panel-header">
            <strong>{diff.facet}</strong>
            <span>{diff.step_id.slice(0, 8)}</span>
          </div>
          <div className="json-columns">
            <div>
              <span className="eyebrow">Before</span>
              <pre>{JSON.stringify(diff.before_json ?? {}, null, 2)}</pre>
            </div>
            <div>
              <span className="eyebrow">After</span>
              <pre>{JSON.stringify(diff.after_json ?? {}, null, 2)}</pre>
            </div>
          </div>
        </article>
      ))}
    </div>
  );
}
