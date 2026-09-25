# Dependency / License Audit

Recheck package metadata one final time immediately before public submission because transitive wheel contents can change.

Core runtime:
- OpenCV / `opencv-python-headless`: OpenCV project Apache-2.0; wheels may include separately licensed third-party components.
- NumPy: BSD-3-Clause.
- `pytesseract`: Apache-2.0.
- Tesseract OCR: Apache-2.0.
- Pillow: MIT-CMU.
- `pypdfium2`: permissive wrapper licensing; PDFium distribution carries its documented Chromium/PDFium third-party notices.

Development/evaluation:
- scikit-learn: BSD-3-Clause.
- requests: Apache-2.0.
- Playwright: Apache-2.0.

BACKROW intentionally uses `pypdfium2` rather than PyMuPDF in the competition runtime to avoid importing PyMuPDF's AGPL/commercial licensing choice into this build.

Project code, AudienceNet weights, procedural fixtures, and documentation are project artifacts. No paid AI API or paid plugin is required by the core system.

External research papers/standards are **referenced only**. No VI-OCR code or model is copied into BACKROW. AVIXA table values used by `physical_baseline.py` are the publicly displayed numerical guidance, with attribution and scope preserved.
