import json
from pathlib import Path


BENCHMARK_PATH = Path(__file__).resolve().parents[1] / "data" / "evaluation_questions.json"

REQUIRED_CATEGORIES = {
    "coding_simple",
    "debugging",
    "algorithm",
    "sql",
    "python",
    "javascript",
    "api_backend",
    "frontend",
    "security",
    "mathematics",
    "logic",
    "machine_learning",
    "data_analysis",
    "ambiguous",
    "false_premise",
    "uncertainty",
    "short_answer",
    "detailed_answer",
    "comparison",
}


def _load_items():
    return json.loads(BENCHMARK_PATH.read_text(encoding="utf-8"))


def test_evaluation_question_bank_has_at_least_fifty_items():
    items = _load_items()

    assert len(items) >= 50


def test_evaluation_question_bank_items_have_required_fields():
    items = _load_items()
    required_fields = {"id", "category", "task_type", "question", "expected_keywords", "must_not_contain", "rubric"}

    for item in items:
        assert required_fields <= set(item)
        assert item["id"]
        assert item["category"]
        assert item["task_type"]
        assert item["question"]
        assert item["expected_keywords"]
        assert item["rubric"]


def test_evaluation_question_bank_covers_required_categories():
    items = _load_items()
    categories = {item["category"] for item in items}

    assert REQUIRED_CATEGORIES <= categories


def test_evaluation_question_ids_are_unique():
    items = _load_items()
    ids = [item["id"] for item in items]

    assert len(ids) == len(set(ids))
