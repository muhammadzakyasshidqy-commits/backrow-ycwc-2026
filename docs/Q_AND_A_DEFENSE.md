# BACKROW 11.0 — Q&A Defense

Answers must stay within measured evidence.

## “Why not just walk to the back?”

For one slide, walking back is reasonable. BACKROW targets a whole-deck rehearsal: load the deck once, leave a camera at the audience position, advance normally, and get source-localized evidence plus rescan. We are measuring the time/critical-failure difference against manual checking in the physical validation console; until that field comparison is complete, we do not claim a measured speedup.

## “Why not increase every font?”

Because source font size is only one variable. Actual projection can lose information through distance, focus, washout, glare, contrast, perspective, and capture/display conditions. BACKROW also keeps a source-only geometry comparator so it can distinguish “source geometry was weak” from “the room/capture added evidence.”

## “Doesn’t lecture-hall legibility software already exist?”

Yes. Cai, Kim & Green published a lecture-hall text-legibility program in 2011. That is prior art, not something we hide. BACKROW's narrower applied contribution is the audience-camera workflow with automatic source-slide matching, exact localized information-loss evidence, repair/rescan, and locked physical validation.

## “What about projector-camera quality research?”

Le et al. (CRV 2017) already used camera-captured projections for visual quality assessment and explicitly noted the camera-vs-viewer gap. BACKROW does not claim to invent that field. We use a different presenter workflow and explicitly calibrate the camera/human gap rather than pretending the camera is a human eye.

## “Why not SlideSpeak / PowerPoint Accessibility Checker?”

Those tools are useful source-side checks. They inspect the file or source geometry. BACKROW asks a different question: what exact information survived after the real room/display/camera path? It maps that physical evidence back to the source region and lets the presenter fix then rescan.

## “Why not ChatGPT?”

A frontier multimodal model can compare a source slide and an audience image, so we do not deny that. BACKROW's structural advantages are automatic whole-deck acquisition, source-page retrieval, geometric correspondence, exact deterministic value checks, repeatable evidence hierarchy, fail-closed states, and fix/rescan. We still require a locked same-evidence frontier baseline before claiming measured superiority.

## “What part is AI?”

Two AI components are used:

1. **AudienceNet 2.0** — our custom 48→24 MLP over 16 paired source/camera/room features.
2. **Tesseract 5 LSTM OCR** — third-party pretrained AI used for exact text recovery.

ORB, RANSAC/homography, numeric extraction, source geometry, and evidence fusion are classical/deterministic components and are not presented as AI.

## “What did you train?”

AudienceNet 2.0. The bundled model was trained on 1,440 balanced physics-aware procedural examples across 48 text-template families with group-disjoint family splits. Its test macro-F1 is 0.9422 versus 0.4056/0.4789 for the two bundled simple baselines.

Those are procedural metrics. They are not human-readability accuracy.

## “Why is AudienceNet needed if OCR already detects text?”

OCR provides direct content recovery when the text can be decoded confidently. AudienceNet contributes learned survivability evidence for ambiguous visual conditions. Ablation verifies it changes at least one ambiguous decision. Strong direct exact OCR/numeric evidence remains higher priority, so AudienceNet cannot override a verified contradiction.

## “Camera is not a human eye. Isn’t the whole idea invalid?”

A camera is not a human eye. That is a central design constraint, not something we hide. The camera gives measurable physical evidence. The blinded human field study then measures the relationship between that evidence and naïve-reader recovery. The locked evaluator refuses protocol-invalid studies. Until those results exist, we call the system camera-recoverability + procedural learned evidence, not a calibrated human probability model.

## “How many humans did you test?”

Do not invent a number. State the actual completed count from `LOCKED_FIELD_EVALUATION.json`. Before that file exists, say the final physical human test is still open and show the blinded collector/protocol.

## “Did you train on your test slides?”

The AudienceNet procedural split is group-disjoint by text-template family. For human calibration, development studies and locked studies must use distinct study IDs; the locked evaluator refuses calibration leakage. Physical split reporting must also distinguish room/slide/device conditions.

## “What if the camera is blurry or the wrong slide?”

BACKROW can abstain. Ambiguous deck identity, failed geometry, severe capture quality, or insufficient evidence should produce a rejection/unknown state rather than a fabricated answer.

## “Why a website?”

The browser naturally supports PDF/file input, camera capture, a second participant device, LAN study collection, cross-platform exhibition use, and an install-free judge demo. The web surface is part of the actual workflow, not a wrapper around a chat prompt.

## “What happens without internet?”

Core analysis runs on the BACKROW instance using bundled/local dependencies and no third-party AI API. Exhibition should still be preflighted on the exact device. A deterministic bundled demo remains the fallback if live capture conditions fail.

## “Can I try my own slide?”

Yes. Use **Check a real slide**, load the exact source/PDF, capture an audience image or camera frame, and let BACKROW match/analyze it. Unsupported or ambiguous input should fail closed rather than inherit the judge-demo answer.

## “So is it already proven to predict humans?”

No. That claim is intentionally withheld until the frozen real-projector naïve-reader study passes its predeclared gates.

## Why not just walk to the back?
Walking to the back is still the simplest baseline, and BACKROW measures itself against it. The current two-device workflow removes the biggest workflow disadvantage: the presenter laptop stays at the front while a paired phone remains at the audience position. The phone can run live scan over HTTPS or photo-capture fallback, and the presenter receives slide-matched evidence automatically across the deck. The comparison is therefore not “AI versus eyesight”; it is repeated manual travel/memory versus a persistent measured audience viewpoint.

## Is the second phone a fake demo device?
No. The observer page is a real web client with its own short-lived token. It pairs by a six-digit code, captures the actual projected screen, sends the image to the same BACKROW instance, and receives a result only after page-index-free matching and analysis. The source answer is not exposed on the observer page.
