import type { ClaimFlow } from "../lib/mock-data";

export function WhyPanel({ flows }: { flows: ClaimFlow[] }) {
  return (
    <div className="stack-grid">
      {flows.map((flow) => (
        <article className="panel claim-card" key={flow.claim.id}>
          <div className="panel-header">
            <strong>{flow.claim.claim_type}</strong>
            <span className={`badge claim-${flow.claim.verification_status}`}>
              {flow.claim.verification_status}
            </span>
          </div>
          <h3>{flow.claim.claim_text}</h3>
          <div className="chip-row">
            {flow.stepIds.map((stepId) => (
              <span className="chip" key={stepId}>
                step {stepId.slice(0, 8)}
              </span>
            ))}
          </div>
          <div className="subpanel">
            <span className="eyebrow">Explanations</span>
            <ul className="plain-list">
              {flow.explanations.map((explanation) => (
                <li key={explanation.id}>
                  <strong>{explanation.grade}</strong>
                  <span>{explanation.summary}</span>
                </li>
              ))}
            </ul>
          </div>
          <div className="subpanel">
            <span className="eyebrow">Artifacts</span>
            <ul className="plain-list">
              {flow.artifacts.map((artifact) => (
                <li key={artifact.id}>
                  <strong>{artifact.source_type}</strong>
                  <span>{artifact.source_uri ?? artifact.storage_ref ?? "unknown"}</span>
                </li>
              ))}
            </ul>
          </div>
        </article>
      ))}
    </div>
  );
}
