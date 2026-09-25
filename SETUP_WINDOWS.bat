@echo off
setlocal EnableExtensions
cd /d "%~dp0"
echo =============================================================
echo BACKROW - Windows setup
echo =============================================================
where py >nul 2>nul
if errorlevel 1 (
  where python >nul 2>nul
  if errorlevel 1 (
    echo ERROR: Python 3.11+ was not found. Install Python from python.org, enable "Add Python to PATH", then rerun.
    exit /b 10
  )
  set "PY=python"
) else (
  set "PY=py -3"
)

if not exist .venv (
  %PY% -m venv .venv || exit /b 11
)
call .venv\Scripts\activate.bat || exit /b 12
python -m pip install --upgrade pip || exit /b 13
python -m pip install -r requirements.txt || exit /b 14

where tesseract >nul 2>nul
if errorlevel 1 (
  echo Tesseract OCR was not found. Trying official Windows package through winget...
  where winget >nul 2>nul
  if errorlevel 1 goto :manual_tesseract
  winget install --id UB-Mannheim.TesseractOCR -e --accept-package-agreements --accept-source-agreements
)

if exist "C:\Program Files\Tesseract-OCR\tesseract.exe" set "PATH=C:\Program Files\Tesseract-OCR;%PATH%"
where tesseract >nul 2>nul
if errorlevel 1 goto :manual_tesseract

echo.
echo SETUP PASS
python -c "import cv2,numpy,pytesseract,pypdfium2; print('Python dependencies PASS'); print(pytesseract.get_tesseract_version())" || exit /b 15
echo Next: double-click RUN_WINDOWS.bat
exit /b 0

:manual_tesseract
echo.
echo ERROR: Tesseract OCR is still missing.
echo Install "Tesseract OCR" for Windows, default path C:\Program Files\Tesseract-OCR, then rerun this file.
exit /b 20
