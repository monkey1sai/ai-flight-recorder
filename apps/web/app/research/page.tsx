import { ResearchCorpusPanel } from "../../components/research-corpus-panel";
import { ResearchSourceList } from "../../components/research-source-list";
import {
  getResearchCatalog,
  getResearchCorpus,
  getResearchSyncRuns,
  syncDefaultResearchSources,
} from "../../lib/api";

export default async function ResearchPage() {
  await syncDefaultResearchSources();
  const researchCatalog = await getResearchCatalog();
  const [researchCorpus, syncRuns] = await Promise.all([
    getResearchCorpus(),
    getResearchSyncRuns(),
  ]);
  return (
    <main className="page-shell stack-page">
      <section className="section-copy">
        <h1>Research Connectors</h1>
        <p>
          Drive and arXiv are wired in API-first mode with fixture fallback. The page emphasizes
          provenance fields: source id, source uri, query, cursor, checksum, export status, and
          retrieved timestamp.
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
      <ResearchCorpusPanel items={researchCorpus.items} syncRuns={syncRuns} />
    </main>
  );
}
