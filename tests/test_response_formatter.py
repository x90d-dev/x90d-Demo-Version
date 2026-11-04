from modules.response_formatter import clean_ai_response


def test_clean_ai_response_removes_raw_latex_and_markdown():
    raw = "### Langkah\n\\[ v = \\frac{10 \\, \\text{N}}{2 \\, \\text{kg}} \\]\nJadi **hasilnya** 5."
    cleaned = clean_ai_response(raw)
    assert "###" not in cleaned
    assert "\\[" not in cleaned
    assert "**" not in cleaned
    assert "$$" in cleaned
    assert "\\frac{10 \\, \\text{N}}{2 \\, \\text{kg}}" in cleaned


def test_clean_ai_response_formats_inline_fraction_and_root():
    cleaned = clean_ai_response("Nilai x = 1/2 dan akar sqrt(2), rumus a = F/m.")
    assert "1 per 2" in cleaned
    assert "√(2)" in cleaned
    assert "F per m" in cleaned
    assert "1/2" not in cleaned
    assert "sqrt(2)" not in cleaned


def test_clean_ai_response_preserves_code_blocks():
    raw = "Kode:\n```python\nratio = a / b\npath = 'data/file.txt'\n```"
    cleaned = clean_ai_response(raw)
    assert "ratio = a / b" in cleaned
    assert "data/file.txt" in cleaned


def test_clean_ai_response_compacts_blank_lines():
    assert clean_ai_response("A\n\n\n\nB") == "A\n\nB"


def test_clean_ai_response_removes_unneeded_opening_sentence():
    raw = "Untuk pertanyaan ini, saya akan menjawabnya secara langsung tanpa membagi menjadi beberapa bagian. Presiden Indonesia adalah Prabowo Subianto."
    cleaned = clean_ai_response(raw)

    assert cleaned == "Presiden Indonesia adalah Prabowo Subianto."


def test_clean_ai_response_removes_brief_polite_opening():
    raw = "Baik Admin, berikut jawabannya. Diketahui: massa = 2 kg."
    cleaned = clean_ai_response(raw)

    assert cleaned == "Diketahui: massa = 2 kg."
