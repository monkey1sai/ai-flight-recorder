import { ResearchSourceList } from "../../components/research-source-list";
import { researchCatalog } from "../../lib/mock-data";

export default function ResearchPage() {
  return (
    <main className="page-shell stack-page">
      <section className="section-copy">
        <h1>Research Connectors</h1>
        <p>
          Drive and arXiv are wired in fixture mode first. The page emphasizes provenance fields:
          source id, source uri, query, retrieved timestamp, and terms note.
        </p>
      </section>
      <ResearchSourceList
        title="Drive Connector"
        subtitle="Read-only search and export references with metadata-first retention."
        items={researchCatalog.drive.items}
      />
      <ResearchSourceList
        title="arXiv Connector"
        subtitle="Metadata-only paper search with category/tags preserved for later watchlists."
        items={researchCatalog.arxiv.items}
      />
    </main>
  );
}
