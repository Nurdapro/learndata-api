from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse

from .exceptions import AppError, NotFoundError, ConflictError, BusinessRuleError


def handle_exception(request: Request, exc: AppError):
    error_map = {
        NotFoundError: (404, "not_found"),
        ConflictError: (409, "conflict"),
        BusinessRuleError: (422, "business_rule_violation"),
    }
    status_code, error_name = error_map.get(type(exc), (500, "internal_error"))
    payload = {"error": error_name, "message": exc.message, "details": exc.details}
    return JSONResponse(status_code=status_code, content=payload)
