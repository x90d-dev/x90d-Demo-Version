@echo off
cd /d "%~dp0"
where ollama >nul 2>nul
if errorlevel 1 (
  echo Ollama belum terinstall. Install dari https://ollama.com lalu jalankan ulang file ini.
  pause
  exit /b 1
)

echo Model default qwen2.5:3b sedang diunduh. Proses ini hanya perlu dilakukan sekali.
ollama pull qwen2.5:3b
if errorlevel 1 (
  echo Gagal mengunduh model. Pastikan Ollama berjalan normal dan koneksi internet tersedia.
  pause
  exit /b 1
)

echo Model qwen2.5:3b siap digunakan.
echo.
echo Opsional untuk membaca gambar:
echo Jalankan perintah ini jika ingin fitur vision aktif:
echo ollama pull moondream
pause
