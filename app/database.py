from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Course:
    id: int
    title: str
    description: str | None = None
    status: str = "draft"


@dataclass
class Lecture:
    id: int
    course_id: int
    title: str
    content: str
    status: str = "draft"


@dataclass
class Practice:
    id: int
    course_id: int
    title: str
    description: str
    lecture_id: int | None = None
    max_points: int = 10
    status: str = "draft"


@dataclass
class Student:
    id: int
    name: str


@dataclass
class Enrollment:
    id: int
    student_id: int
    course_id: int
    completed_lectures: list[int] = field(default_factory=list)
    final_score: float | None = None
    final_grade: str | None = None
    completed: bool = False


@dataclass
class Submission:
    id: int
    enrollment_id: int
    practice_id: int
    answer: str
    status: str = "submitted"
    score: int | None = None
    feedback: str | None = None


class Database:
    def __init__(self) -> None:
        self.courses: list[Course] = []
        self.lectures: list[Lecture] = []
        self.practices: list[Practice] = []
        self.students: list[Student] = []
        self.enrollments: list[Enrollment] = []
        self.submissions: list[Submission] = []
        self.counters = {
            "course": 1,
            "lecture": 1,
            "practice": 1,
            "student": 1,
            "enrollment": 1,
            "submission": 1,
        }

    def next_id(self, key: str) -> int:
        value = self.counters[key]
        self.counters[key] += 1
        return value

    def reset(self) -> None:
        self.courses = []
        self.lectures = []
        self.practices = []
        self.students = []
        self.enrollments = []
        self.submissions = []
        self.counters = {
            "course": 1,
            "lecture": 1,
            "practice": 1,
            "student": 1,
            "enrollment": 1,
            "submission": 1,
        }


db = Database()
