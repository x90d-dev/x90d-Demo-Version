from modules.ai_provider import generate_ai_response
from modules.ai_router import SUBJECTS, detect_question_type, detect_subject
from modules.advanced_reasoning import build_advanced_context
from modules.prompt_builder import build_prompt
from modules.rag_engine import infer_topic, search_relevant_context
from modules.response_formatter import clean_ai_response
from modules.smart_context import build_smart_context


VALID_SUBJECTS = set(SUBJECTS.keys()) | {"umum"}


def solve_question(question: str, selected_subject: str = "auto") -> dict:
    clean_question = (question or "").strip()
    if not clean_question:
        raise ValueError("Soal tidak boleh kosong.")
    if len(clean_question) > 4000:
        raise ValueError("Soal terlalu panjang. Ringkas soal agar CoreChiperAgent lebih responsif.")

    selected = (selected_subject or "auto").strip().lower()
    subject = detect_subject(clean_question) if selected == "auto" else selected
    if subject not in VALID_SUBJECTS:
        subject = "umum"

    question_type = detect_question_type(clean_question)
    topic = infer_topic(clean_question, subject)
    rag_context = search_relevant_context(clean_question, subject, topic)
    smart_context = build_smart_context(clean_question, subject)
    advanced_context = build_advanced_context(clean_question, subject, question_type)
    context = "\n".join(part for part in [smart_context, advanced_context, rag_context] if part)
    prompt = build_prompt(clean_question, subject, question_type, context)
    answer = clean_ai_response(generate_ai_response(prompt))

    return {
        "subject": subject,
        "topic": topic,
        "question_type": question_type,
        "answer": answer,
        "context_used": context,
    }
