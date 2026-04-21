import type { ResearchDocumentRecord } from "../lib/mock-data";

export function ResearchSourceList({
  title,
  subtitle,
  items,
}: {
  title: string;
  subtitle: string;
  items: ResearchDocumentRecord[];
}) {
  return (
    <section className="stack-section">
      <div className="section-copy">
        <h2>{title}</h2>
        <p>{subtitle}</p>
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
            <p className="muted-line">
              {item.provenance.source_uri} · retrieved {item.provenance.retrieved_at}
            </p>
          </article>
        ))}
      </div>
    </section>
  );
}
