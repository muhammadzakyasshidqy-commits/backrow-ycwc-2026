# Deployment & Field-Study Networking

BACKROW is a Python local web service plus static browser UI. Core inference does not call a cloud AI API.

## Normal local run

Windows:
1. `SETUP_WINDOWS.bat` once.
2. `RUN_WINDOWS.bat`.
3. Open `http://127.0.0.1:8080` in Chrome/Edge.

Localhost is a secure browser context for camera permission.

## Field-study LAN run

Use `RUN_FIELD_STUDY_WINDOWS.bat` (or the Linux/macOS equivalent). This binds to `0.0.0.0` so reader phones on the same trusted LAN can open the participant form.

The participant page does not need camera permission. The presenter/admin link contains a random secret token; do not distribute that URL to readers. The raw `data/` path is denied by the HTTP handler.

This built-in server is intended for a controlled local study, **not direct public-internet exposure**.

## Docker/public YCWC preview

The included `Dockerfile` installs Tesseract and runtime dependencies and exposes port 8080.

```bash
docker build -t backrow-ycwc .
docker run --rm -p 8080:8080 backrow-ycwc
```

Use an HTTPS reverse proxy/platform for any public hosted link because browser camera access on public origins requires HTTPS. Do not expose field-study raw data publicly. For a public demo, use the judge fixtures or a separately hardened storage/auth deployment.

Before submission, repeat health, API, browser, request-size, and camera-permission tests against the actual hosted URL.
