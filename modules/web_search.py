import base64
import html
import os
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import parse_qs, quote_plus, unquote, urlparse

import requests

from modules.trusted_search import build_trusted_search_result


SEARCH_ENGINES = [
    ("bing_rss", "https://www.bing.com/search?format=rss&q={query}"),
    ("duckduckgo", "https://duckduckgo.com/html/?q={query}"),
    ("bing", "https://www.bing.com/search?q={query}"),
]
USER_AGENT = "Mozilla/5.0 CoreChiperAgent/1.0 (+local personal assistant)"


class DuckDuckGoHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.results = []
        self._in_result_link = False
        self._in_snippet = False
        self._current_link = ""
        self._current_title = []
        self._current_snippet = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        class_name = attrs_dict.get("class", "")
        if tag == "a" and "result__a" in class_name:
            self._in_result_link = True
            self._current_link = attrs_dict.get("href", "")
            self._current_title = []
        elif tag in {"a", "div"} and "result__snippet" in class_name:
            self._in_snippet = True
            self._current_snippet = []

    def handle_data(self, data):
        if self._in_result_link:
            self._current_title.append(data)
        elif self._in_snippet:
            self._current_snippet.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._in_result_link:
            self._in_result_link = False
            title = _clean_text(" ".join(self._current_title))
            url = _normalize_duckduckgo_url(self._current_link)
            if title and url:
                self.results.append({"title": title, "url": url, "snippet": ""})
        elif tag in {"a", "div"} and self._in_snippet:
            self._in_snippet = False
            snippet = _clean_text(" ".join(self._current_snippet))
            if snippet and self.results:
                self.results[-1]["snippet"] = snippet


class BingHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.results = []
        self._in_result = False
        self._depth = 0
        self._in_h2 = False
        self._in_title = False
        self._in_snippet = False
        self._current_link = ""
        self._current_title = []
        self._current_snippet = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        class_name = attrs_dict.get("class", "")
        if tag == "li" and "b_algo" in class_name:
            self._in_result = True
            self._depth = 1
            self._in_h2 = False
            self._current_link = ""
            self._current_title = []
            self._current_snippet = []
            return

        if not self._in_result:
            return

        self._depth += 1
        if tag == "h2":
            self._in_h2 = True
        if tag == "a" and self._in_h2 and not self._current_link:
            href = attrs_dict.get("href", "")
            if href.startswith("http"):
                self._current_link = _normalize_bing_url(href)
                self._in_title = True
        elif tag == "p":
            self._in_snippet = True

    def handle_data(self, data):
        if self._in_title:
            self._current_title.append(data)
        elif self._in_snippet:
            self._current_snippet.append(data)

    def handle_endtag(self, tag):
        if self._in_h2 and tag == "h2":
            self._in_h2 = False
        if self._in_title and tag == "a":
            self._in_title = False
        if self._in_snippet and tag == "p":
            self._in_snippet = False
        if not self._in_result:
            return

        self._depth -= 1
        if self._depth <= 0:
            self._in_result = False
            title = _clean_text(" ".join(self._current_title))
            snippet = _clean_text(" ".join(self._current_snippet))
            if title and self._current_link:
                self.results.append({"title": title, "url": self._current_link, "snippet": snippet})


class WebPageTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self._skip_depth = 0
        self._interesting_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript", "svg", "nav", "footer"}:
            self._skip_depth += 1
        if tag in {"article", "main", "p", "li", "h1", "h2", "h3", "td"}:
            self._interesting_depth += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript", "svg", "nav", "footer"} and self._skip_depth:
            self._skip_depth -= 1
        if tag in {"article", "main", "p", "li", "h1", "h2", "h3", "td"} and self._interesting_depth:
            self._interesting_depth -= 1

    def handle_data(self, data):
        if self._skip_depth:
            return
        text = _clean_text(data)
        if len(text) >= 35 or self._interesting_depth:
            self.parts.append(text)

    def get_text(self) -> str:
        return _clean_text(" ".join(self.parts))


def should_auto_web_search(message: str) -> bool:
    text = (message or "").lower()
    keywords = [
        "terbaru",
        "hari ini",
        "tahun ini",
        "ranking",
        "peringkat",
        "top ",
        "top 10",
        "berita",
        "harga",
        "jadwal",
        "rilis",
        "update",
        "saat ini",
        "sekarang",
        "2025",
        "2026",
        "terkini",
        "real time",
        "daftar",
        "universitas",
        "presiden",
        "menteri",
        "ceo",
    ]
    return any(keyword in text for keyword in keywords)


