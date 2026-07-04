# Smart File Processing API

A production-grade REST API for uploading, validating, and persisting CSV employee data. Built with FastAPI following Clean Architecture principles — strict layer separation, row-level validation with partial success, structured JSON logging, and per-request tracing.

---

## Architecture

```
app/
├── api/          # HTTP layer — routing, request/response wiring, DI
├── config/       # Settings, logging, database engine
├── core/         # Cross-cutting concerns — exceptions
├── models/       # SQLAlchemy ORM table definitions
├── repositories/ # DB access — no business logic
├── schemas/      # Pydantic models — input/output contracts
├── services/     # Business logic — orchestration only
└── utils/        # Pure helpers — CSV parsing, validation
```

**Request flow:**
```
Client → API (validate HTTP concerns)
       → Service (orchestrate)
       → Utils (parse + validate rows)
       → Repository (persist)
       → Service (build result)
       → API (return response)
```

**Key principles:**
- API layer never touches DB directly
- Service layer has no FastAPI imports
- Repository is the only SQLAlchemy consumer
- Partial success model — valid rows persist even if some rows fail validation

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Validation | Pydantic v2 |
| ORM | SQLAlchemy 2.0 |
| Database | SQLite (dev) |
| Config | pydantic-settings |
| Server | Uvicorn |
| Python | 3.13 |

---

## Setup

### 1. Clone & create virtual environment
```bash
git clone https://github.com/your-username/smart-file-processing-api.git
cd smart-file-processing-api
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
Create `.env` in project root:
```env
APP_NAME=Smart File Processing API
ENV=development
UPLOAD_DIR=uploads
MAX_FILE_SIZE_MB=10
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///./smart_files.db
```

### 4. Run
```bash
uvicorn app.main:app --reload
```

API docs available at: `http://127.0.0.1:8000/docs`

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check — returns app name and environment |
| `POST` | `/upload` | Upload a CSV file for processing |
| `GET` | `/employees` | Retrieve all persisted employee records |

---

## Sample Requests

### Health Check
```bash
curl -X GET http://127.0.0.1:8000/health
```
```json
{
  "app": "Smart File Processing API",
  "env": "development"
}
```

---

### Upload CSV
```bash
curl -X POST http://127.0.0.1:8000/upload \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@employees.csv;type=text/csv"
```

**CSV format:**
```csv
name,email,age
John,john@gmail.com,25
Alice,alice@gmail.com,30
Bob,bob@gmail,abc
,empty@gmail.com,28
```

**Response — partial success:**
```json
{
  "filename": "employees.csv",
  "size_kb": 0.11,
  "accepted": 2,
  "rejected": 2,
  "failed_rows": [
    {
      "original_data": { "name": "Bob", "email": "bob@gmail", "age": "abc" },
      "error_reason": "value is not a valid email address; Input should be a valid integer",
      "row_index": 2
    },
    {
      "original_data": { "name": "", "email": "empty@gmail.com", "age": "28" },
      "error_reason": "String should have at least 1 character",
      "row_index": 3
    }
  ]
}
```

**Validation rules per row:**
- `name` — required, non-empty, non-whitespace
- `email` — must be a valid email address
- `age` — integer between 18 and 100

**Error responses:**

| Status | Reason |
|---|---|
| `400` | Non-CSV file, file exceeds size limit, empty file, invalid encoding |
| `409` | Duplicate email already exists in DB |

---

### Get All Employees
```bash
curl -X GET http://127.0.0.1:8000/employees
```
```json
[
  { "id": 1, "name": "John", "email": "john@gmail.com", "age": 25 },
  { "id": 2, "name": "Alice", "email": "alice@gmail.com", "age": 30 }
]
```

---

## Observability

Every request is assigned a UUID (`x-request-id`) injected by middleware and attached to all log lines during that request's lifecycle.

**Log format (JSON):**
```json
{
  "timestamp": "2026-07-04T17:21:02.000000+00:00",
  "level": "INFO",
  "message": "health check called",
  "request_id": "cf261aa9-2369-4dac-9b67-b8652f36c39e",
  "logger": "app.api.health"
}
```

---

## Engineering Decisions

| Decision | Rationale |
|---|---|
| Partial success model | Real-world CSVs are messy — reject individual rows, not the whole file |
| Repository pattern | Decouples service from SQLAlchemy — swappable without touching business logic |
| `pydantic-settings` for config | Type-validated at startup, fails fast on misconfiguration |
| `@lru_cache` on `get_settings()` | Singleton without boilerplate — `.env` parsed once per process |
| Sync SQLAlchemy + SQLite | Async adds complexity without throughput benefit on file-based DB; interface designed for easy swap to async Postgres |
| ContextVar for request ID | Async-safe isolation — global variable would leak across concurrent requests on same event loop |
| `JSONFormatter` without third-party lib | Zero extra dependency for one log format; production system would use `python-json-logger` |

---

## Known Limitations & Production Roadmap

- **No auth** — add OAuth2/JWT before exposing publicly
- **Sync processing** — large files block the request thread; move to background tasks (Celery + Redis) at scale
- **SQLite** — replace with Postgres for production; only the `DATABASE_URL` and session factory change
- **No pagination** on `GET /employees` — add `limit`/`offset` query params
- **Content-type spoofing** — MIME check is client-controlled; real validation is the CSV parse attempt itself