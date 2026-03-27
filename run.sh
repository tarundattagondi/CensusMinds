#!/bin/bash
# CensusMinds — Start both backend and frontend

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Starting CensusMinds..."
echo ""

# Start backend
echo "Starting backend..."
cd "$PROJECT_DIR"
source .venv/bin/activate
uvicorn backend.app:app --reload --port 8000 &
BACKEND_PID=$!

# Start frontend
echo "Starting frontend..."
cd "$PROJECT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "=================================="
echo "  Backend running at http://localhost:8000"
echo "  Frontend running at http://localhost:5173"
echo "=================================="
echo ""
echo "Press Ctrl+C to stop both servers."

# Trap Ctrl+C to kill both processes
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" SIGINT SIGTERM

wait
