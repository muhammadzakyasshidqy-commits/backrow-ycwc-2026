# BACKROW 11.0 — UI Design Audit

## Design gate

The interface must remain identifiable as a **presentation / AV audience-view test instrument** even if the BACKROW logo is hidden.

## Domain-native visual language

The production UI uses:

- source slide and real/captured audience frame as the visual center;
- audience distance and projected-image height;
- matched slide / alignment evidence;
- localized source and rectified audience regions;
- RECOVERED / WATCH / AT RISK only as functional evidence states;
- evidence ledger rather than generic dashboard cards;
- fix → rescan as the action loop;
- thin technical rules, square geometry, compact controls, and instrumentation labels.

## Explicitly prohibited / absent

- decorative AI gradients;
- glassmorphism;
- glowing orb/robot/brain art;
- “magic” controls;
- fake analytics or trust scores;
- generic feature-card grid;
- generated hero illustration;
- chatbot UI;
- AI marketing phrases as the main interface.

## Privacy/status truthfulness

The engine indicator is runtime-derived (`ENGINE READY` / `ENGINE OFFLINE`) rather than a static “local AI” badge. Privacy copy states that images go to the BACKROW instance the user opened and that the core uses no third-party AI service; it does not falsely claim every deployment is on-device browser inference.

## Validation tools

`validate.html`, `study.html`, and `study_admin.html` are separate measurement surfaces. They intentionally look like lab/field instrumentation and do not dilute the main product into a multi-tool dashboard.

## Verified render gates

- V5 desktop: no horizontal overflow;
- V5 mobile 390 px: no horizontal overflow;
- page errors: none in browser harness;
- actual source/audience evidence embedded in the landing proof;
- validation console desktop/mobile: pass.

See `browser_v4_e2e_verification.json` and `browser_validation_verification.json`.
