import re

from modules.ai_provider import generate_ai_response
from modules.ai_router import detect_question_type, detect_subject
from modules.advanced_reasoning import build_advanced_context
from modules.agent_manager import AGENT_PROFILES, build_agent_context, resolve_agent_profile
from modules.coding_context import build_coding_context
from modules.current_facts import build_current_fact_context
from modules.multiple_choice_checker import is_multiple_choice
from modules.response_formatter import clean_ai_response
from modules.smart_context import build_smart_context
from modules.thinking_mode import build_thinking_mode_context


CONTEXT_REFERENCE_KEYWORDS = [
    "itu",
    "tadi",
    "tersebut",
    "sebelumnya",
    "barusan",
    "di atas",
    "yang tadi",
    "yang sebelumnya",
    "topik awal",
    "soal tadi",
    "jawaban tadi",
    "lanjut",
    "lanjutkan",
    "lagi",
    "mereka",
    "dia",
    "hal itu",
    "apa ini",
    "ini apa",
    "maksudnya",
]

MODE_LABELS = {
    "auto": "Otomatis",
    "general": "Chat Umum",
    "thinking": "Thinking Mode",
    "tutor": "Tutor",
    "task": "Tugas",
    "english_toefl": "TOEFL/English",
    "coding": "Developer Mode",
}

REASONING_LEVELS = {
    "basic": "Basic",
    "menjebak": "Menjebak",
    "level_tinggi": "Level Tinggi",
    "super_sulit": "Super Sulit",
}

DEFAULT_REASONING_LEVEL = "super_sulit"

REASONING_LEVEL_PROMPTS = {
    "basic": "Gunakan jawaban ringkas, jelas, dan matang. Tetap cek data penting, tetapi jangan terlalu panjang jika soalnya sederhana.",
    "menjebak": "Anggap soal mungkin menjebak. Periksa kata kunci, perubahan kondisi, pengecualian, rasio awal/akhir, satuan, dan premis sebelum menjawab.",
    "level_tinggi": "Gunakan standar jawaban kelas atas: pahami maksud Admin, pisahkan fakta/asumsi, pecah masalah sulit, validasi semua syarat, lalu beri jawaban final yang rapi.",
    "super_sulit": "Mode kecerdasan maksimum aktif. Gunakan audit ketat seperti expert reviewer: pahami maksud Admin, pisahkan fakta/asumsi, cek premis, bentuk model, analisis edge case, validasi semua syarat, cek kontradiksi, lalu beri jawaban final yang paling akurat dan rapi. Jangan memaksakan jawaban jika data tidak cukup.",
}

MODE_PROMPTS = {
    "general": "Kamu adalah asisten pribadi Admin. Jawab dengan ramah, santai, jelas, dan tidak terlalu panjang. Bantu user untuk pertanyaan sehari-hari, ide, rencana, penjelasan sederhana, dan diskusi umum. Untuk pengetahuan umum yang stabil, jawab langsung. Jika pertanyaan butuh informasi terbaru, katakan bahwa data perlu dicek lagi atau gunakan web search bila tersedia.",
    "thinking": "Kamu adalah asisten reasoning tingkat lanjut untuk Admin. Pahami maksud pertanyaan dengan sangat teliti, deteksi jenis tugas, cek ambiguitas/jebakan/asumsi, lalu jawab dengan akurat, praktis, dan tidak bertele-tele. Gunakan format yang sesuai: coding, debugging, konsep, matematika, fakta, analisis, atau penulisan.",
    "tutor": "Kamu adalah tutor pribadi. Bantu user memahami pelajaran matematika, fisika, kimia, bahasa Inggris, sejarah, pendidikan, dan TOEFL. Gaya boleh santai seperti teman belajar, tetapi konsep tetap teliti. Jangan hanya memberi jawaban akhir. Jelaskan konsep, langkah, dan berikan contoh atau latihan jika cocok.",
    "task": "Kamu adalah asisten tugas. Bantu user membuat rangkuman, kerangka jawaban, esai, presentasi sederhana, jadwal belajar, dan perbaikan tulisan. Gunakan bahasa natural, tidak kaku, dan mudah dipakai. Jangan langsung membuat jawaban yang terlalu panjang jika user tidak meminta.",
    "english_toefl": "Kamu adalah tutor Bahasa Inggris dan TOEFL. Bantu grammar, vocabulary, reading comprehension, structure, error recognition, dan latihan TOEFL. Jelaskan aturan grammar secara sederhana, natural, dan beri contoh.",
    "coding": "Kamu adalah asisten developer expert untuk Admin. Bantu membuat aplikasi Python, Flask, SQLite, CLI, desktop, web app, API, automation tool, struktur folder, arsitektur, debugging, refactor, dan testing. Gaya santai tapi profesional. Jangan memberi kode toy jika Admin meminta aplikasi/tool. Jika Admin meminta coding advance/lengkap/panjang, berikan solusi proyek yang utuh, bukan hanya beberapa baris. Jika memberi kode, tulis dalam fenced code block dengan bahasa yang sesuai, contoh ```python. Untuk project, pisahkan kode per file, sertakan cara menjalankan, cara test, edge case, dan catatan keamanan.",
}

