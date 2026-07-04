import logging
import json
from datetime import datetime, timezone
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="no-request-id")

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log = {
            "timestamp" : datetime.now(timezone.utc).isoformat(),
            "level" : record.levelname,
            "message" : record.getMessage(),
            "request_id" : request_id_var.get(),
            "logger" : record.name,
        }
        return json.dumps(log)
    
def setup_logging(log_level: str) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level.upper())
    root_logger.handlers = [handler]