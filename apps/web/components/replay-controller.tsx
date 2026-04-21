import type { ReplayFrame, ReplayVerification } from "../lib/mock-data";

export function ReplayController({
  frames,
  verification,
}: {
  frames: ReplayFrame[];
  verification: ReplayVerification;
}) {
  return (
    <div className="stack-section">
      <article className="panel">
        <div className="panel-header">
          <strong>Verification</strong>
          <span className={`badge grade-${verification.verification_badge === "replay_verified" ? "verified" : "inferred"}`}>
            {verification.verification_badge}
          </span>
        </div>
        <div className="chip-row">
          <span className="chip">{verification.verified_claim_count} replay-backed claims</span>
          <span className="chip">{verification.claim_count} total claims</span>
          <span className="chip">confidence {formatConfidence(verification.confidence)}</span>
          <span className="chip">{verification.replay_run?.frame_count ?? frames.length} frames</span>
        </div>
        {verification.replay_trace_ids.length > 0 ? (
          <div className="chip-row">
            {verification.replay_trace_ids.map((traceId) => (
              <span className="chip" key={traceId}>
                replay {traceId.slice(0, 8)}
              </span>
            ))}
          </div>
        ) : null}
        <ul className="plain-list">
          {verification.verification_records.map((record) => (
            <li key={record.id}>
              <strong>{record.verification_status}</strong>
              <span>{record.claim_text}</span>
              <span className="muted-line">
                {record.method} · {record.verification_badge} · confidence {formatConfidence(record.confidence)}
              </span>
            </li>
          ))}
        </ul>
      </article>
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
    </div>
  );
}

function formatConfidence(confidence?: number) {
  return typeof confidence === "number" ? confidence.toFixed(2) : "n/a";
}
