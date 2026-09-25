# BACKROW 11.0 — YCWC 2026 Senior

**BACKROW is an AI-integrated web application for testing a presentation through the physical audience path, not only the source file.** Load a slide/PDF deck, place a camera at an audience position, run the presentation, and BACKROW automatically identifies the projected page, rectifies the camera view, checks what exact text/numbers survived, localizes failures, suggests targeted repairs, and verifies the repair through rescan.


## Rehearsal / Demo Presenter Mode

V11 hardens the live competition path around `present.html`: a bilingual rehearsal/demo surface with a domain-specific perspective room diagram, the real `2.5% → 25%` evidence, an embedded live BACKROW judge case, architecture explanation, fix → rescan, and an explicit scientific-boundary scene. Browser speech synthesis is for rehearsal/backup media. The current public YCWC 2026 page confirms English for the International Grand Final; participant-delivery mechanics should be checked against the organizer-provided 2026 guide PDF before the event.

- Windows: `RUN_PRESENTATION_WINDOWS.bat`
- Linux/macOS: `RUN_PRESENTATION_LINUX_MAC.sh`
- Manual: open `/present.html` after starting the server
- Documentation: `docs/AUTO_PRESENTATION.md`, `docs/NARRATION_EN.md`, `docs/NARRATION_ID.md`
- Visual rehearsal cut: `preview_v11/BACKROW_V11_VISUAL_REHEARSAL.mp4`

## Bahasa Indonesia

BACKROW 11.0 ships a first-class Indonesian interface, not only a translated landing page.

- Main product: `/?lang=id`
- Physical validation console: `/validate.html?lang=id`
- Blind reader study: `/study.html?...&lang=id`
- Presenter study console: `/study_admin.html?...&lang=id`
- Indonesian competition deck: `BACKROW_YCWC_2026_PRESENTATION_ID.pptx`
- Indonesian presentation script: `docs/PRESENTATION_SCRIPT_ID.md`
- Indonesian Q&A: `docs/Q_AND_A_DEFENSE_ID.md`
- Indonesian field quickstart: `docs/FIELD_VALIDATION_QUICKSTART_ID.md`
- Indonesian submission checklist: `docs/SUBMISSION_CHECKLIST_ID.md`

Language follows `?lang=id|en`, persists in `localStorage`, and defaults from the browser locale. Study links preserve the selected language.

## Remote audience observer

V11 retains the two-device workflow introduced in V7, which closes a practical workflow gap: the presenter laptop can remain at the front while a second phone sits at the audience position.

1. Load the PDF deck once on the presenter workstation.
2. Choose **Create observer link**.
3. On the audience phone, open `/observer.html` on the same BACKROW instance and enter the 6-digit pairing code.
4. Capture the projected screen from the actual seat. Secure HTTPS can use the live camera; the mobile photo-capture fallback also works when local HTTP blocks `getUserMedia`.
5. The server automatically matches the capture to the deck page, runs the same evidence pipeline, and the presenter workstation receives the result without moving away from the front.

Observer sessions expire automatically and use separate presenter/observer tokens. Pairing attempts are rate-limited, and the 6-digit code becomes invalid after a successful join. The observer page never exposes the source answer.

## Core product loop

```text
SOURCE DECK
  → audience-position camera/photo
  → automatic deck-page retrieval
  → geometric verification + rectification
  → exact OCR / numeric evidence
  → AudienceNet 2.0 procedural visual-survival evidence
  → conservative evidence fusion
  → RECOVERED / WATCH / AT RISK
  → targeted repair
  → RESCAN
```

The main question is deliberately narrow: **Can the last row still read it?**

## Implemented and hardened through 11.0

- browser camera + audience-photo upload;
- PNG/JPG/PDF input (`pypdfium2` / PDFium);
- page-index-free whole-deck matching using ORB retrieval + RANSAC/homography verification;
- Tesseract 5 LSTM exact text/numeric recovery with fail-closed per-call timeout hardening;
- **AudienceNet 2.0**, our compact custom MLP with 16 paired visual/room features;
- transparent source-only display-geometry comparator based on the public AVIXA BDM table range used by the project;
- exact numeric hard guards and fail-closed ambiguous matching/alignment;
- localized evidence ledger; no fake whole-slide “AI score”;
- evidence-driven repair suggestions;
- BEFORE → fix → RESCAN proof loop;
- English + Bahasa Indonesia;
- responsive instrument-style UI, deliberately not a generic AI dashboard;
- whole-deck evidence export;
- **field validation console** (`validate.html`) for real stable-frame deck retrieval and manual-vs-BACKROW timing;
- blinded human-study collector with a frozen randomized order and fixed timed exposures;
- secret presenter/admin token, participant truth separation, blocked raw-study HTTP paths, immutable participant submissions;
- locked evaluator with timed-exposure audit, minimum-sample gates, confidence intervals, and leakage refusal;
- optional human calibrator that remains unavailable until sufficient real physical data exists;
- no cloud LLM or paid AI API in the core runtime.

