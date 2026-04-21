import arxivSearchSeed from "../../../packages/testkit/fixtures/arxiv_search_results.json";
import driveSearchSeed from "../../../packages/testkit/fixtures/drive_search_results.json";
import traceBundleSeed from "../../../packages/testkit/fixtures/demo_trace_bundle.json";

export type EvidenceGrade =
  | "observed"
  | "self_reported"
  | "inferred"
  | "verified";

export type TraceStatus =
  | "queued"
  | "running"
  | "completed"
  | "failed"
  | "cancelled";

export type ClaimVerificationStatus =
  | "supported"
  | "partially_supported"
  | "unsupported"
  | "model_prior_only"
  | "conflicted";

export interface SessionRecord {
  id: string;
  source: string;
  user_id?: string;
  started_at: string;
  status: TraceStatus;
  metadata_json?: Record<string, string>;
  labels_jsonb?: string[];
}

export interface TraceRecord {
  id: string;
  session_id: string;
  task_id?: string;
  model_name?: string;
  trace_kind: string;
  started_at: string;
  ended_at?: string;
  status: TraceStatus;
  config_ref?: string;
  metadata_json?: Record<string, string>;
}

export interface StepRecord {
  id: string;
  trace_id: string;
  step_index: number;
  step_type: string;
  actor: string;
  started_at: string;
  ended_at?: string;
  status: string;
  summary?: string;
  metadata_json?: Record<string, unknown>;
}

export interface TaskRecord {
  id: string;
  session_id: string;
  trace_id: string;
  title: string;
  status: TraceStatus;
  owner?: string;
  summary?: string;
  metadata_json?: Record<string, unknown>;
  created_at?: string;
}

export interface ObservationRecord {
  id: string;
  step_id: string;
  kind: string;
  content_ref: string;
  confidence?: number;
  source_artifact_id?: string;
  metadata_json?: Record<string, unknown>;
}

export interface StateDeltaRecord {
  id: string;
  step_id: string;
  facet: string;
  before_json?: Record<string, unknown>;
  after_json?: Record<string, unknown>;
  metadata_json?: Record<string, unknown>;
}

export interface PlanVersionRecord {
  id: string;
  task_id: string;
  trace_id: string;
  step_id?: string;
  revision: number;
  summary?: string;
  plan_json: Record<string, unknown>;
  metadata_json?: Record<string, unknown>;
  created_at?: string;
}

export interface StateSnapshotRecord {
  id: string;
  trace_id: string;
  step_id?: string;
  task_id?: string;
  snapshot_index: number;
  state_json: Record<string, unknown>;
  metadata_json?: Record<string, unknown>;
  created_at?: string;
}

export interface ArtifactRecord {
  id: string;
  source_type: string;
  source_system?: string;
  source_uri?: string;
  mime_type?: string;
  checksum?: string;
  storage_ref?: string;
  metadata_json?: Record<string, unknown>;
}

export interface EvidenceEdgeRecord {
  id: string;
  from_kind: string;
  from_id: string;
  to_kind: string;
  to_id: string;
  relation: string;
  weight?: number;
  metadata_json?: Record<string, unknown>;
}

export interface ClaimRecord {
  id: string;
  trace_id: string;
  claim_text: string;
  claim_type: string;
  confidence?: number;
  position_index: number;
  verification_status: ClaimVerificationStatus;
  metadata_json?: Record<string, unknown>;
}

export interface ExplanationRecord {
  id: string;
  claim_id: string;
  grade: EvidenceGrade;
  method: string;
  summary: string;
  supporting_edge_ids: string[];
  confidence?: number;
  metadata_json?: Record<string, unknown>;
}

export interface InterventionRecord {
  id: string;
  trace_id: string;
  step_id?: string;
  intervention_type: string;
  reason: string;
  actor: string;
  result: string;
  metadata_json?: Record<string, unknown>;
}

export interface AuditEventRecord {
  id: string;
  trace_id?: string;
  event_type: string;
  actor: string;
  outcome: string;
  occurred_at: string;
  metadata_json?: Record<string, unknown>;
}

