from datetime import date

from modules.chat_manager import build_chat_prompt
from modules.current_facts import build_current_fact_context


def test_current_fact_context_president_indonesia_2026():
    context = build_current_fact_context("siapa presiden indonesia 2026", today=date(2026, 5, 4))

    assert "Prabowo Subianto" in context
    assert "Joko Widodo" in context
    assert "bukan presiden pada 2026" in context


def test_chat_prompt_includes_indonesia_president_guard():
    prompt = build_chat_prompt("siapa presiden indonesia 2026", "general")

    assert "FAKTA TERKINI TERVERIFIKASI LOKAL" in prompt
    assert "Prabowo Subianto" in prompt
    assert "Jangan menjawab Jokowi" in prompt


def test_current_fact_context_finance_minister():
    context = build_current_fact_context("siapa menteri keuangan indonesia saat ini", today=date(2026, 5, 4))

    assert "Purbaya Yudhi Sadewa" in context
    assert "Sri Mulyani" in context


def test_current_fact_context_world_university_ranking():
    context = build_current_fact_context("carikan top 10 universitas dunia", today=date(2026, 5, 4))

    assert "QS World University Rankings 2026" in context
    assert "THE World University Rankings 2026" in context
