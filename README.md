# LearnData API

REST backend for **LearnData**, a learning platform with lecture materials and hands-on
practices. It ships with starter content for one combined course: **Data Wrangling and Visualization**.

Built with Python, FastAPI and Pydantic. All data lives in memory and resets on restart.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000/docs** (Swagger UI). On startup the app loads the seed data
(1 course, 13 lectures, 5 practices, 2 students). Set `LEARNDATA_SEED=0` to start empty.

Run the automated tests (optional, in addition to Swagger testing):

```bash
pytest
```

## Project structure

```
app/
├── main.py              # app creation, router registration, startup seeding
├── database.py          # in-memory tables + id counters
├── seed.py              # starter content (replace with your team's materials)
├─�� core/
│   ├── exceptions.py    # NotFoundError (404), ConflictError (409), BusinessRuleError (422)
│   ├── handlers.py      # turns every error into the same JSON shape
│   └── utils.py         # pagination, timestamps
├── schemas/             # Pydantic models: request validation + response shapes
├── services/            # ALL business logic (no FastAPI imports)
└── routers/             # thin HTTP layer: parse request -> call service -> return result
tests/                   # service-level tests + HTTP smoke tests
```

**Layering:** routers never contain business rules. They validate input with a schema,
call one service function and return the result. Services raise domain errors; one handler
converts them to HTTP responses.

## Data model

```
Course 1──* Lecture
Course 1──* Practice  *──0..1 Lecture   (optional prerequisite lecture)
Student 1──* Enrollment *──1 Course     (unique per student + course)
Enrollment 1──* Submission *──1 Practice
```

## The three main workflows

### 1. Course publishing (content lifecycle)
`draft → published → archived` for courses, lectures and practices.
- A lecture needs at least 20 characters of content to be published.
- A practice can only be published if its linked lecture is published.
- A course can only be published if it has at least one published lecture.
- A lecture cannot be archived while published practices depend on it.
- A course can only be deleted if nobody is enrolled (archive it instead).

### 2. Enrollment and lecture progress
- Enrollment is only open for published courses, once per student per course.
- Lectures must be completed **in order**; completing one twice is rejected.
- `GET /enrollments/{id}/progress` shows lecture/practice progress, the next lecture, and
  `blockers` (what still prevents course completion).

### 3. Practice submission, grading and course completion
- A student can submit only to published practices of their course, after completing the
  practice's prerequisite lecture.
- Each practice has `max_attempts`; a new attempt is blocked while the previous one is
  still waiting to be graded.
- Grading: score must be between 0 and the practice's `max_points`; a submission is graded once.
- `POST /enrollments/{id}/complete` requires all lectures completed, every practice graded,
  and a final score of at least **60%** (best attempt per practice counts). It stores
  `final_score` and a letter grade (A ≥ 90, B ≥ 80, C ≥ 70, D ≥ 60).
- `GET /courses/{id}/leaderboard` ranks learners by earned points.

## Endpoints

| Resource | Endpoints |
|---|---|
| **Courses** | `POST/GET /courses` · `GET/PATCH/DELETE /courses/{id}` · `POST /courses/{id}/publish` · `POST /courses/{id}/archive` · `GET /courses/{id}/leaderboard` |
| **Lectures** | `POST/GET /courses/{id}/lectures` · `GET/PATCH/DELETE /courses/{id}/lectures/{lid}` · `POST …/{lid}/publish` · `POST …/{lid}/archive` |
| **Practices** | `POST/GET /courses/{id}/practices` · `GET/PATCH/DELETE /courses/{id}/practices/{pid}` · `POST …/{pid}/publish` · `POST …/{pid}/archive` |
| **Students** | `POST/GET /students` · `GET/PATCH/DELETE /students/{id}` |
| **Enrollments** | `POST/GET /enrollments` · `GET/DELETE /enrollments/{id}` · `POST /enrollments/{id}/lectures/{lid}/complete` · `GET /enrollments/{id}/progress` · `POST /enrollments/{id}/complete` |
| **Submissions** | `POST/GET /enrollments/{id}/submissions` · `GET /submissions` · `GET /submissions/{id}` · `PATCH /submissions/{id}/grade` |

List endpoints support filters and pagination (`skip`, `limit`), e.g.
`GET /courses?tag=pandas&level=beginner`, `GET /courses/1/practices?difficulty=hard`,
`GET /submissions?status=submitted` (the grading queue).

## Error format

Every error returns the same JSON:

```json
{ "error": "conflict", "message": "Student is already enrolled in this course", "details": null }
```

| Status | `error` | Meaning |
|---|---|---|
| 404 | `not_found` | resource (or a resource referenced in the body) does not exist |
| 409 | `conflict` | valid request that clashes with current state (duplicates, wrong status, prerequisites, attempt limits) |
| 422 | `validation_error` | Pydantic validation failed; `details` lists each field |
| 422 | `business_rule_violation` | well-formed but breaks a domain rule (score above max, publishing without content) |

## Swagger test checklist

On fresh startup, course 1 has 13 lectures and 5 practices. Students 1 and 2 exist.
Use Try it out / Execute at /docs. Record IDs returned by create requests.

1. GET /courses and /courses/1/lectures: 200.
2. POST /enrollments with {"student_id":1,"course_id":1}: 201.
3. Repeat enrollment: 409. Use student_id 999: 404.
4. Complete lecture 2 before lecture 1: 409.
5. POST /enrollments/1/lectures/1/complete, then lecture 2: 200 each.
6. POST /enrollments/1/submissions with {"practice_id":1,"answer":"My results"}: 201.
7. Repeat submission before grading: 409.
8. PATCH /submissions/1/grade with {"score":99}: 422.
9. Grade with {"score":8,"feedback":"Good work"}: 200. Repeat: 409.
10. GET /enrollments/1/progress: 200 with remaining requirements.
11. POST /enrollments/1/complete: 409 until requirements are met.
12. Complete lectures 3-13; submit and grade practices 2-5 with 8 points each.
13. Complete course: 200, final_score 80, final_grade B.
14. GET /courses/1/leaderboard: 200. DELETE /enrollments/1: 409.
15. POST /courses with {"title":"ab"}: 422; GET /courses/999: 404.
16. Check all remaining CRUD and filter endpoints with disposable records,
    invalid input, and conflicting operations. Automated tests do not replace
    the assignment's manual Swagger requirement.

Lecture `files` and practice `dataset` contain local paths relative to the project
folder. The API stores these references; it does not provide a download endpoint.
Open the included materials locally. Answers and notebook URLs are stored for
manual grading; this backend does not execute student Python code.
Authentication and user roles are not implemented.

## Using your own materials

Edit `COURSE, LECTURES and PRACTICES` in `app/seed.py` (lecture text, topics, practice tasks, points) and
restart. Seed data goes through the same schemas and service rules as API requests, so
invalid content fails loudly at startup.

## Team workflow (Git)

```bash
git init
git add .
git commit -m "Initial LearnData API"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

A simple split for three people: one owns `courses/lectures/practices`, one owns
`students/enrollments/progress`, one owns `submissions/grading/tests/README`. Work on
separate branches and open pull requests so each member has visible commits.

## Fixes and verification

- Added lecture files to create/update/output schemas and storage.
- Corrected material paths to files included in this archive.
- Prevented changing a published practice prerequisite to a draft/archived lecture.
- Updated seed expectations and documentation for one combined course.
- Added startup, material-reference, lecture-files and prerequisite regression tests.

Python 3.14: `pytest -q` -> 26 passed. Default seeded application startup verified.
