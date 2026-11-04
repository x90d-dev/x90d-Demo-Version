from modules.web_search import (
    build_search_queries,
    fetch_page_text,
    format_web_context,
    parse_bing_rss_results,
    parse_search_results,
    rank_search_results,
    search_web,
    should_auto_web_search,
)


HTML_SAMPLE = """
<html>
  <body>
    <a class="result__a" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com%2Fa">Example Result</a>
    <a class="result__snippet">Snippet one about universities.</a>
    <a class="result__a" href="https://example.com/b">Second Result</a>
    <div class="result__snippet">Snippet two.</div>
  </body>
</html>
"""

BING_HTML_SAMPLE = """
<html>
  <body>
    <li class="b_algo">
      <h2><a href="https://example.com/bing">Bing Result</a></h2>
      <div class="b_caption"><p>Snippet from Bing result.</p></div>
    </li>
  </body>
</html>
"""

BING_RSS_SAMPLE = """
<rss version="2.0">
  <channel>
    <item>
      <title>QS World University Rankings 2026</title>
      <link>https://www.topuniversities.com/world-university-rankings</link>
      <description><![CDATA[Top universities ranking result with latest data.]]></description>
    </item>
  </channel>
</rss>
"""


def test_parse_search_results_extracts_title_url_snippet():
    results = parse_search_results(HTML_SAMPLE)
    assert len(results) == 2
    assert results[0]["title"] == "Example Result"
    assert results[0]["url"] == "https://example.com/a"
    assert "universities" in results[0]["snippet"]


def test_parse_search_results_extracts_bing_result():
    results = parse_search_results(BING_HTML_SAMPLE, engine="bing")
    assert len(results) == 1
    assert results[0]["title"] == "Bing Result"
    assert results[0]["url"] == "https://example.com/bing"
    assert "Bing result" in results[0]["snippet"]


def test_parse_search_results_extracts_bing_rss_result():
    results = parse_search_results(BING_RSS_SAMPLE, engine="bing_rss")
    assert len(results) == 1
    assert results[0]["title"] == "QS World University Rankings 2026"
    assert results[0]["url"] == "https://www.topuniversities.com/world-university-rankings"
    assert "latest data" in results[0]["snippet"]


def test_parse_bing_rss_results_regex_fallback():
    broken_xml = """
    <rss><channel><item>
      <title>Result &amp; Update</title>
      <link>https://example.com/update</link>
      <description>Snippet <b>penting</b></description>
    </item></channel>
    """
    results = parse_bing_rss_results(broken_xml)
    assert results[0]["title"] == "Result & Update"
    assert results[0]["url"] == "https://example.com/update"
    assert results[0]["snippet"] == "Snippet penting"


def test_should_auto_web_search_for_latest_ranking():
    assert should_auto_web_search("Top 10 universitas China terbaru") is True
    assert should_auto_web_search("Jelaskan persamaan linear") is False


def test_build_search_queries_expands_indonesian_university_ranking():
    queries = build_search_queries("top 10 universitas China terbaru 2026")
    assert queries[0] == "China university rankings 2026 QS Times Higher Education"
    assert any("university China" in query or "university china" in query.lower() for query in queries)


def test_build_search_queries_expands_indonesia_president():
    queries = build_search_queries("siapa presiden indonesia 2026")
    assert queries[0] == "Prabowo Subianto Presiden Republik Indonesia 2024 2029"
    assert any("site:presidenri.go.id" in query for query in queries)


def test_build_search_queries_expands_indonesia_finance_minister():
    queries = build_search_queries("siapa menteri keuangan indonesia saat ini")
    assert queries[0] == "Menteri Keuangan Indonesia saat ini Kementerian Keuangan"
    assert any("site:kemenkeu.go.id" in query for query in queries)


def test_rank_search_results_drops_irrelevant_results():
    results = [
        {"title": "TOP - Cambridge Dictionary", "url": "https://dictionary.cambridge.org/top", "snippet": ""},
        {"title": "China University Rankings 2026", "url": "https://example.com/ranking", "snippet": "Best universities in China."},
    ]
    ranked = rank_search_results(results, "China university rankings 2026")
    assert ranked[0]["title"] == "China University Rankings 2026"
    assert all("Cambridge" not in item["title"] for item in ranked)


def test_parse_search_results_decodes_bing_redirect():
    html = """
    <html><body><li class="b_algo">
      <h2><a href="https://www.bing.com/ck/a?u=a1aHR0cHM6Ly9leGFtcGxlLmNvbS9wcmVzaWRlbg">Presiden Indonesia</a></h2>
      <p>Prabowo Subianto Presiden Indonesia</p>
    </li></body></html>
    """
    results = parse_search_results(html, engine="bing")
    assert results[0]["url"] == "https://example.com/presiden"


def test_format_web_context_includes_sources():
    context = format_web_context(
        {
            "ok": True,
            "query": "test",
            "results": [
                {"title": "A", "url": "https://example.com", "snippet": "Cuplikan"}
            ],
            "error": "",
        }
    )
    assert "WEB SEARCH AKTIF" in context
    assert "https://example.com" in context


def test_format_web_context_failure_allows_general_fallback():
    context = format_web_context({"ok": False, "error": "timeout", "results": []})
    assert "WEB SEARCH DIMINTA TAPI GAGAL" in context
    assert "konsep stabil" in context
    assert "Jangan menjawab 'saya tidak bisa menemukan hasil'" in context


def test_search_web_returns_low_confidence_fallback(monkeypatch):
    class FakeResponse:
        text = BING_RSS_SAMPLE

        def raise_for_status(self):
            return None

    monkeypatch.setenv("WEB_SEARCH_FETCH_PAGES", "false")
    monkeypatch.setattr("modules.web_search.requests.get", lambda *_args, **_kwargs: FakeResponse())

    result = search_web("cuaca mars besok", max_results=2)

    assert result["ok"] is True
    assert result["low_confidence"] is True
    assert result["results"][0]["url"] == "https://www.topuniversities.com/world-university-rankings"


def test_fetch_page_text_extracts_readable_html(monkeypatch):
    class FakeResponse:
        headers = {"Content-Type": "text/html"}
        text = """
        <html><head><style>.x{}</style></head>
        <body><nav>Menu</nav><main><h1>Judul Berita</h1><p>Ini isi halaman terbaru yang cukup panjang untuk dibaca oleh parser web search.</p></main></body></html>
        """

        def raise_for_status(self):
            return None

    def fake_get(*_args, **_kwargs):
        return FakeResponse()

    monkeypatch.setattr("modules.web_search.requests.get", fake_get)
    text = fetch_page_text("https://example.com")

    assert "Judul Berita" in text
    assert "isi halaman terbaru" in text
    assert "Menu" not in text
