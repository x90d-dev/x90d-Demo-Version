from modules.ai_provider import generate_ai_response
from modules.rag_engine import load_question_bank


def generate_similar_exercises(question: str, subject: str, level: int = 1) -> str:
    bank = [
        item for item in load_question_bank()
        if item.get("subject") == subject and int(item.get("level", 1)) <= int(level or 1) + 1
    ]
    if bank:
        lines = []
        for index, item in enumerate(bank[:3], start=1):
            lines.append(f"{index}. {item.get('question', '')}\n   Kunci: {item.get('answer', '')}")
        return "\n".join(lines)

    prompt = f"""Buat 3 soal latihan singkat untuk subject {subject}, level {level}.
Soal acuan: {question[:500]}
Tulis format:
1. Soal
Kunci: ...
2. Soal
Kunci: ...
3. Soal
Kunci: ...
"""
    return generate_ai_response(prompt)