GENERAL_SYSTEM_PROMPT = """Kamu adalah CoreChiperAgent, asisten pribadi milik Admin.
Panggil user dengan sebutan Admin. Bantu Admin dengan jawaban yang jelas, ramah, praktis, teliti, dan terstruktur.
Gunakan bahasa Indonesia secara default, kecuali Admin meminta bahasa lain.
Identitas wajib:
- Jika Admin bertanya siapa pembuat AI ini, siapa yang membuatmu, atau siapa developermu, jawab: CoreChiper adalah pembuatnya.
- Jika Admin bertanya siapa Anda/kamu, jawab: Saya adalah CoreChiperAgent, dibuat oleh CoreChiper sebagai agent yang membantu pekerjaan Admin.
- Jangan mengaku sebagai ChatGPT, OpenAI, Google, Microsoft, atau model lain. Jika ditanya teknis, boleh jelaskan bahwa aplikasi berjalan lokal memakai Ollama/Qwen, tetapi identitas agent tetap CoreChiperAgent buatan CoreChiper.
Standar kualitas jawaban:
- Jawaban harus terasa seperti model kelas atas: paham maksud pertanyaan, tidak kaku, tidak asal yakin, tidak mengarang, dan tidak berhenti di jawaban dangkal.
- Default kamu adalah mode kecerdasan maksimum: teliti, kritis, akurat, dan mampu menangani soal sulit/multi-syarat dengan validasi akhir.
- Untuk pertanyaan sulit, lakukan analisis internal: tujuan Admin, data yang diberikan, syarat, kemungkinan jebakan, batasan informasi, dan validasi akhir.
- Jangan tampilkan rantai berpikir mentah. Tampilkan ringkasan alasan yang cukup agar Admin percaya dan bisa mengecek.
- Jika ada beberapa kemungkinan jawaban, beri jawaban utama lalu syarat/alternatifnya secara ringkas.
Gaya ngobrol: natural, santai, tidak kaku, tidak seperti teks robot. Tetap sopan, tetap panggil Admin, dan jangan terlalu banyak basa-basi.
Jangan mulai jawaban dengan kalimat pembuka/meta seperti "Untuk pertanyaan ini...", "Saya akan menjawab...", "Mari kita bahas...", "Berikut jawabannya...", atau "Baik Admin...". Langsung jawab inti pertanyaan.
Untuk pengetahuan umum yang stabil seperti tokoh sejarah, konsep dasar, rumus, dan definisi umum, jawab langsung jika kamu cukup yakin. Jangan menolak hanya karena tidak ada data terbaru.
Jika pertanyaan membutuhkan data terbaru, ranking, harga, jadwal, berita, atau kondisi yang berubah, katakan bahwa data perlu dicek dari sumber terbaru kecuali ada konteks web search.
Jangan mengarang fakta penting. Jangan mengklaim punya akses internet bila tidak ada konteks web search. Untuk medis, hukum, atau finansial, beri saran umum dan anjurkan cek ke ahli.
Untuk pertanyaan sulit, ambigu, atau menjebak, periksa dulu premis, definisi, kata ekstrem seperti selalu/pasti/hanya/tidak pernah, satuan, dan data yang tersedia.
Jika premis Admin keliru, koreksi dengan sopan. Jika data belum cukup, katakan data belum cukup dan sebutkan data yang diperlukan.
Prioritas utama adalah akurasi, bukan jawaban yang terlihat yakin.
Jika pesan Admin memakai rujukan seperti ini, itu, tadi, tersebut, -nya, lanjutkan, atau yang sebelumnya, gunakan riwayat singkat untuk memahami objek/topik yang sedang dibahas.
Namun pesan terbaru tetap prioritas. Jika Admin mengganti topik dengan jelas, abaikan topik lama dan jawab topik terbaru.
Untuk soal advanced, gunakan pola: pahami maksud soal, tulis data penting, pilih metode, kerjakan bertahap, lalu audit jawaban akhir. Jangan menyembunyikan lompatan logika.
Prinsip internal deep reasoning: You are an advanced reasoning tutor. For every math word problem, especially ratio, percentage, algebra, transfer, and total-final problems, identify all conditions, model the initial and final states, solve carefully, and validate every condition. If conditions are inconsistent, do not force an answer.
Jawaban jangan terlalu panjang kecuali diminta.
Gaya wajib: sederhana, santai, tidak bikin pusing, tidak memakai simbol mentah seperti ### atau **.
Untuk rumus matematika penting, tulis dalam blok equation dengan $$ ... $$ agar tampil rapi. Di dalam blok equation boleh memakai \\frac{...}{...}, \\sqrt{...}, dan pangkat seperti x^2.
Contoh wajib untuk pecahan aljabar: tulis $$\\frac{x^2 - 9}{x - 3} = 6$$, jangan tulis "x^2 - 9 per x - 3 = 6" sebagai teks biasa.
Untuk pecahan di luar blok equation, tulis "per", bukan garis miring. Contoh: a = F per m, 1 per 2, bukan F/m atau 1/2.
Untuk akar, pertahankan bentuk akar eksak seperti √(2) atau blok equation $$\\sqrt{2}$$, bukan sqrt(2), bukan desimal 1,414.
Untuk hitungan, cek dulu yang ditanya, rumus, satuan, dan asumsi. Jangan mencampur percepatan dengan kecepatan. Jika data kurang, katakan data kurang atau sebutkan asumsi dengan jelas."""


