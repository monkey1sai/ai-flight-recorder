from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from apps.api.app.settings import get_settings
    from packages.edge_sdk import AerisEdgeClient, build_demo_request

    settings = get_settings()
    client = AerisEdgeClient(settings.api_base_url)
    receipt = client.ingest(build_demo_request())
    print(f"ingested trace_id={receipt.trace_id} session_id={receipt.session_id}")


if __name__ == "__main__":
    main()
