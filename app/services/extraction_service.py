"""Orchestrates the extraction pipeline: parse -> normalize -> assemble.

This is the seam the API depends on. It knows nothing about HTTP and nothing
about specific file formats — it wires the registry to the normalizer.
"""

from __future__ import annotations

from app.core.errors import FileTooLarge
from app.parsers.registry import ParserRegistry
from app.schemas.extraction import DocumentMetadata, ExtractionResult
from app.services import normalizer

_EXCERPT_CHARS = 500


class ExtractionService:
    def __init__(self, registry: ParserRegistry, max_bytes: int) -> None:
        self._registry = registry
        self._max_bytes = max_bytes

    def extract(self, *, data: bytes, content_type: str, filename: str) -> ExtractionResult:
        if len(data) > self._max_bytes:
            raise FileTooLarge(len(data), self._max_bytes)

        parser = self._registry.get(content_type)
        parsed = parser.parse(data)

        sections = normalizer.split_sections(parsed.text, parsed.headings)
        entities = normalizer.extract_entities(parsed.text)

        metadata = DocumentMetadata(
            filename=filename,
            content_type=content_type,
            page_count=parsed.page_count,
            word_count=len(parsed.text.split()),
            char_count=len(parsed.text),
        )

        return ExtractionResult(
            metadata=metadata,
            sections=sections,
            entities=entities,
            text_excerpt=parsed.text[:_EXCERPT_CHARS],
        )
