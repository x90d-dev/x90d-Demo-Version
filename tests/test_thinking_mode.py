from modules.thinking_mode import build_self_check_context, build_thinking_mode_context, detect_task_type


def test_detect_task_type_debugging_from_error_message():
    assert detect_task_type("TypeError: unsupported operand type(s) for +") == "debugging"


def test_detect_task_type_coding_from_app_request():
    assert detect_task_type("Buat aplikasi Python untuk rename file otomatis") == "coding"


def test_detect_task_type_concept_for_machine_learning_feature():
    assert detect_task_type("Apa yang dimaksud feature dalam machine learning?") == "concept"


def test_detect_task_type_trick_for_accuracy_question():
    assert detect_task_type("Jika accuracy model 99%, apakah pasti bagus?") == "trick"


def test_detect_task_type_ambiguous_short_question():
    assert detect_task_type("Mana yang lebih baik?") == "ambiguous"


def test_thinking_context_includes_internal_self_check():
    context = build_thinking_mode_context("Apa itu data leakage?", mode="thinking")
    lowered = context.lower()

    assert "thinking mode: aktif" in lowered
    assert "self-check internal" in lowered
    assert "jangan mengarang" in lowered
    assert "jenis tugas terdeteksi" in lowered


def test_thinking_context_uses_coding_format_for_project_request():
    context = build_thinking_mode_context("Buat aplikasi Flask kecil dengan SQLite", mode="thinking")
    lowered = context.lower()

    assert "format coding" in lowered
    assert "kode runnable" in lowered
    assert "cara test" in lowered


def test_self_check_context_mentions_uncertainty_and_edge_cases():
    context = build_self_check_context("Siapa menteri keuangan Indonesia saat ini?", mode="thinking")
    lowered = context.lower()

    assert "data belum cukup" in lowered or "butuh info terbaru" in lowered
    assert "edge case" in lowered
