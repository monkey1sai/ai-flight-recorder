import { TraceTimeline } from "../../components/trace-timeline";
import { getTimelineEntries, listTraceSummaries } from "../../lib/api";

export default async function TimelinePage() {
  const summaries = await listTraceSummaries();
  const summary = summaries[0];
  const entries = summary ? await getTimelineEntries(summary.traceId) : [];

  return (
    <main className="page-shell stack-page">
      <section className="section-copy">
        <h1>Timeline</h1>
        <p>
          This view maps each step to its evidence grade, artifact count, claim linkage, and
          intervention count. It prefers the live `/api/v1/traces/:traceId/timeline` surface and
          falls back to fixture data when the API is unavailable.
        </p>
      </section>
      <section className="metric-strip">
        <article className="panel">
          <strong>{summary?.stepCount ?? 0}</strong>
          <span>steps</span>
        </article>
        <article className="panel">
          <strong>{summary?.claimCount ?? 0}</strong>
          <span>claims</span>
        </article>
        <article className="panel">
          <strong>{summary?.policyFlags ?? 0}</strong>
          <span>policy flags</span>
        </article>
      </section>
      <TraceTimeline entries={entries} />
    </main>
  );
}
