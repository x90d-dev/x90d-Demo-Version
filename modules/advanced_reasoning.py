import re

from modules.deep_check import build_deep_check_context

try:
    from sympy import Eq, Symbol, diff, integrate, solve, sympify
    from sympy.functions import cos, exp, log, sin, sqrt, tan
except ImportError:  # pragma: no cover
    Eq = None
    Symbol = None
    diff = None
    integrate = None
    solve = None
    sympify = None
    cos = exp = log = sin = sqrt = tan = None


ADVANCED_KEYWORDS = [
    "advanced",
    "sulit",
    "menjebak",
    "olimpiade",
    "buktikan",
    "pembuktian",
    "induksi",
    "limit",
    "integral",
    "turunan",
    "differential",
    "matriks",
    "determinan",
    "eigen",
    "vektor",
    "probabilitas",
    "kombinatorika",
    "logaritma",
    "trigonometri",
    "stoikiometri",
    "kesetimbangan",
    "termodinamika",
    "listrik",
    "momentum",
    "toefl",
    "structure",
]

MATH_KEYWORDS = [
    "persamaan",
    "fungsi",
    "limit",
    "integral",
    "turunan",
    "matriks",
    "determinan",
    "eigen",
    "vektor",
    "probabilitas",
    "kombinatorika",
    "logaritma",
    "trigonometri",
    "buktikan",
    "induksi",
]


def detect_difficulty(message: str) -> str:
    text = (message or "").lower()
    score = sum(1 for keyword in ADVANCED_KEYWORDS if keyword in text)
    if score >= 2 or _has_any(text, ["olimpiade", "advanced", "menjebak", "buktikan"]):
        return "advanced"
    if score == 1 or len(text) > 420:
        return "intermediate"
    return "basic"


def build_advanced_context(message: str, subject: str | None = None, question_type: str | None = None) -> str:
    text = (message or "").lower()
    if not text.strip():
        return ""

    sections = []
    notes = []
    difficulty = detect_difficulty(message)
    if difficulty in {"advanced", "intermediate"}:
        notes.append(
            "Mode telaah cermat: pecah masalah menjadi subbagian, cek premis, cek satuan/domain, lalu verifikasi jawaban akhir."
        )

    if subject == "matematika" or _has_any(text, MATH_KEYWORDS) or _looks_like_equation(text):
        notes.append(
            "Matematika advanced: tentukan variabel dan domain, pilih metode yang tepat, jangan lompat aljabar, dan cek hasil dengan substitusi/turunan/sifat fungsi."
        )
        symbolic_hint = build_symbolic_math_hint(message)
        if symbolic_hint:
            notes.append(symbolic_hint)

    if subject == "fisika" or _has_any(text, ["gaya", "energi", "momentum", "listrik", "medan", "gelombang", "newton"]):
        notes.append(
            "Fisika advanced: buat model situasi, ubah satuan ke SI, bedakan besaran vektor/skalar, lalu cek dimensi satuan pada jawaban."
        )

    if subject == "kimia" or _has_any(text, ["mol", "reaksi", "asam", "basa", "ph", "kesetimbangan", "stoikiometri"]):
        notes.append(
            "Kimia advanced: setarakan reaksi, tentukan mol/perbandingan koefisien, cek pereaksi pembatas, dan pastikan satuan konsentrasi benar."
        )

    if subject in {"bahasa_inggris", "toefl"} or _has_any(text, ["grammar", "toefl", "structure", "reading", "vocabulary"]):
        notes.append(
            "English/TOEFL: cari subject utama, verb utama, modifier, tense, parallelism, pronoun reference, dan elimination untuk pilihan yang tampak menjebak."
        )

    if question_type == "multiple_choice":
        notes.append(
            "Pilihan ganda: baca stem sebelum opsi, eliminasi opsi salah, waspadai kata ekstrem, lalu pilih jawaban paling sesuai dengan data soal."
        )

    if notes:
        compact = "\n".join(f"- {note}" for note in notes[:6])
        sections.append(f"Konteks advanced untuk meningkatkan ketelitian:\n{compact}")

    deep_check_context = build_deep_check_context(message)
    if deep_check_context:
        sections.append(deep_check_context)

    return "\n".join(sections)


