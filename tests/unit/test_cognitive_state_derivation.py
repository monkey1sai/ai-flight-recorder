from apps.api.app.cognitive import build_task_state_view, ensure_cognitive_state
from packages.testkit import load_trace_bundle_fixture


def test_cognitive_state_derivation_builds_task_plan_and_snapshots() -> None:
    bundle = ensure_cognitive_state(load_trace_bundle_fixture())
    task_state = build_task_state_view(bundle)

    assert len(bundle.tasks) == 1
    assert bundle.trace.task_id == bundle.tasks[0].id
    assert len(bundle.plan_versions) >= 1
    assert len(bundle.state_snapshots) >= 1
    assert task_state is not None
    assert task_state.plan_revision_count == len(bundle.plan_versions)
    assert task_state.snapshot_count == len(bundle.state_snapshots)
    assert "plan_state" in (
        task_state.latest_snapshot.state_json if task_state.latest_snapshot else {}
    )
