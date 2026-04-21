import { notFound } from "next/navigation";

import { ReplayController } from "../../../components/replay-controller";
import { getReplayFrames, getReplayVerification, getTraceBundle } from "../../../lib/api";

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

  const [replayFrames, replayVerification] = await Promise.all([
    getReplayFrames(traceId),
    getReplayVerification(traceId),
  ]);

  return (
    <main className="page-shell stack-page">
      <section className="section-copy">
        <h1>Replay</h1>
        <p>
          Replay frames mirror `/api/v1/replay/{bundle.trace.id}` and `/api/v1/replay/{bundle.trace.id}/verification`,
          so operators can see both the step-by-step reconstruction and the replay-backed
          verification badge derived from explicit evidence.
        </p>
      </section>
      <ReplayController frames={replayFrames} verification={replayVerification} />
    </main>
  );
}
