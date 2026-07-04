from fastapi import FastAPI, Request
from app.api.middleware import RequestIDMiddleware
from app.config.settings import get_settings
from app.api.health import router as health_router
from app.core.exceptions import AppException
from app.config.logging import request_id_var
from app.config.logging import setup_logging
from fastapi.responses import JSONResponse
from app.api.upload import router as upload_router
from app.models.employee import Base
from app.config.database import get_engine
from app.api.employees import router as employees_router



def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging(settings.log_level)
    app = FastAPI(title=settings.app_name)
    app.include_router(health_router)
    app.include_router(upload_router)
    app.add_middleware(RequestIDMiddleware)
    app.include_router(employees_router)
    Base.metadata.create_all(bind=get_engine())

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message, "request_id": request_id_var.get()},
        )

    return app

app = create_app()