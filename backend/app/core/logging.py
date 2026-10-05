import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional

class StructuredJsonFormatter(logging.Formatter):
    """Formats log records as structured JSON without leaking secrets."""
    
    SECRET_KEYS = {"password", "secret", "token", "api_key", "authorization", "key"}
    
    def _sanitize(self, data: Any) -> Any:
        if isinstance(data, dict):
            clean = {}
            for k, v in data.items():
                if any(sec in k.lower() for sec in self.SECRET_KEYS):
                    clean[k] = "******"
                else:
                    clean[k] = self._sanitize(v)
            return clean
        elif isinstance(data, list):
            return [self._sanitize(item) for item in data]
        return data

    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        
        # Inject standard contextual fields if present
        for field in [
            "request_id", "tenant_id", "user_id", "search_id",
            "job_id", "module_id", "provider_id", "execution_id"
        ]:
            if hasattr(record, field):
                log_obj[field] = getattr(record, field)
                
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
            
        sanitized = self._sanitize(log_obj)
        return json.dumps(sanitized)

def setup_logging(level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("sential")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Avoid duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredJsonFormatter())
        logger.addHandler(handler)
        
    return logger

app_logger = setup_logging()
