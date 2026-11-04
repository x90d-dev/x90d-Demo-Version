@echo off
cd /d "%~dp0"
if not exist venv\Scripts\python.exe (
  echo Virtual environment belum ada. Jalankan setup_windows.bat terlebih dahulu.
  pause
  exit /b 1
)

echo Menjalankan CoreChiperAgent.
echo Buka browser ke http://127.0.0.1:5000
echo Window ini harus tetap terbuka selama website digunakan.
venv\Scripts\python app.py
echo Aplikasi berhenti atau terjadi error.
pause
