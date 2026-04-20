import { notFound } from "next/navigation";

import { StateDiffPanel } from "../../../components/state-diff-panel";
import { TraceTimeline } from "../../../components/trace-timeline";
import { WhyPanel } from "../../../components/why-panel";
import {
  claimFlows,
  getTraceBundleById,
  stateDiffs,
  timelineEntries,
} from "../../../lib/mock-data";

export default function TraceDetailPage({
  params,
}: {
  params: { traceId: string };
}) {
  const { traceId } = params;
  const bundle = getTraceBundleById(traceId);

  if (!bundle) {
    notFound();
  }

  return (
    <main className="page-shell stack-page">
      <section className="section-copy">
        <h1>Trace Detail</h1>
        <p>
          Trace `{bundle.trace.id}` captures the operator slice end-to-end: plan update, Drive
          search, arXiv search, and response synthesis. This page mirrors the API detail,
          state-diff, and claim-evidence surfaces.
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
