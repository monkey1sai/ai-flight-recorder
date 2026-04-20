from __future__ import annotations

import base64
import csv
import hashlib
import os
import shutil
import zipfile
from io import StringIO
from pathlib import Path


def _user_home() -> Path:
    for key in ("USERPROFILE", "HOME"):
        value = os.environ.get(key)
        if value:
            return Path(value)
    return Path(r"C:\Users\IOT")


CACHE_ROOT = _user_home() / "AppData" / "Local" / "uv" / "cache"
WHEELS_ROOT = CACHE_ROOT / "wheels-v5" / "pypi"
OUTPUT_ROOT = Path(__file__).resolve().parents[1] / "vendor" / "python" / "wheels"
REPO_ROOT = Path(__file__).resolve().parents[1]

PACKAGE_SPECS = [
    {
        "cache_dir": "annotated-types",
        "cache_key": "0.7.0-py3-none-any",
        "wheel": "annotated_types-0.7.0-py3-none-any.whl",
    },
    {
        "cache_dir": "anyio",
        "cache_key": "4.13.0-py3-none-any",
        "wheel": "anyio-4.13.0-py3-none-any.whl",
    },
    {
        "cache_dir": "certifi",
        "cache_key": "2026.2.25-py3-none-any",
        "wheel": "certifi-2026.2.25-py3-none-any.whl",
    },
    {
        "cache_dir": "colorama",
        "cache_key": "0.4.6-py2.py3-none-any",
        "wheel": "colorama-0.4.6-py2.py3-none-any.whl",
    },
    {
        "cache_dir": "fastapi",
        "cache_key": "0.116.1-py3-none-any",
        "wheel": "fastapi-0.116.1-py3-none-any.whl",
    },
    {
        "cache_dir": "h11",
        "cache_key": "0.16.0-py3-none-any",
        "wheel": "h11-0.16.0-py3-none-any.whl",
    },
    {
        "cache_dir": "httpcore",
        "cache_key": "1.0.9-py3-none-any",
        "wheel": "httpcore-1.0.9-py3-none-any.whl",
    },
    {
        "cache_dir": "httpx",
        "cache_key": "0.28.1-py3-none-any",
        "wheel": "httpx-0.28.1-py3-none-any.whl",
    },
    {
        "cache_dir": "idna",
        "cache_key": "3.11-py3-none-any",
        "wheel": "idna-3.11-py3-none-any.whl",
    },
    {
        "cache_dir": "iniconfig",
        "cache_key": "2.3.0-py3-none-any",
        "wheel": "iniconfig-2.3.0-py3-none-any.whl",
    },
    {
        "cache_dir": "packaging",
        "cache_key": "25.0-py3-none-any",
        "wheel": "packaging-25.0-py3-none-any.whl",
    },
    {
        "cache_dir": "pluggy",
        "cache_key": "1.6.0-py3-none-any",
        "wheel": "pluggy-1.6.0-py3-none-any.whl",
    },
    {
        "cache_dir": "pydantic",
        "cache_key": "2.12.5-py3-none-any",
        "wheel": "pydantic-2.12.5-py3-none-any.whl",
    },
    {
        "cache_dir": "pydantic-core",
        "cache_key": "2.41.5-cp312-cp312-win_amd64",
        "wheel": "pydantic_core-2.41.5-cp312-cp312-win_amd64.whl",
    },
    {
        "cache_dir": "pygments",
        "cache_key": "2.19.2-py3-none-any",
        "wheel": "pygments-2.19.2-py3-none-any.whl",
    },
    {
        "cache_dir": "pytest",
        "cache_key": "8.4.2-py3-none-any",
        "wheel": "pytest-8.4.2-py3-none-any.whl",
    },
    {
        "cache_dir": "ruff",
        "cache_key": "0.12.8-py3-none-win_amd64",
        "wheel": "ruff-0.12.8-py3-none-win_amd64.whl",
    },
    {
        "cache_dir": "sniffio",
        "cache_key": "1.3.1-py3-none-any",
        "wheel": "sniffio-1.3.1-py3-none-any.whl",
    },
    {
        "cache_dir": "starlette",
        "cache_key": "0.47.2-py3-none-any",
        "wheel": "starlette-0.47.2-py3-none-any.whl",
    },
    {
        "cache_dir": "typing-extensions",
        "cache_key": "4.15.0-py3-none-any",
        "wheel": "typing_extensions-4.15.0-py3-none-any.whl",
    },
    {
        "cache_dir": "typing-inspection",
        "cache_key": "0.4.2-py3-none-any",
        "wheel": "typing_inspection-0.4.2-py3-none-any.whl",
    },
]


