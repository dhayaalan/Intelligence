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
    def list_logs_paginated(
        tenant_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        col = audit_repo.sync_collection
        query = {"tenant_id": tenant_id} if tenant_id and tenant_id not in ["platform_admin", "system"] else {}
        if search:
            query["$or"] = [
                {"action": {"$regex": search, "$options": "i"}},
                {"resource_type": {"$regex": search, "$options": "i"}},
                {"user_id": {"$regex": search, "$options": "i"}},
            ]

        skip = (page - 1) * page_size

        if col is not None:
            try:
                total = col.count_documents(query)
                docs = list(col.find(query, {"_id": 0}).sort("timestamp", -1).skip(skip).limit(page_size))
                items = [AuditLogEntry(**l) for l in docs]
                total_pages = max(1, (total + page_size - 1) // page_size) if total > 0 else 1
                return {
                    "items": items,
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages
                }
            except Exception:
                pass

        with db._lock:
            logs = list(db.audit_logs)
            if tenant_id and tenant_id not in ["platform_admin", "system"]:
                logs = [l for l in logs if l.get("tenant_id") == tenant_id]
            if search:
                s_lower = search.lower()
                logs = [
                    l for l in logs
                    if s_lower in str(l.get("action", "")).lower()
                    or s_lower in str(l.get("resource_type", "")).lower()
                    or s_lower in str(l.get("user_id", "")).lower()
                ]
            total = len(logs)
            sorted_logs = sorted(logs, key=lambda x: str(x["timestamp"]), reverse=True)
            paged = sorted_logs[skip : skip + page_size]
            total_pages = max(1, (total + page_size - 1) // page_size) if total > 0 else 1
            return {
                "items": [AuditLogEntry(**l) for l in paged],
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }

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
            logs = list(db.audit_logs)
            if tenant_id and tenant_id not in ["platform_admin", "system"]:
                logs = [l for l in logs if l.get("tenant_id") == tenant_id]
            return [AuditLogEntry(**l) for l in sorted(logs, key=lambda x: str(x["timestamp"]), reverse=True)[:limit]]

audit_logger = AuditLogger()
