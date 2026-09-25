# BACKROW 11.0 — Experiment Summary

## Question

Can BACKROW identify presentation regions that naïve audience members fail to recover from actual audience positions better than simpler baselines, while reducing whole-deck checking effort?

## Frozen physical inputs

- source slide/deck;
- real projector/display;
- measured audience position;
- real camera capture;
- target source regions;
- frozen randomized presentation order;
- fixed exposure time (default 6 s).

## Human label

Reader sees the real projected target for the fixed interval and types exactly what they recover. Source truth and BACKROW prediction remain hidden until submission is frozen.

## Baselines

- manual back-row inspection;
- source geometry rules;
- OCR/image-quality deterministic baseline;
- current frontier multimodal AI on the same source/audience evidence;
- BACKROW full system.

## Primary locked metrics

- `AT_RISK` precision;
- `AT_RISK` recall;
- false-alert rate;
- critical-number failure recall;
- manual vs BACKROW time and critical-failure recall.

## Predeclared gates

- precision ≥90%;
- critical-number failure recall ≥90%;
- false-alert rate ≤10%;
- stable-frame page retrieval ≥98%;
- whole-deck workflow faster than manual for 15+ slides without worse critical-failure recall.

## Statistics

Report raw counts and Wilson 95% confidence intervals. Report pooled and per-room/per-distance results. Locked studies cannot overlap optional calibrator training studies.

## Current status

Collector, randomized/timed presentation flow, validation console, leakage checks, calibrator refusal logic, and locked evaluator are implemented and unit/integration tested. Real projector/reader results are still external and must not be fabricated.
