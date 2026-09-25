# Research Audit — BACKROW 11.0

Research refresh: **2026-09-10**.

## Competition fit

The current official YCWC 2026 page states:
- theme: **AI For Daily Life**;
- Senior age: **15–18**;
- platform: **HTML, CSS, JS, or any framework**;
- required Senior output: **AI Integrated Website**;
- International Grand Final: **20–21 November 2026**, online.

Official current source: https://timedooracademy.com/ycwc/

The supplied Indonesia project-history/guidebook material remains the working source for the 40/30/30 judging split used by this project: **Idea & Creativity 40 / Coding & AI Implementation 30 / Presentation 30**. Where global/current pages and Indonesia-specific guidance conflict, submission operations must follow the organizer instructions for the participant's actual regional path.

## Exact problem

A slide that is readable on the author's laptop can lose exact information after the physical display path:

`source deck → projector/display → surface + ambient light + focus → viewing geometry → audience seat`

BACKROW therefore asks one bounded question:

> **From the audience position being tested, which exact source information survived the real display path, which did not, and did the repair actually fix it?**

The product intentionally does **not** claim to measure comprehension or diagnose eyesight.

## Prior art that materially narrows novelty

### 1. Lecture-hall text legibility is old prior art

Cai, Kim & Green (2011), *Computational Assessment of Text Legibility in Lecture Halls*, modeled display geometry, text geometry, lighting, and observer visual acuity and validated the program in a 21-person lecture-hall experiment.

Source: https://doi.org/10.1177/1420326X11400881

Therefore BACKROW cannot claim that computing audience legibility in lecture rooms is new.

### 2. Projector-camera quality assessment already exists

Le et al. (CRV 2017), *Visual Quality Assessment for Projected Content*, uses camera-captured projection and explicitly identifies the gap between camera-captured quality and what a human viewer perceives.

Source: https://doi.org/10.1109/CRV.2017.47

Therefore homography, camera capture, projection-quality analysis, and the camera-versus-human problem are not novel by themselves.

### 3. Human text-legibility prediction is an active research area

LIVE-COCO-TL contains **74,440** text patches with legible/illegible annotations. The related LIVE text-quality work builds computational models of human-rated embedded text legibility.

Source: https://live.ece.utexas.edu/research/LIVE_YouTube_Text_Quality_Assessment/index.html

VI-OCR (Scientific Reports, 2026) evaluates OCR/VLM systems against human text-recognition behavior under controlled visual degradation and reports that models can diverge from people, especially under severe conditions.

Source: https://www.nature.com/articles/s41598-025-30982-7

These papers reinforce BACKROW's decision **not** to equate OCR confidence or camera quality with human readability.

### 4. Source-file presentation readability products already exist

SlideSpeak currently offers an AI PowerPoint Readability Checker that uploads a PowerPoint and analyzes text complexity, font sizes, color contrast, and slide density.

Source: https://slidespeak.co/free-tools/ai-powerpoint-readability-checker

Therefore BACKROW cannot defend itself as merely “AI checks whether slides are readable.” Its distinctive value must come from the **actual physical audience-view path** and its session workflow.

## Defensible applied contribution

The narrow applied contribution is the integrated presenter workflow:

`deck once → unattended audience-position camera → automatic page retrieval → geometric verification → exact text/numeric recovery evidence → custom visual-survival channel → transparent source-geometry baseline → localized repair → same-seat rescan → locked human validation`

The strongest differentiators are:
- the system sees the **real projected/displayed result**, not only the source file;
- it matches camera frames to a deck **without manually supplying the slide number** during normal audit;
- it reports **localized exact information survival**, including numeric hard guards, rather than an opaque whole-slide score;
- it deliberately fails closed on uncertain page/geometry evidence;
- it includes a repeatable **repair → rescan** loop;
- it includes a blinded, fixed-exposure, frozen-order human-study path and a locked evaluator instead of inventing human accuracy.

Novelty classification: **N3–N4 applied workflow**, not N5 new capability.

## Why AI is still core

Classical CV performs slide retrieval, geometry and rectification. Deterministic rules protect exact numeric mismatch and catastrophic OCR loss. AI is used in two distinct places:

1. **Tesseract LSTM OCR** — third-party pretrained AI for exact text recovery. BACKROW does not claim to have trained it.
2. **AudienceNet 2.0** — BACKROW's custom MLP on source/camera visual-survival + room-geometry features. The bundled model is procedural pretraining only, not a human model.

A separate **FieldCalibrator** exists but is deliberately unavailable until real projector + naïve-reader labels satisfy the training gate. This is a scientific boundary, not a missing fake model.

## Baselines that must remain visible

- manual back-row rehearsal;
- source-only geometry / AVIXA BDM comparator;
- deterministic rule channel;
- OCR confidence/exact recovery;
- current frontier multimodal model under the same source/camera evidence;
- BACKROW full workflow.

The project only earns a strong superiority claim if the locked physical evaluation supports it.

## Current kill conditions

BACKROW must be killed or materially redesigned if a sufficiently sized locked physical evaluation shows any of the following:
- high-confidence `AT_RISK` precision below the predeclared gate;
- critical numeric failures are missed at an unacceptable rate;
- false alerts are too frequent;
- automatic deck retrieval is unreliable in real rehearsal conditions;
- the whole-deck workflow is not meaningfully better than manual checking;
- a current off-the-shelf product is found that already provides the same source-deck + audience-camera + automatic page matching + localized exact recovery + repair/rescan workflow with comparable evidence.

Until those physical gates are run, BACKROW is a functioning competition web application with bounded engineering evidence — **not a completed claim of human-readable accuracy or guaranteed YCWC ranking**.
