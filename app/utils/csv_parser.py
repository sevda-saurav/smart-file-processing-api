import io
import csv
from app.core.exceptions import AppException
from pydantic import ValidationError
from app.schemas.csv_row import EmployeeRow

def parse_csv(contents:bytes) -> list[dict]:
    try:
        text= contents.decode("utf-8")
    except UnicodeDecodeError:
        raise AppException("Invalid File Encoding, expected utf-8", 400)
    
    reader = csv.DictReader(io.StringIO(text))
    rows = [row for row in reader]

    if not rows:
        raise AppException("File is empty or invalid csv", 400)
    
    return rows

def validate_rows(rows: list[dict]) -> tuple[list[EmployeeRow], list[dict]]:
    valid_rows : list[EmployeeRow] = []
    failed_rows : list[dict] = []

    for index, row_data in enumerate(rows):
        try:
            employee = EmployeeRow(**row_data)
            valid_rows.append(employee)

        except ValidationError as e:
            error_messages = [err["msg"] for err in e.errors()]
            error_reason = "; ".join(error_messages)
            
            failed_rows.append({
                "original_data": row_data,
                "error_reason": error_reason,
                "row_index": index
            })
    
    return valid_rows, failed_rows