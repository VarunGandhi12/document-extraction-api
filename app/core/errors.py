"""Domain exceptions.

Kept free of any web framework so the parser/service layers stay transport
agnostic. `app.main` maps these to HTTP responses.
"""

from __future__ import annotations


class ExtractionError(Exception):
    """Base class for anything this service raises deliberately."""


class UnsupportedContentType(ExtractionError):
    def __init__(self, content_type: str) -> None:
        self.content_type = content_type
        super().__init__(f"Unsupported content type: {content_type!r}")


class ParseError(ExtractionError):
    """Raised when a file matches a known type but cannot be parsed."""


class FileTooLarge(ExtractionError):
    def __init__(self, size: int, limit: int) -> None:
        self.size = size
        self.limit = limit
        super().__init__(f"File is {size} bytes; limit is {limit} bytes.")
