from modules.database import init_db
from modules.progress_tracker import (
    calculate_next_level,
    get_progress_summary,
    save_practice_result,
    update_progress,
)


def test_calculate_next_level():
    assert calculate_next_level(8, 10, 1) == 2
    assert calculate_next_level(6, 10, 2) == 2
    assert calculate_next_level(4, 10, 2) == 1
    assert calculate_next_level(0, 0, 1) == 1


def test_save_and_update_progress(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.db"))
    init_db()

    save_practice_result(
        subject="matematika",
        topic="persamaan linear",
        question="2x=8",
        user_answer="4",
        correct_answer="4",
        is_correct=True,
        mistake_note="",
        level=1,
    )
    update_progress("matematika", "persamaan linear", True, "", 1)

    rows = get_progress_summary()
    assert len(rows) == 1
    assert rows[0]["total_questions"] == 1
    assert rows[0]["correct_count"] == 1