export interface PolicyRuleRecord {
  id: string;
  name: string;
  category: string;
  mode: string;
  applies_to: string[];
  description: string;
  configured_by: string;
  metadata_json?: Record<string, unknown>;
}

export interface RetentionPolicyRecord {
  id: string;
  name: string;
  applies_to: string[];
  retention_days: number;
  purge_strategy: string;
  redaction_scope: string[];
  metadata_json?: Record<string, unknown>;
}

export interface ResearchSourceRecord {
  source_type: string;
  source_id: string;
  source_uri: string;
  retrieved_at: string;
  query: string;
  license_or_terms_note?: string;
  checksum?: string;
  metadata_json?: Record<string, unknown>;
}

export interface ResearchDocumentRecord {
  id: string;
  title: string;
  summary: string;
  authors: string[];
  published_at?: string;
  mime_type?: string;
  content_ref?: string;
  tags: string[];
  provenance: ResearchSourceRecord;
}

export interface ResearchSearchResult {
  query: string;
  items: ResearchDocumentRecord[];
}

export interface TraceSummary {
  traceId: string;
  status: string;
  modelName: string;
  stepCount: number;
  claimCount: number;
  policyFlags: number;
}

export interface TraceBundle {
  session: SessionRecord;
  trace: TraceRecord;
  tasks: TaskRecord[];
  plan_versions: PlanVersionRecord[];
  state_snapshots: StateSnapshotRecord[];
  steps: StepRecord[];
  observations: ObservationRecord[];
  state_deltas: StateDeltaRecord[];
  artifacts: ArtifactRecord[];
  evidence_edges: EvidenceEdgeRecord[];
  claims: ClaimRecord[];
  explanations: ExplanationRecord[];
  interventions: InterventionRecord[];
  audit_events: AuditEventRecord[];
  policies: PolicyRuleRecord[];
  retention: RetentionPolicyRecord[];
}

export interface TimelineEntry {
  step: StepRecord;
  evidenceGrade: EvidenceGrade;
  observationCount: number;
  artifactIds: string[];
  claimIds: string[];
  interventionIds: string[];
}

export interface ClaimFlow {
  claim: ClaimRecord;
  explanations: ExplanationRecord[];
  edges: EvidenceEdgeRecord[];
  artifacts: ArtifactRecord[];
  stepIds: string[];
}

export interface ReplayFrame {
  step: StepRecord;
  observations: ObservationRecord[];
  stateDiffs: StateDeltaRecord[];
  claims: ClaimRecord[];
  interventions: InterventionRecord[];
}

export interface GovernanceSnapshot {
  auditEvents: AuditEventRecord[];
  policies: PolicyRuleRecord[];
  retention: RetentionPolicyRecord[];
}

export interface TaskState {
  task: TaskRecord;
  latestPlan?: PlanVersionRecord;
  latestSnapshot?: StateSnapshotRecord;
  planRevisionCount: number;
  snapshotCount: number;
}

const traceBundle = normalizeTraceBundle(traceBundleSeed as Partial<TraceBundle>);
const driveSearch = driveSearchSeed as ResearchSearchResult;
const arxivSearch = arxivSearchSeed as ResearchSearchResult;

const gradePriority: Record<EvidenceGrade, number> = {
  self_reported: 1,
  inferred: 2,
  observed: 3,
  verified: 4,
};

const claimIdsByStep = new Map<string, string[]>();

for (const edge of traceBundle.evidence_edges) {
  if (edge.from_kind === "claim" && edge.to_kind === "step") {
    const current = claimIdsByStep.get(edge.to_id) ?? [];
    current.push(edge.from_id);
    claimIdsByStep.set(edge.to_id, current);
  }
}

function getExplanationGrade(stepId: string, observationCount: number, interventionCount: number): EvidenceGrade {
  const claimIds = claimIdsByStep.get(stepId) ?? [];
  const explanations = traceBundle.explanations.filter((item) =>
    claimIds.includes(item.claim_id),
  );

  if (explanations.length === 0) {
    if (observationCount > 0) {
      return "observed";
    }
    if (interventionCount > 0) {
      return "inferred";
    }
    return "self_reported";
  }

  return explanations
    .map((item) => item.grade)
    .sort((left, right) => gradePriority[right] - gradePriority[left])[0];
}

