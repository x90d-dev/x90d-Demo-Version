import re

try:
    from sympy import simplify, sympify
except ImportError:  # pragma: no cover - dependency is installed in normal setup
    simplify = None
    sympify = None


def normalize_math_answer(text: str) -> str:
    value = (text or "").lower().strip()
    value = value.replace("^", "**").replace(",", ".")
    if "=" in value:
        value = value.split("=")[-1]

    numeric_candidates = re.findall(
        r"[-+]?\d+(?:\.\d+)?(?:\s*(?:\*\*|/|\+|\-|\*)\s*[-+]?\d+(?:\.\d+)?)*",
        value,
    )
    if numeric_candidates:
        return numeric_candidates[0].replace(" ", "")

    value = re.sub(r"(jawaban|hasil|nilai|maka|adalah)", " ", value)
    value = re.sub(r"\b(x|y)\s*", " ", value)
    value = re.sub(r"[^0-9a-zA-Z\.\+\-\*/\(\)]", " ", value)
    parts = [part for part in value.split() if part]
    return parts[-1] if parts else ""


def compare_math_answers(user_answer: str, correct_answer: str) -> bool:
    user = normalize_math_answer(user_answer)
    correct = normalize_math_answer(correct_answer)
    if not user or not correct:
        return False
    if user == correct:
        return True

    if simplify and sympify:
        try:
            return simplify(sympify(user) - sympify(correct)) == 0
        except Exception:
            pass

    try:
        return abs(float(user) - float(correct)) < 1e-9
    except ValueError:
        return False
