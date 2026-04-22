import { DriveLiveAcceptancePanel } from "../../components/drive-live-acceptance-panel";
import { ResearchCorpusPanel } from "../../components/research-corpus-panel";
import { ResearchSourceList } from "../../components/research-source-list";
import {
  getArxivCatalog,
  getDriveActivity,
  getDriveAuthStatus,
  getDriveCatalog,
  getResearchCorpus,
  getResearchSyncRuns,
  syncDriveActivity,
  syncDriveChanges,
  syncDefaultResearchSources,
} from "../../lib/api";

export default async function ResearchPage() {
  const driveAuthStatus = await getDriveAuthStatus();
  const includeDrive = !(driveAuthStatus.connector_kind === "live" && !driveAuthStatus.authorized);
  await syncDefaultResearchSources(includeDrive);
  const [driveCatalog, arxivCatalog, researchCorpus, syncRuns] = await Promise.all([
    getDriveCatalog(driveAuthStatus),
    getArxivCatalog(),
    getResearchCorpus(),
    getResearchSyncRuns(),
  ]);
  const driveChangeReceipt = includeDrive ? await syncDriveChanges(driveAuthStatus) : {
    source_type: "drive",
    previous_cursor: undefined,
    cursor: undefined,
    item_count: 0,
    upserted_count: 0,
    changed_source_ids: [],
    blocked_reason: driveAuthStatus.blocked_reason ?? "drive_not_authorized",
    metadata_json: { connector_mode: driveAuthStatus.connector_kind },
  };
  const selectedDriveItem = researchCorpus.items.find((item) => item.provenance.source_type === "drive");
  const driveActivityReceipt = includeDrive && selectedDriveItem
    ? await syncDriveActivity(selectedDriveItem.provenance.source_id)
    : {
        source_id: selectedDriveItem?.provenance.source_id ?? "",
        item_count: 0,
        stored_count: 0,
        blocked_reason: includeDrive ? undefined : (driveAuthStatus.blocked_reason ?? "drive_not_authorized"),
        metadata_json: { connector_mode: driveAuthStatus.connector_kind },
      };
  const driveActivity = selectedDriveItem
    ? await getDriveActivity(selectedDriveItem.provenance.source_id, driveAuthStatus)
    : { source_id: "", items: [], metadata_json: { connector_mode: driveAuthStatus.connector_kind } };
  const latestDriveSync = syncRuns.find((item) => item.source_type === "drive");
  return (
    <main className="page-shell stack-page">
      <section className="section-copy">
        <h1>Research Connectors</h1>
        <p>
          Drive and arXiv are wired in API-first mode. In live Drive mode, this page doubles as
          the acceptance surface for OAuth, sync, change tracking, and activity persistence.
        </p>
      </section>
      <DriveLiveAcceptancePanel
        authStatus={driveAuthStatus}
        latestDriveSync={latestDriveSync}
        changeReceipt={driveChangeReceipt}
        activityReceipt={driveActivityReceipt}
        activity={driveActivity}
      />
      <ResearchSourceList
        title="Drive Connector"
        subtitle="Read-only search and export references with metadata-first retention."
        items={driveCatalog.items}
      />
      <ResearchSourceList
        title="arXiv Connector"
        subtitle="Metadata-only paper search with category/tags preserved for later watchlists."
        items={arxivCatalog.items}
      />
      <ResearchCorpusPanel items={researchCorpus.items} syncRuns={syncRuns} />
    </main>
  );
}
