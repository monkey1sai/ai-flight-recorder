import { GovernancePanel } from "../../components/governance-panel";
import { governanceSnapshot } from "../../lib/mock-data";

export default function AdminPage() {
  return (
    <main className="page-shell stack-page">
      <section className="section-copy">
        <h1>Admin / Governance</h1>
        <p>
          Audit, policy, and retention live next to trace review instead of being added after the
          fact. This page mirrors the `/api/v1/admin/snapshot` surface.
        </p>
      </section>
      <GovernancePanel
        auditEvents={governanceSnapshot.auditEvents}
        policies={governanceSnapshot.policies}
        retention={governanceSnapshot.retention}
      />
    </main>
  );
}
