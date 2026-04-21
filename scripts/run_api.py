from __future__ import annotations

import sys
from pathlib import Path

import uvicorn

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    uvicorn.run("apps.api.app.main:app", host="0.0.0.0", port=8080)


if __name__ == "__main__":
    main()