def search_web(query: str, max_results: int = 5, timeout: int | None = None) -> dict:
    clean_query = (query or "").strip()
    if not clean_query:
        return {"ok": False, "query": clean_query, "results": [], "error": "Query kosong."}

    trusted_result = build_trusted_search_result(clean_query)
    if trusted_result:
        return trusted_result

    safe_limit = max(1, min(int(max_results or 5), 8))
    safe_timeout = timeout or _env_int("WEB_SEARCH_TIMEOUT", 10)
    last_error = ""
    low_confidence_candidate = None
    for search_query in build_search_queries(clean_query):
        for engine, url_template in SEARCH_ENGINES:
            url = url_template.format(query=quote_plus(search_query[:240]))
            try:
                response = requests.get(
                    url,
                    headers={
                        "User-Agent": USER_AGENT,
                        "Accept": "text/html,application/xhtml+xml,application/xml,application/rss+xml",
                        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                    },
                    timeout=safe_timeout,
                )
                response.raise_for_status()
            except requests.exceptions.Timeout:
                last_error = "Web search timeout. Coba ulangi atau ringkas query."
                continue
            except requests.exceptions.RequestException as exc:
                last_error = f"Web search {engine} gagal: {str(exc)[:120]}"
                continue

            raw_results = parse_search_results(response.text, engine=engine)[: max(safe_limit * 4, 12)]
            if raw_results and low_confidence_candidate is None:
                low_confidence_candidate = (engine, search_query, raw_results[:safe_limit])
            results = rank_search_results(raw_results, search_query)[:safe_limit]
            if not results:
                last_error = f"Web search {engine} tidak menemukan hasil relevan untuk query: {search_query}"
                continue

            if _env_bool("WEB_SEARCH_FETCH_PAGES", True):
                enrich_search_results(results, timeout=max(3, min(safe_timeout, 8)))
            return {
                "ok": True,
                "query": clean_query,
                "query_used": search_query,
                "results": results,
                "engine": engine,
                "error": "",
            }

    if low_confidence_candidate:
        engine, search_query, results = low_confidence_candidate
        if _env_bool("WEB_SEARCH_FETCH_PAGES", True):
            enrich_search_results(results, timeout=max(3, min(safe_timeout, 8)))
        return {
            "ok": True,
            "query": clean_query,
            "query_used": search_query,
            "results": results,
            "engine": engine,
            "low_confidence": True,
            "error": "Hasil search ditemukan, tetapi relevansinya perlu dicek.",
        }

    return {"ok": False, "query": clean_query, "results": [], "engine": "", "error": last_error or "Web search gagal. Periksa koneksi internet."}


def parse_search_results(html_text: str, engine: str = "duckduckgo") -> list[dict]:
    if engine == "bing_rss":
        raw_items = parse_bing_rss_results(html_text)
    else:
        parser = BingHTMLParser() if engine == "bing" else DuckDuckGoHTMLParser()
        parser.feed(html_text or "")
        raw_items = parser.results

    seen = set()
    results = []
    for item in raw_items:
        url = _normalize_bing_url(item.get("url", ""))
        if not url or url in seen or _is_blocked_result_url(url):
            continue
        seen.add(url)
        results.append(
            {
                "title": item.get("title", "")[:140],
                "url": url,
                "snippet": item.get("snippet", "")[:260],
            }
        )
    return results


def parse_bing_rss_results(xml_text: str) -> list[dict]:
    try:
        root = ET.fromstring(xml_text or "")
    except ET.ParseError:
        return _parse_rss_items_with_regex(xml_text)

    results = []
    for item in root.findall(".//item"):
        title = _clean_text(item.findtext("title", default=""))
        link = _clean_text(item.findtext("link", default=""))
        snippet = _strip_html(item.findtext("description", default=""))
        if title and link:
            results.append({"title": title, "url": link, "snippet": snippet})
    return results


def _parse_rss_items_with_regex(xml_text: str) -> list[dict]:
    results = []
    for match in re.finditer(r"<item\b.*?</item>", xml_text or "", flags=re.IGNORECASE | re.DOTALL):
        item_text = match.group(0)
        title = _strip_html(_first_xml_tag(item_text, "title"))
        link = _clean_text(_first_xml_tag(item_text, "link"))
        snippet = _strip_html(_first_xml_tag(item_text, "description"))
        if title and link:
            results.append({"title": title, "url": link, "snippet": snippet})
    return results


def _first_xml_tag(text: str, tag: str) -> str:
    match = re.search(rf"<{tag}\b[^>]*>(.*?)</{tag}>", text or "", flags=re.IGNORECASE | re.DOTALL)
    return html.unescape(match.group(1).strip()) if match else ""


def _strip_html(value: str) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", value or "")
    return _clean_text(without_tags)


