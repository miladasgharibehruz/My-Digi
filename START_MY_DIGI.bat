@echo off
setlocal
cd /d "%~dp0"
set "PY=python"
for /f "delims=" %%P in ('py -3.13 -c "import sys; print(sys.executable)" 2^>nul') do set "PY=%%P"
"%PY%" -c "import PIL, webview" >nul 2>&1
if errorlevel 1 (
  echo Installing required My Digi components for Python 3.13...
  "%PY%" -m pip install -r requirements.txt
  if errorlevel 1 (
    echo Installation failed.
    echo My Digi requires regular CPython 3.13 for the calculator window.
    pause
    exit /b 1
  )
)
"%PY%" "My_Digi(1).py"
if errorlevel 1 pause
