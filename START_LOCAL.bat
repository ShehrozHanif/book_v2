@echo off
REM Start Hackathon1 Book locally - Complete Setup Script
REM This script starts all services and opens browsers

echo ========================================
echo Hackathon1 Book - Local Testing Setup
echo ========================================
echo.

REM Check if Docker is installed
echo Checking Docker...
docker --version
if errorlevel 1 (
    echo ERROR: Docker is not installed or not in PATH
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo ✓ Docker is installed
echo.

REM Navigate to project directory
cd /d "%~dp0"
echo Current directory: %cd%
echo.

REM Start Docker services
echo ========================================
echo Starting Docker Services...
echo ========================================
docker-compose up -d
echo.

REM Wait for services to be healthy
echo Waiting for services to become healthy (15 seconds)...
timeout /t 15 /nobreak
echo.

REM Check service status
echo Checking service status...
docker-compose ps
echo.

REM Test API health
echo Testing API health...
for /f %%i in ('curl -s http://localhost:8000/health') do set health=%%i
if "%health%"=="" (
    echo ⚠ API not responding yet, waiting...
    timeout /t 10 /nobreak
) else (
    echo ✓ API is responding
)
echo.

REM Start Docusaurus in new terminal window
echo ========================================
echo Starting Docusaurus Documentation...
echo ========================================
echo.
echo Starting Docusaurus in new terminal window...
start cmd /k "cd frontend\textbook-site && npm install && npm run start"
echo.

REM Wait for Docusaurus to start
timeout /t 10 /nobreak
echo.

REM Open browsers
echo ========================================
echo Opening browser windows...
echo ========================================
echo.

echo Opening Docusaurus at http://localhost:3000
start http://localhost:3000

timeout /t 3 /nobreak

echo Opening API Docs at http://localhost:8000/docs
start http://localhost:8000/docs

echo.
echo ========================================
echo ✓ Services Started Successfully!
echo ========================================
echo.
echo Available URLs:
echo   📚 Docusaurus Book:   http://localhost:3000
echo   🔌 API Docs:          http://localhost:8000/docs
echo   📊 ReDoc:             http://localhost:8000/redoc
echo   ✅ Health Check:      http://localhost:8000/health
echo.
echo Services running:
echo   - PostgreSQL:    localhost:5432
echo   - Redis:         localhost:6379
echo   - FastAPI:       localhost:8000
echo.
echo To stop services, run:
echo   docker-compose down
echo.
pause
