"""Application factory + exception mapping.

Domain errors are translated to HTTP status codes here, in one place, so the
service and parser layers can stay framework-agnostic.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.core.config import get_settings
from app.core.errors import (
    FileTooLarge,
    ParseError,
    UnsupportedContentType,
)
from app.core.logging import configure_logging
from app.schemas.extraction import ErrorResponse


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description="Turn PDF and DOCX files into structured JSON.",
    )
    app.include_router(router)
    _register_error_handlers(app)
    return app


def _error(status: int, error: str, detail: str) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content=ErrorResponse(error=error, detail=detail).model_dump(),
    )


def _register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(UnsupportedContentType)
    async def _unsupported(_: Request, exc: UnsupportedContentType) -> JSONResponse:
        return _error(415, "unsupported_media_type", str(exc))

    @app.exception_handler(FileTooLarge)
    async def _too_large(_: Request, exc: FileTooLarge) -> JSONResponse:
        return _error(413, "payload_too_large", str(exc))

    @app.exception_handler(ParseError)
    async def _parse(_: Request, exc: ParseError) -> JSONResponse:
        return _error(422, "unprocessable_document", str(exc))


app = create_app()
