# Import Manifest

## Source Checked

- Google Drive connector: requested, but no callable Drive search/download tools were exposed in this session.
- In-app browser fallback: unavailable in this session.
- Local project cache: searched `C:\Users\Surya Narayanaa\Downloads`, `Documents`, `Desktop`, and `OneDrive` for project-related notebooks.

## Imported Notebook Groups

- `notebooks/00_benchmarks/` - Indic embedding, Samanantar, FLORES, and IN22 benchmark notebooks.
- `notebooks/03_finetuning/` - Additional downloaded checkpointed fine-tuning notebook.
- `notebooks/04_phase_finetuning/` - Phase 1-4 LaBSE fine-tuning notebooks.
- `notebooks/05_evaluation/` - Phase and source-aware evaluation notebooks.

## Imported Supporting Files

- `data/reference/indic_indic_462_pairs.xlsx`
- `scripts/indic_embedding_benchmark_colab.py`
- `scripts/labse_indic_alignment_directed_pairs_gen_train_conv_eval.py`
- `results/packages/indic_embedding_benchmark_colab_package.zip`

## Google Drive Placeholder Audit

Run from the workspace root:

```powershell
python scripts\audit_google_drive_import.py --quarantine
```

Latest local audit: 59 files under `google_drive_import/`, 0 Google Drive warning/login/unauthorized placeholder payloads, and 0 files quarantined. The named file `google_drive_import/data/labse_all_pairs_indic_finetuning/train_pairs_used.csv` passed this placeholder audit.

If a future audit finds a bad file, it is moved to `google_drive_import/_quarantine/` with its original relative path preserved. Replace the original path with a fresh authenticated download, then rerun the audit before running notebooks or scripts.

## Intentionally Not Imported

- `C:\Users\Surya Narayanaa\Downloads\labse_finetuning_important_results.zip` - approximately 7 GB.
- `C:\Users\Surya Narayanaa\Downloads\labse_finetuning_important_results\` - corresponding extracted results folder.
- `C:\Users\Surya Narayanaa\Downloads\WhatsApp Chat with Glen Enosh WSAI IITM.zip` - likely personal chat export, not appropriate for a public GitHub repo.

Large result artifacts should be stored outside normal Git history, for example in a GitHub Release, Google Drive, Hugging Face Hub, or another artifact store.
