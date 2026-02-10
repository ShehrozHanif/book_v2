@echo off
echo Killing all Node and Python processes...
taskkill /IM node.exe /F 2>nul
taskkill /IM python.exe /F 2>nul
timeout /t 3 /nobreak

echo.
echo Starting backend on port 3000...
cd /d "C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\backend"
start "Backend Server" cmd /k "python -m uvicorn src.main:app --host 0.0.0.0 --port 3000 --reload"

echo.
echo Server starting on http://localhost:3000
echo Access the app at: http://localhost:3000/book/
timeout /t 5
start http://localhost:3000/book/
