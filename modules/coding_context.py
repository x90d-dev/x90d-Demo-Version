import re


APP_BUILDER_KEYWORDS = [
    "buat aplikasi",
    "membuat aplikasi",
    "aplikasi python",
    "project python",
    "struktur folder",
    "arsitektur",
    "crud",
    "database",
    "sqlite",
    "flask",
    "fastapi",
    "django",
    "tkinter",
    "streamlit",
    "api",
    "backend",
    "frontend",
    "full stack",
    "desktop app",
    "web app",
    "advance",
    "advanced",
    "expert",
    "profesional",
    "production",
    "lengkap",
    "besar",
    "panjang",
    "serius",
    "kompleks",
]

DEBUG_KEYWORDS = ["debug", "error", "traceback", "bug", "exception", "gagal jalan", "tidak jalan"]

FILE_AUTOMATION_KEYWORDS = [
    "rename file",
    "rename otomatis",
    "ubah nama file",
    "ganti nama file",
    "bulk rename",
    "file otomatis",
    "folder",
    "direktori",
]


def detect_coding_complexity(message: str) -> str:
    text = (message or "").lower()
    if not text.strip():
        return "none"
    if _has_any(text, APP_BUILDER_KEYWORDS) or (_has_any(text, DEBUG_KEYWORDS) and len(text) > 350):
        return "project"
    if _has_any(text, DEBUG_KEYWORDS):
        return "debug"
    if _has_any(text, ["python", "kode", "coding", "program", "script", "function", "class"]):
        return "code"
    return "none"


def build_coding_context(message: str) -> str:
    complexity = detect_coding_complexity(message)
    if complexity == "none":
        return ""

    lines = [
        "Developer Mode: AKTIF",
        "Peran: bantu Admin sebagai software architect dan Python/full-stack developer.",
        "Aturan wajib coding:",
        "- Pahami tujuan aplikasi sebelum menulis kode.",
        "- Jika kebutuhan belum lengkap, sebutkan asumsi secara jelas.",
        "- Jangan memberi kode toy/contoh minimal jika Admin meminta aplikasi atau tool. Berikan versi siap pakai yang rapi.",
        "- Jika Admin meminta coding advance/expert/panjang/lengkap, jangan berhenti di beberapa baris. Buat solusi proyek yang utuh dan bisa dijalankan.",
        "- Hindari bug dasar seperti if name == 'main'. Gunakan if __name__ == '__main__': untuk Python script.",
        "- Untuk project aplikasi, mulai dari struktur folder, alur data, modul utama, lalu kode inti.",
        "- Tulis kode dalam fenced code block dengan nama bahasa, misalnya ```python, agar tombol Copy muncul.",
        "- Pisahkan file berbeda dengan judul path file sebelum code block.",
        "- Jangan memberi kode setengah jadi tanpa menjelaskan cara menjalankan dan cara test.",
        "- Utamakan kode yang sederhana dirawat, error handling jelas, dan dependency tidak berlebihan.",
        "- Untuk kode panjang, bagi menjadi beberapa file/blok yang rapi. Jangan meringkas bagian penting dengan komentar seperti 'lanjutkan sendiri' atau 'kode lainnya sama'.",
        "- Wajib jaga kualitas expert: struktur modular, validasi input, logging bila perlu, konfigurasi environment, error handling, keamanan dasar, dan test minimal.",
        "- Self-check coding sebelum final: apakah kode bisa dijalankan, import benar, entry point benar, input tervalidasi, error handling ada, dan edge case utama sudah dipikirkan.",
        "- Jika request menyangkut data/file/user input, prioritaskan keamanan dasar: jangan overwrite diam-diam, jangan hardcode secret, dan beri mode preview bila risikonya tinggi.",
    ]

    if complexity == "project":
        lines.extend(
            [
                "Format untuk coding aplikasi:",
                "1. Ringkasan solusi",
                "2. Arsitektur singkat dan alasan desain",
                "3. Struktur folder",
                "4. Kode per file lengkap",
                "5. Konfigurasi dan dependency",
                "6. Cara menjalankan",
                "7. Cara test",
                "8. Edge case dan keamanan",
                "9. Pengembangan berikutnya",
                "Standar proyek advance:",
                "- Jika aplikasi cukup besar, gunakan layer yang jelas: route/controller, service, data/database, validation, dan utility.",
                "- Untuk Python, gunakan pathlib, dataclass/type hints bila membantu, fungsi kecil, dan entry point yang benar.",
                "- Untuk Flask/API, sediakan route, validasi JSON/form, status code tepat, template/static bila perlu, dan SQLite schema jika memakai database.",
                "- Untuk CLI/tool, sediakan argparse, --help, dry-run bila operasi berisiko, dan contoh command.",
                "- Untuk test, minimal beri pytest/unit test untuk logika penting atau langkah manual test yang konkret.",
            ]
        )
    if _has_any((message or "").lower(), FILE_AUTOMATION_KEYWORDS):
        lines.extend(
            [
                "Checklist khusus file automation / rename tool:",
                "- Gunakan pathlib, argparse, dataclass bila membantu, dan fungsi kecil yang mudah dites.",
                "- Wajib ada opsi --dry-run untuk preview tanpa mengubah file.",
                "- Wajib ada validasi folder, filter ekstensi, recursive opsional, dan exclude pattern bila relevan.",
                "- Wajib aman dari overwrite dengan collision handling: suffix angka atau timestamp.",
                "- Wajib membuat log operasi rename agar bisa diaudit.",
                "- Jika memungkinkan, sediakan fitur --undo dari log.",
                "- Sertakan contoh perintah menjalankan dan minimal test pytest untuk fungsi penamaan/collision.",
                "- Jelaskan risiko rename massal dan sarankan dry-run dulu.",
            ]
        )
    elif complexity == "debug":
        lines.extend(
            [
                "Format debugging:",
                "1. Akar kemungkinan masalah",
                "2. Baris/konsep yang perlu dicek",
                "3. Perbaikan kode",
                "4. Cara memastikan bug selesai",
            ]
        )
    else:
        lines.extend(
            [
                "Format kode pendek:",
                "1. Kode",
                "2. Penjelasan singkat",
                "3. Cara menjalankan",
            ]
        )

    return "\n".join(lines)


def _has_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)
