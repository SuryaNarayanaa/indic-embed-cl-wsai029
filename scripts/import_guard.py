"""Guards against accidentally loading Google Drive placeholder pages as data."""

from __future__ import annotations

import io
import os
from pathlib import Path
from typing import Any, BinaryIO


READ_BYTES = 65536

PLACEHOLDER_MARKERS = (
    b"<!doctype html",
    b"<html",
    b"accounts.google.com",
    b"servicelogin",
    b"uc-download-link",
    b"download_warning",
    b"virus scan warning",
    b"google drive can't scan",
    b"you need access",
    b"access denied",
    b"unauthorized",
    b"error 403",
    b"quota exceeded",
)


class PlaceholderImportError(ValueError):
    """Raised when an import artifact is a browser/auth placeholder, not data."""


def _read_prefix(path_or_buffer: Any, read_bytes: int = READ_BYTES) -> bytes:
    if isinstance(path_or_buffer, (str, os.PathLike)):
        with open(path_or_buffer, "rb") as f:
            return f.read(read_bytes)

    if isinstance(path_or_buffer, io.BytesIO):
        pos = path_or_buffer.tell()
        try:
            path_or_buffer.seek(0)
            return path_or_buffer.read(read_bytes)
        finally:
            path_or_buffer.seek(pos)

    if isinstance(path_or_buffer, io.StringIO):
        pos = path_or_buffer.tell()
        try:
            path_or_buffer.seek(0)
            return path_or_buffer.read(read_bytes).encode("utf-8", errors="ignore")
        finally:
            path_or_buffer.seek(pos)

    if hasattr(path_or_buffer, "read") and hasattr(path_or_buffer, "seek"):
        stream: BinaryIO = path_or_buffer
        pos = stream.tell()
        try:
            stream.seek(0)
            chunk = stream.read(read_bytes)
            if isinstance(chunk, str):
                return chunk.encode("utf-8", errors="ignore")
            return chunk
        finally:
            stream.seek(pos)

    return b""


def classify_placeholder(path_or_buffer: Any) -> str | None:
    """Return a reason if the payload looks like a Drive/browser placeholder."""

    prefix = _read_prefix(path_or_buffer)
    if not prefix:
        return None

    lowered = prefix.lower().lstrip()
    if lowered.startswith(b"<!doctype html") or lowered.startswith(b"<html"):
        return "html payload"

    for marker in PLACEHOLDER_MARKERS:
        if marker in lowered:
            return marker.decode("utf-8", errors="replace")

    return None


def assert_not_placeholder(path_or_buffer: Any, *, label: str | None = None) -> None:
    reason = classify_placeholder(path_or_buffer)
    if reason is None:
        return

    name = label
    if name is None and isinstance(path_or_buffer, (str, os.PathLike)):
        name = str(Path(path_or_buffer))
    if name is None:
        name = "<file-like object>"

    raise PlaceholderImportError(
        f"{name} looks like a Google Drive warning/login/unauthorized page "
        f"({reason}), not a usable data artifact. Re-download it with an "
        "authenticated Drive export/download and rerun the import audit before "
        "using it."
    )


def install_pandas_guards() -> None:
    """Patch pandas readers in the current Python process."""

    import pandas as pd

    if getattr(pd, "_wsai_import_guard_installed", False):
        return

    original_read_csv = pd.read_csv
    original_read_excel = pd.read_excel

    def guarded_read_csv(filepath_or_buffer: Any, *args: Any, **kwargs: Any):
        assert_not_placeholder(filepath_or_buffer)
        return original_read_csv(filepath_or_buffer, *args, **kwargs)

    def guarded_read_excel(io_obj: Any, *args: Any, **kwargs: Any):
        assert_not_placeholder(io_obj)
        return original_read_excel(io_obj, *args, **kwargs)

    pd.read_csv = guarded_read_csv
    pd.read_excel = guarded_read_excel
    pd._wsai_import_guard_installed = True