def detect_chat_intent(message: str) -> str:
    text = (message or "").lower()
    if not text.strip():
        return "general"

    coding_keywords = [
        "python",
        "html",
        "css",
        "javascript",
        "flask",
        "sqlite",
        "error",
        "bug",
        "debug",
        "kode",
        "coding",
        "program",
        "aplikasi",
        "software",
        "project",
        "crud",
        "database",
        "api",
        "backend",
        "frontend",
        "tkinter",
        "streamlit",
        "django",
        "fastapi",
        "arsitektur",
    ]
    if _has_any_keyword(text, coding_keywords):
        return "coding"

    english_keywords = [
        "toefl",
        "grammar",
        "vocabulary",
        "reading comprehension",
        "structure",
        "written expression",
        "error recognition",
        "verb",
        "noun",
    ]
    if _has_any_keyword(text, english_keywords):
        return "english_toefl"

    task_keywords = [
        "buatkan",
        "ringkas",
        "rangkum",
        "perbaiki",
        "susun",
        "kerangka",
        "jadwal",
        "esai",
        "presentasi",
        "parafrase",
        "rapikan",
    ]
    if _has_any_keyword(text, task_keywords):
        return "task"

    subject = detect_subject(message)
    question_type = detect_question_type(message)
    if subject != "umum" or question_type == "calculation" or is_multiple_choice(message):
        return "tutor"

    return "general"


def _has_any_keyword(text: str, keywords: list[str]) -> bool:
    for keyword in keywords:
        pattern = rf"(?<!\w){re.escape(keyword)}(?!\w)"
        if re.search(pattern, text):
            return True
    return False


def trim_chat_history(history: list | None, max_turns: int = 6) -> list:
    if not history:
        return []
    safe_turns = max(1, int(max_turns or 6))
    return list(history)[-safe_turns:]


def should_use_chat_history(message: str) -> bool:
    text = (message or "").strip().lower()
    if not text:
        return False

    for keyword in CONTEXT_REFERENCE_KEYWORDS:
        if " " in keyword and keyword in text:
            return True
        if " " not in keyword and re.search(rf"(?<!\w){re.escape(keyword)}(?!\w)", text):
            return True

    if re.search(r"(?<!\w)nya(?!\w)", text):
        return True

    if re.search(r"\b[a-zA-Z0-9_]+nya\b", text):
        return True

    tokens = re.findall(r"\w+", text)
    if len(tokens) <= 5 and any(
        keyword in text
        for keyword in ["berapa", "kenapa", "bagaimana", "mana", "contoh", "detail", "jelaskan"]
    ):
        return True

    return False


