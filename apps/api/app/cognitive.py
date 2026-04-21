from __future__ import annotations

from datetime import UTC, datetime
from uuid import NAMESPACE_URL, UUID, uuid5

from packages.schema.flight_recorder_schema import (
    PlanVersionRecord,
    StateDeltaRecord,
    StateSnapshotRecord,
    TaskRecord,
    TaskStateView,
    TaskStatus,
    TraceBundleView,
    TraceStatus,
)


def ensure_cognitive_state(bundle: TraceBundleView) -> TraceBundleView:
    enriched = bundle.model_copy(deep=True)

    task = _ensure_task(enriched)
    trace = enriched.trace
    if task is not None and trace.task_id != task.id:
        trace = trace.model_copy(update={"task_id": task.id})

    tasks = list(enriched.tasks) if enriched.tasks else ([task] if task is not None else [])
    plan_versions = (
        list(enriched.plan_versions)
        if enriched.plan_versions
        else _derive_plan_versions(enriched, task)
    )
    state_snapshots = (
        list(enriched.state_snapshots)
        if enriched.state_snapshots
        else _derive_state_snapshots(enriched, task)
    )

    return enriched.model_copy(
        update={
            "trace": trace,
            "tasks": tasks,
            "plan_versions": plan_versions,
            "state_snapshots": state_snapshots,
        }
    )


def build_task_state_view(bundle: TraceBundleView) -> TaskStateView | None:
    enriched = ensure_cognitive_state(bundle)
    if not enriched.tasks:
        return None

    task = enriched.tasks[0]
    plan_versions = sorted(enriched.plan_versions, key=lambda item: item.revision)
    state_snapshots = sorted(enriched.state_snapshots, key=lambda item: item.snapshot_index)

    return TaskStateView(
        task=task,
        latest_plan=plan_versions[-1] if plan_versions else None,
        latest_snapshot=state_snapshots[-1] if state_snapshots else None,
        plan_revision_count=len(plan_versions),
        snapshot_count=len(state_snapshots),
    )


def _ensure_task(bundle: TraceBundleView) -> TaskRecord | None:
    if bundle.tasks:
        return bundle.tasks[0]

    status = _to_task_status(bundle.trace.status)
    intent = str(bundle.trace.metadata_json.get("intent") or "").strip()
    title = intent or _fallback_task_title(bundle)
    summary = _fallback_task_summary(bundle)
    task_id = bundle.trace.task_id or _stable_uuid("task", bundle.trace.id)

    return TaskRecord(
        id=task_id,
        session_id=bundle.session.id,
        trace_id=bundle.trace.id,
        title=title,
        status=status,
        owner=bundle.session.user_id,
        summary=summary,
        metadata_json={
            "workspace": bundle.session.metadata_json.get("workspace"),
            "intent": bundle.trace.metadata_json.get("intent"),
            "derived_from": "trace_bundle",
            "trace_kind": bundle.trace.trace_kind,
        },
        created_at=_bundle_created_at(bundle),
    )


