from __future__ import annotations

from fastapi import APIRouter, Query

from app.core.exceptions import NotFoundError, ConflictError, BusinessRuleError
from app.database import db, get_course_by_id, get_enrollment_by_id, get_student_by_id, get_practice_by_id
from app.schemas.models import SubmissionCreate, SubmissionGrade, SubmissionOut

router = APIRouter(prefix="/students", tags=["students"])


@router.get("", response_model=list[dict])
def list_students() -> list[dict]:
    return [{"id": s.id, "name": s.name} for s in db.students]


@router.post("", status_code=201, response_model=dict)
def create_student(payload: dict) -> dict:
    name = payload.get("name")
    if not name or len(name.strip()) < 2:
        raise BusinessRuleError("Name must be at least 2 characters")
    student = type("Student", (), {"id": db.next_id("student"), "name": name.strip()})()
    db.students.append(student)
    return {"id": student.id, "name": student.name}
