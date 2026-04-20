import type { ReplayFrame } from "../lib/mock-data";

export function ReplayController({ frames }: { frames: ReplayFrame[] }) {
  return (
    <div className="replay-list">
      {frames.map((frame) => (
        <article className="panel replay-frame" key={frame.step.id}>
          <div className="panel-header">
            <strong>
              Frame {frame.step.step_index + 1}: {frame.step.step_type}
            </strong>
            <span>{frame.step.actor}</span>
          </div>
          <p>{frame.step.summary ?? "No summary available."}</p>
          <div className="chip-row">
            <span className="chip">{frame.observations.length} observations</span>
            <span className="chip">{frame.stateDiffs.length} state diffs</span>
            <span className="chip">{frame.claims.length} claims</span>
            <span className="chip">{frame.interventions.length} interventions</span>
          </div>
        </article>
      ))}
    </div>
  );
}
