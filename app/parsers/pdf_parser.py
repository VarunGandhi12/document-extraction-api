"""PDF parser backed by PyMuPDF (fitz).

PyMuPDF is fast and handles a wide range of real-world PDFs. We only ever read
text here — no rendering, no external calls.
"""

from __future__ import annotations

import fitz  # PyMuPDF

from app.core.errors import ParseError
from app.parsers.base import ParsedDocument


class PdfParser:
    content_types = frozenset({"application/pdf"})

    def parse(self, data: bytes) -> ParsedDocument:
        try:
            doc = fitz.open(stream=data, filetype="pdf")
        except Exception as exc:  # noqa: BLE001 — normalize any fitz failure
            raise ParseError(f"Could not open PDF: {exc}") from exc

        try:
            pages = [page.get_text("text") for page in doc]
            extra: dict[str, str] = {}
            title = doc.metadata.get("title") if doc.metadata else None
            if title:
                extra["title"] = title
            return ParsedDocument(
                text="\n".join(pages).strip(),
                page_count=doc.page_count,
                extra=extra,
            )
        finally:
            doc.close()
