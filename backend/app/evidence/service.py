from typing import List, Optional
import uuid
from app.core.database import db
from app.evidence.models import EvidenceRecord
from app.module_sdk.models import EvidencePayload
from app.infrastructure.mongodb.repositories import evidence_repo

class EvidenceService:
    @staticmethod
    def store_evidence(tenant_id: str, payload: EvidencePayload, investigation_id: Optional[str] = None, search_id: Optional[str] = None) -> EvidenceRecord:
        ev_id = payload.id or f"ev_{uuid.uuid4().hex[:12]}"
        record = EvidenceRecord(
            id=ev_id,
            tenant_id=tenant_id,
            investigation_id=investigation_id,
            search_id=search_id,
            source=payload.source,
            provider=payload.provider,
            module=payload.module,
            collection_method=payload.collection_method,
            reference=payload.reference,
            confidence=payload.confidence,
            raw_data=payload.raw_data,
            hash=payload.hash or "",
            timestamp=payload.timestamp
        )
        r_dict = record.dict()
        with db._lock:
            db.evidence[ev_id] = r_dict
        evidence_repo._sync_write({"id": ev_id, "tenant_id": tenant_id}, r_dict)
        return record

    @staticmethod
    def list_evidence(tenant_id: str, investigation_id: Optional[str] = None, search_id: Optional[str] = None) -> List[EvidenceRecord]:
        with db._lock:
            records = [EvidenceRecord(**d) for d in db.evidence.values() if d.get("tenant_id") == tenant_id]
            if investigation_id:
                inv_data = db.investigations.get(investigation_id, {})
                linked_ids = set(inv_data.get("evidence_ids", []))
                inv_search_id = inv_data.get("search_id")
                records = [
                    r for r in records
                    if r.investigation_id == investigation_id or r.id in linked_ids or (inv_search_id and r.search_id == inv_search_id)
                ]
            if search_id:
                records = [r for r in records if r.search_id == search_id]
            return records

    @staticmethod
    def get_evidence(tenant_id: str, evidence_id: str) -> Optional[EvidenceRecord]:
        with db._lock:
            data = db.evidence.get(evidence_id)
            if data and data.get("tenant_id") == tenant_id:
                return EvidenceRecord(**data)
        col = evidence_repo.sync_collection
        if col is not None:
            doc = col.find_one({"id": evidence_id, "tenant_id": tenant_id}, {"_id": 0})
            if doc:
                with db._lock:
                    db.evidence[evidence_id] = doc
                return EvidenceRecord(**doc)
        return None

evidence_service = EvidenceService()
