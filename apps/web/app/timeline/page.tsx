import { TraceTimeline } from "../../components/trace-timeline";
import { timelineEntries, traceSummaries } from "../../lib/mock-data";

export default function TimelinePage() {
  const summary = traceSummaries[0];

  return (
    <main className="page-shell stack-page">
      <section className="section-copy">
        <h1>Timeline</h1>
        <p>
          This view maps each step to its evidence grade, artifact count, claim linkage, and
          intervention count. It is designed to mirror the `/api/v1/traces/{summary.traceId}/timeline`
          surface.
        </p>
      </section>
      <section className="metric-strip">
        <article className="panel">
          <strong>{summary.stepCount}</strong>
          <span>steps</span>
        </article>
        <article className="panel">
          <strong>{summary.claimCount}</strong>
          <span>claims</span>
        </article>
        <article className="panel">
          <strong>{summary.policyFlags}</strong>
          <span>policy flags</span>
        </article>
      </section>
      <TraceTimeline entries={timelineEntries} />
    </main>
  );
}
