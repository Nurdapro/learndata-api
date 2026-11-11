from __future__ import annotations

from fastapi import APIRouter, Query

from app.core.exceptions import NotFoundError, ConflictError, BusinessRuleError
from app.database import db, get_course_by_id, get_student_by_id, get_enrollment_by_id, get_course_by_id
from app.schemas.models import EnrollmentCreate, EnrollmentOut

router = APIRouter(prefix="/enrollments", tags=["enrollments"])


@router.get("", response_model=list[EnrollmentOut])
def list_enrollments() -> list[EnrollmentOut]:
    return [EnrollmentOut(**e.__dict__) for e in db.enrollments]


@router.post("", status_code=201, response_model=EnrollmentOut)
def create_enrollment(payload: EnrollmentCreate) -> EnrollmentOut:
    student = get_student_by_id(payload.student_id)
    if student is None:
        raise NotFoundError(f"Student {payload.student_id} not found")
    course = get_course_by_id(payload.course_id)
    if course is None:
        raise NotFoundError(f"Course {payload.course_id} not found")
    if any(e.student_id == payload.student_id and e.course_id == payload.course_id for e in db.enrollments):
        raise ConflictError("Student is already enrolled in this course")
    enrollment = type("Enrollment", (), {"id": db.next_id("enrollment"), "student_id": payload.student_id, "course_id": payload.course_id, "completed_lectures": [], "final_score": None, "final_grade": None, "completed": False})()
    db.enrollments.append(enrollment)
    return EnrollmentOut(id=enrollment.id, student_id=enrollment.student_id, course_id=enrollment.course_id, completed_lectures=enrollment.completed_lectures, final_score=enrollment.final_score, final_grade=enrollment.final_grade, completed=enrollment.completed)


@router.get("/{enrollment_id}", response_model=EnrollmentOut)
def get_enrollment(enrollment_id: int) -> EnrollmentOut:
    enrollment = get_enrollment_by_id(enrollment_id)
    if enrollment is None:
        raise NotFoundError(f"Enrollment {enrollment_id} not found")
    return EnrollmentOut(id=enrollment.id, student_id=enrollment.student_id, course_id=enrollment.course_id, completed_lectures=enrollment.completed_lectures, final_score=enrollment.final_score, final_grade=enrollment.final_grade, completed=enrollment.completed)


@router.post("/{enrollment_id}/lectures/{lecture_id}/complete")
def complete_lecture(enrollment_id: int, lecture_id: int) -> dict[str, object]:
    enrollment = get_enrollment_by_id(enrollment_id)
    if enrollment is None:
        raise NotFoundError(f"Enrollment {enrollment_id} not found")
    course = get_course_by_id(enrollment.course_id)
    if course is None:
        raise NotFoundError(f"Course {enrollment.course_id} not found")
    course_lecture_ids = [l.id for l in db.lectures if l.course_id == course.id]
    if lecture_id not in course_lecture_ids:
        raise NotFoundError(f"Lecture {lecture_id} not found")
    completed = enrollment.completed_lectures
    if completed and lecture_id != sorted(completed)[-1] + 1 and lecture_id not in completed:
        raise ConflictError("Lectures must be completed in order")
    if lecture_id in completed:
        raise ConflictError("Lecture already completed")
    completed.append(lecture_id)
    enrollment.completed_lectures = sorted(completed)
    return {"enrollment_id": enrollment_id, "lecture_id": lecture_id, "completed_lectures": enrollment.completed_lectures}


@router.get("/{enrollment_id}/progress")
def progress(enrollment_id: int) -> dict[str, object]:
    enrollment = get_enrollment_by_id(enrollment_id)
    if enrollment is None:
        raise NotFoundError(f"Enrollment {enrollment_id} not found")
    course_lectures = sorted([l.id for l in db.lectures if l.course_id == enrollment.course_id])
    next_lecture = next((i for i in course_lectures if i not in enrollment.completed_lectures), None)
    return {
        "enrollment_id": enrollment.id,
        "course_id": enrollment.course_id,
        "completed_lectures": enrollment.completed_lectures,
        "next_lecture": next_lecture,
        "blockers": [] if len(enrollment.completed_lectures) == len(course_lectures) else ["complete remaining lectures"],
    }


@router.post("/{enrollment_id}/complete")
def complete_course(enrollment_id: int) -> dict[str, object]:
    enrollment = get_enrollment_by_id(enrollment_id)
    if enrollment is None:
        raise NotFoundError(f"Enrollment {enrollment_id} not found")
    course_lectures = [l.id for l in db.lectures if l.course_id == enrollment.course_id]
    if len(enrollment.completed_lectures) != len(course_lectures):
        raise BusinessRuleError("Enrollment cannot be completed until all lectures are done")
    practice_ids = [p.id for p in db.practices if p.course_id == enrollment.course_id]
    submissions = [s for s in db.submissions if s.enrollment_id == enrollment_id]
    if len(submissions) < len(practice_ids):
        raise BusinessRuleError("All practices must be submitted and graded")
    scores = [s.score for s in submissions if s.score is not None]
    if len(scores) < len(practice_ids):
        raise BusinessRuleError("All practices must be graded")
    score = sum(scores) / len(scores) if scores else 0
    enrollment.final_score = round(score, 2)
    enrollment.final_grade = "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "D" if score >= 60 else "F"
    enrollment.completed = True
    return {"enrollment_id": enrollment.id, "final_score": enrollment.final_score, "final_grade": enrollment.final_grade}
