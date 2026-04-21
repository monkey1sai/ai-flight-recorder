import type { PlanVersionRecord } from "../lib/mock-data";

export function PlanHistoryPanel({ plans }: { plans: PlanVersionRecord[] }) {
  return (
    <div className="diff-grid">
      {plans.map((plan) => (
        <article className="panel" key={plan.id}>
          <div className="panel-header">
            <strong>Revision {plan.revision}</strong>
            <span>{plan.step_id?.slice(0, 8) ?? "manual"}</span>
          </div>
          <p>{plan.summary ?? "No plan summary was captured."}</p>
          <pre>{JSON.stringify(plan.plan_json, null, 2)}</pre>
        </article>
      ))}
    </div>
  );
}