def _derive_plan_versions(
    bundle: TraceBundleView,
    task: TaskRecord | None,
) -> list[PlanVersionRecord]:
    if task is None:
        return []

    candidates = []
    for step in sorted(bundle.steps, key=lambda item: item.step_index):
        step_deltas = [delta for delta in bundle.state_deltas if delta.step_id == step.id]
        is_plan_step = step.step_type == "plan_update" or any(
            delta.facet == "plan_state" for delta in step_deltas
        )
        if not is_plan_step:
            continue
        plan_delta = next(
            (delta for delta in step_deltas if delta.facet == "plan_state"),
            None,
        )
        plan_json = {}
        if plan_delta is not None and plan_delta.after_json is not None:
            plan_json = dict(plan_delta.after_json)
        if not plan_json:
            plan_json = {
                "step_type": step.step_type,
                "summary": step.summary,
                "metadata": step.metadata_json,
            }
        candidates.append((step, plan_delta, plan_json))

    if not candidates:
        return [
            PlanVersionRecord(
                id=_stable_uuid("plan", task.id, 0),
                task_id=task.id,
                trace_id=bundle.trace.id,
                revision=0,
                summary=task.summary or task.title,
                plan_json={
                    "title": task.title,
                    "intent": bundle.trace.metadata_json.get("intent"),
                },
                metadata_json={"derived_from": "task"},
                created_at=task.created_at,
            )
        ]

    plan_versions: list[PlanVersionRecord] = []
    for revision, (step, plan_delta, plan_json) in enumerate(candidates):
        plan_versions.append(
            PlanVersionRecord(
                id=_stable_uuid("plan", task.id, revision),
                task_id=task.id,
                trace_id=bundle.trace.id,
                step_id=step.id,
                revision=revision,
                summary=step.summary,
                plan_json=plan_json,
                metadata_json={
                    "derived_from": "step",
                    "step_type": step.step_type,
                    "facet": plan_delta.facet if plan_delta is not None else None,
                },
                created_at=_step_timestamp(step),
            )
        )
    return plan_versions


def _derive_state_snapshots(
    bundle: TraceBundleView,
    task: TaskRecord | None,
) -> list[StateSnapshotRecord]:
    snapshots: list[StateSnapshotRecord] = []
    current_state: dict[str, dict[str, object] | None] = {}

    for step in sorted(bundle.steps, key=lambda item: item.step_index):
        step_deltas = sorted(
            [delta for delta in bundle.state_deltas if delta.step_id == step.id],
            key=lambda item: item.facet,
        )
        if not step_deltas:
            continue

        for delta in step_deltas:
            current_state[delta.facet] = _delta_state_value(delta)

        snapshots.append(
            StateSnapshotRecord(
                id=_stable_uuid("snapshot", bundle.trace.id, step.step_index),
                trace_id=bundle.trace.id,
                step_id=step.id,
                task_id=task.id if task is not None else None,
                snapshot_index=step.step_index,
                state_json={
                    facet: value
                    for facet, value in sorted(current_state.items(), key=lambda item: item[0])
                },
                metadata_json={
                    "derived_from": "state_deltas",
                    "facets": [delta.facet for delta in step_deltas],
                    "delta_ids": [str(delta.id) for delta in step_deltas],
                },
                created_at=_step_timestamp(step),
            )
        )

    return snapshots


def _delta_state_value(delta: StateDeltaRecord) -> dict[str, object] | None:
    if delta.after_json is not None:
        return delta.after_json
    if delta.before_json is not None:
        return delta.before_json
    return None


def _bundle_created_at(bundle: TraceBundleView) -> datetime:
    candidates = [bundle.session.created_at, bundle.trace.created_at]
    return min(candidates)


def _fallback_task_title(bundle: TraceBundleView) -> str:
    for step in sorted(bundle.steps, key=lambda item: item.step_index):
        if step.summary:
            return step.summary
    return f"Trace {bundle.trace.id}"


def _fallback_task_summary(bundle: TraceBundleView) -> str | None:
    if bundle.trace.metadata_json.get("intent"):
        return str(bundle.trace.metadata_json["intent"])
    final_step = next(
        (
            step
            for step in sorted(bundle.steps, key=lambda item: item.step_index, reverse=True)
            if step.summary
        ),
        None,
    )
    return final_step.summary if final_step is not None else None


def _to_task_status(status: TraceStatus) -> TaskStatus:
    return TaskStatus(status.value)


def _step_timestamp(step) -> datetime:
    return step.ended_at or step.started_at or step.created_at or datetime.now(UTC)


def _stable_uuid(kind: str, *parts: UUID | int) -> UUID:
    suffix = ":".join(str(part) for part in parts)
    return uuid5(NAMESPACE_URL, f"aeris:{kind}:{suffix}")
