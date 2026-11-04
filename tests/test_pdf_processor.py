import pytest

from modules.pdf_processor import (
    PDFProcessingError,
    build_pdf_context,
    chunk_document,
    extract_pdf_text_from_bytes,
    search_relevant_chunks,
)


fitz = pytest.importorskip("fitz")


def _pdf_bytes(text: str = "", blank: bool = False) -> bytes:
    document = fitz.open()
    page = document.new_page()
    if text and not blank:
        page.insert_text((72, 72), text)
    data = document.tobytes()
    document.close()
    return data


def test_extract_pdf_text_normal_pdf():
    data = _pdf_bytes("Judul Dokumen\nTujuan penelitian adalah memahami energi.")
    result = extract_pdf_text_from_bytes(data, "materi.pdf")

    assert result["filename"] == "materi.pdf"
    assert result["page_count"] == 1
    assert "Tujuan penelitian" in result["pages"][0]["text"]
    assert result["chunks"]


def test_extract_non_pdf_rejected():
    with pytest.raises(PDFProcessingError, match="berformat .pdf"):
        extract_pdf_text_from_bytes(b"hello", "catatan.txt")


def test_extract_blank_or_scanned_pdf_message():
    with pytest.raises(PDFProcessingError, match="OCR belum didukung"):
        extract_pdf_text_from_bytes(_pdf_bytes(blank=True), "scan.pdf")


def test_search_relevant_chunks_finds_answer_chunk():
    chunks = [
        {"chunk_id": 1, "page_numbers": [1], "text": "Bab energi membahas usaha dan daya."},
        {"chunk_id": 2, "page_numbers": [2], "text": "Kesimpulan dokumen adalah belajar bertahap."},
    ]
    relevant = search_relevant_chunks("Apa kesimpulan dokumen?", chunks, limit=1)
    assert relevant[0]["page_numbers"] == [2]


def test_build_pdf_context_for_missing_answer_instruction():
    document = {
        "filename": "materi.pdf",
        "page_count": 1,
        "chunks": [{"chunk_id": 1, "page_numbers": [1], "text": "Dokumen membahas energi."}],
    }
    context = build_pdf_context("Apa nama penulis?", document)
    assert "Jawab hanya berdasarkan teks PDF" in context
    assert "Jika informasi tidak ditemukan" in context


def test_build_pdf_context_summary_mode():
    document = {
        "filename": "materi.pdf",
        "page_count": 1,
        "chunks": [{"chunk_id": 1, "page_numbers": [1], "text": "Dokumen membahas energi dan usaha."}],
    }
    context = build_pdf_context("Ringkas PDF ini", document)
    assert "Mode PDF: ringkasan" in context
    assert "Ringkas tiap chunk" in context or "ringkasan tiap chunk" in context
