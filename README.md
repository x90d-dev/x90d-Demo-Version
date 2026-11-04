<div align="center">

  <img src="static/corechiperagent-logo.png" alt="CoreChiperAgent Logo" width="120" style="border-radius: 50%;">

  # CoreChiperAgent

  **Private, Lightweight, and Local AI-Powered Learning Assistant**  
  *Powered by Flask, SQLite, and Ollama. Zero Paid APIs. 100% Local Inference.*

  [![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://python.org)
  [![Local AI](https://img.shields.io/badge/Inference-Ollama-000000?logo=ollama&logoColor=white)](https://ollama.com)
  [![Default Model](https://img.shields.io/badge/Model-Qwen2.5%203B-brightgreen)](https://ollama.com/library/qwen2.5)
  [![Database](https://img.shields.io/badge/Storage-SQLite-003B57?logo=sqlite&logoColor=white)](https://sqlite.org)
  [![Framework](https://img.shields.io/badge/Backend-Flask-black?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
  [![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

  <p align="center">
    <a href="#-overview">Overview</a> •
    <a href="#-key-features">Key Features</a> •
    <a href="#-system-requirements">Hardware Requirements</a> •
    <a href="#-quick-start-windows">Quick Start</a> •
    <a href="#-manual-installation">Manual Setup</a> •
    <a href="#-modes--capabilities">Capabilities</a> •
    <a href="#-project-architecture">Architecture</a>
  </p>

</div>

---

## 📌 Overview

**CoreChiperAgent** adalah aplikasi web asisten AI tutor mandiri yang didesain untuk berjalan sepenuhnya di lingkungan lokal (`localhost`). Dibuat khusus untuk laptop dengan spesifikasi standar, CoreChiperAgent menawarkan bantuan penyelesaian masalah akademik, penjelasan konsep materi, latihan ujian (termasuk TOEFL), hingga debugging pemrograman tanpa mengirimkan data ke penyedia API komersial (seperti OpenAI atau ChatGPT).

### Mengapa CoreChiperAgent?
- **Data Privacy First:** Tidak ada data percakapan, file, atau dokumen yang dikirim ke server luar. Semua diproses lokal via Ollama.
- **Resource Efficient:** Dioptimalkan secara ketat untuk laptop dengan RAM 8 GB–12 GB menggunakan model ringkas (3B parameter) tanpa menguras VRAM.
- **No Vector DB Overhead:** Menggunakan pencarian berbasis *keyword context injection* dan SQLite murni tanpa dependensi vector database yang berat.
- **Dual Interfaces:** Tersedia dalam antarmuka Web yang responsif serta Command Prompt (CLI) super cepat.

---

## ✨ Key Features

* 🧠 **Thinking Mode & Guardrails:** Lapisan prompt terstruktur untuk memicu penalaran bertahap, deteksi jebakan soal, validasi premis, dan pencegahan halusinasi sebelum jawaban akhir dibuat.
* 🎓 **Specialized Tutor Modes:** Preset konteks terarah untuk Matematika, Fisika, Kimia, Bahasa Inggris, Pemrograman, dan persiapan TOEFL Structure/Reading.
* ⚡ **CLI Direct Access:** Mengakses langsung agen AI lewat Command Line Interface (`chat_cmd.bat`) untuk alur kerja cepat tanpa browser.
* 📄 **Document & Vision Support:**
  * Ekstraksi teks dari PDF digital dan file teks sumber (`.py`, `.js`, `.json`, `.csv`, `.md`).
  * Analisis visual lokal opsional menggunakan model vision ringan (`moondream`).
* 🌐 **Zero-Cost Web Search Fallback:** Mesin pencari ringan tanpa API berbayar (DuckDuckGo/Bing scrapers) khusus untuk mengambil data mutakhir (pejabat aktif, peringkat universitas, dll).
* 🛡️ **Rule-Based Correction System (Training Mode):** Panel khusus admin untuk menambahkan aturan koreksi statis dan *smart context* instan tanpa perlunya komputasi ulang (*fine-tuning*) bobot model.

---

## 💻 System Requirements

| Komponen | Spesifikasi Minimum | Rekomendasi Ideal |
|---|---|---|
| **OS** | Windows 10/11, Linux, macOS | Windows 11 / Linux 64-bit |
| **RAM** | 8 GB | 12 GB – 16 GB |
| **Processor** | Intel Core i3 / Ryzen 3 (Quad Core) | Intel Core i5 / Ryzen 5 ke atas |
| **GPU** | Terintegrasi (Intel UHD / Vega) | NVIDIA RTX (4GB+ VRAM) untuk latensi rendah |
| **Default Model** | `qwen2.5:3b` | `qwen2.5:3b` |
| **Alternatif Ringan**| `gemma2:2b` | `llama3.2:3b` |

---

## 🚀 Quick Start (Windows)

Jika Anda menggunakan Windows, seluruh alur kerja telah diotomatisasi melalui script batch:

1. **Prasyarat:** Pastikan [Python](https://www.python.org/) dan [Ollama](https://ollama.com/) sudah terpasang.
2. **Setup Awal:**
   * Klik dua kali `setup_windows.bat` untuk menyiapkan environment dan dependensi.
   * Klik dua kali `pull_model.bat` untuk mengunduh model default (`qwen2.5:3b`).
3. **Menjalankan Aplikasi:**
   * Klik dua kali `start_ollama.bat` *(biarkan terminal tetap terbuka)*.
   * Klik dua kali `start_app.bat` *(biarkan terminal tetap terbuka)*.
4. **Buka Browser:**
   Akses antarmuka web di [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## 🛠 Manual Installation

Bagi pengguna Linux/macOS atau pengembang yang ingin menjalankan setup manual via terminal:

### 1. Konfigurasi Ollama
Unduh dan jalankan engine Ollama:
```bash
ollama serve
```
Buka jendela terminal terpisah dan unduh model:
```bash
ollama pull qwen2.5:3b

# Opsional: Jika ingin mengaktifkan dukungan Vision gambar
ollama pull moondream
```

### 2. Konfigurasi Environment Python
Clone repositori dan buat isolasi environment:
```bash
git clone https://github.com/username/CoreChiperAgent.git
cd CoreChiperAgent

# Buat virtual environment
python -m venv venv

# Aktivasi venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependensi
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Setup Konfigurasi `.env`
Salin template konfigurasi:
```bash
# Windows
copy .env.example .env

# Linux/macOS
cp .env.example .env
```

Sesuaikan parameter `.env` sesuai kebutuhan mesin Anda:
```env
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
OLLAMA_VISION_MODEL=moondream
OLLAMA_TIMEOUT=120
WEB_SEARCH_TIMEOUT=10
WEB_SEARCH_MAX_RESULTS=5
FLASK_ENV=development
DATABASE_PATH=database.db
ADMIN_DEFAULT_PASSWORD=dhafir012
```

### 4. Jalankan Server
```bash
python app.py
```
Akses web panel di `http://127.0.0.1:5000`.

---

## 🖥️ Terminal (CMD) Mode

Untuk performa ekstra cepat tanpa beban rendering browser, gunakan antarmuka baris perintah:

1. Pastikan `start_ollama.bat` atau `ollama serve` aktif.
2. Jalankan `chat_cmd.bat` (atau `python cmd_chat.py`).
3. Gunakan slash commands untuk beralih konteks:

```text
/help           - Menampilkan panduan perintah
/mode <nama>    - Ganti mode (tutor, coding, thinking, umum, toefl)
/agent normal   - Mode respon cepat dan ringkas
/agent agent    - Mode tugas analitis/eksekusi bertahap
/clear          - Bersihkan layar terminal
/exit           - Keluar dari aplikasi
```

---

## 🎯 Modes & Capabilities

```text
               ┌───────────────────────┐
               │    CoreChiperAgent    │
               └──────────┬────────────┘
                          │
     ┌────────────────────┼────────────────────┐
     ▼                    ▼                    ▼
[ Tutor Mode ]    [ Thinking Mode ]   [ Developer Mode ]
- Matematika/Fisika - Soal Jebakan/Ambigu - Code Generation
- Bedah Konsep      - Validasi Premis     - Debugging & Trace
- TOEFL/English     - Rantai Logika       - Backend & SQL
```

### 1. Mode Kerja
* **Normal Mode:** Alur percakapan ringkas dengan latensi paling rendah.
* **Agent Mode:** Berorientasi pada tindakan terstruktur (ekstraksi dokumen, instruksi bertahap, perbaikan kode dengan blok validasi).
* **Thinking Mode:** Menyuntikkan prompt analisis multi-sudut untuk memastikan akurasi data sebelum menghasilkan output ke pengguna.

### 2. Admin & Knowledge Control
* **Admin Access:** Akses halaman `/login` dengan kredensial default (`dhafir` / `dhafir012`).
* **Rule Ingestion:** Menu `/training` memungkinkan admin memasang paket aturan berbasis keyword untuk menyuntikkan fakta baku, rumus paten, atau konteks regional tanpa perlu proses fine-tuning model.

---

## 📂 Project Architecture

```plaintext
ai-tutor-lokal-ringan/
├── app.py                     # Entry point Flask server & routing
├── cmd_chat.py                # Standalone CLI chat engine
├── requirements.txt           # Dependensi Python
├── database.db                # Database SQLite (User, Riwayat, Konteks)
├── .env.example               # Template environment configuration
│
├── data/                      # Dataset, bank soal, dan evaluasi
│   ├── bank_soal_sample.json  # Bank soal latihan
│   ├── evaluation_questions.json # Test suite evaluasi kualitas jawaban
│   └── materi_sample.json     # Konteks materi lokal
│
├── modules/                   # Logika inti sistem
│   ├── chat_manager.py        # Pengelola histori dan memory window
│   ├── evaluator.py           # Evaluasi rubric jawaban
│   ├── ollama_client.py       # Wrapper API Ollama lokal
│   ├── search_service.py      # Fallback web scraping
│   └── text_extractor.py      # Ekstraksi PDF & file teks
│
├── static/                    # Aset statis frontend (CSS, JS, Logo)
├── templates/                 # Template HTML Jinja2 (UI Web Chat & Admin)
├── tests/                     # Unit test otomatis (Pytest)
│
├── setup_windows.bat          # Automasi setup environment
├── start_ollama.bat           # Automasi daemon Ollama
├── pull_model.bat             # Automasi unduh model
├── start_app.bat              # Automasi start server web
├── chat_cmd.bat               # Shortcut terminal chat
├── reset_database.bat         # Reset database SQLite
└── run_tests.bat              # Test runner
```

---

## 🧪 Testing & Validation

Proyek ini dilengkapi dengan modul pengujian otomatis berbasis `pytest`:

```bash
# Menjalankan seluruh test suite
pytest

# Menjalankan evaluasi khusus thinking mode dan scoring logic
pytest tests/test_thinking_mode.py tests/test_evaluator.py tests/test_chat_manager.py
```

---

## ⚠️ Performance Guidelines

* **Model Sizing:** Gunakan model berukuran maksimal 3B parameter jika berjalan pada RAM 8 GB–12 GB. Model 7B/8B ke atas berisiko tinggi memicu *RAM/VRAM offloading* ke disk cache yang menyebabkan respon melambat drastis.
* **Context Limit:** Context window bawaan diatur ke `2048` token dengan pembatasan maksimal 6 riwayat obrolan terakhir guna menghemat memori.
* **Scanned Document:** Parser PDF saat ini dikhususkan untuk **PDF berbasis teks digital**. PDF hasil pemindaian (*scanned images*) memerlukan transkrip manual atau model vision terpisah.

---

## 📄 License

Didistribusikan di bawah lisensi MIT. Lihat file `LICENSE` untuk informasi selengkapnya.

<div align="center">
  <sub>Dibangun secara independen untuk mendukung ekosistem AI lokal yang privat, cepat, dan terjangkau.</sub>
</div>

## 📄 Download Database On : https://drive.google.com/drive/folders/1dg7cZ7OevMS7O0olti1X8zxkJVZyvtjP?usp=sharing