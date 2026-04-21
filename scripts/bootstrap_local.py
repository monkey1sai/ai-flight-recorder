from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from apps.api.app.bootstrap import bootstrap_live_local_environment
    from apps.api.app.settings import get_settings

    settings = get_settings()
    migration_dir = Path("packages/schema/migrations")
    bundle = bootstrap_live_local_environment(
        settings=settings,
        migration_dir=migration_dir,
        seed_demo=settings.seed_demo_on_bootstrap,
    )
    if bundle is None:
        print("bootstrap_complete=no_seed")
        return
    print(f"bootstrap_complete=seeded trace_id={bundle.trace.id}")


if __name__ == "__main__":
    main()
