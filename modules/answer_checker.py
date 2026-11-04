import re
import string

from modules.math_checker import compare_math_answers
from modules.multiple_choice_checker import normalize_choice


def _normalize_text(value: str) -> str:
    text = (value or "").lower().strip()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return re.sub(r"\s+", " ", text)


def check_answer(user_answer, correct_answer, subject, question_type) -> dict:
    user = str(user_answer or "").strip()
    correct = str(correct_answer or "").strip()

    if not user:
        return {
            "is_correct": False,
            "score": 0,
            "feedback": "Jawaban masih kosong. Coba isi dulu, lalu periksa kembali.",
            "mistake_note": "Jawaban kosong",
        }

    if question_type == "multiple_choice":
        is_correct = normalize_choice(user) == normalize_choice(correct)
        return {
            "is_correct": is_correct,
            "score": 100 if is_correct else 0,
            "feedback": "Benar, pilihanmu sudah tepat." if is_correct else f"Belum tepat. Kunci jawaban: {correct}.",
            "mistake_note": "" if is_correct else "Pilihan ganda tidak sesuai kunci",
        }

    if subject == "matematika" or question_type == "calculation":
        is_correct = compare_math_answers(user, correct)
        return {
            "is_correct": is_correct,
            "score": 100 if is_correct else 0,
            "feedback": "Benar, hasil hitungan sesuai." if is_correct else f"Belum tepat. Kunci jawaban: {correct}.",
            "mistake_note": "" if is_correct else "Hasil hitungan berbeda dari kunci",
        }

    user_norm = _normalize_text(user)
    correct_norm = _normalize_text(correct)
    is_correct = user_norm == correct_norm or (len(correct_norm) > 3 and correct_norm in user_norm)

    return {
        "is_correct": is_correct,
        "score": 100 if is_correct else 0,
        "feedback": "Benar, jawabanmu sesuai inti kunci." if is_correct else f"Belum tepat. Kunci ringkas: {correct}.",
        "mistake_note": "" if is_correct else "Jawaban belum memuat inti kunci",
    }
