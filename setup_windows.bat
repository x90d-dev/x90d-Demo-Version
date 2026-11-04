@echo off
cd /d "%~dp0"
echo Mengecek Python...
python --version >nul 2>nul
if errorlevel 1 (
  echo Python belum tersedia. Install Python dari https://www.python.org lalu jalankan ulang file ini.
  pause
  exit /b 1
)

if not exist venv\Scripts\python.exe (
  echo Membuat virtual environment...
  python -m venv venv
)

echo Menginstall dependency...
venv\Scripts\python -m pip install --upgrade pip
venv\Scripts\pip install -r requirements.txt
if errorlevel 1 (
  echo Install dependency gagal. Periksa koneksi internet atau versi Python.
  pause
  exit /b 1
)

if not exist .env (
  echo Membuat file .env dari .env.example...
  copy .env.example .env >nul
)

echo.
echo Setup selesai.
echo Jalankan pull_model.bat untuk mengunduh model.
echo Jalankan start_ollama.bat untuk menjalankan Ollama.
echo Jalankan start_app.bat untuk menjalankan aplikasi.
pause
