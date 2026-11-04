from modules.deep_check import (
    analyze_deep_check,
    build_deep_check_context,
    estimate_problem_level,
    format_rupiah,
    should_use_deep_check_mode,
)


def test_deep_check_detects_ratio_final_total_problem():
    question = "A : B = 3 : 5. A bertambah 60.000, B berkurang 20.000. Rasio akhir 2 : 3. Total akhir 640.000."
    assert should_use_deep_check_mode(question)
    assert estimate_problem_level(question) == 7


def test_deep_check_finds_inconsistent_conditions():
    question = "A : B = 3 : 5. A bertambah 60.000, B berkurang 20.000. Rasio akhir 2 : 3. Total akhir 640.000."
    analysis = analyze_deep_check(question)
    assert analysis["consistency"] == "inconsistent"
    assert analysis["contradictions"]


def test_deep_check_handles_three_party_transfer():
    question = (
        "A : B : C = 2 : 3 : 5. A mendapat 40.000. B memakai 30.000. "
        "C memberi 50.000 kepada A. Rasio akhir 5 : 4 : 6. Total akhir 900.000."
    )
    context = build_deep_check_context(question)
    assert "A akhir = 2x + 90000" in context
    assert "C memberi Rp50.000 kepada A" in context
    assert "deep_check_mode: AKTIF" in context


def test_format_rupiah_uses_indonesian_separator():
    assert format_rupiah(900000) == "Rp900.000"
