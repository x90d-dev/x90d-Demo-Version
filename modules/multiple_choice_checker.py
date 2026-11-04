import re


OPTION_PATTERN = re.compile(r"(?im)^\s*([A-E])[\.\)]\s*(.+)$")
INLINE_OPTION_PATTERN = re.compile(r"(?i)(?:^|\s)([A-E])[\.\)]\s+(.+?)(?=\s+[A-E][\.\)]\s+|$)")


def detect_options(question: str) -> list[dict[str, str]]:
    if not question:
        return []

    options = [{"label": m.group(1).upper(), "text": m.group(2).strip()} for m in OPTION_PATTERN.finditer(question)]
    if len(options) >= 2:
        return options

    inline_options = [
        {"label": m.group(1).upper(), "text": m.group(2).strip()}
        for m in INLINE_OPTION_PATTERN.finditer(question)
    ]
    return inline_options if len(inline_options) >= 2 else options


def normalize_choice(answer: str) -> str:
    if not answer:
        return ""
    match = re.search(r"\b([A-E])\b", answer.strip().upper())
    if match:
        return match.group(1)
    prefix = re.match(r"\s*([A-E])[\.\)]", answer.strip().upper())
    return prefix.group(1) if prefix else ""


def is_multiple_choice(question: str) -> bool:
    return len(detect_options(question)) >= 2
