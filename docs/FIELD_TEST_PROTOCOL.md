# BACKROW 11.0 — Locked Real-Projector / Naïve-Reader Protocol

Protocol revision frozen: **2026-09-10** before final physical labels are collected.

## Thesis under test

Does BACKROW identify exact presentation regions that naïve audience members fail to recover from the tested position, with controlled false alarms, and does its whole-deck workflow improve on manual back-row checking?

## Separation of development and locked evaluation

Use different physical collections for:

- **calibration/development** — may be used to train the optional FieldCalibrator;
- **locked final test** — never used for fitting thresholds or weights.

The locked evaluator refuses study IDs that appear in the calibrator training metadata.

## Participants

Target **12–20 naïve readers** across the study rather than repeatedly sampling one author. Readers must not have authored the tested slides and must not see source truth or BACKROW predictions before their response is frozen.

Do not collect medical diagnoses or health history. Normal self-selected glasses/contact lenses are permitted. This is a product legibility/recoverability study, not a medical study.

## Physical coverage target

Aim for at least:

- **3 physically different rooms**;
- **2 projector/display models**;
- **2 camera devices**;
- near / middle / far audience positions;
- more than one ambient-light condition where practical;
- **20+ slides** across different layouts/content families;
- hundreds of participant-region observations rather than one easy repeated frame.

## Content coverage

Include:

- headlines;
- body text;
- short labels;
- decimals and percentages;
- chart labels;
- dense but legitimate tables where supported;
- clean controls;
- hard confusions such as `2.5 / 25`, `15 / 50`, `0 / 8`.

Freeze final locked slide content before inspecting locked outputs.

## Frozen randomized order

When a study is created, BACKROW generates one frozen randomized `presentation_order`. All participants use that order. The public participant payload receives only sequence/slide IDs—not source truth, camera OCR, target boxes, predictions, or the admin token.

## Timed exposure

Default exposure is **6 seconds per target region**. The admin can set **3–12 seconds** when the study is created, but the chosen duration is then part of the study protocol.

For every target:

1. presenter presses **Start timed exposure**;
2. the projected target is shown for the configured duration;
3. BACKROW sends authorized `start` and `end` events to the server;
4. the target is hidden at the end of the timer;
5. the reader enters exactly what they recall/read on the participant device;
6. the response becomes immutable once submitted.

The locked evaluator refuses studies without a valid start/end exposure pair for every target or where measured duration differs materially from the configured interval.

## Human ground truth

For each target source region:

1. reader sits at the actual tested position;
2. reader watches the **real projected/displayed content**, not a phone screenshot;
3. timed exposure runs;
4. reader types exactly what they could recover;
5. blank means unrecovered;
6. numeric/percentage regions require exact numeric-token recovery.

## System freeze

Before final locked testing, freeze:

- source code;
- AudienceNet version;
- optional FieldCalibrator version if used;
- matching thresholds;
- evidence-fusion thresholds;
- study protocol;
- locked slide set.

Predictions and camera evidence must be produced before human source-truth comparison for that trial.

## Baselines

Run on the same frozen physical evidence where applicable:

1. manual presenter back-row checking;
2. source-only geometry rule baseline;
3. deterministic image-quality/OCR-confidence baseline;
4. current frontier multimodal AI under `FRONTIER_AI_BASELINE_PROTOCOL.md`;
5. BACKROW full system.

## Primary metrics

- `AT_RISK` precision on human-unrecovered observations;
- `AT_RISK` recall on human-unrecovered observations;
- false-alert rate on human-recovered observations;
- critical-number failure recall;
- workflow time and critical-failure recall vs manual checking.

## Secondary metrics

- real stable-frame deck match accuracy;
- fail-closed/rejection rate;
- analysis latency;
- setup time;
- participant completion/dropout;
- per-room/per-distance/per-device results.

## Predeclared competition gates

These are **targets, not current results**:

- `AT_RISK` precision ≥ **90%**;
- critical-number failure recall ≥ **90%**;
- false-alert rate ≤ **10%** on human-recoverable observations;
- stable-frame deck retrieval ≥ **98%**;
- for a 15+ slide rehearsal, BACKROW is faster than the manual workflow without worse critical-failure recall.

General failure recall must still be reported even if no threshold is predeclared for it.

## Statistical reporting

Report numerators/denominators and **95% confidence intervals**. Report pooled and per-room/per-distance results. Do not present repeated readers of one region as proof of cross-slide or cross-room generalization.

## Kill rule

If a predeclared gate fails on the locked physical set, do not call BACKROW empirically 100/100. Report the failure, revise the mechanism if justified, or kill the claim.
