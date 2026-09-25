# BACKROW 11.0 delta

V11 is a release-integrity and live-demo hardening pass. It does not change the product thesis.

## Fixed defects

- Restored a **complete source release** instead of a thin top-level artifact bundle.
- Presenter mode now has a consistent **7-scene HTML + JS + test** state machine.
- Added styling and bilingual copy for the scientific-boundary scene.
- Main product evidence export now reports `11.0.0` rather than a stale V7 version.
- CSP now permits **same-origin** embedding required by presenter mode while blocking external framing.
- Added `X-Frame-Options: SAMEORIGIN`.
- Observer camera UI has an explicit projected-screen framing guide.
- Observer live scan now waits for low-motion frames and suppresses unchanged frames.
- Tesseract calls have a **3 s fail-closed timeout** with a regression test.

## Preserved claim boundary

No synthetic/procedural result is relabeled as human-readability accuracy. The remaining real-projector + naïve-reader field gate stays explicit.
- Fixed a live-scan retry defect: a failed frame analysis is no longer marked as successfully sent, so stable frames are retried after transient server/network errors.
- Six-digit observer pairing codes are now **single-use**; the long observer token remains the reload credential after pairing.
- Presenter mode now wires **14 generated natural hosted voice segments** (7 EN + 7 ID) with a 3.5-second failover to local browser speech, so narration remains usable when internet/audio hosting is unavailable.
