#!/bin/bash

# Hackathon1 Book - Local Testing Setup Script
# For Mac and Linux users

echo "========================================"
echo "Hackathon1 Book - Local Testing Setup"
echo "========================================"
echo ""

# Check if Docker is installed
echo "Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed"
    echo "Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo "✓ Docker is installed"
docker --version
echo ""

# Navigate to project directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"
echo "Project directory: $PROJECT_DIR"
echo ""

# Start Docker services
echo "========================================"
echo "Starting Docker Services..."
echo "========================================"
docker-compose up -d
echo ""

# Wait for services to be healthy
echo "Waiting for services to become healthy (15 seconds)..."
sleep 15
echo ""

# Check service status
echo "Checking service status..."
docker-compose ps
echo ""

# Test API health
echo "Testing API health..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ API is responding"
else
    echo "⚠ API not responding yet, waiting..."
    sleep 10
fi
echo ""

# Start Docusaurus in background
echo "========================================"
echo "Starting Docusaurus Documentation..."
echo "========================================"
echo ""
cd frontend/textbook-site
echo "Installing dependencies..."
npm install > /dev/null 2>&1
echo "Starting Docusaurus..."
npm run start > /tmp/docusaurus.log 2>&1 &
DOCUSAURUS_PID=$!
echo "Docusaurus PID: $DOCUSAURUS_PID"
echo ""

# Wait for Docusaurus to start
echo "Waiting for Docusaurus to start (10 seconds)..."
sleep 10
echo ""

# Open browsers (Mac and Linux)
echo "========================================"
echo "Opening browser windows..."
echo "========================================"
echo ""

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # Mac
    open http://localhost:3000
    sleep 2
    open http://localhost:8000/docs
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open http://localhost:3000 &
    sleep 2
    xdg-open http://localhost:8000/docs &
fi

echo ""
echo "========================================"
echo "✓ Services Started Successfully!"
echo "========================================"
echo ""
echo "Available URLs:"
echo "  📚 Docusaurus Book:   http://localhost:3000"
echo "  🔌 API Docs:          http://localhost:8000/docs"
echo "  📊 ReDoc:             http://localhost:8000/redoc"
echo "  ✅ Health Check:      http://localhost:8000/health"
echo ""
echo "Services running:"
echo "  - PostgreSQL:    localhost:5432"
echo "  - Redis:         localhost:6379"
echo "  - FastAPI:       localhost:8000"
echo ""
echo "To stop services, run:"
echo "  docker-compose down"
echo ""
echo "Docusaurus logs: tail -f /tmp/docusaurus.log"
echo ""
echo "Press Ctrl+C to stop or close this window"
echo ""

# Keep script running
wait $DOCUSAURUS_PID
