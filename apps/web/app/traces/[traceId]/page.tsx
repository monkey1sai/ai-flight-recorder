import { notFound } from "next/navigation";

import { StateDiffPanel } from "../../../components/state-diff-panel";
import { TraceTimeline } from "../../../components/trace-timeline";
import { WhyPanel } from "../../../components/why-panel";
import {
  getClaimFlows,
  getStateDiffEntries,
  getTimelineEntries,
  getTraceBundle,
} from "../../../lib/api";

export default async function TraceDetailPage({
  params,
}: {
  params: Promise<{ traceId: string }>;
}) {
  const { traceId } = await params;
  const bundle = await getTraceBundle(traceId);

  if (!bundle) {
    notFound();
  }

  const [timelineEntries, stateDiffs, claimFlows] = await Promise.all([
    getTimelineEntries(traceId),
    getStateDiffEntries(traceId),
    getClaimFlows(traceId),
  ]);

  return (
    <main className="page-shell stack-page">
      <section className="section-copy">
        <h1>Trace Detail</h1>
        <p>
          Trace `{bundle.trace.id}` captures the operator slice end-to-end: timeline, state change,
          claim/evidence linkage, and final synthesis. This page reads live API detail, state-diff,
          and claim-evidence surfaces first, with fixture fallback for local browsing.
        </p>
      </section>
      <section className="stack-section">
        <div className="section-copy">
          <h2>Timeline</h2>
          <p>Every step keeps its evidence grade explicit; no claim is silently upgraded.</p>
        </div>
        <TraceTimeline entries={timelineEntries} />
      </section>
      <section className="stack-section">
        <div className="section-copy">
          <h2>State Diff</h2>
          <p>Plan, belief, and risk state changes are rendered as before/after JSON snapshots.</p>
        </div>
        <StateDiffPanel diffs={stateDiffs} />
      </section>
      <section className="stack-section">
        <div className="section-copy">
          <h2>Claim / Evidence Flow</h2>
          <p>Claim verification status, explanation grade, and supporting artifacts remain separated.</p>
        </div>
        <WhyPanel flows={claimFlows} />
      </section>
    </main>
  );
}