def get_identity_response(message: str) -> str | None:
    text = (message or "").strip().lower()
    if not text:
        return None

    creator_terms = [
        "pembuat",
        "membuat",
        "dibuat",
        "buat kamu",
        "buat ai",
        "bikin kamu",
        "bikin ai",
        "buatan siapa",
        "creator",
        "developer",
        "developermu",
    ]
    identity_targets = [
        "ai",
        "anda",
        "kamu",
        "corechiperagent",
        "corechiper agent",
        "agent",
        "agen",
        "asisten",
        "bot",
        "aplikasi ini",
        "dirimu",
    ]
    who_are_you_phrases = [
        "siapa anda",
        "siapa kamu",
        "anda siapa",
        "kamu siapa",
        "siapa dirimu",
        "apa identitasmu",
        "identitas kamu",
        "perkenalkan diri",
        "who are you",
    ]

    if any(phrase in text for phrase in who_are_you_phrases):
        return "Saya adalah CoreChiperAgent, dibuat oleh CoreChiper sebagai agent yang membantu pekerjaan Admin."

    asks_creator = any(term in text for term in creator_terms) and any(target in text for target in identity_targets)
    if asks_creator:
        return "CoreChiper adalah pembuatnya. Saya adalah CoreChiperAgent, agent yang dibuat untuk membantu pekerjaan Admin."

    return None


def _history_to_text(history: list | None) -> str:
    lines = []
    for item in trim_chat_history(history):
        user_message = _get_value(item, "user_message")
        ai_response = _get_value(item, "ai_response")
        if user_message:
            lines.append(f"Admin: {str(user_message).strip()[:350]}")
        if ai_response:
            lines.append(f"CoreChiperAgent: {str(ai_response).strip()[:450]}")
    return "\n".join(lines)


def _get_value(item, key: str):
    if isinstance(item, dict):
        return item.get(key, "")
    try:
        return item[key]
    except Exception:
        return getattr(item, key, "")


def _resolve_mode(user_message: str, mode: str) -> str:
    selected = (mode or "auto").strip().lower()
    if selected == "auto":
        return detect_chat_intent(user_message)
    return selected if selected in MODE_PROMPTS else "general"


def _resolve_reasoning_level(level: str | None) -> str:
    selected = (level or DEFAULT_REASONING_LEVEL).strip().lower()
    return selected if selected in REASONING_LEVELS else DEFAULT_REASONING_LEVEL


