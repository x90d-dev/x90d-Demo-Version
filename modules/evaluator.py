import re

from modules.thinking_mode import detect_task_type


GENERIC_FAILURE_PHRASES = [
    "tidak bisa menemukan hasil",
    "saya tidak dapat memberikan informasi",
    "silakan lakukan penelitian sendiri",
    "maaf, web search gagal",
    "tidak memiliki akses internet",
]

FAKE_SOURCE_PHRASES = [
    "berdasarkan wikipedia",
    "menurut para ahli",
    "data menunjukkan",
    "menurut penelitian",
]

UNCERTAINTY_KEYWORDS = [
    "saat ini",
    "terbaru",
    "ranking",
    "harga",
    "berita",
    "2026",
    "sekarang",
]


def evaluate_response_quality(question: str, answer: str, task_type: str | None = None) -> dict:
    clean_question = (question or "").strip()
    clean_answer = (answer or "").strip()
    detected_task = task_type or detect_task_type(clean_question)

    checks = {
        "non_empty": bool(clean_answer),
        "answers_directly": _answers_directly(clean_question, clean_answer),
        "not_generic_refusal": not _contains_any(clean_answer, GENERIC_FAILURE_PHRASES),
        "no_fake_source_language": not _contains_any(clean_answer, FAKE_SOURCE_PHRASES),
        "mentions_uncertainty_when_needed": _mentions_uncertainty_when_needed(clean_question, clean_answer),
        "has_relevant_example": _has_relevant_example(clean_question, clean_answer, detected_task),
        "task_specific_quality": _task_specific_quality(clean_question, clean_answer, detected_task),
    }

    weights = {
        "non_empty": 15,
        "answers_directly": 20,
        "not_generic_refusal": 15,
        "no_fake_source_language": 10,
        "mentions_uncertainty_when_needed": 10,
        "has_relevant_example": 10,
        "task_specific_quality": 20,
    }
    score = sum(weights[key] for key, passed in checks.items() if passed)
    missing = [key for key, passed in checks.items() if not passed]

    return {
        "score": score,
        "level": _score_level(score),
        "task_type": detected_task,
        "checks": checks,
        "missing": missing,
        "recommendation": _recommendation(detected_task, missing),
    }


def evaluate_against_rubric(answer: str, expected_keywords: list[str], must_not_contain: list[str] | None = None) -> dict:
    clean_answer = (answer or "").lower()
    expected = [keyword.lower() for keyword in expected_keywords or []]
    forbidden = [keyword.lower() for keyword in must_not_contain or []]

    matched = [keyword for keyword in expected if keyword in clean_answer]
    forbidden_hits = [keyword for keyword in forbidden if keyword in clean_answer]
    keyword_score = int((len(matched) / max(1, len(expected))) * 100)
    final_score = max(0, keyword_score - (20 * len(forbidden_hits)))

    return {
        "score": final_score,
        "matched_keywords": matched,
        "missing_keywords": [keyword for keyword in expected if keyword not in matched],
        "forbidden_hits": forbidden_hits,
        "passed": final_score >= 70 and not forbidden_hits,
    }


def _answers_directly(question: str, answer: str) -> bool:
    if not answer:
        return False
    lowered_answer = answer.lower()
    lowered_question = question.lower()
    if len(answer.split()) < 4:
        return True
    if _contains_any(lowered_answer, ["jawaban inti", "solusi", "penyebab", "masalah", "feature", "fitur"]):
        return True
    question_terms = [word for word in re.findall(r"\w+", lowered_question) if len(word) > 4][:8]
    return any(term in lowered_answer for term in question_terms)


def _mentions_uncertainty_when_needed(question: str, answer: str) -> bool:
    lowered_question = question.lower()
    lowered_answer = answer.lower()
    needs_uncertainty = _contains_any(lowered_question, UNCERTAINTY_KEYWORDS)
    if not needs_uncertainty:
        return True
    return _contains_any(
        lowered_answer,
        ["berdasarkan", "sumber", "perlu dicek", "bisa berubah", "saat ini", "belum bisa memastikan", "tidak ditemukan"],
    )


def _has_relevant_example(question: str, answer: str, task_type: str) -> bool:
    lowered_question = question.lower()
    lowered_answer = answer.lower()
    if task_type in {"fact", "debugging"}:
        return True
    if task_type == "concept":
        return _contains_any(lowered_answer, ["contoh", "misalnya", "seperti"])
    if "contoh" in lowered_question:
        return _contains_any(lowered_answer, ["contoh", "misalnya", "seperti", "luas", "jumlah"])
    return True


def _task_specific_quality(question: str, answer: str, task_type: str) -> bool:
    lowered_answer = answer.lower()
    lowered_question = question.lower()
    if task_type == "coding":
        has_code = "```" in answer or any(mark in lowered_answer for mark in ["def ", "class ", "function ", "import "])
        has_run_or_test = _contains_any(lowered_answer, ["cara menjalankan", "cara test", "pytest", "uji", "test"])
        return has_code and has_run_or_test
    if task_type == "debugging":
        return _contains_any(lowered_answer, ["penyebab", "akar", "kemungkinan"]) and _contains_any(
            lowered_answer, ["cek", "verifikasi", "uji", "test", "pastikan"]
        )
    if task_type == "math":
        return _contains_any(lowered_answer, ["langkah", "rumus", "cek", "jawaban akhir"])
    if task_type == "concept":
        if _contains_any(lowered_question, ["feature", "machine learning", "fitur"]):
            return _contains_any(lowered_answer, ["input", "atribut", "variabel"]) and _contains_any(
                lowered_answer, ["harga rumah", "luas", "jumlah kamar", "lokasi"]
            )
        return _contains_any(lowered_answer, ["adalah", "contoh", "berbeda", "karena"])
    if task_type == "trick":
        return _contains_any(lowered_answer, ["tidak selalu", "belum tentu", "premis", "tergantung", "jebakan"])
    if "sql injection" in lowered_question:
        return _contains_any(lowered_answer, ["parameterized", "prepared", "validasi", "bind"])
    return True


def _score_level(score: int) -> str:
    if score >= 90:
        return "excellent"
    if score >= 75:
        return "good"
    if score >= 60:
        return "needs_review"
    return "weak"


def _recommendation(task_type: str, missing: list[str]) -> str:
    if not missing:
        return "Jawaban sudah memenuhi rubric dasar."
    if task_type == "coding":
        return "Tambahkan kode runnable, cara menjalankan, cara test, dan edge case."
    if task_type == "debugging":
        return "Tambahkan penyebab, langkah cek, perbaikan, dan cara verifikasi."
    if task_type == "concept":
        return "Tambahkan definisi inti, contoh konkret, dan beda konsep yang mirip."
    if task_type == "fact":
        return "Tambahkan sumber/konteks terbaru atau nyatakan ketidakpastian dengan jelas."
    return "Perjelas jawaban inti, asumsi, contoh, dan batasan."


def _contains_any(text: str, phrases: list[str]) -> bool:
    lowered = (text or "").lower()
    return any(phrase.lower() in lowered for phrase in phrases)
