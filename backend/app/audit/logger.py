import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.core.database import db
from app.core.logging import app_logger
from app.infrastructure.mongodb.repositories import audit_repo

class AuditLogEntry(BaseModel):
    id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    tenant_id: str
    user_id: str
    action: str
    resource_type: str
    resource_id: str = ""
    details: Dict[str, Any] = Field(default_factory=dict)
    ip_address: str = "127.0.0.1"

class AuditLogger:
    @staticmethod
    def log(
        tenant_id: str,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str = "",
        details: Optional[Dict[str, Any]] = None,
        ip_address: str = "127.0.0.1"
    ) -> AuditLogEntry:
        entry = AuditLogEntry(
            id=f"aud_{uuid.uuid4().hex[:12]}",
            timestamp=datetime.utcnow(),
            tenant_id=tenant_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address
        )
        e_dict = entry.dict()
        with db._lock:
            db.audit_logs.append(e_dict)
            
        col = audit_repo.sync_collection
        if col is not None:
            try:
                col.insert_one(dict(e_dict))
            except Exception as e:
                app_logger.warning(f"Failed to persist audit log into MongoDB: {e}")
            
        app_logger.info(
            f"AUDIT: {action} on {resource_type}:{resource_id} by {user_id}",
            extra={"tenant_id": tenant_id, "user_id": user_id, "action": action}
        )
        return entry

    @staticmethod
    def list_logs(tenant_id: Optional[str] = None, limit: int = 100) -> List[AuditLogEntry]:
        col = audit_repo.sync_collection
        if col is not None:
            query = {"tenant_id": tenant_id} if tenant_id and tenant_id not in ["platform_admin", "system"] else {}
            try:
                docs = list(col.find(query, {"_id": 0}).sort("timestamp", -1).limit(limit))
                if docs:
                    return [AuditLogEntry(**l) for l in docs]
            except Exception:
                pass

        with db._lock:
            logs = db.audit_logs
            if tenant_id and tenant_id not in ["platform_admin", "system"]:
                logs = [l for l in logs if l.get("tenant_id") == tenant_id]
            return [AuditLogEntry(**l) for l in sorted(logs, key=lambda x: str(x["timestamp"]), reverse=True)[:limit]]

audit_logger = AuditLogger()
