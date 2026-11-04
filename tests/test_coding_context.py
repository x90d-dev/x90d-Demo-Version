from modules.coding_context import build_coding_context, detect_coding_complexity


def test_detect_coding_complexity_project_for_python_app():
    assert detect_coding_complexity("Buat aplikasi Python kasir dengan SQLite") == "project"


def test_file_automation_context_requires_dry_run_and_undo():
    context = build_coding_context("Buat aplikasi menggunakan Python untuk rename file otomatis")
    assert "Jangan memberi kode toy" in context
    assert "--dry-run" in context
    assert "--undo" in context
    assert "pytest" in context
    assert "__name__" in context


def test_advanced_coding_context_requires_full_project_quality():
    context = build_coding_context("Buat aplikasi Python advanced yang lengkap dan panjang")
    lowered = context.lower()

    assert "jangan berhenti di beberapa baris" in lowered
    assert "kode per file lengkap" in lowered
    assert "arsitektur" in lowered
    assert "edge case" in lowered
    assert "keamanan" in lowered
