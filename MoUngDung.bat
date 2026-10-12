@echo off
setlocal
cd /d "%~dp0"
set "PY=python"
if exist "%LOCALAPPDATA%\hermes\hermes-agent\venv\Scripts\python.exe" set "PY=%LOCALAPPDATA%\hermes\hermes-agent\venv\Scripts\python.exe"
"%PY%" -c "import tkinter, PIL" >nul 2>&1
if errorlevel 1 (
  echo Can Python 3 voi Tkinter va Pillow.
  echo Cai thu vien bang: python -m pip install -r requirements.txt
  pause
  exit /b 1
)
"%PY%" -B app.py
if errorlevel 1 pause
