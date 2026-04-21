from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class BlobWriteResult:
    checksum: str
    storage_ref: str
    size_bytes: int


class LocalBlobStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def put_json(self, namespace: str, identifier: str, payload: object) -> BlobWriteResult:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        return self._write_bytes(
            namespace=namespace,
            identifier=identifier,
            body=body,
            suffix=".json",
        )

    def put_text(
        self, namespace: str, identifier: str, text: str, suffix: str = ".txt"
    ) -> BlobWriteResult:
        return self._write_bytes(
            namespace=namespace,
            identifier=identifier,
            body=text.encode("utf-8"),
            suffix=suffix,
        )

    def _write_bytes(
        self, namespace: str, identifier: str, body: bytes, suffix: str
    ) -> BlobWriteResult:
        checksum = f"sha256:{hashlib.sha256(body).hexdigest()}"
        namespace_dir = self.root / namespace
        namespace_dir.mkdir(parents=True, exist_ok=True)
        file_name = f"{identifier}{suffix}"
        target = namespace_dir / file_name
        target.write_bytes(body)
        return BlobWriteResult(
            checksum=checksum,
            storage_ref=target.resolve().as_uri(),
            size_bytes=len(body),
        )
