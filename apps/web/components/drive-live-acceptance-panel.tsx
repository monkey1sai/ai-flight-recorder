import type {
  DriveActivityListView,
  DriveActivitySyncReceipt,
  DriveAuthStatus,
  DriveChangeSyncReceipt,
  ResearchSyncRunRecord,
} from "../lib/mock-data";

export function DriveLiveAcceptancePanel({
  authStatus,
  latestDriveSync,
  changeReceipt,
  activityReceipt,
  activity,
}: {
  authStatus: DriveAuthStatus;
  latestDriveSync?: ResearchSyncRunRecord;
  changeReceipt: DriveChangeSyncReceipt;
  activityReceipt: DriveActivitySyncReceipt;
  activity: DriveActivityListView;
}) {
  const activityBlocked = activityReceipt.blocked_reason ?? activity.blocked_reason;
  return (
    <section className="stack-section">
      <div className="section-copy">
        <h2>Drive Acceptance</h2>
        <p>
          This panel is the live Drive acceptance surface: auth status, latest sync, incremental
          change token, and per-document activity history.
        </p>
      </div>
      <div className="admin-grid">
        <article className="panel">
          <div className="panel-header">
            <strong>Auth Status</strong>
            <span>{authStatus.mode}</span>
          </div>
          <p className="muted-line">connector {authStatus.connector_kind}</p>
          <p className="muted-line">authorized {String(authStatus.authorized)}</p>
          <p className="muted-line">client secrets {String(authStatus.client_secrets_exists)}</p>
          <p className="muted-line">token present {String(authStatus.token_present)}</p>
          <p className="muted-line">can refresh {String(authStatus.can_refresh)}</p>
          <p className="muted-line">blocked {authStatus.blocked_reason ?? "none"}</p>
        </article>
        <article className="panel">
          <div className="panel-header">
            <strong>Latest Drive Sync</strong>
            <span>{latestDriveSync?.status ?? "n/a"}</span>
          </div>
          <p className="muted-line">query {latestDriveSync?.query ?? "(none)"}</p>
          <p className="muted-line">items {latestDriveSync?.item_count ?? 0}</p>
          <p className="muted-line">cursor {latestDriveSync?.cursor ?? "n/a"}</p>
        </article>
        <article className="panel">
          <div className="panel-header">
            <strong>Change Tracking</strong>
            <span>{changeReceipt.item_count} changes</span>
          </div>
          <p className="muted-line">previous {changeReceipt.previous_cursor ?? "n/a"}</p>
          <p className="muted-line">current {changeReceipt.cursor ?? "n/a"}</p>
          <p className="muted-line">upserted {changeReceipt.upserted_count}</p>
          <p className="muted-line">blocked {changeReceipt.blocked_reason ?? "none"}</p>
          {typeof changeReceipt.metadata_json?.ignored_reason === "string" ? (
            <p className="muted-line">
              cursor hygiene {changeReceipt.metadata_json.ignored_reason}
            </p>
          ) : null}
        </article>
      </div>
      <div className="stack-grid">
        <article className="panel">
          <div className="panel-header">
            <strong>Drive Activity</strong>
            <span>{activityReceipt.item_count || activity.items.length} events</span>
          </div>
          <p className="muted-line">source {activity.source_id || "n/a"}</p>
          <p className="muted-line">blocked {activityBlocked ?? "none"}</p>
          <p className="muted-line">stored {activityReceipt.stored_count}</p>
          <ul className="plain-list">
            {activityBlocked ? (
              <li>
                <strong>Blocked</strong>
                <span>{activityBlocked}</span>
              </li>
            ) : activity.items.length === 0 ? (
              <li>
                <strong>No events</strong>
                <span>No persisted Drive activity for the selected document.</span>
              </li>
            ) : (
              activity.items.map((item) => (
                <li key={item.id}>
                  <strong>{item.primary_action}</strong>
                  <span>{item.occurred_at}</span>
                  <span className="muted-line">
                    actors {item.actors.join(", ") || "n/a"} · targets {item.targets.join(", ") || "n/a"}
                  </span>
                </li>
              ))
            )}
          </ul>
        </article>
      </div>
    </section>
  );
}
