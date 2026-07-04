from sqlalchemy.orm import Session
from app.models.employee import Employee


def bulk_insert_employees(db: Session, employees: list[dict]) -> int:
    objects = [Employee(**emp) for emp in employees]
    db.add_all(objects)
    db.commit()
    return len(objects)

def get_all_employees(db: Session) -> list[Employee]:
    return db.query(Employee).all()