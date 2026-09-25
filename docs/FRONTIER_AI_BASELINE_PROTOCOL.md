# Reproducible Frontier-VLM Baseline Protocol

Purpose: test the real replacement question without weakening the baseline through a bad prompt.

## Models

At field-test time, use the strongest generally available multimodal versions of at least two major assistants accessible under the competition/evaluation conditions. Record exact product/model label and date. Do not silently use an older model to make BACKROW look better.

## Information parity

For pairwise mode, give the VLM exactly:
1. source slide image;
2. audience camera frame;
3. the same room metadata if BACKROW received it.

Do **not** give it BACKROW OCR, homography, region results, or the answer key.

For workflow mode, give it the entire source deck and the same ordered sequence of camera frames, with **no source page index** for each frame.

## Prompt — pairwise

Use this verbatim except model-specific attachment syntax:

> Compare the source slide with the audience-seat camera image. Do not rate aesthetics. Identify exact source text or numbers that are missing, altered, or not reliably recoverable in the audience image. If alignment or evidence is insufficient, say UNCERTAIN instead of guessing. Return strict JSON with: `critical_mismatch`, `findings[{source_text,audience_text,status,reason}]`, `uncertain`.

## Prompt — whole deck

> You receive a source presentation deck and an ordered sequence of audience-seat camera frames from a rehearsal. For every camera frame, identify which source page it corresponds to without being given the page number. Reject ambiguous matches. Then identify exact source text/numbers that are missing, altered, or not reliably recoverable. Return strict JSON per frame with matched page, uncertainty, and localized textual findings.

## Metrics

Measure separately:
- correct deck-page match rate;
- ambiguity/rejection behavior;
- critical-number mismatch recall;
- false critical mismatch rate on clean frames;
- exact-source-fragment localization;
- total human preparation steps;
- total elapsed workflow time for 15+ slides.

Do not collapse these into a subjective “AI quality” score.

## Locked fixture sanity cases

Bundled engineering fixtures can check that the protocol is wired correctly, but **must not be used as the final superiority benchmark** because they were designed during development. The final comparison must use unseen real-projector captures frozen before running the external models.

## Status in this package

**Protocol complete. External frontier run not fabricated.** It requires access to the chosen external model(s) at evaluation time and, for the meaningful version, the locked real-projector dataset that has not yet been physically collected.
