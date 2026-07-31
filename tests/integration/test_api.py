"""Integration tests: real HTTP through FastAPI, real parsers, generated files."""

from __future__ import annotations

from tests.conftest import DOCX_CT, PDF_CT


def test_health(client) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_extract_pdf_roundtrip(client, sample_pdf_bytes) -> None:
    resp = client.post(
        "/v1/extract",
        files={"file": ("sample.pdf", sample_pdf_bytes, PDF_CT)},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["metadata"]["page_count"] == 1
    assert body["metadata"]["word_count"] > 0
    emails = [e["value"] for e in body["entities"] if e["type"] == "email"]
    assert "jane.doe@example.com" in emails


def test_extract_docx_roundtrip(client, sample_docx_bytes) -> None:
    resp = client.post(
        "/v1/extract",
        files={"file": ("sample.docx", sample_docx_bytes, DOCX_CT)},
    )
    assert resp.status_code == 200
    body = resp.json()
    headings = [s["heading"] for s in body["sections"]]
    assert "Experience" in headings
    assert "Education" in headings


def test_unsupported_type_returns_415(client) -> None:
    resp = client.post(
        "/v1/extract",
        files={"file": ("x.png", b"\x89PNG\r\n", "image/png")},
    )
    assert resp.status_code == 415
    assert resp.json()["error"] == "unsupported_media_type"


def test_corrupt_pdf_returns_422(client) -> None:
    resp = client.post(
        "/v1/extract",
        files={"file": ("broken.pdf", b"not really a pdf", PDF_CT)},
    )
    assert resp.status_code == 422
    assert resp.json()["error"] == "unprocessable_document"
