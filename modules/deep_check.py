import re
from fractions import Fraction

try:
    from sympy import Eq, Symbol, simplify, solve
except ImportError:  # pragma: no cover
    Eq = None
    Symbol = None
    simplify = None
    solve = None


CHANGE_WORDS = [
    "bertambah",
    "berkurang",
    "mendapat",
    "menerima",
    "memakai",
    "hilang",
    "diberi",
    "ditambah",
    "dikurangi",
]

TRANSFER_WORDS = ["memberi", "memberikan", "mentransfer", "memindahkan"]

FINAL_WORDS = [
    "setelah",
    "akhirnya",
    "jumlah akhir",
    "total akhir",
    "perbandingan menjadi",
    "rasio akhir",
]


def should_use_deep_check_mode(text: str) -> bool:
    lowered = (text or "").lower()
    if not lowered.strip():
        return False

    has_ratio = detect_ratio_problem(lowered)
    has_final_ratio = detect_final_ratio(lowered)
    has_total = detect_total_final(lowered)
    changes = count_changes(lowered)
    transfer = detect_transfer(lowered)
    has_final_marker = any(word in lowered for word in FINAL_WORDS)

    return bool(
        (has_ratio and has_final_marker)
        or (has_ratio and changes >= 1 and has_total)
        or (has_ratio and changes >= 2)
        or (has_ratio and has_final_ratio)
        or (transfer and has_ratio)
        or (has_total and has_final_ratio)
    )


def detect_ratio_problem(text: str) -> bool:
    return bool(re.search(r"\d+\s*:\s*\d+", text or "")) or "rasio" in (text or "").lower() or "perbandingan" in (text or "").lower()


def detect_final_ratio(text: str) -> bool:
    lowered = (text or "").lower()
    return bool(re.search(r"(rasio akhir|perbandingan akhir|perbandingan menjadi|rasio menjadi|menjadi)\s+\d+\s*:\s*\d+", lowered))


def detect_total_final(text: str) -> bool:
    lowered = (text or "").lower()
    return bool(re.search(r"(total akhir|jumlah akhir|jumlah keseluruhan|seluruhnya|totalnya)\D{0,40}(?:rp\s*)?\d", lowered))


def detect_transfer(text: str) -> bool:
    lowered = (text or "").lower()
    return any(word in lowered for word in TRANSFER_WORDS) and any(word in lowered for word in ["kepada", "ke ", "untuk"])


def count_changes(text: str) -> int:
    lowered = (text or "").lower()
    return sum(lowered.count(word) for word in CHANGE_WORDS) + sum(lowered.count(word) for word in TRANSFER_WORDS)


def estimate_problem_level(text: str) -> int:
    lowered = (text or "").lower()
    has_ratio = detect_ratio_problem(lowered)
    has_final_ratio = detect_final_ratio(lowered)
    has_total = detect_total_final(lowered)
    changes = count_changes(lowered)
    transfer = detect_transfer(lowered)
    parties = _estimate_party_count(lowered)

    if has_ratio and parties >= 3 and transfer and has_final_ratio and has_total:
        return 8
    if has_ratio and changes >= 1 and has_final_ratio and has_total:
        return 7
    if has_ratio and has_final_ratio:
        return 6
    if has_ratio and has_total:
        return 5
    if has_ratio and changes >= 2:
        return 4
    if has_ratio and changes >= 1:
        return 3
    if any(word in lowered for word in ["cerita", "setelah", "mula-mula", "akhirnya"]):
        return 2
    return 1


def analyze_deep_check(text: str) -> dict:
    clean_text = text or ""
    enabled = should_use_deep_check_mode(clean_text)
    analysis = {
        "enabled": enabled,
        "level": estimate_problem_level(clean_text),
        "reasons": _detect_reasons(clean_text),
        "initial_ratio": None,
        "final_ratio": None,
        "total_final": None,
        "changes": [],
        "initial_state": [],
        "final_state": [],
        "equations": [],
        "consistency": "not_checked",
        "contradictions": [],
        "solutions": [],
    }

    initial_ratio = parse_initial_ratio(clean_text)
    final_ratio = parse_final_ratio(clean_text)
    total_final = parse_total_final(clean_text)
    analysis["initial_ratio"] = initial_ratio
    analysis["final_ratio"] = final_ratio
    analysis["total_final"] = total_final

    if not enabled or not initial_ratio:
        return analysis

    changes = parse_changes(clean_text, initial_ratio["names"])
    analysis["changes"] = changes
    analysis.update(_build_symbolic_consistency(initial_ratio, final_ratio, total_final, changes))
    return analysis


