@echo off
title Pulse AI - Futuristic Biomechanics & Fitness Platform
color 0b
echo ==============================================================
echo             PULSE AI - FUTURISTIC FULL STACK RUNNER
echo    FastAPI Python Backend (8000) + Next.js Frontend (3000)
echo ==============================================================
echo.
cd /d "%~dp0"

echo [1/3] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "Pulse AI Backend (FastAPI)" cmd /k "cd /d "%~dp0" && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/3] Waiting 3 seconds for Backend to initialize...
timeout /t 3 /nobreak >nul

echo [3/3] Starting Next.js Frontend on http://localhost:3000 ...
start "Pulse AI Frontend (Next.js)" cmd /k "cd /d "%~dp0\frontend" && npm.cmd run dev"

timeout /t 3 /nobreak >nul
start "" "http://localhost:3000"

echo.
echo ==============================================================
echo Pulse AI is now online!
echo - Web Dashboard: http://localhost:3000
echo - FastAPI Interactive Docs: http://127.0.0.1:8000/docs
echo ==============================================================
echo (Keep this window open or close it; servers run in their own windows.)
pause
