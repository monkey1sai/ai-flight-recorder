# Validation Report: Claim-Centric Why v1

## Scope

Validate Product Phase 5 on top of the runnable MVP checkpoint:

- claim extraction fallback for bundles that arrive without precomputed claims
- conservative why assembly that defaults extracted claims to `unsupported` + `self_reported`
- live persistence of `claims`, `evidence_edges`, and `explanation_records`
- why panel rendering of confidence, unsupported flags, and evidence links
- compose-backed proof that a claimless live ingest is queryable through API and visible through the Web trace detail route

## Commands run

```powershell
C:/Repos/active/ai-agent/AI-Flight-Recorder/.venv/Scripts/python.exe -m pytest tests/unit/test_why_derivation.py tests/integration/test_api_operator_surfaces.py -q
C:/Repos/active/ai-agent/AI-Flight-Recorder/.venv/Scripts/ruff.exe check .
node C:/Repos/active/ai-agent/AI-Flight-Recorder/node_modules/pyright/index.js --pythonpath C:/Repos/active/ai-agent/AI-Flight-Recorder/.venv/Scripts/python.exe -p pyrightconfig.json --level error apps packages workers tests
npm run lint --workspace @aeris/web
npm run typecheck --workspace @aeris/web
C:/Repos/active/ai-agent/AI-Flight-Recorder/.venv/Scripts/python.exe -m pytest tests/smoke/test_operator_surfaces_assets.py -q
docker-compose -f infra/compose/docker-compose.yml down -v --remove-orphans
docker-compose -f infra/compose/docker-compose.yml config
docker-compose -f infra/compose/docker-compose.yml up --build -d
Invoke-WebRequest http://localhost:8080/healthz | Select-Object -ExpandProperty StatusCode
@'
from uuid import uuid4
import httpx
from apps.api.app.bootstrap import build_demo_ingest_request

request = build_demo_ingest_request()
session_id = uuid4()
trace_id = uuid4()
step_ids = [uuid4() for _ in request.bundle.steps]
artifact_ids = [uuid4() for _ in request.bundle.artifacts]
step_id_map = {step.id: step_ids[index] for index, step in enumerate(request.bundle.steps)}
artifact_id_map = {artifact.id: artifact_ids[index] for index, artifact in enumerate(request.bundle.artifacts)}

request.bundle = request.bundle.model_copy(
    deep=True,
    update={
        "session": request.bundle.session.model_copy(update={"id": session_id}),
        "trace": request.bundle.trace.model_copy(
            update={"id": trace_id, "session_id": session_id, "task_id": None}
        ),
        "steps": [
            step.model_copy(update={"id": step_id_map[step.id], "trace_id": trace_id})
            for step in request.bundle.steps
        ],
        "observations": [
            observation.model_copy(
                update={
                    "step_id": step_id_map[observation.step_id],
                    "source_artifact_id": artifact_id_map[observation.source_artifact_id]
                    if observation.source_artifact_id is not None
                    else None,
                }
            )
            for observation in request.bundle.observations
        ],
        "state_deltas": [
            delta.model_copy(update={"step_id": step_id_map[delta.step_id]})
            for delta in request.bundle.state_deltas
        ],
        "artifacts": [
            artifact.model_copy(
                update={
                    "id": artifact_id_map[artifact.id],
                    "trace_id": trace_id,
                    "source_uri": f"trace://{trace_id}/output"
                    if artifact.source_type == "final_output"
                    else artifact.source_uri,
                    "metadata_json": {
                        **artifact.metadata_json,
                        "grade": "self_reported"
                        if artifact.source_type == "final_output"
                        else artifact.metadata_json.get("grade", "observed"),
                        "seeded_by": "phase5_validation",
                    },
                }
            )
            for artifact in request.bundle.artifacts
        ],
        "interventions": [
            intervention.model_copy(
                update={
                    "trace_id": trace_id,
                    "step_id": step_id_map[intervention.step_id]
                    if intervention.step_id is not None
                    else None,
                }
            )
            for intervention in request.bundle.interventions
        ],
        "evaluations": [
            evaluation.model_copy(update={"trace_id": trace_id})
            for evaluation in request.bundle.evaluations
        ],
        "claims": [],
        "evidence_edges": [],
        "explanations": [],
        "tasks": [],
        "plan_versions": [],
        "state_snapshots": [],
    },
)
request.raw_artifacts = [
    payload.model_copy(update={"artifact_id": artifact_id_map[payload.artifact_id]})
    for payload in request.raw_artifacts
]
for payload in request.raw_artifacts:
    if payload.text_content:
        payload.text_content = "The deployment manifest is stale. Human review is required before remediation."
        payload.metadata_json = {**payload.metadata_json, "seeded_by": "phase5_validation"}

response = httpx.post(
    "http://127.0.0.1:8080/api/v1/ingest/normalized-trace-bundles",
    json=request.model_dump(mode="json"),
    timeout=30,
)
print(response.status_code)
print(str(trace_id))
print(response.text)
'@ | C:/Repos/active/ai-agent/AI-Flight-Recorder/.venv/Scripts/python.exe -
Invoke-WebRequest http://localhost:8080/api/v1/traces/97c69545-1838-464e-9db9-1cd7daccfd27/claim-evidence | Select-Object -ExpandProperty Content
(Invoke-WebRequest http://localhost:3000/traces/97c69545-1838-464e-9db9-1cd7daccfd27).StatusCode
```

## Results

