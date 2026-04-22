from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from apps.api.app.connectors import LiveDriveConnector
    from apps.api.app.settings import get_settings

    settings = get_settings()
    connector = LiveDriveConnector(settings)
    status = connector.authorize_interactive()
    print(f"mode={status.mode}")
    print(f"authorized={str(status.authorized).lower()}")
    print(f"token_present={str(status.token_present).lower()}")
    print(f"can_refresh={str(status.can_refresh).lower()}")
    if status.blocked_reason is not None:
        print(f"blocked_reason={status.blocked_reason}")


if __name__ == "__main__":
    main()