export const traceSummaries: TraceSummary[] = [
  {
    traceId: traceBundle.trace.id,
    status: traceBundle.trace.status,
    modelName: traceBundle.trace.model_name ?? "unknown",
    stepCount: traceBundle.steps.length,
    claimCount: traceBundle.claims.length,
    policyFlags: traceBundle.interventions.length,
  },
];

export const timelineEntries: TimelineEntry[] = traceBundle.steps.map((step) => {
  const observations = traceBundle.observations.filter((item) => item.step_id === step.id);
  const interventions = traceBundle.interventions.filter((item) => item.step_id === step.id);
  const claimIds = claimIdsByStep.get(step.id) ?? [];
  const artifactIds = observations
    .map((item) => item.source_artifact_id)
    .filter((item): item is string => Boolean(item));

  return {
    step,
    evidenceGrade: getExplanationGrade(
      step.id,
      observations.length,
      interventions.length,
    ),
    observationCount: observations.length,
    artifactIds,
    claimIds,
    interventionIds: interventions.map((item) => item.id),
  };
});

export const claimFlows: ClaimFlow[] = traceBundle.claims.map((claim) => {
  const edges = traceBundle.evidence_edges.filter(
    (edge) => edge.from_kind === "claim" && edge.from_id === claim.id,
  );
  const artifactIds = edges
    .filter((edge) => edge.to_kind === "artifact")
    .map((edge) => edge.to_id);
  const stepIds = edges
    .filter((edge) => edge.to_kind === "step")
    .map((edge) => edge.to_id);

  return {
    claim,
    explanations: traceBundle.explanations.filter(
      (explanation) => explanation.claim_id === claim.id,
    ),
    edges,
    artifacts: traceBundle.artifacts.filter((artifact) =>
      artifactIds.includes(artifact.id),
    ),
    stepIds,
  };
});

export const replayFrames: ReplayFrame[] = traceBundle.steps.map((step) => {
  const claimIds = claimIdsByStep.get(step.id) ?? [];

  return {
    step,
    observations: traceBundle.observations.filter((item) => item.step_id === step.id),
    stateDiffs: traceBundle.state_deltas.filter((item) => item.step_id === step.id),
    claims: traceBundle.claims.filter((item) => claimIds.includes(item.id)),
    interventions: traceBundle.interventions.filter((item) => item.step_id === step.id),
  };
});

export const stateDiffs = traceBundle.state_deltas;
export const governanceSnapshot: GovernanceSnapshot = {
  auditEvents: traceBundle.audit_events,
  policies: traceBundle.policies,
  retention: traceBundle.retention,
};
export const taskState: TaskState | undefined = buildTaskState(traceBundle);
export const planHistory = traceBundle.plan_versions;
export const researchCatalog = {
  drive: driveSearch,
  arxiv: arxivSearch,
};
export const demoTraceBundle = traceBundle;

export function getTraceBundleById(traceId: string): TraceBundle | undefined {
  if (traceBundle.trace.id !== traceId) {
    return undefined;
  }
  return traceBundle;
}

function normalizeTraceBundle(seed: Partial<TraceBundle>): TraceBundle {
  const session = seed.session as SessionRecord;
  const trace = seed.trace as TraceRecord;
  const steps = (seed.steps ?? []) as StepRecord[];
  const stateDeltas = (seed.state_deltas ?? []) as StateDeltaRecord[];
  const tasks = seed.tasks?.length ? seed.tasks : deriveTasks(session, trace, steps, stateDeltas);
  const planVersions = seed.plan_versions?.length
    ? seed.plan_versions
    : derivePlanVersions(trace, steps, stateDeltas, tasks[0]);
  const stateSnapshots = seed.state_snapshots?.length
    ? seed.state_snapshots
    : deriveStateSnapshots(trace, steps, stateDeltas, tasks[0]);

  return {
    session,
    trace: {
      ...trace,
      task_id: trace.task_id ?? tasks[0]?.id,
    },
    tasks,
    plan_versions: planVersions,
    state_snapshots: stateSnapshots,
    steps,
    observations: (seed.observations ?? []) as ObservationRecord[],
    state_deltas: stateDeltas,
    artifacts: (seed.artifacts ?? []) as ArtifactRecord[],
    evidence_edges: (seed.evidence_edges ?? []) as EvidenceEdgeRecord[],
    claims: (seed.claims ?? []) as ClaimRecord[],
    explanations: (seed.explanations ?? []) as ExplanationRecord[],
    interventions: (seed.interventions ?? []) as InterventionRecord[],
    audit_events: (seed.audit_events ?? []) as AuditEventRecord[],
    policies: (seed.policies ?? []) as PolicyRuleRecord[],
    retention: (seed.retention ?? []) as RetentionPolicyRecord[],
  };
}

