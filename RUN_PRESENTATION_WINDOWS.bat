@echo off
set PORT=8080
start "BACKROW SERVER" cmd /k python server.py
ping 127.0.0.1 -n 3 >nul
start "" http://127.0.0.1:8080/present.html
