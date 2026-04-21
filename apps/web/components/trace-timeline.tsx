import type { TimelineEntry } from "../lib/mock-data";

const gradeCopy: Record<string, string> = {
  observed: "Observed evidence",
  self_reported: "Model self-report",
  inferred: "Inferred support",
  verified: "Verified via replay",
};

export function TraceTimeline({ entries }: { entries: TimelineEntry[] }) {
  return (
    <div className="timeline-list">
      {entries.map((entry) => (
        <article className="timeline-item" key={entry.step.id}>
          <div className="timeline-rail">
            <span>{entry.step.step_index + 1}</span>
          </div>
          <div className="timeline-body">
            <div className="timeline-meta">
              <strong>{entry.step.step_type}</strong>
              <span>{entry.step.actor}</span>
              <span className={`badge grade-${entry.evidenceGrade}`}>
                {gradeCopy[entry.evidenceGrade]}
              </span>
            </div>
            <p>{entry.step.summary ?? "No summary provided."}</p>
            <div className="chip-row">
              <span className="chip">{entry.observationCount} observations</span>
              <span className="chip">{entry.artifactIds.length} artifacts</span>
              <span className="chip">{entry.claimIds.length} claims</span>
              <span className="chip">{entry.interventionIds.length} interventions</span>
            </div>
          </div>
        </article>
      ))}
    </div>
  );
}
