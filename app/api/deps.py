"""FastAPI dependency wiring.

Constructing the service here (rather than at import time) keeps it swappable in
tests via `app.dependency_overrides`.
"""

from __future__ import annotations

from functools import lru_cache

from app.core.config import get_settings
from app.parsers.registry import ParserRegistry
from app.services.extraction_service import ExtractionService


@lru_cache
def get_extraction_service() -> ExtractionService:
    settings = get_settings()
    return ExtractionService(
        registry=ParserRegistry(),
        max_bytes=settings.max_upload_bytes,
    )
