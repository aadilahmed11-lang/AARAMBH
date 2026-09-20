@echo off
setlocal
cd /d "%~dp0"
echo ==============================================
echo AARAMBH - First Time Setup
 echo ==============================================
if not exist backend\venv (
  echo Creating Python environment...
  py -m venv backend\venv
)
call backend\venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
if not exist frontend\node_modules (
  echo Installing frontend packages...
  cd frontend
  npm.cmd install
  cd ..
)
echo.
echo Setup complete. Starting AARAMBH...
call START_AARAMBH.bat
endlocal