- `C:/Repos/active/ai-agent/AI-Flight-Recorder/.venv/Scripts/python.exe -m pytest tests/unit/test_why_derivation.py tests/integration/test_api_operator_surfaces.py -q`
  Passed. `5 passed`. Covered claim extraction fallback, normalized ingest behavior when `claims` / `evidence_edges` / `explanations` are absent, and operator API surface expectations.
- `C:/Repos/active/ai-agent/AI-Flight-Recorder/.venv/Scripts/ruff.exe check .`
  Passed.
- `node C:/Repos/active/ai-agent/AI-Flight-Recorder/node_modules/pyright/index.js --pythonpath C:/Repos/active/ai-agent/AI-Flight-Recorder/.venv/Scripts/python.exe -p pyrightconfig.json --level error apps packages workers tests`
  Passed.
- `npm run lint --workspace @aeris/web`
  Passed.
- `npm run typecheck --workspace @aeris/web`
  Passed.
- `C:/Repos/active/ai-agent/AI-Flight-Recorder/.venv/Scripts/python.exe -m pytest tests/smoke/test_operator_surfaces_assets.py -q`
  Passed.
- `docker-compose -f infra/compose/docker-compose.yml down -v --remove-orphans`
  Passed. Cleared prior containers and volumes before compose-backed validation.
- `docker-compose -f infra/compose/docker-compose.yml config`
  Passed.
- `docker-compose -f infra/compose/docker-compose.yml up --build -d`
  Passed on a fresh DB / blob volume set.
- `Invoke-WebRequest http://localhost:8080/healthz`
  Passed with HTTP `200`.
- Live claimless ingest through `POST /api/v1/ingest/normalized-trace-bundles`
  Passed with HTTP `200`. Returned `trace_id=97c69545-1838-464e-9db9-1cd7daccfd27` and `entity_counts.claims=2`, `entity_counts.explanations=2`.
- `GET /api/v1/traces/97c69545-1838-464e-9db9-1cd7daccfd27/claim-evidence`
  Passed with HTTP `200`. Returned two extracted claims:
  - `The deployment manifest is stale.`
  - `Human review is required before remediation.`
- Claim evidence payload for both extracted claims showed:
  - `verification_status="unsupported"`
  - explanation `grade="self_reported"`
  - evidence edge to the final output artifact with `relation="stated_in_output"`
  - evidence edge to the response step with `relation="stated_in"`
- `(Invoke-WebRequest http://localhost:3000/traces/97c69545-1838-464e-9db9-1cd7daccfd27).StatusCode`
  Passed with HTTP `200`. The live trace detail route remained renderable after the why panel changes.

## Observed proof points

- Phase 5 stayed additive to the existing normalized ingest contract. The edge/demo payload did not need a new why-specific endpoint.
- The fallback does not overclaim. Claimless final output text becomes `unsupported` + `self_reported`, not `supported`, `observed`, or `verified`.
- Why panel evidence is no longer opaque summary-only data; the live API surfaces concrete claim-to-artifact and claim-to-step links.
- The live persistence path still works after the why fallback was inserted into repository upsert flow.

## Blocker fixed during validation

- Phase 5 branch validation exposed a fixture/live parity gap: the fixture repository still returned empty `task` / `plan_history`, so the operator-surface integration test failed with `/task -> 404`. The fixture repository now applies the same cognitive derivation and why fallback used by the live path, which keeps tests aligned with the already-runnable API behavior.

## Remaining gaps

- This milestone does not yet auto-upgrade claims to `supported` from observed tool/document evidence. The fallback is intentionally conservative.
- Claim extraction is still heuristic sentence splitting over final output text; there is no richer parser or evidence matcher yet.
- There is still no replay-backed verification in this phase. `verified` remains outside the scope of this milestone.
- OTLP protobuf ingestion remains outside this validation scope.

## Failures

- None in the validated Phase 5 scope after the repository upsert ordering fix.
- A clean Git diff for "Phase 5 only" is not directly available from the current local worktree because this workspace still contains unmerged Phase 1-4 era changes. PR isolation must therefore happen on top of a branch where the earlier phases are already merged, or by selectively porting only the Phase 5 files/hunks.

## Risk assessment

- Low product risk: the why fallback is conservative and does not upgrade unsupported claims to supported or verified.
- Medium integration risk: Phase 5 touches persistence and operator surfaces together, so future changes around task/trace upsert ordering need to preserve the circular-FK workaround.
- Medium delivery risk: from this workstation, Phase 5 is validated and runnable, but the current worktree is not yet a clean standalone branch that can be pushed as-is without mixing earlier phase work.

## Recommendation

`merge_with_known_risks`

Reason:
- the Phase 5 behavior itself is validated and runnable
- the remaining risk is branch hygiene / PR isolation, not a missing product proof inside the Phase 5 slice

## Follow-up items

- Create the actual PR from a base that already includes the runnable baseline and Product Phase 4 cognitive-state slice.
- Keep the PR limited to Phase 5 files/hunks:
  - `apps/api/app/why.py`
  - `apps/api/app/repositories/postgres_store.py`
  - `apps/api/app/repositories/fixture_store.py`
  - `apps/api/app/services/trace_workbench.py`
  - `apps/web/components/why-panel.tsx`
  - `tests/unit/test_why_derivation.py`
  - `tests/integration/test_api_operator_surfaces.py`
  - `tests/smoke/test_operator_surfaces_assets.py`
  - `plans/active/20260421-mvp-phase-1-7-execution.md`
  - `reports/validation/20260421-claim-centric-why-v1.md`
- Use this checkpoint as the baseline for future evidence-link enrichment, not as proof that full verification or counterfactual replay already exists.
