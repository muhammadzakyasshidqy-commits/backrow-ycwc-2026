# BACKROW 11.0 — Prior Art and Competitor Boundaries

Research refreshed **2026-09-10**. BACKROW's novelty claim is intentionally narrow.

## 1. Cai, Kim & Green — lecture-hall text legibility (2011)

Paper: *Computational Assessment of Text Legibility in Lecture Halls*.

Already existed:
- a computer program for lecture-hall legibility;
- display dimensions/position/orientation;
- text geometry;
- lighting/contrast;
- observer visual acuity;
- human validation.

Therefore BACKROW does **not** claim to invent lecture-hall readability computation.

## 2. Le et al. — projected-content quality from a camera (CRV 2017)

Already existed:
- original image + camera-captured projection;
- geometric rectification;
- learned projected-image quality assessment;
- explicit acknowledgement that the camera and viewer perceive a projection differently.

Therefore BACKROW does **not** claim to invent projector-camera quality assessment, homography, or learned projection-quality models.

## 3. SlideSpeak PowerPoint Readability Checker — current source-file product

Current product analyzes uploaded PowerPoint files for text complexity, font size, contrast, slide density, and related source-file readability metrics.

Difference: it analyzes the file; BACKROW's core input includes what the real room/camera receives and then maps failures back to the source slide.

Do not attack SlideSpeak as “just AI.” It is a valid adjacent solution for source-side problems.

## 4. LIVE text-legibility datasets and VI-OCR research

These establish that text legibility can be human-labelled and that OCR/VLM performance is not automatically identical to human recognition.

BACKROW uses this as justification for a human-grounded locked field study—not as evidence that BACKROW itself already predicts humans accurately.

## 5. PowerPoint/AV accessibility checks

Source-side accessibility and display-size guidance can catch many preventable problems. BACKROW should complement, not pretend to replace, those checks.

## Defensible novelty level

**N3–N4: new applied workflow / applied insight**, not N5.

The strongest defensible contribution is the integration of:

> actual audience-position capture → automatic source-slide match → physical-view rectification → localized exact information recovery/loss → custom learned survivability evidence → conservative abstention → source-localized repair → rescan proof → blinded physical validation.

A new name is not the novelty. The end-to-end audience-receipt workflow is.
