@echo off
setlocal EnableExtensions
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo ERROR: Setup has not been run. Double-click SETUP_WINDOWS.bat first.
  pause
  exit /b 10
)
if exist "C:\Program Files\Tesseract-OCR\tesseract.exe" set "PATH=C:\Program Files\Tesseract-OCR;%PATH%"
call .venv\Scripts\activate.bat || exit /b 11
set "BACKROW_HOST=0.0.0.0"
set "PORT=8080"
echo BACKROW field-validation mode is starting on the trusted local network.
echo Main product:        http://127.0.0.1:8080/
echo Validation console: http://127.0.0.1:8080/validate.html
echo Do not expose this development server directly to the public internet.
start "" "http://127.0.0.1:8080/"
start "" "http://127.0.0.1:8080/validate.html"
python server.py