def build_symbolic_math_hint(message: str) -> str:
    if not all([Eq, Symbol, diff, integrate, solve, sympify]):
        return ""

    equation_hint = _solve_simple_equation(message)
    if equation_hint:
        return equation_hint

    derivative_hint = _differentiate_simple_expression(message)
    if derivative_hint:
        return derivative_hint

    integral_hint = _integrate_simple_expression(message)
    if integral_hint:
        return integral_hint

    return ""


def _solve_simple_equation(message: str) -> str:
    match = re.search(r"([0-9a-zA-Z\s+\-*/().^]+)=([0-9a-zA-Z\s+\-*/().^]+)", message)
    if not match:
        return ""

    left = _parse_math_expr(match.group(1))
    right = _parse_math_expr(match.group(2))
    if left is None or right is None:
        return ""

    x = Symbol("x")
    try:
        solutions = solve(Eq(left, right), x)
    except Exception:
        return ""

    if not solutions:
        return ""

    joined = ", ".join(str(solution) for solution in solutions[:4])
    return f"Pengecekan SymPy: persamaan tersebut memiliki solusi x = {joined}. Tetap jelaskan langkah aljabarnya."


def _differentiate_simple_expression(message: str) -> str:
    text = message.lower()
    if "turunan" not in text and "derivative" not in text:
        return ""

    expr_text = _extract_after_keyword(message, ["turunan dari", "turunan", "derivative of", "derivative"])
    expr = _parse_math_expr(expr_text)
    if expr is None:
        return ""

    x = Symbol("x")
    try:
        result = diff(expr, x)
    except Exception:
        return ""

    return f"Pengecekan SymPy: turunan ekspresi sederhana adalah {result}. Jelaskan aturan turunannya."


def _integrate_simple_expression(message: str) -> str:
    text = message.lower()
    if "integral" not in text:
        return ""

    expr_text = _extract_after_keyword(message, ["integral dari", "integral"])
    expr_text = re.sub(r"\bdx\b", "", expr_text, flags=re.IGNORECASE).strip()
    expr = _parse_math_expr(expr_text)
    if expr is None:
        return ""

    x = Symbol("x")
    try:
        result = integrate(expr, x)
    except Exception:
        return ""

    return f"Pengecekan SymPy: integral tak tentu ekspresi sederhana adalah {result} + C. Jelaskan aturan integralnya."


def _extract_after_keyword(message: str, keywords: list[str]) -> str:
    lowered = message.lower()
    for keyword in keywords:
        index = lowered.find(keyword)
        if index >= 0:
            tail = message[index + len(keyword) :]
            return re.split(r"[\n?.!,;]", tail, maxsplit=1)[0].strip()
    return ""


def _parse_math_expr(expr_text: str):
    cleaned = (expr_text or "").strip().replace("^", "**")
    cleaned = re.sub(
        r"\b(selesaikan|tentukan|hitung|nilai|dari|adalah|berapa|persamaan|fungsi)\b",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"(\d)([a-zA-Z])", r"\1*\2", cleaned)
    cleaned = re.sub(r"([a-zA-Z])(\d)", r"\1*\2", cleaned)
    cleaned = cleaned.strip()
    if not cleaned or len(cleaned) > 120:
        return None
    if not re.fullmatch(r"[0-9a-zA-Z\s+\-*/().*]+", cleaned):
        return None

    x = Symbol("x")
    safe_names = {
        "x": x,
        "sin": sin,
        "cos": cos,
        "tan": tan,
        "sqrt": sqrt,
        "log": log,
        "exp": exp,
    }
    try:
        return sympify(cleaned, locals=safe_names)
    except Exception:
        return None


def _looks_like_equation(text: str) -> bool:
    return bool(re.search(r"\b[a-z]\b.*=.*\d|\d.*=.*\b[a-z]\b", text))


def _has_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)
