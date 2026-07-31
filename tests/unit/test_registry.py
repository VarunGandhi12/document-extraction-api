"""Unit tests for parser selection."""

from __future__ import annotations

import pytest

from app.core.errors import UnsupportedContentType
from app.parsers.docx_parser import DocxParser
from app.parsers.pdf_parser import PdfParser
from app.parsers.registry import ParserRegistry


def test_returns_pdf_parser_for_pdf() -> None:
    assert isinstance(ParserRegistry().get("application/pdf"), PdfParser)


def test_returns_docx_parser_for_docx() -> None:
    ct = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert isinstance(ParserRegistry().get(ct), DocxParser)


def test_unknown_type_raises() -> None:
    with pytest.raises(UnsupportedContentType):
        ParserRegistry().get("image/png")


def test_supported_types_reported() -> None:
    supported = ParserRegistry().supported_content_types
    assert "application/pdf" in supported
    assert len(supported) == 2
