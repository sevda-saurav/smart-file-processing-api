from sqlalchemy.orm import Session
from app.config.database import SessionLocal
from app.repositories.employee_repository import bulk_insert_employees
from app.utils.csv_parser import parse_csv, validate_rows
from sqlalchemy.exc import IntegrityError
from app.core.exceptions import AppException


def process_csv_file(contents: bytes, filename: str) -> dict:
    raw_rows = parse_csv(contents)
    valid_rows, failed_rows = validate_rows(raw_rows)
    size_kb = round(len(contents) / 1024, 2)

    db: Session = SessionLocal()
    try:
        inserted = bulk_insert_employees(db, [row.model_dump() for row in valid_rows])
    except IntegrityError:
        db.rollback()
        raise AppException("Duplicate records found — some emails already exist", 409)
    finally:
        db.close()

    return {
        "filename": filename,
        "size_kb": size_kb,
        "accepted": inserted,
        "rejected": len(failed_rows),
        "failed_rows": failed_rows,
    }