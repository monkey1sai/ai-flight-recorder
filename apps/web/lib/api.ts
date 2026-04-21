import {
  claimFlows as claimFlowsFallback,
  demoTraceBundle,
  governanceSnapshot as governanceSnapshotFallback,
  planHistory as planHistoryFallback,
  researchCatalog as researchCatalogFallback,
  replayFrames as replayFramesFallback,
  stateDiffs as stateDiffsFallback,
  taskState as taskStateFallback,
  timelineEntries as timelineEntriesFallback,
  traceSummaries as traceSummariesFallback,
  type AuditEventRecord,
  type ClaimFlow,
  type GovernanceSnapshot,
  type PlanVersionRecord,
  type PolicyRuleRecord,
  type ReplayFrame,
  type ResearchDocumentRecord,
  type RetentionPolicyRecord,
  type StateDeltaRecord,
  type TaskState,
  type TimelineEntry,
  type TraceBundle,
  type TraceSummary,
} from "./mock-data";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  process.env.AERIS_API_BASE_URL ??
  "http://127.0.0.1:8080";

type ApiTimelineEntry = {
  step_id: string;
  step_index: number;
  step_type: string;
  actor: string;
  status: string;
  summary?: string;
  started_at: string;
  ended_at?: string;
  evidence_grade: TimelineEntry["evidenceGrade"];
  observation_count: number;
  artifact_ids: string[];
  claim_ids: string[];
  intervention_ids: string[];
};

type ApiStateDiff = {
  id?: string;
  step_id: string;
  step_index: number;
  facet: string;
  before_json?: Record<string, unknown>;
  after_json?: Record<string, unknown>;
  metadata_json?: Record<string, unknown>;
};

type ApiClaimFlow = {
  claim: ClaimFlow["claim"];
  explanations: ClaimFlow["explanations"];
  supporting_edges: ClaimFlow["edges"];
  artifacts: ClaimFlow["artifacts"];
  supporting_step_ids: string[];
};

type ApiReplayFrame = {
  step: ReplayFrame["step"];
  observations: ReplayFrame["observations"];
  state_deltas: StateDeltaRecord[];
  claims: ReplayFrame["claims"];
  interventions: ReplayFrame["interventions"];
};

type ApiTraceSummary = {
  trace_id: string;
  step_count: number;
  claim_count: number;
  unsupported_claim_count: number;
  model_name?: string;
  status: string;
};

type ApiResearchResponse = {
  query: string;
  items: ResearchDocumentRecord[];
};

type ApiGovernanceSnapshot = {
  audit_events: AuditEventRecord[];
  policies: PolicyRuleRecord[];
  retention: RetentionPolicyRecord[];
};

type ApiTaskState = {
  task: TaskState["task"];
  latest_plan?: PlanVersionRecord;
  latest_snapshot?: {
    id: string;
    trace_id: string;
    step_id?: string;
    task_id?: string;
    snapshot_index: number;
    state_json: Record<string, unknown>;
    metadata_json?: Record<string, unknown>;
    created_at?: string;
  };
  plan_revision_count: number;
  snapshot_count: number;
};

export async function listTraceSummaries(): Promise<TraceSummary[]> {
  const data = await fetchOrFallback<ApiTraceSummary[]>("/api/v1/traces", null);
  if (!data) {
    return traceSummariesFallback;
  }
  return data.map((item) => ({
    traceId: item.trace_id,
    status: item.status,
    modelName: item.model_name ?? "unknown",
    stepCount: item.step_count,
    claimCount: item.claim_count,
    policyFlags: item.unsupported_claim_count,
  }));
}

export async function getTraceBundle(traceId: string): Promise<TraceBundle | undefined> {
  const data = await fetchOrFallback<TraceBundle>(`/api/v1/traces/${traceId}`, null);
  return data ?? (demoTraceBundle.trace.id === traceId ? demoTraceBundle : undefined);
}

