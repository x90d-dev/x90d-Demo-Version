from modules.database import init_db, save_learning_note
from modules.smart_context import build_smart_context


def test_smart_context_physics_velocity_hint():
    context = build_smart_context("Benda massa 2 kg diberi gaya 10 N selama 4 detik, berapa kecepatan?")
    assert "F = m x a" in context
    assert "bukan kecepatan" in context
    assert "v = a x t" in context


def test_smart_context_latest_data_warning():
    context = build_smart_context("Top 10 universitas China terbaru")
    assert "tanpa web search" in context


def test_smart_context_machine_learning_feature_hint():
    context = build_smart_context(
        "Apa yang dimaksud dengan feature dalam machine learning? Berikan contoh feature dalam kasus prediksi harga rumah."
    )

    assert "feature adalah variabel/input/atribut" in context
    assert "harga rumah" in context
    assert "luas tanah" in context
    assert "Target/labelnya" in context


def test_smart_context_uses_learning_notes(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "smart.db"))
    init_db()
    save_learning_note("fisika", "gaya massa waktu", "F/m adalah percepatan, lalu kecepatan perlu waktu.")

    context = build_smart_context("gaya massa waktu")
    assert "Memori koreksi" in context
    assert "F/m adalah percepatan" in context


def test_smart_context_uses_coding_learning_notes(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "coding_smart.db"))
    init_db()
    save_learning_note("coding", "rename file otomatis", "Wajib ada dry-run, undo, log, dan pytest.")

    context = build_smart_context("buat aplikasi python rename file otomatis", subject="coding")
    assert "Coding/Developer" in context
    assert "Memori koreksi (coding)" in context
    assert "dry-run" in context
