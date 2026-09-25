# BACKROW 11.0 — Locked Field Study Quick Start

The collection workflow is already built. The physical work is deliberately reduced to setup + readers; do not hand-edit study JSON.

## 1. Start the field server

On Windows:

```text
RUN_FIELD_STUDY_WINDOWS.bat
```

Use only a trusted local LAN. Do not expose the development study server directly to the public internet.

## 2. Measure the physical setup

Record the actual:

- audience/viewer distance in metres;
- projected active-image height in metres;
- room ID;
- projector/display ID;
- camera/device ID;
- position label (near/mid/far);
- lighting condition.

Do not reuse judge-demo values unless they were physically measured.

## 3. Collect workflow + deck-match measurements

Open:

```text
http://<presenter-ip>:8080/validate.html
```

The validation console provides two independent collections:

### Manual vs BACKROW timing

- choose a 15+ slide deck;
- enter total known critical failures only after the deck is frozen;
- run the manual workflow timer;
- run BACKROW workflow timer;
- record failures found by each;
- export `BACKROW_WORKFLOW.json`.

### Real stable-frame deck retrieval

- upload the exact PDF once;
- choose the expected slide;
- open the real audience-position camera;
- capture stable frames (prefer multiple slides/conditions rather than many copies of one easy frame);
- export `BACKROW_DECK_MATCH.json`.

## 4. Create a blinded reader study

In the main BACKROW analysis, create the locked human field study.

The presenter/admin console contains the source truth and target overlays. The participant endpoint intentionally does not.

Study creation freezes:

- randomized presentation order;
- target list;
- timed exposure interval (default 6 s, allowed 3–12 s).

## 5. Run readers

For every target:

1. seat the reader at the specified physical position;
2. participant opens the generated `/study.html?...` URL;
3. presenter presses **Start timed exposure** in the admin console;
4. the target is visible only for the frozen duration;
5. reader types exactly what they recovered;
6. reader submits once; the response cannot be overwritten.

Readers must not see source truth, camera OCR, BACKROW predictions, or the admin screen.

## 6. Export raw studies

Export each completed study from the presenter/admin console. Preserve the raw export and its SHA-256.

Keep calibration/development studies separate from locked final studies.

## 7. Optional human calibration

Only calibration/development studies may be used here:

```bash
python training/train_field_calibrator.py calibration_room1.json calibration_room2.json \
  --out models/field_calibrator.json
```

Training refuses insufficient or protocol-invalid data. The runtime remains `field_calibrator.available=false` until a valid model exists.

## 8. Run the locked evaluator

```bash
python training/evaluate_locked_field_studies.py locked_room1.json locked_room2.json \
  --workflow-json BACKROW_WORKFLOW.json \
  --deck-json BACKROW_DECK_MATCH.json \
  --out docs/LOCKED_FIELD_EVALUATION.json
```

The evaluator checks sample coverage, timed-exposure logs, study/calibration leakage, confidence intervals, manual workflow results, and deck-match accuracy. It exits failing if a predeclared kill gate is missed.

## Minimum user action remaining

The software side is prepared. The unavoidable external work is:

1. connect a real projector/display;
2. put the camera at measured audience positions;
3. run multiple real rooms/conditions;
4. recruit naïve readers;
5. run the built-in timed study and validation console;
6. return the generated JSON exports for final analysis.
