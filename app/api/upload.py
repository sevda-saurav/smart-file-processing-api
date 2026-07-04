from fastapi import APIRouter, UploadFile
from app.core.exceptions import AppException
from app.config.settings import get_settings
from app.services.file_service import process_csv_file

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile):
    settings = get_settings()

    # Step 1: check content type — reject if not "text/csv"
    if file.content_type != "text/csv":
        raise AppException("Only CSV files are supported", 400)
    
    # Step 2: read file contents with await file.read()
    contents = await file.read()
    
    # Step 3: calculate size in MB, compare to settings.max_file_size_mb
    size_mb = len(contents) / (1024*1024)
    if size_mb > settings.max_file_size_mb:
        raise AppException(
    f"File exceeds max size of {settings.max_file_size_mb}MB", 400
    )
    return process_csv_file(contents, file.filename)