## What is AI, and what is not

**Custom AI:** AudienceNet 2.0. It is a small neural network trained on a physics-aware procedural curriculum to classify paired source/camera regions as `supported`, `watch`, or `at_risk`.

**Pretrained AI:** Tesseract 5 LSTM OCR. It is third-party; we do not claim to have trained it.

**Classical CV / deterministic engineering:** ORB, RANSAC/homography, perspective rectification, exact numeric extraction, source geometry, evidence hierarchy, and safety overrides.

The direct-evidence hierarchy is intentional:

```text
verified exact information loss
> high-confidence OCR/region evidence
> AudienceNet learned evidence
> weak image-quality heuristics
```

AudienceNet is not allowed to overrule a strong exact-value contradiction such as source `2.5%` vs audience decode `25%`.

## AudienceNet 2.0 — measured engineering result

`docs/AUDIENCENET_TRAINING_REPORT.json` records:

- 1,440 balanced procedural samples;
- 48 text-template families;
- group-disjoint family split;
- 870 train / 240 validation / 330 test;
- test accuracy: **0.9424**;
- test macro-F1: **0.9422**;
- signal-rule baseline macro-F1: **0.4056**;
- geometry baseline macro-F1: **0.4789**.

These are **procedural visual-survival metrics, not human-readability accuracy and not real-room generalization**.

## Judge demo

Click **Run judge demo**. The source contains:

`Launch only if error rate stays below 2.5%.`

The bundled audience capture decodes the critical value as `25%`. The exact region must be localized as `AT RISK` while six other regions are recovered.

Then run **fix → rescan proof**. Under the same generated capture transform the repaired slide must end at:

`8 recovered / 0 watch / 0 at risk`

with `2.5%` recovered exactly.

For a stronger live exhibition, load the real deck once, place the camera at the audience position, and let BACKROW identify pages without being given page indices.

## Current verified engineering checks

- generated projection alignment: **6/6**;
- wrong source/view pairs rejected: **2/2**;
- critical `2.5% → 25%`: detected;
- bundled fix/rescan: **2 risk → 0 risk**;
- 3-page PDF auto-match: **3/3**;
- match-only latency on the bundled three cases: about **0.43–0.47 s**;
- full analysis on those cases: about **2.1–2.9 s** in this environment;
- field-study truth leak: none in the participant API test;
- randomized/timed study protocol: enforced and logged;
- evaluator calibration leakage: refused;
- desktop/mobile core browser render: no horizontal overflow, no page errors.

See `docs/FINAL_VERIFICATION.json` for the exact machine-readable verification state.

## Run on Windows

1. Extract the ZIP.
2. Run `SETUP_WINDOWS.bat` once.
3. Run `RUN_WINDOWS.bat`.
4. Open Chrome/Edge at `http://127.0.0.1:8080` if it does not open automatically.

For physical validation, run `RUN_FIELD_STUDY_WINDOWS.bat`, then open:

- `/validate.html` on the presenter machine for workflow/deck-match collection;
- `/study_admin.html?...` via the generated locked-study admin URL;
- `/study.html?...` on participant phones.

Read `docs/FIELD_VALIDATION_QUICKSTART.md` first.

## Reproduce AudienceNet training

```bash
pip install -r requirements-dev.txt
python training/train_audiencenet.py
```

## Locked human calibration

No human field-calibration model is bundled. Training refuses undersized or invalid studies, including studies without valid timed-exposure logs.

```bash
python training/train_field_calibrator.py calibration_room1.json calibration_room2.json \
  --out models/field_calibrator.json
```

## Scientific claim boundary

A camera is not a human eye. Prior work in projector-camera assessment explicitly identifies this gap, and recent text-accessibility work also shows that OCR/VLM behavior need not equal human recognition. BACKROW therefore does **not** convert procedural model scores or OCR confidence into a human-readability percentage.

The field collector, validation console, and locked evaluator are included specifically to close the remaining physical empirical gate with real projector/room/reader evidence instead of fabricating it.

### V11 live-demo hardening

- production CSP explicitly allows the same BACKROW origin to embed the live product inside `present.html`; external framing stays blocked;
- observer live scan waits for stable low-motion frames and skips unchanged frames instead of hammering the analyzer;
- the observer has a projected-screen framing guide;
- exported evidence reports now carry the correct `11.0.0` version;
- presenter rehearsal uses captions plus browser/OS local Speech Synthesis only; no external voice/TTS plugin is required by the submission build.

- V11 fixes the presenter-mode 7-scene state machine and styles the scientific-boundary scene instead of leaving it as an untested HTML insertion.
- V11 observer live scan now waits for low-motion frames and skips materially unchanged frames before sending analysis requests.
- V11 CSP allows only same-origin framing (`frame-ancestors 'self'` + `X-Frame-Options: SAMEORIGIN`) so presenter mode can embed the real product without enabling third-party framing.
- V11 Tesseract calls use a 3-second fail-closed timeout per OCR call, with a dedicated regression test.
