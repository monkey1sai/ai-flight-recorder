import Link from "next/link";

import type { ClaimFlow, TimelineEntry } from "../lib/mock-data";
import {
  getClaimFlows,
  getGovernanceSnapshot,
  getResearchCatalog,
  getTimelineEntries,
  listTraceSummaries,
} from "../lib/api";

export default async function Home() {
  const traceSummaries = await listTraceSummaries();
  const summary = traceSummaries[0];
  const [researchCatalog, governanceSnapshot, timelineEntries, claimFlows] = await Promise.all([
    getResearchCatalog(),
    getGovernanceSnapshot(summary?.traceId),
    summary ? getTimelineEntries(summary.traceId) : Promise.resolve<TimelineEntry[]>([]),
    summary ? getClaimFlows(summary.traceId) : Promise.resolve<ClaimFlow[]>([]),
  ]);

  return (
    <main className="page-shell">
      <section className="hero">
        <strong>Operator Slice</strong>
        <h1>AERIS Flight Recorder</h1>
        <p>
          目前 repo 已經從 bootstrap 與 canonical schema 推進到第一個 operator-facing
          vertical slice：FastAPI ingest/query/replay/research/admin API、Rust edge daemon
          skeleton、Drive / arXiv fixture connector、timeline / trace detail / replay /
          governance 畫面，以及 e2e 與 deployment manifests。
        </p>
        <div className="hero-actions">
          <Link className="action-pill" href="/timeline">
            Open timeline
          </Link>
          <Link
            className="action-pill secondary"
            href={summary ? `/traces/${summary.traceId}` : "/timeline"}
          >
            Inspect trace
          </Link>
        </div>
        <div className="hero-grid">
          <div className="hero-card">
            <strong>Trace</strong>
            <span>{summary?.stepCount ?? 0} steps with {summary?.claimCount ?? 0} claims and {summary?.policyFlags ?? 0} policy flags.</span>
          </div>
          <div className="hero-card">
            <strong>Research</strong>
            <span>{researchCatalog.drive.items.length + researchCatalog.arxiv.items.length} provenance-backed sources are available in fixture mode.</span>
          </div>
          <div className="hero-card">
            <strong>Governance</strong>
            <span>{governanceSnapshot.auditEvents.length} audit events and {governanceSnapshot.policies.length} policy rules are already modeled.</span>
          </div>
        </div>
      </section>

      <section className="section-copy">
        <h2>What This Slice Covers</h2>
        <p>
          Home 不再只是概念說明，而是把目前 operator workflow 的關鍵入口對齊到同一個
          fixture-backed contract。這一輪的焦點，是讓 timeline、claim/evidence flow、replay、
          connector provenance、governance 和 deployment 邊界同時存在。
        </p>
      </section>

      <section className="section-grid" aria-label="Evidence grades">
        {timelineEntries.map((entry) => (
          <article className="grade-card" key={entry.step.id}>
            <strong>{entry.step.step_type}</strong>
            <span>{entry.step.summary}</span>
          </article>
        ))}
      </section>

      <section className="section-copy">
        <h2>Claim / Evidence Flow</h2>
        <p>
          why engine 的第一個 UI contract 已經具備：claim verification status、supporting
          artifacts、explanation grade 與 replay/step linkage 會被分開呈現。
        </p>
      </section>

      <section className="section-grid" aria-label="Bootstrap milestones">
        {claimFlows.map((flow) => (
          <article className="grade-card" key={flow.claim.id}>
            <strong>{flow.claim.verification_status}</strong>
            <span>{flow.claim.claim_text}</span>
          </article>
        ))}
      </section>
    </main>
  );
}
