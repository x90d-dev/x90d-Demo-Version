import re


def clean_ai_response(text: str) -> str:
    """Make small-model output easier to read in plain HTML."""
    if not text:
        return ""

    cleaned = str(text).replace("\r\n", "\n")
    code_blocks: list[str] = []
    cleaned = _stash_code_blocks(cleaned, code_blocks)
    cleaned = re.sub(r"\\\[\s*([\s\S]*?)\s*\\\]", r"$$\1$$", cleaned)
    math_blocks: list[str] = []
    cleaned = _stash_math_blocks(cleaned, math_blocks)
    cleaned = cleaned.replace("\\[", "").replace("\\]", "")
    cleaned = cleaned.replace("\\(", "").replace("\\)", "")
    cleaned = cleaned.replace("\\,", " ")
    cleaned = cleaned.replace("\\times", "x")
    cleaned = cleaned.replace("\\cdot", "x")
    cleaned = cleaned.replace("\\text", "text")
    cleaned = _remove_unneeded_opening(cleaned)

    cleaned = re.sub(r"text\{([^{}]+)\}", r"\1", cleaned)
    cleaned = _replace_frac(cleaned)
    cleaned = _replace_inline_division(cleaned)
    cleaned = _replace_roots(cleaned)
    cleaned = re.sub(r"(?m)^\s{0,3}#{1,6}\s*", "", cleaned)
    cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", cleaned)
    cleaned = re.sub(r"__([^_]+)__", r"\1", cleaned)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    cleaned = re.sub(r"[ \t]+\n", "\n", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = _restore_math_blocks(cleaned, math_blocks)
    cleaned = _restore_code_blocks(cleaned, code_blocks)
    return cleaned.strip()


def _remove_unneeded_opening(text: str) -> str:
    opening_patterns = [
        r"^\s*(?:baik|tentu|siap)[,!\s]*(?:admin)?[,!\s]*(?:\n+|$)",
        r"^\s*(?:baik|tentu|siap)[,!\s]*(?:admin)?[,!\s]+(?=(?:jawaban|inti|diketahui|ditanya|mata pelajaran|topik|berikut|saya|untuk)\b)",
        r"^\s*(?:untuk|pada)\s+(?:pertanyaan|soal|permintaan)\s+(?:ini|tersebut)[,\s]+(?:saya|aku|kita)\s+[^.!?\n]{0,180}[.!?]\s*",
        r"^\s*(?:saya|aku)\s+(?:akan|coba|bisa)\s+(?:menjawab|menjelaskan|membantu|mengerjakan|membahas)[^.!?\n]{0,180}[.!?]\s*",
        r"^\s*(?:mari|ayo)\s+(?:kita\s+)?(?:bahas|jawab|selesaikan|kerjakan|lihat)[^.!?\n]{0,160}[.!?]\s*",
        r"^\s*berikut\s+(?:adalah\s+)?(?:jawaban|penjelasan|pembahasan)[^.!?\n]{0,120}[.!?]\s*",
    ]
    cleaned = text
    for pattern in opening_patterns:
        cleaned = re.sub(pattern, "", cleaned, count=1, flags=re.IGNORECASE)
    return cleaned.lstrip()


def _replace_frac(text: str) -> str:
    pattern = re.compile(r"\\frac\{([^{}]+)\}\{([^{}]+)\}")
    previous = None
    current = text
    while previous != current:
        previous = current
        current = pattern.sub(r"\1 per \2", current)
    return current


def _replace_inline_division(text: str) -> str:
    text = re.sub(r"(?<![\w:/.-])(\d+(?:[.,]\d+)?)\s*/\s*(\d+(?:[.,]\d+)?)(?![\w/])", r"\1 per \2", text)
    text = re.sub(
        r"(?<![\w:/.-])([A-Za-z](?:\d)?(?:\s*[+\-]\s*\d+)?)\s*/\s*([A-Za-z](?:\d)?)(?![\w/])",
        r"\1 per \2",
        text,
    )
    return text


def _replace_roots(text: str) -> str:
    text = re.sub(r"\\sqrt\{([^{}]+)\}", r"√(\1)", text)
    text = re.sub(r"\bsqrt\s*\(\s*([^)]+?)\s*\)", r"√(\1)", text, flags=re.IGNORECASE)
    text = re.sub(r"\bsqrt\s*\{\s*([^{}]+?)\s*\}", r"√(\1)", text, flags=re.IGNORECASE)
    return text


def _stash_code_blocks(text: str, blocks: list[str]) -> str:
    def store(match: re.Match) -> str:
        blocks.append(match.group(0))
        return f"@@CODE_BLOCK_{len(blocks) - 1}@@"

    return re.sub(r"```[\s\S]*?```", store, text)


def _stash_math_blocks(text: str, blocks: list[str]) -> str:
    def store(match: re.Match) -> str:
        blocks.append(match.group(0))
        return f"@@MATH_BLOCK_{len(blocks) - 1}@@"

    return re.sub(r"\$\$[\s\S]*?\$\$", store, text)


def _restore_math_blocks(text: str, blocks: list[str]) -> str:
    for index, block in enumerate(blocks):
        text = text.replace(f"@@MATH_BLOCK_{index}@@", block)
    return text


def _restore_code_blocks(text: str, blocks: list[str]) -> str:
    for index, block in enumerate(blocks):
        text = text.replace(f"@@CODE_BLOCK_{index}@@", block)
    return text
