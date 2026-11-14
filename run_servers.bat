@echo off
title Pulse AI - Full Stack Development Runner
color 0b
echo ==============================================================
echo             PULSE AI - FULL STACK RUNNER
echo    FastAPI Python Backend (8000) + Next.js Frontend (3000)
echo ==============================================================
echo.
cd /d "%~dp0"

echo [1/3] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "Pulse AI Backend (FastAPI)" cmd /k "cd /d %~dp0 && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/3] Waiting for Backend to initialize...
timeout /t 3 /nobreak >nul

echo [3/3] Starting Next.js Frontend on http://localhost:3000 ...
start "Pulse AI Frontend (Next.js)" cmd /k "cd /d %~dp0\frontend && npm run dev"

timeout /t 2 /nobreak >nul
start "" "http://localhost:3000"

echo.
echo ==============================================================
echo Pulse AI is now running!
echo - Frontend UI: http://localhost:3000
echo - FastAPI Docs: http://127.0.0.1:8000/docs
echo ==============================================================
pause
