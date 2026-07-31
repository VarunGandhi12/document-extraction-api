"""Public API contracts for the extraction service.

These Pydantic models are the *only* shape the outside world sees. Keeping them
separate from the internal parser types means the wire format can stay stable
even if the parsing internals change.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class EntityType(StrEnum):
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"
    DATE = "date"


class Entity(BaseModel):
    """A single value pulled out of the document text."""

    type: EntityType
    value: str
    # Heuristic 0-1 score. Not ML — a transparent signal the caller can threshold on.
    confidence: float = Field(ge=0.0, le=1.0)


class Section(BaseModel):
    """A heading and the body text that follows it, until the next heading."""

    heading: str
    content: str = ""
    word_count: int = 0


class DocumentMetadata(BaseModel):
    filename: str
    content_type: str
    page_count: int = Field(ge=0)
    word_count: int = Field(ge=0)
    char_count: int = Field(ge=0)


class ExtractionResult(BaseModel):
    metadata: DocumentMetadata
    sections: list[Section]
    entities: list[Entity]
    text_excerpt: str = Field(
        description="First N characters of extracted text, for a quick sanity check.",
    )


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str


class ErrorResponse(BaseModel):
    error: str
    detail: str
