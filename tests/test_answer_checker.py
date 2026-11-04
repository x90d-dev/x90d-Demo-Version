from modules.answer_checker import check_answer


def test_multiple_choice_correct():
    result = check_answer("B", "B", "bahasa_inggris", "multiple_choice")
    assert result["is_correct"] is True
    assert result["score"] == 100


def test_multiple_choice_wrong():
    result = check_answer("A", "C", "matematika", "multiple_choice")
    assert result["is_correct"] is False


def test_math_checker_simple_equation_answer():
    result = check_answer("x = 4", "4", "matematika", "calculation")
    assert result["is_correct"] is True


def test_calculation_with_unit_answer():
    result = check_answer("5 m/s^2", "5", "fisika", "calculation")
    assert result["is_correct"] is True


def test_text_answer_contains_key():
    result = check_answer("Indonesia merdeka pada 17 Agustus 1945", "17 Agustus 1945", "sejarah", "essay")
    assert result["is_correct"] is True
