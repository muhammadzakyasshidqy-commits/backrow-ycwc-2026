@echo off
setlocal
cd /d "%~dp0"
python tests\run_all.py --with-browser
if errorlevel 1 goto :fail
echo.
echo BACKROW V11 full verification PASS.
exit /b 0
:fail
echo.
echo BACKROW V11 verification FAILED.
exit /b 1
