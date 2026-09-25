# BACKROW 11.0 — Benchmark Report

Generated: **2026-09-10**.

All metrics below are separated by evidence type. Generated/procedural results must not be described as human accuracy.

## AudienceNet 2.0 procedural curriculum

Source: `AUDIENCENET_TRAINING_REPORT.json`

- samples: 1,440;
- class balance: 480 at-risk / 480 supported / 480 watch;
- split: group-disjoint by text-template family;
- train/validation/test: 870 / 240 / 330;
- test accuracy: **0.9424**;
- test macro-F1: **0.9422**;
- signal baseline macro-F1: **0.4056**;
- geometry baseline macro-F1: **0.4789**;
- human-readability claim: **false**.

## Engineering projection harness

Source: `engineering_runtime_verification.json`

- cases: 6;
- alignment pass: **6/6**;
- wrong-pair rejection: **2/2**;
- critical numeric demo: **PASS**;
- median analysis latency: **2.377 s** in the recorded environment.

## Adversarial generated projection harness

Source: `adversarial_projection_benchmark.json`

The bundled harness covers clean, critical-number loss, glare/washout, extra blur, and low resolution. It verifies:

- clean control does not produce false critical risk;
- critical numeric loss is detected;
- actual degraded camera evidence can add information beyond source geometry;
- severe degradation cannot silently become an all-green result.

## Learned-channel ablation

Source: `ablation_benchmark.json`

The custom learned channel changes at least one ambiguous final decision. Direct exact evidence can override pessimistic model output, and the numeric hard guard remains active.

This is a mechanism test, not human superiority evidence.

## Repair/rescan regression

Source: `fix_rescan_verification.json`

- BEFORE: **6 recovered / 0 watch / 2 at risk**;
- AFTER: **8 recovered / 0 watch / 0 at risk**;
- critical `2.5%` recovered exactly.

Same generated capture transform; not a physical result.

## Whole-deck page matching

Source: `deck_api_verification.json`

Three-page bundled PDF, no page index supplied:

| Expected | Matched | Match-only latency |
|---:|---:|---:|
| 1 | 1 | 435 ms |
| 2 | 2 | 431 ms |
| 3 | 3 | 468 ms |

Full analysis on the three cases was about 2.1–2.9 seconds in that run.

Real stable-frame ≥98% accuracy remains a predeclared physical gate and is collected through `/validate.html`.

## Field-study protocol/software verification

`field_study_api_verification.json` verifies:

- no participant source/camera truth leak;
- admin API requires secret token;
- raw study files blocked from static serving;
- admin token not exported;
- participant response immutable;
- frozen randomized order;
- timed exposure protocol;
- authorized start/end presentation events logged;
- tiny/protocol-invalid calibration training refused.

`locked_evaluator_logic_verification.json` verifies evaluator/refusal logic using a synthetic logic fixture only. It does not claim field performance.

## Browser/UI verification

`browser_v4_e2e_verification.json`:

- engine-ready state rendered;
- desktop horizontal overflow: false;
- mobile horizontal overflow: false;
- judge result: 2 risk / 0 watch / 6 recovered;
- fix/rescan delta reaches 0 risk;
- page errors: none.

`browser_validation_verification.json` verifies the physical validation console renders on desktop/mobile without horizontal overflow or page errors.

## External empirical results

Not yet present in this package:

- human `AT_RISK` precision/recall;
- human false-alert rate;
- critical-number human failure recall;
- real-room stable-frame deck-match accuracy;
- manual-vs-BACKROW field timing;
- locked frontier multimodal comparison.

Those must come from the frozen physical protocol. Absence of these results is not replaced by procedural accuracy.
