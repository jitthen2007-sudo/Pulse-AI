@echo off
title Pulse AI - Full-Stack Fitness Platform
color 0b

echo ======================================================================
echo                   PULSE AI - LAUNCHER
echo ======================================================================
echo.

cd /d "%~dp0"

echo [1/3] Starting FastAPI Backend on port 8000...
start "Pulse AI Backend" cmd /k "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"

timeout /t 2 >nul

echo [2/3] Starting Next.js Frontend on port 3000...
start "Pulse AI Frontend" cmd /k "npm start"

timeout /t 3 >nul

echo [3/3] Opening Pulse AI in your browser...
start http://localhost:3000

echo.
echo ======================================================================
echo  READY! Pulse AI is running live on your PC:
echo.
echo  PC Browser:      http://localhost:3000
echo  Phone (Wi-Fi):   http://192.168.1.10:3000
echo ======================================================================
echo.
pause
