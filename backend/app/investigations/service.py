from typing import List, Optional
import uuid
from datetime import datetime
from app.core.database import db
from app.investigations.models import (
    InvestigationRecord, InvestigationCreateRequest,
    InvestigationUpdateRequest, InvestigationStatus, TimelineEvent, InvestigationNote
)
from app.infrastructure.mongodb.repositories import investigation_repo, case_repo

class InvestigationService:
    @staticmethod
    def create_investigation(
        tenant_id: str,
        user_id: str,
        user_name: str,
        request: InvestigationCreateRequest
    ) -> InvestigationRecord:
        inv_id = f"inv_{uuid.uuid4().hex[:10]}"
        now = datetime.utcnow()
        
        initial_event = TimelineEvent(
            id=f"evt_{uuid.uuid4().hex[:8]}",
            timestamp=now,
            title="Investigation Initialized",
            description=f"Investigation opened targeting {request.target_type} '{request.target}'",
            author=user_name,
            event_type="status_change"
        )
        
        record = InvestigationRecord(
            id=inv_id,
            tenant_id=tenant_id,
            title=request.title.strip(),
            description=request.description.strip(),
            summary=request.summary.strip() if request.summary else None,
            priority=request.priority.upper() if request.priority else "HIGH",
            status=InvestigationStatus.OPEN,
            target=request.target.strip(),
            target_type=request.target_type.strip(),
            selected_modules=request.selected_modules or ["osint", "threat_intelligence"],
            search_id=request.search_id,
            created_by=user_id,
            timeline=[initial_event],
            created_at=now,
            updated_at=now
        )
        
        r_dict = record.dict()
        with db._lock:
            db.investigations[inv_id] = r_dict
        
        # Persist to MongoDB collections 'investigations' and 'cases'
        investigation_repo._sync_write({"id": inv_id, "tenant_id": tenant_id}, r_dict)
        case_repo._sync_write({"id": inv_id, "tenant_id": tenant_id}, r_dict)
            
        return record

    @staticmethod
    def get_investigation(tenant_id: str, investigation_id: str) -> Optional[InvestigationRecord]:
        with db._lock:
            data = db.investigations.get(investigation_id)
            if data and data.get("tenant_id") == tenant_id:
                return InvestigationRecord(**data)
        col = investigation_repo.sync_collection
        if col is not None:
            doc = col.find_one({"id": investigation_id, "tenant_id": tenant_id}, {"_id": 0})
            if doc:
                with db._lock:
                    db.investigations[investigation_id] = doc
                return InvestigationRecord(**doc)
        return None

    @staticmethod
    def list_investigations(
        tenant_id: str,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        module: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[InvestigationRecord]:
        with db._lock:
            records = [
                InvestigationRecord(**d) for d in db.investigations.values()
                if d.get("tenant_id") == tenant_id
            ]
            
            if status and status.upper() != "ALL":
                records = [r for r in records if r.status.value.upper() == status.upper() or (status.upper() == "ACTIVE" and r.status in [InvestigationStatus.OPEN, InvestigationStatus.IN_PROGRESS])]
            if priority and priority.upper() != "ALL":
                records = [r for r in records if (r.priority or "HIGH").upper() == priority.upper()]
            if module and module.upper() != "ALL":
                mod_lower = module.lower()
                records = [r for r in records if mod_lower in [m.lower() for m in (r.selected_modules or [])]]
            if search and search.strip():
                s_lower = search.strip().lower()
                records = [
                    r for r in records
                    if s_lower in r.title.lower() or s_lower in r.target.lower() or s_lower in (r.description or "").lower() or s_lower in r.id.lower()
                ]

            return sorted(records, key=lambda x: x.updated_at, reverse=True)

    @staticmethod
    def list_investigations_paginated(
        tenant_id: str,
        page: int = 1,
        page_size: int = 10,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        module: Optional[str] = None,
        search: Optional[str] = None
    ):
        with db._lock:
            all_tenant_records = [
                InvestigationRecord(**d) for d in db.investigations.values()
                if d.get("tenant_id") == tenant_id
            ]

        # Calculate module counts across all records in tenant
        osint_count = sum(1 for r in all_tenant_records if "osint" in [m.lower() for m in (r.selected_modules or [])])
        ti_count = sum(1 for r in all_tenant_records if any("threat" in m.lower() or "ti" in m.lower() for m in (r.selected_modules or [])))
        module_counts = {
            "all": len(all_tenant_records),
            "osint": osint_count,
            "threat_intelligence": ti_count,
        }

        # Apply filters
        filtered = all_tenant_records
        if status and status.upper() != "ALL":
            filtered = [r for r in filtered if r.status.value.upper() == status.upper() or (status.upper() == "ACTIVE" and r.status in [InvestigationStatus.OPEN, InvestigationStatus.IN_PROGRESS])]
        if priority and priority.upper() != "ALL":
            filtered = [r for r in filtered if (r.priority or "HIGH").upper() == priority.upper()]
        if module and module.upper() != "ALL":
            mod_lower = module.lower()
            filtered = [r for r in filtered if any(mod_lower in m.lower() for m in (r.selected_modules or []))]
        if search and search.strip():
            s_lower = search.strip().lower()
            filtered = [
                r for r in filtered
                if s_lower in r.title.lower() or s_lower in r.target.lower() or s_lower in (r.description or "").lower() or s_lower in r.id.lower()
            ]

        sorted_records = sorted(filtered, key=lambda x: x.updated_at, reverse=True)
        total = len(sorted_records)
        total_pages = max(1, (total + page_size - 1) // page_size) if total > 0 else 1
        start = (page - 1) * page_size
        items = sorted_records[start:start + page_size]

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "module_counts": module_counts,
        }

    @staticmethod
    def update_investigation(
        tenant_id: str,
        investigation_id: str,
        request: InvestigationUpdateRequest,
        user_name: str
    ) -> Optional[InvestigationRecord]:
        with db._lock:
            data = db.investigations.get(investigation_id)
            if not data or data.get("tenant_id") != tenant_id:
                return None
                
            inv = InvestigationRecord(**data)
            now = datetime.utcnow()
            
            if request.title is not None:
                inv.title = request.title
            if request.description is not None:
                inv.description = request.description
            if request.status is not None and request.status != inv.status:
                inv.timeline.append(TimelineEvent(
                    id=f"evt_{uuid.uuid4().hex[:8]}",
                    timestamp=now,
                    title="Status Changed",
                    description=f"Status transitioned from {inv.status.value} to {request.status.value}",
                    author=user_name,
                    event_type="status_change"
                ))
                inv.status = request.status
                
            inv.updated_at = now
            i_dict = inv.dict()
            db.investigations[investigation_id] = i_dict
            
        investigation_repo._sync_write({"id": investigation_id, "tenant_id": tenant_id}, i_dict)
        case_repo._sync_write({"id": investigation_id, "tenant_id": tenant_id}, i_dict)
        return inv

    @staticmethod
    def add_note(
        tenant_id: str,
        investigation_id: str,
        user_id: str,
        user_name: str,
        content: str
    ) -> Optional[InvestigationRecord]:
        with db._lock:
            data = db.investigations.get(investigation_id)
            if not data or data.get("tenant_id") != tenant_id:
                return None
                
            inv = InvestigationRecord(**data)
            now = datetime.utcnow()
            note = InvestigationNote(
                id=f"note_{uuid.uuid4().hex[:8]}",
                author_id=user_id,
                author_name=user_name,
                content=content.strip(),
                created_at=now
            )
            inv.notes.append(note)
            inv.timeline.append(TimelineEvent(
                id=f"evt_{uuid.uuid4().hex[:8]}",
                timestamp=now,
                title="Investigator Note Added",
                description=f"New analysis note recorded by {user_name}",
                author=user_name,
                event_type="note"
            ))
            inv.updated_at = now
            i_dict = inv.dict()
            db.investigations[investigation_id] = i_dict
            
        investigation_repo._sync_write({"id": investigation_id, "tenant_id": tenant_id}, i_dict)
        case_repo._sync_write({"id": investigation_id, "tenant_id": tenant_id}, i_dict)
        return inv

    @staticmethod
    def link_entity(tenant_id: str, investigation_id: str, entity_id: str) -> bool:
        with db._lock:
            data = db.investigations.get(investigation_id)
            if not data or data.get("tenant_id") != tenant_id:
                return False
            if entity_id not in data.get("entity_ids", []):
                data.setdefault("entity_ids", []).append(entity_id)
                investigation_repo._sync_write({"id": investigation_id, "tenant_id": tenant_id}, data)
                case_repo._sync_write({"id": investigation_id, "tenant_id": tenant_id}, data)
            return True

    @staticmethod
    def link_evidence(tenant_id: str, investigation_id: str, evidence_id: str) -> bool:
        with db._lock:
            data = db.investigations.get(investigation_id)
            if not data or data.get("tenant_id") != tenant_id:
                return False
            if evidence_id not in data.get("evidence_ids", []):
                data.setdefault("evidence_ids", []).append(evidence_id)
                investigation_repo._sync_write({"id": investigation_id, "tenant_id": tenant_id}, data)
                case_repo._sync_write({"id": investigation_id, "tenant_id": tenant_id}, data)
            return True

investigation_service = InvestigationService()
