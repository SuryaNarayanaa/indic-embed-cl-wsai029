# Missing and Quarantined Artifact Manifest

Generated: 2026-07-01 14:18:54 UTC
Audited root: `C:\Academics\wsai\google_drive_import`

## Current Audit Result

No Google Drive warning, login, unauthorized, or HTML placeholder payloads were found in the audited import tree.

## Quarantine

No files were quarantined in this audit run.

## Known Missing Large Artifacts

| Artifact | Status | Recovery action |
| --- | --- | --- |
| `C:\Users\Surya Narayanaa\Downloads\labse_finetuning_important_results.zip` | Intentionally not imported because it is approximately 7 GB | Re-download from the original Drive item or copy from the local Downloads folder, then keep it outside Git or attach it to an external artifact store. |
| `C:\Users\Surya Narayanaa\Downloads\labse_finetuning_important_results\` | Intentionally not imported extracted results folder | Restore from the zip above or from the original Drive folder. |
| Full fine-tuned model checkpoint directories | Not present in this lightweight workspace import | Recover from Google Drive/Hugging Face/artifact storage before running model-loading notebooks that expect checkpoint folders. |

## Recovery Steps

1. Open the original file or folder in Google Drive while signed in to the account that has access.
2. For binary files, use Drive's Download action. For Google-native files, use File > Download and choose the required format such as `.xlsx`, `.docx`, or `.ipynb`.
3. Replace the missing or quarantined path under `google_drive_import/` with the newly downloaded artifact.
4. Run `python scripts/audit_google_drive_import.py --quarantine` from the workspace root.
5. Only rerun notebooks or scripts after the audit reports zero bad files.
