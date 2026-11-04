import base64
from pathlib import Path

from modules.pdf_processor import PDFProcessingError, extract_pdf_text_from_bytes


TEXT_EXTENSIONS = {
    ".txt",
    ".md",
    ".csv",
    ".json",
    ".py",
    ".html",
    ".css",
    ".js",
    ".log",
}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
PDF_EXTENSIONS = {".pdf"}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_TEXT_CHARS = 2500


def prepare_chat_attachment(file_storage, vision_enabled: bool = False) -> dict:
    if not file_storage or not getattr(file_storage, "filename", ""):
        return {"prompt_context": "", "display_note": "", "images": [], "pdf_document": None}

    filename = Path(file_storage.filename).name
    extension = Path(filename).suffix.lower()
    content = file_storage.read()
    file_storage.seek(0)

    if len(content) > MAX_UPLOAD_BYTES:
        raise ValueError("File terlalu besar. Maksimal 5 MB agar aplikasi tetap ringan.")

    if extension in TEXT_EXTENSIONS:
        text = _decode_text(content)
        excerpt = text[:MAX_TEXT_CHARS].strip()
        if not excerpt:
            raise ValueError("File teks kosong atau tidak bisa dibaca.")
        return {
            "prompt_context": f"\n\nIsi file terlampir ({filename}, dipotong agar ringan):\n{excerpt}",
            "display_note": f"[File teks: {filename}]",
            "images": [],
            "pdf_document": None,
        }

    if extension in PDF_EXTENSIONS:
        try:
            pdf_document = extract_pdf_text_from_bytes(content, filename)
        except PDFProcessingError:
            raise
        return {
            "prompt_context": "",
            "display_note": f"[PDF terbaca: {filename}, {pdf_document['page_count']} halaman, {len(pdf_document['chunks'])} chunk]",
            "images": [],
            "pdf_document": pdf_document,
        }

    if extension in IMAGE_EXTENSIONS:
        if vision_enabled:
            encoded = base64.b64encode(content).decode("ascii")
            return {
                "prompt_context": (
                    f"\n\nAdmin mengupload gambar ({filename}). "
                    "Baca gambar dengan teliti: identifikasi teks, angka, tabel, diagram, soal, kode, atau objek penting. "
                    "Jika gambar berisi soal, kerjakan berdasarkan isi gambar. "
                    "Jika tulisan buram/tidak terbaca, sebutkan bagian yang tidak jelas dan minta Admin mengirim gambar lebih jelas atau mengetik ulang. "
                    "Jangan menebak detail kecil yang tidak terlihat."
                ),
                "display_note": f"[Gambar terbaca oleh vision model: {filename}]",
                "images": [encoded],
                "pdf_document": None,
            }
        return {
            "prompt_context": (
                f"\n\nAdmin mengupload gambar ({filename}), tetapi vision model lokal belum dikonfigurasi. "
                "Jelaskan dengan ramah bahwa untuk membaca gambar Admin perlu mengisi OLLAMA_VISION_MODEL dan menarik model vision lokal, "
                "atau mengetik isi gambar agar bisa dibantu dengan akurat."
            ),
            "display_note": f"[Gambar: {filename} - vision model belum aktif]",
            "images": [],
            "pdf_document": None,
        }

    raise ValueError("Format file belum didukung. Gunakan .pdf, .txt, .md, .csv, .json, .py, .html, .css, .js, .log, .png, .jpg, .jpeg, atau .webp.")


def _decode_text(content: bytes) -> str:
    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    return content.decode("utf-8", errors="replace")
