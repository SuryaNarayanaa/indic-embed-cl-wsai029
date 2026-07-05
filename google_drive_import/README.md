# Google Drive Project Import

Imported on 2026-07-01 for the WSAI / IITM multilingual Indic text embedding project.

## Search Anchors

Drive was searched with project-specific terms including:

- `WSAI`
- `Indic Embedding`
- `LaBSE Indic`
- `IN22 Indic`
- `Samanantar FLORES`

## Local Layout

- `admin/` - WSAI daily/weekly activity tracker export.
- `data/reference/` - reference workbook for Indic-Indic language pairs.
- `data/labse_all_pairs_indic_finetuning/` - large training and validation CSVs.
- `results/indic_embedding_benchmark/` - FLORES benchmark metrics and plots.
- `results/indic_embedding_benchmark_samanantar/` - Samanantar benchmark metrics.
- `results/labse_indic_indic_benchmark/` - LaBSE Indic-Indic benchmark summaries.
- `results/labse_all_pairs_indic_finetuning/` - finetuning metrics, eval deltas, and exported metrics archive.

## Import Safety

Run this before consuming imported Drive artifacts:

```powershell
python scripts\audit_google_drive_import.py --quarantine
```

The audit checks for Google Drive warning, login, unauthorized, quota, and HTML placeholder payloads that can be saved with data-like filenames after failed browser downloads. Bad files are moved to `_quarantine/` and recorded in `docs/missing_artifacts_manifest.md`.

The notebooks and scripts install `scripts/import_guard.py`, which wraps `pandas.read_csv` and `pandas.read_excel` so these placeholders fail loudly instead of being consumed as training or evaluation data.

## Inventory

See `download_manifest.csv` for the original local file inventory and `import_audit_manifest.csv` for the latest placeholder audit.

Current verified audit: 59 files, 483,342,954 bytes, with no Google Drive warning, login, unauthorized, quota, or HTML placeholder payloads. The specifically checked `data/labse_all_pairs_indic_finetuning/train_pairs_used.csv` is a large CSV payload, not a Drive placeholder page.
