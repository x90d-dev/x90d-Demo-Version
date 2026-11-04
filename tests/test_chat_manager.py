from modules.chat_manager import (
    DEFAULT_REASONING_LEVEL,
    chat_with_ai,
    detect_chat_intent,
    get_identity_response,
    should_use_chat_history,
    trim_chat_history,
)
from modules.chat_manager import build_chat_prompt


def test_detect_chat_intent_general():
    assert detect_chat_intent("Apa kabar? Beri ide aktivitas sore.") == "general"


def test_detect_chat_intent_tutor():
    assert detect_chat_intent("Selesaikan persamaan 2x + 3 = 11") == "tutor"


def test_detect_chat_intent_toefl():
    assert detect_chat_intent("TOEFL Structure: choose the correct verb.") == "english_toefl"


def test_detect_chat_intent_coding():
    assert detect_chat_intent("Tolong bantu debug error Flask di Python") == "coding"


def test_detect_chat_intent_python_app_builder():
    assert detect_chat_intent("Buat aplikasi kasir dengan Python dan SQLite") == "coding"


def test_detect_chat_intent_history_after_coding_topic():
    assert detect_chat_intent("Kapan Indonesia merdeka?") == "tutor"


def test_trim_chat_history_limits_to_six_turns():
    history = [{"user_message": str(index), "ai_response": "ok"} for index in range(10)]
    trimmed = trim_chat_history(history, max_turns=6)
    assert len(trimmed) == 6
    assert trimmed[0]["user_message"] == "4"
    assert trimmed[-1]["user_message"] == "9"


def test_should_use_chat_history_for_followup_reference():
    assert should_use_chat_history("penguin nya ada berapa?")
    assert should_use_chat_history("yang tadi jelaskan lebih singkat")
    assert should_use_chat_history("ada berapa?")


def test_should_not_use_chat_history_for_clear_new_topic():
    assert not should_use_chat_history("Kapan Indonesia merdeka?")
    assert not should_use_chat_history("Siapa presiden Indonesia saat ini?")


def test_build_chat_prompt_includes_history_for_followup():
    history = [
        {
            "user_message": "Jelaskan tentang penguin",
            "ai_response": "Penguin adalah burung laut yang tidak bisa terbang.",
        }
    ]
    prompt = build_chat_prompt("penguin nya ada berapa?", "general", history)
    assert "Riwayat singkat terakhir" in prompt
    assert "Jelaskan tentang penguin" in prompt
    assert "penguin nya ada berapa?" in prompt
    assert "gunakan riwayat singkat" in prompt.lower()


def test_build_chat_prompt_includes_smart_context():
    prompt = build_chat_prompt("Benda massa 2 kg diberi gaya 10 N selama 4 detik, kecepatan?", "tutor")
    assert "Konteks pemeriksaan" in prompt
    assert "F = m x a" in prompt


def test_build_chat_prompt_uses_relaxed_style_instruction():
    prompt = build_chat_prompt("jelaskan penguin dengan singkat", "general")
    lowered = prompt.lower()
    assert "santai" in lowered
    assert "tidak kaku" in lowered
    assert "jangan asal yakin" in lowered
    assert "jangan mulai jawaban dengan kalimat pembuka" in lowered
    assert "kalimat pertama harus berisi jawaban/inti" in lowered


def test_build_chat_prompt_includes_high_end_answering_rules():
    prompt = build_chat_prompt("jawab soal sulit dan menjebak", "tutor", reasoning_level="level_tinggi")
    lowered = prompt.lower()
    assert "model kelas atas" in lowered
    assert "pisahkan fakta/asumsi" in lowered
    assert "validasi semua syarat" in lowered


def test_default_reasoning_level_is_maximum():
    prompt = build_chat_prompt("jawab soal sulit dan menjebak", "tutor")
    lowered = prompt.lower()
    assert DEFAULT_REASONING_LEVEL == "super_sulit"
    assert "level reasoning: super sulit" in lowered
    assert "mode kecerdasan maksimum aktif" in lowered


def test_identity_response_for_creator_question():
    response = get_identity_response("siapa pembuat ai ini?")
    assert response == "CoreChiper adalah pembuatnya. Saya adalah CoreChiperAgent, agent yang dibuat untuk membantu pekerjaan Anda."


