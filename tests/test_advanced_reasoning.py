from modules.advanced_reasoning import build_advanced_context, build_symbolic_math_hint, detect_difficulty


def test_detect_difficulty_advanced_keywords():
    assert detect_difficulty("Buktikan dengan induksi soal olimpiade ini") == "advanced"


def test_symbolic_math_hint_solves_simple_equation():
    hint = build_symbolic_math_hint("Selesaikan persamaan 2x + 3 = 11")
    assert "x = 4" in hint


def test_advanced_context_adds_physics_protocol():
    context = build_advanced_context("Soal momentum sulit dengan massa dan kecepatan", "fisika", "calculation")
    assert "cek dimensi satuan" in context
