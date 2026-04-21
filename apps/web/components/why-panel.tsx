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
            <span className="chip">confidence {formatConfidence(flow.claim.confidence)}</span>
            {hasUnsupportedFlag(flow) ? (
              <span className="chip">unsupported evidence gap</span>
            ) : null}
          </div>
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
                  <span className="muted-line">
                    {explanation.method} · confidence {formatConfidence(explanation.confidence)}
                  </span>
                </li>
              ))}
            </ul>
          </div>
          <div className="subpanel">
            <span className="eyebrow">Evidence Links</span>
            <ul className="plain-list">
              {flow.edges.map((edge) => (
                <li key={edge.id}>
                  <strong>{edge.relation}</strong>
                  <span>
                    {edge.to_kind} {edge.to_id.slice(0, 8)}
                  </span>
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

function formatConfidence(confidence?: number) {
  return typeof confidence === "number" ? confidence.toFixed(2) : "n/a";
}

function hasUnsupportedFlag(flow: ClaimFlow) {
  return flow.claim.verification_status === "unsupported"
    || flow.claim.verification_status === "model_prior_only"
    || flow.explanations.some((item) => item.metadata_json?.unsupported_flag === true);
}
