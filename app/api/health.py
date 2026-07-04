import logging
from fastapi import APIRouter, Depends
from app.config.settings import Settings, get_settings
from app.schemas.health import HealthResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health", response_model=HealthResponse)
def health_check(settings: Settings = Depends(get_settings)):
    logger.info("health check called")
    return {"app": settings.app_name, "env": settings.env}