def pointer_path(cache_dir: str, cache_key: str) -> Path:
    return WHEELS_ROOT / cache_dir / cache_key


def archive_path(cache_dir: str, cache_key: str) -> Path:
    pointer = pointer_path(cache_dir, cache_key)
    if not pointer.exists():
        raise FileNotFoundError(f"Missing uv cache pointer: {pointer}")

    relative = pointer.read_text(encoding="utf-8").strip()
    archive = CACHE_ROOT / relative
    if not archive.exists():
        raise FileNotFoundError(f"Missing uv cache archive: {archive}")

    return archive


def build_wheel(archive: Path, target: Path) -> None:
    if target.exists():
        return

    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(".zip")
    if tmp.exists():
        tmp.unlink()

    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for item in sorted(archive.rglob("*")):
            if item.is_dir():
                continue
            zf.write(item, item.relative_to(archive).as_posix())

    if target.exists():
        target.unlink()
    shutil.move(tmp, target)


def _record_row(path: str, content: bytes) -> list[str]:
    digest = hashlib.sha256(content).digest()
    encoded = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return [path, f"sha256={encoded}", str(len(content))]


def build_mypy_compat_wheel() -> None:
    target = OUTPUT_ROOT / "mypy-1.19.1-py3-none-any.whl"

    package_source = REPO_ROOT / "tools" / "mypy_compat" / "src" / "mypy_compat" / "__init__.py"
    dist_info = "mypy-1.19.1.dist-info"
    metadata = "\n".join(
        [
            "Metadata-Version: 2.1",
            "Name: mypy",
            "Version: 1.19.1",
            "Summary: Offline mypy-compatible wrapper backed by Pyright for bootstrap validation.",
            "Requires-Python: >=3.12",
            "",
        ]
    ).encode("utf-8")
    wheel = "\n".join(
        [
            "Wheel-Version: 1.0",
            "Generator: aeris-offline-builder",
            "Root-Is-Purelib: true",
            "Tag: py3-none-any",
            "",
        ]
    ).encode("utf-8")
    entry_points = "[console_scripts]\nmypy = mypy_compat:main\n".encode("utf-8")

    files: dict[str, bytes] = {
        "mypy_compat/__init__.py": package_source.read_bytes(),
        f"{dist_info}/METADATA": metadata,
        f"{dist_info}/WHEEL": wheel,
        f"{dist_info}/entry_points.txt": entry_points,
    }

    record_buffer = StringIO()
    writer = csv.writer(record_buffer, lineterminator="\n")
    for path, content in files.items():
        writer.writerow(_record_row(path, content))
    writer.writerow([f"{dist_info}/RECORD", "", ""])
    files[f"{dist_info}/RECORD"] = record_buffer.getvalue().encode("utf-8")

    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(".zip")
    if tmp.exists():
        tmp.unlink()

    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path, content in files.items():
            zf.writestr(path, content)

    if target.exists():
        target.unlink()
    shutil.move(tmp, target)
    print(f"built {target.name}")


def main() -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    for spec in PACKAGE_SPECS:
        archive = archive_path(spec["cache_dir"], spec["cache_key"])
        build_wheel(archive, OUTPUT_ROOT / spec["wheel"])
        print(f"built {spec['wheel']}")
    build_mypy_compat_wheel()


if __name__ == "__main__":
    main()