export async function getTimelineEntries(traceId: string): Promise<TimelineEntry[]> {
  const timeline = await fetchOrFallback<ApiTimelineEntry[]>(
    `/api/v1/traces/${traceId}/timeline`,
    null,
  );
  if (!timeline) {
    return timelineEntriesFallback;
  }

  return timeline.map((entry) => ({
    step: {
      id: entry.step_id,
      trace_id: traceId,
      step_index: entry.step_index,
      step_type: entry.step_type,
      actor: entry.actor,
      started_at: entry.started_at,
      ended_at: entry.ended_at,
      status: entry.status,
      summary: entry.summary,
      metadata_json: {},
    },
    evidenceGrade: entry.evidence_grade,
    observationCount: entry.observation_count,
    artifactIds: entry.artifact_ids,
    claimIds: entry.claim_ids,
    interventionIds: entry.intervention_ids,
  }));
}

export async function getStateDiffEntries(traceId: string): Promise<StateDeltaRecord[]> {
  const data = await fetchOrFallback<ApiStateDiff[]>(
    `/api/v1/traces/${traceId}/state-diff`,
    null,
  );
  if (!data) {
    return stateDiffsFallback;
  }
  return data.map((item, index) => ({
    id: item.id ?? `${item.step_id}-${item.facet}-${index}`,
    step_id: item.step_id,
    facet: item.facet,
    before_json: item.before_json,
    after_json: item.after_json,
    metadata_json: item.metadata_json,
  }));
}

export async function getClaimFlows(traceId: string): Promise<ClaimFlow[]> {
  const data = await fetchOrFallback<ApiClaimFlow[]>(
    `/api/v1/traces/${traceId}/claim-evidence`,
    null,
  );
  if (!data) {
    return claimFlowsFallback;
  }
  return data.map((item) => ({
    claim: item.claim,
    explanations: item.explanations,
    edges: item.supporting_edges,
    artifacts: item.artifacts,
    stepIds: item.supporting_step_ids,
  }));
}

export async function getReplayFrames(traceId: string): Promise<ReplayFrame[]> {
  const data = await fetchOrFallback<ApiReplayFrame[]>(
    `/api/v1/replay/${traceId}`,
    null,
  );
  if (!data) {
    return replayFramesFallback;
  }
  return data.map((item) => ({
    step: item.step,
    observations: item.observations,
    stateDiffs: item.state_deltas,
    claims: item.claims,
    interventions: item.interventions,
  }));
}

export async function getResearchCatalog(): Promise<{
  drive: ApiResearchResponse;
  arxiv: ApiResearchResponse;
}> {
  const [drive, arxiv] = await Promise.all([
    fetchOrFallback<ApiResearchResponse>(
      "/api/v1/research/drive/search?q=incident notes",
      null,
    ),
    fetchOrFallback<ApiResearchResponse>(
      "/api/v1/research/arxiv/search?q=faithful explanations provenance",
      null,
    ),
  ]);
  return {
    drive: drive ?? researchCatalogFallback.drive,
    arxiv: arxiv ?? researchCatalogFallback.arxiv,
  };
}

export async function getGovernanceSnapshot(traceId?: string): Promise<GovernanceSnapshot> {
  const query = traceId ? `?trace_id=${traceId}` : "";
  const data = await fetchOrFallback<ApiGovernanceSnapshot>(
    `/api/v1/admin/snapshot${query}`,
    null,
  );
  if (!data) {
    return governanceSnapshotFallback;
  }
  return {
    auditEvents: data.audit_events,
    policies: data.policies,
    retention: data.retention,
  };
}

export async function getTaskState(traceId: string): Promise<TaskState | undefined> {
  const data = await fetchOrFallback<ApiTaskState>(`/api/v1/traces/${traceId}/task`, null);
  if (!data) {
    return taskStateFallback;
  }
  return {
    task: data.task,
    latestPlan: data.latest_plan,
    latestSnapshot: data.latest_snapshot,
    planRevisionCount: data.plan_revision_count,
    snapshotCount: data.snapshot_count,
  };
}

export async function getPlanHistory(traceId: string): Promise<PlanVersionRecord[]> {
  const data = await fetchOrFallback<PlanVersionRecord[]>(
    `/api/v1/traces/${traceId}/plan-history`,
    null,
  );
  return data ?? planHistoryFallback;
}

async function fetchOrFallback<T>(path: string, fallback: T | null): Promise<T | null> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, { cache: "no-store" });
    if (!response.ok) {
      return fallback;
    }
    return (await response.json()) as T;
  } catch {
    return fallback;
  }
}