def build_search_queries(query: str) -> list[str]:
    clean_query = (query or "").strip()
    lowered = clean_query.lower()
    variants = []

    if ("universitas" in lowered or "university" in lowered or "universities" in lowered) and (
        "china" in lowered or "tiongkok" in lowered
    ):
        variants.append("China university rankings 2026 QS Times Higher Education")
        variants.append("best universities in China 2026 ranking")

    if ("presiden" in lowered or "president" in lowered) and "indonesia" in lowered:
        variants.append("Prabowo Subianto Presiden Republik Indonesia 2024 2029")
        variants.append("Prabowo Gibran Presiden Wakil Presiden Indonesia 2024 2029")
        variants.append("site:presidenri.go.id Prabowo Subianto Presiden Republik Indonesia")
        variants.append("site:setkab.go.id Prabowo Subianto Presiden 2024 2029")

    if ("menteri keuangan" in lowered or "menkeu" in lowered or "finance minister" in lowered) and (
        "indonesia" in lowered or "ri" in lowered or "sekarang" in lowered or "saat ini" in lowered
    ):
        variants.append("Menteri Keuangan Indonesia saat ini Kementerian Keuangan")
        variants.append("site:kemenkeu.go.id Menteri Keuangan Indonesia Purbaya Yudhi Sadewa 2026")
        variants.append("site:djpb.kemenkeu.go.id Menteri Keuangan Purbaya Yudhi Sadewa")

    translated = clean_query
    replacements = {
        "universitas": "university",
        "peringkat": "ranking",
        "terbaru": "latest",
        "tiongkok": "China",
    }
    for source, target in replacements.items():
        translated = re.sub(source, target, translated, flags=re.IGNORECASE)
    if translated != clean_query:
        variants.append(f"{translated} ranking latest")

    variants.append(clean_query)
    seen = set()
    unique = []
    for item in variants:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique


def rank_search_results(results: list[dict], query: str) -> list[dict]:
    query_tokens = _expanded_search_tokens(query)
    if not query_tokens:
        return results

    required_score = 2 if len(query_tokens) >= 3 else 1
    if {"ranking", "rankings", "peringkat", "university", "universities", "universitas"}.intersection(query_tokens):
        required_score = 3

    scored = []
    for index, item in enumerate(results):
        haystack = " ".join(
            [
                item.get("title", ""),
                item.get("url", ""),
                item.get("snippet", ""),
            ]
        ).lower()
        result_tokens = _search_tokens(haystack)
        score = len(query_tokens.intersection(result_tokens))
        host = urlparse(item.get("url", "")).netloc.lower()
        if any(trusted in host for trusted in _trusted_domains_for_query(query)):
            score += 5
        if any(blocked in host for blocked in _low_quality_domains_for_query(query)):
            score -= 5
        if score >= required_score:
            scored.append((score, -index, item))

    if not scored:
        return []
    scored.sort(key=lambda entry: (entry[0], entry[1]), reverse=True)
    return [item for _, _, item in scored]


def format_web_context(search_result: dict) -> str:
    if not search_result.get("ok"):
        return (
            "WEB SEARCH DIMINTA TAPI GAGAL.\n"
            f"Error: {search_result.get('error', 'Web search gagal.')}\n"
            "Aturan wajib: jika pertanyaan adalah konsep stabil, definisi, materi pelajaran, coding umum, matematika, atau penjelasan teknis dasar, tetap jawab langsung dari pengetahuan umum dan konteks pemeriksaan. "
            "Jangan menjawab 'saya tidak bisa menemukan hasil' untuk konsep stabil. "
            "Jika pertanyaan benar-benar membutuhkan data terbaru, baru katakan bahwa data terbaru belum bisa dipastikan dan sarankan cek sumber resmi."
        )

    lines = [
        "WEB SEARCH AKTIF - KONTEKS TERBARU.",
        "Aturan wajib: jawab data terbaru hanya berdasarkan sumber di bawah ini. Jika sumber tidak cukup, katakan hasil web belum cukup. Jangan memakai ingatan lama yang bertentangan dengan sumber.",
        f"Query Admin: {search_result.get('query', '')}",
        f"Query web yang dipakai: {search_result.get('query_used', search_result.get('query', ''))}",
        "Sumber:",
    ]
    if search_result.get("low_confidence"):
        lines.append("Catatan: hasil search ditemukan, tetapi relevansinya perlu dicek ulang. Utamakan sumber resmi/terpercaya di daftar ini.")
    for index, item in enumerate(search_result.get("results", []), start=1):
        page_text = item.get("page_text", "")
        page_line = f"\n   Isi halaman ringkas: {page_text}" if page_text else ""
        lines.append(
            f"{index}. {item.get('title', 'Tanpa judul')}\n"
            f"   Link: {item.get('url', '')}\n"
            f"   Cuplikan: {item.get('snippet', '')}"
            f"{page_line}"
        )
    return "\n".join(lines)


