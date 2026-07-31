"""Maps a content type to the parser that handles it.

Single source of truth for "what file types do we support". The API's accepted
types and the OpenAPI docs both derive from this, so they can never drift.
"""

from __future__ import annotations

from app.core.errors import UnsupportedContentType
from app.parsers.base import Parser
from app.parsers.docx_parser import DocxParser
from app.parsers.pdf_parser import PdfParser


class ParserRegistry:
    def __init__(self, parsers: list[Parser] | None = None) -> None:
        default_parsers: list[Parser] = [PdfParser(), DocxParser()]
        self._parsers: list[Parser] = parsers if parsers is not None else default_parsers
        self._by_type: dict[str, Parser] = {
            ct: parser for parser in self._parsers for ct in parser.content_types
        }

    @property
    def supported_content_types(self) -> frozenset[str]:
        return frozenset(self._by_type)

    def get(self, content_type: str) -> Parser:
        try:
            return self._by_type[content_type]
        except KeyError:
            raise UnsupportedContentType(content_type) from None
