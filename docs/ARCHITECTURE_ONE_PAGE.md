# BACKROW 11.0 — Architecture in One Page

```text
SOURCE PDF / IMAGE
│
├─ PDFium render
├─ source OCR (Tesseract LSTM; third-party pretrained AI)
├─ source ORB page signature
└─ source-only room/display geometry comparator (non-AI)
             │
             │
REAL AUDIENCE CAMERA / PHOTO
             │
             ├─ deck retrieval across source pages
             ├─ geometric verification
             ├─ RANSAC homography
             └─ rectified audience frame
                         │
            ┌────────────┴────────────┐
            │                         │
  exact OCR / numeric evidence   AudienceNet 2.0
  direct content recovery        custom 48→24 MLP
            │                         │
            └────────────┬────────────┘
                         │
             conservative evidence hierarchy
                         │
       RECOVERED / WATCH / AT RISK / ABSTAIN
                         │
               localized source evidence
                         │
                 targeted repair
                         │
                      RESCAN
```

## AudienceNet 2.0 features

16 paired source/camera/room features including structural correlation, contrast/sharpness ratios, glare/dark fractions, edge ratio, relative text height, source OCR confidence, token/numeric context, and optional viewing-ratio/physical-geometry features.

## Evidence priority

`verified exact information loss > strong OCR/region evidence > AudienceNet > weak heuristics`.

## Human calibration layer

Optional `FieldCalibrator` is deliberately absent until sufficient real blinded physical data exists. It may be trained only on calibration/development studies with valid timed-exposure logs. Locked final studies are rejected if leaked into calibration metadata.

## Privacy/deployment

Core runtime uses the BACKROW server instance the user opened and no third-party AI API. Field studies use a trusted LAN, separate admin/participant access, blocked raw study files, and immutable participant submissions.
