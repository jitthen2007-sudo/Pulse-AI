# Pulse AI Full-Stack Development Runner
Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host "             PULSE AI - FULL STACK RUNNER" -ForegroundColor Cyan
Write-Host "    FastAPI Backend (:8000) + Next.js Frontend (:3000)" -ForegroundColor Cyan
Write-Host "==============================================================" -ForegroundColor Cyan

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. Start FastAPI Backend
Write-Host "`n[1/3] Starting FastAPI Backend on http://127.0.0.1:8000..." -ForegroundColor Yellow
$backend = Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload" -WorkingDirectory $projectRoot -PassThru

Start-Sleep -Seconds 2

# 2. Start Next.js Frontend
Write-Host "[2/3] Starting Next.js Frontend on http://localhost:3000..." -ForegroundColor Yellow
$frontend = Start-Process -FilePath "npm.cmd" -ArgumentList "run", "dev" -WorkingDirectory (Join-Path $projectRoot "frontend") -PassThru

Start-Sleep -Seconds 2
Start-Process "http://localhost:3000"

Write-Host "`n[3/3] Both services are live!" -ForegroundColor Green
Write-Host "  * Frontend UI: http://localhost:3000" -ForegroundColor White
Write-Host "  * Backend API: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "`nPress Ctrl+C or close this window to terminate both servers." -ForegroundColor Gray

try {
    Wait-Process -Id $frontend.Id
} finally {
    Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $frontend.Id -Force -ErrorAction SilentlyContinue
}
