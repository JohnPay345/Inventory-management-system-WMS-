from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from domain.exceptions import (
  AlreadyExistsError,
  BusinessRuleViolationError,
  DomainError,
  IsNoneError,
  LoginFailedError,
  NotFoundError,
)

ERROR_STATUS_MAP = {
  NotFoundError: status.HTTP_404_NOT_FOUND,
  AlreadyExistsError: status.HTTP_409_CONFLICT,
  BusinessRuleViolationError: status.HTTP_422_UNPROCESSABLE_CONTENT,
  IsNoneError: status.HTTP_409_CONFLICT,
  LoginFailedError: status.HTTP_400_BAD_REQUEST,
}


def register_exception_handlers(app: FastAPI) -> None:

  @app.exception_handler(DomainError)
  async def global_domain_exception_handler(request: Request, exc: DomainError):
    http_status = status.HTTP_400_BAD_REQUEST
    error_code = exc.__class__.__name__

    for error_class, status_code in ERROR_STATUS_MAP.items():
      if isinstance(exc, error_class):
        http_status = status_code
        entity_name = getattr(exc, "entity_name", "")
        error_code = f"{entity_name}{error_class.__name__}"
        break

    return JSONResponse(
      status_code=http_status,
      content={
        "error_code": error_code,
        "detail": str(exc),
      },
    )
