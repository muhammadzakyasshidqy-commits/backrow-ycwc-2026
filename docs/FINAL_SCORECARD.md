# YCWC Readiness Scorecard — BACKROW 11.0

Date: **2026-09-24**.

The official YCWC 2026 guide was re-verified on **2026-09-25**. Senior is an **AI-integrated website** category for ages 15–18, and the guide confirms the **40% Idea & Creativity / 30% Coding & AI Implementation / 30% Presentation** scoring structure. The Indonesian guide allows Bahasa Indonesia or English in the project; International Exhibition presentation is conducted in English.

## Defensible current position

| YCWC area | Current defensible score | Why |
|---|---:|---|
| Idea & Creativity | **37/40** | Strong physical-audience workflow, paired back-row phone, automatic deck matching, and localized repair/rescan loop; prior art still exists in lecture-hall legibility and projector-camera assessment, so the novelty claim remains deliberately narrow. |
| Coding & AI Implementation | **29/30** | Custom AudienceNet 2.0 + Tesseract LSTM + deck retrieval + homography + evidence fusion + two-device observer session + security/blinding/evaluator stack. Real human-grounded field performance is still unmeasured. |
| Presentation | **30/30** | Three-second exact-information failure, judge-changeable live input, fix/rescan proof, deterministic backup, first-class English/Indonesian UI, and separate EN/ID competition decks/scripts. |
| **Current defensible total** | **96/100** | Pre-field engineering position after the two-device workflow closure; not a promised judge score. |

## Why the Idea score is not 40/40 yet

The 2026 red-team found closer prior art than earlier versions acknowledged:

- Cai, Kim & Green (2011) already developed a computer program for text legibility in lecture halls using display geometry, text geometry, lighting, and visual acuity.
- Le et al. (CRV 2017) already assessed projected visual quality from camera captures and explicitly discussed the camera-vs-viewer gap.
- SlideSpeak currently provides a source-file PowerPoint readability checker for font size, contrast, density, and text complexity.
- modern text-legibility datasets/research already measure human legibility and compare OCR/VLM behavior with humans.

Therefore BACKROW is not “new because it checks readability.” The defensible applied contribution is the integrated workflow:

> **actual audience-position capture + automatic source-slide matching + physical-view rectification + exact information-loss evidence + custom learned survivability channel + conservative abstention + fix/rescan verification + blinded real-projector validation.**

## What is actually closed

Software/engineering gates now passed include:

- functioning AI-integrated web application;
- real deck/camera input paths;
- page-index-free whole-deck matching;
- custom AudienceNet 2.0 runtime and reproducible procedural training;
- AudienceNet 2.0 procedural macro-F1 above both bundled simple baselines;
- explicit AI/non-AI component boundaries;
- exact numeric hard guard;
- source geometry kept separate from camera evidence;
- wrong-pair/ambiguous failure handling;
- evidence-driven repair and before/after rescan;
- niche non-AI-slop instrument UI;
- first-class English/Indonesian rendering across main product, physical validation console, blinded reader form, and presenter console;
- separate English and Indonesian competition decks, scripts, Q&A, field instructions, and submission checklists;
- blinded human-study collector;
- frozen randomized presentation order;
- fixed timed exposure with authorized server-side event log;
- immutable participant responses and truth separation;
- field validation console for manual timing and real stable-frame deck match collection;
- locked evaluator with confidence intervals, sample requirements, timed-exposure validation, and calibration-leakage refusal;
- adversarial generated projection tests;
- clean-release verification tooling.

## Remaining 100/100 gate

The remaining gap cannot be resolved honestly by another synthetic benchmark:

1. physical projector/display + real rooms + multiple audience positions;
2. naïve human reader ground truth;
3. manual-vs-BACKROW workflow measurement;
4. stable-frame real deck retrieval measurement;
5. locked frontier multimodal baseline on the same frozen physical evidence;
6. confidence-interval reporting on the untouched test set.

Correct status:

> **ENGINEERING-CLOSED / PHYSICAL EMPIRICAL GATE OPEN**

If the locked physical data misses a predeclared kill gate, the score must go down or the mechanism must be revised. No procedural score is allowed to substitute for human evidence.
