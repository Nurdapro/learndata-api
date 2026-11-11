from __future__ import annotations

from pydantic import BaseModel, Field


class CourseCreate(BaseModel):
    title: str = Field(..., min_length=2)
    description: str | None = None


class CourseOut(BaseModel):
    id: int
    title: str
    description: str | None = None
    status: str = "draft"


class LectureCreate(BaseModel):
    title: str = Field(..., min_length=2)
    content: str = Field(..., min_length=20)


class LectureOut(BaseModel):
    id: int
    course_id: int
    title: str
    content: str
    status: str = "draft"


class PracticeCreate(BaseModel):
    title: str = Field(..., min_length=2)
    description: str = Field(..., min_length=5)
    lecture_id: int | None = None
    max_points: int = Field(default=10, ge=1)


class PracticeOut(BaseModel):
    id: int
    course_id: int
    title: str
    description: str
    lecture_id: int | None = None
    max_points: int
    status: str = "draft"


class EnrollmentCreate(BaseModel):
    student_id: int
    course_id: int


class EnrollmentOut(BaseModel):
    id: int
    student_id: int
    course_id: int
    completed_lectures: list[int]
    final_score: float | None = None
    final_grade: str | None = None
    completed: bool = False


class SubmissionCreate(BaseModel):
    practice_id: int
    answer: str = Field(..., min_length=1)


class SubmissionGrade(BaseModel):
    score: int = Field(..., ge=0)
    feedback: str | None = None


class SubmissionOut(BaseModel):
    id: int
    enrollment_id: int
    practice_id: int
    answer: str
    status: str
    score: int | None = None
    feedback: str | None = None
