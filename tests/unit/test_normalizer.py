"""Unit tests for the pure normalizer logic — the heart of the service."""

from __future__ import annotations

from app.schemas.extraction import EntityType
from app.services.normalizer import extract_entities, split_sections


def _entities_by_type(text: str) -> dict[EntityType, list[str]]:
    grouped: dict[EntityType, list[str]] = {}
    for e in extract_entities(text):
        grouped.setdefault(e.type, []).append(e.value)
    return grouped


def test_extracts_email_url_phone_date() -> None:
    text = "Reach me at a.b+tag@corp.co or https://a.co, +1 415 555 0132, on 2026-01-15."
    grouped = _entities_by_type(text)
    assert grouped[EntityType.EMAIL] == ["a.b+tag@corp.co"]
    assert grouped[EntityType.URL] == ["https://a.co"]
    assert grouped[EntityType.DATE] == ["2026-01-15"]
    assert any("415 555 0132" in p for p in grouped[EntityType.PHONE])


def test_entities_are_deduped_case_insensitively() -> None:
    text = "x@Y.com and x@y.com appear twice"
    emails = _entities_by_type(text)[EntityType.EMAIL]
    assert len(emails) == 1


def test_url_trailing_punctuation_is_trimmed() -> None:
    urls = _entities_by_type("See https://example.com/page.")[EntityType.URL]
    assert urls == ["https://example.com/page"]


def test_phone_confidence_reflects_digit_count() -> None:
    good = extract_entities("+1 415 555 0132")[0]
    assert good.type is EntityType.PHONE
    assert good.confidence == 0.8


def test_iso_date_is_not_also_reported_as_a_phone() -> None:
    # Regression: the phone pattern used to swallow the digits of "2026-01-15".
    grouped = _entities_by_type("Shipped services in 2026-01-15.")
    assert grouped.get(EntityType.PHONE) is None
    assert grouped[EntityType.DATE] == ["2026-01-15"]


def test_known_headings_split_even_when_lowercase() -> None:
    text = "objectives\nDeliver value.\nnotes\nAll good."
    sections = split_sections(text, headings=frozenset({"objectives", "notes"}))
    assert [s.heading for s in sections] == ["objectives", "notes"]


def test_sections_split_on_uppercase_headings() -> None:
    text = "EXPERIENCE\nDid things.\nEDUCATION\nStudied things."
    sections = split_sections(text)
    headings = [s.heading for s in sections]
    assert "EXPERIENCE" in headings
    assert "EDUCATION" in headings
    exp = next(s for s in sections if s.heading == "EXPERIENCE")
    assert exp.content == "Did things."
    assert exp.word_count == 2


def test_colon_suffixed_line_is_a_heading_but_sentence_is_not() -> None:
    sections = split_sections("Skills:\nPython, Go\nI shipped a service.")
    assert any(s.heading == "Skills" for s in sections)


def test_empty_text_yields_no_sections() -> None:
    assert split_sections("") == []
