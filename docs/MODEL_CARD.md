# Model Card — BACKROW 11.0

## System type

Hybrid source-conditioned presentation-audit system:
- classical slide retrieval + geometric verification;
- third-party pretrained OCR;
- BACKROW custom learned visual-survival model;
- deterministic exact-information safety guards;
- transparent source-only room geometry baseline;
- optional real-field human calibration model that is **not bundled until real labels exist**.

## AudienceNet 2.0 — custom model

- version: `AudienceNet-2.0.0`;
- architecture: compact MLP, hidden layers **48 → 24**;
- runtime: exported JSON weights + NumPy, so scikit-learn is not required in production;
- features: **16** paired source/camera + optional room-geometry features;
- output: `SUPPORTED / WATCH / AT_RISK` probability distribution;
- training target: **physics-aware procedural projector/camera signal-survival curriculum**;
- split: group-disjoint by text-template family;
- calibration: temperature scaling recorded in model metadata;
- scope: **engineering visual-survival pretraining, not human eyesight/readability**.

Feature families:
- structural correlation;
- contrast ratio;
- sharpness ratio;
- glare/dark fractions;
- edge preservation;
- source text-region height;
- source OCR confidence;
- token/numeric/source-length signals;
- room availability;
- farthest-seat / screen-height ratio;
- BDM-relative source-region size;
- projected region height;
- visual angular region height.

Exact current procedural training statistics live in `AUDIENCENET_TRAINING_REPORT.json`. Current run: **1,440 balanced examples; macro-F1 0.9422** on the held-out procedural target, versus **0.4056** signal-threshold and **0.4789** geometry baselines. Those numbers are deliberately never presented as human accuracy.

## Third-party AI — Tesseract 5 LSTM OCR

Tesseract is used to recover exact source/audience text and numbers. BACKROW does not claim to have trained or invented it.

## Classical/non-AI components

- ORB local features;
- Hamming matching;
- RANSAC homography;
- perspective rectification;
- image statistics;
- exact numeric-token comparison;
- transparent BDM source-geometry comparator;
- fail-closed page/geometry policy.

## Evidence hierarchy

Hard evidence is intentionally allowed to overrule a soft learned model:

`exact numeric divergence / catastrophic OCR loss`
`>`
`strong exact source-camera recovery`
`>`
`AudienceNet procedural visual-survival evidence`
`>`
`weak image heuristics`

This avoids a neural classifier clearing a changed number such as `2.5% → 25%` or creating false red alarms when the exact phrase was cleanly recovered.

## AudienceNet contribution boundary

`ablation_benchmark.json` records generated-fixture interactions between the deterministic channel and AudienceNet. It verifies that:
- the learned channel can escalate at least one ambiguous deterministic case;
- direct exact evidence can override a pessimistic learned output;
- numeric hard guards remain independent.

This proves the channel is executed and can affect the system on the engineering fixtures. It **does not** prove human-readability gain. Only the locked field study can establish that.

## Optional FieldCalibrator

`field_calibrator.py` implements a compact logistic human-recovery calibration head. No `models/field_calibrator.json` is bundled in an unvalidated release.

`training/train_field_calibrator.py` now requires:
- real exported field-study responses;
- fixed-exposure logs for every target;
- at least 100 participant-region judgments;
- at least 8 independent slide groups;
- both recovered and unrecovered labels in group-disjoint train/test splits.

The locked evaluator refuses a final study that was used to train the calibrator.

## Known failure modes

- camera does not contain enough of the projected screen;
- near-identical deck pages produce ambiguous retrieval;
- transition/motion blur;
- no OCR-detectable source text;
- unsupported OCR language or unusual glyphs;
- charts/images where exact text is not the right evidence target;
- camera exposure or dynamic range differs materially from human perception;
- procedural-to-real domain shift;
- camera cannot recover text a person can recover, or vice versa.

Uncertain matching/geometry fails closed rather than manufacturing a result.

## Intended use

Presentation rehearsal/preflight in classrooms, competitions, meetings, pitch rooms, conference rooms, and similar environments.

## Not intended for

Medical eyesight assessment, legal accessibility certification, safety-critical display certification, or guaranteed audience comprehension.
