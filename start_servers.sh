#!/bin/bash

echo "=========================================="
echo "Starting Personalization Demo"
echo "=========================================="
echo ""

# Start backend in background
echo "🚀 Starting Backend API (port 8000)..."
cd backend
python -m uvicorn src.main:app --reload --port 8000 &
BACKEND_PID=$!
sleep 3

# Check if backend started
if ! curl -s http://localhost:8000/api/v1/health &>/dev/null; then
  echo "⚠️ Backend not responding yet, waiting..."
  sleep 2
fi

# Start frontend in another tab/window
echo ""
echo "🚀 Starting Frontend (port 3000)..."
cd ../frontend/textbook-site
npm run start &
FRONTEND_PID=$!

echo ""
echo "=========================================="
echo "✅ Servers Started!"
echo "=========================================="
echo ""
echo "📚 Textbook: http://localhost:3000/book/"
echo "🔐 Login:    http://localhost:3000/book/login"
echo "📊 Dashboard: http://localhost:3000/book/dashboard"
echo "🔌 Backend API: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop servers"
echo "=========================================="

wait
