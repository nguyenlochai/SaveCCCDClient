@echo off
setlocal
cd /d "%~dp0"
set "PY=python"
if exist "%LOCALAPPDATA%\hermes\hermes-agent\venv\Scripts\python.exe" set "PY=%LOCALAPPDATA%\hermes\hermes-agent\venv\Scripts\python.exe"
"%PY%" -c "import tkinter" >nul 2>&1
if errorlevel 1 (
  echo Can Python 3 voi Tkinter.
  pause
  exit /b 1
)
"%PY%" -c "import PIL, cv2, numpy" >nul 2>&1
if errorlevel 1 (
  echo Dang cai thu vien Pillow va quet QR. Buoc cai dat can Internet.
  where uv >nul 2>&1
  if not errorlevel 1 (
    uv pip install --python "%PY%" -r requirements.txt
  ) else (
    "%PY%" -m ensurepip --upgrade
    "%PY%" -m pip install -r requirements.txt
  )
)
"%PY%" -c "import tkinter, PIL, cv2, numpy" >nul 2>&1
if errorlevel 1 (
  echo Khong cai duoc thu vien. Kiem tra Internet va thu lai.
  echo Cai thu cong bang dung Python: "%PY%" -m pip install -r requirements.txt
  pause
  exit /b 1
)
"%PY%" -B app.py
if errorlevel 1 pause
