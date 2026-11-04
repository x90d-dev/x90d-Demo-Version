import re


AGENT_PROFILES = {
    "normal": "Normal",
    "agent": "Agent",
}

AGENT_ACTION_KEYWORDS = [
    "buatkan",
    "kerjakan",
    "susun",
    "rancang",
    "analisis",
    "debug",
    "perbaiki",
    "ringkas",
    "buat aplikasi",
    "buat kode",
    "buat jadwal",
    "cek",
    "evaluasi",
    "ubah",
    "bantu saya",
]


def resolve_agent_profile(value: str | None) -> str:
    selected = (value or "normal").strip().lower()
    return selected if selected in AGENT_PROFILES else "normal"


def should_use_agent_flow(message: str, profile: str) -> bool:
    if resolve_agent_profile(profile) == "agent":
        return True
    text = (message or "").lower()
    return any(keyword in text for keyword in AGENT_ACTION_KEYWORDS)


def build_agent_context(
    message: str,
    profile: str = "normal",
    has_pdf: bool = False,
    has_images: bool = False,
) -> str:
    resolved = resolve_agent_profile(profile)
    if resolved == "normal":
        return (
            "Cara kerja: Normal.\n"
            "- Jawab langsung dan natural.\n"
            "- Tetap teliti, tetapi jangan membuat rencana panjang jika pertanyaannya sederhana.\n"
            "- Jika Admin memberi perintah kerja yang jelas, boleh beri langkah praktis singkat."
        )

    task_hint = _detect_agent_task(message)
    attachment_hint = _attachment_hint(has_pdf=has_pdf, has_images=has_images)
    return (
        "Cara kerja: Agent.\n"
        "Peran: CoreChiperAgent bertindak sebagai personal work agent lokal milik Admin.\n"
        f"Jenis pekerjaan terdeteksi: {task_hint}.\n"
        "Aturan Agent:\n"
        "- Pahami perintah Admin sebagai pekerjaan yang harus dibantu sampai bisa dipakai.\n"
        "- Jika tugas besar, pecah menjadi tujuan, rencana singkat, eksekusi, validasi, dan langkah berikutnya.\n"
        "- Jika tugas sederhana, jawab langsung tanpa rencana panjang.\n"
        "- Jangan hanya memberi teori; berikan output yang bisa dipakai Admin.\n"
        "- Untuk coding, buat solusi runnable, struktur file jika perlu, cara menjalankan, cara test, dan edge case.\n"
        "- Untuk debugging, jelaskan penyebab, langkah cek, perbaikan, dan verifikasi.\n"
        "- Untuk dokumen/PDF/gambar, jawab berdasarkan isi file. Jika ada bagian tidak terbaca, katakan jelas.\n"
        "- Jika data kurang atau perintah ambigu, sebutkan asumsi atau tanya klarifikasi singkat.\n"
        "- Lakukan self-check sebelum final: apakah hasil menjawab perintah, bisa dijalankan, dan tidak mengarang.\n"
        f"{attachment_hint}"
    )


def _detect_agent_task(message: str) -> str:
    text = (message or "").lower()
    if _has_any(text, ["debug", "error", "traceback", "bug", "tidak jalan", "gagal jalan"]):
        return "debugging"
    if _has_any(text, ["python", "flask", "sqlite", "javascript", "html", "css", "api", "aplikasi", "kode"]):
        return "coding/project"
    if _has_any(text, ["pdf", "dokumen", "file", "ringkas", "rangkuman"]):
        return "dokumen/ringkasan"
    if _has_any(text, ["jadwal", "rencana", "planning", "to-do", "checklist"]):
        return "perencanaan"
    if _has_any(text, ["soal", "matematika", "fisika", "kimia", "toefl", "grammar"]):
        return "tutor/tugas belajar"
    if re.search(r"\b(analisis|evaluasi|bandingkan|cek)\b", text):
        return "analisis/evaluasi"
    return "pekerjaan umum"


def _attachment_hint(has_pdf: bool, has_images: bool) -> str:
    hints = []
    if has_pdf:
        hints.append("- PDF aktif: gunakan konteks PDF sebagai sumber utama dan sebutkan halaman jika tersedia.")
    if has_images:
        hints.append("- Gambar aktif: baca teks/objek/angka pada gambar dengan hati-hati; jangan menebak bagian buram.")
    return "\n".join(hints)


def _has_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)
