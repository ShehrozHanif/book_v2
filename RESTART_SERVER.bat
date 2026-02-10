@echo off
REM Stop any existing npm processes
taskkill /F /IM node.exe 2>nul

REM Wait a moment
timeout /t 2 /nobreak

REM Clear cache
cd /d "C:\Users\Shehroz Hanif\Desktop\Hackathon1\book\frontend\textbook-site"
call npm run clear

REM Restart server
call npm start

pause
