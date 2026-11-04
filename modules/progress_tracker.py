from modules import database


def calculate_next_level(correct_count, total_questions, current_level):
    if total_questions <= 0:
        return max(1, int(current_level or 1))

    level = max(1, int(current_level or 1))
    accuracy = correct_count / total_questions
    if accuracy >= 0.8:
        return level + 1
    if accuracy >= 0.5:
        return level
    return max(1, level - 1)


def save_practice_result(subject, topic, question, user_answer, correct_answer, is_correct, mistake_note, level=1):
    return database.insert_practice_result(
        subject=subject or "umum",
        topic=topic or "umum",
        question=question or "",
        user_answer=user_answer or "",
        correct_answer=correct_answer or "",
        is_correct=bool(is_correct),
        mistake_note=mistake_note or "",
        level=int(level or 1),
    )


def update_progress(subject, topic, is_correct, mistake_note="", level=1):
    subject = subject or "umum"
    topic = topic or "umum"
    database.init_db()
    with database.get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM progress WHERE subject = ? AND topic = ?",
            (subject, topic),
        ).fetchone()

        if row:
            total = int(row["total_questions"]) + 1
            correct = int(row["correct_count"]) + (1 if is_correct else 0)
            wrong = int(row["wrong_count"]) + (0 if is_correct else 1)
            next_level = calculate_next_level(correct, total, int(row["level"]))
            weakness = row["weakness"] if is_correct else (mistake_note or "Perlu latihan ulang")
            conn.execute(
                """
                UPDATE progress
                SET total_questions = ?, correct_count = ?, wrong_count = ?,
                    level = ?, weakness = ?, updated_at = CURRENT_TIMESTAMP
                WHERE subject = ? AND topic = ?
                """,
                (total, correct, wrong, next_level, weakness, subject, topic),
            )
        else:
            total = 1
            correct = 1 if is_correct else 0
            wrong = 0 if is_correct else 1
            next_level = calculate_next_level(correct, total, int(level or 1))
            weakness = "" if is_correct else (mistake_note or "Perlu latihan ulang")
            conn.execute(
                """
                INSERT INTO progress
                (subject, topic, total_questions, correct_count, wrong_count, level, weakness)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (subject, topic, total, correct, wrong, next_level, weakness),
            )
        return conn.execute(
            "SELECT * FROM progress WHERE subject = ? AND topic = ?",
            (subject, topic),
        ).fetchone()


def get_progress_summary():
    return database.get_progress_rows()