def build_deep_check_context(text: str) -> str:
    analysis = analyze_deep_check(text)
    if not analysis["enabled"]:
        return ""

    lines = [
        "deep_check_mode: AKTIF",
        f"Level soal terdeteksi: {analysis['level']}",
        f"Alasan aktif: {', '.join(analysis['reasons']) or 'soal multi-syarat'}",
        "Aturan wajib: jangan pakai rasio awal untuk kondisi akhir setelah ada perubahan; cek semua syarat sebelum kesimpulan.",
    ]

    if analysis["initial_state"]:
        lines.append("Variabel dan kondisi awal:")
        lines.extend(f"- {item}" for item in analysis["initial_state"])

    if analysis["changes"]:
        lines.append("Perubahan terdeteksi:")
        lines.extend(f"- {change['description']}" for change in analysis["changes"])

    if analysis["final_state"]:
        lines.append("Kondisi akhir:")
        lines.extend(f"- {item}" for item in analysis["final_state"])

    if analysis["equations"]:
        lines.append("Persamaan yang harus dicek:")
        lines.extend(f"- {item}" for item in analysis["equations"])

    if analysis["solutions"]:
        lines.append("Hasil syarat terpisah:")
        lines.extend(f"- {item}" for item in analysis["solutions"])

    if analysis["contradictions"]:
        lines.append("Kontradiksi:")
        lines.extend(f"- {item}" for item in analysis["contradictions"])
        lines.append('Kesimpulan wajib jika kontradiksi valid: "Tidak ada solusi yang memenuhi semua syarat."')
    elif analysis["consistency"] == "consistent":
        lines.append("Validasi awal: syarat tampak konsisten. Tetap substitusi kembali sebelum jawaban akhir.")

    return "\n".join(lines)


def parse_initial_ratio(text: str) -> dict | None:
    pattern = re.compile(
        r"((?:\b[A-Za-z][A-Za-z0-9_]*\b\s*:\s*)+\b[A-Za-z][A-Za-z0-9_]*\b)\s*=\s*((?:\d+\s*:\s*)+\d+)",
        re.IGNORECASE,
    )
    match = pattern.search(text or "")
    if not match:
        return None

    names = [part.strip() for part in match.group(1).split(":")]
    values = [int(part.strip()) for part in match.group(2).split(":")]
    if len(names) != len(values) or len(names) < 2:
        return None
    return {"names": names, "values": values}


def parse_final_ratio(text: str) -> list[int] | None:
    pattern = re.compile(
        r"(?:rasio akhir|perbandingan akhir|perbandingan menjadi|rasio menjadi|menjadi)\s*((?:\d+\s*:\s*)+\d+)",
        re.IGNORECASE,
    )
    match = pattern.search(text or "")
    if not match:
        return None
    return [int(part.strip()) for part in match.group(1).split(":")]


def parse_total_final(text: str) -> int | None:
    pattern = re.compile(
        r"(?:total akhir|jumlah akhir|jumlah keseluruhan|seluruhnya|totalnya)\D{0,40}(?:rp\s*)?(\d[\d.,]*)",
        re.IGNORECASE,
    )
    match = pattern.search(text or "")
    return parse_amount(match.group(1)) if match else None


def parse_changes(text: str, names: list[str]) -> list[dict]:
    deltas = {name.lower(): 0 for name in names}
    changes = []

    for match in re.finditer(
        r"\b([A-Za-z][A-Za-z0-9_]*)\b\s+(?:memberi|memberikan|mentransfer|memindahkan)\s+(?:rp\s*)?(\d[\d.,]*)\s+(?:kepada|ke|untuk)\s+\b([A-Za-z][A-Za-z0-9_]*)\b",
        text or "",
        flags=re.IGNORECASE,
    ):
        giver, amount_text, receiver = match.group(1), match.group(2), match.group(3)
        amount = parse_amount(amount_text)
        if giver.lower() in deltas:
            deltas[giver.lower()] -= amount
        if receiver.lower() in deltas:
            deltas[receiver.lower()] += amount
        changes.append({
            "name": giver,
            "delta": -amount,
            "description": f"{giver} memberi {format_rupiah(amount)} kepada {receiver}: {giver} - {format_rupiah(amount)}, {receiver} + {format_rupiah(amount)}",
        })
        changes.append({
            "name": receiver,
            "delta": amount,
            "description": f"{receiver} menerima {format_rupiah(amount)} dari {giver}: {receiver} + {format_rupiah(amount)}",
        })

    positive_words = "bertambah|mendapat|menerima|diberi|ditambah"
    negative_words = "berkurang|memakai|dipakai|hilang|dikurangi|mengeluarkan"
    for match in re.finditer(
        rf"\b([A-Za-z][A-Za-z0-9_]*)\b\s+({positive_words}|{negative_words})\s+(?:rp\s*)?(\d[\d.,]*)",
        text or "",
        flags=re.IGNORECASE,
    ):
        name, word, amount_text = match.group(1), match.group(2).lower(), match.group(3)
        amount = parse_amount(amount_text)
        sign = -1 if re.fullmatch(negative_words, word) else 1
        if name.lower() in deltas:
            deltas[name.lower()] += sign * amount
        operator = "+" if sign > 0 else "-"
        changes.append({
            "name": name,
            "delta": sign * amount,
            "description": f"{name} {word} {format_rupiah(amount)}: {name} {operator} {format_rupiah(amount)}",
        })

    for change in changes:
        change["net_delta"] = deltas.get(change["name"].lower(), change["delta"])
    return changes


