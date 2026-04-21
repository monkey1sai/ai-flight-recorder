from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path.cwd().resolve()


def _node_candidates() -> list[Path]:
    env_value = os.environ.get("AERIS_NODE_EXE")
    candidates = []
    if env_value:
        candidates.append(Path(env_value))

    visual_studio_node = (
        r"C:\Program Files\Microsoft Visual Studio\2022\Professional\MSBuild\Microsoft"
        r"\VisualStudio\NodeJs\node.exe"
    )
    candidates.extend(
        [
            Path(r"C:\Program Files\nodejs\node.exe"),
            Path(visual_studio_node),
            Path(r"C:\Users\IOT\.lmstudio\.internal\utils\node.exe"),
        ]
    )
    return candidates


def _resolve_node() -> Path:
    for candidate in _node_candidates():
        if candidate.exists():
            return candidate
    raise FileNotFoundError("No working Node.js runtime found for the offline mypy shim.")


def _resolve_pyright() -> Path:
    pyright = Path(r"C:\Users\IOT\AppData\Roaming\npm\node_modules\pyright\index.js")
    if not pyright.exists():
        raise FileNotFoundError("Global pyright installation not found for the offline mypy shim.")
    return pyright


def main() -> int:
    repo_root = _repo_root()
    python_path = repo_root / ".venv" / "Scripts" / "python.exe"
    if not python_path.exists():
        raise FileNotFoundError(f"Expected project interpreter at {python_path}")

    command = [
        str(_resolve_node()),
        str(_resolve_pyright()),
        "--pythonpath",
        str(python_path),
        "--pythonversion",
        "3.12",
        "--level",
        "error",
        *sys.argv[1:],
    ]
    return subprocess.run(command, cwd=repo_root, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
