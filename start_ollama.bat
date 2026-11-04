@echo off
cd /d "%~dp0"
where ollama >nul 2>nul
if errorlevel 1 (
  echo Ollama belum terinstall. Install dari https://ollama.com lalu jalankan ulang file ini.
  pause
  exit /b 1
)

echo Mengecek apakah Ollama sudah berjalan...
powershell -NoProfile -Command "try { Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 3 > $null; exit 0 } catch { exit 1 }"
if not errorlevel 1 (
  echo Ollama sudah berjalan di http://127.0.0.1:11434.
  echo Tidak perlu membuka server Ollama kedua.
  echo Sekarang jalankan start_app.bat untuk membuka CoreChiperAgent.
  pause
  exit /b 0
)

echo Menjalankan Ollama server lokal.
echo Window ini harus tetap terbuka selama aplikasi digunakan.
ollama serve
echo Ollama berhenti atau terjadi error.
pause
