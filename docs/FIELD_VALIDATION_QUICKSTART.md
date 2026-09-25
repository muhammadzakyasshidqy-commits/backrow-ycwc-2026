# BACKROW 11.0 — Physical Validation Console

Open `/validate.html` after starting BACKROW with the field-study launcher.

This page exists so the remaining physical evidence can be collected without spreadsheets or hand-edited JSON.

## A. Manual vs BACKROW workflow

Use the same frozen 15+ slide deck for both conditions.

Record:
- total slides;
- total known critical failures;
- critical failures found by manual inspection;
- critical failures found by BACKROW;
- actual elapsed time for each workflow.

Use the built-in timers. Export `BACKROW_WORKFLOW.json`.

## B. Stable-frame whole-deck retrieval

1. Upload the exact PDF once.
2. Select the expected slide before capture.
3. Open the audience-position camera.
4. Capture stable frames from multiple slides and conditions.
5. BACKROW calls the match-only endpoint and records matched page, rejection, score, inliers, inlier ratio, screen coverage, and latency.
6. Export `BACKROW_DECK_MATCH.json`.

A rejected ambiguous frame must remain a rejection; do not relabel it as a correct match.

## C. Locked evaluation

Use the exported workflow/deck files together with completed locked reader-study exports in `training/evaluate_locked_field_studies.py`.

The console is for measurement, not a second product dashboard. It is intentionally separate from the main presenter workflow.