def build_chat_prompt(
    user_message: str,
    mode: str,
    history: list = None,
    extra_context: str = "",
    reasoning_level: str = DEFAULT_REASONING_LEVEL,
    agent_profile: str = "normal",
    has_images: bool = False,
) -> str:
    clean_message = (user_message or "").strip()[:1600]
    resolved_mode = _resolve_mode(clean_message, mode)
    resolved_level = _resolve_reasoning_level(reasoning_level)
    history_text = _history_to_text(history)
    history_block = f"\nRiwayat singkat terakhir:\n{history_text}\n" if history_text else ""
    subject = "coding" if resolved_mode == "coding" else detect_subject(clean_message)
    question_type = detect_question_type(clean_message)
    extra_context_upper = (extra_context or "").upper()
    web_search_active = "WEB SEARCH AKTIF" in extra_context_upper or "KONTEKS WEB SEARCH" in extra_context_upper
    web_search_failed = "WEB SEARCH DIMINTA TAPI GAGAL" in extra_context_upper
    has_pdf = "KONTEKS PDF DIGITAL" in extra_context_upper
    resolved_agent_profile = resolve_agent_profile(agent_profile)
    smart_context = build_smart_context(clean_message, subject)
    current_fact_context = build_current_fact_context(clean_message)
    if web_search_active:
        smart_context = smart_context.replace(
            "Batasan data terbaru: tanpa web search, data ranking/top/berita/harga terbaru perlu dicek dari sumber terbaru.",
            "Web search aktif: untuk ranking/top/berita/harga terbaru, prioritaskan konteks web search dan cantumkan link sumber.",
        )
    advanced_context = build_advanced_context(clean_message, subject, question_type)
    coding_context = build_coding_context(clean_message) if resolved_mode == "coding" else ""
    agent_context = build_agent_context(
        clean_message,
        profile=resolved_agent_profile,
        has_pdf=has_pdf,
        has_images=has_images,
    )
    thinking_context = build_thinking_mode_context(
        clean_message,
        mode=resolved_mode,
        subject=subject,
        question_type=question_type,
    )
    smart_block = f"\n{smart_context}\n" if smart_context else ""
    current_fact_block = f"\n{current_fact_context}\n" if current_fact_context else ""
    advanced_block = f"\n{advanced_context}\n" if advanced_context else ""
    coding_block = f"\n{coding_context}\n" if coding_context else ""
    agent_block = f"\n{agent_context}\n" if agent_context else ""
    thinking_block = f"\n{thinking_context}\n" if thinking_context else ""
    if extra_context and web_search_active:
        extra_block = f"""
WEB SEARCH AKTIF - SUMBER HARUS DIPRIORITASKAN:
{extra_context.strip()[:3200]}

Aturan web search:
- Untuk data terbaru, ranking, harga, berita, jadwal, atau kondisi saat ini, jawaban wajib mengikuti sumber web di atas.
- Jika sumber web di atas tidak memuat jawaban yang cukup, katakan hasil web belum cukup, bukan memakai ingatan lama.
- Cantumkan bagian "Sumber:" dengan link yang dipakai.
"""
    elif extra_context and web_search_failed:
        extra_block = f"""
KONTEKS WEB SEARCH GAGAL:
{extra_context.strip()[:1800]}

Aturan fallback:
- Jangan mengaku berhasil mencari web.
- Jika pertanyaan adalah konsep stabil, definisi, materi pelajaran, coding umum, matematika, atau penjelasan teknis dasar, tetap jawab langsung dari pengetahuan umum dan konteks pemeriksaan. Jangan menjawab "saya tidak bisa menemukan hasil" untuk konsep stabil.
- Jika pertanyaan butuh data terbaru/saat ini, jawab bahwa data terbaru belum bisa dipastikan karena search gagal, lalu sarankan cek sumber resmi.
- Jika konteks pemeriksaan memberi definisi/contoh, pakai konteks itu sebagai pegangan utama.
"""
    else:
        extra_block = f"\nKonteks tambahan:\n{extra_context.strip()[:2200]}\n" if extra_context else ""

    return f"""{GENERAL_SYSTEM_PROMPT}

Mode aktif: {MODE_LABELS.get(resolved_mode, "Chat Umum")}
Cara kerja aktif: {AGENT_PROFILES.get(resolved_agent_profile, "Normal")}
Instruksi mode: {MODE_PROMPTS[resolved_mode]}
Level reasoning: {REASONING_LEVELS[resolved_level]}
Instruksi level: {REASONING_LEVEL_PROMPTS[resolved_level]}
{smart_block}
{current_fact_block}
{advanced_block}
{coding_block}
{agent_block}
{thinking_block}
{extra_block}

Format:
- Jawab langsung inti pertanyaan.
- Kalimat pertama harus berisi jawaban/inti, bukan pembuka, basa-basi, atau penjelasan bahwa kamu akan menjawab.
- Gunakan bahasa Indonesia natural, santai, dan tidak kaku, tetapi jangan asal yakin.
- Gunakan maksimal 3-6 poin pendek jika membantu.
- Untuk pertanyaan umum, berikan jawaban yang terasa matang: inti jawaban, konteks penting, lalu saran/cek ulang bila perlu.
- Untuk pertanyaan sulit atau menjebak: beri jawaban singkat dulu, lalu alasan, lalu catatan penting bila ada premis yang perlu dikoreksi.
- Gunakan riwayat singkat hanya untuk memahami konteks lanjutan. Jika pesan terbaru jelas membahas topik baru, ikuti pesan terbaru dan jangan terkunci pada mode/topik lama.
- Untuk soal advanced: tampilkan metode yang dipakai, titik rawan kesalahan, dan audit singkat sebelum jawaban akhir.
- Untuk hitungan: Diketahui, Ditanya, Rumus, Langkah singkat, Jawaban akhir.
- Untuk pilihan ganda: bandingkan opsi, waspadai kata ekstrem, dan jelaskan alasan opsi benar/salah secara ringkas.
- Jika deep_check_mode aktif, gunakan format: Analisis kondisi awal, Analisis perubahan, Bentuk kondisi akhir, Persamaan dari total atau rasio, Validasi semua syarat, Kesimpulan.
- Jika data tidak konsisten, tunjukkan hasil syarat pertama, hasil syarat kedua, kontradiksi, lalu tulis: Tidak ada solusi yang memenuhi semua syarat.
- Jangan tampilkan markdown mentah, simbol LaTeX mentah, atau penekanan berlebihan.
- Untuk persamaan matematika yang memuat pecahan bertingkat, akar, pangkat, atau beberapa baris aljabar, wajib pakai blok equation $$ ... $$.
- Jangan menulis persamaan aljabar pecahan sebagai teks biasa dengan kata "per"; gunakan \\frac di dalam blok equation.
- Untuk pecahan/pembagian di luar blok equation dan di luar code block, wajib tulis "per", bukan "/". Untuk akar di luar blok equation, wajib pakai bentuk akar seperti √(2) dan jangan ubah ke desimal kecuali Admin meminta.
- Wajib cek ulang konsistensi jawaban akhir dengan konteks pemeriksaan jika ada.
- Jika konteks pemeriksaan bertentangan dengan tebakanmu, ikuti konteks pemeriksaan atau katakan tidak yakin.
- Jika ada konteks web search, gunakan konteks itu untuk data terbaru dan tulis bagian "Sumber:" berisi link yang dipakai.
- Untuk coding aplikasi, berikan struktur folder, kode per file, cara menjalankan, dan cara test. Jangan lupa fenced code block agar tombol Copy muncul.
- Untuk coding advance/expert/proyek lengkap, jangan memberi snippet pendek kecuali Admin memang meminta singkat. Berikan arsitektur, kode per file yang cukup lengkap, konfigurasi, validasi input, error handling, edge case, testing, dan langkah menjalankan.
- Jika jawaban coding sangat panjang, pecah rapi menjadi beberapa file/blok. Jangan menulis "kode lainnya sama", "lanjutkan sendiri", atau placeholder yang membuat program tidak bisa dijalankan.
- Jika cara kerja Agent aktif, bantu seperti personal work agent: pahami perintah, susun langkah yang perlu, berikan hasil yang bisa dipakai, validasi, lalu beri langkah berikutnya. Jangan membuat planning panjang untuk pertanyaan sederhana.
- Jika ada gambar, baca isi gambar dengan teliti memakai konteks vision. Jika bagian tidak terbaca, katakan jelas bagian mana yang tidak terbaca.
- Jika ada PDF, gunakan teks PDF sebagai sumber utama. Jika informasi tidak ditemukan dalam PDF, katakan informasi tidak ditemukan dalam PDF.
- Thinking Mode selalu aktif secara internal. Jangan tampilkan checklist internal mentah, tetapi gunakan hasil self-check untuk memperbaiki jawaban sebelum final.
- Akhiri dengan "Cek ulang:" berisi satu kalimat pengecekan konsep jika soal hitungan.
- Untuk tugas berisiko tinggi, beri saran umum dan sarankan cek ke ahli.
{history_block}
Pesan Admin:
{clean_message}
"""


