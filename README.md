`# WSAI Workspace

This workspace is organized by artifact type so reports, experiments, and source files are easier to find.

## Folder Map

- `reports/docx/` - Word report drafts and final report documents.
- `reports/pdf/` - PDF reports and exported summaries.
- `reports/certificates/` - Certificates and official internship documents.
- `notebooks/` - Jupyter notebooks for LaBSE/Indic embedding experiments.
- `results/zip_packages/` - Compressed result bundles and upload packages.
- `latex/` - LaTeX source files.

## Notes

- Original filenames were preserved to avoid breaking references.
- Similar files such as numbered notebook copies and duplicate-looking PDF exports were kept rather than deleted.
- Imported Drive artifacts are guarded against browser warning/login placeholders. Run `python scripts\audit_google_drive_import.py --quarantine` before using `google_drive_import/`; see `docs/missing_artifacts_manifest.md` for missing-artifact recovery steps.
