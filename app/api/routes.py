"""HTTP surface. Thin: it validates the upload, delegates to the service, and
maps the result to a response model. No business logic lives here.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile

from app.api.deps import get_extraction_service
from app.core.config import get_settings
from app.schemas.extraction import ExtractionResult, HealthResponse
from app.services.extraction_service import ExtractionService

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["ops"])
def health() -> HealthResponse:
    """Liveness/readiness probe. Cheap and dependency-free."""
    return HealthResponse(version=get_settings().version)


@router.post(
    "/v1/extract",
    response_model=ExtractionResult,
    tags=["extraction"],
    summary="Extract structured content from a PDF or DOCX file",
)
async def extract(
    service: Annotated[ExtractionService, Depends(get_extraction_service)],
    file: Annotated[UploadFile, File(description="A PDF or DOCX document.")],
) -> ExtractionResult:
    data = await file.read()
    return service.extract(
        data=data,
        content_type=file.content_type or "application/octet-stream",
        filename=file.filename or "upload",
    )