def enrich_search_results(results: list[dict], timeout: int = 6) -> None:
    max_pages = max(0, min(_env_int("WEB_SEARCH_FETCH_LIMIT", 2), 4))
    page_chars = max(200, min(_env_int("WEB_SEARCH_PAGE_CHARS", 900), 1800))
    if max_pages <= 0:
        return

    fetched = 0
    for item in results:
        if fetched >= max_pages:
            break
        url = item.get("url", "")
        if not _is_fetchable_url(url):
            continue
        page_text = fetch_page_text(url, timeout=timeout)
        if page_text:
            item["page_text"] = page_text[:page_chars]
            fetched += 1


def fetch_page_text(url: str, timeout: int = 6) -> str:
    try:
        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"},
            timeout=timeout,
            allow_redirects=True,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return ""

    content_type = response.headers.get("Content-Type", "").lower()
    if "html" not in content_type and "text" not in content_type:
        return ""

    parser = WebPageTextParser()
    try:
        parser.feed(response.text[:250000])
    except Exception:
        return ""
    return parser.get_text()


def _normalize_duckduckgo_url(url: str) -> str:
    if not url:
        return ""
    decoded = html.unescape(url)
    if decoded.startswith("//duckduckgo.com/l/"):
        decoded = "https:" + decoded
    parsed = urlparse(decoded)
    query = parse_qs(parsed.query)
    if "uddg" in query and query["uddg"]:
        return unquote(query["uddg"][0])
    return decoded


def _normalize_bing_url(url: str) -> str:
    decoded = html.unescape(url or "")
    parsed = urlparse(decoded)
    query = parse_qs(parsed.query)
    raw_target = query.get("u", [""])[0]
    if raw_target:
        target = _decode_bing_target(raw_target)
        if target:
            return target
    return decoded


def _decode_bing_target(value: str) -> str:
    raw = unquote(value or "")
    if raw.startswith("a1"):
        raw = raw[2:]
    padding = "=" * (-len(raw) % 4)
    try:
        decoded = base64.urlsafe_b64decode(raw + padding).decode("utf-8", errors="ignore")
    except Exception:
        return ""
    return decoded if decoded.startswith(("http://", "https://")) else ""


def _clean_text(value: str) -> str:
    text = html.unescape(value or "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _expanded_search_tokens(text: str) -> set[str]:
    tokens = _search_tokens(text)
    expanded = set(tokens)
    synonyms = {
        "universitas": {"university", "universities", "campus"},
        "university": {"universitas", "universities"},
        "universities": {"universitas", "university"},
        "peringkat": {"ranking", "rank", "rankings"},
        "ranking": {"peringkat", "rank", "rankings"},
        "rankings": {"ranking", "peringkat"},
        "china": {"chinese", "tiongkok"},
        "tiongkok": {"china", "chinese"},
    }
    for token in list(tokens):
        expanded.update(synonyms.get(token, set()))
    return expanded


def _search_tokens(text: str) -> set[str]:
    stopwords = {
        "apa", "yang", "dan", "atau", "untuk", "dari", "dalam", "dengan", "the", "and", "for",
        "top", "terbaru", "latest", "hari", "ini", "tahun", "daftar", "list", "best", "of",
    }
    tokens = {token for token in re.findall(r"[a-zA-Z0-9]+", (text or "").lower()) if len(token) > 2}
    return {token for token in tokens if token not in stopwords}


def _is_fetchable_url(url: str) -> bool:
    parsed = urlparse(url or "")
    if parsed.scheme not in {"http", "https"}:
        return False
    host = (parsed.netloc or "").lower()
    blocked_hosts = ["youtube.com", "youtu.be", "facebook.com", "instagram.com", "tiktok.com"]
    return not any(blocked in host for blocked in blocked_hosts)


def _is_blocked_result_url(url: str) -> bool:
    host = urlparse(url or "").netloc.lower()
    blocked_hosts = ["kaskus.co.id", "dictionary.cambridge.org", "zhihu.com", "baidu.com"]
    return any(blocked in host for blocked in blocked_hosts)


def _trusted_domains_for_query(query: str) -> list[str]:
    text = (query or "").lower()
    domains = []
    if ("presiden" in text or "president" in text) and "indonesia" in text:
        domains.extend(["presidenri.go.id", "setkab.go.id", "indonesia.go.id", "mpr.go.id", "kompas.com", "apnews.com", "dw.com"])
    if ("university" in text or "universitas" in text or "ranking" in text) and ("china" in text or "tiongkok" in text):
        domains.extend(["topuniversities.com", "timeshighereducation.com", "shanghairanking.com", "usnews.com"])
    return domains


def _low_quality_domains_for_query(query: str) -> list[str]:
    text = (query or "").lower()
    domains = ["dictionary.cambridge.org", "kaskus.co.id"]
    if "presiden" in text or "president" in text:
        domains.extend(["zhihu.com", "baidu.com", "reddit.com"])
    return domains


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}
