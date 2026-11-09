#!/usr/bin/env bash
# Pulse AI Startup Script (Unix / macOS)

echo -e "\033[1;36m======================================================"
echo -e " 🚀 Starting Pulse AI (FastAPI + Next.js Dev Servers)"
echo -e "======================================================\033[0m"

# Start FastAPI backend
python3 -m uvicorn backend.main:app --port 8000 --reload &
BACKEND_PID=$!

trap "kill $BACKEND_PID 2> /dev/null" EXIT

sleep 2

# Start Next.js frontend
echo -e "\n\033[1;32mStarting Next.js Frontend on http://localhost:3000 ...\033[0m"
npm run dev
