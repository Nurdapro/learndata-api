from __future__ import annotations

from fastapi import FastAPI

from app.core.exceptions import AppError, NotFoundError, ConflictError, BusinessRuleError
from app.core.handlers import handle_exception
from app.database import db, seed_database
from app.routers.courses import router as courses_router
from app.routers.enrollments import router as enrollments_router
from app.routers.students import router as students_router
from app.routers.submissions import router as submissions_router

app = FastAPI(title="LearnData API")

app.add_exception_handler(AppError, handle_exception)
app.add_exception_handler(NotFoundError, handle_exception)
app.add_exception_handler(ConflictError, handle_exception)
app.add_exception_handler(BusinessRuleError, handle_exception)

app.include_router(courses_router)
app.include_router(enrollments_router)
app.include_router(students_router)
app.include_router(submissions_router)


@app.on_event("startup")
def startup_event() -> None:
    seed_database()


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "LearnData API"}
