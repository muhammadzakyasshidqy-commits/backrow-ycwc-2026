# Dataset Card — BACKROW 11.0

## A. AudienceNet procedural curriculum

Purpose: engineering pretraining/stress coverage for source-camera visual-survival patterns before real human field labels exist.

Current generation covers:
- 48 text-template families;
- supported/watch/at-risk curriculum strata;
- multiple installed font families;
- numbers, percentages, times, short labels and sentences;
- randomized blur, resolution loss, washout/exposure, compression, glare and related camera/projection degradations;
- optional physical room geometry across multiple screen heights and viewing ratios.

Current exact report (`AUDIENCENET_TRAINING_REPORT.json`):
- total: **1,440**;
- class distribution: **480 / 480 / 480**;
- split: group-disjoint by text-template family;
- human labels: **none**.

### Valid claims

- model can be trained/exported/reproduced;
- model outperforms the included simple baselines on its stated procedural curriculum;
- custom inference runs in the production pipeline.

### Invalid claims

- “94.2% accurate for humans”;
- real-room/projector generalization;
- medical/visual-acuity performance;
- prevalence of unreadable slides.

## B. Bundled engineering fixtures

`assets/` contains generated source slides, audience-view transforms, a targeted fixed-slide pair, and a three-page PDF used for regression tests of:
- alignment;
- exact-number loss;
- glare/washout;
- blur and low resolution;
- page-index-free deck retrieval;
- wrong-pair rejection;
- repair → rescan.

These fixtures are development/regression assets and are **not** a locked final evaluation.

## C. External human-legibility research (not bundled training data)

The project research audit documents adjacent public human-legibility work including LIVE-COCO-TL (74,440 legibility-annotated text patches) and VI-OCR. BACKROW does not silently relabel those datasets as projector-room evidence and does not bundle their images/models in this release.

## D. BACKROW real field-study format

A created study stores locally:
- source truth and region coordinates;
- frozen camera/OCR/model evidence;
- room metadata supplied by tester;
- **one frozen randomized target order**;
- **fixed exposure interval**;
- server-timestamped presentation start/end events;
- blinded participant transcriptions;
- immutable participant-code submissions.

The public participant API omits source truth, camera decode, source images, target boxes and admin token. Raw study files are blocked from HTTP static access. Admin/export requires a separate secret token.

## E. Required locked physical evaluation

Target coverage before International:
- at least 3 physically different rooms;
- at least 2 projector/display models;
- at least 2 camera devices;
- near/middle/farthest meaningful audience positions;
- multiple ambient-light states where permitted;
- at least 20 slides with varied text/numeric content;
- 12–20 naïve readers;
- at least 100 participant-region observations across 8+ independent slides for any human calibrator/evaluator path.

Calibration/development studies and final locked studies must have distinct study IDs. The final evaluator refuses a locked study ID that appears in FieldCalibrator training metadata.
