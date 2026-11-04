@echo off
cd /d "%~dp0"

if not exist venv\Scripts\python.exe (
  echo Virtual environment belum ada. Jalankan setup_windows.bat terlebih dahulu.
  pause
  exit /b 1
)

echo Menjalankan CoreChiperAgent CMD Chat.
echo Pastikan Ollama sudah berjalan. Jika belum, jalankan start_ollama.bat di window lain.
echo.

venv\Scripts\python.exe cmd_chat.py

echo.
pause
