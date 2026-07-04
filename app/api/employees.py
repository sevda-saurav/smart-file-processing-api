from fastapi import APIRouter
from app.config.database import SessionLocal
from app.repositories.employee_repository import get_all_employees

router = APIRouter()

@router.get("/employees")
def list_employees():
    db = SessionLocal()
    try:
        employees = get_all_employees(db)
        return [{"id": e.id, "name": e.name, "email": e.email, "age": e.age} for e in employees]
    finally:
        db.close()