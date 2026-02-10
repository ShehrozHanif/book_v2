@echo off
REM Start both Backend and Frontend servers for local testing

setlocal enabledelayedexpansion

echo.
echo ==========================================
echo  Personalization Demo - Local Testing
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found in PATH
    echo Please install Node.js and try again
    pause
    exit /b 1
)

echo [1/4] Checking dependencies...
echo ✓ Python found:
python --version
echo ✓ Node.js found:
node --version
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

echo [2/4] Starting Backend API (port 8000)...
cd /d "%SCRIPT_DIR%backend"
start "Backend API - Uvicorn" cmd /k python -m uvicorn src.main:app --reload --port 8000
timeout /t 3 /nobreak

echo.
echo [3/4] Starting Frontend (port 3000)...
cd /d "%SCRIPT_DIR%frontend\textbook-site"
start "Frontend - Docusaurus" cmd /k npm run start
timeout /t 2 /nobreak

echo.
echo ==========================================
echo ✅ Servers Starting!
echo ==========================================
echo.
echo 📚 Textbook: http://localhost:3000/book/
echo 🔐 Login:    http://localhost:3000/book/login
echo 📊 Dashboard: http://localhost:3000/book/dashboard
echo 🔌 Backend API: http://localhost:8000
echo.
echo ==========================================
echo Instructions:
echo 1. Wait for browser to open automatically
echo 2. Go to http://localhost:3000/book/login
echo 3. Create an account and test features
echo 4. Close terminal windows to stop servers
echo ==========================================
echo.

REM Keep this window open so user can see the message
timeout /t 5 /nobreak
