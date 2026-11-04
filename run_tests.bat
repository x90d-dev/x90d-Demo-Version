@echo off
cd /d "%~dp0"
if not exist venv\Scripts\python.exe (
  echo Virtual environment belum ada. Jalankan setup_windows.bat terlebih dahulu.
  pause
  exit /b 1
)

venv\Scripts\pytest
pause
