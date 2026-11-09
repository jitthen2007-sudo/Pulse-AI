# Pulse AI Development Startup Script (Windows PowerShell)
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host " 🚀 Starting Pulse AI (FastAPI + Next.js Dev Servers)" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan

# 1. Start FastAPI Backend in background job
Write-Host "`n[1/2] Starting FastAPI Backend on http://127.0.0.1:8000 ..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PSScriptRoot
    python -m uvicorn backend.main:app --port 8000 --reload
}

Start-Sleep -Seconds 2

# 2. Start Next.js Frontend
Write-Host "[2/2] Starting Next.js Frontend on http://localhost:3000 ..." -ForegroundColor Green
Write-Host "`nOpen http://localhost:3000 in your browser to use Pulse AI!`n" -ForegroundColor Cyan

try {
    npm.cmd run dev
} finally {
    Write-Host "`nStopping backend server..." -ForegroundColor Yellow
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob -ErrorAction SilentlyContinue
}