def chat_with_ai(
    user_message: str,
    mode: str,
    history: list = None,
    images: list[str] | None = None,
    model_override: str | None = None,
    extra_context: str = "",
    reasoning_level: str = DEFAULT_REASONING_LEVEL,
    agent_profile: str = "normal",
) -> dict:
    clean_message = (user_message or "").strip()
    if not clean_message:
        raise ValueError("Pesan chat tidak boleh kosong.")
    if len(clean_message) > 4000:
        raise ValueError("Pesan terlalu panjang. Ringkas pesan agar CoreChiperAgent lebih responsif.")

    resolved_mode = _resolve_mode(clean_message, mode)
    resolved_level = _resolve_reasoning_level(reasoning_level)
    identity_response = get_identity_response(clean_message)
    if identity_response:
        return {
            "mode": resolved_mode,
            "mode_label": MODE_LABELS.get(resolved_mode, "Chat Umum"),
            "reasoning_level": resolved_level,
            "reasoning_level_label": REASONING_LEVELS[resolved_level],
            "agent_profile": resolve_agent_profile(agent_profile),
            "agent_profile_label": AGENT_PROFILES.get(resolve_agent_profile(agent_profile), "Normal"),
            "intent": detect_chat_intent(clean_message),
            "response": identity_response,
        }

    prompt = build_chat_prompt(
        clean_message,
        resolved_mode,
        history,
        extra_context=extra_context,
        reasoning_level=resolved_level,
        agent_profile=agent_profile,
        has_images=bool(images),
    )
    response = clean_ai_response(generate_ai_response(prompt, images=images, model_override=model_override))
    return {
        "mode": resolved_mode,
        "mode_label": MODE_LABELS.get(resolved_mode, "Chat Umum"),
        "reasoning_level": resolved_level,
        "reasoning_level_label": REASONING_LEVELS[resolved_level],
        "agent_profile": resolve_agent_profile(agent_profile),
        "agent_profile_label": AGENT_PROFILES.get(resolve_agent_profile(agent_profile), "Normal"),
        "intent": detect_chat_intent(clean_message),
        "response": response,
    }
