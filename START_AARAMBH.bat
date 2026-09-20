@echo off
setlocal
cd /d "%~dp0"
echo Starting AARAMBH backend and frontend...
start "AARAMBH Backend" powershell -NoExit -ExecutionPolicy Bypass -Command "Set-Location -LiteralPath '%~dp0backend'; .\venv\Scripts\Activate.ps1; python -m uvicorn app.main:app --reload"
timeout /t 2 /nobreak >nul
start "AARAMBH Frontend" powershell -NoExit -ExecutionPolicy Bypass -Command "Set-Location -LiteralPath '%~dp0frontend'; npm.cmd run dev"
echo.
echo AARAMBH is starting.
echo Open http://localhost:5173 after the frontend window shows VITE ready.
endlocal
