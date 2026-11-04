from modules.evaluator import evaluate_against_rubric, evaluate_response_quality


def test_evaluator_penalizes_generic_web_failure_for_stable_ml_concept():
    result = evaluate_response_quality(
        "Apa yang dimaksud dengan feature dalam machine learning? Berikan contoh feature dalam kasus prediksi harga rumah.",
        "Maaf, saya tidak bisa menemukan hasil langsung dari pencarian web.",
    )

    assert result["score"] < 70
    assert "not_generic_refusal" in result["missing"]


def test_evaluator_rewards_good_machine_learning_feature_answer():
    answer = (
        "Feature adalah input atau atribut yang dipakai model untuk membuat prediksi. "
        "Pada prediksi harga rumah, contohnya luas tanah, jumlah kamar, lokasi, usia bangunan, "
        "dan kondisi rumah. Targetnya adalah harga rumah."
    )
    result = evaluate_response_quality(
        "Apa yang dimaksud dengan feature dalam machine learning? Berikan contoh feature dalam kasus prediksi harga rumah.",
        answer,
    )

    assert result["score"] >= 80
    assert result["checks"]["task_specific_quality"]


def test_evaluator_requires_runnable_shape_for_coding_answer():
    weak = evaluate_response_quality("Buat script Python untuk rename file.", "Gunakan os.rename untuk mengganti nama file.")
    strong = evaluate_response_quality(
        "Buat script Python untuk rename file.",
        "Solusi:\n```python\nfrom pathlib import Path\nprint('ok')\n```\nCara menjalankan: python rename.py\nCara test: jalankan dry-run dulu.",
    )

    assert weak["score"] < strong["score"]
    assert "task_specific_quality" in weak["missing"]
    assert strong["checks"]["task_specific_quality"]


def test_evaluator_requires_debugging_cause_and_verification():
    result = evaluate_response_quality(
        "Mengapa error TypeError unsupported operand type?",
        "Penyebabnya tipe data int dan str dicampur. Cek baris operasi tambah, konversi input, lalu verifikasi dengan test kecil.",
    )

    assert result["task_type"] == "debugging"
    assert result["checks"]["task_specific_quality"]


def test_rubric_evaluator_matches_keywords_and_forbidden_words():
    result = evaluate_against_rubric(
        "Gunakan parameterized query atau prepared statement, validasi input, dan jangan concatenation query langsung.",
        expected_keywords=["parameterized", "prepared", "validasi"],
        must_not_contain=["password hardcoded"],
    )

    assert result["passed"]
    assert result["score"] >= 70
