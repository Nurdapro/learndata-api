from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.core.exceptions import NotFoundError, ConflictError, BusinessRuleError
from app.database import db, get_course_by_id, get_lecture_by_id, get_practice_by_id, get_student_by_id, get_enrollment_by_id, get_submissions_for_enrollment
from app.schemas.models import CourseCreate, CourseOut, LectureCreate, LectureOut, PracticeCreate, PracticeOut

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=list[CourseOut])
def list_courses(skip: int = Query(0, ge=0), limit: int | None = Query(None, ge=1)) -> list[CourseOut]:
    items = db.courses
    result = items[skip:limit and skip + limit]
    return [CourseOut(**c.__dict__) for c in result]


@router.post("", status_code=201, response_model=CourseOut)
def create_course(payload: CourseCreate) -> CourseOut:
    course = type("Course", (), {"id": db.next_id("course"), "title": payload.title, "description": payload.description, "status": "draft"})()
    db.courses.append(course)
    return CourseOut(id=course.id, title=course.title, description=course.description, status=course.status)


@router.get("/{course_id}", response_model=CourseOut)
def get_course(course_id: int) -> CourseOut:
    course = get_course_by_id(course_id)
    if course is None:
        raise NotFoundError(f"Course {course_id} not found")
    return CourseOut(id=course.id, title=course.title, description=course.description, status=course.status)


@router.get("/{course_id}/lectures", response_model=list[LectureOut])
def list_lectures(course_id: int) -> list[LectureOut]:
    if get_course_by_id(course_id) is None:
        raise NotFoundError(f"Course {course_id} not found")
    lectures = [l for l in db.lectures if l.course_id == course_id]
    return [LectureOut(id=l.id, course_id=l.course_id, title=l.title, content=l.content, status=l.status) for l in lectures]


@router.post("/{course_id}/lectures", status_code=201, response_model=LectureOut)
def create_lecture(course_id: int, payload: LectureCreate) -> LectureOut:
    if get_course_by_id(course_id) is None:
        raise NotFoundError(f"Course {course_id} not found")
    lecture = type("Lecture", (), {"id": db.next_id("lecture"), "course_id": course_id, "title": payload.title, "content": payload.content, "status": "draft"})()
    db.lectures.append(lecture)
    return LectureOut(id=lecture.id, course_id=lecture.course_id, title=lecture.title, content=lecture.content, status=lecture.status)


@router.get("/{course_id}/practices", response_model=list[PracticeOut])
def list_practices(course_id: int) -> list[PracticeOut]:
    if get_course_by_id(course_id) is None:
        raise NotFoundError(f"Course {course_id} not found")
    practices = [p for p in db.practices if p.course_id == course_id]
    return [PracticeOut(id=p.id, course_id=p.course_id, title=p.title, description=p.description, lecture_id=p.lecture_id, max_points=p.max_points, status=p.status) for p in practices]


@router.post("/{course_id}/practices", status_code=201, response_model=PracticeOut)
def create_practice(course_id: int, payload: PracticeCreate) -> PracticeOut:
    if get_course_by_id(course_id) is None:
        raise NotFoundError(f"Course {course_id} not found")
    if payload.lecture_id is not None and get_lecture_by_id(course_id, payload.lecture_id) is None:
        raise NotFoundError(f"Lecture {payload.lecture_id} not found")
    practice = type("Practice", (), {"id": db.next_id("practice"), "course_id": course_id, "title": payload.title, "description": payload.description, "lecture_id": payload.lecture_id, "max_points": payload.max_points, "status": "draft"})()
    db.practices.append(practice)
    return PracticeOut(id=practice.id, course_id=practice.course_id, title=practice.title, description=practice.description, lecture_id=practice.lecture_id, max_points=practice.max_points, status=practice.status)


@router.post("/{course_id}/publish")
def publish_course(course_id: int) -> dict[str, str]:
    course = get_course_by_id(course_id)
    if course is None:
        raise NotFoundError(f"Course {course_id} not found")
    course.status = "published"
    return {"status": course.status, "course_id": course_id}
