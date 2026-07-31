"""Parser strategy interface.

Each concrete parser turns raw bytes of one file type into a `ParsedDocument`.
The service layer depends on this Protocol, never on a concrete parser — so
adding a new file type is a new class + a registry entry, nothing else changes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class ParsedDocument:
    """The internal, format-agnostic result of parsing a file.

    `text` is always clean, human-readable text — no internal markers leak out.
    A parser that *knows* which lines are headings (e.g. DOCX, from style names)
    reports them in `headings`; parsers that don't (e.g. PDF) leave it empty and
    the normalizer falls back to heuristics.
    """

    text: str
    page_count: int
    #: Exact heading lines the parser identified with certainty, if any.
    headings: frozenset[str] = frozenset()
    # Optional raw key/values a specific format exposes (e.g. PDF title). Kept
    # loose on purpose; the normalizer decides what, if anything, to use.
    extra: dict[str, str] = field(default_factory=dict)


@runtime_checkable
class Parser(Protocol):
    """A strategy for one family of content types."""

    #: Content types this parser handles, e.g. {"application/pdf"}.
    content_types: frozenset[str]

    def parse(self, data: bytes) -> ParsedDocument:
        """Parse raw file bytes. Raise `ParseError` on malformed input."""
        ...
