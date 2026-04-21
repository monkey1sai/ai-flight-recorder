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

export interface TraceBundle {
  session: SessionRecord;
  trace: TraceRecord;
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

const traceBundle = traceBundleSeed as TraceBundle;
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

export const traceSummaries = [
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
export const governanceSnapshot = {
  auditEvents: traceBundle.audit_events,
  policies: traceBundle.policies,
  retention: traceBundle.retention,
};
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
