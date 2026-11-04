from modules.database import get_learning_notes, init_db
from modules.smart_context import build_smart_context
from modules.training_seed import BRUTAL_TRAINING_NOTES, install_training_notes


SAMPLE_TRAINING_NOTES = [
    {"subject": "coding", "trigger_text": "rename file otomatis", "correction": "Wajib ada dry-run, undo, log, dan pytest."},
    {"subject": "matematika", "trigger_text": "rasio perubahan", "correction": "Wajib validasi kondisi awal dan akhir."},
]


def test_brutal_training_pack_installs_idempotently(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "training.db"))
    init_db()

    first = install_training_notes(SAMPLE_TRAINING_NOTES)
    second = install_training_notes(SAMPLE_TRAINING_NOTES)

    assert first["inserted"] == len(SAMPLE_TRAINING_NOTES)
    assert first["skipped"] == 0
    assert second["inserted"] == 0
    assert second["skipped"] == len(SAMPLE_TRAINING_NOTES)
    assert len(get_learning_notes(limit=100000)) == len(SAMPLE_TRAINING_NOTES)


def test_brutal_training_pack_feeds_smart_context(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "training_context.db"))
    init_db()
    install_training_notes(SAMPLE_TRAINING_NOTES)

    context = build_smart_context("buat aplikasi python rename file otomatis", subject="coding")

    assert "Memori koreksi (coding)" in context
    assert "dry-run" in context
    assert "pytest" in context


def test_brutal_training_pack_has_hundreds_thousands_notes():
    assert len(BRUTAL_TRAINING_NOTES) >= 400000
