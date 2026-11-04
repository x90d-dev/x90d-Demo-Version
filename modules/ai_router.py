import re

from modules.multiple_choice_checker import is_multiple_choice


SUBJECTS = {
    "matematika": [
        "persamaan",
        "hitung",
        "integral",
        "turunan",
        "aljabar",
        "fungsi",
        "akar",
        "pecahan",
        "gradien",
        "matriks",
        "sin",
        "cos",
        "tan",
    ],
    "fisika": [
        "gaya",
        "massa",
        "kecepatan",
        "percepatan",
        "energi",
        "newton",
        "usaha",
        "daya",
        "momentum",
        "tegangan",
        "arus",
        "gerak",
    ],
    "kimia": [
        "mol",
        "reaksi",
        "asam",
        "basa",
        "ph",
        "atom",
        "stoikiometri",
        "ikatan",
        "larutan",
        "oksidasi",
        "reduksi",
    ],
    "bahasa_inggris": [
        "grammar",
        "verb",
        "noun",
        "sentence",
        "adjective",
        "adverb",
        "tenses",
        "vocabulary",
        "synonym",
        "antonym",
        "translate",
    ],
    "sejarah": [
        "kerajaan",
        "proklamasi",
        "perang",
        "kolonial",
        "kemerdekaan",
        "merdeka",
        "indonesia merdeka",
        "17 agustus",
        "1945",
        "revolusi",
        "majapahit",
        "sriwijaya",
        "penjajahan",
    ],
    "pendidikan": [
        "pedagogik",
        "kurikulum",
        "pembelajaran",
        "evaluasi",
        "asesmen",
        "didik",
        "guru",
        "kelas",
        "kompetensi",
    ],
    "toefl": [
        "toefl",
        "structure",
        "written expression",
        "reading comprehension",
        "error recognition",
        "listening",
    ],
    "coding": [
        "python",
        "kode",
        "coding",
        "program",
        "aplikasi",
        "software",
        "project",
        "flask",
        "sqlite",
        "api",
        "debug",
        "bug",
        "backend",
        "frontend",
        "tkinter",
        "streamlit",
        "django",
        "fastapi",
        "arsitektur",
    ],
}


def _keyword_score(text: str, keywords: list[str]) -> int:
    score = 0
    for keyword in keywords:
        if " " in keyword:
            score += 2 if keyword in text else 0
        elif re.search(rf"\b{re.escape(keyword)}\b", text):
            score += 1
    return score


def detect_subject(question: str) -> str:
    text = (question or "").lower()
    if not text.strip():
        return "umum"

    scores = {subject: _keyword_score(text, keywords) for subject, keywords in SUBJECTS.items()}

    if re.search(r"\b[x-y]\b", text) and re.search(r"[=+\-*/^]|\d", text):
        scores["matematika"] += 2
    if "?" in text and any(word in text for word in ["why", "choose", "sentence", "correct"]):
        scores["bahasa_inggris"] += 1
    if "toefl" in text or "reading comprehension" in text or "written expression" in text:
        scores["toefl"] += 3

    subject, score = max(scores.items(), key=lambda item: item[1])
    return subject if score > 0 else "umum"


def detect_question_type(question: str) -> str:
    text = (question or "").lower()
    if is_multiple_choice(question):
        return "multiple_choice"
    if any(key in text for key in ["reading comprehension", "read the text", "passage", "bacaan", "teks berikut", "paragraf"]):
        return "reading"
    if re.search(r"\d+\s*[\+\-\*/=^]\s*\d+", text) or any(
        key in text for key in ["hitung", "berapa", "tentukan", "persamaan", "integral", "turunan", "mol", "ph"]
    ):
        return "calculation"
    return "essay"
