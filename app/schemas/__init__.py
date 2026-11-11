from __future__ import annotations

from pydantic import BaseModel, Field


class CourseBase(BaseModel):
    title: str = Field(..., min_length=2)
    description: str | None = None


class CourseCreate(CourseBase):
    pass


class CourseOut(CourseBase):
    id: int
    status: str = "draft"


class LectureBase(BaseModel):
    title: str = Field(..., min_length=2)
    content: str = Field(..., min_length=20)


class LectureCreate(LectureBase):
    pass


class LectureOut(LectureBase):
    id: int
    course_id: int
    status: str = "draft"


class PracticeBase(BaseModel):
    title: str = Field(..., min_length=2)
    description: str = Field(..., min_length=5)
    max_points: int = Field(default=10, ge=1)


class PracticeCreate(PracticeBase):
    lecture_id: int | None = None


class PracticeOut(PracticeBase):
    id: int
    course_id: int
    lecture_id: int | None = None
    status: str = "draft"


class StudentBase(BaseModel):
    name: str = Field(..., min_length=2)


class StudentCreate(StudentBase):
    pass


class StudentOut(StudentBase):
    id: int


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
