from io import BytesIO

import pytest
from werkzeug.datastructures import FileStorage

from modules.attachment_handler import prepare_chat_attachment


def _file(name: str, content: bytes) -> FileStorage:
    return FileStorage(stream=BytesIO(content), filename=name)


def test_prepare_text_attachment_reads_excerpt():
    result = prepare_chat_attachment(_file("catatan.txt", b"Materi persamaan linear"), vision_enabled=False)
    assert "Materi persamaan linear" in result["prompt_context"]
    assert "[File teks: catatan.txt]" == result["display_note"]
    assert result["images"] == []


def test_prepare_image_without_vision_gives_clear_context():
    result = prepare_chat_attachment(_file("soal.png", b"fakepng"), vision_enabled=False)
    assert "vision model lokal belum dikonfigurasi" in result["prompt_context"]
    assert result["images"] == []


def test_prepare_image_with_vision_encodes_image_and_instructs_careful_reading():
    result = prepare_chat_attachment(_file("soal.png", b"image-bytes"), vision_enabled=True)

    assert "Baca gambar dengan teliti" in result["prompt_context"]
    assert "Jangan menebak" in result["prompt_context"]
    assert result["images"]
    assert result["pdf_document"] is None


def test_prepare_unsupported_attachment_raises_error():
    with pytest.raises(ValueError):
        prepare_chat_attachment(_file("arsip.exe", b"x"), vision_enabled=False)


def test_prepare_non_pdf_extension_rejected_by_supported_list():
    with pytest.raises(ValueError):
        prepare_chat_attachment(_file("dokumen.docx", b"x"), vision_enabled=False)
