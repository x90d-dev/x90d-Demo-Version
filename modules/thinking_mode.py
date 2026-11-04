import re


TASK_LABELS = {
    "coding": "coding",
    "debugging": "debugging",
    "concept": "konsep",
    "math": "matematika/logika",
    "fact": "fakta/pengetahuan umum",
    "analysis": "analisis",
    "writing": "penulisan",
    "ambiguous": "ambigu",
    "trick": "jebakan/premis rawan",
    "general": "umum",
}

CODING_KEYWORDS = [
    "python",
    "javascript",
    "html",
    "css",
    "flask",
    "django",
    "fastapi",
    "sqlite",
    "sql",
    "api",
    "backend",
    "frontend",
    "kode",
    "coding",
    "program",
    "aplikasi",
    "script",
    "class",
    "function",
    "algoritma",
]

DEBUG_KEYWORDS = [
    "traceback",
    "typeerror",
    "valueerror",
    "indexerror",
    "keyerror",
    "exception",
    "syntaxerror",
    "error:",
    "bug",
    "debug",
    "gagal jalan",
    "tidak jalan",
    "crash",
]

CONCEPT_KEYWORDS = [
    "apa itu",
    "apa yang dimaksud",
    "jelaskan konsep",
    "perbedaan",
    "machine learning",
    "feature",
    "label",
    "target",
    "precision",
    "recall",
    "accuracy",
    "data leakage",
    "correlation",
    "causation",
    "authentication",
    "authorization",
    "race condition",
]

FACT_KEYWORDS = [
    "siapa",
    "kapan",
    "di mana",
    "saat ini",
    "terbaru",
    "tahun ini",
    "ranking",
    "top 10",
    "harga",
    "berita",
    "presiden",
    "menteri",
]

ANALYSIS_KEYWORDS = [
    "analisis",
    "evaluasi",
    "bandingkan",
    "bottleneck",
    "data analysis",
    "dataset",
    "grafik",
    "rata-rata",
    "median",
    "anomali",
]

WRITING_KEYWORDS = [
    "ringkas",
    "rangkum",
    "tulis",
    "buatkan teks",
    "perbaiki tulisan",
    "parafrase",
    "kerangka",
    "esai",
    "surat",
]

TRICK_KEYWORDS = [
    "pasti",
    "selalu",
    "tidak pernah",
    "hanya",
    "semua",
    "mana yang benar",
    "apakah benar",
    "premis",
    "jebakan",
    "99%",
]

AMBIGUOUS_MARKERS = [
    "ini",
    "itu",
    "tersebut",
    "yang mana",
    "bagaimana caranya",
    "bagus tidak",
    "lebih baik",
]


def detect_task_type(message: str, subject: str | None = None, question_type: str | None = None) -> str:
    text = (message or "").strip().lower()
    if not text:
        return "general"

    if _has_any(text, DEBUG_KEYWORDS):
        return "debugging"
    if looks_trick_question(text):
        return "trick"
    if _has_any(text, CONCEPT_KEYWORDS) and _is_concept_question(text):
        return "concept"
    if _is_coding_request(text) or subject == "coding":
        return "coding"
    if subject in {"matematika", "fisika", "kimia"} or question_type == "calculation" or _looks_math(text):
        return "math"
    if _has_any(text, CONCEPT_KEYWORDS):
        return "concept"
    if _has_any(text, ANALYSIS_KEYWORDS):
        return "analysis"
    if _has_any(text, WRITING_KEYWORDS):
        return "writing"
    if _has_any(text, FACT_KEYWORDS):
        return "fact"
    if looks_ambiguous(text):
        return "ambiguous"
    return "general"


def looks_trick_question(message: str) -> bool:
    text = (message or "").lower()
    if not text:
        return False
    if _has_any(text, TRICK_KEYWORDS) and any(mark in text for mark in ["?", "apakah", "jika", "kalau"]):
        return True
    return bool(re.search(r"\b(semua|selalu|pasti|hanya|tidak pernah)\b", text))


def looks_ambiguous(message: str) -> bool:
    text = (message or "").strip().lower()
    if not text:
        return False
    tokens = re.findall(r"\w+", text)
    if len(tokens) <= 4 and _has_any(text, AMBIGUOUS_MARKERS):
        return True
    return "lebih baik" in text and not any(word in text for word in ["untuk", "karena", "dibanding"])


def build_self_check_context(message: str, mode: str = "auto", subject: str | None = None, question_type: str | None = None) -> str:
    task_type = detect_task_type(message, subject=subject, question_type=question_type)
    task_label = TASK_LABELS.get(task_type, "umum")
    return (
        "Self-check internal sebelum final:\n"
        f"- Jenis tugas: {task_label}. Pilih format jawaban yang cocok untuk jenis tugas ini.\n"
        "- Pastikan jawaban menjawab pertanyaan utama, bukan melebar.\n"
        "- Cek istilah mirip, asumsi tersembunyi, ambiguitas, dan kemungkinan jebakan.\n"
        "- Jangan mengarang fakta, angka, sumber, atau detail yang tidak ada dasar.\n"
        "- Jika data belum cukup atau butuh info terbaru, sebutkan keterbatasannya.\n"
        "- Untuk coding/debugging, pastikan solusi bisa dijalankan, ada error handling, edge case, dan cara test.\n"
        "- Untuk matematika/logika, cek angka, satuan, syarat, dan validasi jawaban akhir.\n"
        "- Lakukan self-check ini secara internal; tampilkan hanya ringkasan cek ulang bila membantu Admin."
    )


