import json
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def _read_json(filename: str, fallback):
    path = DATA_DIR / filename
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return fallback


def load_materials():
    return _read_json("materi_sample.json", [])


def load_question_bank():
    return _read_json("bank_soal_sample.json", [])


def _tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-zA-Z0-9]+", (text or "").lower()) if len(token) > 2}


def _item_text(item: dict) -> str:
    values = []
    for key in ["subject", "topic", "title", "content", "question", "answer", "explanation"]:
        value = item.get(key)
        if isinstance(value, str):
            values.append(value)
    keywords = item.get("keywords", [])
    if isinstance(keywords, list):
        values.extend(str(keyword) for keyword in keywords)
    return " ".join(values)


def _score_item(item: dict, question_tokens: set[str], subject: str, topic: str | None = None) -> int:
    text = _item_text(item).lower()
    item_tokens = _tokens(text)
    score = len(question_tokens.intersection(item_tokens))
    if item.get("subject") == subject:
        score += 4
    if topic and topic.lower() in text:
        score += 3
    return score


def _shorten(text: str, limit: int = 320) -> str:
    clean = re.sub(r"\s+", " ", text).strip()
    return clean if len(clean) <= limit else clean[: limit - 3].rstrip() + "..."


def search_relevant_context(question, subject, topic=None):
    question_tokens = _tokens(question)
    items = load_materials() + load_question_bank()
    scored = []
    for item in items:
        score = _score_item(item, question_tokens, subject, topic)
        if score > 0:
            scored.append((score, item))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    contexts = []
    for _, item in scored[:2]:
        label = item.get("topic") or item.get("title") or "Materi"
        body = item.get("content") or item.get("explanation") or item.get("question") or ""
        if body:
            contexts.append(f"{label}: {_shorten(body)}")
    return "\n".join(contexts)


def infer_topic(question: str, subject: str) -> str:
    question_tokens = _tokens(question)
    items = load_materials() + load_question_bank()
    best_topic = "umum"
    best_score = 0
    for item in items:
        if item.get("subject") != subject:
            continue
        score = _score_item(item, question_tokens, subject)
        if score > best_score:
            best_score = score
            best_topic = item.get("topic", "umum")
    return best_topic
