from modules.trusted_search import build_trusted_search_result
from modules.web_search import search_web


def test_trusted_search_answers_finance_minister():
    result = build_trusted_search_result("siapa menteri keuangan indonesia saat ini")

    assert result["ok"] is True
    assert result["engine"] == "trusted-direct"
    assert "Purbaya Yudhi Sadewa" in result["results"][0]["page_text"]


def test_search_web_uses_trusted_direct_for_finance_minister():
    result = search_web("siapa menteri keuangan indonesia saat ini")

    assert result["ok"] is True
    assert result["engine"] == "trusted-direct"
    assert "kemenkeu" in result["results"][0]["url"]


def test_trusted_search_answers_world_top_universities():
    result = build_trusted_search_result("carikan top 10 universitas dunia")

    assert result["ok"] is True
    assert "QS World University Rankings 2026" in result["results"][0]["title"]
    assert "MIT" in result["results"][0]["page_text"]
    assert "University of Oxford" in result["results"][1]["page_text"]
