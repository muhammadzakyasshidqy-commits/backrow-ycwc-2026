@echo off
setlocal EnableExtensions
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo ERROR: Setup has not been run. Double-click SETUP_WINDOWS.bat first.
  pause
  exit /b 10
)
if exist "C:\Program Files\Tesseract-OCR\tesseract.exe" set "PATH=C:\Program Files\Tesseract-OCR;%PATH%"
call .venv\Scripts\activate.bat
set "BACKROW_HOST=127.0.0.1"
set "PORT=8080"
start "" "http://127.0.0.1:8080"
echo BACKROW is starting at http://127.0.0.1:8080
echo Keep this window open. Press Ctrl+C to stop.
python server.py
