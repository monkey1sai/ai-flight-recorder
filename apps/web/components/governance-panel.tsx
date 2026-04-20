import type {
  AuditEventRecord,
  PolicyRuleRecord,
  RetentionPolicyRecord,
} from "../lib/mock-data";

export function GovernancePanel({
  auditEvents,
  policies,
  retention,
}: {
  auditEvents: AuditEventRecord[];
  policies: PolicyRuleRecord[];
  retention: RetentionPolicyRecord[];
}) {
  return (
    <div className="admin-grid">
      <section className="panel">
        <div className="panel-header">
          <strong>Audit Trail</strong>
          <span>{auditEvents.length} events</span>
        </div>
        <ul className="plain-list">
          {auditEvents.map((event) => (
            <li key={event.id}>
              <strong>{event.event_type}</strong>
              <span>
                {event.actor} · {event.outcome} · {event.occurred_at}
              </span>
            </li>
          ))}
        </ul>
      </section>
      <section className="panel">
        <div className="panel-header">
          <strong>Policy Rules</strong>
          <span>{policies.length} rules</span>
        </div>
        <ul className="plain-list">
          {policies.map((policy) => (
            <li key={policy.id}>
              <strong>{policy.name}</strong>
              <span>
                {policy.mode} · {policy.applies_to.join(", ")}
              </span>
            </li>
          ))}
        </ul>
      </section>
      <section className="panel">
        <div className="panel-header">
          <strong>Retention</strong>
          <span>{retention.length} policies</span>
        </div>
        <ul className="plain-list">
          {retention.map((policy) => (
            <li key={policy.id}>
              <strong>{policy.name}</strong>
              <span>
                {policy.retention_days} days · {policy.purge_strategy}
              </span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
