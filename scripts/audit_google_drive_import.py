"""Audit Google Drive imports and quarantine placeholder pages."""

from __future__ import annotations

import argparse
import csv
import hashlib
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from import_guard import classify_placeholder


SIGNATURE_EXTENSIONS = {".csv", ".xlsx", ".xls", ".zip", ".png", ".json"}
SCAN_EXTENSIONS = {".csv", ".xlsx", ".xls", ".zip", ".png", ".json", ".docx", ".pdf"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_file(path: Path, root: Path) -> dict[str, str]:
    rel = path.relative_to(root).as_posix()
    size = path.stat().st_size
    suffix = path.suffix.lower()
    issues: list[str] = []

    if suffix in SCAN_EXTENSIONS:
        placeholder = classify_placeholder(path)
        if placeholder:
            issues.append(f"placeholder:{placeholder}")

    if size == 0:
        issues.append("empty")

    prefix = path.read_bytes()[:16]
    if suffix in {".xlsx", ".docx", ".zip"}:
        if not prefix.startswith(b"PK"):
            issues.append("zip_signature_mismatch")
        else:
            try:
                with zipfile.ZipFile(path) as zf:
                    corrupt_member = zf.testzip()
                if corrupt_member:
                    issues.append(f"zip_corrupt:{corrupt_member}")
            except Exception as exc:  # noqa: BLE001 - report exact audit failure.
                issues.append(f"zip_open_failed:{type(exc).__name__}")

    if suffix == ".png" and not prefix.startswith(b"\x89PNG\r\n\x1a\n"):
        issues.append("png_signature_mismatch")

    return {
        "path": rel,
        "bytes": str(size),
        "sha256": sha256(path) if suffix in SIGNATURE_EXTENSIONS else "",
        "status": "bad" if issues else "ok",
        "issues": ";".join(issues),
    }


def quarantine_file(path: Path, root: Path, quarantine_root: Path) -> Path:
    destination = quarantine_root / path.relative_to(root)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(path), str(destination))
    return destination


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["path", "bytes", "sha256", "status", "issues"])
        writer.writeheader()
        writer.writerows(rows)


def write_missing_manifest(path: Path, root: Path, rows: list[dict[str, str]], quarantined: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bad_rows = [row for row in rows if row["status"] == "bad"]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        "# Missing and Quarantined Artifact Manifest",
        "",
        f"Generated: {now}",
        f"Audited root: `{root}`",
        "",
        "## Current Audit Result",
        "",
    ]

    if bad_rows:
        lines.append("The following imported files were identified as invalid and must be recovered:")
        lines.append("")
        lines.append("| Path | Bytes | Issue |")
        lines.append("| --- | ---: | --- |")
        for row in bad_rows:
            lines.append(f"| `{row['path']}` | {row['bytes']} | `{row['issues']}` |")
    else:
        lines.append("No Google Drive warning, login, unauthorized, or HTML placeholder payloads were found in the audited import tree.")

    lines.extend(["", "## Quarantine", ""])
    if quarantined:
        lines.append("| Original path | Quarantine path | Issue |")
        lines.append("| --- | --- | --- |")
        for row in quarantined:
            lines.append(f"| `{row['path']}` | `{row['quarantine_path']}` | `{row['issues']}` |")
    else:
        lines.append("No files were quarantined in this audit run.")

    lines.extend(
        [
            "",
            "## Known Missing Large Artifacts",
            "",
            "| Artifact | Status | Recovery action |",
            "| --- | --- | --- |",
            "| `C:\\Users\\Surya Narayanaa\\Downloads\\labse_finetuning_important_results.zip` | Intentionally not imported because it is approximately 7 GB | Re-download from the original Drive item or copy from the local Downloads folder, then keep it outside Git or attach it to an external artifact store. |",
            "| `C:\\Users\\Surya Narayanaa\\Downloads\\labse_finetuning_important_results\\` | Intentionally not imported extracted results folder | Restore from the zip above or from the original Drive folder. |",
            "| Full fine-tuned model checkpoint directories | Not present in this lightweight workspace import | Recover from Google Drive/Hugging Face/artifact storage before running model-loading notebooks that expect checkpoint folders. |",
            "",
            "## Recovery Steps",
            "",
            "1. Open the original file or folder in Google Drive while signed in to the account that has access.",
            "2. For binary files, use Drive's Download action. For Google-native files, use File > Download and choose the required format such as `.xlsx`, `.docx`, or `.ipynb`.",
            "3. Replace the missing or quarantined path under `google_drive_import/` with the newly downloaded artifact.",
            "4. Run `python scripts/audit_google_drive_import.py --quarantine` from the workspace root.",
            "5. Only rerun notebooks or scripts after the audit reports zero bad files.",
            "",
        ]
    )

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default="google_drive_import", help="Import tree to audit.")
    parser.add_argument("--output", default="google_drive_import/import_audit_manifest.csv", help="CSV audit manifest path.")
    parser.add_argument("--missing-manifest", default="docs/missing_artifacts_manifest.md", help="Markdown missing-artifact manifest path.")
    parser.add_argument("--quarantine-dir", default="google_drive_import/_quarantine", help="Quarantine directory.")
    parser.add_argument("--quarantine", action="store_true", help="Move bad files into the quarantine directory.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        raise FileNotFoundError(root)

    quarantine_root = Path(args.quarantine_dir).resolve()
    rows: list[dict[str, str]] = []
    quarantined: list[dict[str, str]] = []

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if quarantine_root in path.resolve().parents:
            continue
        if path.resolve() == Path(args.output).resolve():
            continue

        row = inspect_file(path, root)
        rows.append(row)
        if args.quarantine and row["status"] == "bad":
            destination = quarantine_file(path, root, quarantine_root)
            quarantined.append({**row, "quarantine_path": destination.relative_to(root).as_posix()})

    write_csv(Path(args.output), rows)
    write_missing_manifest(Path(args.missing_manifest), root, rows, quarantined)

    bad_count = sum(1 for row in rows if row["status"] == "bad")
    print(f"Audited {len(rows)} files under {root}")
    print(f"Bad files: {bad_count}")
    print(f"Wrote {args.output}")
    print(f"Wrote {args.missing_manifest}")
    if args.quarantine:
        print(f"Quarantined {len(quarantined)} files into {quarantine_root}")

    return 1 if bad_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
