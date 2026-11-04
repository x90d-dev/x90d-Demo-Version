import re
from pathlib import Path


MAX_PDF_BYTES = 5 * 1024 * 1024
DEFAULT_CHUNK_CHARS = 1200
DEFAULT_OVERLAP_CHARS = 160


class PDFProcessingError(ValueError):
    pass


def extract_pdf_text_from_bytes(content: bytes, filename: str = "document.pdf") -> dict:
    filename = Path(filename or "document.pdf").name
    _validate_pdf_bytes(content, filename)

    try:
        import fitz
    except ImportError as exc:  # pragma: no cover - exercised when dependency missing
        raise PDFProcessingError("Dependency PyMuPDF belum terinstall. Jalankan: pip install -r requirements.txt") from exc

    try:
        document = fitz.open(stream=content, filetype="pdf")
    except Exception as exc:
        raise PDFProcessingError("File PDF tidak bisa dibuka atau rusak.") from exc

    pages = []
    try:
        for index, page in enumerate(document, start=1):
            text = clean_pdf_text(page.get_text("text") or "")
            pages.append({"page_number": index, "text": text})
    finally:
        document.close()

    readable_pages = [page for page in pages if page["text"]]
    if not readable_pages:
        raise PDFProcessingError("Teks PDF tidak bisa diekstrak. PDF mungkin hasil scan dan OCR belum didukung.")

    chunks = chunk_document(readable_pages)
    return {
        "filename": filename,
        "page_count": len(pages),
        "pages": readable_pages,
        "chunks": chunks,
        "full_text_length": sum(len(page["text"]) for page in readable_pages),
    }


def clean_pdf_text(text: str) -> str:
    value = (text or "").replace("\r\n", "\n").replace("\r", "\n").replace("\u00a0", " ")
    lines = []
    blank_seen = False
    for raw_line in value.split("\n"):
        line = re.sub(r"[ \t]+", " ", raw_line).strip()
        if not line:
            if not blank_seen and lines:
                lines.append("")
            blank_seen = True
            continue
        lines.append(line)
        blank_seen = False
    cleaned = "\n".join(lines).strip()
    return re.sub(r"\n{3,}", "\n\n", cleaned)


def chunk_document(pages: list[dict], max_chars: int = DEFAULT_CHUNK_CHARS, overlap_chars: int = DEFAULT_OVERLAP_CHARS) -> list[dict]:
    chunks = []
    current_parts = []
    current_pages = set()

    def flush():
        if not current_parts:
            return
        text = "\n\n".join(part for part in current_parts if part).strip()
        if not text:
            return
        chunks.append(
            {
                "chunk_id": len(chunks) + 1,
                "page_numbers": sorted(current_pages),
                "text": text,
            }
        )

    for page in pages:
        page_number = int(page["page_number"])
        paragraphs = _split_into_paragraphs(page.get("text", ""))
        for paragraph in paragraphs:
            for piece in _split_long_text(paragraph, max_chars):
                candidate_length = len("\n\n".join(current_parts + [piece]))
                if current_parts and candidate_length > max_chars:
                    previous_text = "\n\n".join(current_parts)
                    flush()
                    overlap = previous_text[-overlap_chars:].strip()
                    current_parts.clear()
                    current_pages.clear()
                    if overlap:
                        current_parts.append(overlap)
                current_parts.append(piece)
                current_pages.add(page_number)

    flush()
    return chunks


def search_relevant_chunks(question: str, chunks: list[dict], limit: int = 4) -> list[dict]:
    query_tokens = _tokens(question)
    if not query_tokens:
        return chunks[:limit]

    scored = []
    for chunk in chunks:
        chunk_tokens = _tokens(chunk.get("text", ""))
        score = len(query_tokens.intersection(chunk_tokens))
        if score > 0:
            scored.append((score, chunk))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _, chunk in scored[: max(1, int(limit or 4))]]


def is_pdf_summary_request(message: str) -> bool:
    text = (message or "").lower()
    return any(keyword in text for keyword in ["ringkas", "rangkuman", "summary", "summarize", "intisari", "poin penting"])


def should_use_pdf_context(message: str) -> bool:
    text = (message or "").lower()
    return any(keyword in text for keyword in ["pdf", "dokumen", "file", "halaman", "teks", "ringkas", "rangkuman", "isi dokumen"])


def build_pdf_context(message: str, pdf_document: dict, max_chunks: int = 4) -> str:
    chunks = pdf_document.get("chunks", [])
    if not chunks:
        return "Konteks PDF: teks PDF tidak tersedia."

    summary_mode = is_pdf_summary_request(message)
    selected_chunks = chunks[:max_chunks] if summary_mode else search_relevant_chunks(message, chunks, limit=max_chunks)

    instruction = (
        "Jawab hanya berdasarkan teks PDF yang diberikan. Jangan menambahkan informasi dari luar dokumen. "
        "Jika informasi tidak ditemukan, katakan bahwa informasi tidak ditemukan dalam PDF. "
        "Jika mengutip isi, sebutkan halaman jika tersedia."
    )
    if summary_mode:
        instruction += " Buat ringkasan tiap chunk terlebih dahulu, lalu ringkasan gabungan."

    if not selected_chunks:
        return (
            f"Konteks PDF: {instruction} "
            "Tidak ada chunk yang relevan dengan pertanyaan. "
            "Jika informasi tidak ditemukan, jawab: Informasi tidak ditemukan dalam PDF."
        )

    lines = [
        "Konteks PDF digital:",
        f"Nama file: {pdf_document.get('filename', 'document.pdf')}",
        f"Jumlah halaman terbaca: {pdf_document.get('page_count', '-')}",
        f"Mode PDF: {'ringkasan' if summary_mode else 'tanya jawab'}",
        "Status PDF: teks digital berhasil diekstrak dan siap dibaca.",
        f"Instruksi PDF: {instruction}",
    ]
    for chunk in selected_chunks:
        pages = ", ".join(str(page) for page in chunk.get("page_numbers", []))
        lines.append(f"\nChunk {chunk.get('chunk_id')} (halaman {pages}):\n{chunk.get('text', '')[:1400]}")
    return "\n".join(lines)


def _validate_pdf_bytes(content: bytes, filename: str) -> None:
    if Path(filename).suffix.lower() != ".pdf":
        raise PDFProcessingError("File harus berformat .pdf.")
    if not content:
        raise PDFProcessingError("File PDF kosong.")
    if len(content) > MAX_PDF_BYTES:
        raise PDFProcessingError("File PDF terlalu besar. Maksimal 5 MB agar proses tetap ringan.")
    if not content.lstrip().startswith(b"%PDF"):
        raise PDFProcessingError("File tidak terlihat seperti PDF valid.")


def _split_into_paragraphs(text: str) -> list[str]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text or "") if part.strip()]
    if paragraphs:
        return paragraphs
    return [line.strip() for line in (text or "").split("\n") if line.strip()]


def _split_long_text(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    pieces = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        pieces.append(text[start:end].strip())
        start = end
    return [piece for piece in pieces if piece]


def _tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-zA-Z0-9]+", (text or "").lower()) if len(token) > 2}
