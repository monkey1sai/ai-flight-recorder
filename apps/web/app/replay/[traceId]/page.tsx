import { notFound } from "next/navigation";

import { ReplayController } from "../../../components/replay-controller";
import { getReplayFrames, getTraceBundle } from "../../../lib/api";

export default async function ReplayPage({
  params,
}: {
  params: Promise<{ traceId: string }>;
}) {
  const { traceId } = await params;
  const bundle = await getTraceBundle(traceId);

  if (!bundle) {
    notFound();
  }

  const replayFrames = await getReplayFrames(traceId);

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
