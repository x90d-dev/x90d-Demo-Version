@echo off
cd /d "%~dp0"
if not exist venv\Scripts\python.exe (
  echo Virtual environment belum ada. Jalankan setup_windows.bat terlebih dahulu.
  pause
  exit /b 1
)

echo PERINGATAN: Ini akan menghapus database.db dan semua riwayat latihan.
set /p confirm=Ketik YES untuk melanjutkan: 
if /I not "%confirm%"=="YES" (
  echo Reset database dibatalkan.
  pause
  exit /b 0
)

if exist database.db (
  del /f /q database.db
)

venv\Scripts\python -c "from modules.database import init_db; init_db()"
echo Database baru sudah dibuat.
pause