function deriveTasks(
  session: SessionRecord,
  trace: TraceRecord,
  steps: StepRecord[],
  stateDeltas: StateDeltaRecord[],
): TaskRecord[] {
  const title =
    (typeof trace.metadata_json?.intent === "string" && trace.metadata_json.intent) ||
    steps.find((step) => step.summary)?.summary ||
    `Trace ${trace.id}`;
  return [
    {
      id: trace.task_id ?? `task-${trace.id}`,
      session_id: session.id,
      trace_id: trace.id,
      title,
      status: trace.status,
      owner: session.user_id,
      summary:
        (typeof trace.metadata_json?.intent === "string" && trace.metadata_json.intent) ||
        steps.at(-1)?.summary,
      created_at: trace.started_at,
      metadata_json: {
        workspace: session.metadata_json?.workspace,
        facets: [...new Set(stateDeltas.map((item) => item.facet))],
        derived_from: "mock-data",
      },
    },
  ];
}

function derivePlanVersions(
  trace: TraceRecord,
  steps: StepRecord[],
  stateDeltas: StateDeltaRecord[],
  task?: TaskRecord,
): PlanVersionRecord[] {
  const planSteps = steps.filter((step) =>
    step.step_type === "plan_update" ||
    stateDeltas.some((delta) => delta.step_id === step.id && delta.facet === "plan_state"),
  );

  if (planSteps.length === 0 || !task) {
    return [];
  }

  return planSteps.map((step, revision) => {
    const planDelta = stateDeltas.find(
      (delta) => delta.step_id === step.id && delta.facet === "plan_state",
    );
    return {
      id: `plan-${task.id}-${revision}`,
      task_id: task.id,
      trace_id: trace.id,
      step_id: step.id,
      revision,
      summary: step.summary,
      plan_json: planDelta?.after_json ?? {
        summary: step.summary,
        metadata: step.metadata_json ?? {},
      },
      metadata_json: {
        derived_from: "mock-data",
      },
      created_at: step.ended_at ?? step.started_at,
    };
  });
}

function deriveStateSnapshots(
  trace: TraceRecord,
  steps: StepRecord[],
  stateDeltas: StateDeltaRecord[],
  task?: TaskRecord,
): StateSnapshotRecord[] {
  const state: Record<string, unknown> = {};
  const snapshots: StateSnapshotRecord[] = [];

  for (const step of steps) {
    const stepDeltas = stateDeltas.filter((delta) => delta.step_id === step.id);
    if (stepDeltas.length === 0) {
      continue;
    }
    for (const delta of stepDeltas) {
      state[delta.facet] = delta.after_json ?? delta.before_json ?? {};
    }
    snapshots.push({
      id: `snapshot-${trace.id}-${step.step_index}`,
      trace_id: trace.id,
      step_id: step.id,
      task_id: task?.id,
      snapshot_index: step.step_index,
      state_json: { ...state },
      metadata_json: {
        derived_from: "mock-data",
        facets: stepDeltas.map((delta) => delta.facet),
      },
      created_at: step.ended_at ?? step.started_at,
    });
  }

  return snapshots;
}

function buildTaskState(bundle: TraceBundle): TaskState | undefined {
  const task = bundle.tasks[0];
  if (!task) {
    return undefined;
  }
  return {
    task,
    latestPlan: bundle.plan_versions.at(-1),
    latestSnapshot: bundle.state_snapshots.at(-1),
    planRevisionCount: bundle.plan_versions.length,
    snapshotCount: bundle.state_snapshots.length,
  };
}
