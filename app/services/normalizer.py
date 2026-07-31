"""Turns raw extracted text into structured sections and entities.

Pure functions, no I/O — which makes this the easiest and most valuable part of
the codebase to unit-test exhaustively.
"""

from __future__ import annotations

import re

from app.schemas.extraction import Entity, EntityType, Section

_EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
_URL_RE = re.compile(r"\bhttps?://[^\s)>\]]+", re.IGNORECASE)
_PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)")
_DATE_RE = re.compile(
    r"\b("
    r"\d{4}-\d{2}-\d{2}"  # 2026-01-31
    r"|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}"  # Jan 2026
    r"|\d{1,2}/\d{1,2}/\d{2,4}"  # 31/01/2026
    r")\b",
    re.IGNORECASE,
)

# A short, capitalized or ALL-CAPS line with no sentence punctuation reads as a
# heading. Combined with the explicit DOCX marker, this covers most documents.
_MAX_HEADING_WORDS = 8


def _looks_like_heading(line: str, known_headings: frozenset[str]) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped in known_headings:
        return True
    if len(stripped.split()) > _MAX_HEADING_WORDS:
        return False
    if stripped.endswith((".", ",", ";", ":")):
        return stripped.endswith(":")  # "Experience:" is a heading; a sentence isn't
    return stripped.isupper() or stripped.istitle()


def split_sections(text: str, headings: frozenset[str] = frozenset()) -> list[Section]:
    """Group lines under the heading that precedes them.

    `headings` are lines a parser identified as headings with certainty; any
    other line is judged by heuristics.
    """
    sections: list[Section] = []
    current_heading = "Document"
    buffer: list[str] = []

    def flush() -> None:
        body = "\n".join(buffer).strip()
        if body or current_heading != "Document":
            sections.append(
                Section(
                    heading=current_heading,
                    content=body,
                    word_count=len(body.split()),
                )
            )

    for raw in text.splitlines():
        line = raw.strip()
        if _looks_like_heading(line, headings):
            flush()
            current_heading = line.rstrip(":")
            buffer = []
        elif line:
            buffer.append(line)

    flush()
    return sections


def _dedupe_preserving_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for v in values:
        key = v.lower()
        if key not in seen:
            seen.add(key)
            out.append(v)
    return out


def extract_entities(text: str) -> list[Entity]:
    """Pull emails, URLs, phone numbers and dates out of free text.

    Confidence is a transparent heuristic, not a model score: precise patterns
    (email, URL) score higher than fuzzy ones (phone).
    """
    entities: list[Entity] = []

    for value in _dedupe_preserving_order(_EMAIL_RE.findall(text)):
        entities.append(Entity(type=EntityType.EMAIL, value=value, confidence=0.99))

    for value in _dedupe_preserving_order(_URL_RE.findall(text)):
        entities.append(Entity(type=EntityType.URL, value=value.rstrip(".,"), confidence=0.95))

    # A run of digits/dashes can match both a phone and a date (e.g. 2026-01-15).
    # Dates are the more specific pattern, so anything that is fully a date is not
    # a phone number.
    phones = [
        re.sub(r"\s{2,}", " ", p).strip()
        for p in _PHONE_RE.findall(text)
        if not _DATE_RE.fullmatch(p.strip())
    ]
    for value in _dedupe_preserving_order(phones):
        digits = sum(c.isdigit() for c in value)
        # 10-13 digits is a plausible international number; further out is noisier.
        confidence = 0.8 if 10 <= digits <= 13 else 0.5
        entities.append(Entity(type=EntityType.PHONE, value=value, confidence=confidence))

    for value in _dedupe_preserving_order(_DATE_RE.findall(text)):
        entities.append(Entity(type=EntityType.DATE, value=value, confidence=0.7))

    return entities