def test_identity_response_for_who_are_you_question():
    response = get_identity_response("siapa anda?")
    assert response == "Saya adalah CoreChiperAgent, agent yang dibuat untuk membantu pekerjaan Anda."


def test_chat_with_ai_identity_response_without_model_call(monkeypatch):
    def fail_generate(*_args, **_kwargs):
        raise AssertionError("Model tidak perlu dipanggil untuk pertanyaan identitas.")

    monkeypatch.setattr("modules.chat_manager.generate_ai_response", fail_generate)
    result = chat_with_ai("siapa developer kamu?", "general")

    assert result["response"].startswith("CoreChiper adalah Founder sekaligus Developer")


def test_build_chat_prompt_includes_extra_web_context():
    prompt = build_chat_prompt(
        "Top 10 universitas China terbaru",
        "general",
        extra_context="Konteks web search terbaru.\n1. Source\nLink: https://example.com",
    )
    assert "WEB SEARCH AKTIF" in prompt
    assert "Sumber:" in prompt
    assert "https://example.com" in prompt


def test_build_chat_prompt_handles_failed_web_context_as_fallback():
    prompt = build_chat_prompt(
        "Siapa menteri keuangan Indonesia saat ini?",
        "general",
        extra_context="WEB SEARCH DIMINTA TAPI GAGAL.\nError: timeout",
    )
    assert "KONTEKS WEB SEARCH GAGAL" in prompt
    assert "WEB SEARCH AKTIF - SUMBER HARUS DIPRIORITASKAN" not in prompt


def test_build_chat_prompt_answers_stable_ml_concept_even_if_web_fails():
    prompt = build_chat_prompt(
        "Apa yang dimaksud dengan feature dalam machine learning? Berikan contoh feature dalam kasus prediksi harga rumah.",
        "general",
        extra_context="WEB SEARCH DIMINTA TAPI GAGAL.\nError: tidak ada hasil",
    )
    lowered = prompt.lower()

    assert "feature adalah variabel/input/atribut" in lowered
    assert "tetap jawab langsung dari pengetahuan umum" in lowered
    assert "jangan menjawab \"saya tidak bisa menemukan hasil\"" in lowered
    assert "harga rumah" in lowered


def test_build_chat_prompt_includes_developer_mode_context():
    prompt = build_chat_prompt("Buat aplikasi Python kasir dengan SQLite", "coding")
    assert "Developer Mode: AKTIF" in prompt
    assert "Struktur folder" in prompt
    assert "Cara test" in prompt


def test_build_chat_prompt_includes_expert_coding_rules():
    prompt = build_chat_prompt("Buat aplikasi Python advanced yang lengkap dan panjang", "coding")
    lowered = prompt.lower()

    assert "asisten developer expert" in lowered
    assert "jangan berhenti di beberapa baris" in lowered
    assert "kode per file yang cukup lengkap" in lowered
    assert "jangan menulis \"kode lainnya sama\"" in lowered


def test_build_chat_prompt_includes_thinking_mode_context():
    prompt = build_chat_prompt("Apa yang dimaksud feature dalam machine learning?", "thinking")
    lowered = prompt.lower()

    assert "mode aktif: thinking mode" in lowered
    assert "thinking mode: aktif" in lowered
    assert "self-check internal" in lowered
    assert "jenis tugas terdeteksi: konsep" in lowered


def test_build_chat_prompt_includes_agent_profile_context():
    prompt = build_chat_prompt(
        "Buatkan aplikasi Python untuk mencatat tugas",
        "coding",
        agent_profile="agent",
    )
    lowered = prompt.lower()

    assert "cara kerja aktif: agent" in lowered
    assert "personal work agent" in lowered
    assert "tujuan, rencana singkat, eksekusi, validasi" in lowered


def test_build_chat_prompt_includes_image_and_pdf_rules():
    prompt = build_chat_prompt(
        "Ringkas isi file ini",
        "task",
        extra_context="Konteks PDF digital:\nNama file: modul.pdf",
        agent_profile="agent",
        has_images=True,
    )
    lowered = prompt.lower()

    assert "pdf aktif" in lowered
    assert "gambar aktif" in lowered
    assert "jika ada gambar" in lowered
    assert "jika ada pdf" in lowered