def build_thinking_mode_context(
    message: str,
    mode: str = "auto",
    subject: str | None = None,
    question_type: str | None = None,
) -> str:
    task_type = detect_task_type(message, subject=subject, question_type=question_type)
    format_rule = _format_rule_for_task(task_type)
    risk_rule = _risk_rule_for_task(task_type)
    return (
        "Thinking Mode: AKTIF\n"
        "Tujuan: membuat jawaban lebih teliti, akurat, tidak asal yakin, dan tetap praktis.\n"
        f"Jenis tugas terdeteksi: {TASK_LABELS.get(task_type, 'umum')}.\n"
        "Langkah internal wajib:\n"
        "- Baca pertanyaan dua kali secara konseptual: tujuan Admin dan batasan data.\n"
        "- Tentukan apakah tugasnya coding, debugging, konsep, matematika, fakta, analisis, atau penulisan.\n"
        "- Periksa ambiguitas, premis salah, kata ekstrem, data kurang, dan risiko halusinasi.\n"
        "- Jawab dengan format yang paling cocok, tidak terlalu panjang jika soal sederhana.\n"
        f"{format_rule}\n"
        f"{risk_rule}\n"
        f"{build_self_check_context(message, mode=mode, subject=subject, question_type=question_type)}"
    )


def _format_rule_for_task(task_type: str) -> str:
    if task_type == "debugging":
        return "Format debugging: masalah yang ditemukan, penyebab paling mungkin, solusi, kode/perintah bila perlu, cara verifikasi."
    if task_type == "coding":
        return "Format coding: tujuan, desain singkat, struktur/file bila project, kode runnable, cara menjalankan, cara test, edge case."
    if task_type == "math":
        return "Format hitungan: diketahui, ditanya, langkah, validasi syarat/satuan, jawaban akhir."
    if task_type == "concept":
        return "Format konsep: jawaban inti, penjelasan sederhana, contoh konkret, catatan salah-paham umum."
    if task_type == "fact":
        return "Format fakta: jawab inti, sebutkan apakah informasi bisa berubah, gunakan sumber/konteks terbaru jika tersedia."
    if task_type == "analysis":
        return "Format analisis: masalah, metode analisis, temuan utama, batasan, rekomendasi praktis."
    if task_type == "writing":
        return "Format penulisan: hasil siap pakai, versi ringkas/rapi, dan catatan gaya bila perlu."
    if task_type in {"ambiguous", "trick"}:
        return "Format rawan: jelaskan interpretasi/premis, koreksi jebakan bila ada, lalu jawab berdasarkan asumsi yang dinyatakan."
    return "Format umum: jawaban inti, penjelasan singkat, contoh/catatan bila perlu."


def _risk_rule_for_task(task_type: str) -> str:
    if task_type == "coding":
        return "Risiko coding yang harus dicek: input kosong, path tidak valid, overwrite data, exception, dependency, keamanan dasar, dan cara rollback bila relevan."
    if task_type == "debugging":
        return "Risiko debugging yang harus dicek: jangan menebak tanpa error, bedakan gejala dan akar masalah, verifikasi setelah perbaikan."
    if task_type == "fact":
        return "Risiko fakta yang harus dicek: data jabatan, ranking, harga, dan berita bisa berubah; jangan pakai ingatan lama jika ada konteks web terbaru."
    if task_type == "math":
        return "Risiko hitungan yang harus dicek: operasi tidak valid, pembagian nol, satuan salah, rasio awal/akhir tertukar, dan syarat tidak konsisten."
    if task_type == "trick":
        return "Risiko jebakan yang harus dicek: jangan menerima premis salah, kata selalu/pasti/hanya sering membuat opsi keliru."
    return "Risiko umum yang harus dicek: jawaban terlalu umum, asumsi tidak disebut, dan contoh tidak relevan."


def _looks_math(text: str) -> bool:
    if re.search(r"\b\d+\s*[\+\-\*/=^]\s*\d+\b", text):
        return True
    return _has_any(
        text,
        ["persamaan", "hitung", "rasio", "perbandingan", "akar", "integral", "turunan", "persen", "logika"],
    )


def _is_concept_question(text: str) -> bool:
    return _has_any(text, ["apa ", "apa itu", "apa yang", "perbedaan", "mengapa", "kenapa", "jelaskan"])


def _is_coding_request(text: str) -> bool:
    if _has_any(text, ["buat", "tulis", "implementasikan", "perbaiki kode", "route", "script", "aplikasi"]):
        return _has_any(text, CODING_KEYWORDS)
    return _has_any(text, ["kode error", "coding", "program ini", "debug kode"])


def _has_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)
