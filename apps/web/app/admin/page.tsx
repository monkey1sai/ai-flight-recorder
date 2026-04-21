import { GovernancePanel } from "../../components/governance-panel";
import { getGovernanceSnapshot } from "../../lib/api";

export default async function AdminPage() {
  const governanceSnapshot = await getGovernanceSnapshot();
  return (
    <main className="page-shell stack-page">
      <section className="section-copy">
        <h1>Admin / Governance</h1>
        <p>
          Audit, policy, and retention live next to trace review instead of being added after the
          fact. This page mirrors the live `/api/v1/admin/snapshot` surface with a local fallback.
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
