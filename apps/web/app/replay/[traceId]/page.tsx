import { notFound } from "next/navigation";

import { ReplayController } from "../../../components/replay-controller";
import { getTraceBundleById, replayFrames } from "../../../lib/mock-data";

export default function ReplayPage({
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
        <h1>Replay</h1>
        <p>
          Replay frames mirror `/api/v1/replay/{bundle.trace.id}` and make it clear which
          observations, state diffs, and interventions were active at each step.
        </p>
      </section>
      <ReplayController frames={replayFrames} />
    </main>
  );
}
