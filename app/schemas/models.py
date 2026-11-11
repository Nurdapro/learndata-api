from __future__ import annotations

from fastapi import APIRouter

from app.core.exceptions import NotFoundError, ConflictError, BusinessRuleError
from app.database import db, get_enrollment_by_id, get_practice_by_id
from app.schemas.models import SubmissionCreate, SubmissionGrade, SubmissionOut

router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.get("", response_model=list[SubmissionOut])
def list_submissions() -> list[SubmissionOut]:
    return [SubmissionOut(id=s.id, enrollment_id=s.enrollment_id, practice_id=s.practice_id, answer=s.answer, status=s.status, score=s.score, feedback=s.feedback) for s in db.submissions]


@router.get("/{submission_id}", response_model=SubmissionOut)
def get_submission(submission_id: int) -> SubmissionOut:
    submission = next((s for s in db.submissions if s.id == submission_id), None)
    if submission is None:
        raise NotFoundError(f"Submission {submission_id} not found")
    return SubmissionOut(id=submission.id, enrollment_id=submission.enrollment_id, practice_id=submission.practice_id, answer=submission.answer, status=submission.status, score=submission.score, feedback=submission.feedback)


@router.post("", status_code=201, response_model=SubmissionOut)
def create_submission(payload: SubmissionCreate) -> SubmissionOut:
    enrollment = next((e for e in db.enrollments if e.student_id == 1), None)
    if enrollment is None:
        raise NotFoundError("No enrollment found")
    practice = next((p for p in db.practices if p.id == payload.practice_id), None)
    if practice is None:
        raise NotFoundError(f"Practice {payload.practice_id} not found")
    if payload.practice_id not in [p.id for p in db.practices]:
        raise NotFoundError(f"Practice {payload.practice_id} not found")
    existing = next((s for s in db.submissions if s.enrollment_id == enrollment.id and s.practice_id == payload.practice_id and s.status == "submitted"), None)
    if existing is not None:
        raise ConflictError("A submission already exists for this practice")
    submission = type("Submission", (), {"id": db.next_id("submission"), "enrollment_id": enrollment.id, "practice_id": payload.practice_id, "answer": payload.answer, "status": "submitted", "score": None, "feedback": None})()
    db.submissions.append(submission)
    return SubmissionOut(id=submission.id, enrollment_id=submission.enrollment_id, practice_id=submission.practice_id, answer=submission.answer, status=submission.status, score=submission.score, feedback=submission.feedback)


@router.patch("/{submission_id}/grade", response_model=SubmissionOut)
def grade_submission(submission_id: int, payload: SubmissionGrade) -> SubmissionOut:
    submission = next((s for s in db.submissions if s.id == submission_id), None)
    if submission is None:
        raise NotFoundError(f"Submission {submission_id} not found")
    if submission.status == "graded":
        raise ConflictError("Submission has already been graded")
    relevant_practice = next((p for p in db.practices if p.id == submission.practice_id), None)
    if relevant_practice is None:
        raise NotFoundError(f"Practice {submission.practice_id} not found")
    if payload.score > relevant_practice.max_points:
        raise BusinessRuleError("Score above max_points for the practice")
    submission.score = payload.score
    submission.feedback = payload.feedback
    submission.status = "graded"
    return SubmissionOut(id=submission.id, enrollment_id=submission.enrollment_id, practice_id=submission.practice_id, answer=submission.answer, status=submission.status, score=submission.score, feedback=submission.feedback)
