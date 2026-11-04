from pathlib import Path


def test_chat_loading_text_is_simple_thinking_label():
    script = Path("static/script.js").read_text(encoding="utf-8")

    assert "Berpikir" in script
    assert "AI sedang memeriksa semua syarat" not in script
    assert "Memeriksa..." not in script


def test_chat_welcome_copy_matches_requested_clean_ui():
    template = Path("templates/chat.html").read_text(encoding="utf-8")
    script = Path("static/script.js").read_text(encoding="utf-8")
    base = Path("templates/base.html").read_text(encoding="utf-8")

    assert "Lets Start" in template
    assert "Bisa Mulai Dengan" in template
    assert "Cara kerja" in template
    assert "composerPlus" in template
    assert "composerMenu" in template
    assert "agent_profile" in template
    assert "Riwayat chat" in template
    assert "sidebar-open-button" in template
    assert "Buka sidebar" in template
    assert "data-user-name" in template
    assert "display_name" in template
    assert "Login Admin" not in Path("templates/login.html").read_text(encoding="utf-8")
    assert "Password default" not in Path("templates/login.html").read_text(encoding="utf-8")
    assert "Level soal" not in template
    assert "Aksi cepat" not in template
    assert "Matematika advanced</button>" not in template
    assert "Fisika teliti</button>" not in template
    assert "Jadwal belajar</button>" not in template
    assert "Buat app Python</button>" not in template
    assert "CoreChiperAgent siap bekerja" not in template
    assert "Dapatkan layanan bantuan berupa jawaban instan" not in template
    assert "PDF teks digital dan file teks didukung. Scan/OCR belum." not in template
    assert "PDF teks digital dan file teks didukung. Scan/OCR belum." not in script
    assert "Aktifkan saat butuh data terbaru, ranking, harga, atau berita." not in template
    assert "url_for('home')" not in base
    assert "url_for('practice')" not in base
    assert "url_for('history')" not in base
    assert "url_for('report')" not in base


def test_sidebar_can_be_collapsed_from_chat_ui():
    template = Path("templates/chat.html").read_text(encoding="utf-8")
    script = Path("static/script.js").read_text(encoding="utf-8")
    css = Path("static/style.css").read_text(encoding="utf-8")

    assert "sidebarClose" in template
    assert "sidebarOpen" in template
    assert "sidebar-collapsed" in script
    assert "body.sidebar-collapsed.chat-page .chat-sidebar" in css
    assert ".sidebar-open-button img" in css


def test_chat_skin_uses_refined_professional_override():
    css = Path("static/style.css").read_text(encoding="utf-8")
    refined = css.split("/* Refined professional chat skin */", 1)[1]

    assert "/* Refined professional chat skin */" in css
    assert "#7da2c8" in refined
    assert "#2de7df" not in refined
    assert "#35fff2" not in refined
    assert "#7a4aff" not in refined
    assert "box-shadow: none" in refined