def parse_amount(text: str) -> int:
    value = (text or "0").strip().lower().replace("rp", "").replace(" ", "")
    value = value.strip(".,")
    if "," in value and "." in value:
        value = value.replace(".", "").replace(",", ".")
    elif "." in value and re.fullmatch(r"\d{1,3}(?:\.\d{3})+", value):
        value = value.replace(".", "")
    elif "," in value and re.fullmatch(r"\d{1,3}(?:,\d{3})+", value):
        value = value.replace(",", "")
    else:
        value = value.replace(",", ".")
    return int(float(value))


def format_rupiah(value) -> str:
    try:
        amount = int(value)
    except Exception:
        return str(value)
    return f"Rp{amount:,}".replace(",", ".")


def _build_symbolic_consistency(initial_ratio: dict, final_ratio: list[int] | None, total_final: int | None, changes: list[dict]) -> dict:
    if not all([Eq, Symbol, simplify, solve]):
        return {}

    x = Symbol("x")
    names = initial_ratio["names"]
    ratios = initial_ratio["values"]
    delta_map = {name.lower(): 0 for name in names}
    for change in changes:
        delta_map[change["name"].lower()] = delta_map.get(change["name"].lower(), 0) + change["delta"]

    initial_exprs = {name: ratios[index] * x for index, name in enumerate(names)}
    final_exprs = {name: initial_exprs[name] + delta_map.get(name.lower(), 0) for name in names}

    equations = []
    equation_items = []
    if total_final is not None:
        eq = Eq(sum(final_exprs.values()), total_final)
        equations.append(("Total akhir", eq))
        equation_items.append(f"Total akhir: {_expr_text(sum(final_exprs.values()))} = {format_rupiah(total_final)}")

    if final_ratio and len(final_ratio) == len(names):
        base_name = names[0]
        base_ratio = final_ratio[0]
        for index, name in enumerate(names[1:], start=1):
            eq = Eq(base_ratio * final_exprs[name], final_ratio[index] * final_exprs[base_name])
            equations.append((f"Rasio akhir {base_name}:{name}", eq))
            equation_items.append(
                f"Rasio akhir {base_name}:{name}: ({_expr_text(final_exprs[base_name])}) / ({_expr_text(final_exprs[name])}) = {base_ratio} / {final_ratio[index]}"
            )

    solutions = []
    individual_values = []
    for label, eq in equations:
        try:
            solved = solve(eq, x)
        except Exception:
            solved = []
        if solved:
            value = solved[0]
            individual_values.append((label, value))
            solutions.append(f"{label} menghasilkan x = {_format_value(value)}")

    contradictions = []
    consistency = "unknown"
    if len(equations) >= 2:
        try:
            combined = solve([eq for _, eq in equations], x)
        except Exception:
            combined = []
        if not combined:
            consistency = "inconsistent"
            if len(individual_values) >= 2:
                first_label, first_value = individual_values[0]
                for label, value in individual_values[1:]:
                    if simplify(first_value - value) != 0:
                        contradictions.append(
                            f"{first_label} memberi x = {_format_value(first_value)}, tetapi {label} memberi x = {_format_value(value)}."
                        )
        else:
            consistency = "consistent"
    elif equations:
        consistency = "partial"

    return {
        "initial_state": [f"{name} awal = {ratios[index]}x" for index, name in enumerate(names)],
        "final_state": [f"{name} akhir = {_expr_text(final_exprs[name])}" for name in names],
        "equations": equation_items,
        "solutions": solutions,
        "consistency": consistency,
        "contradictions": contradictions,
    }


def _detect_reasons(text: str) -> list[str]:
    lowered = (text or "").lower()
    reasons = []
    if detect_ratio_problem(lowered):
        reasons.append("rasio")
    if detect_final_ratio(lowered):
        reasons.append("rasio akhir")
    if detect_total_final(lowered):
        reasons.append("total akhir")
    if count_changes(lowered) >= 1:
        reasons.append("perubahan")
    if count_changes(lowered) >= 2:
        reasons.append("dua atau lebih perubahan")
    if detect_transfer(lowered):
        reasons.append("transfer")
    return reasons


def _estimate_party_count(text: str) -> int:
    ratio = parse_initial_ratio(text)
    return len(ratio["names"]) if ratio else 0


def _format_value(value) -> str:
    try:
        fraction = Fraction(str(value)).limit_denominator()
        if fraction.denominator == 1:
            return format_rupiah(fraction.numerator) if abs(fraction.numerator) >= 1000 else str(fraction.numerator)
        return f"{fraction.numerator}/{fraction.denominator}"
    except Exception:
        return str(value)


def _expr_text(expr) -> str:
    text = str(expr).replace("*", "")
    text = re.sub(r"(?<!^)-", "- ", text)
    text = text.replace("+ -", "- ")
    return text
