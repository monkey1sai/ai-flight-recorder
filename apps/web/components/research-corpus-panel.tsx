import type { ResearchDocumentRecord, ResearchSyncRunRecord } from "../lib/mock-data";

export function ResearchCorpusPanel({
  items,
  syncRuns,
}: {
  items: ResearchDocumentRecord[];
  syncRuns: ResearchSyncRunRecord[];
}) {
  return (
    <section className="stack-section">
      <div className="section-copy">
        <h2>Corpus Explorer</h2>
        <p>
          Persisted research corpus items with sync provenance. This is the MVP single-db slice:
          metadata stays queryable in Postgres while raw refs remain external.
        </p>
      </div>

      <div className="stack-grid">
        {syncRuns.map((run) => (
          <article className="panel" key={run.id}>
            <div className="panel-header">
              <strong>{run.source_type} sync</strong>
              <span>{run.status}</span>
            </div>
            <p className="muted-line">
              query {run.query || "(all)"} · items {run.item_count}
            </p>
            <p className="muted-line">cursor {run.cursor ?? "n/a"}</p>
          </article>
        ))}
      </div>

      <div className="stack-grid">
        {items.map((item) => (
          <article className="panel" key={item.id}>
            <div className="panel-header">
              <strong>{item.title}</strong>
              <span>{item.provenance.source_type}</span>
            </div>
            <p>{item.summary}</p>
            <div className="chip-row">
              {item.tags.map((tag) => (
                <span className="chip" key={tag}>
                  {tag}
                </span>
              ))}
            </div>
            <p className="muted-line">source id {item.provenance.source_id}</p>
            <p className="muted-line">uri {item.provenance.source_uri}</p>
            <p className="muted-line">retrieved {item.provenance.retrieved_at}</p>
            <p className="muted-line">cursor {item.provenance.cursor ?? "n/a"}</p>
            <p className="muted-line">checksum {item.provenance.checksum ?? "n/a"}</p>
            <p className="muted-line">export {item.provenance.export_status ?? "n/a"}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
