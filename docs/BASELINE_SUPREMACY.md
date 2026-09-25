# BACKROW 11.0 — Baseline Status

This file separates baselines that are actually beaten now from baselines that remain external empirical work.

## 1. AudienceNet 2.0 vs bundled procedural baselines — VERIFIED

`AUDIENCENET_TRAINING_REPORT.json`:

| Model / baseline | Test macro-F1 | Scope |
|---|---:|---|
| Signal threshold baseline | 0.4056 | procedural curriculum |
| Source/room geometry baseline | 0.4789 | procedural curriculum |
| **AudienceNet 2.0** | **0.9422** | procedural curriculum |

Split is group-disjoint by text-template family. This proves the custom model learned the procedural survivability curriculum substantially better than those two simple baselines.

It does **not** prove superiority on human readability or real rooms.

## 2. Learned-channel ablation — VERIFIED

`ablation_benchmark.json` verifies all three required properties on bundled fixtures:

- AudienceNet changes at least one ambiguous final decision, so the learned channel is not purely decorative;
- strong exact OCR evidence can safely override pessimistic model output;
- numeric hard guards remain active.

The safety override is a feature, not a failure: learned evidence is deliberately subordinate to direct exact-information evidence.

## 3. Source-only geometry vs actual degraded camera evidence — VERIFIED AS MECHANISM

`avixa_baseline_verification.json` verifies the source-only geometry comparator remains independent. Bundled degraded camera fixtures can fail even when source geometry alone looks acceptable. This supports the need to observe the physical display path.

No AVIXA/source rule is claimed to model humans or replace the locked field study.

## 4. Exact OCR/numeric evidence — VERIFIED ON FIXTURES

The judge fixture contains source `2.5%` and audience decode `25%`. The pipeline localizes this as an exact critical-information loss.

## 5. Whole-deck retrieval — ENGINEERING VERIFIED, REAL FIELD GATE OPEN

Bundled 3-page PDF: **3/3 page matches** without page index.

Match-only latency in the current test: about **0.43–0.47 s**.

The physical target is ≥98% stable-frame match accuracy on a diverse real projector set. Collect it with `/validate.html`.

## 6. Manual workflow — OPEN PHYSICAL GATE

Required comparison:

- manual presenter back-row inspection;
- BACKROW whole-deck workflow;
- same frozen 15+ slide deck;
- elapsed time + critical failures found.

The validator exports the exact locked-evaluator schema.

## 7. Frontier multimodal AI — OPEN EXTERNAL GATE

Use `FRONTIER_AI_BASELINE_PROTOCOL.md`. Give the model the same source slide and audience image. Measure correctness, exact-value recovery, localization, false alarms, abstention, latency, repeatability, and whole-deck user effort.

Do not claim ChatGPT/Gemini/Claude cannot compare two images. BACKROW must win on measured workflow/system structure or field performance.

## 8. Human-grounded prediction — OPEN PHYSICAL GATE

The final question is whether BACKROW predicts human unrecoverability on held-out physical conditions better than simple baselines. The package contains the blinded timed collector, optional calibrator, and locked evaluator; the physical data does not yet exist in this runtime.
