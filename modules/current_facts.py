import re
from datetime import date


def build_current_fact_context(message: str, today: date | None = None) -> str:
    text = (message or "").lower()
    today = today or date.today()
    contexts = []

    if _asks_indonesia_president(text):
        requested_year = _extract_year(text) or today.year
        if 2024 <= requested_year <= 2029:
            contexts.append(
                "FAKTA TERKINI TERVERIFIKASI LOKAL:\n"
                "- Presiden Republik Indonesia untuk periode 2024-2029 adalah Prabowo Subianto.\n"
                "- Wakil Presiden Republik Indonesia untuk periode 2024-2029 adalah Gibran Rakabuming Raka.\n"
                "- Prabowo-Gibran dilantik pada 20 Oktober 2024.\n"
                "- Joko Widodo adalah presiden periode 2014-2024, bukan presiden pada 2026.\n"
                "Aturan wajib: jika Admin bertanya presiden Indonesia pada 2026, jawab Prabowo Subianto. Jangan menjawab Jokowi."
            )

    if _asks_indonesia_finance_minister(text):
        if today.year >= 2025:
            contexts.append(
                "FAKTA TERKINI TERVERIFIKASI LOKAL:\n"
                "- Menteri Keuangan Republik Indonesia saat ini adalah Purbaya Yudhi Sadewa.\n"
                "- Sri Mulyani Indrawati bukan Menteri Keuangan saat ini pada 2026.\n"
                "- Untuk jawaban terbaru, prioritaskan sumber Kementerian Keuangan, Setneg, atau sumber berita kredibel.\n"
                "Aturan wajib: jika Admin bertanya Menteri Keuangan Indonesia saat ini pada 2026, jawab Purbaya Yudhi Sadewa."
            )

    if _asks_world_university_ranking(text):
        contexts.append(
            "FAKTA RANKING TERVERIFIKASI LOKAL:\n"
            "- Ranking universitas dunia tergantung lembaga pemeringkat. Jangan mencampur QS dan THE tanpa menyebut lembaganya.\n"
            "- QS World University Rankings 2026 top 3: MIT, Imperial College London, Stanford University.\n"
            "- THE World University Rankings 2026 top 3: University of Oxford, MIT, Princeton University / University of Cambridge berbagi peringkat 3.\n"
            "Aturan wajib: jika Admin minta top 10 universitas dunia, sebutkan sumber ranking yang dipakai, misalnya QS 2026 atau THE 2026."
        )

    if contexts:
        return "\n\n".join(contexts)
    return ""


def _asks_indonesia_president(text: str) -> bool:
    return (
        _has_any(text, ["presiden", "president"])
        and _has_any(text, ["indonesia", "ri", "republik indonesia"])
    )


def _asks_indonesia_finance_minister(text: str) -> bool:
    return (
        _has_any(text, ["menteri keuangan", "menkeu", "finance minister"])
        and _has_any(text, ["indonesia", "ri", "republik indonesia", "saat ini", "sekarang"])
    )


def _asks_world_university_ranking(text: str) -> bool:
    return (
        _has_any(text, ["universitas", "university", "universities"])
        and _has_any(text, ["dunia", "world", "global"])
        and _has_any(text, ["top", "ranking", "peringkat", "terbaik"])
    )


def _extract_year(text: str) -> int | None:
    match = re.search(r"\b(20[0-9]{2})\b", text or "")
    if not match:
        return None
    return int(match.group(1))


def _has_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)
