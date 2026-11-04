_CURRENT_PDF = None


def set_current_pdf(document: dict | None) -> None:
    global _CURRENT_PDF
    _CURRENT_PDF = document


def get_current_pdf() -> dict | None:
    return _CURRENT_PDF


def clear_current_pdf() -> None:
    set_current_pdf(None)
